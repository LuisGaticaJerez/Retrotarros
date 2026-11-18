# Los mejores juegos de película: diseño (2026-11-18)

Diseño corto, cerrado con Luis en chat el 2026-11-18. Cubre el primer episodio del especial; el de los peores y el segundo top de mejores quedan para sesiones aparte.

## Intención

Un ranking nuevo del canal: los mejores juegos basados en películas, de cualquier consola. Es un **especial multi-consola** (prefijo `retro-`, carpeta `studio/specials/`), no un ranking por consola, porque los rankings por consola ya existen y se repetirían. Los años son contexto, no el eje: cada slide lleva consola y año del juego, y los años sirven de hilo en intros y divisores.

## Metas, no metas y anti-metas

- **Metas:** un top 10 con crítica verificable que se vea y se lea como los demás rankings del canal (gráfica nueva, letra grande para TV, notas ocultas de unos 3 minutos por juego).
- **No metas:** no es un ranking por década (queda para una segunda fase si el formato funciona), no mezcla juegos de peores y mejores, no se numera como "Parte N".
- **Anti-metas:** que se sienta reciclado de los rankings por consola; que un juego entre solo por estar de moda y sin respaldo de crítica; que el texto en pantalla menosprecie a alguien.

## Reglas cerradas con Luis

1. **Qué cuenta como juego de película (opción A, estricta):** el juego adapta una película concreta o salió atado a su estreno, sea live action o animada. Fuera: series de TV, cómics sin película, y juegos que solo comparten universo con una franquicia (Star Wars: KOTOR, Rogue Leader).
2. **Una entrada por película y por franquicia.** Si hay varias versiones por consola, se muestra la que tiene mejor crítica o más se recuerda, y las otras van en las notas (Aladdin: Genesis en pantalla, Capcom SNES en notas; El Señor de los Anillos: solo The Return of the King).
3. **Repetidos con rankings por consola:** se permiten, con tope de 2 por episodio. Al desempatar gana el que no está en otro ranking. Un repetido lleva en las notas el ángulo de la película, no el de la consola. En este primer episodio el único repetido es GoldenEye (N64 Top Mundial).
4. **Corte de época:** hasta la generación PS2/Xbox/GameCube (2006). Alien: Isolation y similares quedan fuera.
5. **Orden:** primero cuántas listas de crítica y qué fuerza de crítica tiene el juego; después la nota agregada (Metacritic o GameRankings) cuando existe. Para 16-bit, donde casi no hay agregadores, se usan reseñas de época (EGM, Famitsu, IGN, GameSpot) y se dice en pantalla qué criterio se usó.
6. **Un episodio independiente, sin rótulo de serie.** Puede teasear otro video, no llamarlo "Parte 2" (memoria `feedback_no_numerar_episodios_como_partes`).
7. **Segundo top de mejores, condicional.** La pauta del primero deja un banco de reservas ordenado (15 a 20 juegos con sus notas). Si hay 10 con nota decente (unos 75 o su equivalente en crítica de época) se arma el segundo como episodio independiente con título propio. Hoy las reservas rondan 74 a 78, así que no se compromete todavía.
8. **Orden de trabajo:** primero Mejores, después Peores. Un episodio por sesión.

## Top 10 aprobado (de #10 a #1)

| # | Juego | Consola, año | Película | Crítica de partida (Wikipedia) |
|---|---|---|---|---|
| 1 | GoldenEye 007 | N64, 1997 | GoldenEye | MC 96 |
| 2 | The Chronicles of Riddick: Escape from Butcher Bay | Xbox, 2004 | The Chronicles of Riddick | MC 89, GR 88,7 |
| 3 | The Lord of the Rings: The Return of the King | PS2, 2003 | El Señor de los Anillos | MC 85 |
| 4 | The Warriors | PS2/Xbox, 2005 | The Warriors (1979) | MC 84/85 |
| 5 | Peter Jackson's King Kong | PS2/Xbox, 2005 | King Kong | MC 82 |
| 6 | Spider-Man 2 | PS2/Xbox/GC, 2004 | Spider-Man 2 | por confirmar |
| 7 | Disney's Aladdin (Virgin) | Genesis, 1993 | Aladdin | EGM 9/8/9/8, Famitsu 9/9/9/8 |
| 8 | Super Star Wars | SNES, 1992 | Star Wars | GR 85%, EGM 9 x4 |
| 9 | Die Hard Trilogy | PS1, 1996 | La trilogía Duro de Matar | GameSpot 9,4, EGM 8,75 |
| 10 | The Lion King | SNES/Genesis, 1994 | El Rey León | EGM 31/40, por confirmar |

La tabla de arriba es la posición de partida. Las cifras vienen de Wikipedia, que cita las fuentes: **cada nota se cruza con una segunda fuente antes de ir a pantalla**, y lo no confirmado se marca como "por confirmar". El orden final puede moverse al verificar, siempre con la regla 5.

**Reservas (banco):** Aladdin de Capcom (SNES), Star Wars Episode I: Racer, Batman Returns (Konami), Spider-Man (2002), Scarface: The World Is Yours, Ghostbusters: The Video Game, Indiana Jones' Greatest Adventures, Batman (Sunsoft, NES), Toy Story 2 (PS1).

**Casos límite a documentar en cámara:** Riddick (es un tie-in que salió con el estreno de la película) y The Warriors (adaptación fiel de una película de 1979). Hay que verificar también qué versión por consola pesa más en Spider-Man 2 y The Lion King.

## Approaches considerados

- **Especial multi-consola, dos episodios independientes (elegido).** No repite los rankings por consola y deja los años como contexto.
- **Un ranking por consola o por generación (descartado).** Ya existen y los juegos de película se repetirían.
- **Por década (segunda fase).** Los 80 casi no llenan un top de mejores (es la época de los licenciados malos), así que solo tiene sentido para los 90 y los 2000 y se decide después de probar el formato.
- **Cómo se construye:** `scripts/top_deck.py` con `generar_top(data, slug)` y `"grafica": "nueva"`. Es lo mismo que usan los demás rankings nuevos; no hay otra opción razonable.

## Cómo se construye (detalle para quien arme)

- **Slug y carpeta:** `retro-peliculas-mejores`, en `studio/specials/` por la regla `^retro-` de `scripts/_studio_layout.py`. Verificar que `generar_top` escribe ahí y que el sync a Drive lo mapea.
- **Estructura del deck:** portada con mosaico, divisor de intro (qué cuenta como juego de película y qué criterio de orden se usó), slides #10 a #1, análisis/cierre y cliffhanger que teasea el especial de los peores.
- **Reglas de ranking que siguen vigentes:** box art real NTSC USA (nunca logo ni screenshot; `scripts/fetch_boxart_wiki.py` o libretro, verificado en mosaico), letra grande para TV (`tv_grande`, no bajarla), texto en pantalla sin tildes, TarroVision sin tocar, notas ocultas de 450 a 550 palabras por slide con más información que la pantalla, datos cruzados con 2 fuentes.
- **Tono:** positivo y de nostalgia. Nada de crítica dura en pantalla; el humor, si hay, es al juego y nunca a las personas.
- **Capas de entrega:** HTML `studio/specials/retro-peliculas-mejores.html`, `docs/pautas/pauta-retro-peliculas-mejores.md` (incluye el banco de reservas y la tabla de verificación), `docs/discusiones/discusion-retro-peliculas-mejores.md`, kit `docs/descripciones/descripcion-retro-peliculas-mejores.md` (se pega también en el chat) y capturas con `capture-slides.py`.
- **Pruebas:** `python scripts/test_top_grafica.py` y `python scripts/test_top_grafica_visual.py`. No correr drivers viejos de `.cache` para probar: escriben pautas y JSON en el repo principal.
- **Cierre:** trabajar en rama y PR (nunca push directo a `master`). Push, PR, merge y sync a Drive (`sync-to-drive.ps1 -Episodios retro-peliculas-mejores` y `sync-tarrobot-to-drive.ps1 -Rapido`) solo con el dale de Luis. Dejar el repo del PC en 0/0 con `origin/master`, el estado en `HANDOFF.md` y la decisión en la bitácora.

## Lo que queda al builder

Verificar el orden final con 2 fuentes, resolver las versiones por consola, decidir los textos en pantalla, escribir las notas y el kit, y marcar como "por confirmar" lo que no se pueda cruzar. Cualquier cambio de la tabla se anota en la pauta.
