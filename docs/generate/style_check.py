"""Count the style guide's tells here and in a reference corpus.

Advisory. The point is the comparison: a pattern this project's own
documentation uses is the author's, and a pattern only the draft uses
is the one worth looking at. The counts are evidence, never a verdict,
so this never exits non-zero.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Final

ROOT: Final[Path] = Path(__file__).resolve().parents[2]
REFERENCE: Final[Path] = ROOT.parent / 'numpy-stl'

PATTERNS: Final[dict[str, str]] = {
    'contracted negatives': r"\b(?:don|doesn|can|isn|won|didn|wasn|aren)'t\b",
    'uncontracted negatives': (
        r'\b(?:do not|does not|cannot|is not|will not)\b'
    ),
    'antithesis pairs': r'\brather than\b|\binstead of\b',
    'you / your': r'\byou\b|\byour\b',
    'must / should': r'\bmust\b|\bshould\b',
    'first person': r'(?:^|[.!?]\s)I\s',
    'however': r'\bhowever\b',
    'question marks': r'\?',
    'result verbs': (
        r'\b(?:submits?|reports?|prints?|returns?|raises?|fails?)\b'
    ),
    'semicolons': r';',
    'em / en dashes': '[\u2013\u2014]',
    'banned adverbs': r'\b(?:genuinely|quietly|deliberately)\b',
}


def sources(root: Path) -> list[Path]:
    found = [root / 'README.md']
    docs = root / 'docs'
    if docs.is_dir():
        found += [
            path
            for path in sorted(docs.rglob('*.rst'))
            if '_build' not in path.parts
        ]
    return [path for path in found if path.is_file()]


def count(paths: list[Path]) -> tuple[dict[str, int], int]:
    text = '\n'.join(
        path.read_text(encoding='utf-8', errors='replace') for path in paths
    )
    words = len(text.split()) or 1
    counts = {
        label: len(re.findall(pattern, text, re.M | re.I))
        for label, pattern in PATTERNS.items()
    }
    return counts, words


def main() -> int:
    here, here_words = count(sources(ROOT))
    if REFERENCE.is_dir():
        there, there_words = count(sources(REFERENCE))
        reference_name = REFERENCE.name
    else:
        there, there_words, reference_name = {}, 1, '(not found)'

    header = f'{"pattern":<24}{"here":>10}{reference_name:>18}'
    print(header)
    print('-' * len(header))
    for label in PATTERNS:
        mine = here[label]
        theirs = there.get(label, 0)
        rate = theirs / there_words * here_words
        print(f'{label:<24}{mine:>10}{theirs:>10} ({rate:>4.0f} pro rata)')

    print(f'\nwords: {here_words} here, {there_words} in {reference_name}')
    print("Advisory only. A pattern the reference uses is the author's.")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
