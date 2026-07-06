from typing import Any

import pytest
from asgiref.sync import async_to_sync
from django.http import HttpRequest, HttpResponse
from django.test import AsyncClient
from django_statsd import (
    middleware,
    settings as statsd_settings,
)

from tests.conftest import metric_keys


def test_basic_request_metrics(client: Any, sent: list) -> None:
    response = client.get('/')
    assert response.status_code == 200
    keys = metric_keys(sent)
    assert 'prefix.view.get.tests.views.index.total' in keys
    assert 'prefix.view.get.tests.views.index.hit' in keys
    assert 'prefix.view.get.tests.views.index.process_request' in keys
    assert 'prefix.view.get.tests.views.index.process_response' in keys
    assert 'prefix.view.site.hit' in keys
    assert 'prefix.view.http_codes.2xx' in keys
    assert 'prefix.view.http_codes.hit' in keys


def test_async_request(sent: list) -> None:
    response = async_to_sync(AsyncClient().get)('/')
    assert response.status_code == 200
    assert 'prefix.view.get.tests.views.index.total' in metric_keys(sent)


def test_exception_counts_5xx(client: Any, sent: list) -> None:
    client.raise_request_exception = False
    response = client.get('/error/')
    assert response.status_code == 500
    assert 'prefix.view.http_codes.5xx' in metric_keys(sent)


def test_ajax_suffix(client: Any, sent: list) -> None:
    client.get('/', headers={'x-requested-with': 'XMLHttpRequest'})
    assert 'prefix.view.get_ajax.tests.views.index.total' in metric_keys(sent)


def test_template_response(client: Any, sent: list) -> None:
    response = client.get('/template/')
    assert response.status_code == 200
    assert b'Hello statsd!' in response.content
    assert 'prefix.view.get.tests.views.template.total' in metric_keys(sent)


def test_skip_view(
    client: Any,
    sent: list,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        statsd_settings, 'STATSD_VIEWS_TO_SKIP', ['tests.views']
    )
    response = client.get('/')
    assert response.status_code == 200
    assert metric_keys(sent) == set()


def test_tags_like_request(
    client: Any,
    sent: list,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(middleware, 'MAKE_TAGS_LIKE', '_is_')
    client.get('/')
    assert (
        'prefix.view.method_is_get.view_is_tests_views_index.is_ajax__is_false.total'
    ) in metric_keys(sent)


def test_get_tags_like_values(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(statsd_settings, 'STATSD_TAGS_LIKE', None)
    assert middleware._get_tags_like() is None
    monkeypatch.setattr(statsd_settings, 'STATSD_TAGS_LIKE', True)
    assert middleware._get_tags_like() == '_is_'
    monkeypatch.setattr(statsd_settings, 'STATSD_TAGS_LIKE', '=')
    assert middleware._get_tags_like() == '='
    monkeypatch.setattr(statsd_settings, 'STATSD_TAGS_LIKE', 'bogus')
    with pytest.warns(UserWarning, match='Unsupported'):
        assert middleware._get_tags_like() is None


def test_stop_without_start_is_safe() -> None:
    middleware.StatsdMiddleware.stop('anything')  # must not raise


def test_process_exception_without_scope_is_safe() -> None:
    mw = middleware.StatsdMiddleware(lambda request: None)  # type: ignore[arg-type,return-value]
    mw.process_exception(HttpRequest(), ValueError('x'))  # must not raise


def test_process_view_callable_class() -> None:
    class CallableView:
        def __call__(self, request: HttpRequest) -> None:
            return None

    middleware.StatsdMiddleware.start()
    mw = middleware.StatsdMiddleware(lambda request: None)  # type: ignore[arg-type,return-value]
    mw.process_view(HttpRequest(), CallableView(), (), {})
    assert (
        middleware.StatsdMiddleware.scope.view_name
        == 'tests.test_middleware.CallableView'
    )


def test_stop_with_partial_scope() -> None:
    middleware.StatsdMiddleware.start()
    middleware.StatsdMiddleware.scope.counter = None
    middleware.StatsdMiddleware.scope.counter_site = None
    middleware.StatsdMiddleware.stop()  # must not raise


def test_process_request_without_track_middleware(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(statsd_settings, 'STATSD_TRACK_MIDDLEWARE', False)
    mw = middleware.StatsdMiddleware(lambda request: None)  # type: ignore[arg-type,return-value]
    request = HttpRequest()
    mw.process_request(request)
    assert (
        'process_request'
        not in middleware.StatsdMiddleware.scope.timings.starts
    )


def test_process_view_without_timings() -> None:
    mw = middleware.StatsdMiddleware(lambda request: None)  # type: ignore[arg-type,return-value]

    def dummy_view(request: HttpRequest) -> None:
        return None

    mw.process_view(HttpRequest(), dummy_view, (), {})
    assert (
        middleware.StatsdMiddleware.scope.view_name
        == 'tests.test_middleware.dummy_view'
    )


def test_process_response_without_scope() -> None:
    mw = middleware.StatsdMiddleware(lambda request: None)  # type: ignore[arg-type,return-value]
    request = HttpRequest()
    request.method = 'GET'
    response = HttpResponse()
    assert mw.process_response(request, response) is response


def test_process_response_tags_like_without_view_name(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(middleware, 'MAKE_TAGS_LIKE', '_is_')
    mw = middleware.StatsdMiddleware(lambda request: None)  # type: ignore[arg-type,return-value]
    request = HttpRequest()
    request.method = 'GET'
    response = HttpResponse()
    assert mw.process_response(request, response) is response


def test_process_template_response_without_scope() -> None:
    mw = middleware.StatsdMiddleware(lambda request: None)  # type: ignore[arg-type,return-value]
    request = HttpRequest()
    response = HttpResponse()
    assert mw.process_template_response(request, response) is response


def test_middleware_timer_noop_when_track_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(statsd_settings, 'STATSD_TRACK_MIDDLEWARE', False)
    assert middleware.StatsdMiddlewareTimer._timings() is None

    timer_mw = middleware.StatsdMiddlewareTimer(lambda request: HttpResponse())
    request = HttpRequest()
    response = HttpResponse()

    timer_mw.process_request(request)  # no-op
    timer_mw.process_view(request, lambda r: None, (), {})  # no-op
    assert timer_mw.process_response(request, response) is response
    timer_mw.process_exception(request, ValueError('x'))  # no-op
    assert timer_mw.process_template_response(request, response) is response
