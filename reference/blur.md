# Motion blur sin artefactos

## Por qué no dentro del navegador

`CameraMotionBlur` de Remotion (y cualquier variante que apile copias con opacidad) mezcla las
muestras **a 8 bits**:

- con `plus-lighter` y opacidad `1/n`, cada muestra se redondea por separado: los oscuros se
  desplazan de canal (un `27,30,35` sale `24,32,32`, tinte verde);
- con media progresiva (`opacity: 1/(k+1)`), el fondo baja 1–2 niveles, **distinto por zonas**
  (las capas de composición de Chrome): rectángulos que la compresión convierte en cortes;
- además silencia el audio de su subárbol (hay que duplicar la escena para el sonido).

Sirve para previsualizar en el Studio, no para el máster.

## Subfotogramas promediados

1. Una composición sin blur a `SUB` veces la cadencia, que congela el tiempo en fracciones
   (`templates/Subframes.tsx` y `templates/Root.tsx`):

```tsx
// templates/Subframes.tsx
export const SUB = 24;
export const Subframes = () => {
  const frame = useCurrentFrame();
  return <Freeze frame={frame / SUB}><Main /></Freeze>;
};
// Root.tsx
<Composition id="MainSub" component={Subframes} durationInFrames={TOTAL * SUB} fps={FPS * SUB} width={1920} height={1080} />
```

2. Render en un intermedio de 10 bits (ProRes HQ), con el temporal en disco.
3. ffmpeg se queda con `SHUTTER` instantes de cada `SUB`, los promedia en 16 bits y toma uno por
   fotograma. Fondo idéntico (la media de valores iguales es exacta) y estelas continuas.

```bash
scripts/blur.sh src/index.ts MainSub Main 30 out/master.mp4 24 17
RANGE=1230-1259 scripts/blur.sh src/index.ts MainSub Main 30 out/tramo.mp4   # solo un tramo
```

El script comprueba el espacio antes de empezar, manda el temporal de Remotion al disco, renderiza
el audio aparte y une todo en un H.264 CRF 12 con audio ALAC, listo para `deliver.sh`.

| Ajuste | Valor | Por qué |
|---|---|---|
| `SUB` | 24 | 10 dejaba copias escalonadas en barridos y en la cámara rápida |
| `SHUTTER` | 17 (≈ 255°) | estela de cine; 7 de 10 se veía a pasos |
| Intermedio | ProRes HQ 10 bits | ≈ 170 KB por instante: un minuto a 30 fps y 24 instantes ≈ 7,5 GB |
| Concurrencia | núcleos − 2 | |
| Temporal | `TMPDIR=<disco>` | `/tmp` en RAM se llena en el cosido final (hace una copia) y el render entero se pierde |

Coste: ~2–2,5× un render con blur del navegador de 6 muestras, y un paso de ffmpeg de 15–20 min
para un minuto de vídeo. Espacio: `fotogramas × SUB × 170 KB`, por 2,2 durante el cosido.
El obturador va hacia delante (instantes `f … f+0,67`): el desfase con el audio es de ~11 ms,
imperceptible.

## Requisitos de la escena

- Todo función de `frame`, con fotogramas fraccionarios (ver motion.md). Nada de `Math.round` en
  posiciones, cámaras o tablas.
- No leer `fps` de `useVideoConfig()`: en la composición de subfotogramas valdría `FPS·SUB`.
- El audio se renderiza aparte desde la composición normal (`--codec=wav`) y se une al promediar.
- `Freeze` silencia el audio: en `MainSub` renderiza con `--muted`.

## Comprobación

- Fotogramas a mitad de los movimientos más rápidos (zoom a través de un texto, barrido entre
  planos, objeto que pasa junto a la cámara): estela continua, sin contornos repetidos.
- Fondo oscuro realzado (0–30 %): un solo valor en todo el fotograma.
- `bgcheck.py` sobre fotogramas en reposo del máster: ≤ 0,6 niveles. Medido en un caso real: el
  blur del navegador dio 0,93–1,03 (rectángulos visibles); el promediado, 0,21–0,25.
- Fotogramas en reposo: idénticos a un `remotion still` sin blur.
