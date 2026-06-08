# RETROTARROS — Pauta de episodio especial (formato SAGA)

*Nostalgia + Juegos + Música*

**Especial Saga — The Legend of Zelda**

*El recorrido historico de la saga mezclado con nuestra coleccion*

Documento de trabajo · Luis Balbrigame & Koko

---

## Proposito de esta pauta

Primer episodio del **formato SAGA** del canal: se recorre la **linea principal de una franquicia juego por juego, en orden cronologico**, contando su importancia historica, y se va marcando cuales tenemos en FISICO en la coleccion (sello "EN COLECCION").

Es la mezcla que pidio Luis: **historia + coleccion**. La gracia: cuando el recorrido llega a un juego que tenemos, Luis lo muestra fisico (el momento "esta la tengo"); los que no tenemos se cuentan igual para completar la historia.

Zelda es el piloto ideal: tenemos **10 de los 16** juegos de la linea principal, repartidos en NES, SNES, N64, DS, Wii, Wii U y Switch (casi 4 decadas en el estante).

> **Formato reutilizable:** mismo esquema sirve para Mario, Metroid, Pokemon, Castlevania, etc. Generado con `scripts/top_deck.py` (cada juego es un item; el año va a la izquierda, el sello "EN COLECCION" a la derecha).

---

## Concepto del episodio — LINEA DE TIEMPO + ZOOM

HTML (`studio/saga-zelda.html`): 21 slides, generado con `scripts/saga_deck.py`. Mecanica visual (idea de Luis):

1. **Slide LINEA DE TIEMPO COMPLETA** (slide 02): se muestra la saga entera de 1986 a 2023 como una cinta horizontal con todos los juegos (box mini + año + consola + sello EN COLECCION/FALTA). "Casi 40 años de Hyrule" de un vistazo.
2. **DOS slides por juego:**
   - **(a) ZOOM a la linea de tiempo + ficha:** la cinta centrada y ampliada en el juego que toca (el nodo crece, brilla, marcador "estamos aqui"). Abajo: box grande, "LLEGAMOS A <año> · <consola>", titulo, por que importa, sello EN COLECCION. Luis dice "llegamos a 1986, a la NES... aparece The Legend of Zelda" y la imagen hace el zoom.
   - **(b) GAMEPLAY en TarroVision grande:** una TarroVision (CRT) ocupando la pantalla para correr gameplay del juego mientras se comenta brevemente. Al lado, "EL DATO" (una curiosidad corta) + sello mini EN COLECCION. Es el respiro de "ver el juego en accion".
3. **Slide BONUS** (EN LA VITRINA): remakes/remasters + Game & Watch Zelda (la edicion especial / hardware al final).
4. **Balance + cierre**.

> Flujo por juego: zoom-ficha → gameplay. En edicion se anima el zoom real entre la cinta y cada juego, y se monta el gameplay en la TarroVision (placeholder NO SIGNAL en el HTML).

**Duracion objetivo:** 24-30 minutos (37 slides: 16 juegos x 2).

---

## El recorrido (linea principal, cronologico)

| Año | Juego | Consola | En coleccion |
|-----|-------|---------|:---:|
| 1986 | The Legend of Zelda | NES | ✓ (cartucho dorado) |
| 1987 | Zelda II: The Adventure of Link | NES | — |
| 1991 | A Link to the Past | SNES | ✓ |
| 1993 | Link's Awakening | Game Boy | ✓ (remake Switch) |
| 1998 | Ocarina of Time | N64 | ✓ |
| 2000 | Majora's Mask | N64 | ✓ |
| 2001 | Oracle of Seasons / Ages | GBC | — |
| 2002 | The Wind Waker | GameCube | ✓ (HD) |
| 2004 | The Minish Cap | GBA | — |
| 2006 | Twilight Princess | GameCube / Wii | ✓ |
| 2007 | Phantom Hourglass | DS | ✓ |
| 2009 | Spirit Tracks | DS | — |
| 2011 | Skyward Sword | Wii | — |
| 2013 | A Link Between Worlds | 3DS | — |
| 2017 | Breath of the Wild | Wii U / Switch | ✓ (las dos) |
| 2023 | Tears of the Kingdom | Switch | ✓ (+ coleccionista) |

**En la coleccion:** 10 de 16. Box art real de cada uno (Wikipedia).

> La coleccion tiene ademas remakes (OoT 3D, MM 3D, TP HD, WW HD) y el Game & Watch Zelda — se pueden mostrar como bonus en sus respectivos slides.

---

## Estructura (22-28 min)

- **Cold open (0:00-0:40):** Luis con el cartucho dorado de Zelda: "Casi cuarenta años de Hyrule. Hoy recorremos la saga entera, juego por juego, y te muestro cuales tengo aca en fisico."
- **Setup (0:40-1:30):** explica el formato (cronologico + sello coleccion).
- **Recorrido (1:30-25:00):** 16 juegos, ~1:30 c/u. En los que tenemos, Luis muestra el fisico (momento coleccion). En los que no, cuenta la historia igual.
- **Balance (25:00-26:30):** 10 de 16, las consolas que cubren.
- **Cierre (26:30-28:00):** "cual es tu Zelda?" + que saga viene despues. Opcional: Koko toca un tema de Zelda.

---

## Reglas de ejecucion

- Orden cronologico ESTRICTO (es la gracia del recorrido).
- En los que tenemos: mostrar el fisico, contar como/cuando se consiguio (anecdota coleccionista).
- En los que NO tenemos: honesto ("este me falta", se vuelve wishlist).
- No spoilear finales; hablar de importancia historica, no de trama.

---

## Material visual

- [ ] Box art: ✓ ya descargadas (`studio/img/saga-zelda/`).
- [ ] Gameplay corto de cada juego (16 clips).
- [ ] Los cartuchos/cajas fisicas de los 10 que tenemos, para los planos.
- [ ] Opcional: tema de Zelda para el cierre de Koko.

---

## Estado

| Item | Estado |
|------|--------|
| HTML (`studio/saga-zelda.html`) | ✓ 20 slides + box art |
| JSON TarroBot | ✓ 16 juegos |
| Pauta MD (este) | ✓ |
| Discusion MD | ✓ |
| Gameplay + fisicos | ☐ Pendiente |

---

**Ultima actualizacion:** 2026-06-07
**Slug:** `saga-zelda`
**HTML:** `studio/saga-zelda.html`
**Discusion:** `docs/discusion-saga-zelda.md`
