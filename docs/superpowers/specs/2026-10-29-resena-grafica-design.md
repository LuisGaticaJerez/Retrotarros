# Mejoras gráficas de las reseñas

**Fecha:** 2026-10-29
**Estado:** borrador para aprobación de Luis
**Tamaño:** proyecto (siete cambios de render en `scripts/resena_deck.py`, campos nuevos en el DATA y extensiones del lint)

## Intención y por qué

Las reseñas se ven iguales de una a otra y varias slides son solo texto sobre fondo oscuro. Luis eligió, viendo mockups hechos sobre el HTML real de The Sims y Commandos, siete cambios que hacen cada slide más informativa y más reconocible sin cambiar la estructura de 8 slides ni las reglas de contenido (nada de crítica en pantalla, sin tildes débiles, la colección es de Retrotarros).

## Objetivos

- Portada, ficha, contexto, jugabilidad, audiovisual, veredicto y cierre con los cambios de abajo.
- Que las reseñas nuevas puedan salir con la gráfica nueva con una línea en el driver (`grafica="nueva"`), y que ninguna reseña existente cambie al regenerarla sin que alguien lo pida.

## No objetivos y anti-objetivos

- No cambia la estructura (8 slides fijas, comparativa sin texto, notas ocultas).
- No toca los HTML ya generados ni los 49 drivers existentes: sin la marca `grafica` todo sale como hoy.
- No migra las reseñas del backlog a la gráfica nueva: eso exige investigar años por plataforma, compositores y viñetas de cada juego, y es una tarea aparte que se hace cuando se toque cada reseña.
- No incluye la cifra gancho en el contexto (idea E: descartada por Luis), ni el slide opcional de dato curioso, ni la etiqueta de comparativa.
- No cambia las cajas: se usan las que ya hay en `studio/resenas/img/resenas/` (la caja en mejor resolución quedó descartada).

## Enfoques considerados

- **A. Gráfica nueva por defecto, con `grafica="clasica"` para reproducir una reseña grabada.** Descartado tras la revisión: regenerar el driver de una reseña ya filmada la cambiaría en silencio, y solo Luis sabe cuáles están grabadas.
- **B. Gráfica clásica por defecto y `grafica="nueva"` explícita en cada reseña nueva.** Elegido. Ningún driver existente cambia sin que alguien lo decida. Para que las nuevas no se olviden de pedirla, el lint avisa cuando falta la marca y `CLAUDE.md` lo exige para toda reseña nueva.
- **C. Dos generadores separados.** Descartado: duplica CSS y JS de navegación y notas.

## Decisiones de Luis

1. **A. Portada con la caja de fondo:** caja desenfocada y oscurecida llena el fondo; la caja nítida va inclinada a la derecha; el título a la izquierda.
2. **B. Ficha con chips de plataforma** en orden de lanzamiento, la primera en amarillo con su año.
3. **C. Veredicto con la escala visible:** la etiqueta grande se mantiene y debajo van las cuatro categorías con la elegida encendida.
4. **D. Contexto con imagen:** la caja a un costado del texto.
5. **F. Jugabilidad con tres viñetas** numeradas junto al gameplay.
6. **G. Crédito del compositor** como etiqueta propia en la slide de audiovisual.
7. **H. Cierre con la próxima reseña**, pero solo cuando se sabe: en el estudio a veces el próximo juego se decide después de grabar, así que es un campo opcional que se completa luego y se regeneran las capturas del cierre.

## Diseño

### Marca de gráfica

`generar_resena` lee `data.get("grafica", "clasica")`. Con `"clasica"` (o sin la marca) el HTML sale idéntico, byte a byte, al que producía el generador antes de este cambio. Todo CSS y HTML nuevo se agrega solo con `grafica="nueva"`. Las reseñas nuevas llevan `grafica="nueva"` en su driver; una reseña ya hecha pasa a la gráfica nueva solo si alguien lo cambia en su driver a propósito.

### Campos nuevos del DATA (todos opcionales)

- `plataformas`: lista de pares `[nombre, año]` para los chips de la ficha. Si falta, los chips salen de `consola` separada por `·` sin año, con el primero en amarillo.
- `jugabilidad_vinetas`: lista de 3 pares `[titulo, texto]` (títulos en mayúsculas, textos cortos). Si falta, la slide queda con el bloque `jugabilidad_dato` de hoy.
- `audiovisual_compositor`: texto con el crédito (ej. `Jerry Martin · Marc Russo`). Si falta, no aparece la etiqueta.
- `proxima`: diccionario `{juego, consola, anio, img_key}`. Si falta, el cierre queda como hoy. `img_key` es opcional; sin imagen la tarjeta sale sin caja.

### Cada cambio

- **Portada (A):** fondo con la caja (`img_key`) desenfocada y oscurecida, caja nítida inclinada a la derecha a ~70 % de alto, título y subtítulo alineados a la izquierda. Si no existe la imagen, la portada queda como hoy.
- **Ficha (B):** el valor de CONSOLA pasa a chips (primer chip amarillo con el año, los demás en cian) separados por `▸`. Pueden bajar a una segunda línea.
- **Veredicto (C):** una fila de cuatro píldoras bajo la etiqueta, con la elegida (`veredicto_tag`) en amarillo y las demás atenuadas. Un tag fuera de la escala (reseñas históricas) no enciende ninguna.
- **Contexto (D):** si existe la caja, va a la izquierda a ~70 % de alto y el texto a la derecha alineado a la izquierda. Sin imagen queda como hoy.
- **Jugabilidad (F):** reemplaza el bloque "EL DATO" por tres filas con número (`01`, `02`, `03`), título en Orbitron y texto corto.
- **Audiovisual (G):** bajo el dato, una caja con borde cian, etiqueta `BANDA SONORA` y el texto de `audiovisual_compositor`.
- **Cierre (H):** bajo el SUSCRIBETE, una tarjeta con borde magenta con la caja (si hay), `PROXIMA RESEÑA`, el nombre del juego y `consola · año`.

### Lint

- Los textos nuevos que salen en pantalla (`jugabilidad_vinetas`, `audiovisual_compositor`, `proxima.juego`, `proxima.consola`) entran a la revisión de tildes débiles y de palabras de crítica.
- `jugabilidad_vinetas` con una cantidad distinta de 3: error.
- `grafica` con un valor distinto de `nueva` o `clasica`: error.
- Sin la marca `grafica`: aviso ("sale con la gráfica clásica; las reseñas nuevas deben llevar grafica=\"nueva\"").
- Con `grafica="nueva"`: aviso si falta `jugabilidad_vinetas`, y aviso si `consola` tiene varias plataformas y falta `plataformas` (los chips saldrían sin año). `audiovisual_compositor` y `proxima` no generan aviso: pueden no existir.

### Capturas

Después de implementar, `python scripts/capture-slides.py` sobre una reseña de prueba y revisión visual de cada slide.

## Decisiones tomadas por mí (para que las revises)

- Gráfica clásica por defecto y `nueva` explícita (enfoque B), porque proteger las reseñas ya filmadas pesa más que ahorrar una línea en cada driver nuevo.
- Los avisos del lint por campos nuevos faltantes son avisos y no errores, para no bloquear una reseña cuyo juego no tiene compositor conocido o que es de una sola plataforma.
- Altura de la caja nítida en la portada (~70 %, más chica que el mockup, que usaba 78 %) para que se note menos que las cajas son de baja resolución.
- Exactamente 3 viñetas, igual que en el mockup.
- La slide de portada no cambia si falta la caja.

## Lo que queda para quien construya

- El CSS exacto (tamaños, márgenes, sombras): partir de los mockups en `.superpowers/brainstorm/` y de `scripts/resena_deck.py`.
- Cómo ordenar el código nuevo dentro de `resena_deck.py` (funciones por slide) y las pruebas de regresión byte a byte contra el generador anterior.
- La documentación en `CLAUDE.md` (regla: toda reseña nueva lleva `grafica="nueva"` y, cuando se pueda, `plataformas` con año, `jugabilidad_vinetas` y `audiovisual_compositor`) y en `HANDOFF.md` (incluida la nota de que migrar el backlog es una tarea pendiente aparte).
