from __future__ import with_statement
import time
import logging
import functools
import threading
import warnings
import collections
import statsd

from django.conf import settings

from django_statsd import utils

logger = logging.getLogger(__name__)


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
        self.prefix = prefix
        self.data = collections.defaultdict(int)

    def get_client(self, *args):
        prefix = '%s.%s' % (self.prefix, '.'.join(args))
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
        for k, v in self.data:
            if v:
                client.increment(k, v)

class Timer(Client):
    class_ = statsd.Timer

    def __init__(self, prefix='view'):
        Client.__init__(self, prefix)
        self.starts = {}
        self.data = collections.defaultdict(float)

    def start(self, key):
        assert key not in self.starts, 'Already started tracking %s' % key
        self.starts[key] = time.time()

    def stop(self, key):
        assert key in self.starts, ('Unable to stop tracking %s, never '
            'started tracking it' % key)

        delta = time.time() - self.starts.pop(key)
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
        return cls.scope

    def process_request(self, request):
        # store the timings in the request so it can be used everywhere
        request.statsd = self.start()
        self.view_name = None

    def process_view(
            self,
            request,
            view_func,
            view_args,
            view_kwargs,
        ):

        # View name is defined as module.view
        # (e.g. django.contrib.auth.views.login)
        self.view_name = view_func.__module__ + '.' + view_func.__name__

    @classmethod
    def stop(cls, *key):
        if getattr(cls.scope, 'timings', None):
            cls.scope.timings.stop('total')
            cls.scope.timings.submit(*key)
            cls.scope.counter.submit(*key)

    def process_response(self, request, response):
        method = request.method.lower()
        if request.is_ajax():
            method += '_ajax'

        if getattr(self, 'view_name', None):
            self.stop(
                method,
                self.view_name,
            )

        self.cleanup(request)

        return response

    def process_exception(self, request, exception):
        self.cleanup(request)

    def cleanup(self, request):
        self.scope.timings = None
        self.scope.counter = None
        self.view_name = None
        request.statsd = None


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
        StatsdMiddleware.scope.counter.incr(key, value)

def decr(key, value=1):
    if getattr(StatsdMiddleware.scope, 'counter', None):
        StatsdMiddleware.scope.counter.decr(key, value)

def wrapper(prefix, f):
    @functools.wraps(f)
    def _wrapper(*args, **kwargs):
        with with_('%s.%s' % (prefix, f.__name__.lower())):
            return f(*args, **kwargs)
    return _wrapper

def decorator(prefix):
    return lambda f: wrapper(prefix, f)

