# Rendimiento del canal

Aquí viven los informes legibles sobre cómo anda el canal: análisis de vistas y suscriptores, pruebas de anuncios y propuestas de hashtags y tags. Los datos crudos (JSON de los scripts de YouTube y los respaldos) quedan en `data/youtube/`.

## Cómo agregar un informe

1. Escribir el informe en esta carpeta con el nombre `<tipo>-<tema>-AAAA-MM-DD.md`. Tipos: `analisis`, `anuncios`, `hashtags`.
2. Agregarlo a la tabla de **Informes** y, si trae cifras del canal, una fila a la tabla de **Seguimiento**.
3. Dejar los datos crudos en `data/youtube/` (los scripts ya lo hacen) y nombrarlos en el informe.
4. Sin números de cuenta, claves ni datos de acceso en estos documentos.

Los scripts que generan los datos: `scripts/youtube_inventario.py` (público, sin credenciales), `scripts/youtube_analisis.py`, `scripts/youtube_analytics.py` y `scripts/youtube_estado.py` (solo lectura). El acceso y sus límites están descritos en la memoria del proyecto (acceso controlado a la API de YouTube).

## Informes

| Fecha | Informe | Qué encontró |
|---|---|---|
| 2026-10-14 | [analisis-canal-2026-10-14](analisis-canal-2026-10-14.md) | Los Shorts suman el 87% de las vistas, pero con Analytics se corrigió: 83% de las vistas eran publicidad. Las reseñas rinden 500 a 900 vistas orgánicas cada una. |
| 2026-10-14 | [hashtags-propuesta-2026-10-14](hashtags-propuesta-2026-10-14.md) | Propuesta de hashtags y etiquetas por tipo de video; se aplicó a los 82 videos el mismo día. La receta vigente está en `docs/canal/guia-youtube-viral.md`, sección 4. |
| 2026-10-28 | [anuncios-gamecube-2026-10-28](anuncios-gamecube-2026-10-28.md) | Prueba de anuncios con unos 10.000 CLP: 759 vistas, 2 suscriptores y unos 1.840 CLP por hora de reproducción. Recomienda no subir el presupuesto con ese esquema. |
| 2026-10-29 | [hashtags-propuesta-2026-10-29](hashtags-propuesta-2026-10-29.md) | Propuesta de hashtags sobre el inventario nuevo (88 videos). Solo se aplicó el caso de Melee, que había quedado fuera de la receta (6 hashtags con `#Gaming` y `#fyp`): ahora `#RetroReseñas #SuperSmashBrosMelee #GameCube #Retrogaming #Retrotarros`, con sus 18 etiquetas intactas. Respaldo previo en `data/youtube/respaldo-api-2026-10-29-154728.json`. |
| 2026-10-29 | [analisis-canal-2026-10-29](analisis-canal-2026-10-29.md) | Las vistas bajaron con la publicidad (84% sigue siendo pagada); los suscriptores son pocos pero ven mucho más tiempo por vista; los hashtags y tags están completos y no mueven tráfico medible. |

## Seguimiento

Una fila por análisis, siempre con las mismas columnas, para ver la tendencia sin abrir cada informe. `n/d` = no se midió.

| Periodo | Vistas | % de publicidad | Suscriptores ganados / perdidos | Vistas de suscritos (minutos) | Suscriptores totales | Horas de reproducción, 12 meses, videos largos | Informe |
|---|---:|---:|---:|---|---:|---:|---|
| 14 jul a 12 oct | 153.653 | 83% | 3.272 / 1.294 | n/d (fuente suscriptores: 12.296 vistas) | 2.240 (12 oct) | n/d | análisis 10-14 |
| 29 ago a 27 sep | 73.530 | 81% | 1.114 / 356 | 2.451 (4.856 min) | n/d | n/d | análisis 10-29 |
| 27 sep a 27 oct | 29.834 | 84% | 746 / 300 | 1.334 (5.156 min) | 2.510 (29 oct) | 814,6 h (al 28 oct) | análisis 10-29 y anuncios |

Notas: "Vistas de suscritos" es el estado de suscripción del espectador (SUBSCRIBED), no la fuente de tráfico "feed de suscripciones". Las horas de reproducción vienen del informe de anuncios; ese informe indica 4.000 horas como el umbral que falta cubrir.
