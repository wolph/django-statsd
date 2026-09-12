django-statsd
=============

.. image:: https://raw.githubusercontent.com/WoLpH/django-statsd/master/docs/images/logo.png
   :alt: django-statsd
   :width: 420

Two middleware entries and every view, query, template and Celery task
in your project reports its duration to statsd.

.. image:: https://raw.githubusercontent.com/WoLpH/django-statsd/master/docs/images/terminal.gif
   :alt: Metric names arriving as requests are served

Everything in these pages that claims django-statsd submits a metric
shows you the metric. The transcripts are recorded by really running
the code, and a test fails if one of them stops being true.

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   getting-started/installation
   getting-started/quickstart

.. toctree::
   :maxdepth: 2
   :caption: Measure

   measure/views
   measure/queries
   measure/celery-tasks
   measure/your-own-code
   measure/patched-libraries

.. toctree::
   :maxdepth: 2
   :caption: Reference

   reference/metrics
   reference/settings
   api/index

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
