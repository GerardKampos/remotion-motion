# Audio: efectos, música y masterizado

El sonido es la mitad del acabado. Un vídeo sin efectos parece una presentación; uno con efectos
estridentes o música protagonista parece un tutorial.

## Efectos

- **Uno por evento visual**, colocado en el fotograma exacto con `<Sfx at={f} name=… />`
  (`templates/Sfx.tsx`). Nada de pistas de efectos montadas a ojo.
- **Familias distintas** para cosas distintas. Si el teclado y la entrada de palabras suenan
  parecido, el espectador no sabe qué pasa. Lo que funcionó:

| Evento | Sonido | Nivel relativo |
|---|---|---|
| Tecla | chasquido amortiguado + golpe grave (170–255 Hz), 6 variantes alternas, máx. 1 cada 2 fot. | 0,4–0,6 |
| Palabra que entra | golpe sordo grave (70 Hz con caída desde 120 Hz), 6 variantes | 0,55 |
| Clic de cursor | clic seco con liberación | 0,7 |
| Aparición de tarjeta | «pop» suave (250→360 Hz) | 0,35–0,5 |
| Barrido / transición | ruido filtrado en barrido, **paso bajo a 3 kHz** | 0,25–0,55 |
| Golpe de marca | sub grave + cola corta | 0,35–0,65 |
| Logro / confirmación | campana suave a dos notas | 0,4 |
| Denegado | dos notas descendentes graves | 0,5 |

- Todo con paso bajo: por encima de ~3–4 kHz los barridos suenan a «slide» estridente.
- Variantes y una tabla de ganancia por familia (`GAIN`) + un `MASTER`, así se reequilibra todo
  sin tocar cada llamada.
- Notas afinadas (piano, campanas melódicas) para las palabras: se cansan pronto y compiten con la
  música. Mejor percusivo y grave.
- `python3 scripts/sfx.py public/sfx` sintetiza una biblioteca original (sin muestras de terceros)
  con los nombres que espera `templates/Sfx.tsx`. La semilla es fija: si añades un sonido, hazlo
  al final para no alterar el ruido de los demás.

## Música

- Tempo entero en fotogramas (motion.md) y secciones de la música en tiempos, alineadas con los
  capítulos: intro corta, entrada al primer gran momento, caída o hueco antes del cierre.
- Que acompañe: 8–12 dB por debajo de los efectos. Ducking suave (×0,65) en los tramos donde se
  teclea o se lee, con rampas de 8–12 fotogramas.
- Estilo: pide al usuario el carácter (enérgica, cálida, cinematográfica) y ofrécele 2–3 opciones
  de 20 s para escuchar antes de montar nada encima. Si suena a «tutorial de YouTube» (pads
  genéricos, arpegio brillante, bombo en cada tiempo sin variación), cambia de enfoque, no de
  volumen.
- Si cambia la duración, regenera la música con la nueva longitud y las secciones desplazadas,
  no la recortes.

## Masterizado

`scripts/master.py <render.mp4> <salida.mp4>`:

1. Extrae la mezcla de Remotion en coma flotante.
2. Ganancia lineal hasta −14 LUFS integrados y limitador a −1 dBTP con sobremuestreo ×4.
3. Remux con el vídeo copiado y AAC 192 k, `+faststart`.
4. Mide el pico verdadero **sobre el AAC final** (el codificador añade sobreoscilación) y repite
   con más margen si se pasa.

Objetivo: −14 LUFS ±0,5, pico ≤ −1 dBTP, rango de sonoridad 4–8 LU.

## Revisión de audio

- Escuchar clips cortos aislados de cada familia sobre la música (el usuario elige mejor así que
  sobre el vídeo entero). Para comparar opciones, genera un mp3 por opción con la misma frase.
- Sonoridad a corto plazo por segundo (`ebur128`): ningún segundo debe saltar más de ~4 LU sobre
  sus vecinos salvo un golpe intencionado.
