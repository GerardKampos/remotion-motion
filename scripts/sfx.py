"""Efectos de sonido originales del vídeo, sintetizados en código → public/sfx/*.wav.

    python3 sfx.py [carpeta-salida=public/sfx]

Biblioteca base: teclas (6 variantes), espacio, intro, clic, pop, pop suave, golpe de fieltro
(tick), golpes sordos para palabras (word0–5), barridos con paso bajo, campana, denegado, brillo,
impacto y subida. Ajusta frecuencias y niveles al carácter de cada vídeo. La semilla es fija: si
añades un sonido, hazlo al final de main() para no cambiar el ruido de los demás.

Cortos, limpios y sin samples de terceros. Remotion los coloca uno a uno junto al evento
visual que los produce (tecla, clic, aparición, transición), así el audio sigue a la imagen.
"""
import os
import sys
import numpy as np
import soundfile as sf
from scipy import signal

SR = 48000
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join('public', 'sfx')
rng = np.random.default_rng(90)


def t(d):
    return np.arange(int(d * SR)) / SR


def noise(n):
    return rng.standard_normal(n)


def bp(x, lo, hi, order=2):
    return signal.sosfilt(signal.butter(order, [lo, hi], 'bandpass', fs=SR, output='sos'), x)


def lp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, 'lowpass', fs=SR, output='sos'), x)


def hp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, 'highpass', fs=SR, output='sos'), x)


def fade(x, ms=4):
    n = int(SR * ms / 1000)
    x = x.copy()
    x[-n:] *= np.linspace(1, 0, n)
    return x


def save(name, x, peak_db=-3.0, stereo_pan=0.0):
    x = fade(x / (np.max(np.abs(x)) + 1e-9) * 10 ** (peak_db / 20))
    left, right = x * np.sqrt(0.5 - stereo_pan / 2) * np.sqrt(2), x * np.sqrt(0.5 + stereo_pan / 2) * np.sqrt(2)
    sf.write(os.path.join(OUT, f'{name}.wav'), np.stack([left, right], 1).astype(np.float32), SR, subtype='PCM_16')


def key(body_hz, bright, length=0.09):
    """Tecla mecánica: chasquido de la cúpula y golpe grave de la tecla al tocar fondo."""
    x = t(length)
    click = lp(bp(noise(len(x)), 900 * bright, 4200, 2), 3000) * np.exp(-x * 700)
    thock = np.sin(2 * np.pi * body_hz * x) * np.exp(-x * 75) * 0.9
    knock = bp(noise(len(x)), 300, 1400) * np.exp(-x * 220) * 0.5
    release = np.zeros(len(x))
    j = int(0.045 * SR)
    release[j:] = bp(noise(len(x) - j), 2500, 6000) * np.exp(-x[: len(x) - j] * 1400) * 0.25
    return click * 0.7 + thock + knock + release


def thock():
    """Golpe sordo de tecla de fieltro: cuerpo grave, sin agudos. Para palabras y filas que entran."""
    x = t(0.11)
    body = np.sin(2 * np.pi * np.cumsum(260 - 90 * (1 - np.exp(-x * 40))) / SR) * np.exp(-x * 45)
    felt = lp(noise(len(x)), 1400) * np.exp(-x * 160) * 0.5
    return lp(body + felt, 1800) * np.minimum(1, x / 0.0015)


def thump(end_hz):
    """Golpe sordo para cada palabra que entra: grave y corto, se nota más que se oye. Ni teclado ni melodía."""
    x = t(0.16)
    f = end_hz + 50 * np.exp(-x * 40)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 30)
    tip = lp(noise(len(x)), 900) * np.exp(-x * 300) * 0.25
    return body + tip


def pop(f0, f1, length=0.12):
    x = t(length)
    f = f0 + (f1 - f0) * (1 - np.exp(-x * 60))
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 34) * np.minimum(1, x / 0.003)
    return tone + bp(noise(len(x)), 2000, 6000) * np.exp(-x * 500) * 0.08


def whoosh(length, lo, hi, air=1.0):
    x = t(length)
    u = x / length
    env = np.sin(np.pi * u) ** 1.6
    n = noise(len(x))
    centre = lo * (hi / lo) ** u
    out = np.zeros(len(x))
    block = 256
    for i in range(0, len(x), block):
        c = centre[min(i, len(x) - 1)]
        seg = bp(n[max(0, i - 2048): i + block], c * 0.6, min(c * 1.8, 20000), 2)[-min(block, len(x) - i):]
        out[i: i + len(seg)] = seg
    return out * env * air


def bell(freqs, length, decay):
    x = t(length)
    return sum(np.sin(2 * np.pi * f * x) * np.exp(-x * decay * (1 + k * 0.4)) * (1 / (k + 1)) for k, f in enumerate(freqs)) * np.minimum(1, x / 0.004)


def main():
    os.makedirs(OUT, exist_ok=True)
    for i in range(6):
        save(f'key{i}', key(170 + i * 17 + rng.uniform(-8, 8), 0.85 + i * 0.07), -6)
    save('key-space', key(120, 0.7, 0.12) + lp(noise(int(0.12 * SR)), 900) * np.exp(-t(0.12) * 60) * 0.3, -5)
    save('key-enter', key(105, 0.75, 0.14) * 1.2, -3)

    x = t(0.12)
    press = bp(noise(len(x)), 1500, 5000) * np.exp(-x * 700) + np.sin(2 * np.pi * 900 * x) * np.exp(-x * 400) * 0.4
    up = np.zeros(len(x))
    j = int(0.07 * SR)
    up[j:] = bp(noise(len(x) - j), 2500, 7000)[: len(x) - j] * np.exp(-x[: len(x) - j] * 900) * 0.45
    save('click', press + up, -4)

    save('pop', lp(pop(330, 520, 0.16), 2500), -6)
    save('pop-soft', lp(pop(250, 360, 0.16), 2000), -9)
    save('tick', thock(), -8)
    # Barridos oscuros y suaves: sin agudos por encima de ~3 kHz, que en la v4 sonaban estridentes.
    save('whoosh', lp(whoosh(0.42, 220, 2400), 3200), -8)
    save('whoosh-long', lp(whoosh(0.85, 160, 2600), 3000), -8)
    save('swoosh', lp(whoosh(0.34, 300, 2200), 2800), -10)

    chime = bell([1318.5, 2637], 1.2, 4.5)
    second = bell([1975.5, 3951], 1.2, 4.5)
    j = int(0.09 * SR)
    chime[j:] += second[: len(chime) - j]
    save('chime', chime, -6)

    x = t(0.5)
    deny = np.zeros(len(x))
    for k, (f, at) in enumerate(((330, 0.0), (247, 0.12))):
        i = int(at * SR)
        seg = x[: len(x) - i]
        deny[i:] += (np.sin(2 * np.pi * f * seg) + 0.35 * np.sin(2 * np.pi * 2 * f * seg)) * np.exp(-seg * 9)
    save('deny', lp(deny, 2500), -7)

    x = t(2.4)
    shimmer = sum(bell([f], 2.4, 1.6)[: len(x)] * np.exp(-x * 0.2) * w for f, w in ((1174.7, 1), (1760, 0.7), (2349.3, 0.5), (2960, 0.35)))
    shimmer += lp(whoosh(2.4, 600, 3000, 0.15), 3500)
    save('shimmer', lp(shimmer, 6000), -10)

    x = t(1.4)
    impact = np.sin(2 * np.pi * np.cumsum(55 + 60 * np.exp(-x * 18)) / SR) * np.exp(-x * 4.5)
    impact += lp(noise(len(x)), 2500) * np.exp(-x * 7) * 0.35
    save('impact', impact, -4)

    x = t(1.6)
    riser = lp(noise(len(x)), 3200) * (x / 1.6) ** 2.5
    save('riser', hp(riser, 300), -12)

    for i, hz in enumerate([70, 67, 73, 69, 71, 68]):
        save(f'word{i}', thump(hz), -6)


if __name__ == '__main__':
    main()
    print('\n'.join(sorted(os.listdir(OUT))))
