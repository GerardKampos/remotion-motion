# remotion-motion

**Skill de Claude Code para hacer vídeos de motion graphics con [Remotion](https://www.remotion.dev)
con acabado profesional.**

> *English:* a Claude Code skill for professional-finish motion graphics in Remotion: artifact-free
> motion blur, banding-free dark backgrounds, tagged color, mastered audio, size-targeted encoding
> and frame-by-frame QA. Docs are in Spanish.

No decide cómo debe verse tu vídeo: decide que lo que diseñes **salga limpio**. Nace de un vídeo
promocional real de 62 s en el que cada defecto de esta lista apareció, se midió y se resolvió.

## Qué resuelve

| Lo que se ve | Por qué pasa | Qué hace la skill |
|---|---|---|
| «Cortes», rectángulos o tintes en fondos oscuros | El motion blur del navegador mezcla las muestras a 8 bits; los degradados de pocos niveles se rompen al comprimir | Blur fuera de Chrome: 24 instantes por fotograma promediados en 16 bits. Fondos lisos |
| Halos con anillos o un aro más oscuro que el fondo | `filter: blur()` y `box-shadow` redondean a 8 bits | Halo con tramado y brillos que suman luz (`plus-lighter`) |
| El color cambia según el reproductor | Vídeo sin espacio de color etiquetado | BT.709 en el render y en cada paso de `ffmpeg` |
| Texto que tiembla o sale duplicado | Tiempo redondeado; texto que se recentra al teclearse | Tiempo fraccionario en todo; ancho reservado |
| Estelas a saltos, copias escalonadas | Pocas muestras de blur | 17 instantes de 24 por fotograma |
| Sonido estridente o «de tutorial» | Barridos sin filtrar, música protagonista | Efectos sintetizados con paso bajo, música por debajo, −14 LUFS |
| Archivo enorme o con bloques | Una pasada sin control de tamaño | Dos pasadas al tamaño pedido, más bits a las zonas oscuras |

## Instalación

```bash
# Para todos tus proyectos
git clone https://github.com/GerardKampos/remotion-motion ~/.claude/skills/remotion-motion

# Solo para un proyecto (desde su raíz)
git clone https://github.com/GerardKampos/remotion-motion .claude/skills/remotion-motion
```

Actualizar: `git -C ~/.claude/skills/remotion-motion pull`.

### Requisitos

- Node 18+ y Remotion 4
- `ffmpeg` con libx264, libvpx-vp9 y libopus
- ImageMagick 7 (`magick`)
- Python 3 con `numpy`, `scipy`, `soundfile` y `pillow`:
  `pip install numpy scipy soundfile pillow`

## Uso

Claude Code la carga sola cuando trabajas un vídeo con Remotion. Por ejemplo:

- «Hazme un vídeo promocional de 45 s en Remotion para mi producto»
- «En el vídeo se ven cortes en el fondo oscuro, revísalo»
- «Saca la versión final por debajo de 15 MB, en MP4 y WebM»

También puedes nombrarla: «usa la skill remotion-motion».

### Flujo con los scripts

```bash
# 1. Proyecto y piezas
npx create-video@latest                      # plantilla en blanco
cp ~/.claude/skills/remotion-motion/templates/*.ts* src/
mkdir -p scripts && cp ~/.claude/skills/remotion-motion/scripts/* scripts/
python3 scripts/sfx.py public/sfx                                   # efectos de sonido
python3 scripts/glow.py public/textures/glow.png --color 133,149,191 # halo sin bandas

# 2. Borradores sin blur, por tramos
npx remotion studio src/index.ts
npx remotion render src/index.ts Main out/tramo.mp4 --frames=120-240

# 3. Máster con motion blur (comprueba el espacio en disco antes de empezar)
scripts/blur.sh src/index.ts MainSub Main 30 out/master.mp4
RANGE=120-180 scripts/blur.sh src/index.ts MainSub Main 30 out/tramo-final.mp4

# 4. Entregables: audio a −14 LUFS, MP4 web < 15 MB, WebM, póster y hoja de contactos
scripts/deliver.sh out/master.mp4 out/promo 14400000 250

# 5. Revisión
scripts/qa.sh sheet out/promo-web.mp4 out/hoja.jpg 30 150 300 450
scripts/qa.sh boost out/promo-web.mp4 out/realce.jpg 30 150 300 450
python3 scripts/bgcheck.py web.png --ref master.png
```

## Qué incluye

```
remotion-motion/
├── SKILL.md              Lo que lee Claude: flujo, reglas de acabado, revisión y checklist
├── reference/
│   ├── motion.md         Rejilla de tempo, curvas, cámara con paralaje, legibilidad, transiciones
│   ├── image.md          Bandas, halos, sombras, fondos y color: qué evitar y por qué
│   ├── blur.md           Motion blur por instantes promediados fuera del navegador
│   ├── audio.md          Efectos, música, ducking y masterizado a −14 LUFS
│   └── delivery.md       Máster, MP4 web por tamaño, WebM, póster y revisión
├── templates/
│   ├── beat.ts           fps, tempo, capítulos y duración en un solo sitio
│   ├── Main.tsx          Esqueleto con un Sequence por capítulo
│   ├── Root.tsx          Composición normal y composición de instantes
│   ├── Subframes.tsx     El vídeo a 24 instantes por fotograma
│   ├── motion.ts         Curvas, ease, keys, sample, integrate, typed, seeded
│   ├── Typed.tsx         Texto tecleado que no se recoloca
│   ├── Halo.tsx          Brillo que suma luz, sin aro oscuro
│   └── Sfx.tsx           Efectos anclados al fotograma: Sfx, Typing, Words
└── scripts/
    ├── blur.sh           Máster con motion blur (instantes en ProRes → media en 16 bits)
    ├── deliver.sh        Audio, MP4 web en dos pasadas, WebM, póster y hoja de contactos
    ├── master.py         Masterizado de audio a −14 LUFS / −1 dBTP
    ├── sfx.py            Biblioteca de efectos sintetizados (sin muestras de terceros)
    ├── glow.py           Halo con tramado
    ├── qa.sh             Hojas de revisión, normal y con contraste exagerado
    └── bgcheck.py        Mide la uniformidad del fondo y lo que añade la compresión
```

## Resultados medidos

En el vídeo del que sale la skill (62 s, 1080p, 30 fps):

| Medida | Antes | Después |
|---|---|---|
| Dispersión del fondo oscuro (`bgcheck`) | 0,93–1,03 niveles con el blur del navegador | 0,21–0,25 con el blur promediado |
| Aro bajo el halo de la marca | 0,8 niveles por debajo del fondo | no baja del fondo |
| Estela en el movimiento más rápido | copias escalonadas con 7 de 10 instantes | continua con 17 de 24 |
| Entregable | — | 14,5 MB, −14,2 LUFS, −1,5 dBTP, BT.709 |

Y lo que no funcionó, para no repetirlo: grano a pantalla completa (quita las bandas pero
multiplica el bitrate por 3–4) y perseguir décimas con parámetros del codificador (dos
codificaciones equivalentes ya varían ±0,3 niveles).

## Limitaciones

- Scripts probados en Linux con Remotion 4.0.537, Node 22, ffmpeg 9, ImageMagick 7.1 y Python
  3.14. Están escritos para macOS (bash 3.2, sin `df`, `nproc` ni `mktemp -p`), pero no se han
  ejecutado ahí.
- El máster con blur es lento: un minuto de vídeo son ~25–35 min de render y ~15–20 de promedio
  con 12 hilos, y ~7,5 GB de disco temporal (el doble durante el cosido final).
- Cadencias enteras (24, 25, 30, 60 fps).
- La documentación está en español.

## Licencia

[MIT](LICENSE).
