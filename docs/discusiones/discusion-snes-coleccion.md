# Discusion editorial · `snes-coleccion`

> Documento de decisiones que se tomaron al armar el episodio. Lectura
> obligatoria antes de grabar para no abrir debates resueltos.

---

## 0. Reforge 2026-11-10: que cambia respecto del video publicado

Version reforjada de la coleccion SNES (el video original salio el 25 de mayo de 2026). Mismo catalogo, 9 categorias y 27 joyas; cambia como se ve y se corrigieron datos.

- **Grafica nueva** (`"grafica": "nueva"`): cajas reales de las 27 joyas (edicion NTSC USA de SNES, revisadas una por una), letra grande para TV, TarroVision 16:9 en el paneo y 4:3 en el triple, balance con barras por categoria y capa de notas (tecla N): en cada paneo la lista completa de juegos de la categoria (nueva: antes no existia) y en cada triple editor, desarrollador, genero y estado en la coleccion.
- **El catalogo es el del CSV** (`data/coleccion/coleccion-retrotarros.csv`, export de GameEye): 110 juegos, 3 consolas y 1 accesorio. El deck publicado no guardaba que juego iba en que categoria, asi que se **reconstruyo el reparto** respetando los conteos publicados (32, 17, 14, 12, 10, 9, 8, 5 y 3). Los juegos "de frontera" quedaron asi: Taz-Mania, Earthworm Jim, Toy Story, Lion King y Chuck Rock en Plataformas; Tick, Batman Forever, Battletoads & Double Dragon y La Muerte y Regreso de Superman en Beat 'em up; Addams Family Values en Aventura / RPG; Jungle Strike, Joe & Mac y Super Pinball en Arcade; Mega Man X en Accion. Si Luis quiere mover alguno, se cambia en `data/colecciones/snes-coleccion.json` y se regenera (los conteos de cada categoria tienen que seguir sumando 110).
- **Datos corregidos:**
  - **Anos en NTSC USA** (cruzados con Wikipedia, fechas de Norteamerica): Super Mario World 1991 (decia 1990, fecha de Japon), A Link to the Past 1992 (decia 1991), Mystical Ninja 1992 (decia 1991), F-Zero 1991 (decia 1990) y Wild Guns 1995 (decia 1994). Los otros 22 se confirmaron tal cual.
  - **Chip de editor = editor real segun el CSV:** Donkey Kong Country, Killer Instinct, Super R-Type, Super Mario RPG y Super Tennis son de Nintendo (decian Rare, Irem, Square y Tonkin House); Mortal Kombat II y NBA Jam T.E. son de Acclaim (decian Midway); Aero Fighters, de Tecmo (decia Video System). X-Men: Mutant Apocalypse va como Capcom: el CSV dice Avalon Hill, que parece un error del export y queda anotado.
  - **Balance:** la fila 2 ahora trae CONSOLAS (3) y EDITOR (Nintendo, 22 juegos de la coleccion, contado del CSV). Las cifras del balance se calculan desde las categorias.
  - El cierre del deck publicado decia "panorama N64" (error de copia); ahora el cierre es generico como el del resto de las colecciones.
- **Hardware (decision tomada por mi, a confirmar con Luis):** el deck publicado tenia una slide de **perifericos** (Super Scope y Super Game Boy) que el generador no soporta. En vez de perderla, el slide de hardware muestra las 4 piezas que el CSV tiene como consola o accesorio: Super Nintendo, SNES Donkey Kong Set, SNES Classic Edition y Super Game Boy. **La Super Scope fisica no esta en el CSV** (solo sus juegos: Battle Clash, Bazooka Blitzkrieg y Metal Combat van en Arcade; Super Scope 6 en Puzzle). Si la bazuca esta en el estudio, se puede sumar como quinta tarjeta; si no, se menciona en el paneo de Arcade (la capa de notas ya lo dice).
- **Hardware sin fotos todavia:** las 4 tarjetas salen con la placa "FOTO DEL EQUIPO". Fotos propias: `hw-super-nintendo.jpg`, `hw-snes-donkey-kong-set.jpg`, `hw-snes-classic-edition.jpg`, `hw-super-game-boy.jpg` en `studio/colecciones/img/snes-coleccion/`.
- **Pendiente de elegir:** el video del bloque "Sigue con" del cierre (campo `proximo`). Y que pasa con el video original de mayo (el con mas vistas de las colecciones).
- Se quitaron de esta discusion frases del documento original que no tenian respaldo (precio de Chrono Trigger, juegos "descartados" que no estan en el CSV, recuerdos personales atribuidos a Luis o Coco, "la coleccion personal").

---

## 1. Por que panorama y no ranking

SNES fue el piloto del formato "coleccion por generacion". La audiencia engancha mas con **vitrina + conversacion** que con un top numerado, y el episodio funciona como ancla: despues, cuando hablemos de un cartucho puntual, ya lo vieron en la coleccion.

No es un top: se avisa al comienzo ("esto NO es un ranking, es la coleccion completa").

---

## 2. Por que 9 categorias y no otras

Se descartaron:

- **Por region** (NTSC / PAL / JP): demasiado tecnico para la audiencia casual.
- **Cronologico por ano de salida:** pierde el patron visual del paneo.
- **Por desarrollador:** atomiza demasiado, varias categorias quedarian con 1 o 2 titulos.
- **Por puntuacion:** ya lo cubren `snes-top-mundial` y `snes-top-precios`.

| # | Categoria | Titulos | Por que |
|---|-----------|--------:|---------|
| 1 | Plataformas | 32 | El genero reina del SNES: abre con peso. |
| 2 | Lucha | 17 | Conversacion garantizada (SF II, MK II, Killer Instinct). |
| 3 | Deportes | 14 | Cantidad razonable, separa del bloque de accion. |
| 4 | Accion | 12 | Contra, Star Wars y X-Men: material visual fuerte. |
| 5 | Arcade | 10 | Shooters y juegos de bazuca, distinto a accion pura. |
| 6 | Aventura / RPG | 9 | Zelda y Mario RPG. |
| 7 | Beat 'em up | 8 | Subgenero con identidad propia. |
| 8 | Puzzle | 5 | Chica pero diversa. |
| 9 | Carreras | 3 | Pocas, pero con Mario Kart y F-Zero. |

**Orden:** descendente por cantidad. Plataformas (32) abre con peso; Carreras (3) cierra como "chica pero todos brillan".

---

## 3. Joyas: criterios de seleccion

3 por categoria. Criterios: reconocimiento universal, material visual fuerte (se nota en 8 segundos de gameplay) y que Luis y Coco tengan algo que decir.

| Categoria | Joyas (ano NTSC USA · editor) |
|---|---|
| Plataformas | Super Mario World (1991) · Donkey Kong Country (1994) · Yoshi's Island (1995) |
| Lucha | Street Fighter II (1992) · Mortal Kombat II (1994) · Killer Instinct (1995) |
| Deportes | NBA Jam T.E. (1995) · ISS Deluxe (1995) · Super Tennis (1991) |
| Accion | Contra III (1992) · Super Star Wars (1992) · X-Men: Mutant Apocalypse (1994) |
| Arcade | Super R-Type (1991) · Wild Guns (1995) · Aero Fighters (1994) |
| Aventura / RPG | A Link to the Past (1992) · Super Mario RPG (1996) · Mystical Ninja (1992) |
| Beat 'em up | Final Fight (1991) · Captain Commando (1995) · Batman Returns (1993) |
| Puzzle | Tetris 2 (1994) · Wario's Woods (1994) · Kirby's Avalanche (1995) |
| Carreras | Super Mario Kart (1992) · F-Zero (1991) · RPM Racing (1991) |

Ganchos para conversar (no son guion, son puntos de partida):

- **Plataformas:** DKC y los graficos pre-renderizados de Rare contra la estetica dibujada a mano de Yoshi's Island.
- **Lucha:** Street Fighter II en arcade contra su version SNES; en Mortal Kombat II, la sangre en la version de SNES (el primer Mortal Kombat de SNES salio censurado); Killer Instinct tambien es de Rare, como DKC.
- **Deportes:** el grito de NBA Jam; ISS Deluxe es de la saga que despues fue Pro Evolution Soccer.
- **Accion:** Contra III como cima del run-and-gun de Konami; Super Star Wars tiene la trilogia completa en la coleccion (los tres cartuchos); X-Men: Mutant Apocalypse divide opiniones.
- **Arcade:** Wild Guns como el "no sabia que existia". Aca van tambien tres de los juegos de la Super Scope.
- **Aventura / RPG:** Chrono Trigger y EarthBound **no estan en la coleccion** (confirmado en el CSV). Hay que decirlo con honestidad en la grabacion: la coleccion es la que tenemos, no el catalogo ideal.
- **Beat 'em up:** Final Fight y Captain Commando son ports de arcades de Capcom; Batman Returns es el beat 'em up de Konami basado en la pelicula.
- **Puzzle:** Tetris 2, Wario's Woods y Kirby's Avalanche; Super Scope 6 tambien cuenta aqui.
- **Carreras:** el Mode 7 de F-Zero y Mario Kart; RPM Racing es de Silicon & Synapse, el estudio que despues fue Blizzard.

---

## 4. Bloque de hardware · que decimos y que no

**Lo que SI:**
- Contar la pieza que tenemos: la consola, el pack con Donkey Kong Country, la SNES Classic Edition y el Super Game Boy.
- Del Super Game Boy: corre los cartuchos de Game Boy en la tele (conecta con el universo Game Boy).
- Si la Super Scope esta en el estudio, mostrarla y conectarla con Battle Clash, Bazooka Blitzkrieg, Metal Combat y Super Scope 6.

**Lo que NO:**
- Precios de mercado (eso es de `snes-top-precios`).
- Comparativas tecnicas: es coleccionismo visual, no review.
- Afirmar que tenemos la Super Scope si no esta en la mesa.

---

## 5. Cierre y "Sigue con"

El cierre dice: "Cuentanos cual fue tu favorita... Suscribete para no perderte lo que viene en el canal". Generico a proposito: no se nombra la siguiente consola. El video de "Sigue con" se elige al publicar (el de mas horas del mismo formato).

---

## 6. Riesgos y como mitigarlos

| Riesgo | Mitigacion |
|--------|------------|
| 9 categorias casi identicas pueden aburrir | Variar el tono de Luis y Coco por categoria; reservar la mejor anecdota para Plataformas, Lucha y Aventura / RPG. |
| La audiencia espera un ranking y se decepciona | Aviso explicito al inicio: "esto NO es un ranking, es la coleccion completa". |
| Faltan paneos grabados | El HTML funciona con placeholders. Plan B: foto fija del slide de joyas. |
| Un cartucho no esta en la mesa | Decirlo con honestidad y mostrarlo en foto. |

---

## 7. Reglas inmutables aplicadas

- **TarroVisiones vacias:** la guia para edicion va en la capa de notas. Sin tildes en el HTML, sin emojis en titulos o labels visibles.
- **Chileno neutro con tuteo** en pauta y discusion. La coleccion es de **Retrotarros** (el canal), no de una persona.

---

## 8. Material a grabar (checklist resumido)

- [ ] 9 paneos de camara (uno por categoria), 15-25 seg cada uno.
- [ ] 27 clips de gameplay (3 por categoria).
- [ ] Hardware en mesa: SNES, pack Donkey Kong, SNES Classic y Super Game Boy (y la Super Scope, si esta).
- [ ] Fotos de las 4 piezas para las tarjetas.

---

*Discusion original cerrada 2026-05-21. Reforge con grafica nueva: 2026-11-10.*
