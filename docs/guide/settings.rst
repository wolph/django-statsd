.. _settings:

Settings
========

Every setting is read through :func:`django_statsd.settings.get_setting`,
which falls back to the default when Django is not configured yet
instead of raising. The full list with its docstrings is in
:mod:`django_statsd.settings`.

The ones you are most likely to set:

.. code-block:: python

    STATSD_HOST = '127.0.0.1'
    STATSD_PORT = 8125
    STATSD_PREFIX = 'myproject'
    STATSD_SAMPLE_RATE = 1.0

    STATSD_TRACK_MIDDLEWARE = True
    STATSD_TRACK_DATABASE = True

    STATSD_DEBUG = False
    STATSD_DISABLED = False

``STATSD_PREFIX`` nests everything under one name, which is what you
want as soon as a second project reports to the same statsd.

``STATSD_SAMPLE_RATE`` is the probability that a given metric is
actually submitted, between 0 and 1. Lower it when the volume costs more
than the resolution is worth.

``STATSD_DISABLED`` keeps the whole package loaded and quiet, which is
more convenient in a test suite than removing the middlewares.

``STATSD_DEBUG`` warns about timers that were started and never
stopped. It defaults to your ``DEBUG`` setting.
