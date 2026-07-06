import importlib
import json

from django.template import loader
from django_statsd import (
    json as statsd_json,
    middleware,
    redis as statsd_redis,
    templates as statsd_templates,
)

import redis as redis_lib


def test_json_patched() -> None:
    assert getattr(json, 'statsd_patched', False)
    middleware.StatsdMiddleware.start()
    assert json.dumps({'a': 1}) == '{"a": 1}'
    assert json.loads('{"a": 1}') == {'a': 1}
    assert 'json.dumps' in middleware.StatsdMiddleware.scope.timings.data
    assert 'json.loads' in middleware.StatsdMiddleware.scope.timings.data


def test_json_reimport_does_not_double_patch() -> None:
    inner = json.dumps.__wrapped__  # type: ignore[attr-defined]
    importlib.reload(statsd_json)
    assert json.dumps.__wrapped__ is inner  # type: ignore[attr-defined]


def test_template_render_patched() -> None:
    assert getattr(loader, 'statsd_patched', False)
    middleware.StatsdMiddleware.start()
    result = loader.render_to_string('example.html', {'name': 'x'})
    assert 'Hello x!' in result
    assert 'render_django' in middleware.StatsdMiddleware.scope.timings.data


def test_template_reimport_does_not_double_patch() -> None:
    inner = loader.render_to_string
    importlib.reload(statsd_templates)
    assert loader.render_to_string is inner


def test_redis_patched(monkeypatch) -> None:
    assert getattr(redis_lib.Redis, 'statsd_patched', False)
    monkeypatch.setattr(
        statsd_redis._original_redis,
        'execute_command',
        lambda self, *args, **kwargs: 'PONG',
    )
    middleware.StatsdMiddleware.start()
    client = redis_lib.Redis()
    assert client.execute_command('PING') == 'PONG'
    assert 'redis.ping' in middleware.StatsdMiddleware.scope.timings.data


def test_redis_reimport_does_not_double_patch() -> None:
    patched = redis_lib.Redis
    importlib.reload(statsd_redis)
    assert redis_lib.Redis is patched


def test_urls_module_removed() -> None:
    import pytest

    with pytest.raises(ImportError):
        importlib.import_module('django_statsd.urls')
