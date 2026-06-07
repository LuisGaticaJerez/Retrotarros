# RETROTARROS — Pauta de episodio largo

*Nostalgia + Juegos + Música*

**Top 10 NES mas caros del mundo — Ranking de mercado**

*Generacion 3 · Nintendo Entertainment System · Ranking de precios*

Documento de trabajo · Luis Balbrigame & Koko

---

## Proposito de esta pauta

Top 10 de los cartuchos NES mas caros del mundo (valor de mercado coleccionista). Es el **ranking de PRECIOS** — la contraparte de `nes-top-mundial` (ranking de calidad).

Sirve como:
- Contenido "wow" de alto enganche (cifras que sorprenden).
- Educacion coleccionista: por que algo es caro (rareza, no calidad).
- Cierre del arco NES (coleccion + mundial + precios).

**Cierra el arco NES completo** con invitacion a la proxima consola.

---

## Concepto del episodio

Formato presentacion visual con HTML del estudio (`studio/nes-top-precios.html`):

- 14 slides navegables del 01 al 14.
- Portada con tag "TOP 10 · MAS CAROS · VALOR DE MERCADO".
- 10 slides hibridas (cartucho + posicion + TarroVision + precio + bloque "POR QUE").
- Recorrido #10 → #1 (suspenso creciente de cifras).
- Cierre con analisis (rareza, no calidad) + cierre de arco NES.

**Duracion objetivo:** 18-24 minutos.

---

## El ranking (#10 → #1)

| # | Juego | Año | Editor | Valor aprox. (USD) | Por que es caro |
|---|-------|-----|--------|--------------------|-----------------|
| 10 | Bonk's Adventure | 1994 | Hudson | 700 | Tirada minima de fin de ciclo. |
| 9 | Panic Restaurant | 1992 | Taito | 850 | Obscuro, pocos lo compraron. |
| 8 | Cheetahmen II | 1992 | Active Enterprises | 900 | Nunca salio, hallado en bodega. |
| 7 | Bubble Bath Babes | 1991 | Panesian | 1.500 | Sin licencia (adulto), prohibido. |
| 6 | Flintstones: Surprise at Dinosaur Peak | 1994 | Taito | 2.000 | Solo alquiler Blockbuster USA. |
| 5 | Little Samson | 1992 | Taito | 3.000 | Gran juego, vendio pesimo. |
| 4 | Stadium Events | 1987 | Bandai | 25.000 | Retirado del mercado (grial famoso). |
| 3 | Nintendo Campus Challenge 1991 | 1991 | Nintendo | 20.000+ | Cartucho de competencia, ~1 sobrevivio. |
| 2 | Nintendo World Championships (gris) | 1990 | Nintendo | 30.000+ | ~90 carts de torneo. |
| 1 | Nintendo World Championships (dorado) | 1990 | Nintendo | 100.000+ | Solo 26 carts dorados, el grial absoluto. |

> Valores de mercado APROXIMADOS (USD), cruce de PriceCharting, Den of Geek y GameValueNow (2025). Las cifras fluctuan; presentarlas como "valor aproximado", no precio fijo.

---

## Estructura del episodio (18-24 min)

### Bloque 1 · Cold open (0:00 – 0:40)

Plano de un cartucho NES comun. Luis:

> *"Este cartucho cuesta como diez lucas. Pero hay uno de NES que cuesta mas de cien mil dolares. Hoy vemos los diez juegos de NES mas caros del planeta, y el numero uno es una locura. Del diez al uno."*

### Bloque 2 · Setup (0:40 – 1:30)

- Luis aclara: esto es PRECIO, no calidad (a diferencia del episodio pasado).
- "Casi ninguno esta aca por bueno. Estan por raros".
- Avisa que las cifras son valor de mercado aproximado.

### Bloque 3 · Recorrido #10 → #1 (1:30 – 20:00)

~18 min / 10 = ~1:50 por puesto.

**Estructura repetible (1 slide):**
- Luis lee posicion + titulo + precio.
- Corre gameplay/box en la TarroVision.
- Luis explica POR QUE es caro (la rareza, la historia).
- Koko reacciona a la cifra ("¿¿cuanto??").

**Donde NO ahorrar:** el podio (#3 Campus Challenge, #2 NWC gris, #1 NWC dorado) — las historias mas locas.

### Bloque 4 · Analisis + cierre (20:00 – 24:00)

- Slide 13: rareza, no calidad (la tesis del episodio).
- Slide 14: cierre del arco NES + proxima consola.

---

## Reglas de ejecucion en vivo

- **Cada puesto max 2:00.** Guardar tiempo para el podio.
- **Siempre decir "valor aproximado"** — nunca afirmar un precio como fijo.
- **Separar precio de calidad**: dejar claro que caro ≠ bueno (Cheetahmen II es malo y carisimo).

### Lo que SI se dice
- "Esto es valor de mercado, fluctua".
- "Es caro por X" (rareza concreta: retiro, competencia, alquiler).

### Lo que NO se dice
- No prometer que vale eso "seguro" (es referencial).
- No dar consejo de inversion.

---

## Material visual necesario

- [ ] **Box art / fotos** de los 10 grales (el HTML usa etiqueta de color si falta imagen).
- [ ] Cartucho NES comun para el cold open (contraste con los caros).
- [ ] Idealmente, foto del cartucho dorado de NWC para el #1.

El HTML funciona con placeholders `tv-noscreen` + etiqueta de color por juego.

---

## Estado de la pauta

| Item | Estado |
|------|--------|
| HTML estudio (`studio/nes-top-precios.html`) | ✓ Cerrado (14 slides) |
| JSON TarroBot (`studio/pautas/nes-top-precios.tarrobot.json`) | ✓ 10 datos #10→#1 + precio_short |
| Box art / fotos | ☐ Pendiente |
| Pauta MD (este archivo) | ✓ |
| Discusion MD (`docs/discusion-nes-top-precios.md`) | ✓ |

---

**Ultima actualizacion:** 2026-06-07
**Slug:** `nes-top-precios`
**HTML asociado:** `studio/nes-top-precios.html`
**Discusion:** `docs/discusion-nes-top-precios.md`
