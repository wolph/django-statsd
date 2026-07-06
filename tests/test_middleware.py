from typing import Any

from tests.conftest import metric_keys


def test_basic_request_metrics(client: Any, sent: list) -> None:
    response = client.get("/")
    assert response.status_code == 200
    keys = metric_keys(sent)
    assert "prefix.view.get.tests.views.index.total" in keys
    assert "prefix.view.get.tests.views.index.hit" in keys
    assert "prefix.view.get.tests.views.index.process_request" in keys
    assert "prefix.view.get.tests.views.index.process_response" in keys
    assert "prefix.view.site.hit" in keys
    assert "prefix.view.http_codes.2xx" in keys
    assert "prefix.view.http_codes.hit" in keys
