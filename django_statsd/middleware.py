from __future__ import with_statement
import time
from django_statsd import utils
import logging
import threading
logger = logging.getLogger(__name__)

class WithTimer(object):
    def __init__(self, timer, key):
        self.timer = timer
        self.key = key

    def __enter__(self):
        self.timer.start(self.key)

    def __exit__(self, type_, value, traceback):
        self.timer.stop(self.key)


class Timer(object):
    def __init__(self):
        self.starts = {}
        self.totals = {}

    def start(self, key):
        assert key not in self.starts, 'Already started tracking %s' % key
        self.starts[key] = time.time()

    def stop(self, key):
        assert (
            key in self.starts,
            'Unable to stop tracking %s, never started tracking it' % key,
        )

        delta = time.time() - self.starts.pop(key)
        self.totals[key] = self.totals.get(key, 0.0) + delta
        return delta

    def submit(self, request_method, view_name):
        prefix = 'view.%s.%s' % (request_method, view_name)

        timer = utils.get_timer(prefix)

        for k in self.totals.keys():
            timer.send(k, self.totals.pop(k))
    
    def __call__(self, key):
        return WithTimer(self, key)


class TimingMiddleware(object):
    scope = threading.local()

    def process_request(self, request):
        # store the timings in the request so it can be used everywhere
        request.timings = Timer()
        request.timings.start('total')
        self.scope = request
        self.view_name = None

    def process_view(self, request, view_func, view_args, view_kwargs):
        # View name is defined as module.view
        # (e.g. django.contrib.auth.views.login)
        self.view_name = view_func.__module__ + '.' + view_func.__name__

        # Time the response
        with request.timings('view'):
            response = view_func(request, *view_args, **view_kwargs)

        return response

    def process_response(self, request, response):
        request.timings.stop('total')
        if self.view_name:
            request.timings.submit(
                request.method.lower(),
                self.view_name,
            )

        return response

