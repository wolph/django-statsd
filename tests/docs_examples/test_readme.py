"""Guards on the README, which is the page most people ever read."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Final

from ._docs_examples import README_PATH
from ._metrics import TRANSCRIPT_ROOT

#: Markdown images and raw <img> tags.
IMAGE_PATTERNS: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(r'!\[[^\]]*\]\(([^)]+)\)'),
    re.compile(r'<img[^>]+src="([^"]+)"'),
)

TRANSCRIPT_BLOCK: Final[re.Pattern[str]] = re.compile(
    r'<!-- transcript: (?P<name>[a-z_]+) -->\n'
    r'```text\n(?P<body>.*?)```\n'
    r'<!-- /transcript -->',
    re.S,
)


def image_urls(text: str) -> list[str]:
    return [
        match for pattern in IMAGE_PATTERNS for match in pattern.findall(text)
    ]


def test_every_readme_image_url_is_absolute() -> None:
    """Relative URLs break on PyPI, which renders the README detached
    from the repository it came from."""
    relative = [
        url
        for url in image_urls(README_PATH.read_text(encoding='utf-8'))
        if not url.startswith(('https://', 'http://'))
    ]
    assert not relative, f'relative image URLs in README.md: {relative}'


def test_readme_carries_at_least_one_image() -> None:
    assert image_urls(README_PATH.read_text(encoding='utf-8'))


def test_readme_transcripts_match_their_recordings() -> None:
    """The README cannot use literalinclude, so its transcripts are
    pasted. This checks the paste against the recording."""
    text = README_PATH.read_text(encoding='utf-8')
    blocks = list(TRANSCRIPT_BLOCK.finditer(text))
    assert blocks, 'no marked transcript blocks found in README.md'

    for block in blocks:
        source = TRANSCRIPT_ROOT / f'{block["name"]}.txt'
        assert source.exists(), f'{source} is missing'

        recorded = [
            line
            for line in source.read_text(encoding='utf-8').splitlines()
            if line and not line.startswith('#')
        ]
        pasted = [line for line in block['body'].splitlines() if line]
        assert pasted == recorded, (
            f'README transcript {block["name"]!r} is stale. '
            f'Copy it from {source.name}.'
        )


def test_readme_images_live_in_the_repository() -> None:
    """A README image URL has to point at a file that exists here."""
    prefix = 'https://raw.githubusercontent.com/WoLpH/django-statsd/master/'
    root = Path(README_PATH).parent
    for url in image_urls(README_PATH.read_text(encoding='utf-8')):
        if not url.startswith(prefix):
            continue
        assert (root / url[len(prefix) :]).exists(), f'missing: {url}'
