Timing your own code
====================

The per-view numbers tell you which view is slow. They do not tell you
which part of it is. For that, time the block yourself.

Through the request
-------------------

Inside a tracked request, ``request.statsd`` is the timer for that
request. Use it as a context manager, or start and stop it by hand when
the two ends are far apart.

.. code-block:: python

    def some_view(request):
        with request.statsd.timings('something_to_time'):
            ...

    def some_other_view(request):
        request.statsd.timings.start('something_to_time')
        ...
        request.statsd.timings.stop('something_to_time')

A timer you start and never stop is a bug django-statsd can warn you
about. Set ``STATSD_DEBUG`` to get those warnings, which defaults to
your ``DEBUG`` setting.

Through the module
------------------

When the code doing the work has no request to hand, the module-level
helpers reach the same scope. They work anywhere during a tracked
request, and inside a celery task as well.

.. code-block:: python

    import django_statsd

    django_statsd.start('my.timer')
    django_statsd.stop('my.timer')

    with django_statsd.with_('my.timer'):
        ...

    django_statsd.incr('my.counter')
    django_statsd.decr('my.counter')

    @django_statsd.decorator('my.prefix')
    def timed_function():
        ...

The decorator names the metric after the function it wraps, under the
prefix you give it. ``django_statsd.wrapper`` and
``django_statsd.named_wrapper`` do the same for a callable you cannot
decorate, which is how the json and template patches are built.
