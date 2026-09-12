Quickstart
==========

Two middlewares and one app entry are the whole installation. The order
matters: the tracker goes at the top of the stack and the timer at the
bottom, so that between them they wrap every other middleware you run.

.. code-block:: python

    INSTALLED_APPS = [
        'django_statsd',
    ]

    MIDDLEWARE = [
        'django_statsd.middleware.StatsdMiddleware',
        'django_statsd.middleware.StatsdMiddlewareTimer',
    ]

    STATSD_HOST = '127.0.0.1'
    STATSD_PORT = 8125
    STATSD_TRACK_MIDDLEWARE = True

Your own middlewares go between those two entries. With
``STATSD_TRACK_MIDDLEWARE`` left at its default of ``False`` the
middlewares install but submit nothing, which is a convenient way to
land the configuration change before you turn the metrics on.

What you get
------------

Every request now submits timings and counters keyed by view, under the
``view`` prefix:

* ``view.<method>.<view name>.total`` for the whole request
* ``view.<method>.<view name>.process_request`` and
  ``.process_response`` for the two halves
* ``view.site.hit`` for a bare request counter
* ``view.http_codes.<status class>`` for the response status

Set :ref:`STATSD_PREFIX <settings>` to nest all of that under a name of
your own.
