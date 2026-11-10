# Gráfica nueva de las colecciones

**Fecha:** 2026-11-10
**Estado:** diseño aprobado por Luis el 2026-11-10 (viendo las maquetas). Implementadas la Fase 0 y la Fase 1 (ver sección 9); sin push, PR ni sync. No se regeneró ni se tocó ninguna colección publicada.
**Tamaño:** proyecto (módulo nuevo `scripts/coleccion_grafica.py`, enganches en `scripts/coleccion_deck.py`, pruebas, datos de las colecciones al repo)

Maquetas: [`2026-11-10-colecciones-grafica-mockups/`](2026-11-10-colecciones-grafica-mockups/) (HTML navegable `mock-nes-nueva.html`, capturas 1920x1080 en `capturas/`, comparación con lo de hoy en `antes-nes-mosaico.jpg`, script `mock_coleccion.py` que las arma).

## 1. Resumen

- Las 4 colecciones armadas (N64, NES, SNES, PS Vita) están **publicadas y retiradas del repo** (commit `29e93c1`, 2026-10-21). No hay ninguna colección grabada sin publicar ni sin grabar: la gráfica nueva solo puede entrar por **reforge** (rehacer el video, como en los rankings) o en **colecciones nuevas**.
- **Hallazgo que bloquea todo:** `scripts/coleccion_deck.py` hoy **no puede generar** (su base `studio/colecciones/n64-coleccion.html` se retiró; verificado: `BASE.exists()` da `False`). Además solo sobreviven los drivers de NES y PS Vita en `.cache/`; los de N64 y SNES se perdieron, y el deck de SNES se armó a mano con otro layout. La causa de fondo es que los datos de cada colección viven en `.cache/` (gitignored). Hay que arreglar eso antes de la gráfica.
- La propuesta sigue el patrón ya aprobado para rankings y reseñas: marca opt-in `"grafica": "nueva"` en el `DATA`, módulo aparte, HTML clásico idéntico byte a byte protegido por hashes.
- El cambio visual de fondo: letra para TV (hoy hay textos de 9 a 17 px), **cajas reales de los juegos** (hoy ninguna slide muestra una sola caja), slides que llenan la pantalla (hoy 3 de 7 tipos usan el 25 a 40 % del alto) y TarroVision con el formato que de verdad tiene el gameplay.

## 2. Inventario y estado

Fuentes: `docs/canal/inventario-contenido.md`, `data/youtube/estado-canal.json` (API de YouTube), memoria de grabados sin publicar, `HANDOFF.md` 3d, historial de git.

| Colección | Juegos / cats / joyas | Slides | Publicada (YouTube) | Vistas hoy | En el rango de reforge (19 may a 28 jun) | Driver | Layout |
|---|---|---:|---|---:|---|---|---|
| SNES | 110 / 9 / 27 | 23 | 25 may 2026 (34 min) | 2.118 | **Sí** | perdido | a mano, distinto del generador (sin hardware, índice y balance propios) |
| N64 | 58 / 8 / 24 | 21 | 8 jun 2026 (35 min) | 204 | **Sí** | perdido | generador |
| NES | 34 / 6 / 18 | 17 | 15 jun 2026 (38 min) | 102 | **Sí** | `.cache/gen_nes_coleccion.py` | generador |
| PS Vita | 91 / 9 / 27 | 23 | 6 jul 2026 (42 min) | 115 | No (fuera del rango) | `.cache/gen_psvita_coleccion.py` | generador |
| N64 "G-OLD" | 25 min | | 16 may 2026 | 348 | No | archivado, discontinuado | no se toca |

- **Grabadas sin publicar:** ninguna. **Sin grabar:** ninguna de las 4. Calendario: ninguna colección programada.
- Los números salen del CSV (`data/coleccion/coleccion-retrotarros.csv`): SNES 110 juegos + 3 consolas + 1 accesorio, N64 58 + 6, NES 34 + 2, Vita 91 + 1 (consolas y accesorios van al slide de hardware, no al conteo).
- Los TarroShorts de colección (`tarroshort-*-coleccion`, 3 en `studio/shorts/`) quedan fuera de este diseño.
- Decisión pendiente de Luis desde el 2026-10-23: si SNES, N64 y NES (en rango) se reforjan. PS Vita queda fuera del rango acordado.
- **Colecciones nuevas posibles** (el CSV tiene material, sin episodio hecho): Switch 87, PS4 76, PS2 52, PS3 51, 3DS 46, Xbox 360 44, Wii U 39, PSP 38, Wii 32, GameCube 27. No propongo cuál: es decisión de programación de Luis. Todas nacerían con la gráfica nueva.

## 3. Qué falla visualmente hoy

Evidencia: `antes-nes-mosaico.jpg` (8 slides del deck de NES recuperado de git) y capturas de N64, SNES y Vita hechas a 1920x1080 del historial.

1. **Texto demasiado chico para TV.** Los rankings ya pasaron a letra grande (`why` 32 px, regla del 2026-10-09). En colecciones: índice 17 px, conteo de categoría 13 px, meta de cada joya 12 px y título de la joya 20 px, descripción de hardware 14 px, subtítulos del balance 15 px, cierre 21 px. Los rótulos en `Press Start 2P` bajan a 9 px (tags del hardware).
2. **Slides vacías.** Hardware: las tarjetas ocupan el tercio superior y el resto es fondo. Balance: la mitad de arriba. Cierre y portada: un bloque chico al centro. Índice: una lista angosta (880 px de 1920).
3. **Cero cajas de juego.** La regla del canal para rankings es "box art real siempre"; las colecciones, que son justo el catálogo físico, no muestran ninguna. La joya es un nombre bajo una TarroVision vacía.
4. **TarroVision clásica (~1,54:1)** ni 4:3 ni 16:9: recorta o deja bandas al gameplay (ver `scripts/tarrovision.py`). En el triple, además, son tres TV cuadradas de 1 : 1 por el `aspect-ratio` clásico.
5. **Paneo sin información:** banner angosto con el nombre y el conteo, y una TV cuadrada vacía. No dice qué juegos vienen ni da soporte al presentador.
6. **Tres linajes distintos.** N64, NES y Vita salen del generador; SNES es un HTML a mano (nombres de categoría con letras separadas "P L A T A F O R M A S", índice con otro estilo, sin hardware). Las cuatro colecciones no se ven como un mismo formato.
7. **Datos tipeados a mano en el balance** (juegos, categorías, joyas): se pueden descuadrar de las categorías sin que nada avise.
8. **Sin capa de notas** (tecla N) como los rankings, aunque el generador ya sabe la lista completa de juegos por categoría.
9. **Cierre sin encadenar:** el bloque "Sigue con" de las descripciones no tiene correlato en pantalla.

## 4. Propuesta por slide

Todas las medidas son a 1920 px de ancho. Mínimos: texto corrido 24 px, rótulos pixel 20 px (hoy 9 a 13), títulos 34 px o más. La estructura (7 tipos de slide) **no cambia**; cambia cómo se ven. Colores por categoría: se alternan magenta, cian y amarillo (variable `--acc`).

| Slide | Hoy | Nueva (maqueta) | Datos |
|---|---|---|---|
| **Portada** | Título 101 px y tag de 13 px al centro, sobre fondo vacío | Mosaico de las cajas de las joyas, desenfocado y oscuro (mismo recurso que rankings, orden barajado con semilla fija). Sello "COLECCION RETROTARROS" (regla: la colección es del canal), título 170 px, tres pastillas grandes (juegos, categorías, joyas) | `portada`, `categorias[].joyas[].img` |
| **Índice** | Lista de 6 a 9 filas de 17 px | Grilla de tarjetas (3 columnas): número 64 px, nombre 38 px, conteo 56 px y las 3 cajas de esa categoría en miniatura. Con 9 categorías son 3 x 3 sin pasar del alto | `categorias` |
| **Paneo** | Banner angosto y TV cuadrada vacía | Tarjeta lateral con el conteo en 170 px ("N TITULOS EN LA COLECCION"), el aviso de las 3 joyas que siguen (cajas en miniatura) y **TarroVision ancha 16:9** (el paneo de cámara sobre los lomos es 16:9). La lista completa de juegos de la categoría va a la **capa de notas** (tecla N), no a pantalla | `categorias[].juegos` |
| **Triple de joyas** | 3 TV cuadradas, título de 20 px | Celda con fondo = caja de la joya desenfocada, TarroVision (`nueva` 4:3 por defecto), debajo la **caja real** inclinada, la etiqueta "EN LA COLECCION" (cian), el título a 36 px y chips de año (amarillo) y editor (cian). Sin caja: placa de color con el título (respaldo igual al de rankings) | `joyas[]`, `data["tarrovision"]` |
| **Hardware** | 3 tarjetas de 14 px arriba, resto vacío | Tarjetas a todo el alto: **foto del equipo** (o placa de respaldo), nombre 38 px, chip del año o formato, descripción a 26 px. Con 6 equipos (N64) pasa a 3 x 2 | `hardware[].img` (opcional) |
| **Balance** | 5 números de tarjetas chicas arriba | Columna con las 3 cifras a 120 px (calculadas desde `categorias`, ya no tipeadas) y a la derecha un **gráfico de barras horizontales de juegos por categoría**; abajo las 2 tarjetas extra (consola y studio rey) a 64 px | `categorias`, `balance.row2` |
| **Cierre** | Texto centrado de 21 px | Mosaico tenue de fondo, "SIGUE LA SAGA" a 120 px, tarjeta **"SIGUE CON"** (video recomendado, mismo criterio de las descripciones) y tres botones (comenta, pide otra consola, suscríbete) a 24 px | `proximo` (opcional, como `proxima` en reseñas), `cierre` |

Detalles de decisión:

- **TarroVision por slide.** El paneo es video de cámara: siempre `ancha` (16:9). El triple es gameplay: `data["tarrovision"]` (campo que ya usan reseñas y sagas), por defecto `nueva` (4:3) para consolas de NES a N64 y `ancha` para portátiles y modernas (Vita 960x544, PSP, Switch). Con la marca `grafica="nueva"` y sin `tarrovision`, se asume `nueva`.
- **Cajas:** 260 px de ancho (las que ya tenemos de Wikipedia) alcanzan hasta ~250 px de alto en pantalla sin verse blandas, que es lo que usa la maqueta. No usar cajas más grandes que eso sin una versión mejor.
- **Sin tildes en pantalla.** Los textos de la maqueta ya lo cumplen.
- **Texto fijo:** "EN LA COLECCION" en cada joya es redundante en un episodio donde todo es de la colección, pero hace explícita la regla de propiedad del canal (nunca "de Coco") y alinea la gráfica con reseñas y rankings. Si a Luis le sobra, es una línea para quitar.

## 5. Cómo se activa (mismo patrón que rankings y reseñas)

- `generar_deck(data, slug)` lee `data.get("grafica", "clasica")`. Solo `"nueva"` importa y llama a `scripts/coleccion_grafica.py`; cualquier otro valor distinto de `clasica` o `nueva` lanza `ValueError`. Sin la marca no se importa código nuevo y el HTML sale **idéntico, byte a byte**.
- Los campos nuevos son todos opcionales: `categorias[].joyas[].img` (si falta, se busca la caja por clave en `studio/colecciones/img/<slug>/<clave>.jpg`, igual que `_auto_img` de rankings, y si no existe sale el respaldo de color), `hardware[].img`, `proximo` (`{titulo, consola, tag}`), `notas` por categoría, `tarrovision`.
- `coleccion_grafica.py`: `css_nueva()`, `mosaico()`, `portada()`, `indice()`, `paneo()`, `triple()`, `hardware()`, `balance()`, `cierre()`. Cada slide nueva reemplaza a su gemela clásica; las claves de reemplazo fallan en voz alta (`RuntimeError`) si el HTML clásico cambia, como en `top_grafica._inyectar`.
- La TarroVision sale de `scripts/tarrovision.py` (módulo existente), sin copiarla.
- Capa de notas: el CSS/JS de notas de los rankings, activa solo con la marca (tecla N; `capture-slides.py` ya fuerza `read-mode` apagado).
- `generar_deck` gana dos parámetros con valores por defecto que no cambian nada (`out_dir=None`, `lista=True`) para que las pruebas escriban a una carpeta temporal: hoy cada llamada escribe el HTML y `docs/descripciones/lista-paneo-<slug>.md` dentro del repo.

### Pruebas (`scripts/test_coleccion_grafica.py`, sin pytest)

- **Regresión byte a byte:** hash golden del HTML clásico generado con un `DATA` de prueba, con y sin `grafica="clasica"`. Además se comprobó una vez que el generador con la base restaurada produce el mismo HTML que el generador original (ver sección 9). El deck de NES publicado no se puede usar de referencia: ya difería en tamaños de fuente porque la base se ajustó después de publicarlo.
- Con la marca: mosaico, tarjetas, chips; con y sin cajas; categorías de 3 a 9; hardware de 1 a 6 equipos; `ValueError` con un valor inválido.
- **Prueba visual con Chromium** (como `test_top_grafica_visual.py`): ninguna slide desborda su alto (`scrollHeight` mayor que `clientHeight`), el texto visible no baja de 20 px, la TarroVision ancha mide 16:9 exacto.
- Las pruebas crean cajas temporales y no dependen de imágenes del estudio.

## 6. Plan de migración

El pedido original hablaba de migrar "solo las no grabadas ni publicadas". Hoy esa lista está **vacía** (las 4 están publicadas), y los HTML ya no existen para parchear (a diferencia de rankings, donde `aplicar_grafica_nueva.py` parchea el HTML commiteado). Entonces:

**Fase 0, prerrequisitos (sin cambio visual; recomiendo hacerlas aunque Luis no apruebe la gráfica):**
1. Dejar la base de CSS/JS como archivo versionado `studio/templates/_base-coleccion.html` (se recupera de `git show 29e93c1^:studio/colecciones/n64-coleccion.html`) y apuntar `BASE` ahí, así el generador vuelve a funcionar y no depende de un HTML que se retira al publicar.
2. Mover los datos de cada colección a archivos versionados `data/colecciones/<slug>.json` (hoy solo viven en `.cache/`, gitignored). NES y Vita salen de sus drivers; N64 y SNES se reconstruyen desde las pautas (`docs/pautas/pauta-<slug>-coleccion.md`) y el HTML recuperado de git. Cada driver pasa a ser una línea que lee el JSON.
3. Escribir las pruebas de regresión del clásico (sección 5) **antes** de tocar el generador.

**Fase 1, implementación (tras el dale):** `coleccion_grafica.py`, enganches, pruebas, regla en `CLAUDE.md` (marca solo en colecciones nuevas o reforjadas; nunca en una grabada o publicada). Verificación visual con un `out_slug` temporal, nunca se pisa un deck existente.

**Fase 2, reforge (solo con el dale de Luis, una colección por sesión):** orden sugerido: **NES** primero (la más chica: 34 juegos y 6 categorías, driver sano, ya hay 9 de las 18 cajas en el repo), luego **N64** y por último **SNES** (110 juegos, 9 categorías, hay que reconstruir los datos). **PS Vita** queda fuera salvo que Luis la sume. Cada reforge es un video nuevo: trae su kit de YouTube, capturas (`capture-slides.py`) y sync a Drive con el dale. Cajas: antes de bajar nada, reutilizar las que ya están en `studio/rankings/**/img/` (por clave) y bajar solo las faltantes con `fetch_boxart_wiki.py`. Estimado: 18 cajas NES, 24 N64, 27 SNES. Fotos de hardware: las tiene que sacar Luis o bajar de Wikipedia; sin foto sale la placa de respaldo.

**Fase 3, colecciones nuevas:** nacen con `grafica="nueva"`, `data/colecciones/<slug>.json` y la regla vigente de que la colección es del canal.

**Qué no se hace:** no se toca ningún driver ni HTML de una colección publicada; no se recrean "archivo-koko" ni "retrotarros-vs-mundo"; no se agrega la marca a nada grabado.

## 7. Decisiones para que Luis revise

1. ¿Se reforjan SNES, N64 y NES (en rango) o solo se hace la gráfica para colecciones nuevas? Eso define si la fase 2 existe.
2. ¿Aprueba la Fase 0 sola (arreglar el generador y versionar los datos) aunque no apruebe aún el rediseño? Es independiente y de bajo riesgo.
3. ¿Mantiene la etiqueta "EN LA COLECCION" en cada joya?
4. ¿Fotos propias del hardware (mejor resultado) o fotos de Wikipedia / placa de respaldo?
5. ¿El triple va en 4:3 (`nueva`) por defecto salvo portátiles, como propongo?
6. ¿Agregamos al balance la composición del estado (loose, boxed, CIB) sacada del CSV? Es interesante en Vita (69 en caja, 16 CIB, 7 nuevos) y plano en las consolas viejas (casi todo suelto). No lo incluí en la maqueta.
7. ¿Valor estimado de la colección en el balance? No lo incluí: exigiría fuente primaria y la aclaración de "valor aproximado", y es otra conversación.

## 8. Observaciones al margen

- `scripts/fetch_boxart_wiki.py` envía en su `User-Agent` un correo personal a Wikipedia. Para la fase 2 conviene cambiarlo por un nombre genérico de cliente; no lo cambié aquí (fuera de alcance).
- El deck de SNES dice "110 juegos" y el CSV tiene 114 filas de SNES: la diferencia son 3 consolas y 1 accesorio, o sea consistente; lo anoto para que nadie lo "corrija" al reconstruir.
- Los hashes de regresión del clásico deben generarse con la base restaurada, no con otra copia: si la base cambia, cambian los hashes.

## 9. Implementado (2026-11-10)

Fase 0:
- `studio/templates/_base-coleccion.html` (CSS/JS base versionado, recuperado de `git show 29e93c1^:studio/colecciones/n64-coleccion.html`, sin las slides) y `scripts/fixtures_coleccion_grafica/base_congelada.html` para las pruebas. `BASE` de `coleccion_deck.py` apunta ahí.
- `data/colecciones/{nes,n64,snes,psvita}-coleccion.json`: NES y Vita salen de los drivers de `.cache/`; N64 y SNES se reconstruyeron parseando el HTML publicado. Estos dos no traen la lista `juegos` por categoría. El SNES no incluye la slide RAREZAS (Super Scope y Super Game Boy) del deck publicado, y su cierre decía "panorama N64": el JSON dice SNES.
- `generar_deck(data, slug, out_dir=None, lista=True)`: con los valores por defecto nada cambia. Hardware y fila 2 del balance pasaron a ser opcionales (SNES no los tenía); para cualquier dato que ya funcionaba la salida es idéntica.
- Verificación de regresión: salida idéntica al generador original para el dato de prueba, NES y N64 (comparación directa con `git show HEAD:scripts/coleccion_deck.py`).

Fase 1:
- `scripts/coleccion_grafica.py` y la marca `grafica="nueva"` como en la sección 5; campos opcionales y comportamientos tal como están en el docstring del módulo y en `CLAUDE.md`.
- `scripts/test_coleccion_grafica.py` (22 pruebas, hashes de regresión en `fixtures_coleccion_grafica/golden.json`) y `scripts/test_coleccion_grafica_visual.py` (2 pruebas en Chromium sobre los 4 JSON).
- La prueba visual encontró y se corrigieron tres problemas de la maqueta: el mosaico hacía desbordar la slide de portada y cierre (ahora va en un envoltorio recortado), la caja inclinada de las celdas del triple desbordaba la celda (bajó a 215 px) y el índice de 8 o 9 categorías cortaba el conteo (versión compacta con miniaturas más bajas).

Por hacer en la siguiente fase (con el dale de Luis): cajas de las joyas, fotos de hardware, `proximo` del cierre, reconstruir la lista `juegos` y la slide RAREZAS de SNES si se reforja, y las capturas de un deck real con `capture-slides.py` al generar el primero.
