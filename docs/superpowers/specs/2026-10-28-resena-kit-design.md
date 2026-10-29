# Esqueleto del kit de YouTube para reseñas

**Fecha:** 2026-10-28
**Estado:** borrador para aprobación de Luis
**Tamaño:** cambio pequeño (un script nuevo, un refactor mínimo del lint y sus pruebas)

## Intención y por qué

Cada reseña cierra con un kit de publicación (`docs/descripciones/descripcion-resena-<slug>.md`) con título, descripción, tags, hashtags y comentario fijado. Hoy se arma de cero cada vez, y la parte mecánica (hashtags según la receta, tope de 500 caracteres en tags, estructura, CTA, pie) se puede equivocar o olvidar. La parte humana (gancho, contexto, pregunta a la comunidad, comentario fijado) no se automatiza: Luis pidió que no suene robótica, así que sigue escribiéndose a mano con la voz del canal.

## Objetivos

- Un comando que crea el esqueleto del kit con lo mecánico ya relleno y marcadores `[REDACTAR: ...]` donde va lo humano.
- Un chequeo del kit terminado antes de pegarlo en el chat.

## No objetivos y anti-objetivos

- No genera prosa automática (ni gancho, ni párrafo de contexto, ni pregunta, ni comentario fijado).
- No escribe nada solo: se ejecuta cuando se pide, y no sobrescribe un kit existente.
- No toca kits ya hechos ni reseñas ya publicadas.
- Fuera de alcance: caja en buena resolución, segundos por slide, export de notas.

## Enfoques considerados

- **A. Automático dentro de `generar_resena`.** Descartado: generar o regenerar una reseña escribiría en `docs/` como efecto secundario, ensuciaría las pruebas y podría crear kits de reseñas ya publicadas.
- **B. Comando aparte `python scripts/resena_kit.py`.** Elegido por Luis (2026-10-28). Explícito, no pisa nada, y reutiliza la lectura de drivers del lint.

## Diseño

### 1. Crear el esqueleto

`python scripts/resena_kit.py .cache/gen_resena_<juego>.py` lee el DATA del driver sin generar nada (misma captura que el CLI del lint, factorizada como `capturar_driver(ruta)` en `resena_lint.py`) y escribe `docs/descripciones/descripcion-<out_slug>.md`. Si el archivo ya existe, no escribe nada, lo avisa y sale con código 2.

Contenido, en el formato de los kits vigentes:

- **Títulos:** (1) `[REDACTAR: título con dato curioso]` marcado como recomendado; (2) `<Juego> (<año>): [REDACTAR: ¿sigue siendo ...?]`.
- **Descripción:** línea de apertura `Volvemos a <año> para revisar <Juego>, [REDACTAR: qué es en una frase] 🎮`; párrafo `[REDACTAR: historia, cómo se juega hoy y comparativa]`; si el DATA tiene `pedido`, `[REDACTAR: agradecer a quien lo pidió]`; `[REDACTAR: pregunta a la comunidad]` seguida de `Cuéntanos en los comentarios 👇`; CTA fijo `🔔 Suscríbete a RETROTARROS para más reseñas retro: nostalgia + juegos + música.`; línea de hashtags.
- **Hashtags:** `#RetroReseñas #<Juego> #<Consola> #Retrogaming #Retrotarros`. `<Juego>` sale del nombre en CamelCase sin signos y cortado en el primer `:` (Commandos: Behind Enemy Lines da `#Commandos`); `<Consola>` es la primera plataforma de `consola` (la de lanzamiento original). Un campo opcional `hashtag_juego` en el DATA lo sobreescribe.
- **Tags:** juego, `<juego> reseña`, año, developer (sin el paréntesis "publica ..."), consola(s), género en minúsculas, más la cola fija `retroreseñas, reseña retro, retrogaming, juegos retro, nostalgia gamer, ¿envejeció bien?, retrotarros`, y al final `[REDACTAR: sumar tags propios del juego: personas, secuela, términos]`.
- **Comentario fijado:** `Dato random: [REDACTAR: dato curioso]. [REDACTAR: pregunta]`.
- **Pie:** `**Slug:** `<out_slug>``, `**Formato:** Reseña (horizontal, hasta 10 min)`, `**Última actualización:** <fecha de hoy>`.

### 2. Revisar el kit terminado

`python scripts/resena_kit.py --revisar docs/descripciones/descripcion-<slug>.md` devuelve código 1 si hay errores:

- Queda algún `[REDACTAR`.
- El bloque de tags pasa de 500 caracteres o tiene menos de 15 o más de 20 tags.
- Los hashtags no son 4 o 5, o el primero no es `#RetroReseñas`, o el último no es `#Retrotarros`.
- Falta el CTA de suscripción o el comentario fijado.
- Hay voseo rioplatense (lista corta: tenés, querés, sabés, decime, elegís, defendés, "vos "), porque ya se colaron antes en kits de TarroShorts.

## Decisiones tomadas por mí (para que las revises)

- La primera plataforma de `consola` como hashtag de consola.
- El tope inferior de 15 tags y el superior de 20 (la guía dice "~15-20").
- Código de salida 2 cuando el kit ya existe.
- La lista corta de voseo es heurística y puede ampliarse.

## Lo que queda para quien construya

- Los nombres exactos de las funciones y el texto de los mensajes.
- Pruebas en `scripts/test_resena_kit.py` con asserts simples (sin pytest), incluyendo que el CLI del lint siga funcionando tras el refactor.
- Una línea en `CLAUDE.md` (sección de kit de publicación) y otra en `HANDOFF.md`.
