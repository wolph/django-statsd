from __future__ import absolute_import
from django_statsd import middleware, utils

try:
    from celery import signals
    from celery.utils import dispatch

    counter = utils.get_counter('celery.status')

    def increment(signal):
        counter.increment(signal)

        def _increment(**kwargs):
            pass
        return _increment

    for signal in dir(signals):
        instance = getattr(signals, signal)
        if isinstance(instance, dispatch.Signal):
            instance.connect(increment(signal))

    def start(**kwargs):
        middleware.StatsdMiddleware.start('celery')

    def stop(**kwargs):
        middleware.StatsdMiddleware.stop(kwargs.get('task').name)
        middleware.StatsdMiddleware.scope.timings = None

    def clear(**kwargs):
        middleware.StatsdMiddleware.scope.timings = None

    signals.task_prerun.connect(start)
    signals.task_postrun.connect(stop)
    signals.task_failure.connect(clear)

except ImportError:
    pass

