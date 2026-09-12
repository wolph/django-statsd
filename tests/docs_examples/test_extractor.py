"""Tests for the documentation sample extractor itself.

The extractor decides what gets executed, so a silent regression in it
would quietly stop testing the documentation.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ._docs_examples import (
    DOCS_ROOT,
    README_PATH,
    extract_samples,
    install_target,
    iter_doc_sources,
    runnable_samples,
)

#: Every documented source and the sample languages it must still carry.
#: A doc that stops yielding samples is a regression, not a pass.
EXPECTED_LANGUAGES = {
    'README.md': ('bash', 'python', 'python', 'python'),
    'docs/getting-started/installation.rst': ('bash',),
    'docs/getting-started/quickstart.rst': ('python',),
    'docs/guide/database.rst': ('python',),
    'docs/guide/manual-timing.rst': ('python', 'python'),
    'docs/guide/middleware.rst': ('python', 'python'),
    'docs/guide/settings.rst': ('python',),
}


def test_doc_sources_are_discovered() -> None:
    sources = iter_doc_sources()
    assert README_PATH in sources
    assert DOCS_ROOT / 'getting-started' / 'quickstart.rst' in sources
    assert DOCS_ROOT / 'api' / 'index.rst' in sources


@pytest.mark.parametrize('relative_path', sorted(EXPECTED_LANGUAGES))
def test_expected_samples_are_extracted(relative_path: str) -> None:
    path = README_PATH.parent / relative_path
    languages = tuple(sample.language for sample in runnable_samples(path))
    assert languages == EXPECTED_LANGUAGES[relative_path]


def test_markdown_extraction(tmp_path: Path) -> None:
    source = tmp_path / 'sample.md'
    source.write_text(
        'Intro\n\n```python\nvalue = 1\n```\n\n```\nnot tagged\n```\n',
        encoding='utf-8',
    )

    samples = extract_samples(source)
    assert [sample.language for sample in samples] == ['python', '']
    assert samples[0].body == 'value = 1\n'
    assert samples[0].start_line == 4
    assert runnable_samples(source) == (samples[0],)


def test_rst_extraction(tmp_path: Path) -> None:
    source = tmp_path / 'sample.rst'
    source.write_text(
        'Title\n=====\n\n'
        '.. code-block:: python\n\n'
        '    value = 1\n'
        '    other = 2\n\n'
        'Trailing prose.\n',
        encoding='utf-8',
    )

    (sample,) = extract_samples(source)
    assert sample.language == 'python'
    assert sample.body == 'value = 1\nother = 2\n'
    assert sample.start_line == 6


def test_sample_location_points_at_the_document() -> None:
    sample = runnable_samples(README_PATH)[0]
    assert sample.display_path == 'README.md'
    assert sample.location == f'README.md:{sample.start_line}'


def test_install_commands_are_rewritten_to_the_checkout() -> None:
    assert install_target('pip install django-statsd') == '.'
    assert install_target('  pip install django-statsd  ') == '.'
    assert install_target('pip install something-else') is None
