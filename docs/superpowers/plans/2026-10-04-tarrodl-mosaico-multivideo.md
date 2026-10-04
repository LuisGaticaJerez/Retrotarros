# TarroMosaico (mosaico multi-video en TarroDL) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Agregar a TarroDL una pestaña TarroMosaico que arma un solo clip mosaico de duración total fija con trozos intercalados de varios videos del disco, con vista previa en línea de tiempo antes de crearlo.

**Architecture:** Planificador puro `plan_multi` (reparto entre videos, posiciones, intercalado) usado igual por la vista previa y por el render. El render es un job `mosaic` en el pool `clips` con una sola pasada de ffmpeg (`-filter_complex_script`, una entrada `-ss -t -i` por trozo). La UI suma una barra de pestañas y una pantalla nueva en el mismo `index.html`.

**Tech Stack:** Python 3.14 solo librería estándar (`unittest` para pruebas), ffmpeg/ffprobe externos, HTML/JS vanilla sin librerías.

**Spec:** `docs/superpowers/specs/2026-10-04-tarrodl-mosaico-multivideo-design.md`

## Global Constraints

- Solo librería estándar de Python; yt-dlp/ffmpeg/ffprobe se llaman como programas externos (como hoy).
- Límites: 2 a 12 videos; total `MOSAIC_MIN_SEC, MOSAIC_MAX_SEC = 60, 900`; trozo de 10 a 60 s y `<= total`; `share` en {`parejo`, `proporcional`}; `seed` entero `>= 0`; resolución en {720, 1080}.
- Orden final intercalado (v1, v2, v3... y vuelta a v1); cronológico dentro de cada video. `k = total // piece` trozos, cada uno dura `p = total / k` (nunca menos de `piece`), suma exacta `total`.
- Misma semilla, mismo plan: la vista previa y el render usan el mismo `resolve_mosaic_request`.
- Salida: `<carpeta de clips>/<nombre>.mp4`, nombre por defecto `mosaico`; si existe, `<nombre>_2`, `_3`...; nunca `_clipN`; nunca pisar archivos (`-n`).
- Normalización por trozo: escala con barras a 1920x1080 o 1280x720, `setsar=1`, 30 fps, audio estéreo 48 kHz; un trozo sin audio lleva silencio (`anullsrc`).
- Filtro siempre por `-filter_complex_script <archivo temporal>`; el temporal se borra al terminar o cancelar.
- Cancelar borra el mp4 a medias y el temporal; un mosaico terminado no se toca.
- Textos de UI en español chileno neutro con tuteo, sin emojis ni guiones largos. Nombres de archivo siempre con `textContent`, nunca `innerHTML`.
- Commits locales sin firma `Co-Authored-By`. No hacer push: el push va solo con el "dale" de Luis.

## Review Focus

Entradas que el spec insinúa y que ninguna prueba de las tareas "felices" cubriría; cada línea tiene su prueba en la tarea que se indica.

1. Nombres de archivo con espacios, tildes, `ñ`, corchetes, paréntesis y apóstrofe (ej. `Juego ñandú [test] (1).mp4`): no deben romper ffprobe, ffmpeg ni la UI. (Tarea 3)
2. El mismo video agregado dos veces con distinta escritura de ruta (barras `/` vs `\`, mayúsculas): cuenta como duplicado. (Tarea 2)
3. Un video más corto que un trozo, o con sección de menos de un trozo: recibe 0 trozos, sigue en la lista y los trozos pasan a los otros; no rompe el plan. (Tarea 1)
4. Video vertical (celular, 720x1280) mezclado con horizontales: sale con barras laterales dentro de 16:9, sin deformarse. (Tarea 3)
5. Un archivo que desaparece entre la vista previa y "Crear mosaico", y cancelar un mosaico que aún espera turno en la cola: error claro con el nombre del archivo, y ningún archivo creado. (Tarea 3)

## File Structure

- Modify `tools/tarrodl/tarrodl.py`: constantes `MOSAIC_*`, `plan_multi`, `validate_mosaic_params`, `clean_mosaic_name`, `probe_video`, `resolve_mosaic_request`, `mosaic_filter`, `unique_name`, endpoints `api_probe`, `api_session_files`, `api_pickvideos`, `api_mosaic_plan`, `api_mosaic`, entradas nuevas en `ROUTES`. Sigue el estilo del archivo (funciones `api_*` planas, `ApiError` con mensajes en español sin tildes).
- Modify `tools/tarrodl/ui/index.html`: barra de pestañas, sección `#tabMosaic`, CSS nuevo y JS de TarroMosaico (bloque propio al final del `<script>`).
- Create `tools/tarrodl/tests/common.py`: aislar config/log/carpetas en un temporal, generar videos sintéticos con ffmpeg `lavfi`, servidor HTTP de prueba.
- Create `tools/tarrodl/tests/test_mosaic_plan.py` (Tarea 1), `tests/test_mosaic_api.py` (Tarea 2), `tests/test_mosaic_render.py` (Tarea 3).
- Modify `docs/modus-operandi/bitacora-decisiones.md` y el spec (Tareas 2 y 6).

Correr pruebas desde `D:\Recursos Retrotarros\repo\tools\tarrodl`: `python -m unittest discover -s tests -v`.

---

### Task 1: Planificador `plan_multi` y validación

**Files:**
- Modify: `tools/tarrodl/tarrodl.py` (después de `plan_section`, cerca de la línea 753)
- Create: `tools/tarrodl/tests/common.py`, `tools/tarrodl/tests/test_mosaic_plan.py`

**Interfaces:**
- Produces:
  - `MOSAIC_MIN_SEC, MOSAIC_MAX_SEC = 60, 900`; `MOSAIC_MIN_VIDEOS, MOSAIC_MAX_VIDEOS = 2, 12`; `MOSAIC_HEIGHTS = (720, 1080)`; `MOSAIC_SHARES = ("parejo", "proporcional")`.
  - `validate_mosaic_params(n_videos: int, total: int, piece: int, share: str, seed: int, height: int) -> None` (lanza `ApiError` con mensaje en español).
  - `plan_multi(videos: list[dict], total: int, piece: int, share: str, seed: int) -> dict`. Cada video: `{"file": str, "duration": float, "a": float, "b": float}`. Retorna `{"pieces": k, "seg": p, "lanes": [{"file", "duration", "range": [a, b], "starts": [float, ...]}], "sequence": [{"video": int, "start": float, "at": float}, ...]}` con inicios absolutos, `lanes` en el orden de entrada y `sequence` en el orden final con `at` = instante acumulado dentro del clip.
  - `tests/common.py`: `sys.path` apunta a `tools/tarrodl`; `import tarrodl` expuesto.

- [ ] **Step 1: Crear `tests/common.py`** con solo lo mínimo de esta tarea: inserta el directorio padre en `sys.path` y exporta `tarrodl`. Las utilidades de aislamiento y videos sintéticos se agregan en la Tarea 2.

- [ ] **Step 2: Escribir las pruebas fallidas en `tests/test_mosaic_plan.py`** (`unittest.TestCase`, helper `V(dur, a=0, b=None, name="v")` que arma un dict de video):
  - `test_suma_exacta_y_cantidad`: 5 videos de 3600 s, total 300, piece 15 → `pieces == 20`, `seg == 15.0`, `len(sequence) == 20`, `abs(sequence[-1]["at"] + seg - 300) < 1e-6`.
  - `test_seg_nunca_menor_que_piece`: total 300, piece 40 → `pieces == 7`, `seg > 40`, `seg * pieces == 300` (tolerancia 1e-6).
  - `test_sin_solapes_dentro_de_cada_video`: para cada lane, `starts` ordenados y `starts[i+1] - starts[i] >= seg - 1e-6`, todos dentro de `range` (`a <= s` y `s + seg <= b + 1e-6`).
  - `test_intercalado`: 3 videos, total 90, piece 10 → `[s["video"] for s in sequence][:6] == [0, 1, 2, 0, 1, 2]`; dentro de cada video los `start` crecen en la secuencia.
  - `test_parejo_reparte_igual_y_sobrante_a_las_secciones_largas`: 3 videos (3600, 1800, 600 s), `pieces == 10` → conteos `[4, 3, 3]` (el sobrante de 1 va al de sección más larga).
  - `test_proporcional_sesga_al_largo`: mismos 3 videos, `share="proporcional"` → el conteo del primero es estrictamente mayor que el del tercero.
  - `test_video_corto_cede_sus_trozos`: videos (3600, 3600, 20 s), piece 15, total 150 → el tercero queda con `<= 1` trozo, la suma sigue siendo `pieces`.
  - `test_video_mas_corto_que_un_trozo_recibe_cero`: videos (3600, 3600, 8 s), piece 15, total 150 → `lanes[2]["starts"] == []` y la suma es `pieces` (Review Focus 3).
  - `test_no_caben_error_claro`: 2 videos de 100 s, total 300 → `ApiError` y `"no alcanzan"` en el mensaje.
  - `test_semilla`: `seed=0` dos veces → resultados idénticos y trozos centrados en su ranura; `seed=7` dos veces → idénticos entre sí y distintos a `seed=0`; con `seed=7` siguen sin solaparse.
  - `test_validate_mosaic_params`: 1 video, 13 videos, total 59, total 901, piece 9, piece 61, piece mayor que total, share `"x"`, seed `-1`, height 480 → cada uno lanza `ApiError`; el caso `(2, 300, 15, "parejo", 0, 1080)` no lanza.

- [ ] **Step 3: Correr las pruebas y verificar que fallan**
  Run: `python -m unittest tests.test_mosaic_plan -v` (desde `tools/tarrodl`)
  Expected: errores `AttributeError: module 'tarrodl' has no attribute 'plan_multi'` / `validate_mosaic_params`.

- [ ] **Step 4: Implementar `validate_mosaic_params`** en `tarrodl.py` con los límites de Global Constraints; mensajes del estilo de `validate_clip_params` (ej. `"El mosaico lleva entre 2 y 12 videos."`).

- [ ] **Step 5: Implementar `plan_multi`** en `tarrodl.py` siguiendo la sección "Planificador" del spec. Piezas que el spec no fija y que quedan decididas aquí:
  - `k = total // piece`, `p = total / k`; capacidad de cada video `cap = floor((b - a) / p)`; si `sum(cap) < k` lanza `ApiError("Los videos no alcanzan para N min sin repetir material. Amplia secciones, agrega videos o baja el largo total.")`.
  - Asignación con helper interno `_allocate(k, weights, caps) -> list[int]`: reparte `k` por cuota entera + sobrante por resto mayor (en `parejo` los pesos son todos iguales y el desempate del sobrante va por sección más larga y luego por orden de entrada; en `proporcional` el peso es `b - a`); si alguno supera su capacidad se le fija en `cap` y el exceso se vuelve a repartir entre los que tienen capacidad libre, repitiendo hasta que no haya excesos.
  - Un video con `m` trozos divide su sección en `m` ranuras iguales de ancho `w = (b - a) / m`; el margen libre de cada ranura es `w - p`; `seed == 0` pone el trozo a `margen / 2`; `seed > 0` usa `random.Random(f"{seed}:{indice_video}")` y `uniform(0, margen)` por trozo.
  - `sequence` por rondas: turno `t` toma el trozo `t` de cada video que aún tenga, en orden de lista.

- [ ] **Step 6: Correr las pruebas y verificar que pasan**
  Run: `python -m unittest tests.test_mosaic_plan -v`
  Expected: todas `ok`.

- [ ] **Step 7: Commit**
  ```bash
  git add tools/tarrodl/tarrodl.py tools/tarrodl/tests/common.py tools/tarrodl/tests/test_mosaic_plan.py
  git commit -m "feat(tarrodl): planificador del mosaico multi-video con reparto parejo o proporcional y orden intercalado"
  ```

---

### Task 2: Videos de entrada y vista previa por API

**Files:**
- Modify: `tools/tarrodl/tarrodl.py` (después de `plan_multi`; rutas en `ROUTES` línea ~1113)
- Modify: `tools/tarrodl/tests/common.py`
- Create: `tools/tarrodl/tests/test_mosaic_api.py`
- Modify: `docs/superpowers/specs/2026-10-04-tarrodl-mosaico-multivideo-design.md` (tabla de endpoints)

**Interfaces:**
- Consumes: `plan_multi`, `validate_mosaic_params` (Tarea 1); `probe_duration(ffprobe, src) -> float`, `has_audio(fp, src) -> bool`, `resolve_range(body, duration) -> tuple[float, float]`, `need_tool`, `out_base`, `clips_base`, `slugify`, `PICK_PREAMBLE`, `VIDEO_EXTS`, `NOWIN` (existentes).
- Produces:
  - `norm_path(p: str) -> str`: `os.path.normcase(os.path.abspath(p.strip().strip('"')))`.
  - `probe_video(src: Path) -> dict` con `{"duration": float, "audio": bool}`, cacheado en `PROBE_CACHE` por `(str(src), mtime_ns, size)`.
  - `clean_mosaic_name(raw: object) -> str`: vacío o `None` → `"mosaico"`; si no, `slugify(raw, 60)`.
  - `resolve_mosaic_request(body: dict) -> dict`: valida y devuelve `{"videos": [{"file","duration","a","b","audio"}], "total": int, "piece": int, "share": str, "seed": int, "height": int, "name": str, "plan": dict}` donde `plan` es el resultado de `plan_multi`. Entrada `body`: `{"videos": [{"file", "range_start"?, "range_end"?}], "total_sec", "piece_sec", "share"?="parejo", "seed"?=0, "height"?=1080, "name"?}`.
  - Rutas: `POST /api/probe` `{"files": [...]}` → `{"videos": [{"file","name","duration","audio"}]}` (falla con 400 y nombre del archivo si alguno no sirve); `POST /api/mosaic_plan` → `plan` de `resolve_mosaic_request` más `"total"`; `GET /api/session_files` → `{"files": [{"file","name","size","mtime"}]}` (videos de `out_base()` no recursivo, sin `.temp.`, más recientes primero, máximo 50); `POST /api/pickvideos` `{"start"?}` → `{"files": [...]}` o `{"cancelled": true}`.
  - `parse_picked(stdout: str) -> list[str]`: una ruta por línea, filtra vacíos y extensiones fuera de `VIDEO_EXTS`.

- [ ] **Step 1: Ampliar `tests/common.py`** con: `isolate(tmp: Path)` (apunta `tarrodl.CONFIG_DIR/CONFIG_FILE/LOG_FILE` a un temporal, `out_base`/`clips_base` a `tmp/dl` y `tmp/clips`, llama `setup_logging`), `make_video(path, seconds, size="320x240", fps=30, audio=True)` que genera con `ffmpeg -f lavfi -i testsrc2=...` (más `sine` si hay audio, `libx264 -preset ultrafast`), y `start_server() -> (base_url, call)` con un `ThreadingHTTPServer` en puerto 0 y la función `call(path, body=None)` que manda `X-Token` (mismo patrón que `scratchpad/test_queue.py`).

- [ ] **Step 2: Escribir las pruebas fallidas en `tests/test_mosaic_api.py`** (`setUpClass`: aislar, generar 3 videos sintéticos de 40/60/90 s a 320x240 más uno de `Juego ñandú [test] (1).mp4`):
  - `test_probe_devuelve_duracion_y_audio`: `/api/probe` con 2 archivos → duraciones ≈ 40 y 60 (±1) y `audio == True`; con un archivo sin audio → `audio == False`.
  - `test_probe_archivo_inexistente_400_con_nombre`: mensaje contiene el nombre del archivo.
  - `test_probe_acepta_nombres_raros`: el archivo con ñ/corchetes/paréntesis se lee bien (Review Focus 1).
  - `test_plan_ok`: 3 videos, `total_sec=60`, `piece_sec=10`, `seed=0` → 200, `len(sequence) == 6`, `lanes` con las 3 rutas.
  - `test_plan_respeta_rango_por_video`: con `range_start=10, range_end=30` en el primer video, todos sus `starts` están en `[10, 30]`.
  - `test_plan_mismos_parametros_mismo_plan`: dos llamadas idénticas devuelven JSON igual; con `seed=3` difiere de `seed=0`.
  - `test_duplicados_normalizados`: el mismo archivo con `/` y con `\`, y con otra capitalización, cuenta como duplicado → 400 (Review Focus 2).
  - `test_validaciones`: 1 video → 400; 13 → 400; extensión `.txt` → 400; `total_sec` fuera de rango → 400; `height` 480 → 400; `share` inválido → 400.
  - `test_session_files_lista_videos_recientes_primero_y_sin_temporales`: crear en `out_base()` un `.mp4`, uno `x.temp.mp4` y un `.txt` → solo aparece el primero, ordenado por mtime descendente.
  - `test_parse_picked`: `"C:\\a.mp4\r\n\r\nC:\\b.txt\r\nC:\\c.MKV\r\n"` → `["C:\\a.mp4", "C:\\c.MKV"]`.
  - `test_probe_cache_no_vuelve_a_medir`: monkeypatch de `tarrodl.probe_duration` con un contador; dos `probe_video` del mismo archivo → 1 llamada; tras tocar el mtime del archivo → 2 llamadas.

- [ ] **Step 3: Correr y ver que fallan**
  Run: `python -m unittest tests.test_mosaic_api -v`
  Expected: fallos por rutas y funciones inexistentes (404 `ruta desconocida` o `AttributeError`).

- [ ] **Step 4: Implementar** `norm_path`, `PROBE_CACHE`/`probe_video`, `clean_mosaic_name`, `resolve_mosaic_request` (usa `norm_path` para duplicados, `resolve_range(video_dict, duration)` por video, `validate_mosaic_params`, `plan_multi`; cada error de archivo nombra el archivo), `api_probe`, `api_mosaic_plan`, `api_session_files`, `PICK_VIDEOS_SCRIPT` (copia de `PICK_VIDEO_SCRIPT` con `$d.Multiselect = $true`, título "Elige los videos para el mosaico" e imprime `$d.FileNames` una por línea), `parse_picked` y `api_pickvideos` (mismo patrón que `api_pickvideo`, devuelve `{"files": parse_picked(stdout)}`). Registrar `("POST","probe")`, `("POST","mosaic_plan")`, `("GET","session_files")`, `("POST","pickvideos")` en `ROUTES`.

- [ ] **Step 5: Actualizar el spec**: agregar la fila `/api/probe` a la tabla de endpoints ("mide duración y audio de cada archivo para armar las barras desde/hasta al agregarlo").

- [ ] **Step 6: Correr todas las pruebas**
  Run: `python -m unittest discover -s tests -v`
  Expected: todas `ok` (Tareas 1 y 2).

- [ ] **Step 7: Commit**
  ```bash
  git add tools/tarrodl docs/superpowers/specs/2026-10-04-tarrodl-mosaico-multivideo-design.md
  git commit -m "feat(tarrodl): API del mosaico multi-video, probe de archivos, vista previa y selector multiple"
  ```

---

### Task 3: Render del mosaico (job `mosaic`)

**Files:**
- Modify: `tools/tarrodl/tarrodl.py` (después de `api_mosaic_plan`; ruta en `ROUTES`; `import tempfile` arriba)
- Create: `tools/tarrodl/tests/test_mosaic_render.py`

**Interfaces:**
- Consumes: `resolve_mosaic_request`, `clean_mosaic_name`, `plan_multi` (Tareas 1-2); `new_job`, `spawn(job, fn, pool="clips")`, `stream(cmd, job, on_line)`, `check_cancel`, `CLEANUPS`, `delete_files`, `need_tool`, `clips_base`, `ApiError`.
- Produces:
  - `mosaic_filter(sequence: list[dict], audio: list[bool], seg: float, height: int) -> str`: texto del filtro para `-filter_complex_script`. `sequence[i]["video"]` indexa `audio` (audio por video); la entrada `i` de ffmpeg corresponde a `sequence[i]`. Salidas etiquetadas `[v]` y `[a]`. Por entrada: `scale=W:H:force_original_aspect_ratio=decrease,pad=W:H:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30,setpts=PTS-STARTPTS`; audio con `aresample=48000` + `aformat=sample_rates=48000:sample_fmts=fltp:channel_layouts=stereo` + `asetpts=PTS-STARTPTS`, o `anullsrc=r=48000:cl=stereo,atrim=duration=<seg>` con el mismo `aformat` si el video no tiene audio; cierre `concat=n=K:v=1:a=1[v][a]`. `W:H` = 1920:1080 o 1280:720.
  - `unique_name(out_dir: Path, name: str, ext: str = ".mp4") -> Path`: `name.mp4`, luego `name_2.mp4`, `name_3.mp4`...
  - `api_mosaic(body: dict) -> dict` (mismo `body` que `/api/mosaic_plan`): resuelve y valida **antes** de crear el job (errores de archivo salen como 400 con nombre), crea el job `kind="mosaic"` en el pool `clips` y devuelve `{"job": id}`. `result` final: `{"dir": str, "file": str, "count": 1}`. Registrar `("POST","mosaic")`.

- [ ] **Step 1: Escribir pruebas fallidas en `tests/test_mosaic_render.py`**
  - `test_mosaic_filter_estructura`: con 3 entradas (la 2.ª sin audio), la salida contiene exactamente 3 `scale=1920:1080`, un `anullsrc` y termina con `concat=n=3:v=1:a=1[v][a]`; con `height=720` usa `1280:720`.
  - `test_unique_name`: carpeta vacía → `mosaico.mp4`; con `mosaico.mp4` y `mosaico_2.mp4` existentes → `mosaico_3.mp4`.
  - Integración con ffmpeg real (`setUpClass` genera: A 320x240@30 con audio 45 s; B 640x360@25 con audio 60 s; C 320x240@30 **sin audio** 50 s; D vertical 360x640@30 con audio 50 s; E `Juego ñandú [test] (1).mp4` 320x240 con audio 50 s):
    - `test_mosaico_mixto_dura_lo_pedido`: videos A, B, C, D, `total_sec=60`, `piece_sec=10`, `height=720` → job `done` (poll de `/api/job?id=`), el mp4 de `clips_base()` mide `60 ± 0.5` s con `ffprobe`, `1280x720`, `r_frame_rate` `30/1`, un stream de video y uno de audio con `sample_rate=48000` y `channels=2`.
    - `test_vertical_queda_con_barras`: genera su propio mosaico con D (vertical) y A, `height=720`; la salida mide `1280x720` y en el instante `at` de un trozo de D (`ffmpeg -ss <at + 1> -frames 1`, rawvideo gris) la columna x=0 es negra (luma < 20) y el centro no (Review Focus 4).
    - `test_nombre_con_caracteres_raros`: E + A + B con `name="Mi Mosaico ñ"` → `mi-mosaico-n.mp4` existe y el job termina `done` (Review Focus 1).
    - `test_nombre_repetido_agrega_sufijo`: dos mosaicos seguidos con el mismo `name` → existen `x.mp4` y `x_2.mp4`.
    - `test_cancelar_borra_parcial_y_temporal`: lanzar un mosaico de 900 s de total con 12 entradas (videos largos sintéticos de 600 s con `testsrc2` a 1280x720 para que tarde), esperar `percent > 0`, `POST /api/cancel`, esperar `cancelled`; no queda ningún `.mp4` en `clips_base()` ni archivo del filtro en el temporal.
    - `test_cancelar_en_cola_no_crea_nada`: con el pool `clips` ocupado por un primer mosaico largo, el segundo queda `queued`; cancelarlo → `cancelled` y su `unique_name` no existe (Review Focus 5).
    - `test_archivo_desaparece_antes_de_crear`: preview OK, se borra un video, `POST /api/mosaic` → 400 y el mensaje contiene el nombre del archivo; no se crea job (Review Focus 5).
    - `test_error_de_ffmpeg_borra_parcial`: monkeypatch de `tarrodl.need_tool` para devolver un `ffmpeg` falso que sale con código 1 tras crear el archivo → job `error` y sin archivo.

- [ ] **Step 2: Correr y ver que fallan**
  Run: `python -m unittest tests.test_mosaic_render -v`
  Expected: fallos por funciones y ruta inexistentes.

- [ ] **Step 3: Implementar `mosaic_filter` y `unique_name`** según Interfaces y volver a correr solo las pruebas unitarias (`test_mosaic_filter_estructura`, `test_unique_name`): `ok`.

- [ ] **Step 4: Implementar `api_mosaic`** replicando el patrón de `api_clips` (líneas ~820-904): comando `ffmpeg -hide_banner -loglevel error -nostats -progress pipe:1 -n` + por cada elemento de `sequence` `-ss <start:.3f> -t <seg:.3f> -i <archivo>`, luego `-filter_complex_script <tmp>`, `-map [v] -map [a]`, `-c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart <salida>`. Detalles decididos:
  - Archivo del filtro: `tempfile.mkstemp(suffix=".ffgraph")` escrito en UTF-8; `CLEANUPS[job["id"]] = lambda: delete_files([salida, tmp])`.
  - Progreso: `out_time_us / 1e6 / total` en `j["percent"]`; `text = "Armando mosaico (K trozos de N videos, recodifica)..."`.
  - Si `stream(...)` devuelve distinto de 0: borrar parcial y temporal, `ApiError` con las últimas 3 líneas del log, igual que `api_clips`.
  - Éxito: borrar el temporal, `j["text"] = f"Listo: {salida.name} ({fmt_len(total)}) en {out_dir}"` (`fmt_len` ya existe) y `j["result"] = {"dir", "file", "count": 1}`.
  - `unique_name` se calcula dentro del `work` del job (no al encolar) para que dos mosaicos en cola con el mismo nombre no choquen.

- [ ] **Step 5: Correr todas las pruebas**
  Run: `python -m unittest discover -s tests -v`
  Expected: todas `ok`. Si `test_cancelar_borra_parcial_y_temporal` queda flaky por el tiempo de arranque, subir la duración de los videos sintéticos, no bajar la verificación.

- [ ] **Step 6: Commit**
  ```bash
  git add tools/tarrodl
  git commit -m "feat(tarrodl): render del mosaico multi-video en una sola pasada de ffmpeg con cancelar y progreso"
  ```

---

### Task 4: Pestañas y pantalla TarroMosaico (videos, parámetros y vista previa)

**Files:**
- Modify: `tools/tarrodl/ui/index.html`

**Interfaces:**
- Consumes: `/api/probe`, `/api/pickvideos`, `/api/session_files`, `/api/mosaic_plan` (Tarea 2); helpers JS existentes `$`, `api`, `fmtClock`, `parseClock`, `fmtLen`, `stemOf`, `lsGet`, `lsSet`.
- Produces (para la Tarea 5): objeto global `MOS = {videos: [], seed: 0, plan: null, job: null, jobId: null}`; función `mosRequestBody() -> object` (body de `/api/mosaic_plan` y `/api/mosaic`); función `mosaicReady() -> boolean`; el contenedor `#mosJob` reservado para la tarjeta de progreso.

- [ ] **Step 1: Barra de pestañas.** Debajo del `<header>`, `<nav id="tabs">` con dos botones `data-tab="dl"` ("TARRODL") y `data-tab="mosaic"` ("TARROMOSAICO"). Todo el contenido actual del `<main>` queda en `<div id="tabDl">`; la pantalla nueva vive en `<div id="tabMosaic" class="hide">` dentro del mismo `<main>`. `showTab(name)` alterna `hide`, marca la pestaña activa y guarda `lsSet("tarrodl.tab", name)`; al cargar se restaura (por defecto `dl`). CSS nuevo siguiendo `.btn`/`.card` (borde inferior magenta en la activa).

- [ ] **Step 2: Lista de videos.** Sección `card` "01 · VIDEOS" con botones "AGREGAR VIDEOS" (`api("pickvideos", {})`, sin resultado si `cancelled`) y "DESCARGADOS" (despliega la lista de `api("session_files")` con checks y un botón "AGREGAR LOS MARCADOS"). Al agregar, `api("probe", {files})` entrega duración y audio; se ignoran rutas ya presentes (comparar con `.toLowerCase()` y `/`→`\`). Cada fila (`<div class="mrow">` armada con `createElement`/`textContent`): número de turno, nombre, duración, sliders desde/hasta con texto editable (misma mecánica que `secInit/secShow/secFromSlider/secFromText`, escrita como funciones `mv*` que operan sobre la fila, no sobre una tarjeta), botones subir/bajar (reordenan `MOS.videos` y el número de turno) y quitar. Una fila cuya medición falló se muestra marcada en magenta y bloquea el botón crear. Si hay menos de 2 videos el texto de ayuda dice "Agrega al menos 2 videos."

- [ ] **Step 3: Parámetros.** Sección "02 · PARÁMETROS": slider de largo total (60 a 900 s, paso 15, valor mostrado con `fmtLen`), slider de trozo (10 a 60 s), grupo de radios reparto (`parejo` / `proporcional`), select de resolución (1080p / 720p), campo de nombre (placeholder `mosaico`), botón "REGENERAR REPARTO" (suma 1 a `MOS.seed`) y enlace "volver al reparto centrado" (`MOS.seed = 0`). Valores por defecto: total 300, trozo 15, parejo, 1080, seed 0; los parámetros (sin videos) se recuerdan en `localStorage "tarrodl.mosaic"`.

- [ ] **Step 4: Vista previa.** Sección "03 · VISTA PREVIA". `mosRequestBody()` arma `{videos: [{file, range_start?, range_end?}], total_sec, piece_sec, share, seed, height, name}` (rangos solo si el usuario los acortó). `scheduleMosPlan()` con debounce de 350 ms y contador `mosSeq` para descartar respuestas viejas; cualquier cambio de la lista o de los parámetros la dispara. Dibujo: una `.tl` por video (reutilizar el CSS existente `.tl`, `.dim`, `i`) con color propio por video (paleta magenta/cyan/amarillo/verde/morado repetida) y los trozos en `lanes[i].starts` con ancho `seg / duration`; debajo, la franja de la secuencia final con un bloque por trozo del color de su video y el instante `at` (`fmtClock`) bajo cada corte (si son más de 30 trozos, solo cada 2.º o 3.º rótulo para que no se amontonen). Línea resumen: "20 trozos de 15 s, 4 por video, 5:00". Los errores del backend (ej. "no alcanzan...") se muestran en `#mosMsg`, en rojo, sin `alert`, y limpian el dibujo. Un video con 0 trozos se muestra con una nota "sin trozos" en su fila.

- [ ] **Step 5: Verificar en el navegador del panel con una instancia aislada.**
  Run: `python tarrodl.py --no-browser --port 8771` con `APPDATA` apuntando a un temporal (como se hizo para la cola) y videos sintéticos creados con `tests/common.py`; abrir `http://127.0.0.1:8771/`, pestaña TarroMosaico.
  Expected, verificado por lectura de página y capturas: agregar 3 videos muestra 3 filas con duración; mover "hasta" de un video cambia la línea de tiempo en menos de 1 s; "Regenerar reparto" cambia las posiciones; `proporcional` cambia los conteos; con 1 video sale "Agrega al menos 2 videos."; con rango muy corto sale el mensaje de que no alcanzan; la pestaña elegida se recuerda al recargar; sin errores en consola (`read_console_messages`) y sin tocar la pestaña TarroDL. Detener el servidor de prueba y volver el viewport a `desktop` al terminar.

- [ ] **Step 6: Commit**
  ```bash
  git add tools/tarrodl/ui/index.html
  git commit -m "feat(tarrodl): pestaña TarroMosaico con lista de videos, parametros y vista previa en linea de tiempo"
  ```

---

### Task 5: Crear el mosaico desde la UI (progreso, cancelar, abrir)

**Files:**
- Modify: `tools/tarrodl/ui/index.html`

**Interfaces:**
- Consumes: `MOS`, `mosRequestBody()`, `mosaicReady()`, `#mosJob` (Tarea 4); `POST /api/mosaic`, `POST /api/cancel`, `GET /api/jobs?ids=`, `POST /api/open` (`{path}`), `showProg`, `ensureFolder("clips")`, `joinPath`, `cancelJob`.
- Produces: botón `#btnMosaic` "CREAR MOSAICO"; tarjeta de progreso dentro de `#mosJob`.

- [ ] **Step 1: Botón crear.** Al final de la sección 03, `#btnMosaic` habilitado solo si `mosaicReady()` (≥2 videos medidos, plan válido, sin job activo propio). Al pulsar: `ensureFolder("clips")` (si no la eligió aún, abre el selector; si cancela, mensaje en `#mosMsg`), luego `api("mosaic", mosRequestBody())`; guarda `MOS.jobId` y muestra `#mosJob`. Los 400 del backend (incluido "archivo X no existe") van a `#mosMsg`.

- [ ] **Step 2: Progreso.** Tarjeta con `.prog` (misma estructura que las barras de las tarjetas), texto, meta, botón CANCELAR (`cancelJob(MOS.jobId, btn)`). El `poll()` global incorpora `MOS.jobId` a la lista de ids mientras esté activo y actualiza `MOS.job` (extender el poll existente sin romper el de las tarjetas, y llamar a un `renderMosJob()`); estados `queued` ("En cola, puesto N", con CANCELAR), `running`, `done`, `error`, `cancelled`. `renderMosJob` usa `showProg(box, j.text, j.percent, j.meta, j.state === "error", ...)`.

- [ ] **Step 3: Terminado.** Si `done`: botones "VER VIDEO" (`api("open", {path: joinPath(r.dir, r.file)})`, que abre el explorador con el archivo seleccionado) y "ABRIR CARPETA DE CLIPS" (`api("open", {path: r.dir})`); `#btnMosaic` vuelve a habilitarse (puede crear otro, con el nombre se agregará `_2`). Si `error` o `cancelled`: texto del job y botón "REINTENTAR" que repite `api("mosaic", mosRequestBody())`.

- [ ] **Step 4: Verificar en el navegador con la instancia aislada (puerto 8771).**
  Expected: con 3 videos sintéticos, total 60 s y trozo 10 s → CREAR MOSAICO muestra barra avanzando y termina en "Listo: mosaico.mp4"; `ffprobe` del archivo da ≈ 60 s; segundo clic crea `mosaico_2.mp4`; un mosaico largo (900 s de total) se cancela a medias y no deja archivos en la carpeta de clips; con dos mosaicos seguidos el segundo muestra "En cola, puesto 1" y se puede cancelar; la pestaña TarroDL no cambia su comportamiento (agregar un link falso sigue dando su tarjeta). Consola sin errores. Detener servidor y volver viewport a `desktop`.

- [ ] **Step 5: Commit**
  ```bash
  git add tools/tarrodl/ui/index.html
  git commit -m "feat(tarrodl): crear el mosaico desde TarroMosaico con progreso, cancelar y abrir resultado"
  ```

---

### Task 6: Regresión, bitácora y cierre

**Files:**
- Modify: `docs/modus-operandi/bitacora-decisiones.md`

**Interfaces:**
- Consumes: todo lo anterior; suites existentes en `C:\Users\Balbr\AppData\Local\Temp\claude\D--Recursos-Retrotarros-repo\651842ea-3439-43f1-9704-0952796098d3\scratchpad\` (`test_tarrodl.py`, `test_queue.py`, `test_merge.py`).

- [ ] **Step 1: Correr las pruebas nuevas completas.**
  Run: `python -m unittest discover -s tests -v` (desde `tools/tarrodl`)
  Expected: todas `ok`.

- [ ] **Step 2: Correr las suites existentes sin regresiones.**
  Run: `python <scratchpad>\test_queue.py`, `python <scratchpad>\test_tarrodl.py`, `python <scratchpad>\test_merge.py`
  Expected: cada una termina en `TODO OK` (usan YouTube real: si falla la red, repetir antes de dar la falla por real y reportarlo tal cual).

- [ ] **Step 3: Agregar entrada a `docs/modus-operandi/bitacora-decisiones.md`** con fecha 2026-10-04: nombres TarroDL + TarroMosaico como pestañas de la misma app; mosaico multi-video con selección automática + rango por video, intercalado, vista previa en línea de tiempo (no reproductor), una sola pasada de ffmpeg con filtro por archivo; reparto parejo por defecto. Mismo formato de las entradas anteriores del archivo.

- [ ] **Step 4: Revisar el log del servidor de prueba** (`tarrodl.log` del APPDATA aislado) buscando `ERROR`/`Traceback`; no debe haber ninguno.

- [ ] **Step 5: Commit y reporte.**
  ```bash
  git add docs/modus-operandi/bitacora-decisiones.md
  git commit -m "docs(tarrodl): bitacora de la decision de TarroMosaico"
  ```
  Reportar a Luis: SHA de los commits, cómo abrir la pestaña (cerrar TarroDL y abrir `tools\tarrodl\iniciar-tarrodl.cmd`), qué se probó y que lo que queda por probar con sus videos reales es el selector de Windows de "Agregar videos". Preguntar si hace `git push origin master` (cola de descargas + TarroMosaico + spec/plan) y esperar su "dale" antes de subir y correr los dos scripts de sync.
