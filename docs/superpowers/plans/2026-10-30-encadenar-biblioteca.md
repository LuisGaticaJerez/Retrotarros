# Encadenar la biblioteca de videos largos: plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Agregar a cada descripción de video largo un bloque "Sigue con" más el enlace a la lista de su formato, con una herramienta segura (prueba por defecto, respaldo, confirmación) y dejar los kits nuevos con el mismo bloque.

**Architecture:** Un script nuevo `scripts/youtube_enlazar.py` con funciones puras (elegir destino, armar y insertar el bloque) y un CLI calcado de `scripts/youtube_aplicar.py`. Las funciones puras se prueban sin red; el CLI usa la API de YouTube solo para leer y escribir descripciones.

**Tech Stack:** Python 3, google-api-python-client (ya usado en `youtube_aplicar.py`), pruebas sin pytest al estilo de `scripts/test_resena_kit.py`.

**Spec:** `docs/superpowers/specs/2026-10-30-encadenar-biblioteca-design.md`

## Global Constraints

- Español chileno neutro con tuteo; la descripción lleva tildes (es prosa pública de YouTube). Sin emojis en el código y los commits.
- Solo cambia la descripción: título, etiquetas, idioma y categoría quedan como están (la API reemplaza el snippet completo, hay que reenviar `tags`, `defaultLanguage` y `categoryId` tal como vienen).
- Modo prueba por defecto; `--aplicar` guarda respaldo y pide escribir `SI`. Nunca se escribe sin el dale de Luis.
- Cuota: 50 unidades por video, unas 2.900 de 10.000 diarias para 58 videos.
- Sin números de cuenta, claves ni tokens en archivos del repo.
- Datos de entrada ya existentes: `data/youtube/listas-2026-10-30.json` (listas con `titulo`, `id`, `videos`), `data/youtube/horas-por-video-2026-10-30.json` (`video`, `estimatedMinutesWatched`), `data/youtube/inventario-2026-10-29.json` (títulos).

## Review Focus

- Volver a correr la herramienta no duplica el bloque (idempotencia).
- Una lista con un solo video (Sagas) no genera destino ni bloque.
- Descripción vacía o sin línea de hashtags: el bloque queda al final sin romper nada.
- Un video nuevo que no está en el archivo de horas (God of War): se trata como 0 minutos, no falla.
- La lista "G- OLD" no genera enlace de lista.
- La actualización no borra etiquetas ni idioma del video.

---

### Task 1: Funciones puras y sus pruebas

**Files:**
- Create: `scripts/youtube_enlazar.py` (solo las funciones puras en esta tarea)
- Test: `scripts/test_youtube_enlazar.py`

**Interfaces:**
- Produces:
  - `etiqueta_lista(titulo_lista: str) -> str | None`: devuelve el texto de la línea de la lista ("Todas las reseñas", "Todos los rankings", "Todas las colecciones", "Todos los Abriendo el tarro", "Todos los specials", "Todas las sagas") buscando por palabra clave en el título sin distinguir mayúsculas ("rese", "ranking", "coleccion", "abriendo", "special", "saga"); `None` para "G- OLD" o cualquier título desconocido.
  - `elegir_destinos(listas: list[dict], minutos: dict[str, int], titulos: dict[str, str]) -> dict[str, dict]`: para cada video de cada lista con `etiqueta_lista` no nula y al menos 2 videos, devuelve `{"destino_id", "destino_titulo", "lista_id", "lista_etiqueta"}`; el destino es el video de la misma lista con más minutos que no sea el propio (los empates se resuelven por orden en la lista; los ausentes de `minutos` cuentan 0).
  - `bloque_enlaces(d: dict) -> str`: dos líneas, `Sigue con: <destino_titulo> https://youtu.be/<destino_id>` y `<lista_etiqueta>: https://www.youtube.com/playlist?list=<lista_id>`.
  - `insertar_bloque(desc: str, bloque: str) -> str`: inserta el bloque antes de la línea final de hashtags (la detecta con `RESTO_RE` importado de `youtube_aplicar`), separado por una línea en blanco; si `desc` ya contiene `Sigue con:` la devuelve sin cambios; si no hay línea de hashtags lo agrega al final.

- [ ] **Step 1: Write the failing tests** en `scripts/test_youtube_enlazar.py` (funciones `test_*` más `main()`; patrón de `scripts/test_resena_kit.py`):
  - `test_etiqueta_lista`: "Retroreseñas" → "Todas las reseñas"; "Rankings" → "Todos los rankings"; "Colecciones RetroTarros" → "Todas las colecciones"; "G- OLD" → `None`.
  - `test_elegir_destinos_mejor_distinto_del_propio`: lista de 3 videos con minutos 10, 50, 30; el video de 50 apunta al de 30, los otros dos apuntan al de 50.
  - `test_elegir_destinos_lista_de_uno_se_omite` y `test_elegir_destinos_video_sin_horas_cuenta_cero` (el ausente puede ser destino solo si el resto tiene 0).
  - `test_bloque_enlaces` con las dos líneas exactas y los enlaces `youtu.be` y `playlist?list=`.
  - `test_insertar_bloque_antes_de_hashtags`, `test_insertar_bloque_idempotente` (dos llamadas = una), `test_insertar_bloque_sin_hashtags` y `test_insertar_bloque_descripcion_vacia`.
- [ ] **Step 2: Run** `python scripts/test_youtube_enlazar.py`. Expected: FAIL (ImportError, funciones no definidas).
- [ ] **Step 3: Implement** las cuatro funciones en `scripts/youtube_enlazar.py` con las firmas de Interfaces; `etiqueta_lista` con un mapa de palabra clave a texto.
- [ ] **Step 4: Run** `python scripts/test_youtube_enlazar.py`. Expected: `OK <n> pruebas`.
- [ ] **Step 5: Commit** `git add scripts/youtube_enlazar.py scripts/test_youtube_enlazar.py` con mensaje `feat(youtube): funciones del bloque Sigue con para las descripciones`.

### Task 2: CLI con respaldo, prueba y aplicación

**Files:**
- Modify: `scripts/youtube_enlazar.py` (agrega `main()` y la propuesta)
- Test: `scripts/test_youtube_enlazar.py`

**Interfaces:**
- Consumes: Task 1 (`elegir_destinos`, `bloque_enlaces`, `insertar_bloque`); de `youtube_aplicar`: `servicio()`, `leer_snippets(yt, ids)`.
- Produces:
  - `cargar_entradas(repo: Path) -> tuple[list[dict], dict[str, int], dict[str, str]]`: lee los tres archivos de datos (listas, horas por video, títulos del inventario) y devuelve lo que pide `elegir_destinos`.
  - `construir_propuesta(snips: dict[str, dict], destinos: dict[str, dict]) -> list[tuple[str, str, str]]`: lista de `(video_id, descripcion_actual, descripcion_nueva)` solo para videos con cambio.
  - `cuerpo_actualizacion(video_id: str, sn: dict, descripcion: str) -> dict`: cuerpo para `videos().update(part="snippet")` con título, categoría, `tags` y `defaultLanguage` tal como vienen en `sn` y la descripción nueva.
  - CLI: `python scripts/youtube_enlazar.py [--solo id1,id2] [--aplicar]`; sin `--aplicar` muestra antes y después; con `--aplicar` guarda `data/youtube/respaldo-api-<fecha-hora>.json` y pide escribir `SI`.

- [ ] **Step 1: Write the failing tests**: `test_construir_propuesta_omite_videos_que_ya_tienen_el_bloque`, `test_cuerpo_actualizacion_conserva_tags_e_idioma` (el cuerpo trae los `tags` y `defaultLanguage` del original y solo cambia la descripción).
- [ ] **Step 2: Run** `python scripts/test_youtube_enlazar.py`. Expected: FAIL.
- [ ] **Step 3: Implement** las tres funciones y `main()` copiando el flujo de `youtube_aplicar.main()` (respaldo, modo prueba, confirmación `SI`, corte ante error de cuota); mostrar por video el título, el destino elegido y la descripción final.
- [ ] **Step 4: Run** `python scripts/test_youtube_enlazar.py` (Expected: OK) y luego `python scripts/youtube_enlazar.py --solo jSBcr_VcPWw,itup-OCeeTU` (Expected: modo prueba, dos videos con el bloque, "Modo prueba: no se escribió nada"; si el token caducó, Luis vuelve a autorizar en el navegador).
- [ ] **Step 5: Commit** `feat(youtube): CLI para enlazar videos desde las descripciones (modo prueba por defecto)`.

### Task 3: Kits nuevos con el bloque

**Files:**
- Modify: `scripts/resena_kit.py` (esqueleto del kit) y `scripts/test_resena_kit.py`
- Modify: `CLAUDE.md` (una línea en "Kit de publicación YouTube automático")

**Interfaces:**
- Consumes: el esqueleto actual de `scripts/resena_kit.py` (`crear`, `revisar_kit`).
- Produces: el esqueleto trae la línea `Todas las reseñas: https://www.youtube.com/playlist?list=<id de Retroreseñas>` y una línea `Sigue con: [REDACTAR: video sugerido al publicar]`; `--revisar` exige que el marcador se haya reemplazado antes de pegar el kit.

- [ ] **Step 1: Write the failing test** en `scripts/test_resena_kit.py`: el esqueleto contiene `Sigue con:` y la línea de la lista; `revisar_kit` reporta el marcador pendiente.
- [ ] **Step 2: Run** `python scripts/test_resena_kit.py`. Expected: FAIL.
- [ ] **Step 3: Implement** el cambio en `crear` y `revisar_kit`; tomar el id de la lista Retroreseñas de `data/youtube/listas-2026-10-30.json`.
- [ ] **Step 4: Run** `python scripts/test_resena_kit.py`, `python scripts/test_resena_lint.py` y `python scripts/test_resena_grafica.py`. Expected: todas OK.
- [ ] **Step 5: Commit** `feat(resenas): el kit de publicacion incluye el bloque Sigue con`.

### Task 4: Despliegue y medición (con Luis)

**Files:**
- Modify: `docs/canal/rendimiento/README.md` (fila de seguimiento al medir)
- Create: `docs/canal/rendimiento/analisis-encadenado-AAAA-MM-DD.md` (cuando haya medición)

- [ ] **Step 1:** Correr la herramienta en modo prueba sobre los 58 videos y mostrarle a Luis tres ejemplos y la tabla video a destino. Esperar su dale.
- [ ] **Step 2:** Con el dale, `python scripts/youtube_enlazar.py --aplicar --solo <5 ids de prueba>`; verificar en Studio que las descripciones salieron bien y que las etiquetas siguen.
- [ ] **Step 3:** Con el segundo dale, aplicar al resto; guardar el respaldo y registrar el commit.
- [ ] **Step 4:** Entregar a Luis la lista de qué enlazar en tarjetas y en las 3 pantallas finales que faltan (Street Fighter 2, Zombies Ate My Neighbors, colección de SNES).
- [ ] **Step 5:** A las dos semanas, correr la consulta de minutos de videos largos desde RELATED_VIDEO, PLAYLIST y END_SCREEN y compararla con la base (243 h, 23 h y 3 h); guardar el informe y su fila en el seguimiento.
