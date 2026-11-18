# Pauta: Los mejores juegos de película (retro-peliculas-mejores)

> Documento operativo para Claude. Diseño: `docs/superpowers/specs/2026-11-18-retro-peliculas-mejores-design.md`. Versión 1 (datos verificados, 2026-11-18). Se completa al cerrar el episodio.

## Criterio

- **Qué entra (opción A, Luis 2026-11-18):** juego que adapta una película concreta o salió atado a su estreno (live action o animada). Fuera: series de TV, cómics sin película y juegos que solo comparten universo.
- **Una entrada por película y por franquicia.** Si hay varias versiones por consola, se muestra la mejor criticada o más recordada; las otras van en notas.
- **Repetidos con rankings por consola:** tope de 2 por episodio. Hoy solo GoldenEye (N64 Top Mundial).
- **Corte de época:** hasta 2006.
- **Orden (regla 5 del diseño):** se usa la nota agregada de la versión que sale en pantalla (Metacritic o GameRankings, tratadas como equivalentes en escala de 100). Si no hay agregador (Aladdin, The Lion King) se promedia la crítica de época. Las notas se agrupan en bandas y **dentro de cada banda manda el legado** (ventas, impacto cultural, nostalgia), porque 1 a 3 puntos entre un agregador moderno y reseñas de 1993 son ruido.
  - **Banda 1 (88 o más):** GoldenEye 96, Riddick 89, Aladdin ~88.
  - **Banda 2 (84 a 87):** Super Star Wars 85, Die Hard Trilogy 86, The Return of the King 85, The Warriors 85.
  - **Banda 3 (80 a 83):** Spider-Man 2 83, The Lion King ~83, King Kong 82.

## Tabla verificada (de #1 a #10)

| # | Juego | Versión en pantalla | Año NTSC USA | Editor (desarrollador) | Película | Nota de la versión | Segunda fuente |
|---|---|---|---|---|---|---|---|
| 1 | GoldenEye 007 | N64 | 1997 (25 ago) | Nintendo (Rare) | GoldenEye (1995) | MC 96 (21 reseñas) | Wikipedia; EGM 9,5/9,5/9,5/9, GameSpot 9,8, IGN 9,7 |
| 2 | The Chronicles of Riddick: Escape from Butcher Bay | Xbox | 2004 (1 jun) | Vivendi Universal Games (Starbreeze) | The Chronicles of Riddick (11 jun 2004, la película salió 10 días después) | MC 89 (84 reseñas), GR 88,7% | PC: MC 90, 2004 dic; Wikipedia coincide |
| 3 | Disney's Aladdin | Genesis | 1993 (19 oct) | Sega (Virgin Games) | Aladdin (1992) | Sin agregador. Promedio de época ~88: GamePro 93, GameFan ~96, Mega 94, GamesMaster 95, Sega Pro 94, EGM 85, Famitsu 88, IGN 80, Mean Machines Sega 82 | Wikipedia + Sega Retro; 4 millones de copias; EGM y GamePro: mejor juego de Genesis 1993 |
| 4 | Super Star Wars | SNES | 1992 (nov) | JVC (Sculptured Software, LucasArts) | Star Wars (1977) | GR 85% (7 reseñas); reseñas de época 89 a 95 | Wikipedia; EGM 9/9/9/9, GameFan 94%, N-Force 95; EGM: mejor adaptación de película 1992 |
| 5 | Die Hard Trilogy | PS1 | 1996 (18 sep) | Fox Interactive (Probe Entertainment) | Las tres Die Hard (1988, 1990, 1995) | GR 86% (PS1) | EGM 8,75, GameSpot 9,4, IGN 7,5; más de 2 millones vendidos. Metacritic no tiene reseñas |
| 6 | The Lord of the Rings: The Return of the King | PS2 | 2003 (4 nov) | EA Games | El Señor de los Anillos: El Retorno del Rey (2003) | MC 85 (31 reseñas); Xbox 84, GC 84 | Wikipedia; IGN PS2 8,9 |
| 7 | The Warriors | PS2 / Xbox | 2005 (17 oct) | Rockstar Games | The Warriors (1979) | MC Xbox 85 (55), PS2 84 (52) | Wikipedia; GR Xbox 85,1% |
| 8 | Spider-Man 2 | Xbox / PS2 / GameCube | 2004 (29 jun) | Activision (Treyarch) | Spider-Man 2 (30 jun 2004) | MC Xbox 83 (60), PS2 80 (50), GC 80 (41) | Wikipedia; IGN Xbox 9, PS2 8,8; más de 7 millones vendidos |
| 9 | The Lion King | SNES / Genesis | 1994 (9 nov) | Virgin Interactive (Westwood Studios) | El Rey León (24 jun 1994) | Sin agregador. GameFan SNES 268/300 (89%), Nintendo Power 16,3/20, Super Play 82, Next Generation 4/5 | Wikipedia; 1,27 millones de copias de SNES en EE. UU.; unos 4,5 millones en total |
| 10 | Peter Jackson's King Kong | PS2 / Xbox / GameCube | 2005 (21 nov) | Ubisoft | King Kong (14 dic 2005) | MC PS2 82 (41), Xbox 82 (43), GC 81 (30), 360 80 | Wikipedia |

## Cambios respecto del top de partida del diseño

El diseño listaba, de #1 a #10: GoldenEye, Riddick, RotK, Warriors, King Kong, Spider-Man 2, Aladdin, Super Star Wars, Die Hard Trilogy y The Lion King. Al verificar y agrupar en bandas el orden quedó como la tabla de arriba:
- **Aladdin sube** a #3: su promedio de época (~88) es de banda 1 y su legado (4 millones de copias, mejor juego de Genesis 1993) es el más fuerte del especial.
- **Super Star Wars y Die Hard Trilogy suben** a #4 y #5: sus agregadores (85 y 86) son de banda 2, igual que RotK y Warriors, y desempata el legado.
- **King Kong baja** a #10: es el de menor nota (82), y en la banda 3 el legado de Spider-Man 2 y de The Lion King pesa más.
- **The Lion King** deja de ser el #10 por rareza y sube a #9: GameFan lo pone en 89%, pero la crítica de otros medios es más tibia (Next Generation 4 de 5, Super Play 82). Va en el borde de banda 3.
- **Aviso sobre el "EGM 31/40" de la tabla de partida:** esa cifra es de la versión Game Gear, no de SNES. Se reemplazó por las notas de SNES.

## Casos límite (para decir en cámara)

- **Riddick:** la película salió el 11 de junio de 2004 y el juego el 1 de junio de 2004 en Xbox, así que sí es un tie-in atado al estreno. Es una precuela de la película y secuela de Pitch Black. La versión de PC salió en diciembre.
- **The Warriors:** el juego (2005) adapta la película de 1979 y expande su historia (incluye misiones previas a la noche de la película). A confirmar en cámara cuánto cubre la trama original.
- **Super Star Wars:** adapta la película de 1977 con 15 años de diferencia. Entra por ser una adaptación de una película concreta; no existe una versión arcade de este juego (hubo un arcade de Star Wars vectorial en 1983, que es otro juego). Por confirmar.
- **Aladdin:** la versión de Capcom para SNES es otro juego (GR 78%, banco de reservas). La de Genesis sale en pantalla por mejor crítica; en notas va la comparación.
- **Die Hard Trilogy:** fecha NA de PS1 18 de septiembre de 1996 en Wikipedia; Metacritic la lista con 31 de diciembre de 1996 (fecha de marcador). En pantalla solo el año (1996, coinciden). Por confirmar la fecha exacta.
- **Versiones por consola:** en juegos multiplataforma de 2003 a 2005 la versión que sale en pantalla es la de mayor nota agregada, con las demás en la etiqueta de consola.

## Por confirmar antes de la grabación

- Fecha exacta NA de Die Hard Trilogy (PS1).
- Que Super Star Wars no tuvo versión arcade propia, y que Aladdin, GoldenEye, Riddick, The Warriors, King Kong, Spider-Man 2, RotK y The Lion King tampoco (todas nacieron en consola o PC; a confirmar con una fuente por juego).
- Estrenos exactos de las películas (se confirman al escribir las notas de la Tarea 5).
- Cuánta trama cubre The Warriors respecto de la película.
- El promedio ~88 de Aladdin mezcla reseñas de épocas y escalas distintas (ver tabla); es una estimación, no un agregador.

## Banco de reservas (para el posible segundo episodio)

Umbral: 75 o su equivalente en crítica de época. Hoy hay **7 con nota sobre 75** y varios por verificar; el segundo top 10 todavía no se puede armar con datos duros.

| Juego | Versión | Nota de partida | Estado |
|---|---|---|---|
| Spider-Man (2002) | Xbox | MC 79 (PS2 76, GC 76) | verificado en Wikipedia |
| Ghostbusters: The Video Game (2009) | PS3 | MC 78 (PC 74, PS2 64) | fuera del corte de 2006 |
| Disney's Aladdin (Capcom) | SNES | GR 78% | verificado en Wikipedia |
| Scarface: The World Is Yours (2006) | Xbox | MC 76 (PS2 75, Wii 71) | verificado en Wikipedia |
| Star Wars Episode I: Racer | N64 | GR 75,8% (DC 75,4) | verificado en Wikipedia |
| Indiana Jones' Greatest Adventures | SNES | GR 75,1% | verificado en Wikipedia |
| Toy Story 2: Buzz Lightyear to the Rescue | PS1 | MC 75 (N64 58, DC 57) | verificado en Wikipedia |
| Batman Returns (Konami) | SNES | sin nota | por verificar |
| Batman (Sunsoft) | NES | sin nota | por verificar |
| Jurassic Park | SNES/Genesis | sin nota | por verificar |
| RoboCop versus The Terminator | Genesis | sin nota | por verificar |
| Alien Trilogy | PS1 | sin nota | por verificar |
| The Lord of the Rings: The Two Towers | PS2 | sin nota | por verificar (la franquicia ya está con RotK; entra solo si se rompe esa regla) |
| The Godfather (2006) | PS2/Xbox | sin nota | por verificar |
| Disney's Tarzan | PS1/N64 | GR PS1/N64 71,1% (PC 82) | bajo el umbral en consola |

Fuera por nota baja (sin entrar al banco): The Incredibles (MC 62 a 64), Batman Begins (65 a 66), Shrek 2 (72), Spider-Man (2002) en GBA/PC.

## Estructura del deck (14 slides)

Portada con mosaico (gráfica nueva), divisor de intro (criterio del especial), 10 slides de juego de #10 a #1 con barra de progreso, divisor de análisis ("El cine se volvió juego") y divisor cliffhanger que teasea el especial de los peores. Cada slide de juego trae su consola propia (campo `consola` por juego, agregado a `top_deck.py` para los especiales multi-consola) y una nota oculta de 450 a 550 palabras. Slug `retro-peliculas-mejores`, carpeta `studio/specials/`, cajas en `studio/specials/img/retro-peliculas-mejores/`.

## Entregables y estado

- HTML: `studio/specials/retro-peliculas-mejores.html` (generado con `.cache/gen_retro_peliculas_mejores.py`, que no escribe pautas ni JSON).
- Discusión: `docs/discusiones/discusion-retro-peliculas-mejores.md`.
- Kit YouTube: `docs/descripciones/descripcion-retro-peliculas-mejores.md`.
- Capturas: `studio/specials/captures/retro-peliculas-mejores/` (se regeneran con `capture-slides.py`).
- Pendiente: grabación, fechas por confirmar, elegir el "Sigue con" al publicar, y decidir si hay segundo top (ver banco de reservas).
