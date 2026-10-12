#!/usr/bin/env python3
"""Turn the "Visitors" label into an outline path (lib/label.json), so the SVG
needs no embedded font.

    python3 scripts/make_label.py KleeOne-SemiBold.ttf [text]

Klee One: https://fonts.google.com/specimen/Klee+One (SIL OFL).
"""
import json
import sys
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

font = TTFont(sys.argv[1])
text = sys.argv[2] if len(sys.argv) > 2 else "Visitors"
glyphs, cmap, hmtx = font.getGlyphSet(), font.getBestCmap(), font["hmtx"]
upm = font["head"].unitsPerEm
pen = SVGPathPen(glyphs, ntos=lambda v: f"{v:.4f}".rstrip("0").rstrip("."))
x = 0.0
for ch in text:
    name = cmap[ord(ch)]
    # em units, y flipped to SVG's downward axis, baseline at 0
    glyphs[name].draw(TransformPen(pen, (1 / upm, 0, 0, -1 / upm, x, 0)))
    x += hmtx[name][0] / upm
out = Path(__file__).resolve().parent.parent / "lib" / "label.json"
out.write_text(json.dumps({
    "text": text,
    "d": pen.getCommands(),
    "advance": round(x, 4),
    "capHeight": round(font["OS/2"].sCapHeight / upm, 4),
}))
print(f"{out}: {text!r}, {x:.3f} em wide")
