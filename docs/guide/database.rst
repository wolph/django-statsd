Database query timings
======================

A slow view is often a slow query. Turn on ``STATSD_TRACK_DATABASE`` and
every query submits a timing under ``sql.<connection alias>``.

.. code-block:: python

    STATSD_TRACK_DATABASE = True

The implementation is Django's own
:meth:`~django.db.backends.base.base.BaseDatabaseWrapper.execute_wrapper`
hook. The middleware wraps every configured connection for the duration
of the request and unwraps it afterwards, so nothing leaks into code
that runs outside a request.

This replaced a cursor subclass that never worked on Python 3, which is
why the setting is new in 3.0 rather than on by default. Versions before
3.0 collected no database timings at all, whatever they claimed.

Reading the numbers
-------------------

The alias in the metric name is the key from your ``DATABASES``
setting, so a project with a read replica reports ``sql.default`` and
``sql.replica`` separately. The timing covers execution only. Time spent
building the queryset in Python lands in the enclosing view timing
instead.
