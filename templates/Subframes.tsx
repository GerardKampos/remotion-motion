import { Freeze, useCurrentFrame } from 'remotion';
import { Main } from './Main';

/** Instantes por fotograma del vídeo final. Debe coincidir con el SUB que pases a scripts/blur.sh. */
export const SUB = 24;

/**
 * El vídeo a SUB veces la cadencia: cada fotograma de esta composición es un instante intermedio
 * del vídeo, sin motion blur. scripts/blur.sh los promedia en 16 bits fuera del navegador.
 * `Main` no debe aplicar blur propio: si tiene un modo con CameraMotionBlur para el Studio,
 * desactívalo aquí (p. ej. `<Main blur={false} />`).
 */
export const Subframes = () => {
  const frame = useCurrentFrame();
  return (
    <Freeze frame={frame / SUB}>
      <Main />
    </Freeze>
  );
};
