import { Composition } from 'remotion';
import { FPS, HEIGHT, TOTAL, WIDTH } from './beat';
import { Subframes, SUB } from './Subframes';
import { Main } from './Main';

/**
 * Dos composiciones: `Main` para el Studio, los borradores y el audio, y `MainSub` (la misma, a SUB
 * instantes por fotograma) para el máster con motion blur de scripts/blur.sh.
 */
export const Root = () => (
  <>
    <Composition id="Main" component={Main} durationInFrames={TOTAL} fps={FPS} width={WIDTH} height={HEIGHT} />
    <Composition id="MainSub" component={Subframes} durationInFrames={TOTAL * SUB} fps={FPS * SUB} width={WIDTH} height={HEIGHT} />
  </>
);

/** Nombre que importa el `src/index.ts` de los proyectos creados con `npx create-video`. */
export const RemotionRoot = Root;
