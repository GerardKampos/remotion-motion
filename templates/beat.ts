/**
 * Rejilla de tiempo del vídeo. Elige un tempo que dé un número entero de fotogramas por tiempo
 * (a 30 fps: 120 BPM = 15, 100 BPM = 18, 90 BPM = 20) y coloca cortes y acentos en ella.
 */
export const FPS = 30;
export const WIDTH = 1920;
export const HEIGHT = 1080;
export const BPM = 120;
export const PER_BEAT = (FPS * 60) / BPM;

export interface Chapter {
  from: number;
  duration: number;
}

const span = (from: number, to: number): Chapter => ({ from, duration: to - from });

/** Capítulos en fotogramas absolutos; cada corte en un múltiplo de PER_BEAT. */
export const CHAPTERS = {
  hook: span(0, 150),
  brand: span(150, 270),
  close: span(270, 360),
} as const;

export const TOTAL = 360;

/** El fotograma del tiempo `n`, para colocar acentos: `beat(4)` = 60 a 120 BPM. */
export const beat = (n: number) => Math.round(n * PER_BEAT);
