Measure your queries
====================

A slow view is usually a slow query, and the per-view timing won't tell
you which of the two it is. Turn on database timing and it will.

.. code-block:: python

    STATSD_TRACK_DATABASE = True

The middleware wraps every configured connection through Django's
``connection.execute_wrapper()`` for the duration of the request, then
unwraps it. Code that runs outside a request is left alone.

.. literalinclude:: ../_transcripts/queries.txt
   :language: text

The interesting line is the fifth. ``sql.default`` is nested inside the
view's own name, so you get query time per view. A single figure for
the whole site would leave you guessing which view to open.
``default`` is the alias
from your ``DATABASES`` setting, which means a project with a read
replica reports ``sql.default`` and ``sql.replica`` side by side.

The timing covers execution. Building the queryset in Python happens
before any of this and lands in the enclosing view timing instead, so a
view that is slow with a fast ``sql.default`` is telling you the
problem isn't the database.

A note on 3.0
-------------

This is new in 3.0 and off by default. Earlier versions shipped a
cursor subclass that never worked on Python 3, so they collected no
query timings at all whatever the documentation said at the time.
