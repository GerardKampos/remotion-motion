"""Uniformidad del fondo oscuro, por bloques de 48×48.

Sin referencia: toma los bloques que son fondo liso (todos sus píxeles a ±4 niveles del valor
dominante) y mide cuánto se separan sus medias. Un fondo liso da < 0,6 niveles aunque la
compresión alterne dos valores vecinos píxel a píxel; rectángulos, tintes por zonas o bandas lo
superan.

Con --ref: compara cada bloque de fondo oscuro (rodeado de fondo oscuro, para no medir los bordes
de los objetos) con el mismo bloque de un fotograma de referencia (`remotion still` sin blur o el
máster) y mide lo que ha **añadido** la compresión. Un desplazamiento igual en todo el fotograma
(la ida y vuelta RGB→YUV→RGB) no cuenta; las diferencias entre zonas, sí.

    python3 bgcheck.py frame.png [frame2.png …]
    python3 bgcheck.py web.png --ref master.png
"""
import argparse
import numpy as np
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument('frames', nargs='+')
ap.add_argument('--ref', help='fotograma de referencia (solo con un fotograma a comparar)')
ap.add_argument('--dark', type=float, default=40, help='luminancia media máxima de un bloque oscuro')
ap.add_argument('--limit', type=float, default=0.6, help='dispersión aceptable, en niveles')
B = 48
a = ap.parse_args()
if a.ref and len(a.frames) != 1:
    ap.error('con --ref, compara un fotograma cada vez')


def blocks(path):
    rgb = np.asarray(Image.open(path).convert('RGB')).astype(float)
    y = rgb @ [0.2126, 0.7152, 0.0722]
    h, w = (y.shape[0] // B) * B, (y.shape[1] // B) * B
    return y[:h, :w].reshape(h // B, B, w // B, B).swapaxes(1, 2).reshape(h // B, w // B, B * B)


def report(path, values, label):
    lo, hi = np.percentile(values, [2, 98]) if len(values) > 1 else (0.0, 0.0)
    verdict = 'OK' if hi - lo <= a.limit else 'REVISAR'
    print(f'{path}: {len(values)} bloques, {label} 2–98 % {hi - lo:.2f} niveles  {verdict}')


if a.ref:
    test, ref = blocks(a.frames[0]), blocks(a.ref)
    dark = ref.mean(2) < a.dark
    pad = np.pad(dark, 1, constant_values=False)
    inner = np.logical_and.reduce([pad[1 + dy:pad.shape[0] - 1 + dy, 1 + dx:pad.shape[1] - 1 + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1)])
    if inner.sum() < 4:
        raise SystemExit(f'{a.frames[0]}: muy poco fondo oscuro para medir')
    report(a.frames[0], (test.mean(2) - ref.mean(2))[inner], 'diferencia entre zonas frente a la referencia,')
else:
    for path in a.frames:
        b = blocks(path).reshape(-1, B * B)
        dark = b[b.mean(1) < a.dark]
        if not len(dark):
            print(f'{path}: sin fondo oscuro')
            continue
        mode = np.median(dark.mean(1))
        flat = b[(np.abs(b - mode) <= 4).all(1)]
        if len(flat) < 4:
            print(f'{path}: muy poco fondo liso para medir; usa --ref')
            continue
        report(path, flat.mean(1) - mode, 'dispersión del fondo liso,')
