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

**Hechos:** SNES (Tetris Attack #1), PS1 (Wipeout XL #1) y Mega Drive (Shining Force II #1, 2026-10-22; la Genesis casi no tiene Metacritic, se usaron 3 niveles con EGM 1997, IGN 2007 y las listas de Mega/GamesRadar+). Los box arts de Infravalorados viven en `studio/rankings/infravalorados/img/<slug>/`. Siguientes sugeridos: GameCube, PS2, N64 (ya existe `n64-joyas-ocultas` como curaduría).

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
- **Sesiones largas:** a partir de ~400.000 tokens de contexto cada paso se vuelve lento. Cerrar la sesión y seguir en una nueva leyendo `HANDOFF.md`.
