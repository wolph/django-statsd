Measure your own code
=====================

The per-view numbers tell you the view is slow. They don't tell you
which twenty lines of it. For that you time the block yourself, and
django-statsd gives you two ways in.

Through the request
-------------------

Inside a tracked request, ``request.statsd`` is that request's timer.
Use it as a context manager, or start and stop it by hand when the two
ends sit far apart.

.. code-block:: python

    def some_view(request):
        with request.statsd.timings('build_queryset'):
            ...

    def some_other_view(request):
        request.statsd.timings.start('build_queryset')
        ...
        request.statsd.timings.stop('build_queryset')

Through the module
------------------

When the code doing the work has no request to hand, the module-level
helpers reach the same scope from anywhere.

.. code-block:: python

    import django_statsd

    with django_statsd.with_('payment.authorise'):
        ...

    django_statsd.incr('payment.attempt')
    django_statsd.decr('payment.attempt')

    @django_statsd.decorator('payment')
    def authorise():
        ...

What that produces
------------------

Two requests, one using each style:

.. literalinclude:: ../_transcripts/your_own_code.txt
   :language: text

Both names land inside the view that was running:
``search.build_queryset`` and ``checkout.payment.authorise``. That
nesting is the point. The same helper called from two views gives you
two series, so you can see that ``payment.authorise`` is slow from
checkout and fine everywhere else.

``payment.attempt`` sits alongside as a counter, and
``search.json.dumps`` appears without anyone asking for it, because
:doc:`patched-libraries` times the stdlib ``json`` module.

A timer you start and never stop is a bug, and ``STATSD_DEBUG`` makes
django-statsd warn about it. It defaults to your ``DEBUG`` setting, so
you're probably already getting the warnings where you want them.
