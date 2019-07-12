from django.core import exceptions
from django.conf import settings


def get_setting(key, default=None):
    try:
        value = getattr(settings, key, default)
    except exceptions.ImproperlyConfigured:
        value = default

    return value


#: Enable tracking all requests using the middleware
STATSD_TRACK_MIDDLEWARE = get_setting('STATSD_TRACK_MIDDLEWARE', False)

#: Set the global statsd prefix if needed. Otherwise use the root
STATSD_PREFIX = get_setting('STATSD_PREFIX')

#: Enable warnings such as timers which are started but not finished. Defaults
#: to DEBUG if not configured
STATSD_DEBUG = get_setting('STATSD_DEBUG', get_setting('DEBUG'))

#: Statsd disabled mode, avoids to send metrics to the real server.
#: Useful for debugging purposes.
STATSD_DISABLED = get_setting('STATSD_DISABLED', False)

#: Enable creating tags as well as the bare version. This causes an ajax view
#: to be stored both as the regular view name and as the ajax tag. Supported
#: separators are _is_ and =
STATSD_TAGS_LIKE = get_setting('STATSD_TAGS_LIKE')

#: Statsd host, defaults to 127.0.0.1
STATSD_HOST = get_setting('STATSD_HOST', '127.0.0.1')

#: Statsd port, defaults to 8125
STATSD_PORT = get_setting('STATSD_PORT', 8125)

#: Statsd sample rate, lowering this decreases the (random) odds of actually
#: submitting the data. Between 0 and 1 where 1 means always
STATSD_SAMPLE_RATE = get_setting('STATSD_SAMPLE_RATE', 1.0)

#: List of regexp to ignore views.
STATSD_VIEWS_TO_SKIP = get_setting('STATSD_VIEWS_TO_SKIP', [
    r'django.contrib.admin',
])

