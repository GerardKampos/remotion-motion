# Movimiento, tiempo y legibilidad

## Rejilla de tempo

Elige el tempo para que un tiempo sea un número entero de fotogramas: a 30 fps, 120 BPM = 15
fotogramas por tiempo y 60 por compás (también 90 BPM = 20, 100 BPM = 18). Todo se coloca en esa
rejilla:

```ts
export const FPS = 30;
export const PER_BEAT = 15;            // 120 BPM a 30 fps
const span = (from: number, to: number) => ({ from, duration: to - from });
export const CHAPTERS = {
  hook: span(0, 150),                  // cortes siempre en múltiplos de PER_BEAT
  brand: span(150, 270),
  // …
} as const;
export const TOTAL = 1860;
```

- Los cortes entre capítulos, en tiempo. Los acentos (golpe de una palabra clave, aparición de una
  tarjeta, impacto de marca), en tiempo o medio tiempo.
- Si un capítulo necesita más aire, añade **un tiempo entero** y regenera la música con la misma
  rejilla (las secciones de la música también van en tiempos). Mueve los capítulos posteriores.
- Sincronía ≠ bombeo: nada escala ni parpadea con cada golpe de bombo. Se sincronizan los
  **eventos**, no un latido continuo.

## Curvas

```ts
export const EASE_OUT = Easing.bezier(0.16, 1, 0.3, 1);   // entradas: rápida y se asienta
export const SNAP     = Easing.bezier(0.1, 0.9, 0.1, 1);  // golpes, «pop»
export const IN_OUT   = Easing.bezier(0.65, 0, 0.35, 1);  // viajes de cámara y desplazamientos
export const WHIP     = Easing.bezier(0.85, 0, 0.15, 1);  // barridos entre planos
export const ACCEL    = Easing.bezier(0.55, 0, 1, 0.45);  // salidas que se van
```

- `ease(frame, from, duration, curve)` → 0…1 con clamp, y `mix(p, a, b)` para todo lo demás.
  `keys(frame, [[f, v], …])` para trayectorias con paradas (cada tramo con su curva).
- Lineal solo para tecleo, escaneos y velocidades constantes. Velocidad continua: si un objeto se
  para en un punto, que la curva frene ahí (in-out), no que cambie de golpe.
- Rebote: un sobrepaso pequeño (`[[at, 88], [at+8, -7], [at+14, 0]]` en grados) vende peso sin
  parecer de dibujos.

## Tiempo fraccionario (obligatorio si hay blur)

El blur muestrea instantes como 120,35. Cualquier función que haga `Math.round(frame)` o lea
`tabla[frame]` mueve todo a saltos y produce dos copias nítidas en vez de una estela.

```ts
// Mal: tabla[Math.round(frame)]
const at = (frame: number) => {
  const f = Math.max(0, Math.min(N, frame));
  const i = Math.min(N - 1, Math.floor(f));
  return mix(f - i, TABLE[i], TABLE[i + 1]);   // interpola entre entradas
};
```

Lo discreto (texto tecleado, contadores) sí va a saltos; eso es correcto y el blur lo funde.

## Cámara creíble

Si los objetos vuelan hacia la cámara cada uno con su curva, se percibe que «se mueven las cosas».
Para que se mueva la cámara:

1. **Mundo fijo.** Cada elemento tiene `x, y, z` en el mundo y no se anima por su cuenta.
2. **Una cámara**: `z(t)` integrando una velocidad continua, más un balanceo suave
   (`x = 70·sin(t/21)`, `y = 40·sin(t/16+1)`, giro de 1–1,5°) y una lente que se abre algo al
   acelerar.
3. **Proyección única** para todo: `s = lens / (z − cam.z)`, `screen = centro + (pos − cam)·s`.
   El paralaje sale solo.
4. **Aparecen desde el fondo**: visibilidad que sube de 0 a 1 entre `far` y `0,65·far`, y se apaga
   justo antes de rozar la cámara.
5. **Frenar para leer**: velocidad baja en el instante de lectura de cada elemento
   (p. ej. `10 + 245·sin²(π·(t−beat)/15)`) y colocar cada elemento a distancia de lectura en su
   tiempo (`z = cam.z(beat) + READ`). Comprueba que en ese instante el texto sale nítido.
6. Separar carriles: lo lejano se agrupa cerca del punto de fuga; si las tarjetas cercanas tienen
   el borde interior lejos del centro, las del fondo no quedan tapadas.

## Legibilidad

- Al ancho real de reproducción. Para una web a 900 px de ancho, un vídeo 1080p se ve al 47 %:
  32 px en el render = 15 px en pantalla. Cuerpo importante ≥ 24–28 px; titulares 56–110 px.
- Una cosa que leer cada vez; el resto, quieto o fuera. Si hay dos columnas (título fijo a un lado,
  acción al otro), un velo oscuro bajo el título para que nada lo atraviese.
- Tiempo de lectura: titular corto ≥ 1,2 s quieto y legible; añade ~0,4 s por palabra extra.
  Contar desde que el último elemento se asienta, no desde que empieza a entrar.
- Historias de interfaz: mejor una ventana grande y centrada cada vez, que se recoge cuando entra
  la siguiente, que tres ventanas pequeñas a la vez. Nunca que la nueva tape a la anterior.
- Texto tecleado: reserva el ancho final (`visibility: hidden` en lo que falta). En texto centrado
  es obligatorio; en alineado a la izquierda evita saltos de línea.

## Transiciones

- Ninguna «de diapositiva»: el contenido sale con un zoom a través, un barrido o un movimiento de
  cámara, y el siguiente entra con la inercia del anterior. 8–12 fotogramas.
- Fondo quieto durante la transición; lo que se mueve es el contenido.
- Destellos y fogonazos: con mucha mesura. Un círculo borroso que crece hasta tapar la pantalla
  sobre oscuro casi siempre se ve barato y además se comprime mal.
- Revisa el fotograma central de cada transición: solapes de texto de la frase que sale con la que
  entra (2–3 fotogramas con dos frases encima se ven sucios).

## Paleta de movimiento por tipo de elemento

| Elemento | Entrada | Asentado | Salida |
|---|---|---|---|
| Titular por palabras | escala 1,5→1 + desenfoque 16→0, 7 fot. por palabra, 3 fot. entre palabras | quieto | sube y se desvanece |
| Tarjeta / ventana | desde 40–160 px con SNAP, 10–14 fot. | deriva mínima (escala +0,06 % por fot.) | hacia el lado contrario con ACCEL |
| Fila de tabla que se rellena | valor sube 8 px y aparece en 6 fot.; destello de fondo que se apaga en 14 | — | — |
| Cursor | trayectoria in-out entre puntos, pulsación = escala 0,82 + onda | — | se desvanece |
| Icono de estado | pop con sobrepaso 1,08 → 1 | — | — |
