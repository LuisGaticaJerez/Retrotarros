# RETROTARROS — Pauta de episodio largo

*Nostalgia + Juegos + Música*

**Top 10 Atari 2600 mundial — Los mejores juegos segun la critica**

*Generacion 2 · Atari Video Computer System · Ranking de calidad*

Documento de trabajo · Luis Balbrigame & Coco

---

## Proposito de esta pauta

Top 10 mundial del Atari 2600 segun consenso critico (SVG, CBR, GamesRadar, RetroDodo) cruzado con hitos historicos verificables. Es el **ranking de CALIDAD** del catalogo Atari 2600 — la contraparte de `atari-2600-top-precios` (ranking de mercado).

Sirve como:
- Vitrina del catalogo "fundacional" de la consola raiz de toda la industria.
- Anclaje para nuevos suscriptores que no conocen el Atari 2600 mas alla de "el juego de la serpiente".
- Trampolin para discusion en chat ("¿por que Pitfall y no Pac-Man?").
- Primera pieza del arco Atari 2600, junto con `top-precios` (todavia no hay `coleccion` — no hay Atari 2600 en la coleccion fisica de Retrotarros).

**Cierra con cliffhanger a `atari-2600-top-precios`** (¿cuanto valen hoy?).

---

## Concepto del episodio

Formato presentacion visual con HTML del estudio (`studio/rankings/top-mundial/atari-2600-top-mundial.html`):

- 14 slides navegables del 01 al 14.
- Portada con tag "GENERACION 2 · 8 BITS · ATARI".
- 10 slides hibridas (cartucho + posicion + TarroVision + meta + bloque "POR QUE").
- Recorrido #10 → #1 (suspenso, formato estandar ranking).
- Cierre con analisis ("la cuna de los origenes") + cliffhanger a precios.

**Duracion objetivo:** 20-26 minutos.

---

## El ranking (#10 → #1)

| # | Juego | Año | Editor | Por que |
|---|-------|-----|--------|---------|
| 10 | Combat | 1977 | Atari | Pack-in original de la consola: el primer videojuego de millones de personas. |
| 9 | Kaboom! | 1981 | Activision | Larry Kaplan, control de paddle usado como instrumento. |
| 8 | Missile Command | 1981 | Atari | Port de arcade, tension real (el creador tuvo pesadillas nucleares). |
| 7 | Raiders of the Lost Ark | 1982 | Atari | Licencia de pelicula tomada en serio: mapa, inventario, puzzles. |
| 6 | Space Invaders | 1980 | Atari | El primer "killer app" de la industria: vendio 2M+ y disparo la consola. |
| 5 | River Raid | 1982 | Activision | Carol Shaw, primera disenadora mujer ampliamente reconocida de la historia. |
| 4 | Yars' Revenge | 1982 | Atari | El original mas vendido de toda la consola (no port de arcade). |
| 3 | Adventure | 1980 | Atari | Warren Robinett y el primer Easter egg de la historia de los videojuegos. |
| 2 | Pac-Man | 1982 | Atari | El mas vendido (8M+), pero la conversion decepciono a todo el mundo. |
| 1 | Pitfall! | 1982 | Activision | David Crane, 255 pantallas en 4KB. Padre del plataformas de accion. |

**Balance:** 6 Atari first-party · 4 Activision. Todos los items son juegos ORIGINALES o ports oficiales — ningun clon/bootleg en el top mundial (esos van en el episodio de precios, apartado rarezas).

> Ranking de consenso critico/historico cruzado con hitos verificables via Wikipedia/AtariAge. Años en release US para coherencia con la audiencia Latam.

---

## Estructura del episodio (20-26 min)

### Bloque 1 · Cold open (0:00 – 0:40)

Plano de la caja de Pitfall! o Adventure sobre la mesa. Luis:

> *"Antes de Mario, antes de Sonic, antes de que existiera casi todo lo que conocemos como videojuego, estaba esto. Los 10 mejores juegos de la historia del Atari 2600, segun el mundo entero. Vamos del diez al uno."*

### Bloque 2 · Setup (0:40 – 1:30)

- Luis explica la metodologia: cruce de rankings criticos + hitos historicos verificables.
- Aclara: es calidad/impacto historico, no precio (eso viene la proxima).
- "Cada juego de este top inventa algo que todavia usamos hoy."

### Bloque 3 · Recorrido #10 → #1 (1:30 – 22:00)

~20 min / 10 juegos = ~2:00 por puesto.

**Estructura repetible por puesto (1 slide):**
- Luis lee la posicion y el titulo.
- Corre el gameplay en la TarroVision.
- Luis lee/parafrasea el bloque "POR QUE".
- Coco reacciona desde lo personal (jugue / no jugue / me costo).

**Donde NO ahorrar tiempo:** el podio (#3 Adventure, #2 Pac-Man, #1 Pitfall!) — ahi estan los 3 datos mas fuertes del episodio (Easter egg, decepcion historica, 4KB de memoria).

### Bloque 4 · Analisis + cierre (22:00 – 26:00)

- Slide 13: "la cuna de los origenes" (cada juego marco un primero de la industria).
- Slide 14: cliffhanger a `atari-2600-top-precios`.

---

## Reglas de ejecucion en vivo

- **Cada puesto max 2:15.** Reservar tiempo para el podio.
- **No spoilear el #1** hasta llegar.
- **Asumir las polemicas**: "puede que tu pongas Yars' Revenge primero, dinos en los comentarios".

### Lo que SI se dice
- "Esto es consenso critico + hitos verificados, no mi opinion personal".
- "Por que esta aca": justificar cada puesto con el dato historico, no solo nostalgia.

### Lo que NO se dice
- No mencionar precios (es el otro episodio).
- No inventar cifras de ventas sin fuente verificada.

---

## Material visual necesario

- [ ] **10 clips de gameplay** (uno por juego), 10-15 seg distintivos.
- [x] Box art real para los 10 juegos (`studio/rankings/top-mundial/img/atari-2600-top-mundial/`) — todas verificadas, ninguna necesito fallback.
- [ ] Caja fisica de Pitfall! o Adventure para el cold open (conseguir prestada o replica — no esta en la coleccion de Retrotarros).

---

## Estado de la pauta

| Item | Estado |
|------|--------|
| HTML estudio (`studio/rankings/top-mundial/atari-2600-top-mundial.html`) | ✓ Cerrado (14 slides) |
| JSON TarroBot (`studio/pautas/atari-2600-top-mundial.tarrobot.json`) | ✓ 10 datos #10→#1 |
| Box art (10/10 reales) | ✓ |
| Clips de gameplay (10) | ☐ Pendiente |
| Pauta MD (este archivo) | ✓ |
| Discusion MD (`docs/discusion-atari-2600-top-mundial.md`) | ✓ |

---

**Ultima actualizacion:** 2026-07-29
**Slug:** `atari-2600-top-mundial`
**HTML asociado:** `studio/rankings/top-mundial/atari-2600-top-mundial.html`
**Discusion:** `docs/discusion-atari-2600-top-mundial.md`
