Quickstart
==========

One app entry and two middlewares. The order is the only fiddly part:
the tracker goes at the top of the stack and the timer at the bottom,
so that between them they wrap everything else you run.

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
    STATSD_PREFIX = 'myproject'
    STATSD_TRACK_MIDDLEWARE = True

Your own middlewares go between those two entries.

``STATSD_TRACK_MIDDLEWARE`` defaults to ``False``, so the middlewares
install and stay quiet until you set it. That lets the configuration
change land in one deploy and the metrics in the next.

The first request
-----------------

One ``GET /dashboard/`` against that configuration puts this on the
wire:

.. literalinclude:: ../_transcripts/views.txt
   :language: text

Eight metrics from one request, and the shape repeats for every view
you have. ``myproject`` is your ``STATSD_PREFIX`` and ``view`` is the
middleware's own prefix. Then comes the HTTP method and the dotted path
of the view function, so ``dashboard`` here is
``myproject.views.dashboard``.

Under that name, ``total`` is the whole request and ``process_request``,
``process_view`` and ``process_response`` are the three phases inside
it. ``hit`` is a counter. That is how you get a request rate per view
without dividing anything.

The last two are project-wide: ``view.site.hit`` counts every request
that django-statsd saw, and ``view.http_codes.2xx`` counts this
response's status class.

:doc:`../measure/views` takes those apart properly. If you want the
full list of names first, it's in :doc:`../reference/metrics`.
