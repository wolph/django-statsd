The middlewares
===============

django-statsd ships two middlewares that work as a pair.
``StatsdMiddleware`` opens the scope and submits the per-view metrics.
``StatsdMiddlewareTimer`` closes the timers that measure everything
inside the stack. Install the first at the top of ``MIDDLEWARE`` and the
second at the bottom.

.. code-block:: python

    MIDDLEWARE = [
        'django_statsd.middleware.StatsdMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django_statsd.middleware.StatsdMiddlewareTimer',
    ]

Put them the other way around and the timer stops a clock the tracker
never started.

The request scope
-----------------

The scope lives on :class:`asgiref.local.Local`, so it is correct under
ASGI and async views as well as WSGI. Each request gets its own scope,
and the view name is stored on the request rather than on the middleware
instance, which is what keeps two concurrent requests from reporting
each other's timings.

Skipping views
--------------

Some views are not worth measuring. ``STATSD_VIEWS_TO_SKIP`` holds
regular expressions matched against the view name, and defaults to
skipping the Django admin.

.. code-block:: python

    STATSD_VIEWS_TO_SKIP = [
        r'django.contrib.admin',
        r'myproject.views.health_check',
    ]

Ajax requests
-------------

``STATSD_TAGS_LIKE`` stores an ajax view under both its plain name and a
tagged variant, so you can chart the two separately without losing the
combined number. The supported separators are ``_is_`` and ``=``.
