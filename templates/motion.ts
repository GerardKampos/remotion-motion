import { Easing, interpolate } from 'remotion';

/** Curvas con intención: entradas, golpes, viajes, barridos y salidas. */
export const EASE_OUT = Easing.bezier(0.16, 1, 0.3, 1);
export const SNAP = Easing.bezier(0.1, 0.9, 0.1, 1);
export const IN_OUT = Easing.bezier(0.65, 0, 0.35, 1);
export const WHIP = Easing.bezier(0.85, 0, 0.15, 1);
export const ACCEL = Easing.bezier(0.55, 0, 1, 0.45);

const CLAMP = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;

/** 0→1 entre `from` y `from + duration`. Acepta fotogramas fraccionarios (el blur los usa). */
export const ease = (frame: number, from: number, duration: number, easing = EASE_OUT) =>
  interpolate(frame, [from, from + Math.max(1, duration)], [0, 1], { ...CLAMP, easing });

export const mix = (p: number, a: number, b: number) => a + (b - a) * p;

export type Key = readonly [frame: number, value: number];

/** Trayectoria por tramos entre fotogramas clave; cada tramo con la curva dada. */
export const keys = (frame: number, points: readonly Key[], easing = IN_OUT) => {
  if (frame <= points[0][0]) return points[0][1];
  for (let i = 1; i < points.length; i++) {
    const [f1, v1] = points[i];
    const [f0, v0] = points[i - 1];
    if (frame <= f1) return mix(ease(frame, f0, f1 - f0, easing), v0, v1);
  }
  return points[points.length - 1][1];
};

/**
 * Tabla precalculada (p. ej. posición de cámara integrando una velocidad) leída en cualquier
 * instante: interpola entre entradas. Nunca `table[Math.round(frame)]`: con blur saldrían copias.
 */
export const sample = (table: readonly number[], frame: number) => {
  const last = table.length - 1;
  const f = Math.max(0, Math.min(last, frame));
  const i = Math.min(last - 1, Math.floor(f));
  return mix(f - i, table[i], table[i + 1]);
};

/** Integra una velocidad por fotograma: `travel[f]` es la distancia recorrida hasta `f`. */
export const integrate = (frames: number, speed: (f: number) => number) => {
  const travel = [0];
  for (let f = 1; f <= frames; f++) travel.push(travel[f - 1] + speed(f));
  return travel;
};

/** Texto tecleado entre `from` y `to`: lo visible y lo que falta (para reservar su ancho). */
export const typed = (text: string, frame: number, from: number, to: number) => {
  const n = Math.round(interpolate(frame, [from, to], [0, text.length], CLAMP));
  return { shown: text.slice(0, n), rest: text.slice(n) };
};

/** Generador pseudoaleatorio determinista: el mismo render siempre da lo mismo. */
export const seeded = (seed: number) => {
  let s = seed;
  return () => {
    s = (s * 1664525 + 1013904223) % 4294967296;
    return s / 4294967296;
  };
};
