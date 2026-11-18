# Entrega: máster, MP4 web, WebM, póster y QA

## Cadena

```
Remotion (sin blur, subfotogramas) ──ProRes HQ──▶ ffmpeg media 16 bits ──▶ máster H.264 CRF 12
                                                                              │
audio (wav) ─────────────────────────────────────────────────────────────────┘
máster ──master.py──▶ máster con audio −14 LUFS ──▶ MP4 web (2 pasadas, < límite)
                                                └─▶ WebM VP9 + Opus
```

Una sola compresión con pérdida importante (la del entregable). El máster va a CRF 12; si lo haces
a CRF 18 y luego otra vez a CRF 21, las zonas oscuras se degradan dos veces.

## MP4 web por tamaño

`scripts/deliver.sh <máster> <prefijo> [bytes-máx] [fotograma-póster]` hace dos pasadas a un
bitrate calculado para el límite (p. ej. 14,4 MB para un tope de 15):

```
kbps = (bytes·8 / duración − audio_bps − 24000) / 1000
-c:v libx264 -preset slower -profile:v high -level 4.1 -b:v ${kbps}k -maxrate $((kbps*3))k -bufsize $((kbps*4))k
-x264-params aq-mode=3:aq-strength=1.0:chroma-qp-offset=-2:deadzone-inter=8:deadzone-intra=6
-pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv -movflags +faststart
```

- `aq-mode=3`: más bits a las zonas oscuras y planas, justo donde salen bloques.
- `chroma-qp-offset=-2`: menos manchas de color en oscuros.
- Zonas muertas bajas: conservan degradados suaves.
- `+faststart`: arranca sin descargar entero en la web.

Si el resultado sigue con bloques en un plano concreto, el arreglo está casi siempre en la escena
(quitar el degradado), no en el codificador. A bitrate justo, dos codificaciones equivalentes
varían ±0,3 niveles en un mismo parche (medido: 0,52 y 0,80 con los mismos ajustes y el mismo
bitrate): no persigas décimas cambiando parámetros a ciegas. Si un parche se ve con el realce y
molesta, quita la causa en la escena o da más tamaño al archivo.

## WebM

VP9 en dos pasadas, `-crf 28 -b:v 0 -row-mt 1 -tile-columns 2 -auto-alt-ref 1 -lag-in-frames 25`,
Opus 128 k, mismas etiquetas de color. Suele salir un 25–30 % más ligero que el MP4.

## Póster

Un fotograma representativo (la marca con su lema, por ejemplo) **sacado del máster** o con
`remotion still` sin blur. Nunca de un render con blur del navegador (lleva su desplazamiento de
fondo). JPEG calidad 90+.

## QA

`scripts/qa.sh`:

```bash
scripts/qa.sh sheet out/promo-web.mp4 out/qa-sheet.jpg 12 80 140 …     # hoja normal
scripts/qa.sh boost out/promo-web.mp4 out/qa-boost.jpg 30 148 1232 …   # hoja realzada 0–30 %

# Medir el fondo: extraer el mismo fotograma del web y del máster, y comparar.
f=1240; t=$(python3 -c "print(($f + 0.5) / 30)")
ffmpeg -v error -ss $t -i out/promo-web.mp4 -frames:v 1 -vf scale=in_color_matrix=bt709 web.png
ffmpeg -v error -ss $t -i out/master.mp4    -frames:v 1 -vf scale=in_color_matrix=bt709 ref.png
python3 scripts/bgcheck.py web.png               # dispersión del fondo liso
python3 scripts/bgcheck.py web.png --ref ref.png # lo que añade la compresión
```

Bien: ≤ 0,6 niveles. Entre 0,6 y 0,8, mira ese fotograma realzado: suele ser un parche de medio
nivel que no se aprecia sin realce. Desde ~0,9 (lo que daba el blur del navegador) se ve en un buen
monitor. Con movimiento, la referencia ha de ser el máster (mismo blur); un `remotion still` sin
blur solo vale como referencia en planos quietos.

Qué fotogramas elegir:
- Reposo de cada capítulo (composición y legibilidad).
- Mitad de cada transición y del movimiento más rápido (blur, solapes, texto duplicado).
- Todos los planos con fondo oscuro y algo que brilla o se mueve encima (bandas, bloques, tintes).

Comprobaciones finales:

```bash
ffprobe -v error -show_entries format=duration,size:stream=codec_name,color_space,color_primaries,color_transfer -of compact out/video-web.mp4
ffprobe -v error -count_frames -show_entries stream=nb_read_frames -of csv=p=0 out/video-web.mp4   # = TOTAL
ffmpeg -nostats -i out/video-web.mp4 -af ebur128=peak=true -f null - 2>&1 | tail -12               # LUFS y pico
```

## Lo que se entrega

- MP4 web, WebM, póster, hoja de contactos y el máster de alta calidad aparte.
- Storyboard actualizado (capítulos en fotogramas y segundos, qué es real y qué ilustrativo).
- Scripts que lo regeneran de cero.
- Al usuario: tamaños, sonoridad, qué es ilustrativo, y que la aprobación es suya.
