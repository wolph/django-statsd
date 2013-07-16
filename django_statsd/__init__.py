from django_statsd.middleware import (
    decr,
    incr,
    start,
    stop,
    with_,
    wrapper,
    named_wrapper,
    decorator,
)
from django_statsd import redis, celery, json, templates

__all__ = [
    'decr',
    'incr',
    'start',
    'stop',
    'with_',
    'wrapper',
    'named_wrapper',
    'decorator',
    'json',
    'redis',
    'celery',
    'templates',
    #'urls',
]

__name__ = 'python-statsd'
__version__ = '1.9.0'
__author__ = 'Rick van Hattem'
__author_email__ = 'Rick.van.Hattem@Fawo.nl'
__description__ = '''django-statsd is a django app that submits query and 
    view durations to Etsy's statsd.'''
__url__ = 'https://github.com/WoLpH/django-statsd'

