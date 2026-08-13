# Discusion editorial · `snes-top-precios`

> Documento de decisiones que se tomaron al armar el episodio. Lectura
> obligatoria antes de grabar para no abrir debates resueltos.

---

## 1. Por que ranking de precios y no de calidad

Ya tenemos `snes-top-mundial` cubriendo calidad/critica. Este episodio existe porque **el ranking de precios contesta una pregunta distinta** y genera mas conversacion en chat:
- Top calidad → "¿cual es el mejor?"
- Top precios → "¿cual vale mas?" → "¿es justo que valga eso?"

La segunda pregunta es mas viral y mas debatible. Por eso este episodio es probablemente el de mayor CTR de los dos.

---

## 2. Criterio de precios

PriceCharting CIB NTSC USA mayo 2026. Razones:
- **PriceCharting** es la referencia mas neutra del coleccionismo (no es eBay actual, es promedio historico).
- **CIB** (Complete In Box) es el estandar de coleccionismo, no "loose".
- **NTSC USA** porque es el region con mas demanda y mejor track historico.
- **Mayo 2026** porque los precios se mueven — fechar el snapshot evita correcciones publicas.

---

## 3. Top 10 + Kicker · estructura cerrada

Decision tomada: **10 items principales + 1 kicker fuera de concurso**. El kicker (PowerFest '94 a $23.000) no entra en el top porque:
1. **No es retail.** Es promo de torneo. Solo 2 copias en el mundo.
2. **Si entrara como #1, hace todo el resto del ranking pequeno.** $23.000 vs $3.500 = 6.5x. Distorsiona escala visual.
3. **Es bomba narrativa.** Mejor reservarlo para el cierre como reveal en lugar de abrir con el.

Patron replicado de `n64-top-precios` (que tiene el ClayFighter Sculptor's Cut sealed a $9.199 como kicker fuera del top).

---

## 4. Cruz con top mundial

El UNICO juego que aparece en ambos rankings es **Earthbound**:
- Top mundial: #8 (calidad/influencia cultural)
- Top precios: #1 (rareza fisica + big box)

Eso es contenido narrativo IMPORTANTE. Se anticipa en el cold open ("spoiler: solo uno cruza") y se cierra en el balance final. Crea coherencia entre los dos episodios y motiva al espectador a ver los dos.

---

## 5. Items polemicos (decisiones argumentadas)

### #2 Wild Guns ($2.500)

Hay debate sobre si Wild Guns vale 2500 o 1800. Decision: **2.500 USD** porque PriceCharting promedia subastas Heritage de los ultimos 12 meses. Si Luis cita un precio distinto en camara, va con "PriceCharting en mayo 2026 lo tiene en $2.500."

### #4 Chrono Trigger ($1.200)

Algunos coleccionistas argumentan que deberia ser mas alto por su status legendario. Pero el problema es que se imprimio **mucho** — el cartucho suelto es facil de encontrar (~$200), CIB con caja y manual sube a $1.200, pero **sealed** se va a $5.000+. Aqui hablamos de CIB, no sealed.

### Earthbound a $3.500 (incluye player's guide)

El precio $3.500 es por la "**Big Box CIB con player's guide**". Sin player's guide, el CIB baja a ~$1.500. La player's guide oficial sola se vende a $300+. La diferencia es crucial — lo que define el #1 NO es el cartucho, es la caja-VHS-size completa con guide y stickers.

### #7 FF VI vs #4 Chrono Trigger

Pareceria contradictorio que FF VI valga menos que Chrono Trigger siendo ambos Square. Razon: FF VI tuvo **mayor tiraje NTSC** que Chrono Trigger porque Square lo distribuyo mejor en USA. Chrono Trigger se imprimio menos. Mas oferta = menor precio CIB. Estos detalles los explica Luis en camara.

---

## 6. Por que NO esta Demon's Crest mas arriba

Demon's Crest tiene fans hardcore que pagarian $700+, pero el promedio PriceCharting lo deja en $400. La razon es que el mercado oferta-demanda es estrecho: poca gente lo quiere, pero la que lo quiere lo paga caro. El promedio bajo refleja que hay pocas ventas; las subastas individuales pueden ser mucho mas altas.

**No incluir esta nota en el episodio** — confunde al espectador casual. Si Koko o Luis preguntan en camara, responder con "PriceCharting promedio."

---

## 7. Estructura narrativa por bloques

El ritmo del episodio NO es "10 items uno tras otro" sino:

- **Items #10-#7** (Demon's Crest, Harvest Moon, Super Mario RPG, FF VI) → pasada rapida (~1 min cada uno).
- **Items #6-#4** (Pocky & Rocky 2, Mega Man X3, Chrono Trigger) → pasada normal (~1:30 cada uno).
- **Top 3** (Aero Fighters, Wild Guns, Earthbound) → expandidos a 2-3 min cada uno con anecdotas.
- **Kicker** (PowerFest '94) → 3 min completos como mini-historia con suspenso.

Tiempo total estimado: 4 × 1 + 3 × 1.5 + 3 × 2.5 + 3 (kicker) + 4 (intro/outro/recap/balance) = ~22 min.

---

## 8. Bloque PowerFest '94 · que se dice exactamente

Lo critico de este bloque es **no spoilearlo al inicio del episodio**. La estructura del relato:

1. **Build-up:** "Despues del top, queda uno fuera de concurso. No es retail, es PROMO."
2. **Setup historico:** "Nintendo of America organizo PowerFest '94, un torneo nacional."
3. **El dato escalofriante:** "Fabricaron 33 cartuchos para el torneo."
4. **El twist:** "Cuando termino, desarmaron 31 para repuestos. Quedaron 2."
5. **La cifra:** "La ultima venta documentada fue en 2026. Veintitres mil dolares."
6. **Cierre:** "Esto ya no es coleccionismo. Es museo."

---

## 9. Reglas inmutables aplicadas

- **TarroVisiones VACIAS** en los HTMLs (regla canal). El cartucho fisico y el box art van en `.cart-img` no en `.tv-screen-inner`.
- **Sin tildes** en HTML visible.
- **Sin emojis** en titulos / labels.
- **Chileno neutro con tuteo** en pauta y discusion.

---

## 10. Material a grabar (checklist resumido)

- [ ] Cartuchos fisicos de los items que tenga Koko (al menos #1 Earthbound, #4 Chrono, #7 FF VI, #8 Super Mario RPG).
- [ ] Render/foto Earthbound Big Box ABIERTA (cartucho + manual + player's guide visible).
- [ ] Imagen del PowerFest '94 en alta resolucion (Wikipedia commons o similar).
- [ ] Captura comparativa final Top Mundial vs Top Precios (cruz unica Earthbound).

---

## 11. Para el futuro

El formato "top precios" + kicker fuera de concurso se replica facil:
- `n64-top-precios` (ya cerrado, con ClayFighter Sculptor's Cut + Majora gris NFR como kickers).
- `psvita-top-precios` (ya cerrado).
- Futuros: `ps1-top-precios`, `gba-top-precios`, etc.

**Plantilla canonica del formato Top Precios del canal:**
1. Recap del top mundial (slide 02).
2. Recorrido #10 → #1 (10 slides hibridos cartucho + box art + meta + por que es caro).
3. Kicker fuera de concurso (slide 12, "HOLY GRAIL").
4. Balance final con cruz vs top mundial.
5. Cierre con CTA "¿cual te falta?".

---

*Discusion cerrada · 2026-05-24 · Luis Balbrigame*
