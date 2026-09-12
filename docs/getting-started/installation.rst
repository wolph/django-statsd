Installation
============

django-statsd needs Python 3.10 or newer and Django 5.2 or newer. It is
tested against Django 5.2, 6.0 and 6.1.

.. code-block:: bash

    pip install django-statsd

That pulls in ``python-statsd`` and ``asgiref`` alongside Django.

Optional integrations
---------------------

celery and redis are not dependencies. django-statsd patches them only
when they import, so installing either one later is enough to start
collecting their metrics. Nothing needs to change in your settings.

Where the metrics go
--------------------

Metrics are sent over UDP to ``127.0.0.1:8125`` unless you say
otherwise, which means a missing statsd server costs you the metrics
rather than the request. See :doc:`../guide/settings` for the host and
port settings.
