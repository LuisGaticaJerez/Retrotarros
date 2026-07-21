# RETROTARROS — Pauta de episodio largo

*Nostalgia + Juegos + Música*

**Coleccion PS Vita — Un panorama por categorias**

*Generacion 8 · Sony PlayStation Vita · Recorrido coleccionista*

Documento de trabajo · Luis Balbrigame & Koko

---

## Proposito de esta pauta

Tour por la coleccion COMPLETA de **PlayStation Vita** del estudio: **91 juegos en 9 categorias**, con 3 joyas destacadas por categoria + paneos de los lomos. No es ranking, es panorama por genero (mismo formato que SNES / N64 / NES coleccion).

Angulo emocional: la Vita es **la portatil incomprendida** — hardware brutal (OLED, dual analog) que Sony abandono, pero con un catalogo de culto enorme, sobre todo en JRPG e indies. El estudio tiene 91 fisicos: una autoridad real sobre una consola que muchos no le dieron oportunidad.

Sirve como:
- Vitrina de la coleccion (autoridad sobre una consola subvalorada).
- Reivindicacion: "la Vita era increible y aca esta la prueba".
- Cierre del arco Vita (ya estan top-mundial, top-precios, archivo, vs-mundo).

> Data del inventario REAL (`data/coleccion/coleccion-retrotarros.csv`, plataforma `Sony PS Vita`). Generado con `scripts/coleccion_deck.py`.

---

## Concepto del episodio

HTML del estudio (`studio/colecciones/psvita-coleccion.html`): 23 slides. Portada → indice "PRESS START" con 9 categorias → por categoria 2 slides (paneo + 3 joyas en TarroVisiones) → hardware → balance → cierre.

**Duracion objetivo:** 24-30 minutos (catalogo grande, 91 juegos).

---

## Las 9 categorias y sus joyas

| # | Categoria | Cantidad | Joya 1 | Joya 2 | Joya 3 |
|---|-----------|----------|--------|--------|--------|
| 01 | EXCLUSIVOS / ACCION | 19 | Uncharted: Golden Abyss (2011, SCE Bend) | Gravity Rush (2012, SCE Japan) | Soul Sacrifice (2013, SCE) |
| 02 | JRPG / RPG | 14 | Persona 4 Golden (2012, Atlus) | Final Fantasy X/X-2 HD (2013, Square Enix) | Danganronpa 2 (2014, Spike Chunsoft) |
| 03 | PELEA | 11 | Ultimate Marvel vs. Capcom 3 (2011, Capcom) | Mortal Kombat (2012, NetherRealm) | Street Fighter X Tekken (2012, Capcom) |
| 04 | PLATAFORMAS / INDIE | 8 | Rayman Legends (2013, Ubisoft) | Tearaway (2013, Media Molecule) | LittleBigPlanet PS Vita (2012, Sony) |
| 05 | SHOOTER | 6 | Killzone: Mercenary (2013, Guerrilla) | Resistance: Burning Skies (2012, Nihilistic) | Call of Duty: Black Ops Declassified (2012, nStudios) |
| 06 | CARRERAS | 4 | Wipeout 2048 (2012, Studio Liverpool) | Need for Speed: Most Wanted (2012, Criterion) | ModNation Racers: Road Trip (2012, SD Studio) |
| 07 | DEPORTES | 6 | Hot Shots Golf: World Invitational (2011, Clap Hanz) | MLB 13: The Show (2013, SD Studio) | Virtua Tennis 4 (2012, Sega) |
| 08 | LEGO / FAMILIA | 17 | LEGO Marvel Super Heroes (2014, TT Games) | Minecraft: PS Vita Edition (2014, Mojang) | Angry Birds Star Wars (2013, Rovio) |
| 09 | HORROR / SIGILO | 6 | Metal Gear Solid HD Collection (2012, Konami) | Silent Hill: Book of Memories (2012, Konami) | Yomawari: Midnight Shadows (2017, NIS) |

**Total:** 91 juegos · **Joyas:** 27 (3 por categoria).

> Categorizacion derivada del CSV (genero), repartiendo el bloque gigante "Action" (46) en EXCLUSIVOS/ACCION, SHOOTER, HORROR/SIGILO y LEGO/FAMILIA para que cada categoria tenga peso propio.

---

## Bloque especial · Hardware

- **PS Vita Slim (PCH-2000)** — el modelo blanco del estudio, mas liviano.
- **Pantalla OLED (PCH-1000 FAT)** — el primer modelo, colores imbatibles para su epoca.
- **Tarjetas propietarias** — el talon de Aquiles: memorias carisimas y exclusivas (parte de por que la Vita sufrio).

---

## Estructura (24-30 min)

- **Cold open (0:00-0:40):** plano de la Vita encendida (OLED brillando). Luis: "Esta consola la mataron antes de tiempo. Y aca esta todo lo que valio la pena. 91 juegos."
- **Setup (0:40-1:30):** no es ranking, es panorama. La Vita como joya incomprendida.
- **Recorrido (1:30-26:00):** 9 categorias x ~2:40. No ahorrar en EXCLUSIVOS (Uncharted, Gravity Rush) ni JRPG (Persona 4 Golden = el juego que justifica la consola).
- **Hardware (26:00-28:00):** Slim + OLED + el drama de las memorias.
- **Balance + cierre (28:00-30:00):** 91 juegos, 9 categorias, 27 joyas.

---

## Reglas de ejecucion

- Cada categoria max 3:00. No leer los 91 juegos: paneo + 3 joyas.
- Defender la Vita sin amargura: "Sony la abandono, pero miren esto".
- No mencionar precios (eso lo cubre `psvita-top-precios`).

---

## Material visual

- [ ] 9 paneos de camara (lomos por categoria).
- [ ] 27 clips de gameplay (3 por joya).
- [ ] Foto/video Vita Slim + OLED + las memory cards.

El HTML usa placeholders `tv-noscreen`.

---

## Estado

| Item | Estado |
|------|--------|
| HTML (`studio/colecciones/psvita-coleccion.html`) | ✓ 23 slides |
| Pauta MD (este) | ✓ |
| Discusion MD | ✓ |
| Paneos + gameplay | ☐ Pendiente |

---

**Ultima actualizacion:** 2026-06-07
**Slug:** `psvita-coleccion`
**HTML:** `studio/colecciones/psvita-coleccion.html`
**Discusion:** `docs/discusion-psvita-coleccion.md`
