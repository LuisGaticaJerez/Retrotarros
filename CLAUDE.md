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

## Qué es esto

Canal de YouTube en español sobre **Nostalgia + Juegos + Música** (retrogaming + batería). Proyecto chileno. Ver `docs/proyecto.md` para contexto completo.

> **Tagline público canónico:** `Nostalgia + Juegos + Música`. Es lo que va en banners, gráficas de inicio/fin, headers de pautas y cualquier touchpoint visible al público. Internamente seguimos describiendo el formato como "retrogaming + batería" porque eso describe la mecánica (juegos retro + Koko tocando), pero el tagline al público es el de arriba.

## Protagonistas

- **Luis Balbrigame** — rigor histórico, investigación, estructura narrativa. Cámara en lane Luis.
- **Koko** — colección física grande de juegos/consolas, toca batería. Cámara en lane Koko y episodios largos.

## REGLA INMUTABLE — Tono y lengua

Todo output de cara al público en **español chileno neutro**:

- **Sí**: "po", "espérate", "déjanos", "suscríbete", "tení", "mira" — marcas chilenas suaves y naturales.
- **No**: voseo rioplatense ("vos sabés", "che"), mexicanismos ("órale", "güey"), españolismos ("vale", "tío", "guay").
- Registro conversacional — dos chilenos en un café, no locutores de noticiero.
- Si el output sale con marcas regionales equivocadas → corregir y reescribir.

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

**Cómo encontrar la caja correcta:**
1. Wikipedia API: `https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=<juego>+cover&srnamespace=6&format=json` → buscar `File:<Juego> Cover.png` o `.jpg`.
2. Si Wikipedia no la tiene → MobyGames, LaunchBox, TheGamesDB, o página específica del juego en Wikipedia (no del compositor/serie).
3. Verificar con `Read` tool antes de commitear — si sale logo/wordmark/screenshot, descartar y buscar otra.
4. Si NO existe box art accesible → usar fallback CSS estilizado (ya implementado con clase `cart-fallback`), nunca dejar un logo en su lugar.

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
2. **Regenerar capturas** (si tocaste HTMLs) — `python scripts/capture-slides.py <slug>` para cada HTML modificado.
3. **Sync a Drive** — copiar imágenes, HTMLs, DOCX y **capturas** a `G:\Mi unidad\Studio\<slug>\`. Sin esto el PC del estudio queda desactualizado.
4. **Avisar a Luis** del SHA del último commit + qué cambió.

**Anti-patrón:** dejar cambios solo en el repo o solo en Drive. Las tres ubicaciones (repo local, GitHub, Drive del estudio) deben quedar sincronizadas al cerrar la sesión.

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

## Cómo arrancar una sesión

Identificar el escenario y revisar archivos relevantes antes de proponer output:

1. **Short nuevo** → preguntar lane (Luis o Koko) + tema + consultar `docs/guiones-shorts.md` para no repetir ángulos.
2. **Pauta episodio largo** → `docs/estrategia.md` para formato + `data/coleccion_koko.csv` para chequear colección. Generar los tres archivos (pauta + discusión + html) en el mismo flujo, con el mismo slug.
3. **Investigar compositor** → `docs/briefings-compositores.md`, agregar ficha si es nuevo.
4. **Brainstorm tendencias** → revisar redes, traer 3–5 formatos que peguen ahora + adaptaciones al canal.
5. **Producción** (miniaturas, banners, gráficas, HTML estudio) → respetar paleta e identidad visual en `docs/identidad-visual.md`. Para HTML de estudio, basarse en `ref/Retrotarros_Referencia_Visual_N64.html`.
