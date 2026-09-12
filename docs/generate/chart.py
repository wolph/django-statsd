"""Draw the timing breakdown from the recorded chart data.

Run through `tox -e docs-assets`. The numbers come from
`docs/_transcripts/chart_data.txt`, which is recorded by really running
a request, so this script never invents a value.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Final

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT: Final[Path] = Path(__file__).resolve().parents[2]
DATA: Final[Path] = ROOT / 'docs' / '_transcripts' / 'chart_data.txt'
OUTPUT: Final[Path] = ROOT / 'docs' / 'images' / 'timing_breakdown.png'

BAR: Final[str] = '#3b6ea5'
TOTAL: Final[str] = '#b0bec5'
TEXT: Final[str] = '#1b1f23'


def read_timings(path: Path) -> dict[str, float]:
    timings: dict[str, float] = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line or line.startswith('#'):
            continue
        name, _, value = line.rpartition(' ')
        timings[name] = float(value)
    return timings


def draw(timings: dict[str, float], output: Path) -> None:
    total = timings.pop('total')
    labels = list(timings)
    values = [timings[label] for label in labels]

    figure, axes = plt.subplots(figsize=(9, 4.2), dpi=160)
    bars = axes.barh(labels, values, color=BAR, height=0.62)
    axes.invert_yaxis()

    for bar, value in zip(bars, values, strict=True):
        share = value / total * 100
        axes.text(
            value + total * 0.012,
            bar.get_y() + bar.get_height() / 2,
            f'{value:.3f} ms  ({share:.0f}%)',
            va='center',
            fontsize=9,
            color=TEXT,
        )

    axes.set_xlim(0, total * 1.25)
    axes.axvline(total, color=TOTAL, linewidth=1.4, linestyle='--')
    axes.text(
        total,
        -0.62,
        f'total {total:.3f} ms',
        fontsize=9,
        color='#54646f',
        ha='center',
        va='bottom',
    )

    axes.set_xlabel('milliseconds')
    axes.set_title("Where a request's milliseconds go", fontsize=13, pad=14)
    for spine in ('top', 'right', 'left'):
        axes.spines[spine].set_visible(False)
    axes.tick_params(axis='y', length=0)
    axes.grid(axis='x', color='#e6e9ec', linewidth=0.8)
    axes.set_axisbelow(True)

    figure.text(
        0.01,
        0.015,
        'GET /heavy/ on one machine, one run. Recorded by '
        'tests/docs_examples, not estimated.',
        fontsize=7.5,
        color='#7a868f',
    )
    figure.tight_layout(rect=(0, 0.035, 1, 1))
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, facecolor='white')
    plt.close(figure)


def main() -> int:
    if not DATA.exists():
        print(f'{DATA} is missing. Run tox -e docs-assets.', file=sys.stderr)
        return 1

    draw(read_timings(DATA), OUTPUT)
    print(f'wrote {OUTPUT.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
