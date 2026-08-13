# Inventario de contenido — Retrotarros

> Qué tipos de video hace el canal y qué assets tenemos para cada uno. A diferencia de
> `docs/canal/formatos.md` (estructura de producción: bloques, tiempos) y `docs/canal/estrategia.md`
> (documento maestro), este doc está **grounded en las playlists reales de YouTube**
> (`@Retrotarros`), no solo en lo que hay armado en el repo — la vez pasada armamos una
> lista solo desde `studio/` y salió incompleta (faltó "Abriendo el tarro" completo, y no
> reflejaba cuánto está realmente publicado vs. solo armado). Revisar el canal antes de
> asumir que este doc sigue vigente — se desactualiza rápido.
>
> **Última verificación contra YouTube: 2026-07-21.** Canal: 603 suscriptores, 41 videos.

## Cómo leer esto

- **Publicado** = está subido a YouTube, en una playlist real.
- **Armado** = HTML + pauta listos en el repo (`studio/`, `docs/pautas/pauta-*.md`), no subido todavía.
- **Pendiente** = solo formato/idea definida, sin asset armado.

---

## 1. Episodios largos

### Rankings — playlist activa, 9 episodios publicados

Top Mundial (crítica) + Top Precios (mercado) por consola. Es la playlist que más se
actualiza y el formato ancla del canal.

| Consola | Top Mundial | Top Precios |
|---|---|---|
| Master System | ✓ Publicado | ✓ Publicado |
| Mega Drive | ✓ Publicado | Armado, sin subir |
| NES | ✓ Publicado | ✓ Publicado |
| SNES | ✓ Publicado | ✓ Publicado |
| N64 | ✓ Publicado (EP03) | ✓ Publicado (EP04) |
| Dreamcast | Armado, sin subir | Armado, sin subir |
| Saturn | Armado, sin subir | Armado, sin subir |
| PS Vita | Armado, sin subir | Armado, sin subir |

**Backlog: 7 episodios armados esperando subir** (Mega Drive precios, Dreamcast x2, Saturn x2, PS Vita x2).

### Colecciones RetroTarros — playlist, 4 videos, **al día**

PS Vita, NES, N64, SNES. Los 4 armados en el repo (`studio/*-coleccion.html`) están
publicados — sin backlog acá.

### Sagas de videojuegos — playlist, 1 video publicado, **11 armadas sin subir**

Solo Zelda está arriba. Armadas y listas: Donkey Kong, Kirby, Mario, Mega Man, Metal
Gear, Metroid, Mortal Kombat, Resident Evil, Smash Bros, Sonic, Street Fighter (11).
Generador: `scripts/saga_deck.py`. **Es el mayor backlog de publicación del canal.**

### Specials — playlist, 2 videos publicados, 2 armados sin subir

Publicados: Día del Padre (`retro-padres-gamer`), Glorias Navales (`retro-glorias-navales`).
Armados sin subir: Cuadrilla del Frío (`retro-cuadrilla-frio`), Día del Trabajador
(`retro-dia-trabajador`). Multi-consola, top 10 temático atado a fecha chilena.

### Abriendo el tarro — playlist activa, se actualiza seguido

Entrevista a un **coleccionista invitado** (no Luis/Koko) mostrando su colección propia
— puede ser de lo que sea, no solo videojuegos ("Los tesoros numismáticos de Arturo").
No sigue el molde de pauta operativa de los otros formatos porque depende de lo que
traiga el invitado. Assets:
- `docs/abriendo-el-tarro/kit-coleccionista-abriendo-el-tarro.md` — kit que se manda al invitado (qué esperar, preguntas guía).
- `docs/abriendo-el-tarro/abriendo-el-tarro-google-form.gs` — formulario de levantamiento de datos del invitado.
- `studio/_template-abriendo-el-tarro.html` — template de monitor de estudio para este formato.

**Este formato no estaba documentado en `CLAUDE.md`** — corregido en este mismo commit.

### G-OLD — playlist archivada, no se alimenta más

"EP01 Colección RetroTarros N64" y "EP02 Ranking Retrotarros vs el mundo N64": versiones
**viejas/superadas** de lo que hoy es el formato Colecciones (el segundo, "Retrotarros vs
el mundo", fue discontinuado del todo el 2026-08-11 — ver nota más abajo).
Se dejaron archivadas como playlist separada en vez de borrarlas. No production activa acá.

### Curaduría N64-only — armados, sin playlist propia todavía

`n64-hardware-raro`, `n64-joyas-ocultas`, `n64-kirkhope-rare` (biográfico compositor),
`n64-nintendo-vs-playstation` (contexto histórico), `n64-no-latam` (regional). 5 episodios
armados y cerrados para grabar (ver `docs/arcos/n64.md`), **ninguno publicado, y no está
decidido en qué playlist van a caer** cuando se suban (¿Specials? ¿playlist nueva por
tipo?). **Pendiente de decidir con Luis.**

### Retrotarros vs Mundo / Archivo Koko — DISCONTINUADOS (2026-08-11)

Ambos formatos fueron eliminados del canal por decisión de Luis: `n64-retrotarros-vs-mundo`,
`psvita-retrotarros-vs-mundo`, `n64-archivo-koko`, `psvita-archivo-koko`. Todo su contenido
(pautas, discusiones, descripciones, HTML, imágenes, capturas) se borró del repo y del
Drive. **No se vuelven a producir** — ver regla en `CLAUDE.md`.

### Indie Lat — solo formato, sin ningún asset

Entrevistas a devs indie latinoamericanos. Descrito en `docs/canal/formatos.md` y
`docs/canal/estrategia.md`, **cero episodios armados o grabados**.

### Musical / OST en batería — solo formato, sin asset

Koko interpreta el tema icónico de una generación en batería. Sembrado como idea
(`n64-ost-bateria` en `docs/arcos/n64.md`), sin pauta ni HTML armados.

### Reseñas — playlist NUEVA (pendiente crear en YouTube), 5 armadas

Un juego por video, ángulo retrospectivo ("¿envejeció bien?"), máximo 10 min, talento
alterna Luis/Koko 1 y 1, nunca cierra con batería. Diseño completo en
`docs/superpowers/specs/2026-07-21-resena-format-design.md`. Generador:
`scripts/resena_deck.py`. Salida en `studio/resenas/<slug>.html` (carpeta aparte, no la
raíz plana de `studio/` como el resto de formatos).

**Primera tanda armada (0 publicadas):** Super Mario Bros. 3 (NES), Sonic the Hedgehog 2
(Mega Drive), Killer Instinct Gold (N64), Mortal Kombat (SNES), Donkey Kong Country
(SNES). **Pendiente:** crear la playlist "Reseñas" en YouTube Studio (no se puede crear
por API/Claude).

---

## 2. Shorts (9:16)

> Corrección 2026-07-21: el primer barrido de la pestaña Shorts del canal quedó cortado
> por límites de scroll del navegador automatizado (solo cargó 5 de 22). Los números de
> abajo salen de leer `ytInitialData` (`shortsLockupViewModel`) directo del JSON interno
> de la página, que sí trae el listado completo. Si se vuelve a auditar esto, no confiar
> en un scroll simple — extraer del JSON embebido.

### TarroShorts (pipeline HTML + render automático)

Narrados por TarroBot (voz edge-tts), armados con `scripts/tarroshort_render.py` +
generadores (`tarroshort_datos.py`, o a mano siguiendo el molde `item-tag` — ver
`docs/modus-operandi/convenciones-tarroshorts.md`).

| Sub-tipo | Armados | Publicados | Backlog |
|---|---:|---:|---:|
| Derivados de episodio (top-mundial/precios/colección + cross-console) | 17 | 11 | 6 |
| De DATOS (tema curioso libre, lane TarroBot) | 15 | 6 | 9 |
| **TOTAL TarroShort** | **32** | **17** | **15** |

**Publicados (17):** `mas-caros-historia`, `mejor-consola-retro`, `retro-glorias-navales`,
`retro-padres-gamer`, `n64-coleccion`, `n64-top-mundial`, `n64-top-precios`,
`snes-coleccion`, `snes-top-mundial`, `snes-top-precios`, `nes-top-mundial`,
`datos-sonic`, `datos-tetris`, `datos-juegos-peliculas`, `datos-ports-rotos`,
`datos-clones-mario`, `datos-zelda-feos`.

**Backlog (15):** `dreamcast-top-precios`, `master-system-top-precios`,
`mega-drive-top-precios`, `saturn-top-precios`, `nes-coleccion`, `nes-top-precios`,
`datos-cartuchos-caros`, `datos-easter-egg`, `datos-finales-raros`, `datos-game-boy`,
`datos-jefes-dificiles`, `datos-mario-secretos`, `datos-mortal-kombat`, `datos-pacman`,
`datos-secretos-escondidos`.

### Shorts simples de B-roll / trivia (sin pipeline TarroBot)

5 publicados: "Generaciones Nintendo en sus controles", "controles N64", "Pequeña
colección de consolas de Nintendo 64", "La mujer que inventó los videojuegos", "El primer
juego de plantas". Edición directa en CapCut (los de controles/colección sobre clips de
`scripts/extract-broll.ps1`; los dos de trivia histórica parecen lane Luis grabado
directo). Sin HTML ni narración generada — no tienen contraparte en `studio/`.

### Lane Luis / Lane Koko (guionados, sin HTML)

Curiosidades históricas (Luis solo) y batería/performance (Koko solo). Documentados en
`docs/canal/guiones-shorts.md` con guion, timings, B-roll y datos de respaldo — formato
definido, pendiente confirmar cuántos de los shorts ya publicados corresponden a este
molde vs. al de B-roll simple de arriba.

### TarroTeaser (no es contenido final, es insumo de edición)

`scripts/tarroteaser.py` corta automáticamente un teaser crudo del video master de un
episodio (Whisper local + ffmpeg) para que Luis lo edite en CapCut. No se publica tal
cual — alimenta el proceso de armar el short/trailer final.

---

## 3. La brecha principal: se produce más rápido de lo que se publica

- **Sagas:** 12 armadas, 1 publicada (11 de backlog) — **la brecha más grande del canal**.
- **Rankings:** 16 armados, 9 publicados (7 de backlog).
- **TarroShorts:** 32 armados, 17 publicados (15 de backlog) — más sano de lo que parecía a primera vista.
- **Episodios sin playlist asignada** (curaduría N64): 5 armados, 0 publicados.
- **Reseñas** (playlist nueva, aún no creada en YouTube): 5 armadas, 0 publicadas.

**Colecciones es la única categoría al día** (4 armadas = 4 publicadas).

## 4. Pendiente de decidir con Luis

1. Playlist de destino para la curaduría N64-only (hardware-raro, joyas-ocultas,
   kirkhope-rare, nintendo-vs-playstation, no-latam) — hoy no tiene casa en el menú de
   playlists del canal.
2. Ritmo de publicación del backlog de Sagas y TarroShorts — ¿calendario fijo o se suben
   a medida que se van necesitando para el algoritmo?
3. Si los shorts de B-roll simple (sin TarroBot) siguen siendo un formato válido aparte,
   o fueron pruebas tempranas que ya no se repiten.

---

*Fuente: playlists reales de `youtube.com/@retrotarros` (revisadas en vivo) cruzadas con
`studio/`, `docs/pautas/pauta-*.md` y `docs/arcos/`. Actualizar este doc cuando cambie
significativamente lo publicado — no es una foto que se pueda dar por vigente para
siempre.*
