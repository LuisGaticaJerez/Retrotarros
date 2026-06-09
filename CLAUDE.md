# Retrotarros — Claude Code Project Instructions

> Lee este archivo completo antes de cualquier acción. Después lee `HANDOFF.md` y los docs relevantes al escenario.

## Ubicaciones canónicas (importante)

Todo el material Retrotarros vive bajo `D:\Recursos Retrotarros\`:

| Ruta canónica | Contenido |
|---|---|
| `D:\Recursos Retrotarros\repo\` | **Este git repo.** Clone de `github.com/LuisGaticaJerez/Retrotarros`. |
| `D:\Recursos Retrotarros\Drive\` | **Junction** a `G:\Mi unidad\` — espejo del Google Drive. Operaciones internas siguen usando `G:\Mi unidad\Studio\` (es el mismo lugar via Drive Desktop). |
| `D:\Recursos Retrotarros\videos\` | Source MP4s (gameplays largos, GoPro studio sessions, B-roll bruto). |
| `D:\Recursos Retrotarros\videos\clips\` | Clips B-roll cortos generados por `scripts/extract-broll.ps1` (carpetas `clips-<slug>\`). |
| `D:\Recursos Retrotarros\RETROTARROS\` | Material crudo de grabación GoPro. |
| `D:\Recursos Retrotarros\Cap NN - <título>\` | Proyectos DaVinci por episodio. |
| `D:\Recursos Retrotarros\musica\` `Imagenes\` | Audio y B-roll de imágenes. |

**El repo NO está más en OneDrive.** El backup es GitHub (`master` siempre pusheado). No buscar el repo en `C:\Users\Balbr\OneDrive\Documentos\GitHub\Retrotarros\` — esa ubicación queda obsoleta.

## TarroTeaser — generador automático de teasers

**Comando atajo:** cuando Luis dice **"hacé el teaser con el tarroteaser"** o **"corré el tarroteaser"**, esto significa ejecutar:

```bash
python scripts/tarroteaser.py <ruta-al-video-master.mp4> --slug <slug-del-episodio>
```

**Qué hace:** genera un teaser CRUDO vertical 1080×1920 con 5 cortes concatenados:
1. **Inicio divertido** del primer tercio del video
2. **3 highlights** del centro (top score keywords)
3. **Clímax** según el tipo de episodio (auto-detectado del slug)

Output: `D:\Recursos Retrotarros\Drive\Studio\<slug>\teasers\<slug>-tarroteaser-YYYYMMDD.mp4`

**Tipos de episodio auto-detectados:**
| Slug contiene | Tipo | Clímax que busca |
|---|---|---|
| `top-mundial` o `ranking` | `ranking` | "número uno", "el primero" |
| `top-precios` | `top-precios` | "el más caro", "valor récord" |
| `archivo` | `archivo` | "valor total", "vale la colección" |
| `joyas` | `joyas` | "la joya", "infravalorado" |
| `vs-mundo` o `retrotarros-vs` | `vs-mundo` | "puntaje final", "ganó Koko/mundo" |
| `hardware-raro` | `hardware-raro` | "más raro", "única" |
| `no-latam` | `no-latam` | "nunca llegó", "exclusivo Japón" |
| (otro) | `generic` | despedida "vemos", "apóyenos" |

**Cómo lo edita Luis:** importa el MP4 en **CapCut** (preferido) → agrega su intro + outro + lower-thirds + música a gusto. El script entrega solo los cortes, el editor humano hace el polish.

**Limpiar música de fondo del master:** el audio del teaser viene del master con su música embebida. Para aislarla, aplicar **"Voice Enhancement"** o **"Noise Reduction"** de CapCut sobre los clips importados. NO se hace en el script (probamos Demucs pero requiere torchcodec + ffmpeg full-shared build, no vale la pena vs CapCut nativo).

**Generar proyectos CapCut programáticamente:** investigamos cómo automatizar la creación de proyectos `.draft` con Voice Enhancement + lower-thirds + intro/outro pre-cargados. **Pausado** porque el ROI no se justifica para cadencia ~1 teaser/semana. Findings completos en `docs/capcut-automation-research.md` por si en el futuro queremos retomar (3+ teasers/semana o producto SaaS).

**Stack:**
- Whisper local (modelo `small`, 244MB) con cache en `.cache/whisper/` para iteraciones rápidas
- ffmpeg para corte + vertical 1080×1920 con blur background
- Sin OpenAI API, sin internet (Whisper corre local)

**Script complementario:** `scripts/generate-teaser.py` es la versión "todo incluido" (overlays, intro, outro VHS card, música 8 Bits Rock, trivia card). Queda como backup para cuando quieras un teaser completo sin editar. TarroTeaser es la opción por defecto.

## Qué es esto

Canal de YouTube en español sobre **Nostalgia + Juegos + Música** (retrogaming + batería). Proyecto chileno. Ver `docs/proyecto.md` para contexto completo.

> **Tagline público canónico:** `Nostalgia + Juegos + Música`. Es lo que va en banners, gráficas de inicio/fin, headers de pautas y cualquier touchpoint visible al público. Internamente seguimos describiendo el formato como "retrogaming + batería" porque eso describe la mecánica (juegos retro + Koko tocando), pero el tagline al público es el de arriba.

## Protagonistas

- **Luis Balbrigame** — rigor histórico, investigación, estructura narrativa. Cámara en lane Luis.
- **Koko** — colección física grande de juegos/consolas, toca batería. Cámara en lane Koko y episodios largos.

## REGLA INMUTABLE — Tono y lengua

**Aplica a TODO** lo que Claude produce en este proyecto: HTMLs, copies para YouTube/TikTok/IG, capturas, capciones, commits, y **también el chat con Luis aquí mismo**. No solo al output que va para el público — también las explicaciones, listas y resúmenes que le doy a Luis tienen que estar en chileno neutro.

**Reglas concretas:**

- **Español chileno neutro con tuteo.** Usar "tú/tienes/quieres/dime/puedes/sabes". Marcas chilenas suaves OK: "po", "te tinca", "mira", "fíjate", "espérate", "déjanos", "suscríbete", "tení".
- **Sin voseo argentino/rioplatense.** Prohibido: "vos sabés", "tenés", "querés", "decime", "pegás", "navegás", "armás", "bajás", "fijate" (con voseo), "che".
- **Sin mexicanismos.** No "órale", "güey", "chido", "ándale".
- **Sin españolismos.** No "vale", "tío", "guay", "molar".
- **Sin tildes en tildes débiles** (á/é/í/ó/ú → a/e/i/o/u) en los HTMLs y outputs públicos. En chat con Luis pueden ir tildes (decisión de Luis: si pide aplicar también al chat, sí; si no, el chat puede tener tildes para legibilidad).
- **EXCEPCIÓN TarroBot (TTS):** los textos que reproduce TarroBot por voz (Edge TTS) SÍ deben llevar tildes correctas + números en palabras ("20 mil" en vez de "20,000"). Sin tildes, Edge TTS no pronuncia bien las palabras. Aplica a: prompts de Claude en `scripts/tarrobot*.py`, listas hardcoded (SALUDOS_GEEK, DESPEDIDAS_CORTAS, CATCHPHRASES), respuestas pregeneradas de `/api/precio`, y cualquier texto que vaya a edge-tts. Los HTMLs y assets visuales del canal siguen sin tildes (regla general).
- **Registro conversacional.** Dos chilenos en un café, no locutores de noticiero.
- **Si el output sale con marcas regionales equivocadas → corregir y reescribir.** No usar "boludo", "che", "vamos a tirarle" en sentido argentino.

Si Luis señala que sonaste argentino → disculparte breve, reescribir el último mensaje en chileno neutro, y seguir aplicando la regla.

## Formatos

Ver `docs/formatos.md` para estructura completa. Resumen:

- **Episodios largos** (15–25 min): 5 bloques, cierra con Koko tocando en batería. Cadencia: 1 cada 10–12 días.
- **Shorts**: divididos por lane Luis (curiosidades históricas, solo) y lane Koko (batería, performance). Cadencia: 2–3/semana.
- **Indie Lat**: entrevistas a devs indie latinoamericanos. Cierra con Koko tocando el tema del juego.

## Identidad visual

Ver `docs/identidad-visual.md`. Paleta exacta:

- Magenta neón `#FF2E88` — primario
- Cyan eléctrico `#00E5FF` — secundario
- Morado profundo `#2D1B69` — fondo principal
- Amarillo arcade `#FFD23F` — etiquetas, Indie Lat, CTAs
- Blanco hueso `#F5F0E8` — texto sobre oscuro

Tipografía: logo → Monoton/Press Start 2P · títulos miniatura → Bebas Neue/Anton · texto → Inter/Montserrat.

## Documentos del proyecto

Fuente de verdad: archivos `.md` en `docs/`. Los `.docx` originales quedan archivados pero no se editan.

| Archivo | Rol |
|---|---|
| `docs/estrategia.md` | Documento maestro: nombre, enfoques, formatos, plan 3 meses, Indie Lat, identidad visual. |
| `docs/briefings-compositores.md` | Fichas de compositores (Kondo, Uematsu, Mitsuda, Yamaoka, Wise, Kirkhope, etc.). Documento vivo. |
| `docs/guiones-shorts.md` | Guiones lane Luis: timings, B-roll, título YouTube, caption, hashtags, datos de respaldo. Documento vivo. |
| `docs/guia-youtube-viral.md` | **Playbook de virality YouTube** (título, miniatura, descripción, hashtags, capítulos). Toda `descripcion-{slug}.md` lo sigue. |
| `docs/descripcion-{slug}.md` | Descripción YouTube lista para pegar: títulos, resumen, capítulos con timestamps, hashtags, tags. Sigue `guia-youtube-viral.md`. |

> **Regla de entrega (Luis, 2026-06-07):** cada vez que cierre un kit de publicación, **pegar en el chat** el texto listo para YouTube (título + descripción + comentario fijado + tags + hashtags), no solo dejarlo en el `.md`. Luis lo copia directo desde el chat.
| `docs/pauta-{slug}.md` | Pauta operativa de episodio largo (para Claude — denso, tablas, anclas, anexos). |
| `docs/discusion-{slug}.md` | Versión conversacional de la pauta (para Luis + Koko — bullets, preguntas guía, decisiones pendientes). |
| `studio/{slug}.html` | Monitor visual del estudio durante la grabación (paleta synthwave, navegable). |
| `data/coleccion_koko.csv` | **Fuente de verdad** de la colección física de Koko. 899 ítems, 26 plataformas. Leer con `grep`/`csv` directo. |
| `ref/Retrotarros_Referencia_Visual_N64.html` | Referencia visual estilo (header, cards, paleta) para HTML del estudio. |

## Imágenes en HTMLs de ranking (regla obligatoria)

**En todo HTML que rankee juegos (top mundial, top precios, archivo, joyas, retrotarros-vs-mundo, etc.) la imagen del juego debe ser SIEMPRE la box art real, NUNCA el logo del juego.**

- ✓ Sí: caja NTSC USA del cartucho (Wikipedia `File:<Juego> Cover.png` o equivalente).
- ✗ No: logo/wordmark del juego (PNG transparente con el título estilizado).
- ✗ No: screenshot del gameplay.
- ✗ No: artwork promocional sin la caja.

**Por qué:** la caja física es lo que Koko colecciona y lo que el espectador reconoce visualmente. El logo solo dice el nombre que ya está como texto al lado.

**Cómo encontrar la caja correcta (método probado 2026-06):**

1. **Wikipedia REST summary = fuente CONFIABLE y por defecto.** Limpia (sin marca de agua), NTSC, articulo del juego. Script: `scripts/fetch_boxart_wiki.py` → `descargar(out_dir, [(key, "query")])`. Internamente: search API resuelve el titulo → `GET https://en.wikipedia.org/api/rest_v1/page/summary/<Titulo>` → `originalimage.source` (la caratula del infobox). Query con desambiguacion cuando haga falta: `"Metroid (video game)"`, `"Contra (video game)"`, `"Ninja Gaiden (NES video game)"`, `"Mike Tyson's Punch-Out!!"`.
2. **gamesdatabase.org — NO recomendada** (Luis la sugirio, pero la probamos): tiene **marca de agua** "www.gamesdatabase.org" sobre cada imagen y a veces trae la edicion equivocada (Famicom JP, o compilaciones como "All-Stars 25th Anniversary"). Script existe (`scripts/fetch_boxart.py`) pero solo usar si Wikipedia no tiene el juego, y limpiar la marca de agua.
3. Si no → MobyGames, LaunchBox, TheGamesDB.
4. **Verificar SIEMPRE** con `Read`/mosaico antes de commitear — si sale logo/wordmark/screenshot/edicion-equivocada/imagen <6kb, descartar.
5. Si NO existe box accesible → fallback CSS `cart-fallback` (soportado por `top_deck.py`), nunca un logo.

**Wiring automatico:** las box van en `studio/img/<slug>/<key>.jpg` donde `key = slug del titulo` (mismo `_slugify`). `scripts/top_deck.py` las detecta solas (`_auto_img`): si existe el archivo, la usa; si no, `cart-fallback`. Los TarroShorts tambien las toman solas (item-photo con `onerror` que oculta si falta). Asi: bajar la box con la key correcta + regenerar deck / re-render short = aparece sin tocar drivers.

**Aplica a rankings ya hechos:** N64 (top-mundial, top-precios, retrotarros-vs-mundo, archivo-koko, joyas-ocultas) + PS Vita (top-mundial, top-precios, retrotarros-vs-mundo, archivo-koko) + futuros SNES, PS1, etc.

## Convención de pautas (obligatoria)

Cada episodio largo se cierra con **tres archivos**, mismo `{slug}`:

1. **`docs/pauta-{slug}.md`** — para Claude. Operativo y denso: rankings, datos precisos, fuentes, anclas históricas, scorecard, tiempos por bloque, anexos. Es lo que Claude lee como contexto.
2. **`docs/discusion-{slug}.md`** — para Luis + Koko. Conversacional: bullets cortos, preguntas guía para discutir antes de grabar, decisiones pendientes, qué falta cerrar. Es lo que abren impreso o en el celular.
3. **`studio/{slug}.html`** — para el estudio. Monitor visual que ven Luis y Koko en pantalla durante la grabación. Navegable con teclas ← →. Paleta synthwave (`#FF2E88` / `#00E5FF` / `#FFD23F` / `#06030f`). Base de estilo: `ref/Retrotarros_Referencia_Visual_N64.html`.

**Reglas:**
- Slug consistente en los tres archivos (ej. `n64-ranking`, `mario-saga`, `kirkhope-rare`).
- El `.md` de discusión es derivado del `.md` operativo — más corto, más conversacional, sin tablas pesadas.
- El HTML se actualiza solo cuando los datos del `.md` operativo están cerrados. Fuente de verdad = `pauta-{slug}.md`.
- Si se agrega un anexo con datos nuevos (precios, listas confirmadas), se actualizan los tres archivos en el mismo commit.

## Extracción de B-roll desde gameplays

Para resumir un gameplay largo (45–60 min de YouTube) en clips cortos listos para edición:

```powershell
.\scripts\extract-broll.ps1 -Video "C:\Users\Balbr\Downloads\Video\<archivo>.mp4" -Slug "<slug-corto>"
```

- **Salida:** `C:\Users\Balbr\Downloads\Video\clips-<slug>\` con N clips MP4 (1 por escena detectada, sin re-encoding).
- **Detector:** PySceneDetect `detect-adaptive` con threshold 5.5 + min-scene-len 8s por defecto.
- **Ajustes:** `-Threshold 3.5` para más clips · `-Threshold 8.0` para menos · `-MinSceneLen 6` para clips más cortos.
- **Casos especiales:** carreras/escenas únicas (Mario Kart Rainbow Road) generan pocos clips porque no hay cortes de cámara — bajar threshold si se necesitan más.
- **Requisitos:** `pip install scenedetect[opencv]` + `winget install Gyan.FFmpeg` (una vez por máquina).

Ejemplos reales ejecutados (2026-05-15):
- Star Fox 64 (57 min) → 97 clips · 186 MB
- Perfect Dark (10 min) → 58 clips · 142 MB
- Paper Mario (25 min) → 41 clips · 61 MB
- Zelda OoT Espantapájaros → 41 clips · 73 MB

## Capturas de slides para edición (regla obligatoria)

Cada HTML del estudio (`studio/<slug>.html`) genera frames PNG 1920×1080 listos para meter directo en DaVinci como B-roll / cortina entre tomas. Sin rebordes, texto crisp a 2x DPI.

**Comando:**
```powershell
python scripts/capture-slides.py <slug>
```

- **Salida repo:** `studio/captures/<slug>/<slug>-slide-NN.png` (gitignored).
- **Salida Drive:** `G:\Mi unidad\Studio\<slug>\captures\<slug>-slide-NN.png` (sincronizada manualmente con `cp` o `scripts/sync-to-drive.ps1`).

**Cuándo correrlo (obligatorio):**
1. Al **crear** un HTML de ranking nuevo (top mundial, top precios, retrotarros-vs-mundo, archivo, joyas, etc.).
2. Al **modificar** un HTML existente (cambios de texto, box arts, datos, slides nuevos) — re-generar las capturas para que la edición siempre tenga frames actualizados.
3. Cualquier cambio visible en el HTML pide regenerar captures.

**Por qué importa:** Luis edita en DaVinci con estos PNGs como overlay full-screen. Si las capturas están desactualizadas, el video muestra datos viejos. La fuente de verdad sigue siendo el `.html`, pero las capturas son lo que aparece en pantalla.

**Versiones:**
- Horizontal video 16:9 (default): `python scripts/capture-slides.py <slug>`
- Vertical shorts 9:16: `python scripts/capture-slides.py <slug> --width 1080 --height 1920`

**Requisitos (una sola vez):** `pip install playwright && python -m playwright install chromium`.

## Workflow obligatorio al cerrar cambios

Cualquier sesión que modifique HTMLs / imágenes / box arts / pautas / discusiones debe terminar con estos pasos en orden:

1. **Commit + push a GitHub** — Claude ejecuta `git add`, `git commit`, `git push origin master`. Sin esto el equipo no ve los cambios.
2. **Regenerar capturas** (si tocaste HTMLs) — `python scripts/capture-slides.py <slug>` para CADA HTML nuevo/modificado. Episodio nuevo SIEMPRE genera capturas antes de sincronizar.
3. **Sync a Drive — LOS DOS scripts, SIEMPRE (regla de Luis 2026-06-07):**
   - **`scripts/sync-to-drive.ps1`** → `G:\Mi unidad\Studio\<slug>\` (HTML + img + **capturas** por episodio) + `Studio\pautas\*.docx` (pauta y discusión convertidas con pandoc). **Este es el que usa el PC de grabación.** Es el que mas se me olvida — NUNCA saltarlo al cerrar un episodio.
   - **`scripts/sync-tarrobot-to-drive.ps1`** → `G:\Mi unidad\Studio\tarrobot\` (la app TarroBot: scripts + HTMLs + JSON + shorts MP4 + branding).
   - Correr AMBOS. El primero es el critico para que Luis pueda grabar; el segundo para la app/estudio TarroBot.
4. **Avisar a Luis** del SHA del último commit + qué cambió.

**Anti-patrón:** dejar cambios solo en el repo, o sincronizar solo `tarrobot` y olvidar `sync-to-drive.ps1` (= el estudio queda sin la pauta/HTML/capturas para grabar). Las tres ubicaciones (repo local, GitHub, Drive del estudio) deben quedar sincronizadas, y en el Drive deben quedar AMBAS carpetas (`Studio\<slug>\` y `Studio\tarrobot\`).

## Sincronización con Drive del estudio

El PC del estudio Retrotarros consume el contenido desde Google Drive (`G:\Mi unidad\Studio\`). El script `scripts/sync-to-drive.ps1` automatiza la copia:

```
G:\Mi unidad\Studio\
├── <slug>/<slug>.html              ← monitor visual
├── <slug>/img/<slug>/*.{jpg,png}   ← box arts / hardware
└── pautas/
    ├── pauta-<slug>.docx           ← pauta operativa convertida MD→DOCX
    └── discusion-<slug>.docx       ← documento de reunión convertido MD→DOCX
```

**Reglas:**
- La fuente de verdad sigue siendo el `.md` en el repo. Los `.docx` se generan con pandoc (`scripts/sync-to-drive.ps1`).
- Los `.docx` están en `.gitignore` — no se commitean al repo, se regeneran cuando se necesite.
- Requiere pandoc instalado: `winget install JohnMacFarlane.Pandoc`.
- Correr el script después de cerrar cambios en cualquier `pauta-*.md` / `discusion-*.md` / `*.html` de `studio/`.

## Reglas operativas

### Lectura de archivos
- **Markdown** (`.md`): fuente de verdad de todo el contenido del canal. Leer con `Read` tool.
- **CSV colección** (`data/coleccion_koko.csv`): leer con `grep` para búsquedas puntuales por plataforma o título.
- **Word/Excel archivados**: los `.docx` y `.xlsx` originales quedan en sus carpetas pero **no se editan**. Solo lectura si falta info que aún no migró al `.md`.
- Antes de proponer guiones o pautas, **revisar `data/coleccion_koko.csv`** para confirmar que Koko tiene el juego físico.

### Creación de contenido
- Lane Luis y lane Koko son carriles distintos — no mezclar en un short sin indicación explícita.
- Todo short incluye: duración, talento, tono, guión con timings, B-roll por bloque, título YouTube, caption, hashtags, notas de producción y **datos de respaldo** verificables.
- Todo largo respeta la estructura de 5 bloques salvo formatos especiales (game show, etc.).
- Cada episodio largo debe sangrar mínimo 6 shorts (idealmente 8), divididos por lane.

### Datos y verificación
- **Toda afirmación histórica o de precio debe poder defenderse**. Sin respaldo → no va al guión.
- Precios: fuente primaria PriceCharting + GameRant/The Gamer/Vgprice. Siempre aclarar **NTSC USA, CIB**.
- Datos históricos: cruzar mínimo dos fuentes antes de meter número o fecha en cámara.

### Git workflow (convención obligatoria)
- **Claude ejecuta** los `git add`, `git commit`, `git push`, scripts y operaciones de archivo. Luis NO corre comandos manualmente — Claude tiene Bash en el sandbox.
- **Commits locales no destructivos**: Claude los ejecuta sin pedir permiso explícito, luego informa el SHA.
- **Operaciones remotas o destructivas** (push, rebase, reset --hard, rm -rf masivo, force push, cualquier acción contra GitHub o que sobreescriba historia): Claude **pide confirmación con un comando concreto** antes de ejecutar. Ejemplo: "¿Pusheo `git push origin master` con los 5 commits acumulados?" — espera "dale" / "sí" / "ok" antes de correr.
- **Nunca usar** `--force`, `--no-verify`, `commit --amend` (sobre commits ya pusheados), `git reset --hard` sin confirmación explícita en el mismo turno.

### Output esperado
- **Pautas de episodio largo** → tres archivos por slug (ver "Convención de pautas"): `docs/pauta-{slug}.md` + `docs/discusion-{slug}.md` + `studio/{slug}.html`.
- **Guiones de shorts y briefings de compositores** → se agregan al documento vivo correspondiente (`docs/guiones-shorts.md`, `docs/briefings-compositores.md`).
- **Brainstorm interno** → Markdown libre en `docs/` con nombre descriptivo.
- Archivos reales en el repo — no solo mostrar contenido en chat.

## Anti-patrones — lo que NO hacer

- **No** voseo rioplatense ni mexicanismos pesados. Chileno neutro siempre.
- **No** asumir que Koko tiene un juego sin chequear el catálogo Excel.
- **No** guiones sin sección de datos de respaldo verificables.
- **No** mezclar lanes en un mismo short.
- **No** ofrecer 8 ángulos cuando Luis pidió uno — output decidido, luego iterar.
- **No** emojis en el cuerpo del guión hablado (sí en captions y títulos YouTube).
- **No** repetir el chiste del nombre "Retrotarros" — ya lo cubre el short fijado del canal.
- **No** inventar precios ni datos históricos. Si no se puede respaldar, se omite.

## Generadores de decks (reutilizables) — desde 2026-06

Para no escribir HTML a mano, hay dos generadores que clonan el CSS/JS canónico y reconstruyen el deck desde un dict de datos. Reutilizables para cualquier consola.

| Script | Genera | Estructura |
|---|---|---|
| `scripts/coleccion_deck.py` (`generar_deck(data, slug)`) | Episodio **colección** | portada → índice → por categoría: paneo + triple de 3 joyas → hardware → balance → cierre |
| `scripts/top_deck.py` (`generar_top(data, slug)`) | Episodio **top mundial / precios** | portada → divider intro → N slides #10→#1 → (rarezas: divider + items con `badge_text`) → (`grial`) → análisis → cliffhanger |

- Base de estilo: `coleccion_deck.py` clona de `n64-coleccion.html`; `top_deck.py` clona de `snes-top-mundial.html`.
- `top_deck.py` soporta `cart-fallback` (sin box art → etiqueta de color), `badge_text` (rarezas con etiqueta en vez de número) y slide `grial` (HOLY GRAIL).
- Driver one-off por episodio en `.cache/gen_<slug>.py` (gitignored). El generador (`scripts/*.py`) sí se commitea.

### REGLA — Lista de paneo por colección (obligatoria, automática) — Luis 2026-06-08

Cada vez que se genera una **colección** con `coleccion_deck.generar_deck()`, el generador escribe **además** `docs/lista-paneo-<slug>.md`: el catálogo COMPLETO por categoría, con las 3 joyas marcadas con ⭐. Sirve para consultar/compartir al grabar los paneos de cámara.

- Para que la lista traiga el detalle completo de títulos (no solo conteo + joyas), cada categoría del `data` debe incluir `"juegos": [<títulos>]`. Los drivers de colección **deben** pasar esa lista (sale del CSV `data/coleccion/coleccion-retrotarros.csv`).
- El emparejamiento joya↔juego es por mejor coincidencia de prefijo (las joyas vienen en mayúsculas/abreviadas), así que basta con que la joya empiece igual que el título real.
- El `.md` se commitea y se sincroniza al Drive como DOCX con el sync normal.
- Pendiente backfill: `snes-coleccion` y `n64-coleccion` (sus drivers ya no están en `.cache`; regenerar con `"juegos"` cuando se retomen).

## Convención del TOP PRECIOS (obligatoria) — articulada por Luis 2026-06-07

El episodio de precios SIEMPRE se arma en tres bloques, igual que `snes-top-precios`:

1. **Top 10 RETAIL** — solo juegos que de verdad se vendieron en tiendas. Ordenados por valor CIB (#10→#1). Es el ranking "de verdad".
2. **Apartado RAREZAS / NO-RETAIL** — variantes de color, sin licencia, exclusivos de alquiler (Blockbuster), prototipos, hallazgos de bodega y cartuchos de competencia. Van APARTE con etiqueta en vez de número (no se vendieron en retail normal).
3. **SANTO GRIAL** — el que se escapa de todo precio. Slide HOLY GRAIL único.

**Regla visual (obligatoria, Luis 2026-06-07):** en TODO top de precios el **precio va SIEMPRE grande en la esquina superior derecha** de cada slide (pastilla amarilla, `top_deck.py` lo hace solo: detecta `USD ...` en `price`/`precio_short`/`meta` y lo pone con la clase `.game-price`). La posicion (#N) queda arriba a la izquierda.

**Reglas de datos:**
- **Precios actualizados al año en curso (2026)**, cruce PriceCharting / GameValueNow / Den of Geek. Siempre "valor aproximado", nunca precio fijo, nunca consejo de inversión.
- Distinguir **dos ejes** de "el más caro": por **rareza/escasez** (ej. NWC dorado, 26 copias) vs por **venta récord de copia sellada graduada** (ej. Super Mario Bros. sellado WATA 9.8 = USD 2M, récord NES 2026). El grial suele ser el récord de venta.
- **Aclarar SIEMPRE en vivo** cuando el grial es una copia SELLADA Y GRADUADA (fenómeno boom WATA 2020-2021): NO es el cartucho suelto común. Da credibilidad y evita el "yo tengo ese, ¿valgo millones?".

## TarroShorts de DATOS (lane TarroBot) — desde 2026-06-08

Lane nueva de shorts conducidos por **TarroBot** (mascota) sobre un **tema curioso libre** (no atado a la colección): presenta el tema, suelta 5 datos y reacciona al gameplay en cada TarroVisión (placeholder para CapCut). Distinto a los TarroShorts derivados de episodios y a los guiones narrados por Luis (`docs/guiones-shorts.md`).

- **Generador:** `scripts/tarroshort_datos.py` (`generar_short_datos(data, slug)`), clona `_template-tarroshort.html`.
- **Flag `modo`:** `"countdown"` (ranking #5→#1, rank-badge) o `"lista"` (5 datos con etiqueta `DATO N`).
- **Salidas:** `studio/tarroshort-<slug>.html` + `studio/shorts/guion-<slug>.txt` (líneas habladas de TarroBot para el TTS).
- **Investigación curada acá** (no LLM en estudio): el driver `.cache/gen_tarroshorts_batch.py` lleva los datos a mano. Tono **dato + reacción meme**.
- Slug siempre con prefijo `datos-` (ej. `datos-zelda-feos`). El gameplay va en la TarroVisión vacía en CapCut.
- **Intro (regla):** toda intro arranca diciendo **"Soy TarroBot de Retrotarros"** y es **corta**.
- **Display vs hablado (`data-say`):** el texto en **pantalla va SIN tildes** (regla del canal). El texto **hablado va aparte** en los campos `saludo_say` / `say` / `sub_say` **CON tildes y pausas** (comas y `...`), para que el TTS pronuncie bien el español y deje un beat antes/después de los **nombres en inglés**. El render (`tarroshort_render.py`) lee `data-say` si existe, si no, el `textContent`. Las tildes solo viven dentro de `data-say` (no son visibles).
- **Re-render = limpiar audio:** el render reutiliza los MP3 por escena. Si cambian los textos hablados, borrar `studio/shorts/audio/tarroshort-<slug>/` antes de re-rendir, o quedará la voz vieja.

## TarroShorts — generación (vertical 1080×1920)

`scripts/tarroshort_render.py` arma el MP4 vertical donde TarroBot presenta y comenta (voz edge-tts es-CL-CatalinaNeural +12Hz). Reacciones CON tildes (TTS). Bajo 60s.

- **Tops** (mundial/precios): `construir_desde_pauta(<slug>)` desde el JSON `studio/pautas/<slug>.tarrobot.json` (#10→#1, muestra los primeros y teasea el resto al canal).
- **Colección**: short curado con **uno de cada categoría** (decisión Luis para n64-coleccion). Driver curado en `.cache/` que arma el HTML del short con `_template-tarroshort.html` + reacciones manuales en `studio/shorts/highlights/<slug>.json`.
- Render: `python scripts/tarroshort_render.py tarroshort-<slug>`. Output `studio/shorts/tarroshort-<slug>.mp4` (gitignored, va al Drive por sync).
- El short deja un cuadro vacío (placeholder) para montar gameplay encima en CapCut — no trae box ni gameplay embebido.

## Fuente de verdad de la colección (GameEye)

- **Canónico (más nuevo):** `data/coleccion/coleccion-retrotarros.csv` — export de la app **GameEye**, 898 juegos, con `README.md`. Copia estable + snapshot fechado. **Consultar SIEMPRE antes de inventar listas** (colección, tops).
- `data/coleccion_koko.csv` es un export ANTERIOR (15-may) del mismo origen — quedó como snapshot viejo. Usar el de `data/coleccion/`.
- Columnas: `Platform, Title, Publisher, Developer, Genre, Ownership (Loose/Boxed/CIB), PriceLoose/PriceCIB/PriceNew` (coma decimal, EUR), `metacritic` (puede venir `Missing Field`). Nombres exactos de plataforma: `NES/Famicom`, `SNES/Super Famicom`, `Nintendo 64`.
- Actualizar: re-exportar de GameEye → pisar `coleccion-retrotarros.csv` + dejar snapshot fechado.

## Commit en el sandbox (workaround obligatorio)

El Bash sandbox bloquea here-strings con rutas del sistema (`G:\Mi`, `D:\Recursos`). Para commits multilínea:
```bash
printf '%s\n' "titulo" "" "linea cuerpo" > .git/COMMIT_EDITMSG_TMP.txt && git commit -F .git/COMMIT_EDITMSG_TMP.txt && rm -f .git/COMMIT_EDITMSG_TMP.txt
```
- **Sin** `Co-Authored-By` ni firmas automatizadas en commits del canal.
- Sync del estudio TarroBot: `scripts/sync-tarrobot-to-drive.ps1` (sube scripts + HTMLs + pautas + shorts MP4 + branding a `G:\Mi unidad\Studio\tarrobot`). Distinto de `sync-to-drive.ps1` (pautas DOCX).
- `Remove-Item` inline con rutas del sistema también se bloquea → borrar con `python -c "import glob,os; ..."` o desde un `.ps1`.

## Cómo arrancar una sesión

Identificar el escenario y revisar archivos relevantes antes de proponer output:

1. **Short nuevo** → preguntar lane (Luis o Koko) + tema + consultar `docs/guiones-shorts.md` para no repetir ángulos.
2. **Pauta episodio largo** → `docs/estrategia.md` para formato + `data/coleccion_koko.csv` para chequear colección. Generar los tres archivos (pauta + discusión + html) en el mismo flujo, con el mismo slug.
3. **Investigar compositor** → `docs/briefings-compositores.md`, agregar ficha si es nuevo.
4. **Brainstorm tendencias** → revisar redes, traer 3–5 formatos que peguen ahora + adaptaciones al canal.
5. **Producción** (miniaturas, banners, gráficas, HTML estudio) → respetar paleta e identidad visual en `docs/identidad-visual.md`. Para HTML de estudio, basarse en `ref/Retrotarros_Referencia_Visual_N64.html`.
