"""Celery signal integration submitting task counters and timings."""

from collections.abc import Callable
from typing import Any

from django_statsd import middleware, utils

try:
    from celery.utils import dispatch

    from celery import signals
except ImportError:  # pragma: no cover
    # celery ships no type information (see [[tool.mypy.overrides]]),
    # so `signals`/`dispatch` are already typed `Any` for mypy and
    # reassigning `None` here needs no ignore there. ty resolves the
    # real celery submodules instead, so it needs its own suppression.
    signals = None  # ty: ignore[invalid-assignment]
    dispatch = None  # ty: ignore[invalid-assignment]


if signals is not None and dispatch is not None:
    counter = utils.get_counter('celery.status')

    def _make_increment(signal_name: str) -> Callable[..., None]:
        def _increment(**kwargs: Any) -> None:
            counter.increment(signal_name)

        return _increment

    for _signal_name in dir(signals):
        _instance = getattr(signals, _signal_name)
        if isinstance(_instance, dispatch.Signal):
            # weak=False: the receiver is a closure that would otherwise
            # be garbage collected immediately and never fire.
            _instance.connect(_make_increment(_signal_name), weak=False)

    def start(**kwargs: Any) -> None:
        middleware.StatsdMiddleware.start('celery')

    def stop(task: Any = None, **kwargs: Any) -> None:
        if task is not None:
            middleware.StatsdMiddleware.stop(task.name)
        middleware.StatsdMiddleware.scope.timings = None

    def clear(**kwargs: Any) -> None:
        middleware.StatsdMiddleware.scope.timings = None

    signals.task_prerun.connect(start)
    signals.task_postrun.connect(stop)
    signals.task_failure.connect(clear)
