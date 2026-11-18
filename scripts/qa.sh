#!/usr/bin/env bash
# Hojas de revisión de un vídeo, decodificado con la matriz BT.709.
#   qa.sh sheet <video> <salida.jpg> <fotogramas…>   hoja normal (composición, solapes, transiciones)
#   qa.sh boost <video> <salida.jpg> <fotogramas…>   niveles 0–30 %: bandas, bloques, tintes en oscuros
# Fps leídos del vídeo. Para un fotograma de transición, pide el del medio de la transición.
set -euo pipefail
mode=$1; video=$2; out=$3; shift 3
fps=$(ffprobe -v error -select_streams v -show_entries stream=r_frame_rate -of csv=p=0 "$video")
tmp=$(mktemp -d)
i=0
for f in "$@"; do
  t=$(python3 -c "from fractions import Fraction as F; print(float(($f + 0.5) / F('$fps')))")
  ffmpeg -v error -y -ss "$t" -i "$video" -frames:v 1 -vf "scale=in_color_matrix=bt709,format=rgb24" "$tmp/raw.png"
  case "$mode" in
    boost) magick "$tmp/raw.png" -level 0%,30% "$tmp/raw.png" ;;
    sheet) ;;
    *) echo "modo: sheet | boost"; exit 1 ;;
  esac
  magick "$tmp/raw.png" -resize 480x -fill '#fbbf24' -undercolor '#000a' -pointsize 18 -annotate +6+20 "f$f" "$tmp/$(printf %04d $i).png"
  i=$((i + 1))
done
rm "$tmp/raw.png"
magick montage "$tmp"/*.png -tile 4x -geometry +3+3 -background '#333' "$out"
rm -rf "$tmp"
echo "$out"
