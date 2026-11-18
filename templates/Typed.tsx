import { useCurrentFrame } from 'remotion';
import { typed } from './motion';

/**
 * Texto que se teclea sin recolocarse: lo que aún no ha salido ocupa su sitio, invisible.
 * Imprescindible en texto centrado (si no, se recentra letra a letra y el blur lo duplica).
 */
export const Typed = ({ text, from, to }: { text: string; from: number; to: number }) => {
  const frame = useCurrentFrame();
  const { shown, rest } = typed(text, frame, from, to);
  return (
    <>
      {shown}
      <span style={{ visibility: 'hidden' }}>{rest}</span>
    </>
  );
};
