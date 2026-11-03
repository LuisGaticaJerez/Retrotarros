# Gráfica nueva de los rankings

**Fecha:** 2026-11-02
**Estado:** pendiente de aprobación de Luis (diseño construido con él, mockups en `.superpowers/brainstorm/`)
**Tamaño:** proyecto (módulo nuevo `scripts/top_grafica.py`, enganches en `scripts/top_deck.py`, pruebas y documentación)

## Intención y por qué

Los rankings (Top Mundial, Top Precios, Top Peores, Infravalorados) se ven iguales de uno a otro. Cinco slides de un deck de 14 a 19 son solo título y párrafo centrados sobre fondo vacío (portada, intro, análisis, cliffhanger, divisor de rarezas), y la slide de cada juego no dice dónde va el ranking. Luis lo comparó con la gráfica nueva de las reseñas ("tienen más vida, más consistencia y cuerpo") y pidió algo equivalente para los rankings, sin tocar lo que ya funciona en la TV del estudio.

## Objetivos

- Portada, divisores y slide de juego con la gráfica de abajo, activada por una marca opcional en el `data`.
- Que los rankings ya grabados o publicados salgan byte a byte iguales al regenerarlos, y que ninguno cambie sin que alguien ponga la marca a propósito.
- Que funcione con los tres tipos de caja (vertical, cuadrada, horizontal) y con juegos sin caja.

## No objetivos y anti-objetivos

- No cambia la estructura de slides ni el orden #10 a #1 (más rarezas y grial en Top Precios).
- No cambia el TarroVision (tamaño, posición), la letra grande para TV (`tv_grande`, `_tv_css()`), la caja real y nunca logo, el precio grande arriba a la derecha de Top Precios, la capa de notas (tecla N), el texto sin tildes en pantalla, ni los layouts de caja `alta`/`ancha`/`clasica`.
- No migra ningún ranking existente. Qué rankings usan la marca lo decide Luis caso a caso (sin estrenar y sin grabar). Esta tarea no regenera ningún deck publicado ni programado.
- Sin halo, chip ni efecto especial en el grial: Luis pidió explícitamente una versión más limpia.
- Anti-objetivo: que la barra o cualquier elemento nuevo se superponga con la etiqueta de la izquierda, con el precio o con el TarroVision.

## Enfoques considerados

- **A. Todo dentro de `top_deck.py`, con la marca `grafica="nueva"`.** Es el patrón de `resena_deck.py`. El archivo (unas 500 líneas) crecería unas 300 y el diff dificulta demostrar que lo clásico no cambió.
- **B. Código nuevo en `scripts/top_grafica.py`, llamado desde `top_deck.py` solo con la marca.** Elegido por Luis. El diff de `top_deck.py` queda reducido a puntos de enganche, y probar que los 49 rankings no cambian es mucho más fácil.
- **C. Parchear HTML ya generados.** Descartado: no sirve para rankings nuevos y es frágil.

## Qué cambia con la gráfica nueva (decisiones de Luis)

Mockups de referencia en `.superpowers/brainstorm/1112-1793669109/content/` del worktree donde se hizo este diseño (`portada.html`, `divisores.html`, `slide-juego.html`, `precios-v2.html`, `precios-barra.html`, `vertical-y-sin-caja.html`, `miniaturas.html`). Esa carpeta no se versiona (`.superpowers/` va en `.gitignore`): este documento describe todo lo necesario y los mockups son solo ayuda visual si el worktree sigue existiendo.

1. **Portada, opción A "mosaico de fondo".** Las cajas de los juegos del ranking, desenfocadas y oscurecidas, llenan el fondo en una grilla de 5 por 2. El título (etiqueta, consola, subtítulo) sigue al centro. El orden de las cajas en el mosaico **no** es el del ranking, para no arruinar el cliffhanger.
2. **Divisores, opción A "tarjeta de vidrio".** El mismo mosaico, más tenue, y el texto dentro de una tarjeta oscura con borde de neón (cian o magenta según el `color` del divisor, que ya existe en el `data`).
3. **Slide de juego, opción B.**
   - Fondo: la caja del propio juego, desenfocada y oscura.
   - Línea de metadatos como chips: el año destacado en amarillo, el resto en cian.
   - Barra de progreso en la cabecera, **centrada y fija** (siempre en el mismo lugar en todas las slides). Reemplaza la etiqueta por defecto de la derecha (`TOP`, `PODIO`, `EL TRONO`). Si el ítem trae un `block_label` explícito (por ejemplo "EN 1 LISTA" en Top Peores), se mantiene.
4. **Barra de progreso, por tipo de ranking.**
   - **Top Mundial, Top Peores e Infravalorados: miniaturas, variante C.** Alto fijo, ancho según la proporción de la caja (proporción limitada a un rango, 0,6 a 1,7). Un puesto ya revelado muestra su caja con el número abajo a la izquierda; el actual, borde amarillo; los que faltan, en oscuro liso sin imagen.
   - **Top Precios: casillas numeradas, sin miniaturas.** Con hasta 17 casillas no caben miniaturas entre la etiqueta y el precio. Tres grupos separados por una línea: los 10 retail (cian, con su número), las rarezas no-retail (magenta, con "R") y el grial (dorado, con "★"). Sin etiquetas de grupo en el deck: en los mockups iban solo como referencia.
5. **Top Precios.** El precio grande queda exactamente como hoy (misma posición y tamaño, por encima del TarroVision). Las rarezas mantienen su etiqueta (`badge_text`, ej. "HALLADO EN BODEGA") a la izquierda. Si la etiqueta fuera tan larga que se acerque a la barra, se parte en dos líneas; la barra no se achica ni se mueve.
6. **Sin caja.** El fondo toma el degradado de la etiqueta de color que ya hace de caja (`--label-1` a `--label-2` de la clase `lb-*` del ítem), desenfocado y oscuro. En el mosaico, el hueco del juego sin caja se rellena con ese mismo color. Si el ranking tiene menos de 6 cajas de 10, el mosaico no se usa y portada y divisores salen como hoy.
7. **Caja vertical o cuadrada u horizontal.** El fondo desenfocado usa la caja recortada; no cambia la caja principal de la slide (siguen valiendo los layouts alta, ancha y clasica).

## Diseño técnico

### Marca y compatibilidad

`generar_top` lee `data.get("grafica", "clasica")`. Solo con `"nueva"` se llama a `top_grafica.py`. Cualquier otro valor distinto de `clasica` o `nueva` lanza `ValueError` (para no activar la gráfica por un error de tipeo). Sin la marca no se importa ni se ejecuta código nuevo, y el HTML sale idéntico, byte a byte.

### `scripts/top_grafica.py`

Funciones puras que reciben lo necesario (datos del ranking y funciones de ayuda de `top_deck`, importadas de forma diferida para evitar ciclos):
- `css_nueva()`: el CSS de todo lo nuevo, que se agrega al final del bloque de estilo compartido.
- `mosaico(data, out_slug, tenue)`: HTML del mosaico, con las cajas del ranking en un orden barajado de forma determinista (semilla: `out_slug`, para que regenerar no cambie nada).
- `portada(...)`, `divisor(...)` y `slide_item(...)`: variantes de las funciones `_slide_*` de `top_deck`.
- `barra(data, items_orden, actual, tipo)`: arma la barra. `tipo` es `miniaturas` o `numeros` (Top Precios, decidido por la presencia de rarezas o grial en el `data`, o por un campo explícito si el builder lo prefiere).
- `chips(it, consola)`: chips a partir de `it["meta"]` (separado por `·`) o de consola, año y editor. Descarta partes que parezcan un precio (`~USD ...`), porque el precio ya sale grande aparte. Si salen más de 5 chips, mantiene la línea de metadatos de hoy.

### Enganches en `top_deck.py`

En `generar_top`: leer la marca, agregar el CSS, y elegir entre `_slide_portada`/`_slide_divider`/`_slide_item` y sus variantes. En `_slide_item`, pasar a la variante solo cuando corresponde. Nada más.

### Pruebas (`scripts/test_top_grafica.py`, sin pytest)

- **Regresión byte a byte:** generar con un `data` de prueba, antes de tocar el código, y guardar el hash en la prueba (golden). La prueba verifica que sin la marca, y con `grafica="clasica"`, el HTML coincide con el hash.
- La gráfica nueva activa mosaico, tarjeta, chips y barra; con y sin cajas; con un ranking de menos de 6 cajas; con caja vertical, cuadrada y horizontal; en Top Precios con rarezas y grial.
- El valor inválido de `grafica` lanza `ValueError`.
- Las pruebas no dependen de imágenes del estudio: crean cajas temporales y borran lo que generan.

### Revisión visual

Con `scripts/capture-slides.py` sobre al menos: un Top Mundial (cajas cuadradas y verticales), un Top Precios con rarezas y grial (NES o PS1), un Top Peores e Infravalorados. Revisar a mano portada, un divisor, una slide de cada tipo y las medidas a 1920 px de ancho entre etiqueta, barra, precio y TarroVision (los mockups midieron unos 150 px libres de cada lado en el caso más apretado, NES con 17 casillas). Para esto se usa un `out_slug` temporal, nunca se pisa un deck existente.

## Decisiones tomadas por mí (para que las revises)

- **Barra con miniaturas de forma estable:** los puestos que faltan van en oscuro liso pero con el ancho real de su caja, porque si no la barra se movería al revelarse cada uno. Costo: la silueta delata la forma de la caja de lo que viene (cuadrada, vertical u horizontal), un adelanto mínimo.
- Mosaico solo si hay al menos 6 cajas de 10; el umbral es mío.
- Orden del mosaico barajado de forma determinista para no revelar el ranking.
- Valor inválido de `grafica` es error, no aviso.
- Altura de las miniaturas ajustable por el builder al revisar las capturas (3,8 a 4,4 unidades de ancho de slide), siempre que la barra no toque la etiqueta ni el precio.

## Lo que queda para quien construya

- El CSS exacto (tamaños, sombras, desenfoque): partir de los mockups y de `_shared_css()`/`_box_css()` de `top_deck.py`.
- Decidir cómo `generar_top` detecta Top Precios para elegir la barra de números (por ejemplo, por la presencia de `rarezas` o `grial`, o por el sufijo del slug).
- Revisar las etiquetas de todos los Top Precios que existen para confirmar que ninguna se acerca a la barra.
- Documentar en `CLAUDE.md` (regla: rankings nuevos o reforjados pueden llevar `grafica="nueva"`, nunca los grabados o publicados), en `HANDOFF.md` y en `docs/modus-operandi/bitacora-decisiones.md`.
- Qué rankings sin estrenar pasan a la gráfica nueva (Xbox Top Mundial, SNES Top Peores, y el reforge del 19 de mayo al 28 de junio) queda fuera de esta tarea y lo decide Luis.
