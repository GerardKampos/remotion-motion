# Imagen limpia: bandas, brillos, sombras y color

Chrome compone a 8 bits por canal. En fondos claros casi nunca se nota; en fondos oscuros, cada
nivel es visible y la compresión H.264 lo amplifica: un escalón de 1 nivel se convierte en un
bloque de 16×16 con borde duro, y a poco bitrate en una mancha de color que tiembla.

## Qué evitar en fondos oscuros

| Recurso | Problema | Alternativa |
|---|---|---|
| Viñeteado CSS (`radial-gradient` a negro) | 3–5 niveles repartidos en media pantalla: bandas anchas y un parche cuadrado en las esquinas al comprimir | fondo liso |
| Sombra negra larga (`0 60px 120px rgba(0,0,0,.8)`) | degradado largo de 18→5: bloques al moverse | sombra corta (`0 24px 44px -18px rgba(0,0,0,.55)`) |
| Halo con `filter: blur(60px)` | anillos concéntricos y un aro **más oscuro que el fondo** donde el halo se apaga | sprite con tramado + `plus-lighter` |
| `box-shadow` de color como brillo | mismo aro oscuro al final de la sombra | `templates/Halo.tsx` (sombra en una capa aparte con `plus-lighter`) |
| Grano/ruido a pantalla completa | quita bandas, pero multiplica el bitrate por 3–4 (medido) | no; mejor quitar el degradado |
| Blur del navegador (`CameraMotionBlur`, capas con opacidad) | tinte verde en oscuros y desplazamiento de 1–2 niveles por zonas rectangulares | blur por subfotogramas (blur.md) |

## El aro oscuro de los brillos

Al componer un color tenue con alfa pequeño sobre oscuro, el redondeo a 8 bits deja un anillo
**por debajo** del fondo justo donde el brillo se apaga (medido: 0,8 niveles bajo el fondo en un
halo de `blur(60px)`). Se ve como un «borde raro» alrededor de los halos y la compresión lo marca.

Arreglo: que el brillo **sume** luz en lugar de cubrir.

```tsx
<Img src={staticFile('textures/glow.png')} style={{ mixBlendMode: 'plus-lighter', opacity: o }} />
```

Compruébalo midiendo el perfil radial: la luminancia media en anillos alrededor del centro nunca
debe bajar del valor del fondo.

## Halos con tramado

`scripts/glow.py` calcula un disco desenfocado en coma flotante y lo cuantiza con ruido
triangular de ±1 nivel. Sin escalones, y el tramado se mueve con el halo (no es grano global).

```bash
python3 scripts/glow.py public/textures/glow.png --color 133,149,191 --size 720 --radius 150 --sigma 60
```

Equivale a un círculo de 300 px con `blur(60px)`. Para un halo más pequeño, escala el elemento
(la imagen se muestrea bien hacia abajo).

## Fondos

- Liso por defecto. Si el diseño pide profundidad, consíguela con capas de contenido (tarjetas en
  distintas profundidades, desenfoque de elementos lejanos), no con un degradado de fondo.
- Si un degradado es imprescindible: contraste suficiente (≥ 20 niveles en el recorrido), fondo no
  demasiado oscuro, e imagen con tramado en vez de CSS. Y verifícalo en el MP4 final con realce.

## Sombras y profundidad

- Fondo claro: sombras suaves y cálidas (`rgba(86,62,30,.3)`), largas si quieres; no dan problemas.
- Fondo oscuro: casi no se ven y solo añaden degradados problemáticos. Cortas, o un borde de 1 px
  claro (`0 0 0 1px rgba(255,255,255,.08)`) para separar la ventana del fondo.

## Iconos y logotipos SVG

- Revisa a 4× los logos que dibujes en SVG: un trazo con `rotate()` cambia los radios de una
  elipse (rx/ry se intercambian) y el contorno deja de coincidir con el relleno.
- Logos de terceros: de un set con licencia clara (p. ej. Iconify `logos`, CC0), revisando las
  condiciones de uso de cada marca, y en una casilla blanca si el logo es de color, para que se
  lea sobre oscuro.

## Color

- Etiqueta todo en BT.709 (render y cada paso de ffmpeg). Sin etiqueta, unos reproductores usan
  BT.601 y otros BT.709 y los oscuros cambian de tono.
- Al analizar fotogramas, decodifica con `scale=in_color_matrix=bt709`.
- Un fondo `#12141a` tras la ida y vuelta RGB→YUV→RGB puede salir `17,18,25`: es esperable y
  uniforme. Lo que no es aceptable es que **varíe por zonas** dentro del mismo fotograma.

## Diagnóstico rápido

```bash
# ¿Del render o de la compresión? Mismo fotograma, sin comprimir y comprimido, realzados.
npx remotion still src/index.ts Main s.png --frame=1240
ffmpeg -ss $(python3 -c "print(1240.5/30)") -i out/promo-web.mp4 -frames:v 1 -vf scale=in_color_matrix=bt709 w.png
magick s.png w.png -level 0%,30% +append cmp.png
python3 scripts/bgcheck.py s.png w.png        # dispersión del fondo liso en cada uno
python3 scripts/bgcheck.py w.png --ref s.png  # lo que añade la compresión (solo en planos quietos)
```

- Defecto en ambos → es del diseño o del render (degradado, blur del navegador, halo).
- Solo en el comprimido → bitrate o ajustes del codificador (ver delivery.md).
