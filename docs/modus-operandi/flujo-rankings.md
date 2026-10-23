# Flujo de rankings — recetas y trampas (2026-10-21)

> Para arrancar una sesión nueva sin releer la historia. Cuando una receta cambie, actualizar este archivo en el mismo commit.

## 1. Top Precios (reforge de uno existente o nuevo)

**Reglas (CLAUDE.md, "Convención del TOP PRECIOS"):** retail #10→#1 por CIB NTSC USA, rarezas no-retail con etiqueta, un santo grial que sea el ítem más caro de todo el episodio. Precio siempre arriba a la derecha (lo hace `top_deck.py` solo con `USD ...`).

**Receta que funcionó (Dreamcast, Saturn, GameCube, Mega Drive, Vita, SNES):**
1. En PriceCharting abrir `https://www.pricecharting.com/console/<slug>?sort=highest-price` (slug: `sega-genesis`, `super-nintendo`, `playstation-vita`, etc.) con Claude in Chrome y leer la tabla con JS: `#games_table tbody tr`, `td.title a`, `td.used_price`, `td.cib_price`, `td.new_price`. Usar selectores por clase, nunca por posición (las columnas se corren si falta el precio suelto).
2. **Trampa:** el listado se ordena por precio SUELTO y trae solo 150 filas. Los juegos que solo tienen precio CIB (sin suelto) no aparecen. Verificar los juegos conocidos de tirada corta directo en su ficha.
3. **Confirmar cada candidato en su ficha** (`/game/<consola>/<slug>`): Complete, Release Date, Publisher, Description. Leer `#full-prices` y el texto `Release Date:` / `Publisher:`. Las fichas de la lista a veces difieren de la ficha (ej. Valkyrie Drive: lista 90, ficha 77).
4. **Clasificar:** excluir consolas, accesorios, bundles, lanzamientos modernos (Limited Run, Eastasiasoft, homebrew), ediciones de otra región (Asia, PAL, Japón) y juegos que en NTSC USA fueron solo digitales (Atelier Rorona Plus, Deception IV Vita). Variantes, exclusivos de alquiler, NFR y piezas de torneo van a "rarezas".
5. **Grial:** más caro que cualquier ítem. Si PriceCharting no lo lista, usar venta documentada y decirlo en las notas.
6. Box art: primero libretro (`https://thumbnails.libretro.com/<Sistema>/Named_Boxarts/<Titulo> (USA).png`), si no existe usar la imagen de la ficha de PriceCharting (`storage.googleapis.com/images.pricecharting.com/<id>/1600.jpg`; el id sale de `#product_details img`). Verificar con un mosaico antes de generar.
7. Driver en `.cache/gen_<slug>.py` con el helper `it(pos, title, ano, editor, price, img, why, nota, cue=None, **extra)` (copiar `.cache/gen_gamecube_top_precios.py`). Generar, capturar, revisar 2-3 slides.
8. Docs: pauta (tabla + rarezas + grial), discusión (con sección "Auditoría de precios (regla CANON)"), kit de YouTube (títulos, descripción con capítulos, tags, hashtags `#Coleccionismo #<Consola> #Retrogaming #Top10 #Retrotarros`, comentario fijado).
9. **Antes de tocar un ranking, verificar su estado en `data/youtube/estado-canal.json`** (publicado, programado o sin publicar). Un ranking publicado se puede rehacer solo si Luis va a regrabarlo.

**Pendiente del reforge:** auditar con esta receta los Top Precios ya publicados que no se han revisado: NES, N64, Master System, Atari 2600 y Game Boy. PS1: mirar Einhänder y Castlevania Chronicles contra el #10 (USD 350).

## 2. Infravalorados (formato nuevo, 2026-10-19)

Ranking de **calidad**, sin precios. Categoría de salida `studio/rankings/infravalorados/` (slug `<consola>-infravalorados`, regla en `scripts/_studio_layout.py`).

**Regla de orden (Luis): pesa más la crítica que el olvido.** Se ordena por la nota Metacritic, o GameRankings si no hay Metacritic. En SNES se usaron 3 niveles de fuerza de la crítica porque muchos no tienen nota agregada (también valen puestos en listas: IGN Top 100 SNES, Super Play, Nintendo Power). El olvido solo desempata. Tono siempre positivo.

**Receta:**
1. Armar ~25 candidatos de la consola (NTSC USA, no están en el Top Mundial del canal, no hace falta que estén en la colección).
2. `python scripts/wiki_reception.py "<titulo Wikipedia>" ...` → MC, GR, Famitsu, IGN (segundos, sin navegador).
3. Quedarse con 10, ordenar con la regla, anotar las reservas en la discusión.
4. Box arts (libretro o `fetch_boxart_wiki.py`).
5. Driver copiando `.cache/gen_snes_infravalorados.py` o `.cache/gen_ps1_infravalorados.py`: `items` sin `price`, `why_label` "▶ EL MEJOR CRITICADO" en el #1, `sorted([...], key=lambda x: -x["pos"])`.
6. Docs: pauta, discusión (incluye qué confirmar en cámara) y kit.

**Hechos:** SNES (Tetris Attack #1), PS1 (Wipeout XL #1) y Mega Drive (Shining Force II #1, 2026-10-22; la Genesis casi no tiene Metacritic, se usaron 3 niveles con EGM 1997, IGN 2007 y las listas de Mega/GamesRadar+). GameCube (Viewtiful Joe #1, 2026-10-22; la GameCube sí tiene Metacritic: se ordena por la nota de la versión GameCube, y en las multiplataforma cuenta solo esa; `wiki_reception.py` no lee los artículos que usan claves `MC_NGC` o `mc1`, ahí hay que extraer la nota de la plataforma a mano del wikitexto). Los box arts de Infravalorados viven en `studio/rankings/infravalorados/img/<slug>/`. Siguientes sugeridos: PS2, N64 (ya existe `n64-joyas-ocultas` como curaduría).

## 2b. Top Mundial por consola con Metacritic (PS2, Xbox; 2026-10-22)

1. Lista de la consola: `https://www.metacritic.com/browse/game/<xbox|playstation-2|...>/all/all-time/metascore/` (urllib con User-Agent Mozilla; páginas `?page=2..4`). Cada tarjeta viene tras `data-testid="filter-results"`, con título, nota y fecha.
2. Descartar por las reglas de Luis (una entrada por franquicia, sin deportes anuales, un juego va donde salió primero y no se repite si ya está en otro Top Mundial: revisar `studio/rankings/top-mundial/*.html`). Los empates de nota se resuelven por legado.
3. Cruzar con Wikipedia (`wikitexto` de `scripts/wiki_reception.py`; el título del artículo a veces es la franquicia: probar `(video game)` o `(2005 video game)`). **Trampa:** las fichas de Metacritic de juegos multiplataforma muestran la nota de otra plataforma (Half-Life 2 muestra 96 de PC, Soulcalibur II 93 de GameCube); la nota de la consola sale de la lista y del cuadro de Wikipedia. Las fechas NA difieren en 1-2 días entre fuentes: en pantalla solo el año.
4. Box arts de libretro: el índice `https://thumbnails.libretro.com/<Sistema>/Named_Boxarts/` se puede listar con urllib; verificar en mosaico.
5. Driver: copiar `.cache/gen_xbox_top_mundial.py` o el de PS2. Capturas con `capture-slides.py` y revisión en mosaico (un PNG 3x3 de 14 slides alcanza).

## 3. Sync a Drive (rápido)

- Un episodio nuevo o modificado: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/sync-to-drive.ps1 -Episodios <slug1>,<slug2>` (unos 6 s) y `... scripts/sync-tarrobot-to-drive.ps1 -Rapido` (unos 2 s).
- Barrido completo (cambios en muchos episodios, TarroDL, shorts MP4, instalador): los mismos scripts sin parámetros (~10 min).
- Siempre `git push origin master` antes, y solo con el "dale" de Luis.

## 4. Trampas conocidas (shell y herramientas)

- **Bash heredoc con apóstrofes o `\t`:** se rompe o convierte `\t` en tab. Escribir los archivos con la herramienta Write o usar strings raw de Python.
- **Commit:** `printf '%s\n' "msg" > .git/COMMIT_EDITMSG_TMP.txt && git commit -F ... && rm`. Sin `Co-Authored-By` (regla de Luis).
- **Capturas:** `PYTHONIOENCODING=utf-8 python scripts/capture-slides.py <slug>`. Al regenerar, borrar capturas sobrantes de numeraciones viejas.
- **PowerShell:** las variables no distinguen mayúsculas. Un parámetro `$Slug` choca con la variable `$slug` del script (por eso el parámetro se llama `$Episodios`). Con `-File`, `a,b` llega como un solo texto.
- **`fetch_boxart_wiki.descargar(out_dir, ...)`** guarda en `studio/img/<out_dir>/`; si pasas una ruta larga crea carpetas raras. Mover el archivo y borrar lo sobrante.
- **Claude in Chrome:** si el tab se pierde, `tabs_context_mcp` con `createIfEmpty: true`. La verificación "Un momento…" de Cloudflare en PriceCharting se resuelve sola esperando unos segundos; no se resuelve a mano ni se evade.
- **Wikipedia:** pausa de 1 s entre pedidos (429).
- **Heredoc de Python en Bash** con `from X import ...` y caracteres especiales: preferir escribir el script en un archivo.
- **Sesiones largas:** el criterio para cerrar es el de `HANDOFF.md` (seguir bajo 600.000 tokens; ver "Cuándo cambiar de sesión"). Al cerrar, seguir en una nueva leyendo `HANDOFF.md`.
- **Layouts de caja (Luis 2026-10-23):** `top_deck.py` elige solo entre `alta` (cajas verticales, hasta 340x420 al lado del título), `ancha` (cuadradas u horizontales, hasta 440x330) y `clasica` (el marco de cartucho de siempre), según la forma de la mayoría de las imágenes del ranking. Se fuerza con `"box_layout": "alta" | "ancha" | "clasica"` en el `DATA`. El título queda centrado respecto de la caja, el TarroVision ocupa el 51 % y el "por qué" conserva su letra de 32 px (la caja se achica sola si el texto es largo). **Solo para rankings nuevos o reforjados:** al regenerar un deck ya grabado o publicado hay que poner `"box_layout": "clasica"` para no cambiarle el aspecto. Las cajas necesitan resolución decente: bajar la original de Wikipedia, no la miniatura.
