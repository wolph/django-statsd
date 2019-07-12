Introduction
============

`django_statsd` is a middleware that uses `python-statsd` to log query
and view durations to statsd.

* Documentation
    - http://django-stats.readthedocs.org/en/latest/
* Source
    - https://github.com/WoLpH/django-statsd
* Bug reports
    - https://github.com/WoLpH/django-statsd/issues
* Package homepage
    - https://pypi.python.org/pypi/django-statsd
* Python Statsd
    - https://github.com/WoLpH/python-statsd
* Graphite
    - http://graphite.wikidot.com
* Statsd
    - code: https://github.com/etsy/statsd
    - blog post: http://codeascraft.etsy.com/2011/02/15/measure-anything-measure-everything/


Install
=======

To install simply execute `python setup.py install`.
If you want to run the tests first, run `python setup.py test`


Usage
=====

To install, add the following to your ``settings.py``:

1. ``django_statsd`` to the ``INSTALLED_APPS`` setting.
2. ``django_statsd.middleware.StatsdMiddleware`` to the **top** of your
    ``MIDDLEWARE_CLASSES``
3. ``django_statsd.middleware.StatsdMiddlewareTimer`` to the **bottom** of your
    ``MIDDLEWARE_CLASSES``

Configuration
-------------
You can configure ``django-statsd`` using the Django settings config:

    >>> # Settings
    ... STATSD_HOST = '127.0.0.1'
    ... STATSD_PORT = 12345

The full list of configurations is available in ReadTheDocs_.

.. _ReadTheDocs: https://django-stats.readthedocs.io/en/latest/django_statsd.html#module-django_statsd.settings


Advanced Usage
--------------

    >>> def some_view(request):
    ...     with request.timings('something_to_time'):
    ...         # do something here
    ...         pass
    >>>
    >>> def some_view(request):
    ...     request.timings.start('something_to_time')
    ...     # do something here
    ...     request.timings.stop('something_to_time')
