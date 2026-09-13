"""Keep the recorded metric transcripts honest.

Each transcript is regenerated here and compared with the committed
file. A change in what django-statsd puts on the wire fails this test
instead of leaving the documentation quietly wrong.

Regenerate with `tox -e docs-assets`, or::

    DJANGO_STATSD_REGENERATE=1 pytest tests/docs_examples/test_transcripts.py
"""

from __future__ import annotations

import os

import pytest

from ._metrics import (
    CHART_PATH,
    OVERHEAD_PATH,
    PAYLOAD_PATH,
    SCENARIOS,
    WIRE_PATH,
    Scenario,
    payload_names,
    record_chart_data,
    record_database_overhead,
    record_payload,
    record_wire,
    wire_names,
)

REGENERATE = os.environ.get('DJANGO_STATSD_REGENERATE') == '1'


@pytest.mark.django_db
@pytest.mark.parametrize(
    'scenario', SCENARIOS, ids=lambda scenario: scenario.name
)
def test_transcript_matches_the_recording(scenario: Scenario) -> None:
    recorded = scenario.record()

    if REGENERATE:
        scenario.path.parent.mkdir(parents=True, exist_ok=True)
        scenario.path.write_text(recorded, encoding='utf-8')
        return

    assert scenario.path.exists(), (
        f'{scenario.path} is missing. Regenerate with tox -e docs-assets'
    )
    assert scenario.path.read_text(encoding='utf-8') == recorded, (
        f'{scenario.path} is stale. Regenerate with tox -e docs-assets'
    )


def test_every_scenario_has_a_distinct_name() -> None:
    names = [scenario.name for scenario in SCENARIOS]
    assert len(names) == len(set(names))


@pytest.mark.django_db
def test_payload_transcript_shows_real_metric_names() -> None:
    """The payload's numbers are from one run, so only names are checked.

    Asserting the durations would mean patching a recording by hand
    every time the machine had a different afternoon.
    """
    if REGENERATE:
        PAYLOAD_PATH.parent.mkdir(parents=True, exist_ok=True)
        PAYLOAD_PATH.write_text(record_payload(), encoding='utf-8')

    assert PAYLOAD_PATH.exists(), (
        f'{PAYLOAD_PATH} is missing. Regenerate with tox -e docs-assets'
    )

    committed = payload_names(PAYLOAD_PATH.read_text(encoding='utf-8'))
    current = payload_names(record_payload())
    assert set(committed) == set(current), (
        f'{PAYLOAD_PATH} names drifted. Regenerate with tox -e docs-assets'
    )


@pytest.mark.django_db
def test_chart_data_is_recorded() -> None:
    """Durations vary per run, so only the shape is asserted."""
    if REGENERATE:
        CHART_PATH.write_text(record_chart_data(), encoding='utf-8')

    assert CHART_PATH.exists()
    names = payload_names(CHART_PATH.read_text(encoding='utf-8'))
    assert 'total' in names
    assert 'sql' in names or 'render_django' in names


def test_documented_middleware_order_error_is_real() -> None:
    """docs/measure/views.rst quotes this assertion. Keep it quotable."""
    from django.http import HttpResponse
    from django.test import RequestFactory
    from django_statsd import middleware

    def view(request: object) -> HttpResponse:
        return HttpResponse('ok')

    reversed_stack = middleware.StatsdMiddlewareTimer(
        middleware.StatsdMiddleware(view)
    )
    with pytest.raises(AssertionError) as raised:
        reversed_stack(RequestFactory().get('/'))

    message = 'Unable to stop tracking process_response'
    assert message in str(raised.value)

    page = (SCENARIOS[0].path.parents[1] / 'measure' / 'views.rst').read_text(
        encoding='utf-8'
    )
    assert message in page, 'views.rst no longer quotes the real error'


@pytest.mark.django_db
def test_database_overhead_is_recorded() -> None:
    """Timings vary per machine, so only the shape is asserted."""
    if REGENERATE:
        OVERHEAD_PATH.write_text(record_database_overhead(), encoding='utf-8')

    assert OVERHEAD_PATH.exists()
    body = OVERHEAD_PATH.read_text(encoding='utf-8')
    assert 'STATSD_TRACK_DATABASE off' in body
    assert 'STATSD_TRACK_DATABASE on' in body
    assert 'overhead' in body


@pytest.mark.django_db
def test_wire_transcript_shows_real_packets() -> None:
    """The quickstart quotes these bytes, so they have to be the bytes.

    Durations differ per run, so the names are asserted and the numbers
    are left alone.
    """
    if REGENERATE:
        WIRE_PATH.write_text(record_wire(), encoding='utf-8')

    assert WIRE_PATH.exists(), (
        f'{WIRE_PATH} is missing. Regenerate with tox -e docs-assets'
    )

    committed = wire_names(WIRE_PATH.read_text(encoding='utf-8'))
    assert set(committed) == set(wire_names(record_wire())), (
        f'{WIRE_PATH} drifted. Regenerate with tox -e docs-assets'
    )
