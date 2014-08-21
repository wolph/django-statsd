from __future__ import with_statement
import time
import logging
import functools
import threading
import warnings
import collections
import statsd

from django.conf import settings
from django.core import exceptions

from django_statsd import utils

logger = logging.getLogger(__name__)

try:
    TRACK_MIDDLEWARE = getattr(settings, 'STATSD_TRACK_MIDDLEWARE', False)
except exceptions.ImproperlyConfigured:
    TRACK_MIDDLEWARE = False


class WithTimer(object):

    def __init__(self, timer, key):
        self.timer = timer
        self.key = key

    def __enter__(self):
        self.timer.start(self.key)

    def __exit__(
            self,
            type_,
            value,
            traceback,
        ):
        self.timer.stop(self.key)


class Client(object):
    class_ = statsd.Client

    def __init__(self, prefix='view'):
        global_prefix = getattr(settings, 'STATSD_PREFIX', None)
        if global_prefix:
            prefix = '%s.%s' % (global_prefix, prefix)
        self.prefix = prefix
        self.data = collections.defaultdict(int)

    def get_client(self, *args):
        args = [self.prefix] + list(args)
        prefix = '.'.join(a for a in args if a)
        return utils.get_client(prefix, class_=self.class_)

    def submit(self, *args):
        raise NotImplementedError(
            'Subclasses must define a `submit` function')

class Counter(Client):
    class_ = statsd.Counter

    def increment(self, key, delta=1):
        self.data[key] += delta

    def decrement(self, key, delta=1):
        self.data[key] -= delta

    def submit(self, *args):
        client = self.get_client(*args)
        for k, v in self.data.items():
            if v:
                client.increment(k, v)

class Timer(Client):
    class_ = statsd.Timer

    def __init__(self, prefix='view'):
        Client.__init__(self, prefix)
        self.starts = collections.defaultdict(collections.deque)
        self.data = collections.defaultdict(float)

    def start(self, key):
        self.starts[key].append(time.time())

    def stop(self, key):
        assert self.starts[key], ('Unable to stop tracking %s, never '
            'started tracking it' % key)

        delta = time.time() - self.starts[key].pop()
        # Clean up when we're done
        if not self.starts[key]:
            del self.starts[key]

        self.data[key] += delta
        return delta

    def submit(self, *args):
        client = self.get_client(*args)
        for k in self.data.keys():
            client.send(k, self.data.pop(k))

        if settings.DEBUG:
            assert not self.starts, ('Timer(s) %r were started but never '
                'stopped' % self.starts)

    def __call__(self, key):
        return WithTimer(self, key)

class StatsdMiddleware(object):
    scope = threading.local()

    def __init__(self):
        self.scope.timings = None
        self.scope.counter = None

    @classmethod
    def start(cls, prefix='view'):
        cls.scope.timings = Timer(prefix)
        cls.scope.timings.start('total')
        cls.scope.counter = Counter(prefix)
        cls.scope.counter.increment('hit')
        cls.scope.counter_site = Counter(prefix)
        cls.scope.counter_site.increment('hit')
        return cls.scope

    @classmethod
    def stop(cls, *key):
        if getattr(cls.scope, 'timings', None):
            cls.scope.timings.stop('total')
            cls.scope.timings.submit(*key)
            cls.scope.counter.submit(*key)
            cls.scope.counter_site.submit('site')

    def process_request(self, request):
        # store the timings in the request so it can be used everywhere
        request.statsd = self.start()
        if TRACK_MIDDLEWARE:
            self.scope.timings.start('process_request')
        self.view_name = None

    def process_view(self, request, view_func, view_args, view_kwargs):
        if TRACK_MIDDLEWARE:
            StatsdMiddleware.scope.timings.start('process_view')

        # View name is defined as module.view
        # (e.g. django.contrib.auth.views.login)
        self.view_name = view_func.__module__

        # CBV specific
        if hasattr(view_func, '__name__'):
            self.view_name = '%s.%s' % (self.view_name, view_func.__name__)
        elif hasattr(view_func, '__class__'):
            self.view_name = '%s.%s' % (self.view_name, view_func.__class__.__name__)

    def process_response(self, request, response):
        if TRACK_MIDDLEWARE:
            StatsdMiddleware.scope.timings.stop('process_response')
        method = request.method.lower()
        if request.is_ajax():
            method += '_ajax'
        if getattr(self, 'view_name', None):
            self.stop(method, self.view_name)
        self.cleanup(request)
        return response

    def process_exception(self, request, exception):
        if TRACK_MIDDLEWARE:
            StatsdMiddleware.scope.timings.stop('process_exception')

    def process_template_response(self, request, response):
        if TRACK_MIDDLEWARE:
            StatsdMiddleware.scope.timings.stop('process_template_response')
        return response

    def cleanup(self, request):
        self.scope.timings = None
        self.scope.counter = None
        self.view_name = None
        request.statsd = None

class StatsdMiddlewareTimer(object):
    def process_request(self, request):
        if TRACK_MIDDLEWARE:
            StatsdMiddleware.scope.timings.stop('process_request')

    def process_view(self, request, view_func, view_args, view_kwargs):
        if TRACK_MIDDLEWARE:
            StatsdMiddleware.scope.timings.stop('process_view')

    def process_response(self, request, response):
        if TRACK_MIDDLEWARE:
            StatsdMiddleware.scope.timings.start('process_response')
        return response

    def process_exception(self, request, exception):
        if TRACK_MIDDLEWARE:
            StatsdMiddleware.scope.timings.start('process_exception')

    def process_template_response(self, request, response):
        if TRACK_MIDDLEWARE:
            StatsdMiddleware.scope.timings.start('process_template_response')
        return response

class TimingMiddleware(StatsdMiddleware):
    @classmethod
    def deprecated(cls, *args, **kwargs):
        warnings.warn(
            'The `TimingMiddleware` has been deprecated in favour of '
            'the `StatsdMiddleware`. Please update your middleware settings',
            DeprecationWarning
        )

    __init__ = deprecated


class DummyWith(object):
    def __enter__(self):
        pass

    def __exit__(self, type_, value, traceback):
        pass


def start(key):
    if getattr(StatsdMiddleware.scope, 'timings', None):
        StatsdMiddleware.scope.timings.start(key)

def stop(key):
    if getattr(StatsdMiddleware.scope, 'timings', None):
        return StatsdMiddleware.scope.timings.stop(key)

def with_(key):
    if getattr(StatsdMiddleware.scope, 'timings', None):
        return StatsdMiddleware.scope.timings(key)
    else:
        return DummyWith()

def incr(key, value=1):
    if getattr(StatsdMiddleware.scope, 'counter', None):
        StatsdMiddleware.scope.counter.increment(key, value)

def decr(key, value=1):
    if getattr(StatsdMiddleware.scope, 'counter', None):
        StatsdMiddleware.scope.counter.decrement(key, value)

def wrapper(prefix, f):
    @functools.wraps(f)
    def _wrapper(*args, **kwargs):
        with with_('%s.%s' % (prefix, f.__name__.lower())):
            return f(*args, **kwargs)
    return _wrapper

def named_wrapper(name, f):
    @functools.wraps(f)
    def _wrapper(*args, **kwargs):
        with with_(name):
            return f(*args, **kwargs)
    return _wrapper

def decorator(prefix):
    return lambda f: wrapper(prefix, f)

