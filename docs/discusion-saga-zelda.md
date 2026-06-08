# Discusion · Especial Saga Zelda

Documento de trabajo: el "detras de escena". NO es la pauta.

---

## El formato SAGA (nuevo, idea de Luis)

Recorrido historico de una franquicia, juego por juego en orden cronologico, **mezclado con la coleccion**: se marca cuales tenemos en fisico (sello "EN COLECCION") y cuales no. La gracia es el doble eje: divulgacion historica + flex coleccionista + honestidad ("este me falta").

Es distinto a:
- **Coleccion** (panorama por genero de UNA consola).
- **Top mundial/precios** (ranking).
- **Especiales de personajes** (glorias navales, cuadrilla, padres).

Aca el hilo es la FRANQUICIA a traves del tiempo y las consolas.

**Reutilizable:** Mario, Metroid, Pokemon, Castlevania, Mega Man, Sonic, Final Fantasy... cualquier saga con linea cronologica clara. Se cruza el CSV de la coleccion para marcar lo que tenemos.

---

## Por que Zelda de piloto

Porque la coleccion de Zelda del estudio es BRUTAL: 17 entradas en el CSV, 10 de los 16 mainline en fisico, desde el cartucho dorado de NES hasta Tears of the Kingdom coleccionista, cubriendo NES, SNES, N64, DS, 3DS, Wii, Wii U, Switch y hasta el Game & Watch. Da autoridad real para hacer el recorrido.

---

## Que entra en "linea principal"

Decidimos los **16 mainline canonicos** (de The Legend of Zelda 1986 a Tears of the Kingdom 2023). Quedan FUERA a proposito:
- **Remakes/HD** (OoT 3D, MM 3D, WW HD, TP HD, Link's Awakening Switch): se mencionan en el slide del original, no como entrada aparte (sino se infla la lista).
- **Spin-offs** (Hyrule Warriors, Link's Crossbow Training, los CD-i): podrian ser un episodio aparte "los Zelda raros".
- **Four Swords / multiplayer**: fuera del hilo principal.

Asi el recorrido es limpio y la audiencia sigue el hilo sin perderse.

---

## Decision de los "owned"

Cruzamos el CSV (`data/coleccion/coleccion-retrotarros.csv`, 17 entradas Zelda). Marcamos owned los mainline que tenemos en CUALQUIER forma (original o remake), porque lo importante es que Luis puede mostrar algo fisico de ese juego:
- Link's Awakening = owned via remake Switch.
- Wind Waker = owned via HD (Wii U).
- Breath of the Wild = owned x2 (Wii U y Switch) — buen dato.

Los 6 que faltan (Zelda II, Oracle, Minish Cap, Spirit Tracks, Skyward Sword, A Link Between Worlds) se cuentan igual y se vuelven wishlist honesto.

---

## Riesgos

| Riesgo | Mitigacion |
|--------|------------|
| 16 juegos se hace largo | Ritmo agil, 1:30 c/u; los owned llevan el peso (mostrar fisico). |
| Debate de "cual es mainline" | Aclarar el criterio al inicio; remakes/spin-offs fuera a proposito. |
| Sonar a lista de Wikipedia | El gancho es la coleccion fisica + anecdotas de como se consiguio cada uno. |

---

## Decisiones de armado (2026-06-07)

1. Formato SAGA nuevo, generado con `top_deck.py`: año a la izquierda (badge_text), sello "EN COLECCION" a la derecha (campo `price`), box art auto.
2. 16 mainline cronologicos; remakes/spin-offs fuera del hilo.
3. Balance: 10 de 16 en fisico, 7+ consolas.
4. Box art real de Wikipedia en `studio/img/saga-zelda/`.

---

**Ultima actualizacion:** 2026-06-07
**Pauta asociada:** `docs/pauta-saga-zelda.md`
**HTML:** `studio/saga-zelda.html`
