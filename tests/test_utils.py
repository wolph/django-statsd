import statsd
from django_statsd import utils


def test_get_connection_defaults() -> None:
    connection = utils.get_connection()
    assert isinstance(connection, statsd.Connection)


def test_get_connection_explicit() -> None:
    # A numeric IP avoids depending on DNS resolution (real hostnames like
    # "statsd.example.com" are not guaranteed to resolve, e.g. in sandboxed
    # or network-isolated CI runners).
    connection = utils.get_connection(
        host='10.255.255.1', port=9125, sample_rate=0.5, disabled=True
    )
    assert isinstance(connection, statsd.Connection)


def test_get_client_with_connection() -> None:
    connection = utils.get_connection()
    client = utils.get_client('name', connection=connection)
    assert isinstance(client, statsd.Client)
    assert client.name == 'name'


def test_get_timer_and_counter() -> None:
    assert isinstance(utils.get_timer('t'), statsd.Timer)
    assert isinstance(utils.get_counter('c'), statsd.Counter)
