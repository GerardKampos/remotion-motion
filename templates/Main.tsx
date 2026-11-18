import { AbsoluteFill, Sequence } from 'remotion';
import { CHAPTERS } from './beat';

/**
 * Esqueleto: un `Sequence` por capítulo, cada capítulo con sus fotogramas locales. Fondo liso a
 * pantalla completa debajo de todo. Sustituye los capítulos por los tuyos.
 */
const Placeholder = ({ label }: { label: string }) => (
  <AbsoluteFill style={{ alignItems: 'center', justifyContent: 'center', color: '#fff', fontSize: 96, fontFamily: 'sans-serif' }}>{label}</AbsoluteFill>
);

export const Main = () => (
  <AbsoluteFill style={{ backgroundColor: '#12141a' }}>
    {Object.entries(CHAPTERS).map(([name, c]) => (
      <Sequence key={name} name={name} from={c.from} durationInFrames={c.duration}>
        <Placeholder label={name} />
      </Sequence>
    ))}
  </AbsoluteFill>
);
