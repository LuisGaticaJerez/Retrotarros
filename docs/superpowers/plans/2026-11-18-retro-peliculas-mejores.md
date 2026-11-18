# Los mejores juegos de película: plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Armar el episodio `retro-peliculas-mejores` (HTML, pauta, discusión, kit de YouTube y capturas) con el top 10 aprobado.

**Architecture:** Se usa `scripts/top_deck.py` (`generar_top`) con `"grafica": "nueva"`, como los demás rankings nuevos. Hace falta un solo cambio de generador: que cada juego pueda traer su propia consola, porque este especial mezcla consolas y hoy `consola` es un valor único del `data`. El resto es contenido: datos verificados, cajas, notas ocultas y documentos.

**Tech Stack:** Python 3 (`top_deck.py`, `top_grafica.py`, `capture-slides.py`), Playwright/Chromium, Wikipedia y libretro para datos y cajas.

**Spec:** `docs/superpowers/specs/2026-11-18-retro-peliculas-mejores-design.md`

## Global Constraints

- Slug `retro-peliculas-mejores`; el HTML cae en `studio/specials/` (regla `^retro-` de `scripts/_studio_layout.py`). Cajas en `studio/specials/img/retro-peliculas-mejores/<slug-del-titulo>.jpg`, con el slug de `top_deck._slug`.
- Texto en pantalla sin tildes (la ñ sí) y sin crítica dura ni menosprecio. Tono positivo y de nostalgia.
- Box art real NTSC USA (nunca logo, screenshot ni afiche arcade). Sin caja: `cart-fallback`.
- Letra grande para TV activa por defecto (`tv_grande`): no bajar tamaños. TarroVision sin tocar.
- Notas ocultas: 450 a 550 palabras por slide de juego, con más información que la pantalla. Cada dato histórico o de crítica cruzado con 2 fuentes; lo no confirmado queda como "por confirmar".
- Un juego por película y por franquicia; repetidos con rankings por consola, tope de 2 (hoy solo GoldenEye). Corte de época: hasta 2006. Sin rótulo "Parte N".
- No usar `scripts/wiki_reception.py`: lleva un correo en el User-Agent y el bloqueo de privacidad lo frena. Para Wikipedia usar un cliente con User-Agent genérico (ver `recep.py` en el scratchpad de la sesión de diseño, o escribir uno igual). Wikipedia: pausa de 1 s entre pedidos; descargas de cajas con pausa de 15 s.
- Trabajar en la rama del worktree. Push, PR, merge y sync a Drive solo con el dale de Luis. Commits sin `Co-Authored-By`, sin emojis ni guiones largos. Español chileno neutro con tuteo, sin voseo, también en los kits.
- No correr drivers viejos de `.cache` (escriben pautas y JSON en el repo principal). El driver nuevo solo llama a `generar_top`.

## Review Focus

1. Un juego sin caja encontrada: el deck igual se genera (con `cart-fallback`) y la barra de progreso no se rompe. Test en Task 1.
2. Etiqueta de consola larga (`PS2 / XBOX`) que se desborda en la caja o en los chips. Test en Task 1 y revisión visual en Task 7.
3. Caja equivocada en juegos multiplataforma (afiche arcade o logo en Aladdin, Super Star Wars y The Lion King). Revisión en mosaico en Task 3.
4. Tildes o palabras de crítica dura en el texto visible. Chequeo en el driver, Task 4.
5. Posiciones duplicadas o fuera de 1 a 10, o una nota con menos de 450 o más de 550 palabras. Chequeos en el driver, Tasks 4 y 5.

---

### Task 1: Consola propia por juego en `generar_top`

**Files:**
- Modify: `scripts/top_deck.py` (en `generar_top`, las 3 llamadas a `_slide_item` y `G.slide_item`: items, rarezas y grial)
- Test: `scripts/test_top_grafica.py`

**Interfaces:**
- Produces: `it["consola"]: str` opcional en cada item. Si existe, reemplaza a `data["consola"]` en la etiqueta de la caja (`cart-console`), en los chips y en el `meta`. Sin la clave todo sale idéntico (los `golden.json` no cambian).

- [ ] **Step 1: Escribir los tests que fallan** en `scripts/test_top_grafica.py`, con las fixtures existentes (`_data_mundial`, `_generar`, `_nueva`):
  - `test_item_consola_propia_clasica`: un item con `"consola": "PS2 / XBOX"` muestra `<div class="cart-console">PS2 / XBOX</div>` y los demás conservan `data["consola"]`.
  - `test_item_consola_propia_nueva`: lo mismo con `"grafica": "nueva"`, y los chips de ese item muestran `PS2 / XBOX`.
  - `test_item_sin_caja_con_consola_propia`: un item sin imagen y con consola propia genera `cart-fallback` con esa consola en el `sub`.
- [ ] **Step 2: Correr y ver que fallan:** `python scripts/test_top_grafica.py` (los 3 tests nuevos fallan; los demás pasan).
- [ ] **Step 3: Implementar** en `generar_top`: pasar `it.get("consola", consola)` como argumento `consola` en cada llamada a `_slide_item` y `G.slide_item`. Sin tocar `_slide_item` ni `top_grafica.py`.
- [ ] **Step 4: Correr** `python scripts/test_top_grafica.py` y ver todo en verde, incluidos los hashes de `golden.json` sin cambios.
- [ ] **Step 5: Commit** `feat(top_deck): consola propia por juego (especiales multi-consola)`.

### Task 2: Verificar los datos y fijar el orden final

**Files:**
- Create: `docs/pautas/pauta-retro-peliculas-mejores.md` (primera versión: tabla verificada y banco de reservas; se completa en Task 6)

**Interfaces:**
- Produces: la tabla final de 10 filas (posición, título exacto, consola o consolas, año NTSC USA, editor, película, nota y fuentes) y el banco de reservas. Las demás tareas leen esta tabla.

- [ ] **Step 1:** Para cada uno de los 10 juegos, cruzar la nota con una segunda fuente (ficha de Metacritic, GameRankings, MobyGames o reseñas de época) además de Wikipedia. Resolver los dos "por confirmar" (Spider-Man 2 y The Lion King) y anotar qué versión por consola va en pantalla.
- [ ] **Step 2:** Confirmar año y consola de lanzamiento en EE. UU., si hubo versión arcade previa (anotarlo aunque sea "no la tuvo") y el vínculo con la película (Riddick y The Warriors son los casos límite del diseño).
- [ ] **Step 3:** Aplicar la regla de orden del diseño (crítica primero, nota agregada después) y mover posiciones si la verificación lo pide. Anotar cada cambio y su motivo en la pauta.
- [ ] **Step 4:** Armar el banco de reservas de 15 a 20 juegos con nota y fuentes, ordenado, y marcar cuántos pasan del umbral de 75 o equivalente (decide si el segundo episodio es viable).
- [ ] **Step 5: Verificación:** ningún dato de la tabla queda sin segunda fuente o sin la marca "por confirmar". Commit `docs(rankings): datos verificados de los mejores juegos de pelicula`.

### Task 3: Cajas

**Files:**
- Create: `studio/specials/img/retro-peliculas-mejores/<slug-del-titulo>.jpg` (10 archivos)

- [ ] **Step 1:** Para consolas con libretro (N64, SNES, Genesis, PS1, PS2, Xbox, GameCube) probar primero `https://thumbnails.libretro.com/<Sistema>/Named_Boxarts/<Titulo> (USA).png` y convertir a JPG; si no existe, `scripts/fetch_boxart_wiki.py` (`descargar`, ojo con el directorio de salida, ver trampas en `docs/modus-operandi/flujo-rankings.md`). Cada caja es la de la versión que sale en pantalla.
- [ ] **Step 2: Verificación visual:** armar un mosaico de las 10 y revisarlo con `Read`: cada una es la caja NTSC USA correcta, sin logo, screenshot ni afiche arcade, y pesa más de 6 kB. Reemplazar las que no cumplan.
- [ ] **Step 3: Commit** `feat(rankings): cajas del especial de juegos de pelicula`.

### Task 4: Driver y HTML

**Files:**
- Create: `.cache/gen_retro_peliculas_mejores.py` (gitignored, dentro del worktree)
- Generates: `studio/specials/retro-peliculas-mejores.html`

**Interfaces:**
- Consumes: la tabla de Task 2, las cajas de Task 3 y `it["consola"]` de Task 1. Usa `generar_top(DATA, "retro-peliculas-mejores")`.
- Produces: `DATA` con `"grafica": "nueva"`, `"consola": "VARIAS"`, `header_tag`, `doc_title`, `portada`, `intro`, `items` (10, ordenados de #10 a #1 con `sorted(..., key=lambda x: -x["pos"])`), `analisis` y `cliffhanger`. Cada item: `pos, title, ano, editor, consola, img, why, notas`.

- [ ] **Step 1:** Escribir el driver con las 14 slides esperadas: portada, intro (qué cuenta como juego de película y qué criterio de orden se usó), 10 juegos, análisis y cliffhanger que teasea el especial de los peores. Los `why` cortos (~140 caracteres o menos), con el ángulo de la película.
- [ ] **Step 2:** En el driver, antes de generar, asegurar con `assert`: posiciones únicas de 1 a 10, ninguna tilde en `portada`, `intro`, `analisis`, `cliffhanger`, `why`, `title` ni `consola` (letras á é í ó ú), y ninguna de las palabras `peor`, `malo`, `horrible`, `basura` en el texto visible.
- [ ] **Step 3:** Correr el driver. Verificar que se genera `studio/specials/retro-peliculas-mejores.html` con 14 `<section class="slide`, `grafica` nueva (mosaico y barra) y que `git status` no muestra archivos fuera del worktree.
- [ ] **Step 4: Commit** del HTML (`feat(rankings): deck de los mejores juegos de pelicula`).

### Task 5: Notas ocultas

**Files:**
- Create: `.cache/notas_retro_peliculas.py` (gitignored; `NOTAS = {pos: ([lineas], cue)}`, más las notas de la portada)
- Modify: `.cache/gen_retro_peliculas_mejores.py` (importar `NOTAS` antes de `DATA`)

- [ ] **Step 1:** Escribir por juego 450 a 550 palabras que den más información de la que sale en pantalla: la película (estreno, quién la hizo), cómo se hizo el juego, la crítica con sus dos fuentes, versiones por consola, anécdotas y un cue de reacción. GoldenEye lleva además el ángulo de la película porque ya está en N64 Top Mundial. Lo no cruzado queda como "por confirmar".
- [ ] **Step 2:** En el driver, contar las palabras de cada bloque con `assert 450 <= n <= 550`. Regenerar el HTML y revisar en modo lectura (`?notas=1`) que el panel muestre todo.
- [ ] **Step 3: Commit** `feat(rankings): notas ocultas de los mejores juegos de pelicula`.

### Task 6: Pauta, discusión y kit de YouTube

**Files:**
- Modify: `docs/pautas/pauta-retro-peliculas-mejores.md` (denso: tabla final, criterio, banco de reservas, casos límite, qué confirmar en cámara)
- Create: `docs/discusiones/discusion-retro-peliculas-mejores.md` (conversacional para Luis y Coco: preguntas guía, decisiones pendientes, si vale el segundo top)
- Create: `docs/descripciones/descripcion-retro-peliculas-mejores.md` (sigue `docs/canal/guia-youtube-viral.md`: título, descripción con CTA y bloque "Sigue con", hashtags según la receta de la sección 4, tags bajo 500 caracteres, capítulos con timestamps estimados de 3 minutos por juego y la nota "ajustar al editar", comentario fijado)

- [ ] **Step 1:** Escribir los tres archivos con el mismo slug. Las descripciones llevan tildes y ñ correctas.
- [ ] **Step 2: Verificación:** buscar voseo (`sabés|tenés|querés|decime|fijate|vos `) en los tres archivos y corregir; contar caracteres de los tags (menos de 500) y hashtags (4 o 5).
- [ ] **Step 3:** Pegar el kit completo en el chat para Luis. Commit `docs(rankings): pauta, discusion y kit de los mejores juegos de pelicula`.

### Task 7: Capturas y pruebas

**Files:**
- Generates: `studio/specials/captures/retro-peliculas-mejores/*.png` (gitignored)

- [ ] **Step 1:** `PYTHONIOENCODING=utf-8 python scripts/capture-slides.py retro-peliculas-mejores`. Esperado: 14 PNG de 1920x1080.
- [ ] **Step 2:** Revisar las 14 en mosaico: sin desbordes en los `why`, etiqueta de consola completa, TarroVision intacto, barra de progreso sin superposición, mosaico de portada con las cajas correctas.
- [ ] **Step 3:** `python scripts/test_top_grafica.py` y `python scripts/test_top_grafica_visual.py`: ambos en verde.
- [ ] **Step 4:** Si se retocó algo, regenerar HTML y capturas y commitear.

### Task 8: Cierre

**Files:**
- Modify: `HANDOFF.md`, `docs/modus-operandi/bitacora-decisiones.md` (entrada del 2026-11-18 con las reglas del especial), y el inventario `docs/canal/inventario-contenido.md` solo si lista specials armados sin subir

- [ ] **Step 1:** Anotar en HANDOFF el estado (episodio armado, qué falta: grabar, y el de los peores como siguiente sesión) y en la bitácora la decisión y las reglas del diseño.
- [ ] **Step 2:** Commit en la rama. Avisarle a Luis el SHA y pedir el dale para: push de la rama, PR (nunca push directo a `master`), `sync-to-drive.ps1 -Episodios retro-peliculas-mejores` y `sync-tarrobot-to-drive.ps1 -Rapido`, y el merge.
- [ ] **Step 3:** Con el dale: hacer lo anterior, después `get_status` del PR con las herramientas `ccd_pr`, y tras el merge dejar el repo del PC en 0/0 con `origin/master` (`git pull --rebase`).
