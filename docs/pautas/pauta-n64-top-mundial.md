# RETROTARROS — Pauta de episodio largo

*Nostalgia + Juegos + Música*

**Top 10 N64 Mundial — Lo que la crítica ama**

*Generación 5 · Nintendo 64*

Documento de trabajo · Luis Balbrigame & Koko

---

## Propósito de esta pauta

> **REFORGE 2026-08-24:** se sacó el rótulo "Parte 1 de 2" — Luis pidió que cada regeneración se trate como capítulo independiente, no como partes numeradas de una serie. El episodio sigue teniendo un cierre que teasea el top de precios (contenido relacionado natural, no una numeración forzada), pero ya no se presenta como "1 de 2".

Episodio sobre el top 10 de juegos según la crítica internacional: cinco rankings consultados (Nintendo Life, GamesRadar, Dexerto, The Phrasemaker, Cousin Gaming), revelados del #10 al #1 con suspenso ascendente.

**Cierra con un cliffhanger hacia el episodio de precios** — sin numerarlo como "parte 2", solo como contenido relacionado que conviene ver después.

> **Nota histórica:** este episodio se grabó originalmente junto al de precios (1 hora total) y se cortó en dos videos de 18-22 min cada uno. Esa decisión de producción (grabar ambos juntos) se mantiene; lo que cambió es que ya no se presentan como partes numeradas de una serie.

---

## Concepto del episodio

Formato de presentación visual con HTML del estudio (`studio/rankings/top-mundial/n64-top-mundial.html`):

- 14 slides navegables del 01 al 14.
- Portada sin numeración de partes — episodio independiente.
- Separador de bloque → 10 slides de juegos del #10 al #1 → cierre con transición.
- Koko reacciona desde su experiencia personal con cada juego.
- Cierre fija el cliffhanger: "El mundo ama estos. Pero el mercado paga otros."

**Duración objetivo:** 18-22 minutos.

---

> **REFORGE 2026-08-24:** episodio recontrastado (formato visual nuevo de enfasis en gameplay + verificacion de datos). El consenso critico se revisó contra rankings actuales (GamesRadar, game8, Ultimate Ranks) — **sin cambios**: Ocarina, Mario 64, GoldenEye y Banjo siguen top absoluto en todas las fuentes nuevas consultadas. El HTML (`studio/rankings/top-mundial/n64-top-mundial.html`) se regeneró completo con `top_deck.py` (antes era HTML a mano, formato viejo sin TarroVision).

## El Top 10 mundial — consenso crítico 2026

Cruce de 5 fuentes (Nintendo Life mar 2025, GamesRadar feb 2026, Dexerto ene 2026, The Phrasemaker mar 2026, Cousin Gaming dic 2025). Los primeros 4 son consenso absoluto. Del 5 al 10 hay variación entre listas.

| # | Juego | Año | Dato curioso |
|---|-------|-----|--------------|
| **1** | The Legend of Zelda: Ocarina of Time | 1998 | #1 en TODOS los rankings. Música dinámica de Kondo según dirección de Link — predecesor de GTA / Red Dead. |
| **2** | Super Mario 64 | 1996 | Iba a ser on-rails. Miyamoto lo cambió a mitad del desarrollo cuando descubrió el analógico. |
| **3** | Banjo-Kazooie | 1998 | Kirkhope inventó instrumentación dinámica por zona para resolver límite de memoria. |
| **4** | GoldenEye 007 | 1997 | El equipo de Rare nunca había hecho un FPS. Vendió 8M copias. |
| **5** | Mario Kart 64 | 1996 | El caparazón azul se diseñó para que novatos pudieran ganarles a expertos. Política, no técnica. |
| **6** | Super Smash Bros. | 1999 | Iwata + Sakurai lo hicieron a escondidas de Nintendo. |
| **7** | Majora's Mask | 2000 | Hecho en UN AÑO con motor y assets reciclados de Ocarina. |
| **8** | Paper Mario | 2000 | Iba a ser Super Mario RPG 2. La estética de papel nació de un problema legal con Square. |
| **9** | Perfect Dark | 2000 | Primer juego en obligar Expansion Pak. Sin él no podías ni completar el primer nivel. |
| **10** | Star Fox 64 | 1997 | Rumble Pak incluido GRATIS — Nintendo necesitaba que la gente lo tuviera. Caballo de Troya del rumble. |

---

## Estructura del episodio (18-22 min)

### Bloque 1 · Cold open (0:00 – 0:30)

Plano cerrado de un cartucho N64 sobre la mesa. Luis a cámara: *"Estos son los diez N64 que el mundo entero te diría que tení que jugar antes de morirte. Cinco rankings, miles de votos, una sola consola."* Cut a logo.

### Bloque 2 · Setup (0:30 – 1:30)

- Luis explica las 5 fuentes consultadas.
- Aclara que vamos del #10 al #1 — suspenso ascendente.
- Avisa que se viene el top de precios en otro episodio (sin numerarlo como "parte 2").
- Koko: "yo no tengo idea cómo viene el ranking, vamos a ver".

### Bloque 3 · Cuenta regresiva (1:30 – 17:00)

15-16 min para 10 juegos = ~90 seg promedio por juego.

**Estructura repetible por slide:**
- Luis lee el slide: posición + nombre + año.
- Luis lee el dato curioso.
- Koko reacciona desde su experiencia (15-30 seg): ¿lo jugó? ¿qué le hizo a él?
- Si hay debate, máximo 30 seg.
- Avanzar.

**Slides más importantes (donde NO ahorrar tiempo):**
- **#4 GoldenEye** — el dato Martin Hollis sin experiencia FPS, vende ocho millones.
- **#2 Mario 64** — el dato "iba a ser on-rails" es viral.
- **#1 Ocarina** — el clímax. Música dinámica + #1 en todos los rankings.

### Bloque 4 · Cierre con transición (17:00 – 19:30)

- Slide del cierre con dos cards: "EL VEREDICTO" + "PRÓXIMA SEMANA".
- Frase fija de cierre (memorizar palabra por palabra):

> *"Ese es el top que la crítica del mundo te diría que tení que jugar antes de morirte. Diez juegos, diez razones. Pero hay otro top — el del bolsillo. El que paga el mercado del coleccionismo. Y casi ninguno de estos diez aparece ahí. La próxima semana revelamos los N64 más caros del planeta. Spoiler: el más caro vale más de dieciocho mil dólares, y nunca lo viste en una vitrina."*
>
> **Actualizado 2026-08-24:** cifra corregida de "nueve mil" a "dieciocho mil" — el valor sellado (`new`) de ClayFighter Sculptor's Cut en PriceCharting subió de US$9.199 a US$18.056 desde mayo. Ver `pauta-n64-top-precios.md`.

- Outro: suscribite, dejá tu top en comentarios, nos vemos la próxima semana.

---

## Anclas para cámara — un dato por juego

| Juego | Dato curioso |
|-------|--------------|
| **Ocarina of Time** | Música dinámica de Kondo según dirección de Link — primer uso adaptativo en consola. |
| **Super Mario 64** | Iba a ser on-rails. Miyamoto cambió a control libre cuando descubrió el analógico. |
| **Banjo-Kazooie** | Kirkhope inventó instrumentación dinámica por zona — bajo agua, cueva, altura. |
| **GoldenEye 007** | Martin Hollis tenía 30 años con cero experiencia en FPS. Era un experimento. |
| **Mario Kart 64** | El caparazón azul fue decisión política, no técnica — para que novatos ganaran. |
| **Super Smash Bros.** | Iwata y Sakurai lo hicieron a escondidas. Nintendo dijo sí porque ya estaba hecho. |
| **Majora's Mask** | UN AÑO de desarrollo. El sistema de 3 días nació de restricción de tiempo. |
| **Paper Mario** | Iba a ser Mario RPG 2 con Square. Cambió a estilo papel cuando Square se fue con Sony. |
| **Perfect Dark** | Primer juego en obligar Expansion Pak. Sin él el cartucho no arrancaba. |
| **Star Fox 64** | Rumble Pak gratis con el juego — caballo de Troya del rumble en consola. |

---

## Shorts derivados (mínimo 5)

### Lane Luis

1. "Mario 64 iba a ser sobre rieles" — el cambio de Miyamoto.
2. "Smash Bros. se hizo a escondidas de Nintendo" — Iwata y Sakurai.
3. "Goldeneye lo hizo un equipo sin experiencia en FPS" — Martin Hollis.
4. "Majora's Mask se hizo en UN AÑO" — restricción que definió el juego.
5. "El Rumble Pak fue gratis porque Nintendo lo necesitaba" — Star Fox 64 como caballo de Troya.

---

## Checklist antes de grabar

- [ ] Luis abre `studio/rankings/top-mundial/n64-top-mundial.html` en Chrome pantalla completa. Probar navegación con flechas.
- [ ] Memorizar la frase de cierre con transición al episodio de precios.
- [ ] Koko prepara opinión personal sobre los 10 juegos. Si no jugó alguno, decir por qué.
- [ ] Cartuchos físicos a la vista en mesa.
- [ ] Cronómetro visible. ~90 seg promedio por juego.
- [ ] Tono conversacional. NO leer los slides, USAR los slides como soporte.
- [ ] Sembrar fuerte el episodio de precios — el cliffhanger es lo que trae audiencia al próximo, sin numerarlo como "parte 2".

---

## ANEXO A — Conexión con el resto del arco

- **Episodio relacionado (no numerado como serie):** `n64-top-precios` (top precios CIB + NFR + valor colección de Koko).
- **Hermanos en el arco N64:** `n64-hardware-raro` (consolas y periféricos), `n64-no-latam` (juegos cancelados / JP only).
- **Próximos del arco:** `n64-kirkhope-rare`, `n64-nintendo-vs-playstation`, `n64-ost-bateria`.
- Tablero completo en `docs/arcos/n64.md`.

---

*RETROTARROS · pauta de episodio · documento de trabajo*
*Gen 5 · Nintendo 64 · Top Mundial*
