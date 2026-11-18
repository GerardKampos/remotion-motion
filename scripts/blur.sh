#!/usr/bin/env bash
# Máster con motion blur hecho fuera del navegador.
#   blur.sh <entry> <sub-id> <main-id> <fps> <salida.mp4> [SUB=24] [SHUTTER=17] [props-audio-json]
# Ejemplo: scripts/blur.sh src/index.ts MainSub Main 30 out/master.mp4 24 17 '{"blur":false}'
# Solo un tramo (para revisar con la calidad final): RANGE=1230-1259 scripts/blur.sh …
#
# 1. <sub-id>: el vídeo sin blur a SUB instantes por fotograma (templates/Subframes.tsx), en ProRes
#    HQ de 10 bits. El temporal de Remotion va al disco: /tmp suele estar en RAM y se llena.
# 2. El audio, desde la composición normal <main-id>.
# 3. ffmpeg se queda con SHUTTER de cada SUB instantes, los promedia en 16 bits y toma uno por
#    fotograma (obturador ≈ SHUTTER/SUB·360°). Fondo exacto y estelas continuas: mezclar dentro de
#    Chrome a 8 bits tiñe los oscuros y deja rectángulos que la compresión convierte en cortes.
set -euo pipefail
entry=$1; sub_id=$2; main_id=$3; fps=$4; out=$5
SUB=${6:-24}; SHUTTER=${7:-17}; props=${8:-'{}'}
mkdir -p "$(dirname "$out")"
work="$(cd "$(dirname "$out")" && pwd)/blur-work"
mkdir -p "$work/tmp"

range=()
if [ -n "${RANGE:-}" ]; then
  a=${RANGE%-*}; b=${RANGE#*-}
  frames=$(( (b - a + 1) * SUB ))
  range=(--frames="$((a * SUB))-$(((b + 1) * SUB - 1))")
  audio_range=(--frames="$a-$b")
else
  frames=$(npx remotion compositions "$entry" 2>/dev/null | awk -v id="$sub_id" '$1 == id {print $4}' || true)
  audio_range=()
fi

# ProRes HQ 1080p ≈ 170 KB por instante; el cosido final de Remotion hace una copia (×2,2 de margen).
python3 - "$work" "${frames:-0}" <<'PY' || exit 1
import shutil, sys
need = int(sys.argv[2]) * 170e3 / 1e9
free = shutil.disk_usage(sys.argv[1]).free / 1e9
print(f'Instantes: {sys.argv[2]}  intermedio ≈ {need:.1f} GB  libre: {free:.0f} GB')
sys.exit(0 if need * 2.2 < free else 'Espacio insuficiente: hace falta ~2,2× el intermedio')
PY
cores=$(python3 -c "import os; print(max(2, (os.cpu_count() or 4) - 2))")

TMPDIR="$work/tmp" npx remotion render "$entry" "$sub_id" "$work/sub.mov" ${range[@]+"${range[@]}"} --codec=prores --prores-profile=hq \
  --color-space=bt709 --muted --concurrency="$cores"
npx remotion render "$entry" "$main_id" "$work/audio.wav" ${audio_range[@]+"${audio_range[@]}"} --codec=wav --props="$props"

ffmpeg -v error -y -i "$work/sub.mov" -i "$work/audio.wav" -map 0:v -map 1:a \
  -vf "select='lt(mod(n\,$SUB)\,$SHUTTER)',format=yuv444p16le,tmix=frames=$SHUTTER,select='eq(mod(n\,$SHUTTER)\,$((SHUTTER - 1)))',setpts=N/($fps*TB),format=yuv420p" \
  -sws_flags accurate_rnd+full_chroma_int -r "$fps" -c:v libx264 -preset slow -crf 12 \
  -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv -c:a alac -shortest "$out"

rm -rf "$work"
ffprobe -v error -count_frames -show_entries stream=codec_type,nb_read_frames -of compact "$out"
