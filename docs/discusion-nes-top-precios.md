# Discusion · NES Top Precios

Documento de trabajo: el "detras de escena" del armado. NO es la pauta.

---

## Por que este episodio cierra el arco NES

El arco de cada consola en el canal es un triptico: **coleccion** (lo que tenemos) → **top mundial** (lo mejor en calidad) → **top precios** (lo mas caro del mercado). Este episodio cierra NES. El de precios es el de mayor enganche puro: las cifras generan reaccion inmediata y comentarios ("yo tenia ese de chico!!").

---

## La tesis: rareza, no calidad

El gancho editorial es que **caro ≠ bueno**. La mayoria de estos cartuchos valen fortunas por escasez, no por ser buenos juegos:

- **Cheetahmen II**: literalmente inacabado y malo, pero rarisimo (hallado en bodega).
- **Stadium Events**: un juego de ejercicio mediocre, pero retirado del mercado.
- **Bubble Bath Babes**: existe por morbo (sin licencia, adulto), no por calidad.

Las excepciones (buenos Y caros) son **Little Samson** y **Bonk's Adventure**. Eso se recalca en vivo.

---

## De donde salen los precios

Cruce de fuentes coleccionistas 2025:

- **PriceCharting** (referencia loose/CIB/new).
- **Den of Geek** "Rarest and Most Valuable NES Games".
- **GameValueNow** (Stadium Events ~10k loose / 20k+ CIB).

Cifras tratadas como **valor de mercado aproximado**: fluctuan con cada subasta. Por eso en pauta se insiste en "aproximado".

### Casos con cifra firme

- **Stadium Events sellado**: remate documentado de USD 41.977 (Kotaku). En el deck lo dejamos en "USD 25.000" como valor CIB representativo, y la cifra sellada va como dato hablado.
- **NWC dorado**: ventas historicas sobre USD 100.000 (han llegado a 300k+ segun copia/condicion). Lo dejamos en "USD 100.000+".

---

## Decisiones de orden y que quedo afuera

El top mezcla dos familias:
1. **Rarezas retail / fin de ciclo** (Bonk, Panic Restaurant, Little Samson, Flintstones).
2. **Cartuchos de competencia / no-retail** (Campus Challenge, NWC gris y dorado) — los mas caros, van al podio.

**Decision clave**: incluir los NWC y Campus Challenge aunque NO sean retail. Son LOS grales del NES y el publico los espera. Se aclara en vivo que eran cartuchos de evento, no de tienda.

**Afuera quedaron:**
- **Hot Slots / Peek-A-Boo Poker** (Panesian): para no repetir la rareza Panesian (ya esta Bubble Bath Babes).
- **Myriad 6-in-1**: rarisimo pero demasiado obscuro, requiere mucha explicacion.
- **Powerfest 94**: es N64-era / prototipo unico, no encaja limpio.

---

## Distincion vs la coleccion del estudio

OJO: este top es de mercado MUNDIAL, no de la coleccion de Luis (`data/coleccion/coleccion-retrotarros.csv`). Ninguno de estos grales esta en la coleccion del estudio (son inaccesibles). Si Luis quiere, puede mencionar en vivo cual de SU coleccion NES es el mas valioso segun el CSV (PriceCharting via GameEye), como contraste honesto: "yo no tengo ninguno de estos, pero el mas caro que SI tengo es...".

---

## Anecdotas / momentos para Luis y Koko

- **Koko**: reaccionar a cada cifra ("¿cien mil dolares por un cartucho?").
- **Luis**: la historia del NWC dorado y el concurso de Nintendo Power.
- **Compartida**: Stadium Events y la señora que lo vendio sin saber lo que tenia (caso real famoso).
- **Compartida**: Blockbuster y como un juego de alquiler termino valiendo miles.

---

## Decisiones de armado (2026-06-07)

1. Triptico NES cerrado: coleccion + mundial + precios.
2. Precios = **valor de mercado aproximado** (se insiste, no es precio fijo, no es consejo de inversion).
3. Podio = los 3 cartuchos de competencia (NWC dorado/gris + Campus Challenge).
4. Deck con `scripts/top_deck.py`: el precio va como etiqueta de bloque; la etiqueta de cartucho usa color (oro para el NWC dorado, buen detalle).
5. JSON TarroBot con `precio_short` por item + reaccion_short (con tildes para TTS).

---

## Riesgos y como mitigarlos

| Riesgo | Mitigacion |
|--------|------------|
| "Ese precio esta mal / desactualizado" | Decir "valor aproximado, fluctua" + citar que son rangos de mercado. |
| Confundir caro con bueno | Tesis explicita: rareza, no calidad. |
| Parecer consejo de inversion | Nunca recomendar comprar/vender como inversion. |
| Sin fotos de los grales a tiempo | HTML con etiqueta de color + NO SIGNAL. |

---

**Ultima actualizacion:** 2026-06-07
**Pauta asociada:** `docs/pauta-nes-top-precios.md`
**HTML:** `studio/nes-top-precios.html`
