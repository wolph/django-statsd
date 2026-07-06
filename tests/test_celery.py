import importlib.util
import sys
import types
from unittest import mock

import pytest
from django_statsd import (
    celery as statsd_celery,
    middleware,
)

from celery import signals
from tests.conftest import metric_keys


def _task() -> mock.Mock:
    task = mock.Mock()
    task.name = 'tests.sample_task'
    return task


def test_task_prerun_postrun_flow(sent: list) -> None:
    signals.task_prerun.send(sender=None, task_id='1', task=_task())
    assert middleware.StatsdMiddleware.scope.timings is not None

    signals.task_postrun.send(sender=None, task_id='1', task=_task())
    assert middleware.StatsdMiddleware.scope.timings is None

    keys = metric_keys(sent)
    assert 'prefix.celery.tests.sample_task.total' in keys
    assert 'prefix.celery.tests.sample_task.hit' in keys


def test_status_counters_fire(sent: list) -> None:
    signals.task_prerun.send(sender=None, task_id='2', task=_task())
    signals.task_postrun.send(sender=None, task_id='2', task=_task())
    keys = metric_keys(sent)
    assert 'celery.status.task_prerun' in keys
    assert 'celery.status.task_postrun' in keys


def test_task_failure_clears_scope(sent: list) -> None:
    signals.task_prerun.send(sender=None, task_id='3', task=_task())
    signals.task_failure.send(sender=None, task_id='3')
    assert middleware.StatsdMiddleware.scope.timings is None
    assert 'celery.status.task_failure' in metric_keys(sent)


def test_stop_without_task_is_safe() -> None:
    middleware.StatsdMiddleware.start('celery')
    statsd_celery.stop()
    assert middleware.StatsdMiddleware.scope.timings is None


def test_celery_signals_unavailable_skips_connection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Simulate `celery` being uninstalled: the module should import
    cleanly with `signals`/`dispatch` set to `None` and skip connecting
    any receivers. Loaded as a standalone module copy (rather than
    reloading `django_statsd.celery` in place) so the real signal
    connections used by the rest of the suite are left untouched."""
    fake_celery = types.ModuleType('celery')
    monkeypatch.setitem(sys.modules, 'celery', fake_celery)
    # `celery.signals` is already cached from the real import at collection
    # time; drop it too so `from celery import signals` actually fails
    # instead of falling back to the cached submodule.
    monkeypatch.delitem(sys.modules, 'celery.signals', raising=False)

    spec = importlib.util.spec_from_file_location(
        'django_statsd._celery_unavailable_test', statsd_celery.__file__
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module.signals is None
    assert module.dispatch is None
