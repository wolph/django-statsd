Installation
============

.. code-block:: bash

    pip install django-statsd

That brings in Django, ``python-statsd`` and ``asgiref``.

You need Python 3.10 or newer and Django 5.2 or newer. The test matrix
runs Django 5.2, 6.0 and 6.1 across Python 3.10 through 3.14.

Celery and redis
----------------

Neither is a dependency. django-statsd patches them when they import
and does nothing when they don't, so installing either one later starts
its metrics without a settings change.

Where the metrics go
--------------------

statsd speaks UDP, and django-statsd doesn't wait for a reply. A statsd
server that is down or absent costs you the metrics and leaves the
request alone. The default target is ``127.0.0.1:8125``, which
:doc:`../reference/settings` shows you how to change.
