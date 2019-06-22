import statsd
from . import settings


def get_connection(host=None, port=None, sample_rate=None, disabled=None):
    if not host:
        host = settings.STATSD_HOST

    if not port:
        port = settings.STATSD_PORT

    if not sample_rate:
        sample_rate = settings.STATSD_SAMPLE_RATE

    if not disabled:
        disabled = settings.STATSD_DISABLED

    return statsd.Connection(host, port, sample_rate, disabled)


def get_client(name, connection=None, class_=statsd.Client):
    if not connection:
        connection = get_connection()

    return class_(name, connection)


def get_timer(name, connection=None):
    return get_client(name, connection, statsd.Timer)


def get_counter(name, connection=None):
    return get_client(name, connection, statsd.Counter)
