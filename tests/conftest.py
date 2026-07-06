"""Shared fixtures: capture statsd traffic, isolate middleware scope."""

from collections.abc import Iterator
from typing import Any

import pytest
import statsd
from django_statsd import middleware

SCOPE_ATTRS = (
    'timings',
    'counter',
    'counter_codes',
    'counter_site',
    'view_name',
)


@pytest.fixture(autouse=True)
def clean_scope() -> Iterator[None]:
    scope = middleware.StatsdMiddleware.scope
    for attr in SCOPE_ATTRS:
        setattr(scope, attr, None)
    yield
    for attr in SCOPE_ATTRS:
        setattr(scope, attr, None)


@pytest.fixture
def sent(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, Any]]:
    """Capture every metric payload passed to statsd.Connection.send."""
    captured: list[dict[str, Any]] = []

    def fake_send(
        self: Any,
        data: dict[str, Any],
        sample_rate: Any = None,
    ) -> bool:
        captured.append(dict(data))
        return True

    monkeypatch.setattr(statsd.Connection, 'send', fake_send)
    return captured


def metric_keys(sent: list[dict[str, Any]]) -> set[str]:
    return {key for payload in sent for key in payload}
