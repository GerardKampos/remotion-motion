#!/usr/bin/env bash
# Entregables a partir del máster (H.264 de alta calidad con audio, BT.709; p. ej. el de blur.sh).
#   deliver.sh <master.mp4> <prefijo-salida> [bytes-max=14400000] [fotograma-póster=0]
# Ejemplo: scripts/deliver.sh out/master.mp4 out/promo 14400000 250
#
# Genera <prefijo>-fast.mp4 (audio −14 LUFS / −1 dBTP, vídeo copiado), <prefijo>-web.mp4 (dos pasadas
# por tamaño, más bits a las zonas oscuras), <prefijo>.webm, <prefijo>-poster.jpg y
# <prefijo>-contact.jpg.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
master=$1; pre=$2; max=${3:-14400000}; poster=${4:-0}
COLOR=(-colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv)
mkdir -p "$(dirname "$pre")"

python3 "$here/master.py" "$master" "$pre-fast.mp4"

dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$pre-fast.mp4")
kbps=$(python3 -c "print(int(($max * 8 / $dur - 192000 - 24000) / 1000))")
X264="aq-mode=3:aq-strength=1.0:chroma-qp-offset=-2:deadzone-inter=8:deadzone-intra=6"
pass=$(mktemp -d "$(dirname "$pre")/pass.XXXXXX")
for p in 1 2; do
  out="$pre-web.mp4"; [ "$p" = 1 ] && out=/dev/null
  ffmpeg -v error -y -i "$pre-fast.mp4" -map 0:v -map 0:a -c:v libx264 -preset slower -profile:v high -level 4.1 \
    -b:v "${kbps}k" -maxrate "$((kbps * 3))k" -bufsize "$((kbps * 4))k" -pass "$p" -passlogfile "$pass/x264" -x264-params "$X264" \
    -pix_fmt yuv420p "${COLOR[@]}" -c:a copy -movflags +faststart -f mp4 "$out"
done
for p in 1 2; do
  out="$pre.webm"; [ "$p" = 1 ] && out=/dev/null
  ffmpeg -v error -y -i "$pre-fast.mp4" -c:v libvpx-vp9 -crf 28 -b:v 0 -row-mt 1 -tile-columns 2 -auto-alt-ref 1 -lag-in-frames 25 \
    -pass "$p" -passlogfile "$pass/vp9" -pix_fmt yuv420p "${COLOR[@]}" -c:a libopus -b:a 128k -f webm "$out"
done
rm -rf "$pass"

ffmpeg -v error -y -i "$master" -vf "select=eq(n\,$poster),scale=in_color_matrix=bt709" -frames:v 1 -q:v 2 "$pre-poster.jpg"
total=$(ffprobe -v error -count_frames -show_entries stream=nb_read_frames -select_streams v -of csv=p=0 "$pre-web.mp4")
"$here/qa.sh" sheet "$pre-web.mp4" "$pre-contact.jpg" $(python3 -c "n = $total; print(' '.join(str(min(n - 1, int(n * k / 23))) for k in range(24)))")

ls -la "$pre-fast.mp4" "$pre-web.mp4" "$pre.webm" "$pre-poster.jpg" "$pre-contact.jpg"
ffprobe -v error -show_entries format=size,duration:stream=codec_name,color_space -of compact "$pre-web.mp4"
