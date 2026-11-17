# Retiro de lo publicado del estudio

Guía para decidir qué se retira del estudio cuando un video ya se publicó. Se consulta cada vez que se revisa el inventario (lunes, miércoles y viernes, con `docs/canal/inventario-contenido.md`) y la rutina sugiere el retiro; **nada se borra sin el dale de Luis**.

Regla base: Luis 2026-10-09. Lo publicado deja de ocupar el estudio y el Drive. Un video **programado** ya está grabado y no se toca nunca (ni retira ni edita).

## Qué se retira por cada video publicado

Por cada elemento publicado, en el repo y en el Drive (`G:\Mi unidad\Studio\`):

1. El **HTML** del estudio y sus **capturas** (`captures/<slug>/`).
2. Las **imágenes** propias del elemento (`img/<slug>/`, cajas, fotos de hardware).
3. El **kit de YouTube** (`docs/descripciones/descripcion-<slug>.md`).
4. La **discusión** (`docs/discusiones/discusion-<slug>.md`), si existe.
5. La **pauta** (`docs/pautas/`, `studio/pautas/<slug>.tarrobot.json`) y los **shorts derivados** (HTML, audio, MP4).
6. Su carpeta en el Drive, los `.docx` de pauta y discusión de `Studio\Pautas\` y las copias en `Studio\Tarrobot\`.

**Se conserva siempre:** el historial de git (se puede recuperar). Las pautas y los shorts derivados se conservaban hasta el 2026-11-17; desde ese día Luis pidió retirarlos también, así que en un retiro nuevo se borran junto con lo demás (pauta, `.tarrobot.json`, HTML, guion y MP4 del short, y sus copias en el Drive y en `Tarrobot\`), salvo que diga otra cosa.

## Excepciones: lo que NO se retira

| Qué | Hasta cuándo | Por qué |
|---|---|---|
| **Rankings a reforjar** (Luis 2026-11-17): los grabados con baja calidad de audio y video, que son los publicados **antes del PS Vita Top Mundial (17 ago)**, más ese mismo. Son 7: N64 Top Mundial y Top Precios, SNES Top Mundial y Top Precios, NES Top Mundial y Top Precios y PS Vita Top Mundial | Hasta terminar su reforge | Calidad antigua; necesita los archivos a mano |
| **Reforges de colecciones NES, N64 y SNES** (`data/colecciones/*.json`, `studio/colecciones/`) | Hasta que se graben y publiquen | Armados el 2026-11-10 con gráfica nueva, sin grabar |
| **Cualquier programado o grabado sin publicar** | Hasta que salga en YouTube | Ya está filmado: el archivo debe coincidir con el video |

Los demás rankings publicados (Master System Top Mundial y Top Precios, Mega Drive Top Mundial, Atari 2600, Game Boy, GameCube, PS1 Top Mundial, N64 Top Peores, SNES Top Peores, PS1 Top Peores, SNES Joyas ocultas) no se reforjan (Luis 2026-11-17, incluye Master System y Mega Drive): **sí se retiran** como cualquier otro publicado, con el dale de Luis.

## Cómo se aplica en la revisión del inventario

1. Correr `python scripts/youtube_estado.py` y actualizar el inventario.
2. Listar los publicados que siguen en `studio/` o `docs/descripciones/`, **menos** los de la tabla de excepciones.
3. Mostrarle a Luis la lista con el nombre exacto de cada uno y preguntar si los retira.
4. Con su dale: borrar HTML, capturas, imágenes, kit y discusión (repo y Drive), commitear y anotar el retiro en el registro de abajo y en la sección 1.1 del inventario.

## Pendientes de retiro (al 2026-11-17)

Ninguno. Lo publicado que no entra al reforge se retiró el 2026-11-17.

## Registro de retiros hechos

| Fecha | Qué se retiró |
|---|---|
| 2026-10-09 | Las 24 reseñas publicadas hasta ese día (HTML, carpetas del Drive y kits) |
| 2026-10-19 | Reseñas Metal Warriors y Melee; Specials Día del Padre y Mes del Mar (se conservan pautas, discusiones y shorts) |
| 2026-10-21 | Reseña Mighty Morphin Power Rangers, las 4 colecciones (N64, NES, SNES, PS Vita) y la saga Zelda |
| 2026-10-26 | Reseña Montezuma's Revenge |
| 2026-11-17 | Reseñas Yoshi's Island, Ocarina of Time, Need for Speed Underground 2 y Contra; rankings Master System (Top Mundial y Top Precios), Mega Drive Top Mundial, Atari 2600 (Top Mundial, Top Precios y Top Peores), Game Boy (Top Mundial, Top Precios y Top Peores), GameCube Top Mundial, PS1 (Top Mundial y Top Peores), N64 Top Peores, SNES Top Peores y SNES Joyas ocultas. Esta vez se borró **todo**: HTML, capturas, imágenes, kit, discusión, **pauta** y `.tarrobot.json`, el short de Master System Top Precios, y las carpetas y `.docx` del Drive. Solo queda el historial de git |

Cada retiro nuevo suma una fila aquí.
