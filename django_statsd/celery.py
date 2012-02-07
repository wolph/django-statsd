from __future__ import absolute_import

try:
    from celery.signals import task_sent
except ImportError:
    pass

