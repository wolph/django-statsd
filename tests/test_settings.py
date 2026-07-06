from typing import Any

import pytest
from django.core import exceptions
from django_statsd import settings as statsd_settings


def test_get_setting_reads_django_settings() -> None:
    assert statsd_settings.get_setting('STATSD_PREFIX') == 'prefix'


def test_get_setting_default() -> None:
    assert statsd_settings.get_setting('NONEXISTENT_SETTING', 42) == 42


def test_get_setting_improperly_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class Broken:
        def __getattr__(self, name: str) -> Any:
            raise exceptions.ImproperlyConfigured(name)

    monkeypatch.setattr(statsd_settings, 'settings', Broken())
    assert statsd_settings.get_setting('ANY', 'fallback') == 'fallback'


def test_module_defaults() -> None:
    assert statsd_settings.STATSD_HOST == '127.0.0.1'
    assert statsd_settings.STATSD_PORT == 8125
    assert statsd_settings.STATSD_SAMPLE_RATE == 1.0
    assert statsd_settings.STATSD_TRACK_DATABASE is False
    assert statsd_settings.STATSD_VIEWS_TO_SKIP == [r'django.contrib.admin']
