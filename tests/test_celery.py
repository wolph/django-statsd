from unittest import mock

from celery import signals

from django_statsd import celery as statsd_celery
from django_statsd import middleware
from tests.conftest import metric_keys


def _task() -> mock.Mock:
    task = mock.Mock()
    task.name = "tests.sample_task"
    return task


def test_task_prerun_postrun_flow(sent: list) -> None:
    signals.task_prerun.send(sender=None, task_id="1", task=_task())
    assert middleware.StatsdMiddleware.scope.timings is not None

    signals.task_postrun.send(sender=None, task_id="1", task=_task())
    assert middleware.StatsdMiddleware.scope.timings is None

    keys = metric_keys(sent)
    assert "prefix.celery.tests.sample_task.total" in keys
    assert "prefix.celery.tests.sample_task.hit" in keys


def test_status_counters_fire(sent: list) -> None:
    signals.task_prerun.send(sender=None, task_id="2", task=_task())
    signals.task_postrun.send(sender=None, task_id="2", task=_task())
    keys = metric_keys(sent)
    assert "celery.status.task_prerun" in keys
    assert "celery.status.task_postrun" in keys


def test_task_failure_clears_scope(sent: list) -> None:
    signals.task_prerun.send(sender=None, task_id="3", task=_task())
    signals.task_failure.send(sender=None, task_id="3")
    assert middleware.StatsdMiddleware.scope.timings is None
    assert "celery.status.task_failure" in metric_keys(sent)


def test_stop_without_task_is_safe() -> None:
    middleware.StatsdMiddleware.start("celery")
    statsd_celery.stop()
    assert middleware.StatsdMiddleware.scope.timings is None
