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
| Reseñas | 44 | 24 | 0 | 20 |
| Rankings (Top Mundial + Top Precios, 12 consolas + Top Peores: piloto Atari 2600 + NES, SNES, Mega Drive, PS1, N64, Game Boy, Dreamcast, Saturn y GameCube) | 34 | 14 | ? | 20 |
| Sagas de videojuegos | 12 | 1 | 0 | 11 |
| Specials | 5 | 2 | 0 | 3 |
| Curaduría N64-only | 5 | 0 | 0 | 5 |
| RetroNotas | 2 | 0 | 0 | 2 |
| Colecciones | 4 | 4 | 0 | 0 |
| **TOTAL** | **98** | **36** | **4** | **58** |

Aparte, fuera de esta tabla: **Abriendo el tarro** (1 publicado, formato dependiente de
invitado, no tiene "backlog" fijo) y **2 episodios G-OLD** archivados (versiones viejas
superadas, playlist muerta, no cuentan como activo). 25 + 8 + 1 + 2 = 36 de los 28 videos
"largos" reales del canal — los G-OLD y Abriendo el Tarro están dentro de esos 28
publicados totales verificados en YouTube; los 8 programados todavía no cuentan como
publicados.

---

### 1.1 Programados — Reseñas (0 confirmadas, 2026-10-09)

Las 4 que figuraban acá (Super Mario World, Golden Axe, Street Fighter II y Chrono Trigger)
ya están publicadas en el canal (movidas a 1.2). No se revisó YouTube Studio, así que no hay
reseñas programadas confirmadas hoy.

---|---|---|---|
| 25 ago 2026 | Yoshi estuvo 5 años esperando este juego para nacer (Super Mario World) | `resena-super-mario-world` | Reseña |
| 27 ago 2026 | El juego que Sega inspiró en las películas de Conan (Golden Axe) | `resena-golden-axe` | Reseña |
| 1 sept 2026 | El juego que Capcom no le tenía Fe (Street Fighter II) | `resena-street-fighter-ii` | Reseña |
| 4 sept 2026 | Chrono Trigger: el RPG de un viaje de 4 días entre 3 leyendas | `resena-chrono-trigger` | Reseña |

---

### 1.2 Publicados (25 + Abriendo el Tarro + 2 G-OLD, más las Reseñas nuevas de abajo)

**Reseñas (24) — verificado en vivo 2026-10-09, del más reciente al más antiguo:**
Worms Armageddon (pedida), Samurai Shodown (pedida), Doom (pedida), King of Fighters '94,
Battletoads, Super Mario World, Street Fighter II, Golden Axe, Metal Gear Solid (pedida),
Chrono Trigger, The Legend of Zelda (pedida), Cadillacs and Dinosaurs (pedida), Jewel Master
(pedida), Top Gear (pedida), Pokémon Rojo/Azul (pedida), Zombies Ate My Neighbors, Super
Metroid (pedida), Mega Man 2, Donkey Kong Country, Kirby's Adventure, Killer Instinct,
Pitfall: The Mayan Adventure (pedida), Mortal Kombat, Super Mario Bros. 3. Sus HTML, carpetas
del Drive y kits de YouTube (`docs/descripciones/`) se retiraron el 2026-10-09 (siguen en el historial de git).

**Rankings (10):** Master System Top Mundial + Top Precios, Mega Drive Top Mundial, NES
Top Mundial + Top Precios, SNES Top Mundial + Top Precios, N64 Top Mundial + Top Precios,
PS Vita Top Mundial.

**Sagas (1):** Zelda.

**Specials (2):** Día del Padre (`retro-padres-gamer`), Mes del Mar / Glorias Navales
(`retro-glorias-navales`).

**Colecciones (4, al día):** N64, SNES, NES, PS Vita.

**Abriendo el tarro (1):** Los tesoros numismáticos de Arturo.

**G-OLD archivado (2, discontinuado, no se repite):** "Coleccion RetroTarros N64" y
"Ranking Retrotarros vs el mundo N64" — versiones viejas de los primeros pasos del canal.

---

### 1.3 Backlog armado — listo para programar, sin fecha (49)

**Reseñas (20) — verificado en vivo 2026-10-09:** Aladdin, Altered Beast, Contra, Crash
Bandicoot, Earthbound, Earthworm Jim, Fatal Fury, Final Fight, International Superstar
Soccer, Kirby Super Star, A Link to the Past, Sonic the Hedgehog, Sonic the Hedgehog 2, Star
Fox, Yoshi's Island, más 5 pedidas: Metal Warriors, Super Smash Bros. Melee, Mighty Morphin
Power Rangers, JoJo's Bizarre Adventure y Montezuma's Revenge.

**Rankings (17):** Mega Drive Top Precios, PS Vita Top Precios, Dreamcast Top Mundial +
Top Precios, Saturn Top Mundial + Top Precios, PS1 Top Mundial + Top Precios (recién
armados 2026-09-21 — apertura del arco PS1, ver `docs/arcos/ps1.md`), GameCube Top Mundial
+ Top Precios (recién armados 2026-09-22 — apertura del arco GameCube completa, ver
`docs/arcos/gamecube.md`; Top Precios con la auditoría canon aplicada desde el arranque),
Atari 2600 Top Peores (PILOTO de un formato nuevo, espejo del Top Mundial con tono divertido,
armado 2026-10-04; pendiente de ok de Luis y Coco sobre el orden — ver
`docs/pautas/pauta-atari-2600-top-peores.md`), NES Top Peores, SNES Top Peores y Mega Drive Top Peores
(tanda 1 de los Top Peores por consola, armados 2026-10-06; cuñas chistosas a pedido de Luis; pendientes de
ok de Luis y Coco sobre el orden — ver `docs/pautas/pauta-nes-top-peores.md`, `pauta-snes-top-peores.md` y
`pauta-mega-drive-top-peores.md`); tanda 2 (PS1, N64 y Game Boy) armada 2026-10-06, ver `pauta-ps1-top-peores.md`,
`pauta-n64-top-peores.md` y `pauta-gameboy-top-peores.md`; tanda 3 (Dreamcast, Saturn y GameCube) armada 2026-10-06, ver `pauta-dreamcast-top-peores.md`,
`pauta-saturn-top-peores.md` y `pauta-gamecube-top-peores.md` (Saturn relaja la regla NTSC USA con 2 juegos solo Japon, avisado en pantalla).
Atari 2600 Top Precios y Game Boy Top Mundial + Top Precios salieron de esta lista: ya
están publicados en el canal (verificado en vivo 2026-09-21/22), el doc los tenía mal
clasificados como backlog.

**Sagas (11):** Donkey Kong, Kirby, Mario, Mega Man, Metal Gear, Metroid, Mortal Kombat,
Resident Evil, Smash Bros, Sonic, Street Fighter. **Sigue siendo el mayor backlog del
canal en volumen** (11 de 12 sin publicar).

**Specials (3):** Cuadrilla del Frío (`retro-cuadrilla-frio`), Día del Trabajador
(`retro-dia-trabajador`), Día del Gato (`retro-dia-del-gato`).

**Curaduría N64-only (5):** Hardware Raro, Joyas Ocultas, Kirkhope Rare (biográfico
compositor), Nintendo vs PlayStation, No-Latam. **Sigue sin playlist de destino
asignada** (pendiente de decidir con Luis — ver sección 4).

**RetroNotas (2):** Lost Localizations, Chilean Arcade Scene. Formato nuevo (agosto 2026),
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

`scripts/tarroteaser.py` corta un teaser crudo del video master para editar en CapCut. No
se publica tal cual.

---

## 3. La brecha principal: se produce más rápido de lo que se publica

- **Sagas:** 12 armadas, 1 publicada (11 de backlog) — **sigue siendo la brecha más
  grande del canal**, sin cambios desde julio.
- **Reseñas:** 44 armadas, 24 publicadas (verificado en vivo 2026-10-09), 20 de backlog sin
  fecha, 0 programadas confirmadas — el formato que más rápido está publicando, y aun así
  sigue siendo el segundo backlog más grande en volumen absoluto.
- **Rankings:** 20 armados, 10 publicados, 1 programado (9 de backlog).
- **Curaduría N64:** 5 armados, 0 publicados — sigue sin casa en el menú de playlists.
- **RetroNotas:** 2 armadas, 0 publicadas — formato nuevo, sin playlist propia todavía.
- **Colecciones sigue siendo la única categoría 100% al día** (4 armadas = 4 publicadas).

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

---

*Fuente: pestaña "Videos" de `youtube.com/@Retrotarros` (JSON `ytInitialData` extraído en
vivo, 28 videos largos totales) + captura de YouTube Studio "Programado" (Luis,
2026-08-20) + `studio/`, `docs/pautas/pauta-*.md`, `docs/descripciones/descripcion-*.md`.
Actualizar este doc cuando cambie significativamente lo publicado/programado.*
