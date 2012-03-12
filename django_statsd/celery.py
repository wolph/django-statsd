from __future__ import absolute_import
from django_statsd import middleware

try:
    from celery.signals import task_prerun, task_postrun, task_failure

    def start(**kwargs):
        middleware.StatsdMiddleware.start('celery')

    def stop(**kwargs):
        middleware.StatsdMiddleware.stop(kwargs.get('task').name)
        middleware.StatsdMiddleware.scope.timings = None

    def clear(**kwargs):
        middleware.StatsdMiddleware.scope.timings = None

    task_prerun.connect(start)
    task_postrun.connect(stop)
    task_failure.connect(clear)

except ImportError:
    pass

