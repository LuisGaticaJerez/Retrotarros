# Pauta de serie · ABRIENDO EL TARRO

> **Formato recurrente** de entrevistas a coleccionistas. Esta NO es la pauta de
> un episodio: es la guia de la serie. Cada episodio se arma clonando el template
> `studio/_template-abriendo-el-tarro.html` y llenando los `[PLACEHOLDER]`.

---

## Concepto

Cualquier persona que quiera mostrar su coleccion. **Da lo mismo el artefacto**
—consolas, cartuchos, figuras, revistas, periféricos, juguetes, lo que sea—.
Lo que importa es la **nostalgia**, uno de los pilares del canal.

Es el formato que abre Retrotarros a la **comunidad**: no solo la coleccion de
Koko, sino la de cualquiera que tenga su tarro lleno de recuerdos.

- **Serie fija:** "ABRIENDO EL TARRO"
- **Subtitulo por episodio:** "La coleccion de [nombre]"
- **Captura:** el coleccionista EN CAMARA (presencial o videollamada). Muestra
  sus piezas en vivo; las TarroVisiones se rellenan en edicion con su material.
- **Las JOYAS las elige el coleccionista** (no nosotros). Mas personal, mas nostalgia.

---

## Estructura del episodio (14 slides base, flexible)

| # | Slide | Que va |
|---|-------|--------|
| 01 | Portada | Serie + "La coleccion de [nombre]" + conteo (piezas/categorias/joyas) |
| 02 | Quien es | Presentacion + ORIGEN de la coleccion. **Aca vive la nostalgia.** |
| 03 | Ficha del coleccionista | Tarjeta de marca: desde cuando, que colecciona, piezas, origen, lo mas preciado |
| 04 | Indice | Las categorias de SU coleccion (flexibles) + "Las Joyas del Tarro" |
| 05-06 | Categoria 01 | Paneo (TV grande) + Triple (3 destacadas) |
| 07-08 | Categoria 02 | Paneo + Triple |
| ... | Categoria N | **Duplica el par paneo+triple por cada categoria** |
| 09 | Divider JOYAS | Entrada a la seccion de joyas |
| 10-12 | Joya 01..03 | Una joya por slide, con su HISTORIA (la elige el dueno) |
| 13 | Joya de la corona | La pieza #1. La que jamas venderia. Momento emotivo. |
| 14 | Cierre | Reflexion + donde seguir al invitado + CTA "muestra tu tarro" |

**Reglas de flexibilidad:**
- Las **categorias no son fijas** (no FPS/Accion como en juegos). Dependen de
  cada coleccion: "consolas", "lo sellado", "figuras", "imports", "revistas"...
- Agrega o saca pares paneo+triple segun cuantas categorias tenga.
- Agrega o saca slides de joya segun cuantas traiga el invitado.
- Si una categoria es chica, puede ir solo el paneo (sin triple).

---

## Como armar un episodio

1. Copia `studio/_template-abriendo-el-tarro.html` a
   `studio/abriendo-el-tarro-<nombre>.html` (slug en minuscula con guiones).
2. Reemplaza todos los `[PLACEHOLDER]` entre corchetes.
3. Ajusta cantidad de categorias (pares paneo+triple) y de joyas.
4. Renumera los `slide-num` si agregaste/sacaste slides (el contador del footer
   se ajusta solo).
5. Genera capturas: `python scripts/capture-slides.py abriendo-el-tarro-<nombre>`
6. Sincroniza al estudio: `scripts/sync-to-drive.ps1` (HTML + capturas por-episodio).
7. Completa el **set canonico**: pauta MD del episodio, discusion MD, publicacion YT.

---

## Tono editorial

- **Nostalgia primero.** La pregunta clave siempre es *"¿que recuerdo tiene esta
  pieza?"*, no *"¿cuanto vale?"*. El valor sentimental manda sobre el de mercado.
- Chileno neutro con tuteo. Conversacional, dos amigos mirando un tarro de tesoros.
- Sin solemnidad. Humor cariñoso, igual que el resto del canal.
- El invitado es el protagonista: Luis/Koko guian y reaccionan, no compiten.

---

## Guia de preguntas para la entrevista (para sacar la nostalgia)

**Origen (slide 02):**
- ¿Cual fue la primera pieza de tu coleccion? ¿Como llego a ti?
- ¿Que te enganchó a coleccionar? ¿Hubo un momento exacto?
- ¿Coleccionas para jugar, para tener, o para recordar?

**Por categoria (paneos):**
- ¿Cual de esta categoria buscaste mas tiempo?
- ¿Hay alguna que conseguiste de pura suerte?
- ¿Cual te recuerda mas a tu infancia?

**Joyas (las elige el invitado):**
- ¿Por que esta es una joya para ti? (que NO sea el precio)
- ¿Como la conseguiste? La cacería, el dato, el regalo.
- ¿Que sentiste cuando por fin la tuviste en la mano?

**Joya de la corona:**
- Si la casa se incendia y solo salvas una pieza, ¿cual es?
- ¿Por que esa sobre todas las demas?

**Cierre:**
- ¿Que te falta? ¿Cual es el santo grial que aun persigues?
- ¿Donde te pueden seguir / ver mas de tu coleccion?

---

## Notas de produccion

- TarroVisiones **vacias** en el HTML; el material del invitado (fotos/video de
  sus piezas) se compone en edicion. Nos guiamos por el namebox/titulo de abajo.
- Como el coleccionista esta en camara, la toma principal en OBS es el invitado;
  los slides entran como cortina/overlay para los paneos y joyas.
- Primer formato de comunidad del canal. Si funciona, es replicable infinito:
  cada persona = un episodio.
- CTA permanente: invitar a la audiencia a mostrar SU tarro (genera cola de invitados).
