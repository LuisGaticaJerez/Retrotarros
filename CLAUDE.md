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

| Archivo | Rol |
|---|---|
| `Retrotarros_Estrategia.docx` | Documento maestro: nombre, enfoques, formatos, plan 3 meses, Indie Lat, identidad visual. |
| `Retrotarros_Briefings_Compositores.docx` | Fichas de compositores (Kondo, Uematsu, Mitsuda, Yamaoka, Wise, Kirkhope, etc.). Documento vivo. |
| `Retrotarros_Guiones_Shorts.docx` | Guiones lane Luis: timings, B-roll, título YouTube, caption, hashtags, datos de respaldo. Documento vivo. |
| `Retrotarros_Pauta_N64_v3_ranking_corregido.docx` | Pauta episodio largo Top N64 formato game show. |
| `Retrotarros_Catalogo_Juegos.xlsx` | **Fuente de verdad** de la colección física de Koko. Leer con `openpyxl`/`pandas`. |
| `Retrotarros_Referencia_Visual_N64.html` | Referencia visual de miniaturas/gráficas episodio N64. |

## Reglas operativas

### Lectura de archivos
- **Excel** (`.xlsx`): siempre con `openpyxl` o `pandas`. Nunca asumir contenido sin abrirlo.
- **Word** (`.docx`): `python-docx` para editar; extracción de texto para lectura.
- Antes de proponer guiones, **revisar el catálogo Excel** para confirmar que Koko tiene el juego.

### Creación de contenido
- Lane Luis y lane Koko son carriles distintos — no mezclar en un short sin indicación explícita.
- Todo short incluye: duración, talento, tono, guión con timings, B-roll por bloque, título YouTube, caption, hashtags, notas de producción y **datos de respaldo** verificables.
- Todo largo respeta la estructura de 5 bloques salvo formatos especiales (game show, etc.).
- Cada episodio largo debe sangrar mínimo 6 shorts (idealmente 8), divididos por lane.

### Datos y verificación
- **Toda afirmación histórica o de precio debe poder defenderse**. Sin respaldo → no va al guión.
- Precios: fuente primaria PriceCharting + GameRant/The Gamer/Vgprice. Siempre aclarar **NTSC USA, CIB**.
- Datos históricos: cruzar mínimo dos fuentes antes de meter número o fecha en cámara.

### Output esperado
- `.docx` para pautas, guiones, briefings (materiales que se imprimen y van al rodaje).
- Markdown para discusión interna o brainstorm.
- Archivos descargables reales — no solo mostrar contenido en chat.

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

1. **Short nuevo** → preguntar lane (Luis o Koko) + tema + consultar `Retrotarros_Guiones_Shorts.docx`.
2. **Pauta episodio largo** → `Retrotarros_Estrategia.docx` para formato + `Retrotarros_Catalogo_Juegos.xlsx` para chequear colección.
3. **Investigar compositor** → `Retrotarros_Briefings_Compositores.docx`, agregar ficha si es nuevo.
4. **Brainstorm tendencias** → revisar redes, traer 3–5 formatos que peguen ahora + adaptaciones al canal.
5. **Producción** (miniaturas, banners, gráficas) → respetar paleta e identidad visual en `docs/identidad-visual.md`.
