from typing import Any

import pytest

from django_statsd import middleware
from django_statsd import settings as statsd_settings
from tests.conftest import metric_keys


def test_client_submit_not_implemented() -> None:
    with pytest.raises(NotImplementedError):
        middleware.Client().submit()


def test_client_prefix_filters_empty_parts(sent: list) -> None:
    client = middleware.Counter("c")
    assert client.get_client(None, "x").name == "prefix.c.x"


def test_counter_submit_skips_zero(sent: list) -> None:
    counter = middleware.Counter("c")
    counter.increment("a")
    counter.increment("b")
    counter.decrement("b")
    counter.submit()
    assert metric_keys(sent) == {"prefix.c.a"}


def test_timer_nested_same_key() -> None:
    timer = middleware.Timer("t")
    timer.start("x")
    timer.start("x")
    assert timer.stop("x") >= 0
    assert timer.stop("x") >= 0
    assert "x" not in timer.starts


def test_timer_stop_without_start() -> None:
    timer = middleware.Timer("t")
    with pytest.raises(AssertionError, match="never started"):
        timer.stop("missing")


def test_timer_debug_detects_unstopped(
    sent: list,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(statsd_settings, "STATSD_DEBUG", True)
    timer = middleware.Timer("t")
    timer.start("x")
    with pytest.raises(AssertionError, match="never"):
        timer.submit()


def test_with_timer_context(sent: list) -> None:
    timer = middleware.Timer("t")
    with timer("inner"):
        pass
    assert "inner" in timer.data


def test_module_helpers_with_scope(sent: list) -> None:
    middleware.StatsdMiddleware.start()
    scope = middleware.StatsdMiddleware.scope
    middleware.start("key")
    assert middleware.stop("key") is not None
    with middleware.with_("ctx"):
        pass
    middleware.incr("counted")
    middleware.decr("counted")
    middleware.incr("counted")
    assert "ctx" in scope.timings.data
    assert scope.counter.data["counted"] == 1


def test_module_helpers_without_scope() -> None:
    middleware.start("key")  # no-op
    assert middleware.stop("key") is None
    assert isinstance(middleware.with_("ctx"), middleware.DummyWith)
    with middleware.with_("ctx"):
        pass
    middleware.incr("x")  # no-op
    middleware.decr("x")  # no-op


def test_wrapper_and_decorator(sent: list) -> None:
    middleware.StatsdMiddleware.start()
    scope = middleware.StatsdMiddleware.scope

    @middleware.decorator("deco")
    def sample_function() -> str:
        return "ok"

    assert sample_function() == "ok"
    assert "deco.sample_function" in scope.timings.data

    def named(value: Any) -> Any:
        return value

    wrapped = middleware.named_wrapper("custom_name", named)
    assert wrapped(42) == 42
    assert "custom_name" in scope.timings.data
