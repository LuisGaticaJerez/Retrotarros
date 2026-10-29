# Analisis del canal con datos reales (2026-10-14)

Fuente: YouTube Data API (vistas, likes, comentarios, duracion, fecha) de los 82 videos, datos crudos en `analisis-2026-10-14.json`.
Limites: no incluye impresiones, CTR, retencion ni fuentes de trafico (eso vive en YouTube Analytics API / Studio). Los videos mas
antiguos se publicaron cuando el canal era mas chico (1,26 K subs el 20 ago, 2,24 K el 12 oct), asi que la edad confunde la comparacion.

## Totales
82 videos, 168.234 vistas, 5.591 likes, 360 comentarios. **Los 30 Shorts suman 146.915 vistas (87%).**

## Por tipo
| Tipo | Videos | Mediana de vistas | Vistas totales | Likes por 1000 vistas | Comentarios por 1000 vistas |
|---|---:|---:|---:|---:|---:|
| Short | 30 | 272 | 146.915 | 33,6 | 1,0 |
| Reseña | 25 | 310 | 14.177 | 21,0 | 8,6 |
| Coleccion | 5 | 179 | 2.845 | 34,1 | 6,3 |
| Top Mundial | 10 | 163 | 1.699 | 72,4 | 21,8 |
| Abriendo el tarro | 2 | 608 | 1.215 | 50,2 | 21,4 |
| Top Precios | 6 | 120 | 992 | 42,3 | 9,1 |

## Shorts por subtipo
| Subtipo | n | Mediana | Promedio | Maximo |
|---|---:|---:|---:|---:|
| Coleccion (tour de lo que tenemos: portatiles, Mortal Kombat, Zelda...) | 6 | 8.731 | 13.763 | 35.377 |
| Tarrobot "mejor X retro" / mas caros | 9 | 287 | 6.321 | 24.769 |
| Tarrobot datos y curiosidades | 10 | 222 | 215 | 457 |

Por mes (promedio de vistas por short): junio 207, julio 6.475, agosto 14.603, septiembre 35.377.

## Largos (con 14 dias o mas): vistas por dia, mediana
Abriendo el tarro 18,9 · **Reseña 10,3** · Coleccion 1,4 · Top Mundial 1,2 · Top Precios 1,1 · Saga 0,9 · Special 0,5.
Reseñas con "¿envejecio bien?" en el titulo: 10,7 vistas por dia; sin: 10,3 (sin diferencia). Duracion vs vistas por dia: r = -0,34.

## Lo que mas vistas tiene
1. Short "Las portatiles de la coleccion" 35.377 · 2. Short "Coleccion Mortal Kombat" 27.911 · 3. Short "Tarrobot, mejor consola retro" 24.769 ·
4. Short "Tarrobot y el mejor Mario retro" 21.616 · 5. Short "Coleccion zelda" 15.624 · 6. Short "Tarrobot, los mas caros de la historia" 9.014.
Mejor largo: reseña de Zombies Ate My Neighbors, 3.967 vistas.

## CORRECCION (mismo dia, con YouTube Analytics): casi todas esas vistas de Shorts eran publicidad

Con el permiso de Analytics (periodo 2026-07-14 a 2026-10-12): **127.367 de 153.653 vistas (83%) vienen de la fuente ADVERTISING** (publicidad de YouTube).
Los Shorts mas vistos son casi puro anuncio, no vistas organicas: portatiles 33.987 de 35.378; Mortal Kombat 26.376 de 27.910; Tarrobot mejor consola 24.492 de 24.646;
Tarrobot mejor Mario 21.063 de 21.616; Zelda coleccion 11.877 de 12.608. Las conclusiones de arriba sobre "que Shorts funcionan" NO valen como organico.

Lo organico (sin publicidad), periodo de 90 dias:
- Mejores Shorts organicos: "Pequeña colección de consolas de Nintendo 64" 1.838 (retencion 89%), "Generaciones Nintendo en sus controles" 1.355, "controles n64" 471. Todos de hardware Nintendo de la coleccion.
- Mejores largos organicos: Zombies Ate My Neighbors 3.967, Abriendo el tarro (Rodrigo) 1.087, Golden Axe 917, Top Gear 870, Killer Instinct 772, Metal Gear Solid 716. Las reseñas rinden 500 a 900 organicas cada una.
- Fuentes organicas del canal: suscriptores 12.296, Shorts 7.429, pagina del canal 2.594, videos relacionados 2.112, busqueda 812.
- Los anuncios casi no traen suscriptores: los 6 Shorts mas anunciados sumaron ~23 suscriptores atribuidos. El canal gano 3.272 y perdio 1.294 suscriptores en el periodo (neto +1.978).
- El largo "recorrido COMPLETO por la coleccion de Super Nintendo" recibio 1.178 vistas de anuncio con 7,9% de retencion.

Pendiente de saber: cuanto se gasto en publicidad (Analytics no lo muestra) para calcular costo por vista y por suscriptor.

