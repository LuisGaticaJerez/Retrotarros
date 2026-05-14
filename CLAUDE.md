# Retrotarros — Claude Code Project Instructions

> Lee este archivo completo antes de cualquier acción. Después lee `HANDOFF.md` y los docs relevantes al escenario.

## Qué es esto

Canal de YouTube en español sobre **retrogaming + batería**. Proyecto chileno. Ver `docs/proyecto.md` para contexto completo.

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
