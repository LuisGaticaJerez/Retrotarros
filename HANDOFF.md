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
3b. **Arcos nuevos PS2, Xbox y Wii (2026-10-22):** Luis quiere partir cada una por su Top Mundial, un ranking por sesión. PS2 Top Mundial (`ps2-top-mundial`, GTA III #1) y **Xbox Top Mundial (`xbox-top-mundial`, Halo #1)** armados, sin push ni sync. Falta Wii Top Mundial. Confirmar con Luis los desempates de PS2 (`docs/discusiones/discusion-ps2-top-mundial.md`) y, en Xbox, si Prince of Persia y Soulcalibur II (salieron el mismo mes en PS2, Xbox y GameCube y ya están en GameCube Infravalorados) se quedan o suben Jade Empire y Riddick (`docs/discusiones/discusion-xbox-top-mundial.md`).
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

## Cuándo cambiar de sesión (criterio de Luis, 2026-10-22)

Medimos el contexto con `get_usage` (la herramienta de uso de sesión) al cerrar cada ranking, y Claude lo reporta:
- **Menos de 300.000 tokens:** seguimos con el siguiente ranking en la misma sesión.
- **Entre 300.000 y 400.000:** se termina el ranking en curso y se cierra; no se parte uno nuevo.
- **Más de 400.000:** se cambia de sesión, pero solo después de cerrar (commit, push y syncs con el dale de Luis, y este archivo al día).
- **Nunca a mitad de un ranking.** Excepción: si el límite de 5 horas del plan pasa de 85 %, se avisa y se cierra lo que esté en curso.

## Ritual de cierre y nombre de las sesiones (Luis 2026-10-22)

- Al terminar un ranking se corre el comando **`/cierre`** (`.claude/skills/cierre/SKILL.md`): mide el contexto, deja este archivo, la bitácora, el arco y la memoria al día, hace el commit local y ofrece push y syncs (solo con el dale de Luis).
- Claude crea las sesiones nuevas él mismo y les pone el nombre **`Canal Retrotarros · AAAA-MM-DD · <tarea>`** (ej. `Canal Retrotarros · 2026-10-22 · Xbox Top Mundial`). Las sesiones viejas se borran solo con la revisión y el visto bueno de Luis, y cuando no tengan cambios sin commitear ni ramas sin mergear.

## Cómo arrancar la próxima sesión

1. Leer este archivo, `CLAUDE.md` y `docs/modus-operandi/flujo-rankings.md`.
2. Si vas a un episodio, leer su `docs/pautas/pauta-{slug}.md` y `docs/discusiones/discusion-{slug}.md`.
3. Antes de generar contenido nuevo, confirmar con Luis qué se ataca. Trabajar de a un ranking por sesión (las sesiones largas se vuelven lentas).

*Última actualización: 2026-10-22 (PS2 y Xbox Top Mundial armados; Wii Top Mundial pendiente)*
