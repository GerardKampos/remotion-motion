/**
 * Brillo alrededor de una caja que **suma** luz (`plus-lighter`). Con un `box-shadow` normal, el
 * redondeo a 8 bits deja un aro algo más oscuro que el fondo donde el brillo se apaga.
 * Uso: hijo absoluto de la caja (que debe tener `position` distinta de static).
 */
export const Halo = ({ radius, blur, alpha, rgb = '133,149,191' }: { radius: number; blur: number; alpha: number; rgb?: string }) => (
  <div style={{ position: 'absolute', inset: 0, borderRadius: radius, boxShadow: `0 0 ${blur}px rgba(${rgb},${alpha})`, mixBlendMode: 'plus-lighter', pointerEvents: 'none' }} />
);
