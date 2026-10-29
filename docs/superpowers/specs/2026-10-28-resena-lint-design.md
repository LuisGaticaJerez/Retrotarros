# Lint de reseñas, `por_confirmar` y `en_coleccion` de tres estados

**Fecha:** 2026-10-28
**Estado:** borrador para aprobación de Luis
**Tamaño:** cambio pequeño (un módulo nuevo y dos retoques en `scripts/resena_deck.py`)

## Intención y por qué

Casi todo lo que se corrigió a mano en las últimas tandas de reseñas era una regla que ya existe en `CLAUDE.md` y que depende de que alguien se acuerde: tildes en pantalla, largo del contexto, escala de veredicto, TRAMA RESUMIDA, chequeo de arcade, sufijo `-pedido`. Además, los datos dudosos ("por confirmar") quedan enterrados dentro de las líneas de notas y hay que releer todo antes de grabar. Y `en_coleccion` solo admite sí o no, aunque a veces tenemos algo de la familia del juego (MySims con The Sims).

## Objetivos

- Que las reglas escritas se verifiquen solas cada vez que se genera una reseña.
- Que lo dudoso se vea de una mirada antes de grabar.
- Que la ficha pueda decir "no está, pero la familia sí".

## No objetivos y anti-objetivos

- No cambia el diseño de las 8 slides ni el aspecto de pantalla, salvo una línea opcional en la ficha.
- No modifica reseñas ya generadas, grabadas o programadas. El lint solo actúa cuando una reseña se regenera.
- No se rompe ningún driver existente: todo campo nuevo es opcional.
- Fuera de alcance, para después y de a uno: esqueleto del kit de YouTube, caja en buena resolución, segundos por slide, export de notas a DOCX/PDF.

## Enfoques considerados

- **A. Validación solo dentro de `generar_resena`.** Simple y no se olvida, pero no sirve para revisar un driver sin generar.
- **B. Script aparte sobre los HTML.** Audita el catálogo, pero el HTML no conserva el DATA y las reseñas viejas fallarían por reglas posteriores.
- **C. Módulo `scripts/resena_lint.py` con `revisar(data, out_slug)`, llamado siempre desde `generar_resena`.** Elegido por Luis (2026-10-28). Es A con la puerta abierta a revisar un driver suelto sin duplicar reglas.

## Diseño

### 1. Módulo `scripts/resena_lint.py`

`revisar(data, out_slug)` devuelve dos listas: `errores` y `avisos`.

**Errores (frenan la generación):**
- `veredicto_tag` fuera de IMPRESCINDIBLE, JUEGAZO, MEMORABLE, COLECCIONABLE.
- Tildes débiles (á é í ó ú ü) en el texto de pantalla: `juego`, `gancho_sub`, `consola`, `developer`, `genero`, `contexto_texto`, `jugabilidad_dato`, `audiovisual_dato`, `veredicto_resumen`, `cierre_sub`. La ñ y los signos ¿ ¡ están permitidos.
- Falta el bloque TRAMA RESUMIDA en `notas.contexto`.
- `notas.ficha` no menciona "arcade" (regla de verificar versión arcade previa).
- `data["pedido"]` existe y el slug no termina en `-pedido`, o al revés.

**Avisos (se muestran, no frenan):**
- `contexto_texto` con más de 75 palabras (meta: 50 a 70).
- Tildes débiles en las notas.
- Palabras de crítica dura en el texto de pantalla (lista corta: "malo", "peor", "aburrido", "feo", "no compite", "fracaso", "lento", etc.).
- Consola con varias plataformas y `notas.ficha` sin ninguna línea que diga cuál salió primero.
- `notas.jugabilidad` con menos de 3 líneas.
- Falta alguno de los 8 bloques de notas.
- Las notas contienen "por confirmar" pero el campo `por_confirmar` está vacío (ayuda a migrar).
- La caja existe pero mide menos de 400 px de ancho.

### 2. Integración en `generar_resena`

`generar_resena(data, out_slug, lint=True)`. Imprime avisos y errores. Si hay errores, lanza `ValueError` con la lista completa antes de escribir el HTML. `lint=False` queda para reseñas históricas que tengan excepciones conocidas. También se puede correr `python scripts/resena_lint.py .cache/gen_resena_<juego>.py` para revisar un driver sin generar (importa el DATA con el lint desactivado).

### 3. Campo `por_confirmar`

Lista opcional de textos cortos en el DATA. Se muestra como un bloque "POR CONFIRMAR ANTES DE GRABAR" al **inicio de las notas de la portada** (lo primero que se ve en modo lectura), con estilo distinto al resto (borde amarillo y etiqueta). El generador además imprime la lista en consola al terminar.

### 4. `en_coleccion` de tres estados

Valores: `True` (EN LA COLECCION), `False` (NO ESTA EN LA COLECCION) y `"familia"`. Con `"familia"` la etiqueta dice NO ESTA EN LA COLECCION y debajo, más chica, la línea opcional `familia_texto` (ej.: "Si tenemos MySims Kingdom (DS)"). Sin `familia_texto`, `"familia"` se comporta como `False`. La posesión es siempre del canal, nunca de una persona.

## Decisiones tomadas por mí (para que las revises)

- Tildes en notas solo como aviso y no como error, porque las notas no salen en las capturas.
- Umbral de 75 palabras en vez de 70 para no avisar por una palabra de diferencia.
- El bloque `por_confirmar` va en la portada, no en el cierre.
- La caja de menos de 400 px es solo aviso.
- La lista de palabras de crítica es una heurística y puede dar falsos positivos.

## Lo que queda para quien construya

- Redactar la lista exacta de palabras de crítica y afinar el texto de los mensajes.
- CSS del bloque `por_confirmar` y de la línea de familia en la ficha.
- Un script de prueba simple (`scripts/test_resena_lint.py`) con un DATA válido y varios inválidos.
- Verificar que los 49 drivers existentes siguen generando igual (solo fallan si rompen un error; los que tengan excepción histórica se pasan con `lint=False`).
