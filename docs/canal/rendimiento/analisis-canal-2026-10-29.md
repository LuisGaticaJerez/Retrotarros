# Análisis del canal: hashtags, tags y vistas de suscriptores (2026-10-29)

Fuentes: inventario público con yt-dlp (`data/youtube/inventario-2026-10-29.json`, 88 videos, comparado con el del 14 de octubre después del cambio masivo de hashtags) y YouTube Analytics solo lectura (`data/youtube/analytics-2026-10-29.json`, periodo 27 sep a 27 oct; el periodo anterior, 29 ago a 27 sep, se consultó aparte). No se cambió nada en el canal.

## Vistas y suscriptores

- **Canal hoy:** 2.510 suscriptores, 88 videos, 178.803 vistas totales. El 12 de octubre eran 2.240 suscriptores.
- **Últimos 15 días (14 a 29 oct):** +10.772 vistas totales. **6.628 (62%) vinieron de un solo Short, "Coleccion zelda"**, que ya suma 22.085 y ganó 1 suscriptor en 30 días: es el patrón de las vistas pagadas.
- **Publicidad:** en los últimos 30 días, **25.178 de 29.834 vistas (84%) son de la fuente ADVERTISING**, igual que en el análisis anterior (83%). Esa fuente cayó de 59.903 a 25.178 entre un periodo y otro, y con ella las vistas totales (73.530 a 29.883). Lo orgánico del último mes ronda las 4.600 vistas.
- **Suscriptores ganados:** 746 ganados y 300 perdidos en 30 días (neto +446), contra 1.114 y 356 el mes anterior (neto +758). De los 746, solo unos 20 se atribuyen a un video concreto; el resto llega sin video asociado.

## Qué hacen nuestros suscriptores

| | 29 ago a 27 sep | 27 sep a 27 oct |
|---|---:|---:|
| Vistas de gente suscrita | 2.451 | 1.334 |
| Minutos vistos por suscritos | 4.856 | 5.156 |
| Duración media por vista (suscritos) | 323 s | **527 s (8,8 min)** |
| Duración media por vista (no suscritos) | 58 s | 89 s |
| Vistas por la fuente "feed de suscripciones" | 8.635 | 2.995 |

Lectura: son pocos (4,5% de las vistas), pero **ven más tiempo y más completo**; sus minutos totales subieron aunque sus vistas bajaron. El feed de suscripciones entregó menos vistas (-65%) con casi los mismos minutos (-13%), lo que es compatible con que ahora vean largos y no Shorts. Es una lectura, no una medición de causa.

## Videos nuevos desde el 14 de octubre

| Fecha | Video | Vistas |
|---|---|---:|
| 15 oct | Melee (reseña) | 407 |
| 18 oct | PS1 Top Mundial | 1.056 |
| 20 oct | Mighty Morphin Power Rangers (reseña) | 168 |
| 22 oct | Montezuma's Revenge (reseña) | 99 |
| 25 oct | SNES Top Peores | 213 |
| 27 oct | International Superstar Soccer (reseña) | 189 |

Entre los videos que ya existían, los que más ganaron fueron el ranking de Gamecube (+871), Top Peores N64 (+773) y la reseña de Metal Warriors (+126). Parte de ese avance puede ser publicidad: Analytics no separa el gasto.

## Hashtags y tags

- **Cobertura total:** los 88 videos tienen hashtags y etiquetas. Mediana de 5 hashtags en casi todos los tipos; tags: 14 en reseñas, 11 en Shorts, 14 a 16 en rankings. El bloque de tags más largo mide 393 caracteres (límite 500).
- **Reseñas dentro de la receta de hashtags** (4 o 5, `#RetroReseñas` primero, `#Retrotarros` último): 28 de 29. **La excepción es Melee** (publicada el 15 de octubre, después del cambio masivo): trae 6 hashtags, empieza con `#SuperSmashBrosMelee` y termina con `#fyp`.
- **Tags:** 21 de las 29 reseñas tienen 14 tags, uno menos que el mínimo de 15 de la guía (el cambio masivo del 14 de octubre dejó ese número). No es grave.
- **Efecto sobre el tráfico:** la búsqueda de YouTube trajo 229 vistas en 30 días (0,8%) y los videos relacionados 747 (2,5%, pero con 4.354 minutos, mucho tiempo por vista). Con dos semanas desde el cambio no se ve un efecto medible de los hashtags ni de los tags; el tráfico lo mueve la publicidad.

## Datos que faltan

- **Gasto en publicidad:** Analytics no lo muestra; sin él no se puede calcular costo por vista ni por suscriptor.
- **Impresiones y CTR por video:** la consulta de Analytics responde error 400 (no soportada con esos parámetros); habría que sacarlos de YouTube Studio.
