"""Statsd middleware tracking view, middleware and database timings."""

import collections
import functools
import logging
import re
import time
import warnings
from collections.abc import Callable
from contextlib import ExitStack
from types import TracebackType
from typing import Any, ClassVar, ParamSpec, TypeVar

import statsd
from asgiref.local import Local
from django.db import connections
from django.http import HttpRequest
from django.http.response import HttpResponseBase

from django_statsd import settings, utils

logger: logging.Logger = logging.getLogger(__name__)

P = ParamSpec('P')
T = TypeVar('T')

GetResponse = Callable[[HttpRequest], HttpResponseBase]

TAGS_LIKE_SUPPORTED: tuple[str, ...] = ('=', '_is_')


def _get_tags_like() -> str | None:
    """Validate ``STATSD_TAGS_LIKE`` into a separator or ``None``."""
    tags_like = settings.STATSD_TAGS_LIKE
    if tags_like is None:
        return None
    if tags_like is True:
        return '_is_'
    if tags_like in TAGS_LIKE_SUPPORTED:
        return str(tags_like)

    warnings.warn(
        'Unsupported `STATSD_TAGS_LIKE` setting. '
        f'Please, choose from {TAGS_LIKE_SUPPORTED!r}',
        stacklevel=2,
    )
    return None


MAKE_TAGS_LIKE: str | None = _get_tags_like()


def is_ajax(request: HttpRequest) -> bool:
    """Recreate the old Django ``is_ajax`` check (jQuery-style ajax)."""
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


class WithTimer:
    """Context manager returned by calling a :class:`Timer`."""

    def __init__(self, timer: 'Timer', key: str) -> None:
        """Bind the timer and the key this block will be recorded under."""
        self.timer = timer
        self.key = key

    def __enter__(self) -> None:
        """Start the timer."""
        self.timer.start(self.key)

    def __exit__(
        self,
        type_: type[BaseException] | None,
        value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Stop the timer, however the block was left."""
        self.timer.stop(self.key)


class Client:
    """Base for the scope's metric holders.

    Collects values during a request and submits them in one go, so a
    request produces one burst of packets instead of a trickle.
    """

    class_: ClassVar[type[Any]] = statsd.Client

    def __init__(self, prefix: str = 'view') -> None:
        """Build the prefix, nesting it under ``STATSD_PREFIX``."""
        if settings.STATSD_PREFIX:
            prefix = f'{settings.STATSD_PREFIX}.{prefix}'
        self.prefix: str = prefix

    def get_client(self, *args: str | None) -> Any:
        """Build a python-statsd client for this prefix plus `args`."""
        prefix = '.'.join(a for a in (self.prefix, *args) if a)
        return utils.get_client(prefix, class_=self.class_)

    def submit(self, *args: str | None) -> None:
        """Send everything collected. Subclasses define what that means.

        Raises:
            NotImplementedError: always, on the base class.

        """
        raise NotImplementedError('Subclasses must define a `submit` function')


class Counter(Client):
    """Counters accumulated over one request or task."""

    class_: ClassVar[type[Any]] = statsd.Counter

    def __init__(self, prefix: str = 'view') -> None:
        """Start with every counter at zero."""
        super().__init__(prefix)
        self.data: collections.defaultdict[str, int] = collections.defaultdict(
            int
        )

    def increment(self, key: str, delta: int = 1) -> None:
        """Add `delta` to `key`."""
        self.data[key] += delta

    def decrement(self, key: str, delta: int = 1) -> None:
        """Subtract `delta` from `key`."""
        self.data[key] -= delta

    def submit(self, *args: str | None) -> None:
        """Send every counter that moved. Zeroes are not worth a packet."""
        client = self.get_client(*args)
        for key, value in self.data.items():
            if value:
                client.increment(key, value)


class Timer(Client):
    """Timings accumulated over one request or task.

    A key may be started more than once before it is stopped, so the
    starts are kept on a stack and the durations add up.
    """

    class_: ClassVar[type[Any]] = statsd.Timer

    def __init__(self, prefix: str = 'view') -> None:
        """Start with no timers running and nothing recorded."""
        super().__init__(prefix)
        self.starts: collections.defaultdict[str, collections.deque[float]] = (
            collections.defaultdict(collections.deque)
        )
        self.data: collections.defaultdict[str, float] = (
            collections.defaultdict(float)
        )

    def start(self, key: str) -> None:
        """Start timing `key`."""
        self.starts[key].append(time.time())

    def stop(self, key: str) -> float:
        """Stop timing `key` and add the elapsed time to its total.

        Args:
            key: The name passed to a matching :meth:`start`.

        Returns:
            The seconds that elapsed since that `start`.

        Raises:
            AssertionError: if `key` was never started.

        """
        assert self.starts[key], (
            f'Unable to stop tracking {key}, never started tracking it'
        )

        delta = time.time() - self.starts[key].pop()
        # Clean up when we're done
        if not self.starts[key]:
            del self.starts[key]

        self.data[key] += delta
        return delta

    def submit(self, *args: str | None) -> None:
        """Send every recorded timing and clear them.

        Raises:
            AssertionError: under ``STATSD_DEBUG``, if a timer was
                started and never stopped.

        """
        client = self.get_client(*args)
        for key in list(self.data.keys()):
            client.send(key, self.data.pop(key))

        if settings.STATSD_DEBUG:
            assert not self.starts, (
                f'Timer(s) {dict(self.starts)!r} were started but '
                'never stopped'
            )

    def __call__(self, key: str) -> WithTimer:
        """Return a context manager timing `key`."""
        return WithTimer(self, key)


class StatsdMiddleware:
    """Opens the scope and submits the per-view metrics.

    Goes at the top of ``MIDDLEWARE``, with
    :class:`StatsdMiddlewareTimer` at the bottom. The scope lives on
    :class:`asgiref.local.Local`, so each request gets its own under
    both WSGI and ASGI.
    """

    scope: ClassVar[Local] = Local()

    def __init__(self, get_response: GetResponse) -> None:
        """Store the next callable in the middleware chain."""
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponseBase:
        """Time one request, wrapping the database if asked to."""
        # Store the timings in the request so it can be used everywhere
        self.process_request(request)
        try:
            with ExitStack() as stack:
                if settings.STATSD_TRACK_DATABASE:
                    # Imported here to avoid a circular import at load
                    # time: database.py needs this module's helpers.
                    from django_statsd import database

                    for alias in connections:
                        stack.enter_context(
                            connections[alias].execute_wrapper(
                                database.statsd_execute_wrapper(alias)
                            )
                        )
                response = self.get_response(request)
            return self.process_response(request, response)
        finally:
            self.cleanup(request)

    @classmethod
    def _scope_get(cls, name: str) -> Any:
        return getattr(cls.scope, name, None)

    @classmethod
    def skip_view(cls, view_name: str) -> bool:
        """Whether `view_name` matches ``STATSD_VIEWS_TO_SKIP``."""
        for pattern in settings.STATSD_VIEWS_TO_SKIP:
            if re.match(pattern, view_name):
                logger.debug('Skipping metric `%s`', view_name)
                return True

        return False

    @classmethod
    def start(cls, prefix: str = 'view') -> Local:
        """Open a scope and start the total timer.

        Args:
            prefix: The metric prefix, ``view`` for requests and
                ``celery`` for tasks.

        Returns:
            The scope, which the middleware puts on ``request.statsd``.

        """
        cls.scope.timings = Timer(prefix)
        cls.scope.timings.start('total')
        cls.scope.counter = Counter(prefix)
        cls.scope.counter.increment('hit')
        cls.scope.counter_codes = Counter(prefix)
        cls.scope.counter_codes.increment('hit')
        cls.scope.counter_site = Counter(prefix)
        cls.scope.counter_site.increment('hit')
        cls.scope.view_name = None
        return cls.scope

    @classmethod
    def stop(cls, *key: str) -> None:
        """Stop the total timer and submit everything collected."""
        timings: Timer | None = cls._scope_get('timings')
        if not timings:
            return

        timings.stop('total')
        timings.submit(*key)
        counter: Counter | None = cls._scope_get('counter')
        if counter:
            counter.submit(*key)
        counter_site: Counter | None = cls._scope_get('counter_site')
        if counter_site:
            counter_site.submit('site')

    def process_request(self, request: HttpRequest) -> None:
        """Open the scope and hang it off the request."""
        # request.statsd is a documented dynamic attribute (see
        # docs/django_statsd.rst) set by this middleware; neither
        # django-stubs nor ty know about it.
        request.statsd = self.start()  # type: ignore[attr-defined]  # ty: ignore[unresolved-attribute]
        if settings.STATSD_TRACK_MIDDLEWARE:
            self.scope.timings.start('process_request')

    def process_view(
        self,
        request: HttpRequest,
        view_func: Callable[..., HttpResponseBase],
        view_args: tuple[Any, ...],
        view_kwargs: dict[str, Any],
    ) -> None:
        """Name the metric after the view Django resolved."""
        timings: Timer | None = self._scope_get('timings')
        if settings.STATSD_TRACK_MIDDLEWARE and timings:
            timings.start('process_view')

        # View name is defined as module.view
        # (e.g. django.contrib.auth.views.login)
        view_name = view_func.__module__

        # CBV and callable-instance specific
        if hasattr(view_func, '__name__'):
            view_name = f'{view_name}.{view_func.__name__}'
        else:
            view_name = f'{view_name}.{view_func.__class__.__name__}'

        if MAKE_TAGS_LIKE:
            view_name = view_name.replace('.', '_')
            view_name = f'view{MAKE_TAGS_LIKE}{view_name}'

        self.scope.view_name = view_name

    def process_response(
        self,
        request: HttpRequest,
        response: HttpResponseBase,
    ) -> HttpResponseBase:
        """Count the status class and submit the request's metrics."""
        view_name: str | None = self._scope_get('view_name')
        if view_name and self.skip_view(view_name):
            return response

        counter_codes: Counter | None = self._scope_get('counter_codes')
        if counter_codes:
            counter_codes.increment(f'{response.status_code // 100}xx')
            counter_codes.submit('http_codes')

        timings: Timer | None = self._scope_get('timings')
        if settings.STATSD_TRACK_MIDDLEWARE and timings:
            timings.stop('process_response')

        method = (request.method or 'get').lower()
        if MAKE_TAGS_LIKE:
            tag_method = f'method{MAKE_TAGS_LIKE}{method.replace(".", "_")}'
            ajax = f'is_ajax_{MAKE_TAGS_LIKE}{str(is_ajax(request)).lower()}'
            if view_name:
                self.stop(tag_method, view_name, ajax)
        else:
            if is_ajax(request):
                method += '_ajax'
            if view_name:
                self.stop(method, view_name)

        self.cleanup(request)
        return response

    def process_exception(
        self,
        request: HttpRequest,
        exception: BaseException,
    ) -> None:
        """Stop the timer and count the failure as a 5xx."""
        timings: Timer | None = self._scope_get('timings')
        if settings.STATSD_TRACK_MIDDLEWARE and timings:
            timings.stop('process_exception')

        counter_codes: Counter | None = self._scope_get('counter_codes')
        if counter_codes:
            counter_codes.increment('5xx')
            counter_codes.submit('http_codes')

    def process_template_response(
        self,
        request: HttpRequest,
        response: HttpResponseBase,
    ) -> HttpResponseBase:
        """Stop the template timer."""
        timings: Timer | None = self._scope_get('timings')
        if settings.STATSD_TRACK_MIDDLEWARE and timings:
            timings.stop('process_template_response')
        return response

    def cleanup(self, request: HttpRequest) -> None:
        """Clear the scope so the next request starts fresh."""
        self.scope.timings = None
        self.scope.counter = None
        self.scope.counter_codes = None
        self.scope.counter_site = None
        self.scope.view_name = None
        request.statsd = None  # type: ignore[attr-defined]  # ty: ignore[unresolved-attribute]


class StatsdMiddlewareTimer:
    """Closes the timers :class:`StatsdMiddleware` opened.

    Goes at the bottom of ``MIDDLEWARE``. Between the pair they time
    every middleware you install in between.
    """

    def __init__(self, get_response: GetResponse) -> None:
        """Store the next callable in the middleware chain."""
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponseBase:
        """Time the inner half of the stack."""
        self.process_request(request)
        return self.process_response(request, self.get_response(request))

    @staticmethod
    def _timings() -> Timer | None:
        if settings.STATSD_TRACK_MIDDLEWARE:
            return getattr(StatsdMiddleware.scope, 'timings', None)
        return None

    def process_request(self, request: HttpRequest) -> None:
        """Stop the inbound timer the tracker started."""
        timings = self._timings()
        if timings:
            timings.stop('process_request')

    def process_view(
        self,
        request: HttpRequest,
        view_func: Callable[..., HttpResponseBase],
        view_args: tuple[Any, ...],
        view_kwargs: dict[str, Any],
    ) -> None:
        """Stop the view timer."""
        timings = self._timings()
        if timings:
            timings.stop('process_view')

    def process_response(
        self,
        request: HttpRequest,
        response: HttpResponseBase,
    ) -> HttpResponseBase:
        """Start the outbound timer the tracker will stop."""
        timings = self._timings()
        if timings:
            timings.start('process_response')
        return response

    def process_exception(
        self,
        request: HttpRequest,
        exception: BaseException,
    ) -> None:
        """Start the exception timer the tracker will stop."""
        timings = self._timings()
        if timings:
            timings.start('process_exception')

    def process_template_response(
        self,
        request: HttpRequest,
        response: HttpResponseBase,
    ) -> HttpResponseBase:
        """Start the template timer the tracker will stop."""
        timings = self._timings()
        if timings:
            timings.start('process_template_response')
        return response


class DummyWith:
    """Stands in for :class:`WithTimer` outside a tracked request.

    Lets the module-level helpers be used anywhere without the caller
    checking whether a request is being timed.
    """

    def __enter__(self) -> None:
        """Do nothing."""

    def __exit__(
        self,
        type_: type[BaseException] | None,
        value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Do nothing."""


def _timings() -> Timer | None:
    return getattr(StatsdMiddleware.scope, 'timings', None)


def _counter() -> Counter | None:
    return getattr(StatsdMiddleware.scope, 'counter', None)


def start(key: str) -> None:
    """Start timing `key` in the current scope, if there is one."""
    timings = _timings()
    if timings:
        timings.start(key)


def stop(key: str) -> float | None:
    """Stop timing `key`.

    Returns:
        The elapsed seconds, or ``None`` outside a tracked request.

    """
    timings = _timings()
    if timings:
        return timings.stop(key)
    return None


def with_(key: str) -> WithTimer | DummyWith:
    """Return a context manager timing `key`.

    Returns:
        A timer inside a tracked request, and a no-op outside one.

    """
    timings = _timings()
    if timings:
        return timings(key)
    return DummyWith()


def incr(key: str, value: int = 1) -> None:
    """Add `value` to the counter `key`, if a scope is open."""
    counter = _counter()
    if counter:
        counter.increment(key, value)


def decr(key: str, value: int = 1) -> None:
    """Subtract `value` from the counter `key`, if a scope is open."""
    counter = _counter()
    if counter:
        counter.decrement(key, value)


def wrapper(prefix: str, f: Callable[P, T]) -> Callable[P, T]:
    """Wrap `f` so each call is timed as ``<prefix>.<function name>``."""
    # Not every Callable exposes __name__ (e.g. functools.partial or a
    # callable instance), so fall back to the type name instead of
    # assuming a plain function.
    name = getattr(f, '__name__', type(f).__name__)

    @functools.wraps(f)
    def _wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        with with_(f'{prefix}.{name.lower()}'):
            return f(*args, **kwargs)

    return _wrapper


def named_wrapper(name: str, f: Callable[P, T]) -> Callable[P, T]:
    """Wrap `f` so each call is timed as `name`."""

    @functools.wraps(f)
    def _wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        with with_(name):
            return f(*args, **kwargs)

    return _wrapper


def decorator(prefix: str) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Return a decorator timing each call under `prefix`."""
    return functools.partial(wrapper, prefix)
