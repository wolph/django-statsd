"""Draw the wordmark used at the top of the README.

Branding rather than evidence, so this is the one generated asset that
demonstrates nothing. It is a script so that the colours stay in one
place and the file can be rebuilt at another size.
"""

from __future__ import annotations

from pathlib import Path
from typing import Final

from PIL import Image, ImageDraw, ImageFont

ROOT: Final[Path] = Path(__file__).resolve().parents[2]
OUTPUT: Final[Path] = ROOT / 'docs' / 'images' / 'logo.png'

WIDTH: Final[int] = 1200
HEIGHT: Final[int] = 276
BLUE: Final[tuple[int, int, int]] = (59, 110, 165)
INK: Final[tuple[int, int, int]] = (27, 31, 35)
MUTED: Final[tuple[int, int, int]] = (122, 134, 143)

#: Bars standing in for a timing series, tallest where the work is.
BARS: Final[tuple[float, ...]] = (
    0.30,
    0.52,
    0.41,
    0.86,
    0.62,
    1.00,
    0.47,
    0.71,
    0.35,
)

FONT_CANDIDATES: Final[tuple[str, ...]] = (
    '/System/Library/Fonts/SFNSRounded.ttf',
    '/System/Library/Fonts/Helvetica.ttc',
    '/Library/Fonts/Arial.ttf',
)


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in FONT_CANDIDATES:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default(size)


def draw_bars(draw: ImageDraw.ImageDraw, left: int, baseline: int) -> int:
    width, gap, tallest = 18, 12, 150
    for index, height in enumerate(BARS):
        x = left + index * (width + gap)
        top = baseline - int(tallest * height)
        shade = tuple(
            int(channel + (255 - channel) * (1 - height) * 0.55)
            for channel in BLUE
        )
        draw.rounded_rectangle(
            (x, top, x + width, baseline), radius=5, fill=shade
        )
    return left + len(BARS) * (width + gap) - gap


def main() -> int:
    image = Image.new('RGBA', (WIDTH, HEIGHT), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)

    baseline = 210
    bars_right = draw_bars(draw, 60, baseline)

    name_font = load_font(92)
    tag_font = load_font(30)
    draw.text((bars_right + 46, 96), 'django', font=name_font, fill=INK)

    offset = draw.textlength('django', font=name_font)
    draw.text(
        (bars_right + 46 + offset, 96), '-statsd', font=name_font, fill=BLUE
    )
    draw.text(
        (bars_right + 52, 206),
        'every view, every query, on the wire',
        font=tag_font,
        fill=MUTED,
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT)
    print(f'wrote {OUTPUT.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
