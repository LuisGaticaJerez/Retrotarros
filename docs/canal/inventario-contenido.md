# Inventario de contenido — Retrotarros

> Qué tipos de video hace el canal y qué assets tenemos para cada uno. A diferencia de
> `docs/canal/formatos.md` (estructura de producción: bloques, tiempos) y `docs/canal/estrategia.md`
> (documento maestro), este doc está **grounded en las playlists/pestaña Videos reales de
> YouTube** (`@Retrotarros`), no solo en lo que hay armado en el repo.
>
> **Última verificación contra YouTube: 2026-08-20** (canal, pestaña Videos, extraído del
> JSON interno `ytInitialData` — 1.26 K suscriptores, 55 videos totales incluyendo shorts).
> La sección 1 (capítulos largos) fue reconstruida completa esta fecha. La sección 2
> (shorts) sigue con la última verificación de 2026-07-21 — no se reauditó esta vez.
>
> **Re-verificación puntual de Reseñas: 2026-09-03** (pestaña Videos en vivo, orden "Más
> recientes", 1.41 K suscriptores, 64 videos). Solo se reauditó la categoría Reseñas (fila
> 1.1/1.2/1.3 de abajo) — Rankings/Sagas/Specials/Curaduría/RetroNotas siguen con los datos
> del 2026-08-20 aunque 3 de esos videos (Atari 2600 Top Mundial + Top Precios, PS Vita Top
> Mundial) también se confirmaron publicados de paso; sus conteos de categoría no se
> recalcularon todavía.
>
> **Re-verificación de Reseñas: 2026-10-09** (pestaña Videos en vivo, 2.24 K suscriptores, 80
> videos). Hay 24 reseñas publicadas y 20 en backlog; ese mismo día se sacaron del estudio
> (repo y Drive) las 24 publicadas. De paso se vio publicado el Top Mundial de GameCube; el
> resto de las categorías no se recontó.
>
> **Verificación completa con la API de YouTube: 2026-10-19** (`scripts/youtube_estado.py`,
> 84 publicados + 1 programado). Se recalcularon las filas de Reseñas y Rankings (resumen 1.0).
>
> **Verificación con la API de YouTube: 2026-10-21** (85 publicados + 1 programado). Se publicó
> la reseña de Mighty Morphin Power Rangers (mar 20 oct, 20:30); Montezuma's Revenge pasó a jueves 22 oct. Se
> sumó al conteo el Joyas ocultas de SNES (armado, sin publicar).
>
> **Verificación con la API de YouTube: 2026-10-26** (87 publicados + 0 programados). Desde la
> última vez se publicaron Montezuma's Revenge (jue 22 oct, 20:30) y SNES Top Peores (dom 25
> oct, 20:30). Nada programado: el próximo hueco del calendario (martes 27) está libre.
>
> **Verificación con la API de YouTube: 2026-10-30** (89 publicados + 0 programados). Desde la
> última vez se publicó la reseña de God of War (PS2), el jue 29 oct, 20:30. Nada programado.
>
> **Verificación con la API de YouTube: 2026-11-02** (89 publicados + 1 programado). Sin
> publicaciones nuevas desde el 30 oct. Quedó programado PS1 Top Peores para el dom 8 nov, 20:30
> (Chile); ya está grabado, no tocar su HTML ni sus textos.
>
> **Verificación con la API de YouTube: 2026-11-06** (91 publicados + 2 programados). Desde la
> última vez se publicaron Yoshi's Island (mar 3 nov, 20:30) y The Legend of Zelda: Ocarina of
> Time (pedida, jue 5 nov por la tarde). Quedó programada la reseña de Need for Speed
> Underground 2 (ya grabada, no tocar). PS1 Top Peores sigue programado para el dom 8 nov.
>
> **Verificación con la API de YouTube: 2026-11-17** (95 publicados + 2 programados). Desde la
> última vez se publicaron PS1 Top Peores (dom 8 nov), Need for Speed Underground 2 (mar 10 nov),
> Contra (jue 12 nov) y SNES Joyas ocultas (dom 15 nov, "10 juegos de SNES muy buenos que casi
> nadie recuerda"). Quedaron programados The Witcher (hoy mar 17 nov, 20:30) y Dreamcast Top
> Mundial (dom 22 nov, 20:30); ambos ya grabados, no tocar.
>
> **Verificación con la API de YouTube: 2026-11-18** (96 publicados + 1 programado). Desde la
> última vez se publicó la reseña de The Witcher (2007, pedida, mar 17 nov, 20:30). Queda
> programado solo Dreamcast Top Mundial (dom 22 nov, 20:30), ya grabado, no tocar.
>
> **Verificación con la API de YouTube: 2026-11-20** (97 publicados + 2 programados). Desde la
> última vez se publicó la reseña de Final Fight (jue 19 nov, 20:30). Quedan programados Dreamcast
> Top Mundial (dom 22 nov, 20:30) y la reseña de Diablo (mar 24 nov, 20:30); ambos ya grabados,
> no tocar.

> **Consolidación completa contra el disco: 2026-11-22** (estudio/ y docs/ revisados archivo por archivo,
> más `data/youtube/estado-canal.json` del 2026-11-20). Correcciones: Rankings 42 armados / 21 de backlog
> (faltaban PS2 y Xbox Top Mundial y los 3 Joyas ocultas de GameCube, Mega Drive y PS1); Specials 7
> armados (suman los 2 especiales de juegos de película); RetroNotas 3 (suma Consola pirata LATAM);
> Abriendo el tarro 2 publicados (Arturo y Rodrigo); Reseñas con la lista real de backlog. **Hallazgo
> resuelto el mismo día (con el dale de Luis):** el retiro del 2026-11-17 había borrado por error
> `atari-2600-top-peores` y `gameboy-top-peores` (HTML, pauta, discusión, kit, `.tarrobot.json` e imágenes),
> que **no están publicados en YouTube** (los únicos Top Peores publicados son N64, SNES y PS1). Se
> restauraron desde el historial de git (`e3dbd5e^`), con capturas regeneradas y sync a Drive.

## Cómo leer esto

- **Publicado** = está subido a YouTube ahora mismo (verificado en vivo).
- **Programado** = tiene fecha de estreno fijada en YouTube Studio (fuente: captura de
  pantalla de la pestaña "Contenido → Programado" que Luis compartió 2026-08-20).
- **Armado** = HTML + pauta + descripción listos en el repo, sin fecha asignada todavía —
  es el backlog real, lo que se puede programar en cualquier momento.
- **Sin armar** = solo formato/idea definida, cero asset.

---

## 1. Episodios largos (capítulos)

### 1.0 Resumen

| Categoría | Armados | Publicados | Programados | Backlog sin fecha |
|---|---:|---:|---:|---:|
| Reseñas | 63 | 36 | 1 | 26 |
| Rankings (Top Mundial + Top Precios, Top Peores y Joyas ocultas por consola; los publicados que ya se retiraron siguen contados) | 42 | 20 | 1 | 21 |
| Sagas de videojuegos | 12 | 1 | 0 | 11 |
| Specials | 7 | 2 | 0 | 5 |
| Curaduría N64-only | 5 | 0 | 0 | 5 |
| RetroNotas | 3 | 0 | 0 | 3 |
| Colecciones | 4 | 4 | 0 | 0 |
| **TOTAL** | **136** | **63** | **2** | **71** |

Aparte, fuera de esta tabla: **Abriendo el tarro** (2 publicados: Arturo y Rodrigo; formato dependiente de
invitado, no tiene "backlog" fijo) y **2 episodios G-OLD** archivados (versiones viejas
superadas, playlist muerta, no cuentan como activo). **Colecciones** (4 de 4 publicadas) tiene además 3 reforges
(NES, N64, SNES, con gráfica nueva, armados el 2026-11-10, sin grabar) que no suman a la tabla.

---

### 1.1 Programados (leídos de YouTube con la API, 2026-11-20)

**Calendario de publicación: martes, jueves y domingo a las 20:30 (hora de Chile).** Se actualiza solo los lunes, miércoles y viernes (el día siguiente) con `scripts/youtube_estado.py` (datos en `data/youtube/estado-canal.json`). **Un video programado ya está grabado: no tocar su HTML ni sus textos.**

| Publicación (hora de Chile) | Título | Contenido del repo |
|---|---|---|
| Dom 22 nov 2026, 20:30 | Los 10 MEJORES juegos de Sega Dreamcast de la historia (44 min, privado, programado) | `studio/rankings/top-mundial/dreamcast-top-mundial.html`, `docs/descripciones/descripcion-dreamcast-top-mundial.md` |
| Mar 24 nov 2026, 20:30 | Diablo (1996): ¿sigue dando miedo bajar un nivel más? \| RetroReseñas (31 min, privado, programado) | `studio/resenas/resena-diablo.html`, `docs/descripciones/descripcion-resena-diablo.md` |

**Grabado y todavía sin fecha de publicación:** nada conocido a 2026-11-20 aparte de los programados (confirmar con Luis si hay algo grabado que no esté en YouTube). La reseña de Mighty Morphin Power Rangers se publicó el 2026-10-20. Todo lo demás del backlog (resto de reseñas y rankings) sigue sin grabar y se puede actualizar.

Tras la publicación, esos HTML y kits se retiran del estudio como el resto de lo ya publicado (regla de 2026-10-09). Qué se retira, qué se exceptúa (rankings y reforges), pendientes y registro: `docs/canal/retiro-publicados.md`.

**Retiro del estudio 2026-11-20:** se retiraron las reseñas The Witcher (pedida) y Final Fight (HTML, capturas, imágenes, kit y carpetas del Drive).

**Retiro del estudio 2026-11-17:** se retiraron 4 reseñas (Yoshi's Island, Ocarina of Time, NFS Underground 2, Contra) y 11 rankings (Master System, Mega Drive Top Mundial, Atari 2600, Game Boy, GameCube Top Mundial, PS1 Top Mundial y Top Peores, N64 Top Peores, SNES Top Peores y Joyas ocultas), con pautas, discusiones, kits, HTML, capturas, imágenes y el short de Master System Top Precios (repo y Drive). Quedan solo los 7 rankings del reforge. Detalle en `docs/canal/retiro-publicados.md`.

**Retiro del estudio 2026-10-26:** se retiró la reseña de Montezuma's Revenge (HTML, capturas, imágenes, kit y carpeta del Drive).

**Retiro del estudio 2026-10-21:** se retiraron la reseña de Mighty Morphin Power Rangers, las 4 Colecciones (N64, NES, SNES, PS Vita) y la saga Zelda, con HTML, capturas, imágenes, kits de YouTube y discusiones (repo y Drive); se conservan las pautas y los shorts. **Los Rankings publicados (Top Mundial, Top Precios, Top Peores) NO se retiran hasta hacer los "reforge" (decisión de Luis 2026-10-21).**

---

### 1.2 Publicados (26 + Abriendo el Tarro + 2 G-OLD, más las Reseñas nuevas de abajo)

**Reseñas (36) — API de YouTube 2026-11-20, del más reciente al más antiguo:** Final Fight (19 nov), The Witcher (pedida, 17 nov), Contra (12 nov), Need for Speed Underground 2 (10 nov), The Legend of Zelda: Ocarina of Time (pedida, 5 nov), Yoshi's Island (3 nov), God of War (PS2, 29 oct), International Superstar Soccer (27 oct),
Montezuma's Revenge (pedida), Mighty Morphin Power Rangers (pedida), Melee (pedida), Metal Warriors (pedida), Worms Armageddon (pedida), Samurai Shodown (pedida), Doom (pedida), King of Fighters '94,
Battletoads, Super Mario World, Street Fighter II, Golden Axe, Metal Gear Solid (pedida),
Chrono Trigger, The Legend of Zelda (pedida), Cadillacs and Dinosaurs (pedida), Jewel Master
(pedida), Top Gear (pedida), Pokémon Rojo/Azul (pedida), Zombies Ate My Neighbors, Super
Metroid (pedida), Mega Man 2, Donkey Kong Country, Kirby's Adventure, Killer Instinct,
Pitfall: The Mayan Adventure (pedida), Mortal Kombat, Super Mario Bros. 3. Sus HTML, carpetas
del Drive y kits de YouTube (`docs/descripciones/`) se retiraron el 2026-10-09 (siguen en el historial de git).
Metal Warriors y Melee se retiraron el 2026-10-19, igual que los 2 Specials publicados (Día del Padre y Mes del Mar: HTML, capturas, imágenes, kit y carpeta del Drive; se conservan sus pautas, discusiones y shorts).

**Rankings (20):** SNES Joyas ocultas (dom 15 nov), PS1 Top Peores (dom 8 nov), Master System Top Mundial + Top Precios, Mega Drive Top Mundial, NES
Top Mundial + Top Precios, SNES Top Mundial + Top Precios, N64 Top Mundial + Top Precios,
PS Vita Top Mundial, Atari 2600 Top Mundial + Top Precios, Game Boy Top Mundial + Top
Precios, GameCube Top Mundial, PS1 Top Mundial (dom 18 oct), N64 Top Peores (dom 11 oct), SNES Top Peores (dom 25 oct).

**Sagas (1):** Zelda.

**Specials (2):** Día del Padre (`retro-padres-gamer`), Mes del Mar / Glorias Navales
(`retro-glorias-navales`).

**Colecciones (4, al día):** N64, SNES, NES, PS Vita. **Reforges NES, N64 y SNES con gráfica nueva armados el 2026-11-10, sin grabar** (`studio/colecciones/<slug>.html`, kit y discusión en `docs/`).

**Abriendo el tarro (2):** Los tesoros numismáticos de Arturo (16 jul) y Rodrigo, el mercader de aventuras (13 sep).

**G-OLD archivado (2, discontinuado, no se repite):** "Coleccion RetroTarros N64" y
"Ranking Retrotarros vs el mundo N64" — versiones viejas de los primeros pasos del canal.

---

### 1.3 Backlog armado — listo para programar, sin fecha (71)

**Reseñas (26) — consolidado 2026-11-22 contra `studio/resenas/` (27 HTML: 26 de backlog + Diablo programada):** Age of Empires II (PC), Aladdin, Altered Beast, Commandos: Behind Enemy Lines (PC), Counter-Strike (PC), Crash Bandicoot, Earthbound, Earthworm Jim, Fatal Fury, Gears of War (Xbox 360), Halo: Combat Evolved (Xbox), JoJo's Bizarre Adventure (pedida), Kingdom Hearts (PS2), Kirby Super Star, A Link to the Past, Sonic the Hedgehog, Sonic the Hedgehog 2, Star Fox y The Sims (PC). Más **7 reseñas de juegos de origen arcade armadas el 2026-11-22**, con el póster oficial del arcade como imagen principal y gráfica nueva (PR 30 a 36, ya en master y en Drive, sin grabar): Tumble Pop (arcade 1991, port Game Boy), Snow Bros., Michael Jackson's Moonwalker (arcade y Mega Drive, 1990), Bubble Bobble (arcade 1986), Double Dragon (arcade 1987), Captain Commando y Metal Slug (1996). Tumble Pop, Moonwalker y Captain Commando tienen aún el "Sigue con" por elegir al publicar; a las siete les falta `proxima` tras grabar. Programada: Diablo (mar 24 nov). Ya publicadas y retiradas del estudio: Contra, Final Fight, The Witcher, Yoshi's Island, Ocarina of Time, Need for Speed: Underground 2, Mighty Morphin Power Rangers, Metal Warriors, Melee, Montezuma's Revenge, International Superstar Soccer y God of War (PS2).

**Rankings (21) — consolidado 2026-11-22 contra `studio/rankings/` (Dreamcast Top Mundial está programado para el dom 22 nov y no cuenta acá):**
- **Top Mundial (4):** Atari 8-bit, PS2, Saturn y Xbox.
- **Top Precios (7):** Atari 8-bit, Dreamcast, GameCube, Mega Drive, PS1, PS Vita y Saturn (Top Precios con la auditoría canon de grial y rarezas aplicada).
- **Top Peores (7):** Atari 2600 (el piloto del formato, restaurado el 2026-11-22), Dreamcast, Game Boy (restaurado el 2026-11-22), GameCube, Mega Drive, NES y Saturn (Saturn relaja la regla NTSC USA con 2 juegos solo Japón, avisado en pantalla). Todos con gráfica nueva y notas largas; ver sus pautas en `docs/pautas/`.
- **Joyas ocultas (3):** GameCube, Mega Drive y PS1 (el de SNES ya se publicó el 15 nov; el de N64 está en Curaduría N64).
- **Publicados que se conservan para su reforge (7):** N64, SNES y NES Top Mundial y Top Precios, y PS Vita Top Mundial (no son backlog; ver `docs/canal/retiro-publicados.md`).

**Sagas (11):** Donkey Kong, Kirby, Mario, Mega Man, Metal Gear, Metroid, Mortal Kombat,
Resident Evil, Smash Bros, Sonic, Street Fighter. **Sigue siendo el mayor backlog del
canal en volumen** (11 de 12 sin publicar).

**Specials (5):** Cuadrilla del Frío (`retro-cuadrilla-frio`), Día del Trabajador
(`retro-dia-trabajador`), Día del Gato (`retro-dia-del-gato`) y, armados el 2026-11-18 y el 2026-11-20 (PR 28 y 29, en master y en Drive, sin grabar), los dos capítulos del especial de juegos de película: **Mejores** (`retro-peliculas-mejores`) y **Peores** (`retro-peliculas-peores`), multi-consola, 10 juegos cada uno, con gráfica nueva y notas largas. Quedan abiertas las preguntas de la discusión para Luis y Coco y los puntos "por confirmar" de las notas.

**Curaduría N64-only (5):** Hardware Raro, Joyas Ocultas, Kirkhope Rare (biográfico
compositor), Nintendo vs PlayStation, No-Latam. **Sigue sin playlist de destino
asignada** (pendiente de decidir con Luis — ver sección 4).

**RetroNotas (3):** Lost Localizations, Chilean Arcade Scene y Consola pirata LATAM. Formato nuevo (agosto 2026),
0 publicadas todavía — sin playlist propia definida.

---

## 2. Shorts (9:16)

> **Sin reauditar en esta pasada (2026-08-20).** Datos de la última verificación,
> 2026-07-21 — pueden estar desactualizados; el canal pasó de 41 a 55 videos totales en un
> mes, así que hay shorts nuevos sin contar acá. Reauditar del JSON `ytInitialData` de la
> pestaña Shorts cuando se necesite el número real.

### TarroShorts (pipeline HTML + render automático)

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
juego de plantas". Edición directa en CapCut, sin HTML ni narración generada.

### Lane Luis / Lane Koko (guionados, sin HTML)

Curiosidades históricas (Luis solo) y batería/performance (Koko solo). Documentados en
`docs/canal/guiones-shorts.md`.

### TarroTeaser (no es contenido final, es insumo de edición)

`tarroteaser.py` (en TarroDL, `tarrodl_taller/teaser/`) corta un teaser crudo del video master para editar en CapCut. No
se publica tal cual.

---

## 3. La brecha principal: se produce más rápido de lo que se publica

- **Sagas:** 12 armadas, 1 publicada (11 de backlog) — **sigue siendo la brecha más
  grande del canal**, sin cambios desde julio.
- **Reseñas:** 63 armadas, 36 publicadas, 1 programada (Diablo) y 26 de backlog sin
  fecha — el formato que más rápido está publicando, y aun así sigue siendo el mayor
  backlog en volumen absoluto tras sumar las 7 de arcade.
- **Rankings:** 42 armados, 20 publicados, 1 programado (Dreamcast Top Mundial) y 21 de backlog.
- **Specials:** 7 armados, 2 publicados, 5 de backlog (con los dos de juegos de película).
- **Curaduría N64:** 5 armados, 0 publicados — sigue sin casa en el menú de playlists.
- **RetroNotas:** 3 armadas, 0 publicadas — formato nuevo, sin playlist propia todavía.
- **Colecciones sigue siendo la única categoría 100% al día** (4 armadas = 4 publicadas), con 3 reforges armados sin grabar.

## 4. Pendiente de decidir con Luis

1. Playlist de destino para la curaduría N64-only (hardware-raro, joyas-ocultas,
   kirkhope-rare, nintendo-vs-playstation, no-latam) — sigue sin casa en el menú de
   playlists del canal (arrastrado desde julio, sin resolver).
2. Playlist de destino para RetroNotas (formato nuevo, agosto 2026) — mismo problema.
3. Ritmo de publicación del backlog de Sagas, Reseñas y Rankings — ¿calendario fijo o se
   suben a medida que se van necesitando para el algoritmo? El ritmo actual de
   "Programado" en YouTube Studio (1 cada 3-4 días, casi todo Reseñas) sugiere que Reseñas
   se está usando como la cadencia principal mientras Sagas queda estancado.
4. Si los shorts de B-roll simple (sin TarroBot) siguen siendo un formato válido aparte.
5. **Reauditar la sección 2 (shorts):** la API del 2026-11-20 muestra unos 30 videos de hasta 2 minutos publicados (13 de hasta 60 s y 17 entre 1 y 2 min), contra los 22 que cuenta esta sección. Falta cruzarlos uno a uno por título.

---

*Fuente: pestaña "Videos" de `youtube.com/@Retrotarros` (JSON `ytInitialData` extraído en
vivo, 28 videos largos totales) + captura de YouTube Studio "Programado" (Luis,
2026-08-20) + `studio/`, `docs/pautas/pauta-*.md`, `docs/descripciones/descripcion-*.md`.
Actualizar este doc cuando cambie significativamente lo publicado/programado.*
