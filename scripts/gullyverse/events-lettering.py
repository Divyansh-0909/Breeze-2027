"""Builds the events shutter's "EVENTS" lettering from the organising-committee mural's own name lettering.

    python scripts/gullyverse/events-lettering.py

User request (28 Nov): the shutter text must look like the names on the team mural. The mural art is only ~1800 px
wide (letters ~45 px tall), so the letter SHAPES are lifted from it (E, V, N from "RATHNAVEL", T split from its "TH",
S split from "SAIGAL"'s "SA"), enlarged smoothly and re-inked crisp in the mural's colours: cream fill, a dark outline
and the hand-drawn tapered underline the mural puts under every name.

Source: reports/team-wall-rev15k-black-brick-2026-11-11/viewer/art/Organising-Committee.png (the live mural art).
Output: public/models/gullyverse/zone-art/events-lettering.png (RGBA, transparent around the lettering).
"""
import os
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "reports/team-wall-rev15k-black-brick-2026-11-11/viewer/art/Organising-Committee.png")
OUT = os.path.join(ROOT, "public/models/gullyverse/zone-art/events-lettering.png")
SCALE = 6

im = np.array(Image.open(SRC).convert("RGBA")).astype(int)
r, g, b, a = im[..., 0], im[..., 1], im[..., 2], im[..., 3]
spread = np.maximum(np.maximum(r, g), b) - np.minimum(np.minimum(r, g), b)
cream = (r > 175) & (g > 165) & (b > 130) & (spread < 75) & (a > 200)
colour = np.median(im[cream][:, :3], axis=0)


def component(box):
    """The largest cream component inside box (x0, y0, x1, y1), as a mask cropped to the box."""
    x0, y0, x1, y1 = box
    sub = cream[y0:y1, x0:x1]
    lab, n = ndimage.label(sub)
    sizes = ndimage.sum(sub, lab, range(1, n + 1))
    return lab == (int(np.argmax(sizes)) + 1)


def split(mask, keep_left, lo, hi):
    """Splits two touching italic letters along the slanted line that crosses the least cream (its foot between
    lo and hi of the width)."""
    h, w = mask.shape
    best = None
    for slope in np.linspace(0.05, 0.4, 15):
        for c in range(int(w * lo), int(w * hi)):
            xs = (c + slope * (h - 1 - np.arange(h))).astype(int)
            ok = (xs >= 0) & (xs < w)
            cost = mask[np.arange(h)[ok], xs[ok]].sum()
            if best is None or cost < best[0]:
                best = (cost, slope, c)
    _, slope, c = best
    yy, xx = np.mgrid[0:h, 0:w]
    left = xx < c + slope * (h - 1 - yy)
    return mask & (left if keep_left else ~left)


def tight(mask):
    ys, xs = np.nonzero(mask)
    return mask[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


letters = {
    "E": tight(component((1423, 53, 1460, 103))),
    "V": tight(component((1398, 57, 1431, 106))),
    "N": tight(component((1332, 64, 1370, 116))),
    "T": tight(split(component((1282, 72, 1339, 124)), True, 0.22, 0.42)),
    "S": tight(split(component((1576, 351, 1645, 405)), True, 0.3, 0.55)),
}

# Compose at source resolution on a baseline rising like the mural's name lines (≈ −0.13 px per px), letters set
# close (the mural's outlines touch), each bottom on the baseline.
word, gap, slope = "EVENTS", 1, -0.13
pad = 30
height = max(m.shape[0] for m in letters.values())
width = sum(letters[c].shape[1] for c in word) + gap * (len(word) - 1)
canvas = np.zeros((height + pad * 2 + int(abs(slope) * width) + 30, width + pad * 2), bool)
x, base = pad, canvas.shape[0] - pad - 30
for c in word:
    m = letters[c]
    y = int(round(base + slope * (x - pad))) - m.shape[0]
    canvas[y:y + m.shape[0], x:x + m.shape[1]] |= m
    x += m.shape[1] + gap

# The underline: a tapered stroke under the word, slightly bowed, following the baseline (as under each mural name).
uh, uw = canvas.shape
yy, xx = np.mgrid[0:uh, 0:uw]
u0, u1 = pad - 2, pad + width + 2
t = np.clip((xx - u0) / (u1 - u0), 0, 1)
centre = base + 10 + slope * (xx - pad) + 3.0 * np.sin(np.pi * t)
thick = 4.6 * np.sin(np.pi * np.clip(t * 0.92 + 0.04, 0, 1)) ** 0.6
canvas |= (xx >= u0) & (xx <= u1) & (np.abs(yy - centre) < thick / 2 + 0.3)

# Enlarge smoothly and re-threshold (crisp edges), then ink: dark outline around everything, cream inside.
soft = ndimage.gaussian_filter(canvas.astype(float), 1.15)
big = ndimage.zoom(soft, SCALE, order=3) > 0.45
dist = ndimage.distance_transform_edt(~big)
outline = dist < 2.2 * SCALE
glow = dist < 4.5 * SCALE
rgba = np.zeros(big.shape + (4,), np.uint8)
rgba[glow] = (24, 21, 17, 110)
rgba[outline] = (22, 19, 15, 245)
rng = np.random.default_rng(7)
grain = rng.normal(0, 6, big.shape)
shade = np.linspace(6, -10, big.shape[0])[:, None]  # a touch brighter at the top, as painted
fill = np.clip(colour[None, None, :] + (grain + shade)[..., None], 0, 255).astype(np.uint8)
rgba[big, :3] = fill[big]
rgba[big, 3] = 255
ys, xs = np.nonzero(rgba[..., 3])
rgba = rgba[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
os.makedirs(os.path.dirname(OUT), exist_ok=True)
Image.fromarray(rgba, "RGBA").save(OUT, optimize=True)
print("WROTE", OUT, rgba.shape[1], "x", rgba.shape[0], "cream", colour)
