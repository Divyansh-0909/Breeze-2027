"""
Measure-and-fit look calibration (realism rescue; method: render, measure, adjust, repeat).

For every matched sample area in scripts/look-samples.json, take the mean colour of the mockup (references/) and of our
capture and convert both to OKLab. Two fits:
  1. a global display grade (L' = lift + contrast * L; chroma scale; tint), printed as a diagnostic: when it cannot
     close the gap, the error is local, not global;
  2. per zone, the multiplier on the baked light that would match the mockup: the geometric mean over the zone's baked
     samples of (L_ref / L_cap)^3 (OKLab L is close to the cube root of luminance).
With --write the zone multipliers are moved halfway (gain^0.5, composed with the current values, clamped 0.25-4) into
components/gullyverse-runtime/zone-light.json, which the lightmap decode applies (baked-assets.ts). Then render,
measure again, repeat until the numbers agree.

Usage: python scripts/measure-look.py screenshots/<capture-dir> [--write]
"""
import json
import math
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent


def linear(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def oklab(rgb):
    r, g, b = (linear(v) for v in rgb)
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l, m, s = (math.copysign(abs(x) ** (1 / 3), x) for x in (l, m, s))
    return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)


def mean_lab(image, rect):
    w, h = image.size
    x, y, rw, rh = rect
    box = (int(x * w), int(y * h), max(int((x + rw) * w), int(x * w) + 1), max(int((y + rh) * h), int(y * h) + 1))
    crop = image.crop(box).convert("RGB")
    # Average in linear light, then convert: the mean colour of the area, not the mean of its encoded values.
    px = list(crop.get_flattened_data()) if hasattr(crop, "get_flattened_data") else list(crop.getdata())
    lin = [sum(linear(p[i]) for p in px) / len(px) for i in range(3)]
    enc = [255 * (12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055) for v in lin]
    return oklab(enc)


def fit_line(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    k = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx if sxx > 1e-12 else 1.0
    return my - k * mx, k


def main():
    capture_dir = ROOT / sys.argv[1]
    spec = json.loads((ROOT / "scripts/look-samples.json").read_text(encoding="utf8"))
    pairs = []
    for zone in spec["zones"]:
        ref = Image.open(ROOT / zone["reference"])
        cap_path = capture_dir / f"{zone['zone']}.png"
        if not cap_path.exists():
            continue
        cap = Image.open(cap_path)
        for s in zone["samples"]:
            pairs.append((f"{zone['zone']}: {s['name']}", mean_lab(ref, s["ref"]), mean_lab(cap, s["cap"]), zone["light"] if s.get("baked", True) else None))
    refs = [p[1] for p in pairs]
    caps = [p[2] for p in pairs]
    lift, contrast = fit_line([c[0] for c in caps], [r[0] for r in refs])
    # Saturation through the origin on the chroma vectors, then the tint as the mean residual.
    num = sum(c[1] * r[1] + c[2] * r[2] for c, r in zip(caps, refs))
    den = sum(c[1] ** 2 + c[2] ** 2 for c in caps)
    saturation = num / den if den > 1e-12 else 1.0
    tint_a = sum(r[1] - saturation * c[1] for c, r in zip(caps, refs)) / len(pairs)
    tint_b = sum(r[2] - saturation * c[2] for c, r in zip(caps, refs)) / len(pairs)
    clamp = lambda v, lo, hi: max(lo, min(hi, v))
    grade = {
        "lift": round(clamp(lift, -0.08, 0.08), 4), "contrast": round(clamp(contrast, 0.75, 1.35), 4),
        "saturation": round(clamp(saturation, 0.6, 1.3), 4),
        "tintA": round(clamp(tint_a, -0.02, 0.02), 4), "tintB": round(clamp(tint_b, -0.02, 0.02), 4),
    }

    def apply(c):
        return (grade["lift"] + grade["contrast"] * c[0], grade["saturation"] * c[1] + grade["tintA"], grade["saturation"] * c[2] + grade["tintB"])

    def err(a, b):
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

    print(f"{len(pairs)} samples from {capture_dir.relative_to(ROOT)}")
    print(f"{'sample':58} {'ref L':>6} {'cap L':>6} {'ref C':>6} {'cap C':>6} {'err':>6} {'fitted':>6}")
    before = after = 0.0
    for name, r, c, _ in pairs:
        e0, e1 = err(r, c), err(r, apply(c))
        before += e0 ** 2; after += e1 ** 2
        print(f"{name[:58]:58} {r[0]:6.3f} {c[0]:6.3f} {math.hypot(r[1], r[2]):6.3f} {math.hypot(c[1], c[2]):6.3f} {e0:6.3f} {e1:6.3f}")
    print(f"RMSE (OKLab) before {math.sqrt(before / len(pairs)):.4f}  after fit {math.sqrt(after / len(pairs)):.4f}")
    print("raw fit:", {"lift": round(lift, 4), "contrast": round(contrast, 4), "saturation": round(saturation, 4),
                       "tintA": round(tint_a, 4), "tintB": round(tint_b, 4)})
    print("grade (clamped):", grade)
    # Per-zone baked-light multipliers.
    light_path = ROOT / "components/gullyverse-runtime/zone-light.json"
    current = json.loads(light_path.read_text(encoding="utf8")) if light_path.exists() else {}
    gains = {}
    for key in sorted({p[3] for p in pairs if p[3]}):
        logs = [3 * math.log(max(r[0], 1e-3) / max(c[0], 1e-3)) for _, r, c, k in pairs if k == key]
        gains[key] = math.exp(sum(logs) / len(logs))
    print("zone luminance gain to match the mockups:", {k: round(v, 3) for k, v in gains.items()})
    if "--write" in sys.argv:
        updated = {k: round(max(0.25, min(4.0, current.get(k, 1.0) * math.sqrt(g))), 3) for k, g in gains.items()}
        updated["source"] = f"scripts/measure-look.py on {capture_dir.relative_to(ROOT).as_posix()} ({len(pairs)} samples)"
        light_path.write_text(json.dumps(updated, indent=2) + "\n", encoding="utf8")
        print("wrote", light_path.relative_to(ROOT), updated)

if __name__ == "__main__":
    main()
