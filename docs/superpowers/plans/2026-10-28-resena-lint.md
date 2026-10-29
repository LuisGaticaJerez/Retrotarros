# Lint de reseñas Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Que `generar_resena` verifique solo las reglas escritas del formato, muestre los datos "por confirmar" de una mirada y admita `en_coleccion` de tres estados.

**Architecture:** Módulo nuevo `scripts/resena_lint.py` con funciones puras (`revisar`, `formatear`) y un CLI mínimo. `scripts/resena_deck.py` lo llama antes de escribir el HTML y suma dos retoques de render (bloque `por_confirmar` en notas de la portada, línea de familia en la ficha). Todo campo nuevo es opcional.

**Tech Stack:** Python 3.14 (sin pytest instalado: pruebas con asserts simples ejecutables con `python`), Pillow 12 (ya instalado) para medir la caja.

**Spec:** `docs/superpowers/specs/2026-10-28-resena-lint-design.md`

## Global Constraints

- Texto de pantalla y de notas sin tildes débiles (á é í ó ú ü); la ñ, ¿ y ¡ están permitidas.
- Veredicto: IMPRESCINDIBLE, JUEGAZO, MEMORABLE, COLECCIONABLE (en ese orden de peso).
- `contexto_texto`: meta 50 a 70 palabras, aviso sobre 75.
- Ningún cambio altera el HTML de una reseña que no use los campos nuevos (salida idéntica byte a byte).
- Sin emojis ni guiones largos en código, comentarios, commits y mensajes.
- Commits terminan con `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. En el worktree, usar `git commit -m ... -m "Co-Authored-By..."`.
- No se tocan reseñas ya generadas, grabadas o programadas.

## Review Focus

1. DATA sin `notas` o con `notas: None`: `revisar` no debe fallar con `KeyError`; reporta los bloques faltantes.
2. `veredicto_tag` con minúsculas o espacios ("Juegazo "): se acepta tras `strip().upper()`.
3. `en_coleccion` ausente, o `"familia"` sin `familia_texto`: la ficha se comporta como "no está" sin romperse.
4. Textos de `por_confirmar` con `<`, `>` o `&`: se escapan en el HTML.
5. Campos de pantalla ausentes o `None` (ej. sin `cierre_sub`): `revisar` los ignora sin romperse.

---

### Task 1: Núcleo del lint (errores)

**Files:**
- Create: `scripts/resena_lint.py`
- Create: `scripts/test_resena_lint.py`

**Interfaces:**
- Produces:
  - `ESCALA_VEREDICTO: tuple[str, ...]` = `("IMPRESCINDIBLE", "JUEGAZO", "MEMORABLE", "COLECCIONABLE")`
  - `CAMPOS_PANTALLA: tuple[str, ...]` = `("juego", "gancho_sub", "consola", "developer", "genero", "contexto_texto", "jugabilidad_dato", "audiovisual_dato", "veredicto_resumen", "cierre_sub")`
  - `BLOQUES_NOTAS: tuple[str, ...]` = `("portada", "ficha", "contexto", "comparativa", "jugabilidad", "audiovisual", "veredicto", "cierre")`
  - `revisar(data: dict, out_slug: str) -> tuple[list[str], list[str]]` devuelve `(errores, avisos)`; cada elemento es un mensaje legible.
  - `formatear(errores: list[str], avisos: list[str]) -> str`
- En `scripts/test_resena_lint.py`: `DATA_VALIDA` (dict mínimo sin errores ni avisos, con los 8 bloques de notas, una línea "TRAMA RESUMIDA: ..." en contexto, una línea con "arcade" en ficha, 3 líneas en jugabilidad) y un runner al final que ejecuta toda función `test_*` e imprime `OK n pruebas` o sale con código 1.

- [ ] **Step 1: Write failing tests** en `scripts/test_resena_lint.py`: `test_valida_sin_errores` (DATA_VALIDA da `errores == []`), `test_veredicto_fuera_de_escala` (tag "FUNDACIONAL DEL GENERO" da un error que contiene "veredicto"), `test_veredicto_con_espacios_y_minusculas` (tag " juegazo " no da error; Review Focus 2), `test_tilde_en_pantalla` (contexto_texto con "épica" da error que nombra el campo `contexto_texto`; la ñ en "Año" no da error), `test_falta_trama` (sin línea TRAMA RESUMIDA en `notas.contexto.lineas` da error), `test_falta_arcade` (ficha sin la palabra "arcade", en cualquier mayúscula, da error), `test_sufijo_pedido` (dos casos: `pedido` presente con slug sin `-pedido` da error; `pedido` ausente con slug `resena-x-pedido` da error; consistentes no dan error), `test_sin_notas_no_falla` (`notas` ausente y `notas=None` devuelven errores sin lanzar excepción; Review Focus 1), `test_campos_ausentes_o_none` (quitar `cierre_sub` y poner `gancho_sub=None` no lanza excepción; Review Focus 5).
- [ ] **Step 2: Run** `python scripts/test_resena_lint.py`. Expected: falla con `ModuleNotFoundError: resena_lint`.
- [ ] **Step 3: Implement** `revisar`, `formatear` y las constantes en `scripts/resena_lint.py`. Los errores son los cinco de la sección "Errores" del spec; la detección de tildes usa una regex sobre `[áéíóúüÁÉÍÓÚÜ]` en cada campo de `CAMPOS_PANTALLA`. Los avisos quedan como lista vacía por ahora.
- [ ] **Step 4: Run** `python scripts/test_resena_lint.py`. Expected: `OK 9 pruebas`.
- [ ] **Step 5: Commit** `feat(resenas): nucleo del lint con reglas de error` (agregar ambos archivos).

### Task 2: Avisos del lint

**Files:**
- Modify: `scripts/resena_lint.py`
- Modify: `scripts/test_resena_lint.py`

**Interfaces:**
- Consumes: `revisar`, `DATA_VALIDA`, `BLOQUES_NOTAS` de Task 1.
- Produces: `PALABRAS_CRITICA: tuple[str, ...]` = `("malo", "mala", "peor", "aburrido", "aburrida", "feo", "fea", "no compite", "fracaso", "lento", "lenta", "mediocre")`; `revisar` ahora llena la lista de avisos.

- [ ] **Step 1: Write failing tests**: `test_aviso_contexto_largo` (76 palabras da aviso que cita el conteo; 70 palabras no da aviso), `test_aviso_tildes_en_notas` (tilde en una línea de notas da aviso, no error), `test_aviso_critica_en_pantalla` (veredicto_resumen con "no compite ni de cerca" da aviso; la misma frase solo en notas no da aviso), `test_aviso_orden_plataformas` (consola "PC · PS2" sin línea con "primera" o "primero" en ficha da aviso; con la línea, no), `test_aviso_jugabilidad_corta` (2 líneas dan aviso), `test_aviso_bloques_faltantes` (quitar `notas.cierre` da aviso que nombra "cierre"), `test_aviso_por_confirmar_sin_campo` (notas con "por confirmar" y sin `por_confirmar` da aviso; con el campo lleno, no), `test_aviso_caja_chica` (usar `tempfile` y monkeypatch de la ruta base: ver Step 3; imagen de 256 px da aviso, de 600 px no).
- [ ] **Step 2: Run** `python scripts/test_resena_lint.py`. Expected: fallan las pruebas nuevas.
- [ ] **Step 3: Implement** los ocho avisos de la sección "Avisos" del spec. La ruta de la caja es `studio/resenas/img/resenas/<img_key o slug del juego>.jpg` bajo una constante de módulo `RUTA_CAJAS` (`Path`) que la prueba reemplaza por una carpeta temporal; el ancho se mide con Pillow y, si Pillow o el archivo no existen, se omite el aviso sin error. La búsqueda de palabras de crítica compara en minúsculas y con tildes quitadas, por palabra completa.
- [ ] **Step 4: Run** `python scripts/test_resena_lint.py`. Expected: `OK 17 pruebas`.
- [ ] **Step 5: Commit** `feat(resenas): avisos del lint` .

### Task 3: Integración, `por_confirmar` y `en_coleccion` de tres estados

**Files:**
- Modify: `scripts/resena_deck.py` (funciones `_notas`, `_slide_portada`, `_slide_ficha`, `generar_resena`, constante `CSS`)
- Modify: `scripts/test_resena_lint.py`

**Interfaces:**
- Consumes: `revisar`, `formatear`, `DATA_VALIDA`.
- Produces: `generar_resena(data: dict, out_slug: str, lint: bool = True) -> Path`. El lint se salta si `lint=False` o si la variable de entorno `RESENA_LINT` vale `off`. Con errores lanza `ValueError(formatear(...))` antes de escribir ningún archivo; los avisos se imprimen. Campos nuevos opcionales del DATA: `por_confirmar: list[str]`, `familia_texto: str`, y `en_coleccion` acepta `"familia"`.

- [ ] **Step 1: Write failing tests** (cada una genera con `out_slug="_test-lint-tmp"` y borra `studio/resenas/_test-lint-tmp.html` en un `finally`): `test_generar_con_errores_lanza_y_no_escribe` (tag inválido lanza `ValueError` y el archivo no existe), `test_lint_false_permite_generar` (mismo DATA con `lint=False` escribe el HTML), `test_env_off` (con `RESENA_LINT=off` en `os.environ` también), `test_por_confirmar_en_portada` (el HTML contiene "POR CONFIRMAR ANTES DE GRABAR" antes del primer `<h4>` del aside de la portada y los textos aparecen; sin el campo la cadena no aparece), `test_por_confirmar_escapa_html` (texto con `<b>` y `&` sale escapado; Review Focus 4), `test_ficha_familia` (`en_coleccion="familia"` con `familia_texto` muestra "NO ESTA EN LA COLECCION" y la línea de familia; sin `familia_texto`, solo la etiqueta; Review Focus 3), `test_ficha_booleanos_sin_cambio` (True y False dan la misma etiqueta que antes y sin `ficha-familia`), `test_salida_identica_sin_campos_nuevos` (el HTML de `DATA_VALIDA` generado con el código nuevo es igual al de una copia de `_notas`/`_slide_ficha` anteriores: se compara contra un snapshot guardado en la prueba por hash, generado en el Step 2 antes de modificar).
- [ ] **Step 2: Run** `python scripts/test_resena_lint.py`. Expected: fallan las pruebas nuevas. Antes de tocar `resena_deck.py`, guardar el hash SHA-256 del HTML que hoy produce `DATA_VALIDA` como constante `HASH_ANTERIOR` en el archivo de pruebas.
- [ ] **Step 3: Implement** en `scripts/resena_deck.py`: `_notas(bloque, previo="")` inserta `previo` justo después de abrir el `<aside>`, y renderiza el aside aunque `bloque` sea `None` si `previo` no está vacío; `_slide_portada` pasa como `previo` un `<div class="n-pc"><h4>POR CONFIRMAR ANTES DE GRABAR</h4>` más una `<div class="n-line">` escapada por cada texto de `por_confirmar` (vacío si la lista falta o está vacía); `_slide_ficha` decide con `ec = data.get("en_coleccion")` y `ec is True` para la etiqueta verde, y para `"familia"` agrega `<div class="ficha-familia">` con `familia_texto` escapado si existe; CSS nuevo `.notas .n-pc` (borde amarillo grueso, fondo translúcido) y `.ficha-familia` (tamaño menor que `.ficha-owned`, mismo ancho). `generar_resena` llama a `revisar` al inicio según las reglas de Interfaces, e imprime la lista de `por_confirmar` en consola al terminar.
- [ ] **Step 4: Run** `python scripts/test_resena_lint.py`. Expected: `OK 25 pruebas`, incluida la de salida idéntica.
- [ ] **Step 5: Commit** `feat(resenas): lint integrado, por_confirmar y en_coleccion familia`.

### Task 4: Regresión sobre los drivers existentes y documentación

**Files:**
- Modify: `CLAUDE.md` (sección de reseñas: una regla breve sobre el lint y los campos nuevos)
- Modify: `HANDOFF.md` (nota del cambio)

**Interfaces:**
- Consumes: `generar_resena` con `RESENA_LINT=off`.

- [ ] **Step 1: Run** cada driver de `D:\Recursos Retrotarros\repo\.cache\gen_resena_*.py` con `RESENA_LINT=off` desde el worktree (copiarlos temporalmente a la carpeta de scratchpad si hace falta, ya que están en el repo principal) y luego `git status --short studio/resenas`. Expected: sin cambios en los HTML. Cualquier archivo modificado se revisa: si el cambio viene del código nuevo es un bug a corregir; si viene de que el HTML committeado estaba desfasado del driver, se restaura con `git checkout -- studio/resenas`.
- [ ] **Step 2: Run** los mismos drivers sin `RESENA_LINT=off` y registrar en el HANDOFF qué reseñas dan errores o avisos hoy (informativo, no se corrigen aquí: pueden estar grabadas).
- [ ] **Step 3: Edit** `CLAUDE.md`: una regla corta en la sección de reseñas que diga que `generar_resena` corre el lint, que `lint=False` o `RESENA_LINT=off` es solo para excepciones históricas, y que existen `por_confirmar`, `familia_texto` y `en_coleccion="familia"`. Edit `HANDOFF.md` con el resumen y el resultado del Step 2.
- [ ] **Step 4: Run** `python scripts/test_resena_lint.py` una vez más. Expected: `OK 25 pruebas`.
- [ ] **Step 5: Commit** `docs(resenas): regla del lint y registro de regresion`.
