# RETROTARROS — Pauta de episodio largo

*Nostalgia + Juegos + Música*

**Top 10 NES mundial — Los mejores juegos segun la critica**

*Generacion 3 · Nintendo Entertainment System · Ranking de calidad*

Documento de trabajo · Luis Balbrigame & Koko

---

## Proposito de esta pauta

Top 10 mundial de la NES segun el consenso critico (IGN, Nintendo Life, Edge, GamesRadar). Es el **ranking de CALIDAD** del catalogo NES — la contraparte de `nes-top-precios` (ranking de mercado).

Sirve como:
- Vitrina del catalogo "imprescindible" de la consola raiz.
- Anclaje para nuevos suscriptores sin contexto del 8 bits.
- Trampolin para discusion en chat ("¿por que SMB3 y no Zelda?").
- Pieza maestra del arco NES junto con `coleccion` y `top-precios`.

**Cierra con cliffhanger a `nes-top-precios`** (¿cuanto valen hoy?).

---

## Concepto del episodio

Formato presentacion visual con HTML del estudio (`studio/nes-top-mundial.html`):

- 14 slides navegables del 01 al 14.
- Portada con tag "TOP 10 · MUNDIAL · CONSENSO 2026".
- 10 slides hibridas (cartucho + posicion + TarroVision + meta + bloque "POR QUE").
- Recorrido #10 → #1 (suspenso, formato estandar ranking).
- Cierre con analisis (dominio Nintendo) + cliffhanger a precios.

**Duracion objetivo:** 20-26 minutos.

---

## El ranking (#10 → #1)

| # | Juego | Año | Editor | Por que |
|---|-------|-----|--------|---------|
| 10 | Castlevania III: Dracula's Curse | 1990 | Konami | Chip VRC6, rutas ramificadas, Alucard jugable. |
| 9 | Ninja Gaiden | 1989 | Tecmo | Cinematicas tipo comic, action-platformer veloz. |
| 8 | Contra | 1988 | Konami | Run-and-gun cooperativo, el codigo Konami. |
| 7 | Kirby's Adventure | 1993 | HAL Laboratory | Copiar poderes, ultimo gran NES. |
| 6 | Punch-Out!! | 1987 | Nintendo | Boxeo de patrones, Little Mac vs gigantes. |
| 5 | Mega Man 2 | 1989 | Capcom | Perfecciono la formula, BSO legendaria. |
| 4 | Metroid | 1987 | Nintendo | Exploracion no-lineal, el giro de Samus. |
| 3 | The Legend of Zelda | 1987 | Nintendo | Cartucho dorado, mundo abierto, bateria. |
| 2 | Super Mario Bros. | 1985 | Nintendo | Salvo la industria, definio el plataformero. |
| 1 | Super Mario Bros. 3 | 1990 | Nintendo | Para la critica, el mejor NES de todos. |

**Balance:** 6 first-party Nintendo · Konami x2 · Capcom x1 · Tecmo x1.

> Ranking de consenso critico/historico. Años en release NTSC (US) para coherencia con la audiencia Latam.

---

## Estructura del episodio (20-26 min)

### Bloque 1 · Cold open (0:00 – 0:40)

Plano del cartucho dorado de Zelda o de SMB3 sobre la mesa. Luis:

> *"De los cientos de juegos que tuvo la NES, ¿cuales son los diez mejores segun el mundo entero? No es mi opinion, es el consenso de la critica. Y el numero uno no se discute. Vamos del diez al uno."*

### Bloque 2 · Setup (0:40 – 1:30)

- Luis explica la metodologia: cruce de rankings criticos.
- Aclara: es calidad, no precio (eso viene la proxima).
- "Los primeros tres son casi sagrados".

### Bloque 3 · Recorrido #10 → #1 (1:30 – 22:00)

~20 min / 10 juegos = ~2:00 por puesto.

**Estructura repetible por puesto (1 slide):**
- Luis lee la posicion y el titulo.
- Corre el gameplay en la TarroVision.
- Luis lee/parafrasea el bloque "POR QUE".
- Koko reacciona desde lo personal (jugue / no jugue / me costo).

**Donde NO ahorrar tiempo:** el podio (#3 Zelda, #2 SMB, #1 SMB3) — la conversacion fuerte.

### Bloque 4 · Analisis + cierre (22:00 – 26:00)

- Slide 13: dominio Nintendo (6/10 first-party).
- Slide 14: cliffhanger a `nes-top-precios`.

---

## Reglas de ejecucion en vivo

- **Cada puesto max 2:15.** Reservar tiempo para el podio.
- **No spoilear el #1** hasta llegar (aunque sea obvio, mantener el suspenso).
- **Asumir las polemicas**: "puede que tu pongas Zelda primero, dimelo en los comentarios".

### Lo que SI se dice
- "Esto es consenso critico, no mi opinion personal".
- "Por que esta aca": justificar cada puesto.

### Lo que NO se dice
- No mencionar precios (es el otro episodio).
- No inventar cifras de ventas sin estar seguros.

---

## Material visual necesario

- [ ] **10 clips de gameplay** (uno por juego), 10-15 seg distintivos.
- [ ] Box art / cartuchos fisicos para los planos (el HTML usa etiqueta de color si falta imagen).
- [ ] Cartucho dorado de Zelda para el cold open.

El HTML funciona con placeholders `tv-noscreen` (NO SIGNAL) + etiqueta de color por juego.

---

## Estado de la pauta

| Item | Estado |
|------|--------|
| HTML estudio (`studio/nes-top-mundial.html`) | ✓ Cerrado (14 slides) |
| JSON TarroBot (`studio/pautas/nes-top-mundial.tarrobot.json`) | ✓ 10 datos #10→#1 |
| Clips de gameplay (10) | ☐ Pendiente |
| Pauta MD (este archivo) | ✓ |
| Discusion MD (`docs/discusion-nes-top-mundial.md`) | ✓ |

---

**Ultima actualizacion:** 2026-06-07
**Slug:** `nes-top-mundial`
**HTML asociado:** `studio/nes-top-mundial.html`
**Discusion:** `docs/discusion-nes-top-mundial.md`
