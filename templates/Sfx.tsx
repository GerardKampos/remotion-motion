import { Audio, Sequence, staticFile } from 'remotion';

/** Nombres de public/sfx/*.wav (scripts/sfx.py). */
export type SfxName =
  | 'key0' | 'key1' | 'key2' | 'key3' | 'key4' | 'key5' | 'key-space' | 'key-enter'
  | 'click' | 'pop' | 'pop-soft' | 'tick' | 'whoosh' | 'whoosh-long' | 'swoosh'
  | 'chime' | 'deny' | 'shimmer' | 'impact' | 'riser'
  | 'word0' | 'word1' | 'word2' | 'word3' | 'word4' | 'word5';

/** Nivel de cada familia respecto a la música: los barridos, muy por debajo. */
const GAIN: Partial<Record<SfxName, number>> = { whoosh: 0.55, 'whoosh-long': 0.55, swoosh: 0.45, riser: 0.5, impact: 0.7, shimmer: 0.6, tick: 0.75, deny: 0.8 };
const MASTER = 0.8;
/** Duración en fotogramas de los efectos largos; el resto, 20. */
const LENGTH: Partial<Record<SfxName, number>> = { shimmer: 80, impact: 45, riser: 50, chime: 40, 'whoosh-long': 28, deny: 20 };

/** Un efecto anclado al fotograma del evento visual que lo produce. */
export const Sfx = ({ at, name, volume = 1 }: { at: number; name: SfxName; volume?: number }) => {
  if (at < 0) return null;
  return (
    <Sequence from={at} durationInFrames={LENGTH[name] ?? 20} layout="none">
      <Audio src={staticFile(`sfx/${name}.wav`)} volume={volume * (GAIN[name] ?? 1) * MASTER} />
    </Sequence>
  );
};

const KEYS: SfxName[] = ['key0', 'key1', 'key2', 'key3', 'key4', 'key5'];

/** Tecleo: un golpe por carácter, máximo uno cada 2 fotogramas, con la misma rampa que `typed()`. */
export const Typing = ({ text, from, to, volume = 0.5 }: { text: string; from: number; to: number; volume?: number }) => {
  const hits = [...text].reduce<{ at: number; name: SfxName }[]>((acc, ch, i) => {
    const at = Math.round(from + ((to - from) * (i + 1)) / text.length);
    if (acc.length && at - acc[acc.length - 1].at < 2) return acc;
    return [...acc, { at, name: ch === ' ' ? 'key-space' : KEYS[(i * 7 + ch.charCodeAt(0)) % KEYS.length] }];
  }, []);
  return (
    <>
      {hits.map((h) => (
        <Sfx key={h.at} at={h.at} name={h.name} volume={volume * (h.name === 'key-space' ? 0.85 : 1)} />
      ))}
    </>
  );
};

const HITS: SfxName[] = ['word0', 'word1', 'word2', 'word3', 'word4', 'word5'];

/** Palabras que entran: un golpe sordo y grave por palabra, con variantes para que no suene a máquina. */
export const Words = ({ ats, volume = 0.55 }: { ats: readonly number[]; volume?: number }) => (
  <>
    {ats.map((at, i) => (
      <Sfx key={at} at={at} name={HITS[i % HITS.length]} volume={volume} />
    ))}
  </>
);
