.. _settings:

Settings reference
==================

Every setting goes through :func:`django_statsd.settings.get_setting`,
which returns the default when Django isn't configured yet. It won't
raise at import time. Each one's docstring is in
:mod:`django_statsd.settings`.

The ones you'll actually set:

.. code-block:: python

    STATSD_HOST = '127.0.0.1'
    STATSD_PORT = 8125
    STATSD_PREFIX = 'myproject'
    STATSD_SAMPLE_RATE = 1.0

    STATSD_TRACK_MIDDLEWARE = True
    STATSD_TRACK_DATABASE = True

    STATSD_DEBUG = False
    STATSD_DISABLED = False

``STATSD_PREFIX`` nests everything under one name. You want it as soon
as a second project reports to the same statsd, and it costs nothing to
set on the first.

``STATSD_SAMPLE_RATE`` is the odds that any given metric is really
submitted, between 0 and 1. Lowering it is worth considering only on a
really high volume site. The performance impact is usually negligible
either way.

``STATSD_TRACK_MIDDLEWARE`` is the master switch for the view metrics
and defaults to ``False``. ``STATSD_TRACK_DATABASE`` does the same for
query timings, and :doc:`../measure/queries` measures what it costs.

``STATSD_DISABLED`` keeps the package loaded and silent, which is
easier in a test suite than pulling the middlewares out of the stack.

``STATSD_DEBUG`` warns about timers that were started and never
stopped. It defaults to your ``DEBUG`` setting.

``STATSD_VIEWS_TO_SKIP`` and ``STATSD_TAGS_LIKE`` are covered in
:doc:`../measure/views`.
