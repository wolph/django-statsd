<p align="center">
  <img src="https://raw.githubusercontent.com/WoLpH/django-statsd/master/docs/images/logo.png" alt="django-statsd" width="420">
</p>

<p align="center">
  <a href="https://github.com/WoLpH/django-statsd/actions/workflows/ci.yml"><img src="https://github.com/WoLpH/django-statsd/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://pypi.org/project/django-statsd/"><img src="https://img.shields.io/pypi/v/django-statsd" alt="PyPI"></a>
  <a href="https://pypi.org/project/django-statsd/"><img src="https://img.shields.io/pypi/pyversions/django-statsd" alt="Python"></a>
  <a href="https://pypi.org/project/django-statsd/"><img src="https://img.shields.io/pypi/dm/django-statsd" alt="Downloads"></a>
  <a href="https://django-stats.readthedocs.io/en/latest/"><img src="https://readthedocs.org/projects/django-stats/badge/?version=latest" alt="Documentation"></a>
  <!-- Coveralls is case-sensitive on the owner: WoLpH serves an "unknown" badge. -->
  <a href="https://coveralls.io/github/wolph/django-statsd?branch=master"><img src="https://coveralls.io/repos/github/wolph/django-statsd/badge.svg?branch=master" alt="Coverage"></a>
  <a href="https://github.com/WoLpH/django-statsd/blob/master/LICENSE"><img src="https://img.shields.io/pypi/l/django-statsd" alt="License"></a>
</p>

Two middleware entries, and every view, query, template and Celery task
in your Django project reports its duration to
[statsd](https://github.com/statsd/statsd).

![Metric names arriving as requests are served](https://raw.githubusercontent.com/WoLpH/django-statsd/master/docs/images/terminal.gif)

That recording is real. So is every transcript below: they are produced
by running the code and checked by the test suite, so a claim on this
page cannot outlive the behaviour it describes.

## Quick Start

```bash
pip install django-statsd
```

```python
INSTALLED_APPS = [
    'django_statsd',
]

MIDDLEWARE = [
    'django_statsd.middleware.StatsdMiddleware',
    'django_statsd.middleware.StatsdMiddlewareTimer',
]

STATSD_HOST = '127.0.0.1'
STATSD_PORT = 8125
STATSD_PREFIX = 'myproject'
STATSD_TRACK_MIDDLEWARE = True
```

The tracker goes at the top of `MIDDLEWARE` and the timer at the
bottom. Your own middlewares go between them, and the pair times
everything in between.

## What you get

One `GET /dashboard/` puts this on the wire:

<!-- transcript: views -->
```text
myproject.view.get.myproject.views.dashboard.hit
myproject.view.get.myproject.views.dashboard.process_request
myproject.view.get.myproject.views.dashboard.process_response
myproject.view.get.myproject.views.dashboard.process_view
myproject.view.get.myproject.views.dashboard.total
myproject.view.http_codes.2xx
myproject.view.http_codes.hit
myproject.view.site.hit
```
<!-- /transcript -->

`total` is the request, the three `process_*` names are the phases
inside it, and `hit` is a counter so you get a rate per view without
dividing anything. The last three are project-wide: every request, every
response classified, and this response's status class.

## Features

- **Views** timed by method and dotted view path, with status classes
  counted separately
- **Queries** timed through Django's `execute_wrapper`, nested under
  the view that ran them, so you get query time per view
- **Celery tasks** timed per task, plus a counter for every signal
  Celery exports
- **Templates, `json` and `redis`** patched on import and timed
  without a line of configuration
- **Your own code**, timed through `request.statsd` or the
  module-level helpers, nested under the view that was running
- **Async safe.** The scope lives on `asgiref.local.Local`, so ASGI
  and async views report correctly

## Requirements

- Python 3.10 through 3.14
- Django 5.2, 6.0 or 6.1

Celery and redis are optional. django-statsd patches them if they
import and does nothing if they don't.

## Where your milliseconds go

![Timing breakdown of one request](https://raw.githubusercontent.com/WoLpH/django-statsd/master/docs/images/timing_breakdown.png)

Recorded from a real request. The phases don't sum to
`total`, and the gap is the part of the request outside the section
the middleware pair wraps.

## Usage Examples

Time a block inside a view through `request.statsd`:

```python
def some_view(request):
    with request.statsd.timings('build_queryset'):
        ...

def some_other_view(request):
    request.statsd.timings.start('build_queryset')
    ...
    request.statsd.timings.stop('build_queryset')
```

Or reach the same scope from anywhere during a tracked request, and
from inside a Celery task:

```python
import django_statsd

with django_statsd.with_('payment.authorise'):
    ...

django_statsd.incr('payment.attempt')

@django_statsd.decorator('payment')
def authorise():
    ...
```

Both land nested inside the view that was running, so the same helper
called from two views gives you two series.

## In a dashboard

![django-statsd metrics in Grafana](https://raw.githubusercontent.com/WoLpH/django-statsd/master/docs/images/dashboard.png)

statsd, Graphite and Grafana, fed by django-statsd over UDP. The
compose file and the provisioning that produced this are in
`docs/generate/dashboard/`.

## Settings

| Setting | Default | What it does |
| --- | --- | --- |
| `STATSD_HOST` | `127.0.0.1` | Where to send |
| `STATSD_PORT` | `8125` | Which port |
| `STATSD_PREFIX` | none | Nests every metric under one name |
| `STATSD_TRACK_MIDDLEWARE` | `False` | The view metrics |
| `STATSD_TRACK_DATABASE` | `False` | Query timings |
| `STATSD_SAMPLE_RATE` | `1.0` | Odds a metric is really sent |
| `STATSD_VIEWS_TO_SKIP` | admin | Regexes of views to ignore |
| `STATSD_DISABLED` | `False` | Loaded and silent |
| `STATSD_DEBUG` | `DEBUG` | Warn about unstopped timers |

Full list with docstrings:
[settings reference](https://django-stats.readthedocs.io/en/latest/reference/settings.html).

## Documentation

- [Documentation](https://django-stats.readthedocs.io/en/latest/)
- [Metric reference](https://django-stats.readthedocs.io/en/latest/reference/metrics.html)
- [Changelog](https://github.com/WoLpH/django-statsd/blob/master/CHANGELOG.md)

## Contributing

See [CONTRIBUTING.md](https://github.com/WoLpH/django-statsd/blob/master/CONTRIBUTING.md).
Every code sample on this page is executed by the test suite, so a
change to the API that breaks an example fails the build.

## Links

- [Source](https://github.com/WoLpH/django-statsd)
- [Issues](https://github.com/WoLpH/django-statsd/issues)
- [PyPI](https://pypi.org/project/django-statsd/)

## Support

django-statsd is maintained by [Rick van Hattem](https://github.com/wolph) in his own time.

If it saved you an afternoon, a tip covers an hour of issue triage:
[Ko-fi](https://ko-fi.com/wolph_gh) or [GitHub Sponsors](https://github.com/sponsors/wolph).

If your company funds its dependencies, this package is on
[thanks.dev](https://thanks.dev/u/gh/wolph).

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/wolph_gh)

## License

[BSD 3-Clause](https://github.com/WoLpH/django-statsd/blob/master/LICENSE)
