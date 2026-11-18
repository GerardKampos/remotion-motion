---
name: remotion-motion
description: Hacer vídeos de motion graphics con Remotion con acabado profesional: ritmo en rejilla de tempo, legibilidad, cámara creíble, motion blur sin artefactos, degradados y brillos sin bandas en fondos oscuros, color etiquetado, audio masterizado, codificación por tamaño y QA fotograma a fotograma. Usar siempre que se construya, revise o renderice un vídeo con Remotion (promo, explainer, reel, intro, animación de UI), o cuando el usuario se queje de cortes, bandas, halos raros, tintes de color, texto que tiembla o se duplica, blur escalonado, sonido estridente o un archivo demasiado grande. No decide la estética: decide que lo que se diseñe salga limpio.
---

# Remotion con acabado profesional

Esta skill no trata de qué contar ni de cómo debe verse: trata de que lo que se haga **salga
limpio**. Casi todos los defectos que un cliente nota («cortes en el fondo», «halos raros», «el
texto tiembla», «suena a tutorial de YouTube») vienen de cinco sitios: el tiempo, el navegador a
8 bits, la compresión, el audio y no haber mirado de verdad el resultado.

**Referencias** (léelas cuando llegues a esa parte):
- [reference/motion.md](reference/motion.md): rejilla de tempo, curvas, cámara, legibilidad, transiciones.
- [reference/image.md](reference/image.md): bandas, brillos, sombras, fondos, color, por qué Chrome falla.
- [reference/blur.md](reference/blur.md): motion blur por instantes promediados fuera del navegador.
- [reference/audio.md](reference/audio.md): efectos, música, ducking y masterizado a −14 LUFS.
- [reference/delivery.md](reference/delivery.md): máster, MP4 web por tamaño, WebM, póster y QA.

## Requisitos

Node 18+ con Remotion 4, `ffmpeg` con libx264, libvpx-vp9 y libopus, ImageMagick 7 (`magick`) y
Python 3 con `numpy`, `scipy`, `soundfile` y `pillow`. Scripts probados en Linux y escritos para
macOS también (bash 3.2, sin `df`, `nproc` ni `mktemp -p`).

## Piezas

Cópialas al proyecto y adáptalas. `<skill>` es la carpeta de esta skill.

| Pieza | Para qué |
|---|---|
| `templates/beat.ts` | fps, tempo, `PER_BEAT`, `CHAPTERS` y `TOTAL`: el tiempo del vídeo en un sitio |
| `templates/Main.tsx`, `templates/Root.tsx` | esqueleto con un `Sequence` por capítulo y las dos composiciones (normal y de instantes) |
| `templates/motion.ts` | curvas, `ease`, `mix`, `keys`, `sample` (tablas sin redondear), `integrate`, `typed`, `seeded` |
| `templates/Typed.tsx` | texto tecleado que no se recoloca |
| `templates/Subframes.tsx` | la composición a 24 instantes por fotograma para el blur |
| `templates/Halo.tsx` | brillo que suma luz, sin aro oscuro |
| `templates/Sfx.tsx` | `<Sfx at name />`, `<Typing />` y `<Words />` sincronizados al fotograma |
| `scripts/sfx.py` | biblioteca de efectos sintetizados → `public/sfx/*.wav` |
| `scripts/glow.py` | halo con tramado → `public/textures/glow.png` |
| `scripts/blur.sh` | máster con motion blur promediado fuera de Chrome |
| `scripts/deliver.sh` | audio a −14 LUFS, MP4 web por tamaño, WebM, póster y hoja de contactos |
| `scripts/master.py` | masterizado de audio (lo usa `deliver.sh`) |
| `scripts/qa.sh`, `scripts/bgcheck.py` | hojas de revisión y medición del fondo |

Arranque típico:

```bash
npx create-video@latest            # o un proyecto Remotion existente
cp <skill>/templates/*.ts* src/    # Root.tsx sustituye al de la plantilla
mkdir -p scripts && cp <skill>/scripts/* scripts/
python3 scripts/sfx.py public/sfx
python3 scripts/glow.py public/textures/glow.png --color 133,149,191
```

## Flujo

1. **Brief y storyboard en tiempo.** Duración, formato, fps (30 por defecto), tempo de la música y
   capítulos en fotogramas que caen en tiempos (`beat.ts`). Escribe el storyboard en un `.md` y
   mantenlo al día: es lo que permite cambiar algo sin romper lo demás.
2. **Construir por capítulos**, cada uno su componente con fotogramas locales. Nada de tiempos
   sueltos: constantes con nombre (`MAIL_IN`, `fillAt(i)`, `STAMP`) derivadas unas de otras.
3. **Borradores sin blur** para iterar rápido. Renderiza **solo el tramo** que cambia
   (`--frames=a-b`) y enséñaselo así al usuario; el vídeo entero, solo al cerrar una ronda.
4. **Revisión con ojos** antes de enseñar nada (ver «Mirar de verdad»).
5. **Máster** con `scripts/blur.sh` y **entregables** con `scripts/deliver.sh`. Revisión final
   sobre el archivo comprimido, no sobre el render.

Feedback de diseño: si es de concepto, propón antes de hacer; los arreglos técnicos, aplícalos sin
preguntar. Si una idea no convence dos veces, ofrece opciones con vista previa en lugar de una
tercera variante a ciegas. Enseña cada parte cambiada aislada; no rehagas lo que ya gustó.

## Reglas de acabado (las que más se rompen)

**Tiempo**
- Todo es función pura de `frame` y **acepta fotogramas fraccionarios**. Nada de `Math.round` ni
  tablas indexadas por entero en posiciones o cámaras (`sample()` interpola). El blur muestrea
  instantes intermedios; si el tiempo se redondea, salen copias dobles.
- Cortes, entradas de palabras, golpes y acentos en la rejilla del tempo. Sincronizar no es
  bombear: nada debe latir con la música.
- Una cosa que leer cada vez. Mínimo ~1,2 s para un titular y ~0,4 s por palabra extra. Si la
  cámara se mueve, **frena** en el instante de lectura.

**Disposición**
- El texto que se teclea o crece **no puede recolocarse**: reserva su ancho (`Typed`). Un texto
  centrado que se recentra letra a letra sale duplicado con blur.
- Nada tapa lo que hay que leer: comprueba solapes en los fotogramas de entrada, salida y cruce,
  no solo en reposo.
- Legible al ancho real de reproducción (p. ej. 900 px en una web: un 1080p se ve al 47 %).
  Texto que importa ≥ 24 px a 1080p; 18–20 px solo para etiquetas.

**Cámara y movimiento**
- Para que «se mueva la cámara» y no las cosas: mundo fijo y una cámara que se desplaza; cada
  elemento se proyecta por su profundidad. Lo cercano se desplaza más: eso es el paralaje.
- Curvas con intención (salida rápida para entradas, in-out para viajes, aceleración para
  salidas). Nada lineal salvo tecleo y escaneos.

**Imagen (Chrome pinta a 8 bits)**
- Nada de degradados amplios de pocos niveles sobre oscuro (viñeteados, sombras negras largas,
  halos enormes): se rompen en bandas y la compresión los convierte en bloques. Fondos lisos;
  sombras cortas sobre oscuro.
- Halos grandes: imagen con tramado (`glow.py`), no `filter: blur()`. Brillos de luz con
  `mix-blend-mode: plus-lighter` (`Halo`), que no deja aro oscuro.
- Nunca el blur dentro del navegador para el máster (`CameraMotionBlur` ni capas con opacidad):
  tiñe los oscuros y desplaza el fondo por zonas. Ver [reference/blur.md](reference/blur.md).
- Imágenes con `<Img>` de Remotion, que espera a que carguen; nunca `background-image` en CSS.
- Logos SVG propios: revísalos ampliados; un trazo girado puede no coincidir con su relleno.

**Color y salida**
- BT.709 etiquetado en el render (`--color-space=bt709`) y en cada `ffmpeg`. Sin etiqueta, cada
  reproductor interpreta el color a su manera.
- Máster casi sin pérdida y **una sola** compresión fuerte hasta el entregable. El MP4 web, en
  dos pasadas al tamaño pedido, con `aq-mode=3` para dar bits a las zonas oscuras.

**Audio**
- Un efecto por evento visual, en su fotograma. Teclado, palabras, clics y barridos, **distintos**
  entre sí. Barridos y brillos con paso bajo (~3 kHz): sin él suenan estridentes.
- La música acompaña: 8–12 dB por debajo de los efectos y con ducking donde se teclea o se lee.
- −14 LUFS integrados y −1 dBTP medido sobre el AAC final.

## Mirar de verdad

Un fotograma bonito en el Studio no demuestra nada. Antes de enseñar un resultado:

1. **Hoja de contactos** (`scripts/qa.sh sheet vídeo hoja.jpg f1 f2 …`): composición, solapes,
   texto cortado, momentos vacíos.
2. **Fotogramas de transición**, no solo de reposo: mitad de cada entrada, salida y barrido. Ahí
   aparecen las copias escalonadas, el texto duplicado y los solapes.
3. **Contraste exagerado** sobre oscuros (`scripts/qa.sh boost …`, niveles 0–30 %): revela bandas,
   rectángulos, tintes y bloques que en un buen monitor o a oscuras sí se ven.
4. **Medir el fondo** con `scripts/bgcheck.py`: sin referencia, la dispersión del fondo liso; con
   `--ref`, lo que ha añadido la compresión. Referencia: el **máster** si hay movimiento (mismo
   blur), un `remotion still` solo en planos quietos. Bien: ≤ 0,6 niveles; entre 0,6 y 0,8, mira
   el realce (suele ser medio nivel inapreciable); el blur del navegador daba ~1 y se veía.
5. **Sin comprimir frente a comprimido** sobre el mismo fotograma: si el defecto está en ambos, es
   del diseño o del render; si solo en el comprimido, del codificador. El arreglo es distinto.

Decodifica siempre con `scale=in_color_matrix=bt709`; si no, verás tintes que no existen.

## Trampas de entorno

- Renders largos, en segundo plano y **con el espacio comprobado antes** (`blur.sh` lo hace).
  `/tmp` puede estar en RAM: el temporal de Remotion va donde diga `TMPDIR`. ProRes HQ 1080p ≈
  170 KB por instante, y el cosido final hace una copia.
- Para revisar el blur final en un tramo sin renderizar todo: `RANGE=a-b scripts/blur.sh …`.
- `remotion render` en H.264 no admite `--crf=0`; para intermedios sin pérdida, ProRes o PNG.
- Para parar un render: `pkill -f "[r]emotion render"` (el corchete evita matar tu propio shell).
- Con instantes, ningún componente debe leer `fps` de `useVideoConfig()`: valdría `FPS·SUB`.
- Cifras en pantalla: compruébalas (sumas, totales) antes del render final. Un total mal sumado en
  un vídeo comercial es peor que cualquier banda.

## Checklist de entrega

- [ ] Hoja de contactos y fotogramas de transición revisados; nada tapa nada; nada se recoloca.
- [ ] Fondos oscuros sin rectángulos, tintes ni bloques en el MP4 final (realce + `bgcheck`).
- [ ] Blur continuo en los movimientos más rápidos, sin copias escalonadas.
- [ ] Texto legible al ancho real; cada lectura con tiempo suficiente.
- [ ] Audio a −14 LUFS ±0,5 y pico ≤ −1 dBTP; efectos distinguibles; música por debajo.
- [ ] BT.709 etiquetado en MP4 y WebM; tamaño dentro del límite; `+faststart`.
- [ ] Póster y hoja de contactos; storyboard al día; scripts que lo regeneran.
- [ ] Al usuario: tamaños, sonoridad y qué es ilustrativo o ficticio. La aprobación es suya.
