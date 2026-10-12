#!/usr/bin/env python3
"""Cut a 10-pose sprite sheet into digit sprites 0-9 for the counter.

    python3 scripts/make_theme.py sheet.png --name mizuki --font Font.ttf

The sheet has 10 poses (two rows of five, reading order = digits 0-9), each
holding a blank card, on a transparent background. Poses are not evenly
spaced, so they are found as connected regions of opaque pixels; loose bits
(sparkles, props, stray hair) join the nearest pose. The digit is written on
each card, and every sprite is placed on a common canvas, centred on its card
and standing on the same baseline, so the digits line up in the counter.
Writes themes/<name>.json (sprites as base64 WebP data URIs).
"""
import argparse
import base64
import io
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent


def find_poses(rgba):
    """One mask per pose, in reading order. Each body is one connected region
    and is kept whole; loose bits (sparkles, hearts, props) are split between
    the poses of their row by whichever card centre they sit closest to."""
    alpha = rgba[..., 3]
    opaque = alpha > 24
    H = opaque.shape[0]
    rows = opaque.sum(axis=1)
    band = rows[H // 4: 3 * H // 4]
    empty = np.flatnonzero(band == band.min()) + H // 4
    split = int(empty[len(empty) // 2])  # the empty line between the two rows

    lab, n = ndimage.label(opaque)
    sizes = np.bincount(lab.ravel())[1:]
    boxes = ndimage.find_objects(lab)
    bodies = [i for i in range(n) if sizes[i] > 5000]
    if len(bodies) != 10:
        raise SystemExit(f"expected 10 poses, found {len(bodies)} large regions")
    bodies.sort(key=lambda i: (boxes[i][0].stop > split, boxes[i][1].start))
    masks = [lab == i + 1 for i in bodies]
    centres = []
    for m in masks:
        x0, y0, x1, y1 = find_card(rgba, m)
        centres.append((x0 + x1) / 2)
    for i in range(n):
        if i in bodies:
            continue
        ys, xs = boxes[i]
        row = 5 if (ys.start + ys.stop) / 2 > split else 0
        cx = (xs.start + xs.stop) / 2
        k = row + min(range(5), key=lambda j: abs(centres[row + j] - cx))
        masks[k] |= lab == i + 1
    return masks


def find_card(rgba, mask):
    """The blank card: the most rectangular patch of near-colourless paper.
    (The pale pink hair is bright too, but clearly more saturated.)"""
    r, g, b, a = (rgba[..., k].astype(int) for k in range(4))
    hi, lo = np.maximum(np.maximum(r, g), b), np.minimum(np.minimum(r, g), b)
    paper = mask & (a > 200) & (lo > 225) & (hi - lo < 22)
    paper = ndimage.binary_closing(paper, iterations=2)
    lab, n = ndimage.label(paper)
    best, best_score = None, 0
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        area = int((lab[sl] == i).sum())
        box = (sl[0].stop - sl[0].start) * (sl[1].stop - sl[1].start)
        score = area * (area / box) ** 2  # big and rectangular
        if area > 1500 and score > best_score:
            best, best_score = sl, score
    if best is None:
        raise SystemExit("no card found")
    return best[1].start, best[0].start, best[1].stop - 1, best[0].stop - 1


def load_font(path, size, weight):
    font = ImageFont.truetype(path, size)
    if weight:
        font.set_variation_by_name(weight)
    return font


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sheet")
    ap.add_argument("--name", required=True)
    ap.add_argument("--font", required=True)
    ap.add_argument("--weight", help="named instance of a variable font, e.g. Bold")
    ap.add_argument("--ink", default="#3b1f2d", help="digit colour; default is the sprite's own outline plum")
    ap.add_argument("--digit-scale", type=float, default=0.78, help="digit height / card height")
    ap.add_argument("--height", type=int, default=240, help="sprite height in pixels")
    ap.add_argument("--preview", help="also write a PNG preview of 0-9 here")
    args = ap.parse_args()

    sheet = Image.open(args.sheet).convert("RGBA")
    rgba = np.asarray(sheet)
    masks = find_poses(rgba)

    poses = []
    for digit, mask in enumerate(masks):
        ys, xs = np.nonzero(mask)
        x0, y0, x1, y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
        cut = rgba[y0:y1, x0:x1].copy()
        cut[..., 3] = np.where(mask[y0:y1, x0:x1], cut[..., 3], 0)
        cx0, cy0, cx1, cy1 = find_card(rgba, mask)
        poses.append({
            "img": Image.fromarray(cut),
            "card": (cx0 - x0, cy0 - y0, cx1 - x0, cy1 - y0),
            "bottom": y1,
        })

    # write the digits
    for digit, p in enumerate(poses):
        cx0, cy0, cx1, cy1 = p["card"]
        size = 200
        font = load_font(args.font, size, args.weight)
        l, t, r, b = font.getbbox(str(digit))
        size = int(size * args.digit_scale * (cy1 - cy0) / (b - t))
        font = load_font(args.font, size, args.weight)
        draw = ImageDraw.Draw(p["img"])
        draw.text(((cx0 + cx1) / 2, (cy0 + cy1) / 2), str(digit), font=font, fill=args.ink, anchor="mm")

    # common canvas: centred on the card, feet on one baseline (per sheet row)
    left = max((p["card"][0] + p["card"][2]) / 2 for p in poses)
    right = max(p["img"].width - (p["card"][0] + p["card"][2]) / 2 for p in poses)
    height = max(p["img"].height for p in poses)
    W, H = int(left + right), height
    scale = args.height / H
    sprites, preview = [], []
    for p in poses:
        canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        cx = (p["card"][0] + p["card"][2]) / 2
        canvas.alpha_composite(p["img"], (int(left - cx), H - p["img"].height))
        canvas = canvas.resize((round(W * scale), args.height), Image.LANCZOS)
        buf = io.BytesIO()
        canvas.save(buf, "WEBP", quality=90, method=6)
        sprites.append("data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode())
        preview.append(canvas)
    out = ROOT / "themes" / f"{args.name}.json"
    out.parent.mkdir(exist_ok=True)
    # where the cards sit, so a label can be lined up with them
    card_y = sum(H - p["img"].height + (p["card"][1] + p["card"][3]) / 2 for p in poses) / len(poses)
    out.write_text(json.dumps({
        "width": preview[0].width,
        "height": args.height,
        "cardY": round(card_y * scale, 1),
        "digits": sprites,
    }))
    print(f"{out}: {preview[0].width}x{args.height} per digit, {out.stat().st_size // 1024} KB")
    if args.preview:
        sheet = Image.new("RGBA", (preview[0].width * 10, args.height), (255, 255, 255, 255))
        for i, im in enumerate(preview):
            sheet.alpha_composite(im, (i * preview[0].width, 0))
        sheet.save(args.preview)


if __name__ == "__main__":
    main()
