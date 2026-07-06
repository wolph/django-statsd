"""django-statsd: submit Django query and view durations to statsd."""

from importlib import metadata

from django_statsd import celery, json, redis, templates
from django_statsd.middleware import (
    decorator,
    decr,
    incr,
    named_wrapper,
    start,
    stop,
    with_,
    wrapper,
)

__version__: str = metadata.version('django-statsd')

__all__ = [
    'celery',
    'decorator',
    'decr',
    'incr',
    'json',
    'named_wrapper',
    'redis',
    'start',
    'stop',
    'templates',
    'with_',
    'wrapper',
]
