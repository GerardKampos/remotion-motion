"""Masteriza el audio de un render y deja el MP4 listo para la web.

    python3 master.py <entrada.mp4> <salida.mp4>

1. Extrae la mezcla que hace Remotion (efectos + música).
2. Ganancia lineal hasta -14 LUFS integrados y limitador a -1 dBTP con sobremuestreo 4x
   (un limitador a 48 kHz deja pasar picos entre muestras). Re-mide y corrige.
3. Remux: vídeo copiado tal cual, audio AAC 192k y `+faststart` para que arranque rápido.
   El pico verdadero se mide sobre el AAC final, que añade sobreoscilación.
"""
import os, subprocess, sys, tempfile

TARGET_I, TARGET_TP = -14.0, -1.0
if len(sys.argv) != 3:
    raise SystemExit('uso: master.py <entrada.mp4> <salida.mp4>')
src, dst = sys.argv[1], sys.argv[2]


def ff(*args):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-y', *args], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr[-2000:])
    return r.stderr


def measure(path):
    e = ff('-nostats', '-i', path, '-map', '0:a', '-af', 'ebur128=peak=true', '-f', 'null', '-')
    summary = e[e.rfind('Summary'):]
    get = lambda key: float(next(l.split()[1] for l in summary.splitlines() if l.strip().startswith(key)))
    return get('I:'), get('Peak:')


def master(raw, mastered, gain, ceiling):
    ff('-i', raw, '-af',
       f'volume={gain:.2f}dB,aresample=192000,alimiter=limit={ceiling:.4f}:attack=1:release=60:level=false,aresample=48000',
       '-c:a', 'pcm_s24le', mastered)


with tempfile.TemporaryDirectory() as tmp:
    raw = os.path.join(tmp, 'raw.wav')
    mastered = os.path.join(tmp, 'master.wav')
    ff('-i', src, '-vn', '-c:a', 'pcm_f32le', '-ar', '48000', raw)
    i0, tp0 = measure(raw)
    gain, headroom = TARGET_I - i0, 0.6
    for _ in range(6):
        master(raw, mastered, gain, 10 ** ((TARGET_TP - headroom) / 20))
        # El pico verdadero se mide sobre el AAC final: el codificador añade sobreoscilación.
        ff('-i', src, '-i', mastered, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
           '-movflags', '+faststart', dst)
        i, tp = measure(dst)
        if tp <= TARGET_TP and abs(i - TARGET_I) <= 0.3:
            break
        if tp > TARGET_TP:
            headroom += tp - TARGET_TP + 0.2
        gain += TARGET_I - i

fi, ftp = measure(dst)
print(f'antes: {i0:.1f} LUFS, pico {tp0:.1f} dBTP')
print(f'después ({dst}): {fi:.1f} LUFS, pico verdadero {ftp:.1f} dBTP')
if ftp > TARGET_TP + 0.05:
    raise SystemExit(f'Pico verdadero {ftp:.2f} dBTP por encima de {TARGET_TP}')
