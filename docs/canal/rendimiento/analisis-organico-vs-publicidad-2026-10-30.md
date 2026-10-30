# Vistas orgánicas frente a publicidad, desde el inicio del canal (2026-10-30)

Pregunta de Luis: al dejar de pagar anuncios las vistas caen mucho, ¿hay un shadow ban? Fuente: YouTube Analytics solo lectura, vistas diarias por fuente de tráfico del 6 de mayo al 27 de octubre (`data/youtube/serie-diaria-fuentes-2026-10-30.json`, 170 días con datos; el canal parte hacia el 6 de mayo). No se cambió nada en el canal.

## Resultado corto

No hay señales de restricción. Las vistas orgánicas (todo lo que no es publicidad) de los días sin anuncios son **mayores** que las de antes de pagar. Lo que cae al apagar los anuncios es la parte pagada, que era casi todo el volumen.

## Las cifras

| Etapa | Días | Vistas orgánicas por día (media / mediana) |
|---|---:|---|
| Antes de los anuncios (11 may a 5 jul) | 56 | 79 / 35 |
| Con anuncios activos (desde el 6 jul) | 89 | 290 / 206 |
| Sin anuncios (desde el 6 jul, días con menos de 30 vistas pagadas) | 25 | 138 / 97 |
| Desde que se apagaron los anuncios (18 al 27 oct) | 10 | 193 |

Vistas por mes, pagadas y orgánicas:

| Mes | Pagadas | Orgánicas | Días con anuncios |
|---|---:|---:|---:|
| Mayo (desde el 6) | 0 | 678 | 0 |
| Junio | 0 | 3.353 | 0 |
| Julio | 35.169 | 5.876 | 19 |
| Agosto | 27.899 | 7.408 | 19 |
| Septiembre | 59.316 | 11.908 | 26 |
| Octubre (al 27) | 22.787 | 4.250 | 25 |

Total pagado en el periodo: 145.171 vistas contra unas 33.500 orgánicas.

## Lo que dicen los datos

- **Sin anuncios el canal no cae bajo su base de antes.** En junio, sin pagar nada, entraban unas 79 vistas al día (con un pico de Shorts a inicios de mes). Los días sin anuncios de julio a octubre promedian 138, y las últimas diez jornadas, 193.
- **La publicidad dura más de lo recordado.** Hay anuncios en 89 días entre el 6 de julio y el 17 de octubre, con una mediana de unas 1.700 vistas pagadas diarias, y son continuos en septiembre y octubre. Los anuncios se cortaron el 18 de octubre (quedan unas 110 vistas pagadas al día de arrastre). Luis recordaba un par de semanas de julio y agosto; hay que revisar en la cuenta de anuncios si septiembre y octubre fueron otra campaña, una renovación automática o una promoción creada desde YouTube.
- **Lo orgánico sube cuando hay anuncios** (290 contra 138 al día). Puede ser que las vistas pagadas arrastren algo de tráfico (relacionados, suscriptores que vuelven) o que coincidan con semanas de más publicaciones; con estos datos no se separa.
- **La caída de los últimos días es la fuente pagada que se apagó.** Octubre pasó de unas 1.800 vistas pagadas al día a 110 el 18 de octubre, y eso explica casi toda la baja de vistas totales.
- **Alcance real orgánico.** Una vez descontada la publicidad, el canal trae unas 150 a 200 vistas diarias, con más peso de los suscriptores (feed de suscripciones) que de la búsqueda (1.094 vistas en todo el periodo).

## Hipótesis que sigue en pie

Los no suscritos que llegan por anuncios ven en promedio unos 89 segundos (los suscritos, 8,8 minutos). Si el sistema de recomendación aprendió de esas vistas, podría mostrar los videos nuevos a público que no se queda. Es una hipótesis sin prueba: lo orgánico actual está por encima de la base de antes, así que no se ve un daño medible. Para probarla habría que comparar la retención de los videos largos nuevos con y sin anuncios, o probar un periodo largo sin pagar.

## Datos que faltan

- Gasto por campaña y fechas reales de cada una (para costo por vista y por suscriptor, y para confirmar septiembre y octubre).
- Impresiones y CTR por video, que Analytics no entrega con esta consulta (hay que sacarlos de YouTube Studio).
- Suscriptores ganados por fuente de tráfico: la consulta no se permite por día y fuente.
