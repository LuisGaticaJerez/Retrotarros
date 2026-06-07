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

- **Super Mario Bros. sellado (grial)**: USD 2.000.000 documentado (Rally, 2021; Engadget/GameSpot). Copia WATA 9.8 A+ edicion "hangtab". Sigue siendo el record de un juego de NES en 2026.
- **Stadium Events sellado**: remate documentado de USD 41.977 (Kotaku). En el deck lo dejamos en "USD 25.000" como valor CIB representativo, y la cifra sellada va como dato hablado.
- **NWC dorado**: ventas historicas sobre USD 100.000 (han llegado a 300k+ segun copia/condicion). Lo dejamos en "USD 100.000+" como climax de rarezas.

---

## La estructura de tres bloques (convencion del canal)

Igual que `snes-top-precios`, el episodio separa por como llego el juego al mundo:

1. **Top 10 RETAIL**: solo juegos que se vendieron en tiendas. Es el ranking "de verdad", ordenado por valor CIB. Aca el #1 es **Stadium Events** (retail retirado, USD 25.000), que se escapa de los demas (que rondan los miles).
2. **Apartado RAREZAS / NO-RETAIL**: variantes, sin licencia (Panesian), exclusivos de alquiler (Blockbuster), hallazgos de bodega y cartuchos de competencia (Campus Challenge, NWC gris y dorado). NO se vendieron en retail normal, por eso van aparte con etiqueta en vez de numero. El climax del apartado es el **NWC dorado** (26 copias, USD 100.000+): el mas raro del mundo.
3. **SANTO GRIAL**: el que se escapa de todo precio = la **venta record**. Aca: **Super Mario Bros. sellado** WATA 9.8 A+, vendido en **USD 2.000.000** (2021, sigue siendo record en 2026).

**Dos ejes de "el mas caro" (decision editorial, validada con Luis):**
- Por **rareza/escasez** manda el NWC dorado (26 copias). Va como climax de las rarezas.
- Por **venta record** manda Super Mario Bros. sellado (USD 2M). Va como santo grial.
- El grial es la venta record porque es el numero mas alto y mas impactante. CLAVE aclarar en vivo: es una copia SELLADA Y GRADUADA (WATA 9.8) en estado casi perfecto — NO el cartucho suelto comun (que vale ~USD 10). Es el fenomeno "boom WATA" 2020-2021.

**Por que esta separacion**: meter los NWC (USD 30k-100k) o el SMB sellado (USD 2M) en el mismo ranking que Bonk (USD 900) aplastaria todo. Separando, el top retail es comparable entre si, las rarezas brillan en su liga, y el grial cierra con el numero imposible. Misma logica del SNES (retail → variantes/exclusivos → grial Powerfest 94).

**Decision Stadium Events**: es retail (Bandai lo vendio en tiendas en 1987 antes de retirarlo), asi que va como #1 retail, NO como rareza. Es "el mas caro que de verdad estuvo a la venta".

**Afuera quedaron:**
- **Hot Slots / Peek-A-Boo Poker** (Panesian): para no repetir rareza Panesian (ya esta Bubble Bath Babes).
- **Mr. Gimmick / Recca**: carisimos pero solo PAL/Famicom, no retail NTSC (audiencia Latam juega NTSC).
- **Myriad 6-in-1**: rarisimo pero demasiado obscuro.

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
2. Precios = **valor de mercado aproximado 2026** (se insiste: no es precio fijo, no es consejo de inversion).
3. Tres bloques: **10 retail** (#10→#1) + **6 rarezas** (etiqueta, climax NWC dorado) + **grial** (Super Mario Bros. sellado, venta record USD 2M). Igual que SNES.
4. Deck con `scripts/top_deck.py` (extendido para soportar rarezas con `badge_text` + slide `grial`). Etiqueta de cartucho con color (oro para el NWC dorado).
5. JSON TarroBot: `datos` = solo los 10 retail (#10→#1) con `precio_short`, para que sea compatible con el generador de TarroShorts. Rarezas/grial viven en el deck HTML.

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
