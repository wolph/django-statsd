"""A fictional application whose metrics the documentation shows.

django-statsd names a view metric after the view's own `__module__`, so
these views declare `myproject.views` and really report under it. That
keeps one set of names: what a transcript records, what the dashboard
screenshot draws, and what the documentation prints are the same
strings, with nothing rewritten afterwards.
"""

from __future__ import annotations

import json
from typing import Final

import django_statsd
from django.db import connection
from django.http import HttpRequest, HttpResponse
from django.template import loader
from django.urls import path

#: The name a reader should see, and the name these really report under.
DEMO_MODULE: Final[str] = 'myproject.views'


def dashboard(request: HttpRequest) -> HttpResponse:
    return HttpResponse('ok')


def search(request: HttpRequest) -> HttpResponse:
    with request.statsd.timings('build_queryset'):
        json.dumps({'results': []})
    return HttpResponse('ok')


def render_report(request: HttpRequest) -> HttpResponse:
    loader.render_to_string('example.html', {'name': 'report'})
    return HttpResponse('ok')


def checkout(request: HttpRequest) -> HttpResponse:
    with django_statsd.with_('payment.authorise'):
        pass
    django_statsd.incr('payment.attempt')
    return HttpResponse('ok')


def orders(request: HttpRequest) -> HttpResponse:
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
    return HttpResponse('ok')


def heavy_report(request: HttpRequest) -> HttpResponse:
    """Do enough real work to be worth charting.

    The durations in the documentation's chart come from this view. The
    work is real, not a sleep: a few hundred template renders, a real
    serialisation and a handful of queries. It is still a demo, so the
    absolute numbers say more about the machine than about your site.
    """
    rows = [{'id': index, 'name': f'row-{index}'} for index in range(2000)]

    with connection.cursor() as cursor:
        for _ in range(20):
            cursor.execute('SELECT 1')

    for _ in range(200):
        loader.render_to_string('example.html', {'name': 'report'})

    json.dumps(rows)
    return HttpResponse('ok')


def broken(request: HttpRequest) -> HttpResponse:
    raise ValueError('boom')


for _view in (
    dashboard,
    search,
    render_report,
    checkout,
    orders,
    heavy_report,
    broken,
):
    _view.__module__ = DEMO_MODULE


urlpatterns = [
    path('dashboard/', dashboard),
    path('search/', search),
    path('report/', render_report),
    path('checkout/', checkout),
    path('orders/', orders),
    path('heavy/', heavy_report),
    path('broken/', broken),
]
