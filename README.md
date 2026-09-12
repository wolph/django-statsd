# django-statsd

[![CI](https://github.com/WoLpH/django-statsd/actions/workflows/ci.yml/badge.svg)](https://github.com/WoLpH/django-statsd/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/django-statsd.svg)](https://pypi.org/project/django-statsd/)
[![Python versions](https://img.shields.io/pypi/pyversions/django-statsd.svg)](https://pypi.org/project/django-statsd/)
[![Documentation](https://readthedocs.org/projects/django-stats/badge/?version=latest)](https://django-stats.readthedocs.io/en/latest/)

`django-statsd` is a Django app that submits query and view durations to
[statsd](https://github.com/statsd/statsd) using
[python-statsd](https://github.com/WoLpH/python-statsd).

- Documentation: <https://django-stats.readthedocs.io/en/latest/>
- Source: <https://github.com/WoLpH/django-statsd>
- Bug reports: <https://github.com/WoLpH/django-statsd/issues>
- PyPI: <https://pypi.org/project/django-statsd/>

## Requirements

- Python 3.10+
- Django 5.2+

## Install

```bash
pip install django-statsd
```

## Usage

Add the following to your `settings.py`:

1. `django_statsd` to `INSTALLED_APPS`.
2. `django_statsd.middleware.StatsdMiddleware` to the **top** of your
   `MIDDLEWARE`.
3. `django_statsd.middleware.StatsdMiddlewareTimer` to the **bottom** of
   your `MIDDLEWARE`.

```python
INSTALLED_APPS = [
    'django_statsd',
    # ...
]

MIDDLEWARE = [
    'django_statsd.middleware.StatsdMiddleware',
    # ...
    'django_statsd.middleware.StatsdMiddlewareTimer',
]

STATSD_HOST = '127.0.0.1'
STATSD_PORT = 8125
STATSD_TRACK_MIDDLEWARE = True

# Optionally, time every database query as `sql.<alias>`:
STATSD_TRACK_DATABASE = True
```

The full list of settings is documented on
[Read the Docs](https://django-stats.readthedocs.io/en/latest/api/index.html#module-django_statsd.settings).

## Advanced usage

Time code inside a view through `request.statsd`:

```python
def some_view(request):
    with request.statsd.timings('something_to_time'):
        ...

def some_other_view(request):
    request.statsd.timings.start('something_to_time')
    ...
    request.statsd.timings.stop('something_to_time')
```

Or anywhere during a tracked request using the module-level helpers:

```python
import django_statsd

with django_statsd.with_('my.timer'):
    ...

django_statsd.incr('my.counter')

@django_statsd.decorator('my.prefix')
def timed_function():
    ...
```

## License

[BSD 3-Clause](https://github.com/WoLpH/django-statsd/blob/master/LICENSE)
