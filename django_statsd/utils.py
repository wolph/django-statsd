"""Helpers to build python-statsd connections and clients."""

from typing import Any

import statsd

from django_statsd import settings


def get_connection(
    host: str | None = None,
    port: int | None = None,
    sample_rate: float | None = None,
    disabled: bool | None = None,
) -> Any:
    """Build a python-statsd connection, defaulting to the settings."""
    if not host:
        host = settings.STATSD_HOST

    if not port:
        port = settings.STATSD_PORT

    if not sample_rate:
        sample_rate = settings.STATSD_SAMPLE_RATE

    if not disabled:
        disabled = settings.STATSD_DISABLED

    return statsd.Connection(host, port, sample_rate, disabled)


def get_client(
    name: str,
    connection: Any = None,
    class_: type[Any] = statsd.Client,
) -> Any:
    """Build a python-statsd client of `class_` named `name`."""
    if not connection:
        connection = get_connection()

    return class_(name, connection)


def get_timer(name: str, connection: Any = None) -> Any:
    """Build a :class:`statsd.Timer` named `name`."""
    return get_client(name, connection, statsd.Timer)


def get_counter(name: str, connection: Any = None) -> Any:
    """Build a :class:`statsd.Counter` named `name`."""
    return get_client(name, connection, statsd.Counter)
