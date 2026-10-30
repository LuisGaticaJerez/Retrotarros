# Encadenar la biblioteca de videos largos (diseño corto)

Fecha: 2026-10-30. Estado: por aprobar. Origen: conversación con Luis sobre llegar a las 4.000 horas válidas de monetización.

## Intención y por qué

Hoy tenemos unas 737 horas válidas de 4.000 y generamos unas 170 al mes; la ventana es móvil de 12 meses, así que se necesita casi el doble de ritmo. Antes de producir más contenido, probar cuánto se mueve el número ayudando a que quien ve un video siga con otro del canal. Es barato, reversible y se mide en dos o tres semanas (ver `docs/canal/rendimiento/analisis-horas-validas-2026-10-30.md`).

Lo que se encontró en el canal (datos en `data/youtube/listas-2026-10-30.json` y `data/youtube/pantallas-finales-2026-10-30.json`):

- Las 7 listas por formato están bien armadas y los 58 videos largos están en una.
- Las pantallas finales existen en 55 de 58 videos pero casi no se ven (retención de 4% a 22%): trajeron 16 vistas y unas 3 horas en 12 meses. Apuntan a solo 10 destinos.
- 0 de 58 descripciones enlazan a otro video o a una lista.
- Las 58 tarjetas son "Ver las correcciones"; no hay tarjetas que recomienden el siguiente video.
- Lo que ya encadena sin ayuda: videos relacionados 243 horas, listas 23 horas (línea base para medir).

## Objetivos, no objetivos, anti-objetivos

- **Objetivo:** subir las horas que vienen de relacionados, listas y pantallas finales en videos largos, sin grabar nada nuevo.
- **No objetivos:** no se tocan Shorts, títulos, etiquetas ni hashtags; no se compran vistas; no se editan tarjetas ni pantallas finales (la API de YouTube no lo permite, se hacen a mano en Studio).
- **Anti-objetivos:** nada que ensucie la descripción (queda una línea o dos), nada que cambie lo ya grabado, nada irreversible: cada cambio guarda respaldo de la descripción original.

## Enfoques considerados

1. Bloque fijo con solo el enlace a la lista del formato. Simple, pero no sugiere un video concreto.
2. Bloque por video: un video recomendado (el de más horas del mismo formato, distinto del propio) más la lista del formato. Un destino concreto convierte mejor que una lista.
3. Lo anterior más cruces entre formatos (una reseña que sugiere una colección). Más trabajo y sin evidencia aún de que sirva.

**Elegido (propuesta mía, por confirmar): el 2.** Se parte por lo concreto y se mide; el 3 se evalúa con los datos.

## El cambio

- Un bloque de dos líneas al final del cuerpo de la descripción, antes de la línea de hashtags:
  - `Sigue con: <título del video recomendado> https://youtu.be/<id>`
  - `Todas las <formato>: https://www.youtube.com/playlist?list=<id>`
- Destino recomendado = el video del mismo formato con más horas válidas que no sea el propio (el segundo, si el propio es el primero). Escrito con tildes (es prosa pública de YouTube).
- Herramienta nueva `scripts/youtube_enlazar.py`, calcada de `youtube_aplicar.py`: modo prueba por defecto (muestra antes y después), respaldo antes de escribir, pide escribir SI, solo cambia la descripción y no repite el bloque si ya existe. Cuota: unas 2.900 de 10.000 unidades por 58 videos.
- Los kits de publicación nuevos (`resena_kit.py` y los de rankings) llevan el mismo bloque desde el inicio, con el enlace al video sugerido que se completa al publicar.
- Medición cada dos semanas con Analytics: minutos de videos largos desde RELATED_VIDEO, PLAYLIST y END_SCREEN contra la línea base.

## Riesgos y puntos abiertos

- El permiso de escritura guardado en `.cache/youtube/token.json` puede haber caducado; si es así hay que volver a autorizar (lo hace Luis en el navegador).
- El efecto de un enlace en la descripción suele ser chico; por eso se mide y no se promete. Lo que sí puede mover más (tarjetas a mitad del video apuntando al siguiente, pantallas finales en los 3 videos que faltan) lo hace Luis a mano en Studio con una lista que preparo yo.
- Qué queda al criterio del constructor: texto exacto del bloque, orden de la aplicación (empezar con 5 videos de prueba).
