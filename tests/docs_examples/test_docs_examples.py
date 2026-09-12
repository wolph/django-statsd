"""Run every code sample in README.md and docs/.

Gated behind an environment variable because the bash samples build a
virtualenv and install the project into it. Run them with
`tox -e docs-examples`.
"""

from __future__ import annotations

import os
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import pytest
import statsd
from django.http import HttpRequest, HttpResponse
from django.test import RequestFactory
from django_statsd import middleware

from ._docs_examples import (
    PROJECT_ROOT,
    CodeSample,
    InstallSandboxCache,
    call_sample_functions,
    execute_bash_sample,
    execute_python_sample,
    iter_doc_sources,
    runnable_samples,
    validate_dotted_paths,
    validate_statsd_settings,
)

DOC_SOURCES = tuple(
    path for path in iter_doc_sources() if runnable_samples(path)
)

pytestmark = pytest.mark.skipif(
    os.environ.get('DJANGO_STATSD_RUN_DOCS_EXAMPLES') != '1',
    reason='Run the documentation samples via tox -e docs-examples',
)


@pytest.fixture(scope='session')
def install_cache(
    tmp_path_factory: pytest.TempPathFactory,
) -> InstallSandboxCache:
    return InstallSandboxCache(tmp_path_factory.mktemp('docs-installs'))


@pytest.fixture(autouse=True)
def quiet_statsd(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Keep the samples from putting packets on the wire."""

    def fake_send(
        self: Any, data: dict[str, Any], sample_rate: Any = None
    ) -> bool:
        return True

    monkeypatch.setattr(statsd.Connection, 'send', fake_send)
    yield


def run_in_tracked_request(
    body: Callable[[HttpRequest], None],
) -> None:
    """Run `body` inside a request the middleware is timing.

    The module-level helpers are documented as usable "anywhere during a
    tracked request", so that is the context the samples get. Both
    middlewares are installed, in the documented order, because they pair
    up: the timer at the bottom of the stack starts what the tracker at
    the top stops.
    """

    def get_response(request: HttpRequest) -> HttpResponse:
        body(request)
        return HttpResponse('ok')

    handler = middleware.StatsdMiddleware(
        middleware.StatsdMiddlewareTimer(get_response)
    )
    handler(RequestFactory().get('/'))


def run_python_sample(
    sample: CodeSample, namespace: dict[str, Any], request: HttpRequest
) -> None:
    defined = execute_python_sample(sample, namespace)
    validate_dotted_paths(defined)
    validate_statsd_settings(defined)
    call_sample_functions(defined, request)


@pytest.mark.parametrize(
    'source_path',
    DOC_SOURCES,
    ids=lambda path: path.relative_to(PROJECT_ROOT).as_posix(),
)
def test_docs_code_samples_execute(
    source_path: Path, install_cache: InstallSandboxCache
) -> None:
    samples = runnable_samples(source_path)
    for sample in samples:
        if sample.language == 'bash':
            execute_bash_sample(sample, install_cache)

    python_samples = [
        sample for sample in samples if sample.language == 'python'
    ]
    if not python_samples:
        return

    namespace: dict[str, Any] = {'__name__': 'docs_sample'}

    def run_all(request: HttpRequest) -> None:
        for sample in python_samples:
            run_python_sample(sample, namespace, request)

    run_in_tracked_request(run_all)
