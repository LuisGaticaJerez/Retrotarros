# Retiro de lo publicado del estudio

Guía para decidir qué se retira del estudio cuando un video ya se publicó. Se consulta cada vez que se revisa el inventario (lunes, miércoles y viernes, con `docs/canal/inventario-contenido.md`) y la rutina sugiere el retiro; **nada se borra sin el dale de Luis**.

Regla base: Luis 2026-10-09. Lo publicado deja de ocupar el estudio y el Drive. Un video **programado** ya está grabado y no se toca nunca (ni retira ni edita).

## Qué se retira por cada video publicado

Por cada elemento publicado, en el repo y en el Drive (`G:\Mi unidad\Studio\`):

1. El **HTML** del estudio y sus **capturas** (`captures/<slug>/`).
2. Las **imágenes** propias del elemento (`img/<slug>/`, cajas, fotos de hardware).
3. El **kit de YouTube** (`docs/descripciones/descripcion-<slug>.md`).
4. La **discusión** (`docs/discusiones/discusion-<slug>.md`), si existe.
5. Su carpeta en el Drive y los `.docx` de pauta y discusión de `Studio\pautas\`.

**Se conservan siempre:** la pauta (`docs/pautas/pauta-<slug>.md`), los shorts derivados (HTML, guion, MP4) y todo lo que queda en el historial de git (se puede recuperar).

## Excepciones: lo que NO se retira

| Qué | Hasta cuándo | Por qué |
|---|---|---|
| **Rankings a reforjar** (Luis 2026-11-17): los grabados con baja calidad de audio y video, que son los publicados **antes del PS Vita Top Mundial (17 ago)**, más ese mismo. Candidatos: N64 Top Mundial y Top Precios, SNES Top Mundial y Top Precios, NES Top Mundial y Top Precios, PS Vita Top Mundial, y por confirmar Master System Top Mundial y Top Precios y Mega Drive Top Mundial | Hasta terminar su reforge | Calidad antigua; necesita los archivos a mano |
| **Reforges de colecciones NES, N64 y SNES** (`data/colecciones/*.json`, `studio/colecciones/`) | Hasta que se graben y publiquen | Armados el 2026-11-10 con gráfica nueva, sin grabar |
| **Cualquier programado o grabado sin publicar** | Hasta que salga en YouTube | Ya está filmado: el archivo debe coincidir con el video |

Los rankings publicados **después** del PS Vita Top Mundial (Atari 2600, Game Boy, GameCube, PS1 Top Mundial, N64 Top Peores, SNES Top Peores, PS1 Top Peores, SNES Joyas ocultas) no se reforjan, así que **sí se retiran** como cualquier otro publicado, con el dale de Luis. Falta confirmar si Master System y Mega Drive (publicados antes del PS Vita) entran al reforge.

## Cómo se aplica en la revisión del inventario

1. Correr `python scripts/youtube_estado.py` y actualizar el inventario.
2. Listar los publicados que siguen en `studio/` o `docs/descripciones/`, **menos** los de la tabla de excepciones.
3. Mostrarle a Luis la lista con el nombre exacto de cada uno y preguntar si los retira.
4. Con su dale: borrar HTML, capturas, imágenes, kit y discusión (repo y Drive), commitear y anotar el retiro en el registro de abajo y en la sección 1.1 del inventario.

## Pendientes de retiro (al 2026-11-17)

Reseñas ya publicadas que siguen en el estudio, esperando el dale de Luis:

- `resena-yoshis-island`
- `resena-ocarina-of-time-pedido`
- `resena-need-for-speed-underground-2`
- `resena-contra`

## Registro de retiros hechos

| Fecha | Qué se retiró |
|---|---|
| 2026-10-09 | Las 24 reseñas publicadas hasta ese día (HTML, carpetas del Drive y kits) |
| 2026-10-19 | Reseñas Metal Warriors y Melee; Specials Día del Padre y Mes del Mar (se conservan pautas, discusiones y shorts) |
| 2026-10-21 | Reseña Mighty Morphin Power Rangers, las 4 colecciones (N64, NES, SNES, PS Vita) y la saga Zelda |
| 2026-10-26 | Reseña Montezuma's Revenge |

Cada retiro nuevo suma una fila aquí.
