"""Record the Grafana screenshot in the README.

Brings up statsd, graphite and grafana in docker, drives real Django
requests at them through django-statsd, waits for graphite to aggregate,
and screenshots the dashboard. Every series on the picture came from
this package submitting real metrics over UDP.

Run through `tox -e docs-assets`. Takes several minutes, because a
dashboard of a five second window would show nothing worth looking at.
"""

from __future__ import annotations

import json
import logging
import os
import random
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Final

ROOT: Final[Path] = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')

COMPOSE_DIR: Final[Path] = ROOT / 'examples'
OUTPUT: Final[Path] = ROOT / 'docs' / 'images' / 'dashboard.png'

GRAPHITE: Final[str] = 'http://127.0.0.1:18280/'
GRAFANA: Final[str] = 'http://127.0.0.1:13200/'
DASHBOARD: Final[str] = (
    'http://127.0.0.1:13200/d/django-statsd/django-statsd'
    '?kiosk&from=now-12m&to=now'
)

#: Weighted so the picture looks like a site, not a benchmark.
TRAFFIC: Final[tuple[tuple[str, int], ...]] = (
    ('/dashboard/', 12),
    ('/search/', 9),
    ('/orders/', 7),
    ('/report/', 4),
    ('/checkout/', 3),
    ('/broken/', 1),
)

TRAFFIC_SECONDS: Final[int] = int(
    os.environ.get('DJANGO_STATSD_TRAFFIC_SECONDS', '420')
)

#: Each request sends roughly eight UDP packets. Docker Desktop forwards
#: UDP through a proxy that drops them well before a hundred a second,
#: which shows up as counters that never leave zero. Two requests a
#: second keeps every packet.
REQUEST_INTERVAL: Final[float] = float(
    os.environ.get('DJANGO_STATSD_REQUEST_INTERVAL', '0.45')
)


def compose(*args: str) -> None:
    subprocess.run(['docker', 'compose', *args], cwd=COMPOSE_DIR, check=True)


def wait_for(url: str, label: str, timeout: int = 180) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=4) as response:
                if response.status < 500:
                    print(f'{label} is up')
                    return
        except (urllib.error.URLError, OSError, TimeoutError):
            time.sleep(2)

    raise SystemExit(f'{label} never came up at {url}')


def drive_traffic(seconds: int) -> None:
    import django

    django.setup()

    # One of the views raises on purpose, to put a 5xx series on the
    # dashboard. Its traceback would otherwise fill the log.
    logging.getLogger('django.request').setLevel(logging.CRITICAL)

    from tests.docs_examples._metrics import _get, demo_settings

    paths = [path for path, weight in TRAFFIC for _ in range(weight)]
    deadline = time.monotonic() + seconds
    sent = 0

    with demo_settings(
        STATSD_HOST='127.0.0.1',
        STATSD_PORT=18225,
        STATSD_TRACK_DATABASE=True,
    ):
        while time.monotonic() < deadline:
            _get(random.choice(paths), raise_exception=False)
            sent += 1
            if sent % 100 == 0:
                remaining = int(deadline - time.monotonic())
                print(f'{sent} requests, {remaining}s left')
            time.sleep(REQUEST_INTERVAL)

    print(f'{sent} requests sent')


def screenshot(output: Path) -> None:
    from playwright.sync_api import sync_playwright

    output.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(
            # The four panels are seventeen grid rows tall, which comes
            # to roughly this once the kiosk bar is counted.
            viewport={'width': 1600, 'height': 780},
            device_scale_factor=2,
        )
        # Not networkidle: Grafana keeps talking to its backend, so
        # the page never goes quiet and the wait times out.
        page.goto(DASHBOARD, wait_until='domcontentloaded')
        page.wait_for_selector('[data-viz-panel-key]', timeout=60_000)
        page.wait_for_timeout(9000)
        page.screenshot(path=str(output))
        browser.close()

    print(f'wrote {output.relative_to(ROOT)}')


def assert_graphite_has_data() -> None:
    """Fail loudly rather than screenshotting four empty panels."""
    probe = (
        'http://127.0.0.1:18280/render?format=json&from=-15min'
        '&target=stats.timers.myproject.view.get.myproject.views.dashboard.total.count'
    )
    with urllib.request.urlopen(probe, timeout=10) as response:
        series = json.loads(response.read())

    points = [
        point
        for entry in series
        for point, _ in entry.get('datapoints', [])
        if point is not None
    ]
    if not points:
        raise SystemExit(
            'graphite has no data for the dashboard view timer. '
            'The metric names in the dashboard and the ones '
            'django-statsd submits have probably drifted apart.'
        )

    print(f'graphite has {len(points)} points to draw')


def main() -> int:
    # A stack left up by an earlier run still holds port 8125, and the
    # error docker gives for that is easy to misread as a broken
    # compose file.
    subprocess.run(
        ['docker', 'compose', 'down', '-v'],
        cwd=COMPOSE_DIR,
        check=False,
        capture_output=True,
    )
    time.sleep(3)
    compose('up', '-d')
    try:
        wait_for(GRAPHITE, 'graphite')
        wait_for(GRAFANA, 'grafana')
        drive_traffic(TRAFFIC_SECONDS)
        print('waiting for graphite to aggregate')
        time.sleep(30)
        assert_graphite_has_data()
        screenshot(OUTPUT)
    finally:
        if os.environ.get('DJANGO_STATSD_KEEP_STACK') == '1':
            print('leaving the stack up (DJANGO_STATSD_KEEP_STACK=1)')
        else:
            compose('down', '-v')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
