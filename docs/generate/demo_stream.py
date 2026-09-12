"""Fire real requests and print each metric as it reaches the wire.

This is what the animation in the README records. Nothing is scripted
output: every line printed is a metric django-statsd really submitted
during the request above it.
"""

from __future__ import annotations

import logging
import os
import sys
import time
from pathlib import Path
from typing import Final

ROOT: Final[Path] = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')

import django

django.setup()

from tests.docs_examples._metrics import (
    _get,
    capture,
    demo_settings,
)

# The demo deliberately requests a view that raises. Django logs that
# traceback at ERROR, which would bury the metrics this is here to show.
logging.getLogger('django.request').setLevel(logging.CRITICAL)

DIM: Final[str] = '\033[2m'
CYAN: Final[str] = '\033[36m'
GREEN: Final[str] = '\033[32m'
YELLOW: Final[str] = '\033[33m'
BOLD: Final[str] = '\033[1m'
OFF: Final[str] = '\033[0m'

REQUESTS: Final[tuple[tuple[str, str], ...]] = (
    ('/dashboard/', 'a plain view'),
    ('/search/', 'a view timing its own code'),
    ('/orders/', 'a view that hits the database'),
    ('/broken/', 'a view that raises'),
)


def colour(name: str, value: str) -> str:
    if value.endswith('|c'):
        return f'{GREEN}{name}{OFF} {DIM}{value}{OFF}'
    return f'{CYAN}{name}{OFF} {DIM}{value}{OFF}'


def main() -> int:
    print(f'{BOLD}django-statsd{OFF} {DIM}listening on the wire{OFF}\n')
    time.sleep(0.6)

    with demo_settings(STATSD_TRACK_DATABASE=True):
        # One warm-up request, so the first visible timing is not the
        # cost of importing half of Django.
        with capture():
            _get('/dashboard/')

        for path, caption in REQUESTS:
            print(f'{YELLOW}GET {path}{OFF} {DIM}{caption}{OFF}')
            time.sleep(0.35)

            with capture() as payloads:
                _get(path, raise_exception=False)

            seen: set[str] = set()
            for payload in payloads:
                for name, value in payload.items():
                    if name in seen:
                        continue
                    seen.add(name)
                    print(f'  {colour(name, str(value))}')
                    time.sleep(0.045)

            print()
            time.sleep(0.5)

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
