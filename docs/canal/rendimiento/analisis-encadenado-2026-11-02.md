# Encadenar la biblioteca: qué se hizo y cómo se mide

Fecha: 2026-11-02. Datos de partida del 30 de octubre. Diseño en `docs/superpowers/specs/2026-10-30-encadenar-biblioteca-design.md`.

## Qué se hizo (30 de octubre)

- Los 56 videos largos con una lista de 2 o más videos tienen ahora, antes de los hashtags, dos líneas: `Sigue con: <video> <enlace>` y el enlace a la lista de su formato. El video sugerido es el de más horas orgánicas (sin anuncios) de su misma lista. Respaldos previos en `data/youtube/respaldo-api-2026-10-30-205439.json` y `...-205800.json`.
- Se corrigió de paso un defecto de las herramientas: `videos().update` reemplaza el snippet completo y 83 videos habían quedado con audio en en-US. Se restauraron a es-419 y desde ahora toda escritura pasa por `youtube_aplicar.cuerpo_snippet` (regla en `CLAUDE.md`).
- Los kits nuevos de reseñas traen el bloque en el esqueleto.

## Para hacer en Studio (tarjetas y pantallas finales)

Son tres videos con pantalla final que no empuja a otro video largo. Conviene que apunten al mismo destino que su "Sigue con", así el espectador ve la misma recomendación en la descripción y en pantalla:

| Video | Enlazar a (elemento de video) | Segundo elemento |
|---|---|---|
| Street Fighter 2: El juego que Capcom no le tenía fe | Zombies Ate My Neighbors (`RkRTO4KBRBg`) | Lista Retroreseñas |
| Zombies Ate My Neighbors: ¿envejeció bien el shooter de LucasArts? | Killer Instinct (`93dORrQx41M`) | Lista Retroreseñas |
| El recorrido COMPLETO por la colección de Super Nintendo | La colección completa de Nintendo 64 (`guG5ZOfjwqM`) | Lista Colecciones |

La tarjeta (la "i" de arriba a la derecha) va mejor en el minuto donde el video menciona al destino, no al inicio.

## Cómo se mide (13 de noviembre de 2026, dos semanas después)

Consulta: minutos vistos de videos largos (`creatorContentType==videoOnDemand`) por fuente de tráfico, `RELATED_VIDEO`, `PLAYLIST` y `END_SCREEN`, del 31 de octubre al 13 de noviembre. Se compara con la base, que es de 12 meses (6 de mayo a 30 de octubre, unos 178 días):

| Fuente | Base 12 meses | Equivale a 14 días | Meta razonable |
|---|---:|---:|---|
| Videos relacionados | 243 h | 19 h | Sobre 19 h |
| Listas de reproducción | 23 h | 1,8 h | Sobre 1,8 h |
| Pantallas finales | 3 h | 0,24 h | Sobre 0,24 h |

Cómo leerlo sin engañarnos:
- Hay que comparar con el ritmo de 14 días, no con las 243 h totales.
- Si sube relacionados pero también subió el total de vistas orgánicas, no es mérito del bloque. Comparar la proporción de relacionados sobre el total de minutos de videos largos (29% en la base).
- Si algún video publicado en esas dos semanas empuja los números, anotarlo.
- Dos semanas es poco: si el efecto es pequeño, repetir a las cuatro semanas antes de concluir.

Al medir: guardar el informe como `analisis-encadenado-2026-11-13.md` y sumar su fila en "Seguimiento" del README.

## Pendiente de afinar

- Los destinos se concentran (29 reseñas apuntan a Zombies, 17 rankings al Top 10 de PS1). Si la medición muestra poca variedad en lo que se ve a continuación, repartir entre los tres mejores de cada formato.
- Detalles menores que no frenan nada y quedaron sin arreglar en `youtube_enlazar.py`: el límite de 5.000 bytes de la descripción no se avisa en la prueba en seco; el marcador "Sigue con:" distingue mayúsculas; los títulos del inventario son del 29 de octubre.
