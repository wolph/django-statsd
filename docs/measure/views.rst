Measure your views
==================

The question that brings most people here is which view is slow. The
two middlewares answer it without you touching a view.

.. mermaid:: ../generate/flow.mmd

``StatsdMiddleware`` sits at the top of the stack and opens a scope on
the request. ``StatsdMiddlewareTimer`` sits at the bottom and times the
view itself. Everything you install between them is timed by the pair.
Put them the wrong way round and the timer stops a clock nobody
started. The first request tells you so:

.. code-block:: text

    AssertionError: Unable to stop tracking process_response, never
    started tracking it

You find out on the first request in development, so this is a mistake
you make once.

What one request submits
------------------------

.. literalinclude:: ../_transcripts/views.txt
   :language: text

``process_request`` covers the middlewares above the view,
``process_view`` the resolution and the view call, and
``process_response`` the way back out. They don't add up to ``total``,
and the gap is real: it's the part of the request outside the section
the middleware pair wraps.

Errors
------

A view that raises reports under the same name, with two differences:

.. literalinclude:: ../_transcripts/views_error.txt
   :language: text

``process_exception`` appears, and the status counter lands on
``http_codes.5xx``. The view is still timed, so a
view that fails slowly shows up as a slow view and not as a gap.

Skipping views
--------------

Health checks and the admin generate traffic nobody charts.
``STATSD_VIEWS_TO_SKIP`` holds regular expressions matched against the
view name, and the admin is skipped out of the box.

.. code-block:: python

    STATSD_VIEWS_TO_SKIP = [
        r'django.contrib.admin',
        r'myproject.views.health_check',
    ]

Ajax requests
-------------

``STATSD_TAGS_LIKE`` files an ajax view under a tagged name as well as
its plain one, so you can chart the two apart without losing the
combined figure. The separators it understands are ``_is_`` and ``=``.
