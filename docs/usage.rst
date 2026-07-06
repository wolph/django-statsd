Usage
=====

Install
-------

.. code-block:: bash

    pip install django-statsd

Configuration
-------------

Add the following to your ``settings.py``:

1. ``django_statsd`` to ``INSTALLED_APPS``.
2. ``django_statsd.middleware.StatsdMiddleware`` at the **top** of
   ``MIDDLEWARE``.
3. ``django_statsd.middleware.StatsdMiddlewareTimer`` at the **bottom** of
   ``MIDDLEWARE``.

.. code-block:: python

    STATSD_HOST = '127.0.0.1'
    STATSD_PORT = 8125
    STATSD_TRACK_MIDDLEWARE = True
    STATSD_TRACK_DATABASE = True

All settings are documented in
:mod:`django_statsd.settings`.

Timing code manually
--------------------

.. code-block:: python

    def some_view(request):
        with request.statsd.timings('something_to_time'):
            ...

    def some_other_view(request):
        request.statsd.timings.start('something_to_time')
        ...
        request.statsd.timings.stop('something_to_time')

Or through the module-level helpers, usable anywhere during a tracked
request (or celery task):

.. code-block:: python

    import django_statsd

    django_statsd.start('my.timer')
    django_statsd.stop('my.timer')

    with django_statsd.with_('my.timer'):
        ...

    django_statsd.incr('my.counter')

    @django_statsd.decorator('my.prefix')
    def timed_function():
        ...
