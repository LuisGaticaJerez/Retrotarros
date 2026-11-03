# Gráfica nueva de los rankings: plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Agregar a `scripts/top_deck.py` una gráfica nueva opcional (`data["grafica"] = "nueva"`) con mosaico de portada, divisores con tarjeta y slide de juego con fondo de caja, chips y barra de progreso, sin alterar ningún ranking existente.

**Architecture:** Código nuevo en `scripts/top_grafica.py`. `top_deck.generar_top` lo importa solo con la marca y, para cada slide, pide a ese módulo la versión nueva, que parte del HTML clásico y le aplica reemplazos exactos (sin la marca el camino es el de siempre). Una prueba de regresión con base congelada y hashes guarda que lo clásico no cambia.

**Tech Stack:** Python 3.14, Pillow (ya usado por `top_deck`), Playwright (ya usado por `capture-slides.py`), pruebas `test_*` sin pytest (patrón de `scripts/test_resena_grafica.py`).

**Spec:** `docs/superpowers/specs/2026-11-02-rankings-grafica-design.md`. Mockups (solo ayuda visual, locales de este worktree): `.superpowers/brainstorm/1112-1793669109/content/`.

## Global Constraints

- Sin la marca, o con `"clasica"`, el HTML generado es idéntico byte a byte al de hoy. Cualquier otro valor de `grafica` lanza `ValueError`.
- No cambian: TarroVision (tamaño y posición), `_tv_css()` (letra grande), precio grande arriba a la derecha (`.game-price`), capa de notas, layouts `alta`/`ancha`/`clasica`.
- Texto en pantalla sin tildes. La caja es siempre la box art real, nunca el logo.
- Unidades del deck: px a 1920x1080 (el deck es de px, no de `cqw`; los mockups usaron `cqw`, 1 cqw = 19,2 px).
- Mosaico solo si hay al menos 6 imágenes de caja entre los ítems del ranking; si no, portada y divisores salen como hoy.
- Barra: miniaturas (Top Mundial, Top Peores, Infravalorados) o casillas numeradas (Top Precios); centrada y fija; nunca toca la etiqueta de la izquierda, el precio ni el TarroVision (mínimo 100 px libres a 1920 px).
- Commits con `git commit -m` (en este worktree `.git` es un archivo), sin `Co-Authored-By`. No hacer push. No regenerar ni pisar ningún deck existente: toda prueba y revisión usa slugs temporales `zz-...` y los borra.

## Review Focus

1. Ranking con menos de 10 ítems (ej. 8): el mosaico debe completar sus 10 celdas repitiendo cajas y la barra debe tener solo 8 elementos (Task 3 y 5).
2. `img` apunta a un archivo que no existe o que Pillow no abre: `_img_size` da `None`; la miniatura debe salir cuadrada y nada debe lanzar excepción (Task 5).
3. `meta` personalizado con precio adentro (ej. `NES · 1992 · ACTIVE ENTERPRISES · NO LANZADO · ~USD 1.926`): el precio no debe salir como chip, y con más de 5 partes se mantiene la línea gris de hoy (Task 4).
4. Etiqueta larga (`badge_text`) junto a una barra de 17 casillas: la etiqueta se parte en dos líneas y no pisa la barra (Task 6).
5. Divisor sin `color` ni `notas` en el `data`: debe usar cian por defecto y no romper (Task 3).

---

## File Structure

- Create `scripts/top_grafica.py`: todo el código de la gráfica nueva (CSS, mosaico, tarjeta, chips, barra, variantes de slide).
- Modify `scripts/top_deck.py` (`generar_top`, líneas ~410-451): validar la marca, importar `top_grafica`, agregar su CSS y desviar las tres funciones de slide. Nada más.
- Create `scripts/test_top_grafica.py`: pruebas de HTML (regresión + gráfica nueva).
- Create `scripts/test_top_grafica_visual.py`: pruebas con Playwright (TarroVision idéntico, sin superposiciones).
- Create `scripts/fixtures_top_grafica/base_congelada.html` y `golden.json`: base HTML congelada y hashes de lo clásico.
- Modify `CLAUDE.md`, `HANDOFF.md`, `docs/modus-operandi/bitacora-decisiones.md`: regla y estado.

---

### Task 1: Regresión de lo clásico (antes de tocar el código)

**Files:**
- Create: `scripts/test_top_grafica.py`, `scripts/fixtures_top_grafica/base_congelada.html` (copia exacta de `studio/rankings/top-mundial/snes-top-mundial.html`), `scripts/fixtures_top_grafica/golden.json`

**Interfaces:**
- Produces (en `test_top_grafica.py`, lo usan todas las tareas siguientes):
  - `SLUG_M = "zz-prueba-grafica-top-mundial"`, `SLUG_P = "zz-prueba-grafica-top-precios"`, `SLUG_X = "zz-prueba-grafica-top-peores"` (cada slug cae en su carpeta por `episode_category`).
  - `_data_mundial(n: int = 10, cajas: int = 10, **extra) -> dict`: ranking con `n` ítems `pos` n..1 (títulos `Juego 10`, ... con `ano`, `editor`, `why`), de los cuales los primeros `cajas` tienen imagen temporal (formas cíclicas: vertical 200x300, cuadrada 240x240, horizontal 300x200). Incluye `portada`, `intro`, `analisis`, `cliffhanger`, `header_tag`, `doc_title`, `consola`.
  - `_data_precios(**extra) -> dict`: 10 retail con `price` (`USD 100`...), `rarezas_divider`, 3 `rarezas` (`badge_text`, `block_label`, `price`) y un `grial`.
  - `_generar(data: dict, slug: str) -> str`: asegura que existan las imágenes temporales, llama a `top_deck.generar_top(data, slug)` con `top_deck.BASE` apuntando a `base_congelada.html`, devuelve el HTML y borra el HTML generado.
  - `main() -> int`: crea las imágenes temporales bajo `studio/rankings/<cat>/img/<slug>/<slug-del-título>.jpg`, corre todas las `test_*`, limpia en `finally`; con `--golden` escribe `golden.json` en vez de probar.

- [ ] **Step 1: Escribir el arnés y las pruebas de regresión** en `scripts/test_top_grafica.py`: `test_clasica_golden_mundial` (`sha256(_generar(_data_mundial(), SLUG_M)) == GOLDEN["mundial"]`), `test_clasica_golden_precios` (igual con `_data_precios()` y `GOLDEN["precios"]`), `test_clasica_explicita_igual` (`{**data, "grafica": "clasica"}` da el mismo hash).
- [ ] **Step 2: Congelar la base y generar los hashes** con el código actual, sin modificar `top_deck.py`: copiar el archivo base a `scripts/fixtures_top_grafica/base_congelada.html`, correr `python scripts/test_top_grafica.py --golden` y verificar que `golden.json` trae las claves `mundial` y `precios`.
- [ ] **Step 3: Verificar que las pruebas pasan**

Run: `python scripts/test_top_grafica.py`
Expected: `OK 3 pruebas`, y `git status` sin archivos `zz-prueba-*` sobrantes en `studio/`.

- [ ] **Step 4: Commit** `test(rankings): regresion byte a byte de la grafica clasica`.

---

### Task 2: Marca, módulo y enganches

**Files:**
- Create: `scripts/top_grafica.py`
- Modify: `scripts/top_deck.py` (`generar_top`)
- Test: `scripts/test_top_grafica.py`

**Interfaces:**
- Consumes: `_data_mundial`, `_generar`, `SLUG_M` (Task 1).
- Produces (`top_grafica.py`): `css_nueva() -> str` (CSS de todo lo nuevo; por ahora solo la regla marcadora `.g-nueva{}` y se amplía en las tareas siguientes) y `slide_portada(num: int, data: dict, out_slug: str) -> str`, `slide_divisor(num: int, d: dict, data: dict, out_slug: str) -> str`, `slide_item(num: int, it: dict, consola: str, ch: int, box: str, out_slug: str, data: dict, indice: int) -> str`; las tres devuelven, por ahora, la versión clásica llamando a `top_deck._slide_*`. Helper `_inyectar(html: str, viejo: str, nuevo: str) -> str` (reemplaza una sola vez y lanza `RuntimeError` si `viejo` no está).
- Produces (`top_deck.py`): en `generar_top`, `G` es el módulo `top_grafica` o `None`; el CSS extra y las tres funciones de slide pasan por `G` cuando existe.

- [ ] **Step 1: Escribir las pruebas que fallan**: `test_marca_invalida_error` (para `"Nueva"`, `"nuevo"`, `None`, `generar_top` lanza `ValueError`), `test_nueva_agrega_css` (el HTML con `grafica="nueva"` contiene `.g-nueva{}` y sigue conteniendo `.game-why{font-size:32px !important` y `.game-price{`), `test_clasica_no_importa_modulo_nuevo` (tras generar una vez sin marca en un proceso limpio, `"top_grafica" not in sys.modules`; correr la comprobación con `subprocess` para no depender del orden de las pruebas).
- [ ] **Step 2: Verificar que fallan** — Run: `python scripts/test_top_grafica.py` — Expected: FALLAN las 3 pruebas nuevas, pasan las de Task 1.
- [ ] **Step 3: Implementar** `top_grafica.py` con las firmas de Interfaces, y en `generar_top`: antes de tocar `base`, validar `data.get("grafica", "clasica") in ("clasica", "nueva")` (si no, `ValueError` con el valor recibido); `G = None`, y si es `"nueva"`, `import top_grafica as G`. Pasar `extra_css=data.get("css_extra","") + (G.css_nueva() if G else "")` a `_shared_css`, y reemplazar las llamadas a `_slide_portada`, `_slide_divider` (intro, rarezas_divider, analisis, cliffhanger) y `_slide_item` (items, rarezas, grial) por la de `G` cuando `G` existe, sin cambiar la numeración ni el orden. `indice` es la posición del slide de juego dentro de la secuencia retail, rarezas, grial (0 a N-1).
- [ ] **Step 4: Verificar que pasan** — Run: `python scripts/test_top_grafica.py` — Expected: `OK 6 pruebas`.
- [ ] **Step 5: Commit** `feat(rankings): marca grafica y modulo top_grafica con enganches`.

---

### Task 3: Portada con mosaico y divisores con tarjeta

**Files:**
- Modify: `scripts/top_grafica.py`
- Test: `scripts/test_top_grafica.py`

**Interfaces:**
- Consumes: `T._auto_img`/`img` ya resuelto por `generar_top` en cada ítem, `T._slide_portada`, `T._slide_divider`, `T._slug`.
- Produces: `mosaico(data: dict, out_slug: str, tenue: bool) -> str`: `""` si hay menos de 6 ítems (retail, rarezas y grial) con `img`; si no, `<div class="g-mos [tenue]">` con 10 celdas `<i style="background-image:url(...)">` (celda sin caja: `<i class="g-lb lb-xxx">`, con `lb-xxx` el `lb` del ítem o `lb-default`). Orden: lista de ítems barajada con `random.Random(out_slug)`; si hay menos de 10, se repite cíclicamente. `slide_portada` y `slide_divisor` devuelven el clásico con `class="slide active g-nueva"` / `class="slide g-nueva g-div g-<color>"` y el mosaico insertado tras el `slide-num`, o el clásico intacto si `mosaico` da `""`. Color por defecto del divisor `cy`.

- [ ] **Step 1: Escribir las pruebas que fallan**: `test_portada_nueva_con_mosaico` (10 celdas, `slide active g-nueva`), `test_divisores_nueva_con_tarjeta_y_color` (el divisor magenta lleva `g-mg`, el `intro` con `color` `cy`; uno sin `color` lleva `g-cy`; los 3 divisores de `_data_mundial` y los 4 de `_data_precios` llevan `g-mos tenue`), `test_menos_de_6_cajas_sin_mosaico` (`_data_mundial(cajas=5)` con marca da HTML sin `g-mos` y con `<section class="slide active">`), `test_mosaico_determinista_y_barajado` (dos generaciones iguales; el orden de las imágenes en el mosaico no es el del ranking), `test_mosaico_con_8_items_completa_10_celdas`, `test_celda_sin_caja_usa_color_de_etiqueta` (`_data_mundial(cajas=7)`: tres celdas `g-lb`, tipo `lb-default` si el ítem no trae `lb`).
- [ ] **Step 2: Verificar que fallan** — Run: `python scripts/test_top_grafica.py` — Expected: FALLAN las 6 nuevas.
- [ ] **Step 3: Implementar** las dos funciones y `mosaico`, y ampliar `css_nueva()` con la grilla 5x2 del mosaico (celdas con `background-size:cover`, `filter:blur(10px) brightness(.35) saturate(1.2)`; `tenue` más oscuro, `brightness(.24)`), la tarjeta (`.slide.g-div` flex centrado; `.divider` con `background:rgba(6,3,15,.72)`, borde de 3 px cian o magenta con brillo, `border-radius:14px`, ancho `min(1500px,78%)`, `height:auto`, padding `48px 64px`) y el texto de portada sobre el mosaico con sombra. Valores finos: partir de `portada.html` y `divisores.html` de los mockups.
- [ ] **Step 4: Verificar que pasan** — Run: `python scripts/test_top_grafica.py` — Expected: `OK 12 pruebas`.
- [ ] **Step 5: Commit** `feat(rankings): portada con mosaico y divisores con tarjeta`.

---

### Task 4: Slide de juego, fondo y chips

**Files:**
- Modify: `scripts/top_grafica.py`
- Test: `scripts/test_top_grafica.py`

**Interfaces:**
- Consumes: `T._slide_item(num, it, consola, ch, box, out_slug)`.
- Produces: `chips(it: dict, consola: str) -> str`: `<div class="game-meta g-chips">...</div>` con un `<span class="g-chip">` por parte (el año, parte que empieza con 4 dígitos, lleva `g-chip y`), o `""` si no corresponde. Partes: `it["meta"]` separado por `·` si existe, si no `consola`, `ano`, `editor` (en mayúsculas). Se descarta toda parte que contenga `USD`. Más de 5 partes: `""`. `slide_item` (parcial en esta tarea): clase `slide g-nueva`, un `<div class="g-bg" style="background-image:url(<img>)">` (o `class="g-bg g-lb lb-xxx"` sin caja) tras el `slide-num`, `chips` en lugar del `game-meta` si no es `""`, y elimina el rótulo por defecto `<div class="game-block-label (cy|mg)">(TOP|PODIO|EL TRONO)</div>`. Un `block_label` explícito (ej. `EN 1 LISTA`) se conserva.

- [ ] **Step 1: Escribir las pruebas que fallan**: `test_chips_ano_amarillo_y_sin_precio` (`chips({"meta": "NES · 1992 · ACTIVE ENTERPRISES · NO LANZADO · ~USD 1.926"}, "NES")` da 4 chips, `1992` con `y`, sin `USD`), `test_chips_demasiadas_partes_devuelve_vacio`, `test_chips_desde_ano_y_editor`, `test_item_nueva_fondo_con_caja_y_sin_caja` (con imagen `url(img/...)` en `g-bg`; sin imagen `g-bg g-lb`), `test_item_nueva_quita_rotulo_por_defecto` (Mundial sin `game-block-label`; un ítem con `block_label: "EN 1 LISTA"` lo conserva), `test_item_nueva_no_toca_tarrovision_ni_precio` (el bloque `<div class="tv-wrap">...</div>` y el `<div class="game-price">...</div>` del slide son idénticos al generado con `clasica`).
- [ ] **Step 2: Verificar que fallan** — Run: `python scripts/test_top_grafica.py` — Expected: FALLAN las 6 nuevas.
- [ ] **Step 3: Implementar** `chips` y la parte de `slide_item` descrita con `_inyectar` (cada reemplazo debe fallar ruidosamente si el HTML clásico cambia), y en `css_nueva()` los estilos de `.g-bg` (absoluto, `inset:-40px`, `filter:blur(22px) brightness(.3) saturate(1.3)`, `z-index:0`; con `g-lb` degradado `linear-gradient(135deg,var(--label-1),var(--label-2))`), `.slide.g-nueva .slide-hybrid{position:relative;z-index:2}` y `.g-chip`/`.g-chip.y` (22 px, mockup `slide-juego.html`).
- [ ] **Step 4: Verificar que pasan** — Run: `python scripts/test_top_grafica.py` — Expected: `OK 18 pruebas`.
- [ ] **Step 5: Commit** `feat(rankings): fondo de caja y chips en la slide de juego`.

---

### Task 5: Barra de progreso

**Files:**
- Modify: `scripts/top_grafica.py`
- Test: `scripts/test_top_grafica.py`

**Interfaces:**
- Consumes: `T._img_size(it, out_slug) -> tuple[int, int] | None`.
- Produces: `secuencia(data: dict) -> list[tuple[str, dict]]` (`("retail"|"rareza"|"grial", item)` en el orden de los slides); `tipo_barra(data: dict) -> str` (`"numeros"` si el `data` trae `rarezas` o `grial`, si no `"miniaturas"`); `ancho_rel(sz: tuple[int, int] | None) -> float` (ancho/alto limitado a 0,6 a 1,7; `None` da 1,0); `barra(data: dict, indice: int, out_slug: str) -> str` (`<div class="g-barra">`). Miniaturas: un `<div class="g-th r|cur|f" style="--w:<ancho_rel>">` por elemento de la secuencia; con imagen en los revelados y el actual (`<i style="background-image:url(..)">`), sin imagen en los que faltan, y el número (`pos`) abajo a la izquierda. Números: casillas `<div class="g-pip r|cur|f">` con `pos`, `R` (rareza) o `★` (grial), y un `<div class="g-sep">` entre los tres grupos. `slide_item` agrega la barra tras la apertura de `<div class="hybrid-head">` (que recibe `position:relative`).

- [ ] **Step 1: Escribir las pruebas que fallan**: `test_ancho_rel` (200x300 da 0,667; 240x240 da 1,0; 300x200 da 1,5; 100x400 da 0,6; 400x100 da 1,7; `None` da 1,0), `test_barra_miniaturas_estados` (slide del #8: 2 `g-th r`, 1 `g-th cur`, 7 `g-th f`; los `f` sin `background-image`), `test_barra_numeros_precios` (10 pips retail con su `pos`, 3 `R`, 1 `★`, 2 `g-sep`, ninguna `g-th`; en el slide del grial, `g-pip cur` es el `★`), `test_barra_8_items` (8 elementos), `test_barra_imagen_ilegible_cuadrada` (un ítem con `img` inexistente da `--w:1.000` y no lanza), `test_barra_igual_en_todas_las_slides` (el HTML de la barra solo difiere en los estados `r|cur|f`; mismo número de elementos y mismos `--w`).
- [ ] **Step 2: Verificar que fallan** — Run: `python scripts/test_top_grafica.py` — Expected: FALLAN las 6 nuevas.
- [ ] **Step 3: Implementar** las cuatro funciones y el enganche en `slide_item`, y en `css_nueva()`: `.hybrid-head{position:relative}`, `.g-barra` (absoluta, `left:50%`, `top:50%`, `transform:translate(-50%,-50%)`, flex con `gap:6px`), `.g-th` (alto 72 px, ancho `calc(72px*var(--w))`, borde cian; `cur` borde amarillo con brillo; `f` oscuro liso `#0c0720`), `.g-pip` (40 px, mismos estados), `.g-sep`, y `.slide.g-nueva .hybrid-head .game-pos{max-width:420px}`. Valores finos: `slide-juego.html`, `precios-barra.html`, `miniaturas.html` (variante C).
- [ ] **Step 4: Verificar que pasan** — Run: `python scripts/test_top_grafica.py` — Expected: `OK 24 pruebas`.
- [ ] **Step 5: Commit** `feat(rankings): barra de progreso con miniaturas y casillas numeradas`.

---

### Task 6: Pruebas visuales y revisión

**Files:**
- Create: `scripts/test_top_grafica_visual.py`
- Modify: `scripts/top_grafica.py` (solo ajustes de CSS que las medidas exijan)

**Interfaces:**
- Consumes: `_data_mundial`, `_data_precios`, `_generar` y los slugs de `test_top_grafica.py` (importados desde ahí).
- Produces: pruebas con Playwright (Chromium, 1920x1080) que cargan el HTML (el archivo se genera sin borrarlo hasta terminar), van a cada slide con `go(i)` y miden con `getBoundingClientRect`.

- [ ] **Step 1: Escribir las pruebas**: `test_tarrovision_identico` (por cada slide de juego, el rectángulo de `.tarrovision` con `grafica="nueva"` es igual al generado con `clasica`, para los tipos Mundial y Precios); `test_barra_sin_superposicion` (separación mínima de 100 px entre `.g-barra` y `.game-pos` / `.game-price` / `.game-block-label`, y entre `.g-barra` y el borde superior de `.tarrovision`, en Mundial con cajas mixtas, Precios con 14 casillas y un Precios con 6 rarezas, 17 casillas); `test_etiqueta_larga_se_parte` (una rareza con `badge_text` de 40 caracteres: el alto de `.game-pos` es de al menos dos líneas y no cruza la barra).
- [ ] **Step 2: Correr** — Run: `python scripts/test_top_grafica_visual.py` — Expected: `OK 3 pruebas`. Si alguna falla, ajustar el CSS de `top_grafica.py` (no el de `top_deck.py`) y repetir.
- [ ] **Step 3: Revisión con decks reales, sin pisar nada.** Para `ps1-top-mundial` (cajas cuadradas), `nes-top-mundial` (verticales), `nes-top-precios` (rarezas, sin caja, 17 casillas), `ps1-top-peores` e `ps1-infravalorados`: copiar `studio/rankings/<cat>/img/<slug>` a `.../img/zz-vista-<slug>`; ejecutar el driver `D:/Recursos Retrotarros/repo/.cache/gen_<slug con guiones bajos>.py` con `exec` en un script temporal que reemplace `generar_top` por una función que agregue `grafica="nueva"` y use el slug `zz-vista-<slug>` (las carpetas de salida se deducen del sufijo); correr `python scripts/capture-slides.py zz-vista-<slug>`; abrir con `Read` la portada, un divisor, tres slides de juego (primero, medio y último) y el grial/rareza donde corresponda. Revisar contra la spec: mosaico, tarjeta, fondo, chips, barra, TarroVision sin tocar, precio donde siempre, texto sin tildes.
- [ ] **Step 4: Limpiar** los `zz-*` (HTML, capturas, carpetas `img/zz-*`) y confirmar `git status` sin sobrantes de `studio/`.
- [ ] **Step 5: Commit** `test(rankings): pruebas visuales de la grafica nueva`.

---

### Task 7: Documentación y cierre

**Files:**
- Modify: `CLAUDE.md`, `HANDOFF.md`, `docs/modus-operandi/bitacora-decisiones.md`

- [ ] **Step 1: `CLAUDE.md`**: después de "REGLA — Letra grande para TV en los rankings", agregar la regla "Gráfica nueva de los rankings": opcional con `grafica="nueva"` en el driver; nunca en rankings grabados, programados o publicados (confirmar con Luis, mismo corolario que reseñas); qué cambia (portada con mosaico, divisores con tarjeta, fondo de caja, chips, barra con miniaturas o casillas en Top Precios); lo que no cambia (TarroVision, letra grande, precio, notas, sin tildes); mosaico solo con 6 o más cajas; pruebas con `python scripts/test_top_grafica.py` y `python scripts/test_top_grafica_visual.py`; diseño en `docs/superpowers/specs/2026-11-02-rankings-grafica-design.md`.
- [ ] **Step 2: `HANDOFF.md` y bitácora**: estado ("gráfica nueva implementada y probada; ningún ranking migrado; decidir con Luis cuáles sin estrenar la usan: Xbox Top Mundial, SNES Top Peores, reforge") y una entrada con fecha 2026-11-02 con las decisiones de Luis y las mías del diseño.
- [ ] **Step 3: Verificación final** — Run: `python scripts/test_top_grafica.py && python scripts/test_top_grafica_visual.py && python scripts/test_resena_grafica.py` — Expected: las tres terminan en `OK`. Luego `git status` limpio salvo lo propio.
- [ ] **Step 4: Commit** `docs(rankings): regla, handoff y bitacora de la grafica nueva`.
- [ ] **Step 5: Avisar a Luis** con los SHA de los commits y qué falta (migrar rankings sin estrenar). No hacer push sin su dale; antes de cualquier push seguir el protocolo de `CLAUDE.md` (`git fetch`, `git status`, `git log origin/master..master`, avance limpio de la propia rama, sin tuberías).
