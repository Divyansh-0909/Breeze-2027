"""Separate original limestone variant; the approved stone pilot remains unchanged.
Retains its stratified quarry-scale form, with small dissolution pockets and weathered rills.
Metres, Blender Z-up; no reference-photo texels or production-world edits.
"""
import numpy as np
from rock_pilot_surface import coordinates, surface as original_surface, value_noise, slabs

rng = np.random.default_rng(20271012)
POCKETS = [tuple(rng.uniform([-5.5, .35, .075, .06, .018], [5.5, 9.2, .25, .20, .085])) for _ in range(34)]

def dissolution(x, z):
    depression = np.zeros_like(x)
    for cx, cz, rx, rz, depth in POCKETS:
        distance = ((x-cx)/rx)**2 + ((z-cz)/rz)**2
        depression += depth*np.exp(-distance*1.8)
    # Interrupted shallow rainwater solution channels, not repeating UV tiles.
    for i, cx in enumerate([-4.65, -2.45, .55, 3.8]):
        line = cx + .07*np.sin(z*1.15+i) + .02*z
        coverage = np.clip((value_noise(z*.82, np.full_like(z, i*.9), 193)-.25)*1.6, 0, 1)
        depression += .023*np.exp(-((x-line)/.065)**2)*coverage
    return depression

def surface(u, v):
    x, y, z = original_surface(u, v)
    # Original y is negative front relief; dissolution recesses into the rock.
    return x, y+dissolution(x, z), z
