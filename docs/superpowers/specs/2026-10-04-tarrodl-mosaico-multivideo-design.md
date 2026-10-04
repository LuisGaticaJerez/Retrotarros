# TarroMosaico: mosaico a partir de varios videos (TarroDL)

Fecha: 2026-10-04. Estado: spec para revision de Luis.

## Objetivo

Elegir varios videos ya descargados (ej. 5) y armar UN clip mosaico de duracion total fija (ej. 5 min)
con trozos de todos ellos, para usarlo como gameplay en las TarroVisiones. Luis controla de que
seccion de cada video salen los trozos y ve la distribucion antes de crear nada.

Exito: con 5 videos, 5 min totales y trozos de 15 s, la linea de tiempo previa muestra el reparto,
"Crear mosaico" produce un `.mp4` de 5:00 (+-0.5 s) que corresponde exactamente a esa vista previa,
y cancelar a medio camino no deja archivos a medias.

## Decisiones tomadas con Luis

- Seleccion de secciones: automatico + rango desde/hasta por video (sin reproductor, sin edicion manual).
- Orden final: intercalado entre videos (v1, v2, v3, v4, v5, v1...), cronologico dentro de cada video.
- Vista previa: linea de tiempo dibujada, instantanea, sin procesar video.
- Fuentes: cualquier archivo que ffmpeg lea (OBS, GoPro, capturas, descargas de TarroDL).
- Nombres: TarroDL (descargar y clips, como hoy) + TarroMosaico (nuevo), como pestañas de la misma app.

## Fuera de alcance

Elegir cada trozo a mano con reproductor, miniaturas por trozo, preview renderizado en baja calidad,
guardar proyectos de mosaico, separar "Clips" en pestaña propia (hoy cuelgan de la tarjeta de descarga).

## Enfoque

Un job nuevo (`kind = "mosaic"`) con una sola pasada de ffmpeg: una entrada `-ss -t -i` por trozo,
filtro de normalizacion por trozo y `concat`. Reusa `stream`, `spawn(pool="clips")`, `check_cancel`,
`CLEANUPS` y el patron de progreso `-progress pipe:1` de `api_clips`. El pool `clips` limita a un
trabajo pesado a la vez (los clips y los mosaicos se turnan).

## Backend (`tools/tarrodl/tarrodl.py`)

### Planificador

`plan_multi(videos, total, piece, share, seed)` es una funcion pura (testeable sin ffmpeg).

- `videos`: lista ordenada de `{file, duration, a, b}` (seccion `a..b` en segundos, ya resuelta).
- `k = total // piece` trozos en total; cada trozo dura `p = total / k` (nunca menos de `piece`;
  suma exacta `total`).
- Reparto de los `k` trozos entre videos:
  - `share = "parejo"`: `k // n` por video; el sobrante (de a 1) va a los videos con seccion mas larga.
  - `share = "proporcional"`: proporcional al largo de la seccion (metodo del resto mayor).
- Capacidad por video: `floor((b - a) / p)` trozos sin solaparse. Si un video recibe mas que su
  capacidad, se le recorta a su capacidad y el exceso se redistribuye entre los que aun tienen
  capacidad (misma regla de reparto). Si la suma de capacidades < `k`, error claro que dice cuanto
  falta ("Los videos no alcanzan para N min sin repetir material. Amplia secciones, agrega videos o baja
  el largo total.").
- Posicion dentro del video: la seccion se divide en `m` ranuras iguales (m = trozos de ese video) y
  cada trozo cae en su ranura. `seed = 0` los centra (determinista, como `plan_mosaic`); `seed > 0`
  los desplaza al azar dentro del margen libre de la ranura con `random.Random(seed ^ indice_video)`.
  Misma semilla, mismo plan: la vista previa y el render coinciden.
- Orden final: ronda por video (turno 1 de cada video, turno 2, ...); un video sin mas trozos se
  salta. Dentro de un video, los trozos van en orden cronologico.
- Retorna `{"seg": p, "lanes": [{file, duration, range, starts[]}], "sequence": [{video, start, at}]}`
  donde `at` es el instante acumulado en el clip final.

### Validacion (`validate_mosaic_params`)

- 2 a 12 videos (1 video se deriva a TarroDL; un limite protege el comando de ffmpeg y la UI).
- Total: `MOSAIC_MIN_SEC, MOSAIC_MAX_SEC = 60, 900` (1 a 15 min). Trozo: 10 a 60 s y `<= total`.
- `share` en {parejo, proporcional}; `seed` entero >= 0; resolucion en {720, 1080}.
- Cada archivo debe existir y tener extension en `VIDEO_EXTS`; sin duplicados exactos (misma ruta).
- Nombre de salida: se sanea con la misma funcion que usan los slugs de descarga.

### Endpoints

| Ruta | Metodo | Uso |
|---|---|---|
| `/api/pickvideos` | POST | Selector de Windows con `Multiselect = true`; devuelve `{files: [...]}` o `{cancelled: true}`. Reusa `PICK_PREAMBLE`; script nuevo `PICK_VIDEOS_SCRIPT` (un `OpenFileDialog` con multiselect, una ruta por linea). |
| `/api/mosaic_plan` | POST | Vista previa. Mide duraciones (ffprobe, cache en memoria por `(ruta, mtime, size)`), resuelve cada `range_start/end` con `resolve_range` y llama `plan_multi`. No crea nada. |
| `/api/mosaic` | POST | Crea el job: valida, recalcula el plan con los mismos parametros y la misma semilla, y arma el mp4. Devuelve el job (pool `clips`). |
| `/api/session_files` | GET | Videos de la carpeta de descargas (los ya terminados), mas recientes primero, para el boton "Descargados". |

`/api/mosaic_plan` y `/api/mosaic` comparten un `resolve_mosaic_request(body)` para que la vista
previa y el render usen exactamente el mismo plan.

### Comando ffmpeg

Un solo `ffmpeg` con una entrada por trozo en el orden final de la secuencia:

```
-ss S -t p -i <video>          (repetido por trozo)
-filter_complex
  [i:v:0]scale=W:H:force_original_aspect_ratio=decrease,pad=W:H:(ow-iw)/2:(oh-ih)/2,
        setsar=1,fps=30,setpts=PTS-STARTPTS[vi];
  [i:a:0]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS[ai];
  ... (para un trozo sin audio: anullsrc=r=48000:cl=stereo,atrim=duration=p[ai])
  [v0][a0][v1][a1]...concat=n=K:v=1:a=1[v][a]
-c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart
```

- `W:H` = 1920:1080 o 1280:720 segun la opcion.
- Si un trozo no tiene audio se genera silencio con `anullsrc` para ese trozo, asi `concat` siempre
  recibe v+a en todos los segmentos. Se detecta con `has_audio` por archivo (una vez por video).
- Con `-n` (no pisar) y numeracion previa, nunca sobreescribe.
- El filtro siempre se pasa con `-filter_complex_script <archivo temporal>` (borrado al terminar o
  cancelar), para no depender del limite de largo de linea de comandos de Windows (el maximo son
  15 min / 10 s = 90 entradas).

### Salida, progreso y cancelacion

- Archivo: `<carpeta de clips>/<nombre>.mp4`, con nombre editable (por defecto `mosaico`); si existe,
  `<nombre>_2`, `_3`... (no se usa `_clipN`, que es de TarroClip).
- Progreso: `out_time_us / total` con el mismo `on_line` de `api_clips`; texto "Armando mosaico
  (K trozos de N videos, recodifica)...".
- Cancelar: `kill_tree` del proceso (ya existe) y `CLEANUPS` borra el mp4 a medias y el archivo de
  filtro. Un mosaico terminado no se toca.
- Errores de ffmpeg: se loguea el final de stderr y se muestra una version corta; el archivo parcial
  se borra.
- Todo se registra en `tarrodl.log` (plan resumido, comando sin rutas gigantes repetidas, resultado).

## Interfaz (`tools/tarrodl/ui/index.html`)

- Barra de pestañas arriba: **TarroDL** (la pantalla actual, sin cambios) y **TarroMosaico**. La pestaña
  activa se recuerda en `localStorage`. El poll de jobs sigue siendo uno solo.
- Pantalla TarroMosaico:
  1. **Videos**: botones "Agregar videos" (selector multiple) y "Descargados" (lista de
     `/api/session_files` con checks). Cada fila: nombre, duracion, barras desde/hasta (misma logica
     `secInit/secFromSlider` de las tarjetas), subir/bajar (cambia el orden del intercalado) y quitar.
  2. **Parametros**: largo total (slider 1 a 15 min), largo minimo de trozo (slider 10 a 60 s), reparto
     (parejo/proporcional), resolucion (1080p/720p), nombre del archivo, boton "Regenerar reparto"
     (sube la semilla) y volver a la distribucion centrada.
  3. **Vista previa**: una fila por video con color propio y los trozos marcados sobre su duracion
     real (la seccion elegida resaltada), y debajo la franja de la secuencia final con el instante de
     cada corte. Texto resumen: "20 trozos de 15 s, 4 por video, 5:00".
  4. **Crear mosaico**: deshabilitado hasta que haya plan valido; luego una tarjeta de progreso con
     barra, Cancelar y, al terminar, "Ver video" y "Abrir carpeta de clips".
- La vista previa se recalcula con un pequeño debounce al mover cualquier control.
- Mensajes de error del backend se muestran junto al boton, no en un alert.

## Errores y bordes

- Archivo movido o borrado entre la vista previa y el render: error claro con el nombre del archivo.
- Video corrupto o sin duracion legible: se marca esa fila y no se puede crear hasta quitarlo.
- Secciones demasiado cortas: mensaje del planificador (arriba); la vista previa muestra el error en
  vez de la linea de tiempo.
- Videos de largo muy distinto: `parejo` los trata igual; `proporcional` sesga hacia el mas largo.
- Audio estereo, mono o sin audio: todo se normaliza a estereo 48 kHz.
- Intentar crear dos mosaicos: el segundo queda "En cola" (pool `clips`), con las mismas acciones de
  cancelar que el resto.

## Pruebas

- Unitarias (`plan_multi`): cantidad de trozos y suma exacta; ningun solape dentro de un video;
  orden intercalado; mismo `seed` igual plan y `seed` distinto plan distinto; redistribucion cuando un
  video es corto; error cuando no caben; `proporcional` vs `parejo`; 2 y 12 videos.
- Integracion (ffmpeg real, videos sinteticos con `lavfi`): tres videos con resolucion y fps distintos
  y uno sin audio; el mp4 resultante dura el total pedido (+-0.5 s), tiene la resolucion elegida, 30 fps,
  audio estereo 48 kHz y un solo stream de video y uno de audio.
- Cancelar: no queda el mp4 ni el archivo de filtro. Nombre repetido: crea `_2`.
- API: validaciones (1 video, 13 videos, duplicados, archivo inexistente, total fuera de rango).
- UI en instancia aislada (puerto propio, APPDATA falso) con Edge/navegador del panel: agregar videos
  sinteticos, mover desde/hasta, regenerar, crear, ver progreso y cancelar. Se hace antes del commit
  final, igual que con la cola.
- Las suites existentes (`test_tarrodl`, `test_queue`, `test_merge`) deben seguir pasando.

## Documentacion

Nota breve en `docs/modus-operandi/bitacora-decisiones.md` con la decision de nombres (TarroDL +
TarroMosaico) y de "una sola pasada de ffmpeg". `tools/tarrodl/` no tiene README, no se crea uno.
