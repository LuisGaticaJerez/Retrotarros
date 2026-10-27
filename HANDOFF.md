# Retrotarros — Handoff Doc

> Estado de sesión a sesión. **Leer ANTES de cualquier acción**, después `CLAUDE.md`, `docs/modus-operandi/flujo-rankings.md` (recetas y trampas) y los docs del escenario.

## Estado actual (2026-10-21)

**Hecho en la última tanda (todo pusheado salvo lo indicado):**
- Top Precios rehechos con el listado completo de PriceCharting: Dreamcast, Saturn, GameCube, Mega Drive, PS Vita y **SNES** (el SNES ya estaba publicado el 2026-06-01; Luis lo va a regrabar). PS1 se corrigió el 2026-10-09.
- Formato nuevo **Infravalorados** (ranking de calidad, sin precios): `snes-infravalorados` (Tetris Attack #1) y `ps1-infravalorados` (Wipeout XL #1). Regla de Luis: la crítica pesa más que el olvido. Categoría `studio/rankings/infravalorados/`.
- Syncs a Drive incrementales: `sync-to-drive.ps1 -Episodios <slug>,<slug>` (~6 s) y `sync-tarrobot-to-drive.ps1 -Rapido` (~2 s). El barrido completo tarda ~10 min.
- `scripts/wiki_reception.py` (notas MC/GR desde Wikipedia) y `docs/modus-operandi/flujo-rankings.md` (recetas). **Estos dos archivos y los cambios de scripts de sync están commiteados en local, sin push (pedir el dale de Luis).**
- **TarroDL se separó del repo del canal (2026-10-22):** vive en `D:\Recursos Retrotarros\TarroTools\TarroDL` (repo privado `github.com/LuisGaticaJerez/TarroDL`, 19 commits de historia conservados). Se publica en Drive con su `publicar-en-drive.ps1`. Luis quiere que `D:\Recursos Retrotarros\TarroTools\` agrupe las herramientas que se vayan separando (primero TarroDL; el resto, cuando él lo indique). Tiene la pestaña TarroMosaico (2 a 12 videos).

**Pendientes:**
1. Push de lo local + `sync-to-drive.ps1` y `sync-tarrobot-to-drive.ps1` (modo incremental o completo).
2. Auditar con la receta de `flujo-rankings.md` los Top Precios publicados sin revisar: NES, N64, Master System, Atari 2600, Game Boy. PS1: Einhänder y Castlevania Chronicles vs el #10 (USD 350).
3. Más Infravalorados (Mega Drive y GameCube hechos y sincronizados el 2026-10-22; sugerido: PS2; N64 ya tiene `n64-joyas-ocultas`).
3b. **Arcos nuevos PS2, Xbox y Wii (2026-10-22):** Luis quiere partir cada una por su Top Mundial, un ranking por sesión. PS2 Top Mundial (`ps2-top-mundial`, GTA III #1) y **Xbox Top Mundial (`xbox-top-mundial`, Halo #1)** armados, sin push ni sync. Falta Wii Top Mundial. Confirmar con Luis los desempates de PS2 (`docs/discusiones/discusion-ps2-top-mundial.md`) El Xbox Top Mundial quedó aprobado por Luis tal cual (Prince of Persia y Soulcalibur II se quedan, aunque también están en GameCube Infravalorados); ya está en GitHub y en Drive.
3c. **SNES Top Peores, ajustes de Luis (2026-10-22):** (a) cartucho más grande y texto de abajo más corto: hecho y commiteado local (`ca5d506`), sin push ni sync (capturas nuevas solo en el worktree; falta `sync-to-drive.ps1 -Episodios snes-top-peores` con su dale). (b) **Notas ocultas de 3 minutos por juego (regla de Luis, 2026-10-22; 450 a 550 palabras por slide; humor al juego, cada dato cruzado con 2 fuentes, lo no confirmado como "por confirmar"):** **SNES Top Peores NO se toca: Luis lo confirmó como grabado (2026-10-22) y sus notas quedan en 140 a 275 palabras.** **NES Top Peores: hecho 2026-10-22** (notas de 515 a 800 palabras por juego, panel con scroll; texto en `.cache/notas_nes.py` + gancho en `.cache/gen_nes_top_peores.py`; pendiente decidir con Luis si Ghostbusters pasa a 3 listas porque Den of Geek lo tiene #6, y por qué Heroes of the Lance, Color a Dinosaur y Bullwinkle, de la lista de Nintendo Power 100, no están en el top). **Atari 2600 Top Peores: hecho 2026-10-22** (notas de 400 a 640 palabras; `.cache/notas_atari.py`; ojo: su pauta es una hoja de datos, se le agrego una seccion de ampliacion con los hallazgos, p. ej. Star Fox es #7 en el articulo original de Digital Press aunque Wikipedia diga 19, y Spider Droid es el mismo Amidar). **Mega Drive Top Peores: hecho 2026-10-22** (notas de 480 a 590 palabras; `.cache/notas_md.py`; por confirmar: quien publico el port de Rise of the Robots en Mega Drive, el dato de Robin Williams en Awesome Possum y las copias destruidas de Fantasia). **PS1 Top Peores: hecho 2026-10-22** (notas de 520 a 570 palabras; `.cache/notas_ps1.py`; por confirmar: fecha de Hellboy: Asylum Seeker, 2003 o 2004, y de Santa Claus Saves the Earth, 2002 o 2004). **Game Boy Top Peores: hecho 2026-10-22** (notas de 470 a 550 palabras; `.cache/notas_gameboy.py`; ojo: Den of Geek dice que la pelicula Tasmania Story no fue popular, pero Wikipedia dice que fue la segunda mas taquillera de Japon en 1990). **Siguen, en este orden, los Top Peores sin grabar ni publicar:** Dreamcast, Saturn y GameCube (N64 ya está publicado: no se toca). Después, los Top Mundial/Precios/Infravalorados sin publicar, verificando cada uno en `data/youtube/estado-canal.json`. Método: copiar el driver y `peores_*.py` a `.cache/` del worktree, escribir un `notas_<consola>.py` con `NOTAS = {pos: ([lineas], cue)}` y pegarlo en el driver antes de `DATA = {` (ver el del NES), correr el driver (regenera HTML y pauta), `capture-slides.py` y commit local. Fuentes que sirven: Wikipedia por juego (API `extracts`), Den of Geek (listas de peores por consola), Interesting Engineering y la lista de Nintendo Power 100 (DeviantArt/NintendoWiki).
3d. **Cajas grandes en los rankings (2026-10-23, en master y en Drive):** `top_deck.py` tiene los layouts `alta`, `ancha` y `clasica` (`box_layout` en el `DATA`); `scripts/aplicar_layout_cajas.py <slug> --aplicar` parchea decks ya generados. Aplicado a 30 rankings: los 6 del rango de reforge (publicados del 19 mayo al 28 junio 2026, sin specials: N64, SNES y NES, Mundial y Precios) y 24 sin grabar. Siguen en `clasica`, a propósito, los publicados desde el 29 de junio y el SNES Top Peores (grabado). **Pendiente:** reforge de contenido de los 6 del rango (un ranking por sesión); decidir si colecciones (SNES, N64, NES) y saga Zelda del mismo rango se reforjan (usan `coleccion_deck.py` y `saga_deck.py`, otra ficha de caja); bajar en mayor resolución las cajas chicas (Atari 8-bit Top Precios, 7 de 12). **Criterio de sesión duplicado:** seguir bajo 600.000 tokens, cerrar entre 600.000 y 800.000.
3e. **Reseñas nuevas God of War (PS2) y Halo: Combat Evolved (Xbox), 2026-10-27:** pedidas por Luis para saltar a los arcos PS2 y Xbox. HTML, caja NTSC, capturas locales y kits con tags hechos (`docs/descripciones/descripcion-resena-god-of-war.md` y `...halo-combat-evolved.md`); veredictos JUEGAZO e IMPRESCINDIBLE; ninguna esta en la coleccion. Datos con una sola fuente (marcados 'por confirmar' en las notas): Metacritic 94 de God of War PS2 (no se pudo abrir Metacritic), nombre de trabajo 'Dark Odyssey', fechas de UK y Japon, remake 2026. Drivers en `.cache/gen_resena_god-of-war.py` y `gen_resena_halo-combat-evolved.py`. Falta push y syncs a Drive (con el dale de Luis).
4. Confirmar con Luis: Wipeout XL como #1 y Xenogears #10 (PS1); Tetris Attack #1 (SNES); Shining Force II como #1 en Mega Drive (alternativa: Phantasy Star II); GameCube: Viewtiful Joe #1 (empata 93 con Soulcalibur II) y si dejan juegos conocidos (Soulcalibur II, Prince of Persia, RE remake, Tony Hawk's 4) o prefieren reservas más olvidadas.
5. Mediciones de la campaña de Google Ads: 29 Oct y 11 Nov; después revocar el acceso a la API (`python scripts/youtube_aplicar.py --olvidar` + myaccount.google.com/permissions). Tarea de inventario programada lun/mié/vie 09:30.
6. Kits de YouTube de rankings sin estrenar que aún tengan hashtags viejos (guía: `docs/canal/guia-youtube-viral.md` sección 4).

**No tocar (grabado o programado):** ver `docs/canal/inventario-contenido.md` y la memoria `project_grabados_sin_publicar` (SNES Top Peores, Montezuma, entre otros). Los rankings publicados no se retiran hasta hacer su reforge.

## Decidido y cerrado (vigente)

- **Top Mundial por consola (Luis 2026-10-22):** una entrada por franquicia, sin deportes anuales, y un juego solo va en el Top Mundial de la consola donde salió primero (no se repite entre consolas; RE4 queda en GameCube). Lo que queda fuera por legado va a Infravalorados. Sin bonus track.
- Canal **Retrotarros**, tagline `Nostalgia + Juegos + Música`. Presentadores Luis y **Coco**; la colección es del canal.
- Pautas: tres archivos por episodio (`pauta` + `discusion` + `html`). Top Precios en 3 bloques. Calendario de publicación: martes, jueves y domingo 20:30 (Chile).
- Git: Claude commitea; push y syncs solo con el "dale" de Luis. Sin `Co-Authored-By`.
- Estilo de TarroShorts: `docs/modus-operandi/convenciones-tarroshorts.md`.

## Cuándo cambiar de sesión (criterio de Luis, 2026-10-22; duplicado el mismo día)

Medimos el contexto con `get_usage` (la herramienta de uso de sesión) al cerrar cada ranking, y Claude lo reporta:
- **Menos de 600.000 tokens:** seguimos con el siguiente ranking en la misma sesión.
- **Entre 600.000 y 800.000:** se termina el ranking en curso y se cierra; no se parte uno nuevo.
- **Más de 800.000:** se cambia de sesión, pero solo después de cerrar (commit, push y syncs con el dale de Luis, y este archivo al día).
- **Nunca a mitad de un ranking.** Excepción: si el límite de 5 horas del plan pasa de 85 %, se avisa y se cierra lo que esté en curso.

## Ritual de cierre y nombre de las sesiones (Luis 2026-10-22)

- Al terminar un ranking se corre el comando **`/cierre`** (`.claude/skills/cierre/SKILL.md`): mide el contexto, deja este archivo, la bitácora, el arco y la memoria al día, hace el commit local y ofrece push y syncs (solo con el dale de Luis).
- Claude crea las sesiones nuevas él mismo y les pone el nombre **`Canal Retrotarros · AAAA-MM-DD · <tarea>`** (ej. `Canal Retrotarros · 2026-10-22 · Xbox Top Mundial`). Las sesiones viejas se borran solo con la revisión y el visto bueno de Luis, y cuando no tengan cambios sin commitear ni ramas sin mergear.

## Cómo arrancar la próxima sesión

1. Leer este archivo, `CLAUDE.md` y `docs/modus-operandi/flujo-rankings.md`.
2. Si vas a un episodio, leer su `docs/pautas/pauta-{slug}.md` y `docs/discusiones/discusion-{slug}.md`.
3. Antes de generar contenido nuevo, confirmar con Luis qué se ataca. Trabajar de a un ranking por sesión (las sesiones largas se vuelven lentas).

*Última actualización: 2026-10-27 (reseñas de God of War y Halo armadas; antes: cajas grandes en 30 rankings y criterio de 600.000 tokens; notas de 3 minutos hechas en NES, Atari 2600, Mega Drive, PS1 y Game Boy Top Peores; SNES no se toca por estar grabado; siguen Dreamcast, Saturn y GameCube. Top Peores que aun no existen, con Top Mundial hecho: Master System, PS2, PS Vita, Xbox y Atari 8-bit)*
