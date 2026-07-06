from importlib import metadata

import django_statsd


def test_version() -> None:
    assert django_statsd.__version__ == metadata.version('django-statsd')
    assert django_statsd.__version__.startswith('3.')
