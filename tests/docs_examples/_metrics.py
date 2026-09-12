"""Drive real behaviour and record the metric names it puts on the wire.

The documentation claims a great many things about what django-statsd
submits. Every one of those claims is backed by a transcript generated
here, so a claim that stops being true fails a test instead of quietly
misleading a reader.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

import statsd
from django.http import HttpRequest, HttpResponse
from django.test import RequestFactory
from django_statsd import middleware

TRANSCRIPT_ROOT: Final[Path] = (
    Path(__file__).resolve().parents[2] / 'docs' / '_transcripts'
)


@contextmanager
def capture() -> Iterator[list[dict[str, Any]]]:
    """Collect every payload handed to statsd instead of sending it."""
    captured: list[dict[str, Any]] = []
    original = statsd.Connection.send

    def fake_send(
        self: Any, data: dict[str, Any], sample_rate: Any = None
    ) -> bool:
        captured.append(dict(data))
        return True

    statsd.Connection.send = fake_send  # type: ignore[method-assign]
    try:
        yield captured
    finally:
        statsd.Connection.send = original  # type: ignore[method-assign]


def metric_names(payloads: list[dict[str, Any]]) -> tuple[str, ...]:
    return tuple(sorted({key for payload in payloads for key in payload}))


def through_middleware(
    body: Callable[[HttpRequest], None] | None = None,
    path: str = '/',
) -> None:
    """Run one request through both middlewares, in documented order."""

    def get_response(request: HttpRequest) -> HttpResponse:
        if body is not None:
            body(request)
        return HttpResponse('ok')

    handler = middleware.StatsdMiddleware(
        middleware.StatsdMiddlewareTimer(get_response)
    )
    handler(RequestFactory().get(path))


@dataclass(frozen=True)
class Scenario:
    """One recorded situation and the transcript it produces."""

    name: str
    caption: str
    run: Callable[[], None]

    @property
    def path(self) -> Path:
        return TRANSCRIPT_ROOT / f'{self.name}.txt'

    def record(self) -> str:
        with demo_settings(), capture() as payloads:
            self.run()

        names = list(metric_names(payloads))
        lines = [f'# {self.caption}', '', *names]
        return '\n'.join(lines) + '\n'


#: The prefix the documentation uses throughout.
DEMO_PREFIX: Final[str] = 'myproject'


@contextmanager
def demo_settings(**overrides: Any) -> Iterator[None]:
    """Point django_statsd at the documentation's fictional project.

    The settings module reads Django's settings once at import, so the
    values are patched on the module itself.
    """
    from django_statsd import settings as statsd_settings

    overrides.setdefault('STATSD_PREFIX', DEMO_PREFIX)
    previous = {key: getattr(statsd_settings, key) for key in overrides}
    for key, value in overrides.items():
        setattr(statsd_settings, key, value)
    try:
        yield
    finally:
        for key, value in previous.items():
            setattr(statsd_settings, key, value)


DEMO_URLCONF: Final[str] = 'tests.docs_examples._demo'


def _get(path: str, raise_exception: bool = True) -> None:
    from django.test import Client
    from django.test.utils import override_settings

    with override_settings(ROOT_URLCONF=DEMO_URLCONF):
        client = Client()
        client.raise_request_exception = raise_exception
        client.get(path)


def _task(name: str) -> Any:
    from unittest import mock

    task = mock.Mock()
    task.name = name
    return task


def _views() -> None:
    _get('/dashboard/')


def _view_error() -> None:
    _get('/broken/', raise_exception=False)


def _queries() -> None:
    with demo_settings(STATSD_TRACK_DATABASE=True):
        _get('/orders/')


def _celery() -> None:
    from celery import signals

    task = _task('myproject.tasks.send_invoice')
    signals.task_prerun.send(sender=None, task_id='1', task=task)
    signals.task_postrun.send(sender=None, task_id='1', task=task)
    signals.task_failure.send(sender=None, task_id='2')


def _your_own_code() -> None:
    _get('/search/')
    _get('/checkout/')


def _patched_libraries() -> None:
    _get('/report/')


SCENARIOS: Final[tuple[Scenario, ...]] = (
    Scenario('views', 'GET /dashboard/', _views),
    Scenario('views_error', 'GET /broken/, which raises', _view_error),
    Scenario(
        'queries', 'GET /orders/ with STATSD_TRACK_DATABASE on', _queries
    ),
    Scenario('celery', 'One task, run and then failed', _celery),
    Scenario(
        'your_own_code', 'GET /search/ and GET /checkout/', _your_own_code
    ),
    Scenario(
        'patched_libraries',
        'GET /report/, which renders a template',
        _patched_libraries,
    ),
)


PAYLOAD_PATH: Final[Path] = TRANSCRIPT_ROOT / 'payload.txt'


def record_payload() -> str:
    """One real payload, durations and all.

    The numbers here came from one run on one machine, so this
    transcript is recorded rather than asserted. The test only checks
    that the names in it are names django-statsd really submits.
    """
    with demo_settings(), capture() as payloads:
        _get('/search/')

    lines = ['# One request, as handed to statsd', '']
    for payload in payloads:
        for name, value in sorted(payload.items()):
            lines.append(f'{name} {value}')

    return '\n'.join(lines) + '\n'


def payload_names(text: str) -> tuple[str, ...]:
    return tuple(
        line.split(' ', 1)[0]
        for line in text.splitlines()
        if line and not line.startswith('#')
    )


CHART_PATH: Final[Path] = TRANSCRIPT_ROOT / 'chart_data.txt'


def _common_prefix(names: tuple[str, ...]) -> str:
    """The shared `view.get.myproject.views.x.` part of a metric name."""
    if not names:
        return ''

    segments = names[0].split('.')
    for name in names[1:]:
        other = name.split('.')
        segments = [
            left
            for left, right in zip(segments, other, strict=False)
            if left == right
        ]
    return '.'.join(segments) + '.' if segments else ''


def record_chart_data() -> str:
    """Timings from a view doing real work, for the breakdown chart."""
    with demo_settings(STATSD_TRACK_DATABASE=True), capture() as payloads:
        _get('/heavy/')

    raw = {
        name: float(value.split('|')[0])
        for payload in payloads
        for name, value in payload.items()
        if value.endswith('|ms')
    }
    prefix = _common_prefix(tuple(raw))
    timings = {name[len(prefix) :]: value for name, value in raw.items()}
    lines = ['# Milliseconds, one run of GET /heavy/', '']
    lines.extend(
        f'{name} {value:.3f}'
        for name, value in sorted(timings.items(), key=lambda item: -item[1])
    )
    return '\n'.join(lines) + '\n'


OVERHEAD_PATH: Final[Path] = TRANSCRIPT_ROOT / 'database_overhead.txt'


def record_database_overhead(rounds: int = 300) -> str:
    """Time the same view with and without query timing.

    STATSD_TRACK_DATABASE wraps every connection for the duration of a
    request, which sounds expensive until it is measured. One machine,
    one run, so the ratio is the part worth reading.
    """
    import time

    def run(rounds: int, *, tracking: bool) -> float:
        with demo_settings(STATSD_TRACK_DATABASE=tracking), capture():
            _get('/orders/')  # warm up
            start = time.perf_counter()
            for _ in range(rounds):
                _get('/orders/')
            return (time.perf_counter() - start) / rounds * 1000

    off = run(rounds, tracking=False)
    on = run(rounds, tracking=True)

    return (
        '\n'.join(
            [
                f'# Mean ms per GET /orders/, {rounds} requests each',
                '',
                f'STATSD_TRACK_DATABASE off  {off:.3f}',
                f'STATSD_TRACK_DATABASE on   {on:.3f}',
                (
                    f'overhead                   {on - off:+.3f} ms '
                    f'({(on / off - 1) * 100:+.1f}%)'
                ),
            ]
        )
        + '\n'
    )
