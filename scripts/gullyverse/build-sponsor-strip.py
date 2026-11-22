"""Rebuild the cypher sponsor LED strip from the repository's past-sponsor logo files.

The Rev15L strip lit whole tiles for logos with opaque white backgrounds (Dasmesh, OneIndia, Gail),
a dark band behind white lettering (Sparx) or a checkerboard baked into JPEG "transparency" (RedFM,
MTv, BD). This version lights only each mark's ink:

- logos on light, white or checkerboard grounds: dark/saturated ink lights, light ground stays off;
- logos on dark grounds, and white-only marks on transparency: light ink lights.

Order, sizing (48-row logo height, max 150 cells wide) and the 10676-cell loop are unchanged, so the
runtime shader and Blender LED material keep their contract. Logo artwork is never redrawn.

Usage: python build-sponsor-strip.py [review.png]
"""
import hashlib
import io
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SPONSORS = ROOT / "reports/navigation-board-rev15l-led-sponsors-2026-11-11/evidence/sponsors.json"
OUT = ROOT / "public/models/gullyverse/locked-rev15z-cypher-approach"
PERIOD, ROWS, ATLAS_W = 10676, 64, 2048


def load(path):
    data = path.read_bytes()
    if data.lstrip().startswith((b"<svg", b"<?xml")):
        import cairosvg
        assert b"<script" not in data and b"<!ENTITY" not in data
        data = cairosvg.svg2png(bytestring=data, output_width=1024)
    return np.asarray(Image.open(io.BytesIO(data)).convert("RGBA"), dtype=np.float32) / 255


def luminance(rgb):
    return rgb @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def ink(rgba):
    rgb, alpha = rgba[..., :3], rgba[..., 3]
    opaque = alpha > 0.5
    transparent = (alpha < 0.05).mean() > 0.005
    if transparent:
        # An opaque card inside transparent margins (OneIndia) is an opaque logo on that card.
        ys, xs = np.where(alpha > 0.05)
        card = alpha[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        if (card > 0.05).mean() > 0.93:
            rgba = rgba[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
            rgb, alpha, transparent = rgba[..., :3], rgba[..., 3], False
    if transparent:
        # Marks made mostly of white or pale grey (Safar) are drawn on a dark ground. Coloured
        # marks with white details and dark lettering (JioSaavn, Pepsi) keep the light ground.
        light_mark = opaque.any() and float((rgb[opaque].min(-1) > 0.7).mean()) > 0.6
        ground = 0.0 if light_mark else 1.0
    else:
        # The ground is the most common colour, not the border: some files have hairline frames
        # (OneIndia) and some sit on a dark field with dark-but-coloured lettering (Red Bull).
        bins = np.floor(rgb.reshape(-1, 3) * 15.999).astype(np.int32)
        keys = bins[:, 0] * 256 + bins[:, 1] * 16 + bins[:, 2]
        mode = np.bincount(keys).argmax()
        ground_rgb = rgb.reshape(-1, 3)[keys == mode].mean(0)
        distance = np.abs(rgb - ground_rgb).max(-1)
        lum = luminance(rgb)
        chroma = rgb.max(-1) - rgb.min(-1)
        value = smoothstep(0.1, 0.4, distance)
        if luminance(ground_rgb) > 0.6:
            # Pale neutral greys are baked checkerboards or paper, never ink.
            value *= 1 - smoothstep(0.68, 0.76, lum) * smoothstep(0.1, 0.05, chroma)
            # Very light fills (Gail's yellow ellipse) would hide the marks drawn inside them.
            value *= 1 - smoothstep(0.7, 0.84, lum)
        return value
    composite = rgb * alpha[..., None] + ground * (1 - alpha[..., None])
    lum = luminance(composite)
    chroma = composite.max(-1) - composite.min(-1)
    if light_mark:
        return smoothstep(0.35, 0.8, lum)
    # Dark or saturated marks on a light ground. White and pale checkerboard greys (L > 0.75,
    # low chroma) stay dark; pale saturated colours such as Gail's yellow stay dim.
    # Strongly saturated letters (eBay's yellow "a" and green "y") are ink even when fairly light.
    return np.maximum(smoothstep(0.8, 0.35, lum), smoothstep(0.35, 0.6, chroma) * smoothstep(0.96, 0.82, lum))


def main():
    logos = json.loads(SPONSORS.read_text())["logos"]
    tiles = []
    for row in logos:
        mask = ink(load(ROOT / row["source"]))
        # Ignore hairline frames and edge noise when cropping to the mark.
        h, w = mask.shape
        inset = max(2, round(min(h, w) * 0.02))
        mask[:inset], mask[-inset:], mask[:, :inset], mask[:, -inset:] = 0, 0, 0, 0
        ys, xs = np.where(mask > 0.35)
        mask = mask[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        aspect = mask.shape[1] / mask.shape[0]
        width = int(round(min(150, 48 * aspect)))
        height = max(1, int(round(width / aspect)))
        image = Image.fromarray((mask * 255).astype(np.uint8)).resize((width, height), Image.Resampling.LANCZOS)
        tiles.append((row["name"], image))
    gap = (PERIOD - sum(t.width for _, t in tiles)) / len(tiles)
    assert gap >= 64, gap  # Rev15L used at least 72; tighter crops widen marks slightly
    strip = Image.new("L", (PERIOD, ROWS))
    x = 0.0
    for _, tile in tiles:
        strip.paste(tile, (int(round(x + gap / 2)), (ROWS - tile.height) // 2))
        x += tile.width + gap
    atlas = Image.new("L", (ATLAS_W, ROWS * -(-PERIOD // ATLAS_W)))
    for start in range(0, PERIOD, ATLAS_W):
        atlas.paste(strip.crop((start, 0, min(start + ATLAS_W, PERIOD), ROWS)), (0, start // ATLAS_W * ROWS))
    assert atlas.size == (2048, 384)
    target = OUT / "sponsor-led.png"
    atlas.save(target, optimize=True)
    data = target.read_bytes()
    manifest_path = OUT / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    for file in manifest["files"]:
        if file["file"] == "sponsor-led.png":
            file.update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
    manifest["sponsorDisplay"].update(
        sourceStripSHA256=hashlib.sha256(strip.tobytes()).hexdigest(), minimumGapCells=round(gap),
        inkExtraction="scripts/gullyverse/build-sponsor-strip.py: ground-aware ink, no solid tiles",
    )
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    if len(sys.argv) > 1:
        strip.resize((PERIOD // 4, ROWS // 4)).save(sys.argv[1])
    print("SPONSOR STRIP", len(tiles), "logos, gap", round(gap, 1), "cells")


if __name__ == "__main__":
    main()
