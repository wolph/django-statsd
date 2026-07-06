from typing import Any

import pytest
from django_statsd import (
    database,
    middleware,
    settings as statsd_settings,
)

from tests.conftest import metric_keys


@pytest.mark.django_db
def test_database_timing_enabled(
    client: Any,
    sent: list,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(statsd_settings, 'STATSD_TRACK_DATABASE', True)
    response = client.get('/db/')
    assert response.status_code == 200
    metric = 'prefix.view.get.tests.views.db_query.sql.default'
    assert metric in metric_keys(sent)


@pytest.mark.django_db
def test_database_timing_disabled_by_default(
    client: Any,
    sent: list,
) -> None:
    response = client.get('/db/')
    assert response.status_code == 200
    assert not any('sql.default' in key for key in metric_keys(sent))


def test_execute_wrapper_without_scope_passes_through() -> None:
    wrapper = database.statsd_execute_wrapper('other')
    calls: list[str] = []

    def execute(
        sql: str,
        params: Any,
        many: bool,
        context: dict[str, Any],
    ) -> str:
        calls.append(sql)
        return 'result'

    assert wrapper(execute, 'SELECT 1', None, False, {}) == 'result'
    assert calls == ['SELECT 1']


def test_execute_wrapper_records_timing() -> None:
    middleware.StatsdMiddleware.start()
    wrapper = database.statsd_execute_wrapper('other')

    def execute(
        sql: str,
        params: Any,
        many: bool,
        context: dict[str, Any],
    ) -> None:
        return None

    wrapper(execute, 'SELECT 1', None, False, {})
    assert 'sql.other' in middleware.StatsdMiddleware.scope.timings.data
