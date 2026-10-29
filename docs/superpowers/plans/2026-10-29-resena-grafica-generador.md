# Gráfica nueva de las reseñas, generador y lint: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Que `generar_resena` produzca la gráfica nueva (portada con caja, chips en la ficha, veredicto con escala, contexto con imagen, viñetas de jugabilidad, crédito del compositor y próxima reseña) cuando el DATA trae `grafica="nueva"`, sin cambiar ni un byte de lo que ya se genera hoy.

**Architecture:** Cada slide de `scripts/resena_deck.py` gana una rama `nueva` que se activa solo con `data.get("grafica") == "nueva"`; el CSS nuevo vive en una constante `CSS_NUEVA` que se agrega al HTML solo en ese caso. El lint (`scripts/resena_lint.py`) valida la marca y los campos nuevos. Las pruebas van en un archivo nuevo `scripts/test_resena_grafica.py` más ampliaciones de `scripts/test_resena_lint.py`.

**Tech Stack:** Python 3.14 sin pytest (pruebas con asserts, ejecutables con `python`), Playwright para la revisión visual.

**Spec:** `docs/superpowers/specs/2026-10-29-resena-grafica-design.md`. Referencia visual y CSS de los mockups: `docs/superpowers/specs/2026-10-29-resena-grafica-mockups/mock1.py` y `mock2.py` (el JS inyectado de cada una es el CSS y el HTML de partida).

## Global Constraints

- Sin la marca `grafica`, o con `grafica="clasica"`, el HTML generado es idéntico byte a byte al actual: `test_salida_identica_sin_campos_nuevos` (hash en `scripts/test_resena_lint.py`) debe seguir pasando en cada tarea.
- Todo texto que sale en pantalla va sin tildes débiles y sin crítica (reglas del lint).
- Todo texto nuevo del DATA que se inserta en el HTML pasa por `_esc`.
- Sin emojis ni guiones largos en código, comentarios, mensajes y commits.
- Commits sin `Co-Authored-By` (regla del `CLAUDE.md` del canal).
- Suites que deben quedar en verde en cada tarea: `PYTHONIOENCODING=utf-8 python scripts/test_resena_lint.py`, `... test_resena_kit.py` y `... test_resena_grafica.py` (esta última nace en la Tarea 1).

## Review Focus

1. DATA con `grafica="nueva"` pero sin caja en `studio/resenas/img/resenas/`: portada, contexto y cierre no se rompen y quedan como hoy (sin imagen).
2. `plataformas` con elementos mal formados (un elemento de 1 solo valor, vacío o `None`): no lanza excepción.
3. `veredicto_tag` fuera de la escala con `grafica="nueva"`: sin píldora encendida y sin excepción.
4. Textos nuevos con `<`, `>`, `&` o comillas (viñetas, compositor, `proxima`): salen escapados.
5. `jugabilidad_vinetas` con 2 o 4 elementos: el lint da error y, con el lint apagado, el generador usa solo el bloque de texto de hoy sin lanzar excepción.

---

### Task 1: Marca `grafica` y reglas del lint

**Files:**
- Modify: `scripts/resena_lint.py`
- Modify: `scripts/test_resena_lint.py`
- Create: `scripts/test_resena_grafica.py`

**Interfaces:**
- Produces, en `scripts/resena_lint.py`: `GRAFICAS = ("nueva", "clasica")`; `revisar` aplica las reglas nuevas (abajo) y la lista `CAMPOS_PANTALLA` no cambia. Una función `_textos_nuevos(data: dict) -> list[tuple[str, str]]` devuelve pares `(nombre_del_campo, texto)` de los textos nuevos de pantalla: cada título y texto de `jugabilidad_vinetas`, `audiovisual_compositor`, `proxima.juego`, `proxima.consola` y cada nombre de `plataformas`; ignora sin lanzar excepción lo que no sea del tipo esperado.
- Produces, en `scripts/resena_deck.py`: `_nueva(data: dict) -> bool` (`True` si `data.get("grafica") == "nueva"`).
- En `scripts/test_resena_grafica.py`: runner igual al de los otros archivos de prueba y un helper `_generar(data, **kw) -> str` que genera con `out_slug="_test-grafica-tmp"`, devuelve el HTML y borra el archivo. Importa `_data` de `test_resena_lint`.
- `DATA_VALIDA` en `scripts/test_resena_lint.py` gana `"grafica": "clasica"`.

Reglas del lint a agregar:
- Error: `grafica` presente con un valor fuera de `GRAFICAS`.
- Error: `jugabilidad_vinetas` presente con una cantidad de elementos distinta de 3.
- Error: tildes débiles en los textos de `_textos_nuevos`.
- Aviso: palabras de crítica dura en esos mismos textos.
- Aviso: `grafica` ausente ("sale con la gráfica clásica; las reseñas nuevas deben llevar grafica=\"nueva\"").
- Aviso: `grafica="nueva"` sin `jugabilidad_vinetas`.
- Aviso: `grafica="nueva"` con varias plataformas en `consola` (separadas por `·`) y sin `plataformas`.

- [ ] **Step 1: Write failing tests** en `scripts/test_resena_lint.py` (con los nombres exactos): `test_grafica_valor_invalido` (`grafica="otra"` da error que nombra `grafica`), `test_grafica_ausente_avisa` (`DATA_VALIDA` sin la clave da aviso que nombra `grafica="nueva"`; con `"clasica"` o `"nueva"` no da ese aviso), `test_vinetas_cantidad` (2 y 4 viñetas dan error que nombra `jugabilidad_vinetas`; 3 no), `test_vinetas_tilde_y_critica` (tilde en un título de viñeta da error; la palabra `aburrido` da aviso), `test_textos_nuevos_con_tilde` (tilde en `audiovisual_compositor` y en `proxima.juego` dan error cada uno), `test_nueva_sin_vinetas_ni_plataformas_avisa` (`grafica="nueva"` sin viñetas da aviso; con `consola="PC · PS2"` y sin `plataformas` da aviso; con `plataformas` no), `test_textos_nuevos_mal_formados_no_fallan` (`jugabilidad_vinetas=[None, 5, ["solo uno"]]`, `proxima="texto"`, `plataformas=[None, ["PC"]]` no lanzan excepción). Ajustar `test_valida_sin_avisos` si hace falta tras el cambio de `DATA_VALIDA`.
- [ ] **Step 2: Run** `PYTHONIOENCODING=utf-8 python scripts/test_resena_lint.py`. Expected: fallan las pruebas nuevas.
- [ ] **Step 3: Implement** las reglas en `scripts/resena_lint.py`, `_nueva` en `scripts/resena_deck.py` y el archivo `scripts/test_resena_grafica.py` con su runner y helper (sin pruebas todavía: el runner debe imprimir `OK 0 pruebas`).
- [ ] **Step 4: Run** las tres suites. Expected: lint `OK 38 pruebas` (31 + 7), kit `OK 21 pruebas`, grafica `OK 0 pruebas`.
- [ ] **Step 5: Commit** `feat(resenas): marca grafica y reglas del lint para la gráfica nueva`.

### Task 2: Portada con la caja de fondo y veredicto con escala

**Files:**
- Modify: `scripts/resena_deck.py` (`_slide_portada`, `_slide_veredicto`, constante nueva `CSS_NUEVA`, `generar_resena`)
- Modify: `scripts/test_resena_grafica.py`

**Interfaces:**
- Consumes: `_nueva`, `_generar`.
- Produces: constante `CSS_NUEVA: str` en `scripts/resena_deck.py` (al agregar CSS en tareas siguientes se extiende esta constante) y la regla en `generar_resena`: `css += CSS_NUEVA` solo si `_nueva(data)`.
- Marcas de HTML: portada, `<div class="portada-fondo">` (con la imagen como fondo desenfocado) y `<img class="portada-caja" ...>`; solo si la caja existe. Veredicto: `<div class="ver-escala">` con cuatro `<div class="ver-pill">` en orden `IMPRESCINDIBLE, JUEGAZO, MEMORABLE, COLECCIONABLE`, y `ver-pill on` en la que coincide con `veredicto_tag` (sin distinguir mayúsculas ni espacios).

- [ ] **Step 1: Write failing tests** en `scripts/test_resena_grafica.py`: `test_portada_nueva_con_caja` (`_data(grafica="nueva", img_key="the-sims")`: contiene `class="portada-fondo"` y `class="portada-caja"`), `test_portada_nueva_sin_caja` (con `img_key` inexistente no contiene ninguno de los dos y genera sin excepción; Review Focus 1), `test_portada_clasica_sin_cambios` (con `"clasica"` y con `img_key="the-sims"` no aparecen), `test_veredicto_nueva_escala` (contiene exactamente 4 `class="ver-pill` y exactamente 1 `ver-pill on`, y la encendida es la de `JUEGAZO` cuando el tag es `" juegazo "`), `test_veredicto_nueva_tag_fuera_de_escala` (con `veredicto_tag="X"` y `lint=False` hay 4 pastillas y 0 encendidas; Review Focus 3), `test_veredicto_clasica_sin_escala` (no aparece `ver-escala`).
- [ ] **Step 2: Run** `PYTHONIOENCODING=utf-8 python scripts/test_resena_grafica.py`. Expected: fallan las 6 pruebas.
- [ ] **Step 3: Implement** las ramas `nueva` de las dos funciones y `CSS_NUEVA` con las reglas de portada y veredicto, tomando el estilo de los mockups (`mock1.py`, variables `PORTADA` y `VEREDICTO`): fondo con `filter: blur(18px) brightness(.38) saturate(1.2)`, caja inclinada 3° a ~70 % de alto, título alineado a la izquierda; píldoras de Orbitron 20 px, la encendida amarilla con sombra.
- [ ] **Step 4: Run** las cuatro suites. Expected: grafica `OK 6 pruebas`, lint `OK 38`, kit `OK 21`.
- [ ] **Step 5: Commit** `feat(resenas): portada con caja de fondo y veredicto con escala`.

### Task 3: Ficha con chips y contexto con imagen

**Files:**
- Modify: `scripts/resena_deck.py` (`_slide_ficha`, `_slide_contexto`, `CSS_NUEVA`)
- Modify: `scripts/test_resena_grafica.py`

**Interfaces:**
- Consumes: `_nueva`, `_generar`, `CSS_NUEVA`.
- Marcas de HTML: ficha, `<div class="chips">` con un `<span class="chip">` por plataforma (el primero `chip first`), cada uno con el nombre en mayúsculas y, si hay año, un `<i>` con el año, separados por `<span class="arr">`. Contexto: `<img class="ctx-img" ...>` junto al texto, solo si la caja existe, y la clase `con-imagen` en el contenedor `.contexto`.
- Fuente de los chips: `data["plataformas"]` (lista de pares `[nombre, año]`); si falta o no tiene ningún par válido, se arma de `consola` separada por `·` sin año.

- [ ] **Step 1: Write failing tests**: `test_ficha_chips_con_plataformas` (`plataformas=[["PC","2000"],["PS2","2003"]]`: dos `class="chip` con exactamente un `chip first`, los años `2000` y `2003` dentro de `<i>`), `test_ficha_chips_desde_consola` (`consola="PC · Mac"` sin `plataformas`: dos chips sin `<i>`), `test_ficha_chips_una_plataforma` (`consola="PC"`: un chip), `test_ficha_plataformas_mal_formadas` (`plataformas=[None, ["PC"], [], ["PS2","2003"]]` con `lint=False` no lanza excepción y cuenta solo los pares válidos o cae a `consola`; Review Focus 2), `test_ficha_clasica_sin_chips` (con `"clasica"` no aparece `class="chips"`), `test_contexto_nueva_con_imagen` (`img_key="the-sims"`: aparecen `class="ctx-img"` y `con-imagen`), `test_contexto_nueva_sin_imagen` (`img_key` inexistente: ninguno de los dos), `test_contexto_clasica_sin_imagen`.
- [ ] **Step 2: Run** la suite grafica. Expected: fallan las 8.
- [ ] **Step 3: Implement** ambas ramas y el CSS (mockups: `FICHA` en `mock1.py`, `CTX_IMG` en `mock2.py`).
- [ ] **Step 4: Run** las cuatro suites. Expected: grafica `OK 14 pruebas`.
- [ ] **Step 5: Commit** `feat(resenas): ficha con chips de plataforma y contexto con imagen`.

### Task 4: Viñetas de jugabilidad, crédito del compositor y próxima reseña

**Files:**
- Modify: `scripts/resena_deck.py` (`_slide_tarrovision` o las funciones que construyen las slides de jugabilidad y audiovisual, `_slide_cierre`, `CSS_NUEVA`)
- Modify: `scripts/test_resena_grafica.py`

**Interfaces:**
- Consumes: `_nueva`, `_generar`, `CSS_NUEVA`.
- Marcas de HTML: jugabilidad, `<div class="gp-vinetas">` con tres `<div class="vineta">` (número `01` a `03`, título y texto), que reemplaza el bloque `gp-dato`; solo si `jugabilidad_vinetas` tiene exactamente 3 elementos válidos, si no queda el bloque de hoy. Audiovisual: `<div class="gp-compositor">` con la etiqueta `BANDA SONORA` y el texto de `audiovisual_compositor`, debajo del dato, solo si el campo existe. Cierre: `<div class="cierre-proxima">` con `PROXIMA RESEÑA`, `proxima["juego"]` y `consola · año`, más `<img>` de la caja si `proxima["img_key"]` existe en `studio/resenas/img/resenas/`; solo si `proxima` es un diccionario con `juego`.

- [ ] **Step 1: Write failing tests**: `test_jugabilidad_vinetas` (3 viñetas: aparece `class="gp-vinetas"`, exactamente 3 `class="vineta"`, números `01`, `02`, `03`, y no aparece `class="gp-dato"` en esa slide), `test_jugabilidad_vinetas_cantidad_invalida` (2 y 4 viñetas con `lint=False`: sin excepción y aparece `gp-dato`; Review Focus 5), `test_jugabilidad_clasica_ignora_vinetas` (con `"clasica"` y viñetas no aparece `gp-vinetas`), `test_compositor` (aparece `class="gp-compositor"`, `BANDA SONORA` y el texto escapado; sin el campo no aparece), `test_cierre_proxima` (con `proxima={"juego":"God of War","consola":"PlayStation 2","anio":"2005","img_key":"god-of-war"}`: aparece `class="cierre-proxima"`, `God of War`, `PlayStation 2 · 2005` y un `<img` dentro de la tarjeta), `test_cierre_proxima_sin_imagen_ni_campo` (`img_key` inexistente: tarjeta sin `<img`; sin `proxima` o con `proxima="texto"`: sin tarjeta y sin excepción), `test_textos_nuevos_escapados` (viñetas, compositor y `proxima.juego` con `<b>&` salen como `&lt;b&gt;&amp;`; Review Focus 4), `test_clasica_no_tiene_ninguna_marca_nueva` (con `"clasica"` y todos los campos nuevos puestos, no aparece ninguna de las clases `portada-fondo`, `ver-escala`, `chips`, `ctx-img`, `gp-vinetas`, `gp-compositor`, `cierre-proxima`).
- [ ] **Step 2: Run** la suite grafica. Expected: fallan las 8.
- [ ] **Step 3: Implement** las tres ramas y el CSS (mockups: `JUGAB`, `AUDIO` y `CIERRE` en `mock2.py`).
- [ ] **Step 4: Run** las cuatro suites. Expected: grafica `OK 22 pruebas`.
- [ ] **Step 5: Commit** `feat(resenas): vinetas de jugabilidad, credito del compositor y proxima resena`.

### Task 5: Regresión, revisión visual y documentación

**Files:**
- Modify: `CLAUDE.md` (sección de reseñas), `HANDOFF.md`

**Interfaces:**
- Consumes: todo lo anterior.

- [ ] **Step 1: Regresión sobre los 49 drivers.** En memoria, sin escribir en `studio/`: para cada driver de `.cache/gen_resena_*.py`, comparar el HTML que genera el generador anterior (`git show 8521241:scripts/resena_deck.py` cargado como módulo aparte) contra el actual, ambos con `RESENA_LINT=off`. Expected: 0 diferencias en 49. Cualquier diferencia es un bug.
- [ ] **Step 2: Revisión visual.** Generar The Sims con todos los campos nuevos (`grafica="nueva"`, `plataformas` con años, 3 viñetas, compositor y `proxima`) en un slug temporal `resena-the-sims-grafica-prueba`, correr `python scripts/capture-slides.py resena-the-sims-grafica-prueba`, abrir las 8 capturas, comprobar que no hay desbordes ni texto cortado, y luego borrar el HTML y la carpeta de capturas del slug temporal.
- [ ] **Step 3: Edit** `CLAUDE.md` con la regla de la gráfica nueva (toda reseña nueva lleva `grafica="nueva"`, y cuando se pueda `plataformas` con año, `jugabilidad_vinetas`, `audiovisual_compositor`; `proxima` se agrega después de grabar y se regeneran las capturas del cierre; los campos y avisos) y `HANDOFF.md` con una nota breve y el pendiente de la migración del backlog (fase 2).
- [ ] **Step 4: Run** las cuatro suites una vez más. Expected: lint `OK 38 pruebas`, kit `OK 21`, grafica `OK 22`.
- [ ] **Step 5: Commit** `docs(resenas): regla de la gráfica nueva y registro de regresión`.
