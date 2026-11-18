"""Halo con tramado: un disco desenfocado calculado en coma flotante y cuantizado con ruido
triangular de ±1 nivel. Sustituye a un círculo con `filter: blur()`, que a 8 bits deja anillos y
un aro oscuro. Úsalo con `mix-blend-mode: plus-lighter`.

    python3 glow.py public/textures/glow.png --color 133,149,191 --size 720 --radius 150 --sigma 60
"""
import argparse
import numpy as np
from PIL import Image
from scipy import ndimage

ap = argparse.ArgumentParser()
ap.add_argument('out')
ap.add_argument('--color', default='133,149,191')
ap.add_argument('--size', type=int, default=720)
ap.add_argument('--radius', type=float, default=150)
ap.add_argument('--sigma', type=float, default=60)
ap.add_argument('--seed', type=int, default=23)
a = ap.parse_args()

rng = np.random.default_rng(a.seed)
y, x = np.mgrid[0:a.size, 0:a.size].astype(np.float64) + 0.5
disc = (np.hypot(x - a.size / 2, y - a.size / 2) <= a.radius).astype(np.float64)
alpha = ndimage.gaussian_filter(disc, a.sigma) * 255
alpha = np.clip(np.round(alpha + rng.random(alpha.shape) - rng.random(alpha.shape)), 0, 255).astype(np.uint8)
img = np.zeros((a.size, a.size, 4), np.uint8)
img[..., :3] = [int(c) for c in a.color.split(',')]
img[..., 3] = alpha
Image.fromarray(img, 'RGBA').save(a.out, optimize=True)
print(a.out)
