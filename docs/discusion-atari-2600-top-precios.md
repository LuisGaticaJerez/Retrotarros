# Discusion · Atari 2600 Top Precios

Documento de trabajo: el "detras de escena" del armado del ranking. NO es la pauta.

---

## Por que este ranking y como se armo

Siguiendo la Convencion del TOP PRECIOS del canal (3 bloques obligatorios), el desafio especifico de Atari 2600 fue separar bien el **top retail real** (juegos que de verdad se vendieron en tiendas, aunque fuera poco) de las **rarezas mail-order/promocionales** (que nunca pasaron por un canal de venta normal). En Atari 2600 esta linea es mas dificil de trazar que en NES/SNES porque el mercado de coleccionismo de esta consola esta dominado por casos de nicho (mail-order religioso, promocionales corporativos, un juego con 1 copia conocida) mas que por ediciones limitadas de juegos mainstream.

---

## Como se armo el top retail

Fuente base: retrogamepriceguide.com (ranking ordenado por precio), verificado cruzando gamerant.com y racketboy.com para los casos puntuales (Karate Ultravision, Eli's Ladder). Se excluyeron del ranking dos entradas que aparecian en la fuente pero NO son juegos: "Color Bar Generator" (herramienta de calibracion tecnica) y "Copy Cart" (accesorio para copiar cartuchos).

---

## El orden y sus polemicas

| # | Juego | Por que vale eso | Polemica posible |
|---|-------|-------------------|-------------------|
| 1 | River Patrol | Fox Video Games broto y murio con el crash del 83 -tirada minima. | Es una compania tan chica que casi nadie la conoce, puede sentirse "random" en pantalla. |
| 2 | Texas Chainsaw Massacre | Tiendas se negaron a venderlo, produccion baja. | Contenido violento -aclarar contexto historico sin sonar a que se aprueba el contenido. |
| 3 | Out of Control | Ultimos meses de Atari antes del crash. | Nombre generico, poco reconocible para el publico. |
| 4 | Halloween | Mismo caso que Texas Chainsaw Massacre, misma publisher. | Igual que arriba: aclarar contexto de censura de tiendas, no glorificar violencia. |
| 5 | Cakewalk | US Games (Quaker Oats) entro y salio rapido del rubro. | Dato curioso pero el juego en si es poco memorable. |
| 6 | Quadrun | Fin de ciclo de Atari, produccion minima. | Empata en precio con Eli's Ladder -verificar cual poner primero segun fuente mas reciente. |
| 7 | Eli's Ladder | Juego educativo, tirada extremadamente limitada. | Es educativo, no de accion -puede sentirse "raro" en un top de precios de un canal de retrogaming. |
| 8 | Gravitar [Silver Label] | Variante de fin de ciclo de un juego popular de Atari. | Es una VARIANTE del Gravitar normal, hay que explicar bien la diferencia (silver label) para que no se confunda con el juego base. |
| 9 | Ghost Manor | Cartucho Double-Ender (2 juegos en 1). | El otro juego del mismo cartucho (Spike's Peak) no esta en el top -mencionar igual como curiosidad. |
| 10 | Karate [Ultravision] | Version Ultravision original, rarisima; version Froggo, comun. | Confusion real: MUCHOS coleccionistas compran la version Froggo pensando que vale lo mismo. Buen dato de alerta para coleccionistas nuevos. |

---

## Decisiones duras (que quedo afuera / donde se puso)

- **Color Bar Generator ($4.995)**: es una herramienta tecnica de Atari para calibrar televisores, no un juego. Se excluyo del ranking de juegos aunque valga mas que el #1 actual.
- **Copy Cart ($1.000)**: es un accesorio (dispositivo para copiar cartuchos), no un juego. Excluido por el mismo motivo.
- **Stadium Events / Nintendo World Championships (equivalentes NES)**: no aplican a Atari 2600, se mencionan solo si Coco o Luis quieren comparar cross-consola en vivo.
- **E.T. the Extra-Terrestrial**: HISTORICO por ser el chivo expiatorio (parcialmente mito) del crash de 1983, pero hoy vale muy poco porque Atari produjo demasiadas copias (el mito de "enterrados en el desierto de Nuevo Mexico" es real, pero eso significa que sobreviven MUCHAS copias, no pocas). Buen dato de contraste para mencionar en vivo: "el juego mas famoso por arruinar todo vale casi nada hoy".

---

## Dato tecnico para lucirse en vivo

- **Air Raid** es el UNICO cartucho de Atari 2600 con forma de T en toda la historia de la consola -diseño exclusivo de Men-A-Vision, un estudio sin relacion oficial con Atari (lo aclaraban en la propia caja).
- **Gamma Attack** lo hizo un programador aficionado, dueño de una empresa (Gammation) que vendia accesorios de hardware para el 2600 -el juego fue casi un anuncio de una sola vez en una revista.
- **Texas Chainsaw Massacre y Halloween** los publico Wizard Video, una distribuidora de peliculas de terror en VHS que se metio al negocio de los videojuegos -no un estudio de juegos tradicional.
- **Karate [Ultravision] vs [Froggo]**: mismo juego exacto, pero Ultravision transfirio la distribucion a Froggo casi enseguida de lanzarlo. La version Froggo (comun, casi sin valor) inundo el mercado, mientras la Ultravision original (rara) quedo escasa.

---

## Anecdotas para Luis y Coco

- **Luis**: contar la historia de Wizard Video llevando peliculas de terror censuradas a un cartucho de consola -el contexto cultural de 1983 (los videojuegos se consideraban juguete de niños).
- **Coco**: reaccion en vivo al precio de Gamma Attack ($500.000 pedidos por UNA copia) -buen momento para humor/incredulidad genuina.
- **Compartida**: la ironia de que Karate Ultravision y Karate Froggo son EL MISMO juego con valores opuestos -ejemplo perfecto para explicarle a la audiencia como funciona el coleccionismo (no es el juego, es la escasez de la edicion).
- **Compartida**: contraste directo con el episodio anterior -"¿se acuerdan que Pitfall! era el numero 1 del top mundial? Aca ni aparece."

---

## Decisiones de armado (2026-07-29)

1. Estructura de 3 bloques obligatoria: Top 10 retail + rarezas/no-retail + santo grial (regla del canal).
2. Precio SIEMPRE grande arriba-derecha en cada slide (`_price_of`/`_right` en `top_deck.py` lo detecta automatico via el campo `price`/`precio_short`/`meta`).
3. Se excluyeron 2 entradas de la fuente base que NO son juegos (Color Bar Generator, Copy Cart).
4. Box art: se intento descargar 15 imagenes via Wikipedia. **9 de 15 resultaron incorrectas** (Wikipedia resolvio a articulos equivocados: el juego "Control" de 2019 en vez de "Out of Control", la serie de TV "Eli Stone" en vez de "Eli's Ladder", una foto de la consola misma en vez de "Gamma Attack", el arcade "Gauntlet" de 1985 en vez del Atari 2600 mail-order, "Karate Champ" en vez de "Karate", un pin promocional en vez de la caja de "Pepsi Invaders", un flyer de arcade japones en vez de "River Patrol", y una imagen de 7MB no relacionada para "Cakewalk"). Cada una se verifico visualmente antes de commitear y se descarto si no era la caja real -regla del canal (nunca logo/imagen incorrecta), sin excepciones aunque implique mas fallback de lo usual.
5. **Bug de `_auto_img` corregido** (mismo fix que en `atari-2600-top-mundial`, ver esa discusion para el detalle tecnico).
6. JSON TarroBot con 10 datos #10→#1 (solo el top retail, las rarezas y el grial no llevan JSON de TarroBot por ahora).

---

## Riesgos y como mitigarlos

| Riesgo | Mitigacion |
|--------|------------|
| Se malinterpreta como consejo de inversion | Aclarar explicito en vivo: "valor de mercado, no consejo financiero". |
| Contenido de Texas Chainsaw Massacre/Halloween suena a promover violencia | Enmarcar como contexto historico/censura de la epoca, no reaccion de "que genial la sangre". |
| Confusion entre variantes (Karate Ultravision vs Froggo, Gravitar silver label) | Explicar la diferencia en camara antes de dar el precio -sino suena a error. |
| Box art fallback en mas de la mitad del top | Es aceptable segun regla del canal (nunca forzar imagen incorrecta) -compensar con gameplay real en la TarroVision durante la edicion. |

---

**Ultima actualizacion:** 2026-07-29
**Pauta asociada:** `docs/pauta-atari-2600-top-precios.md`
**HTML:** `studio/rankings/top-precios/atari-2600-top-precios.html`
