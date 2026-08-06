# Discusion · Atari 2600 Top Mundial

Documento de trabajo: el "detras de escena" del armado del ranking. NO es la pauta.

---

## Por que este ranking y como se armo

El "top mundial" del canal es siempre el **ranking de calidad** (la contraparte del top precios). Para Atari 2600 cruzamos consenso critico retro (SVG, CBR, GamesRadar, RetroDodo) con hitos historicos verificables via Wikipedia y AtariAge — porque en una consola tan vieja, "el mejor juego" tiene menos que ver con reviews contemporaneas (casi no existen bien documentadas) y mas con impacto real en la industria.

A diferencia del top precios (cifras objetivas de mercado), aca hay subjetividad. El episodio invita explicitamente a debatir.

---

## El orden y sus polemicas

| # | Juego | Defensa | Polemica posible |
|---|-------|---------|------------------|
| 1 | Pitfall! | Padre del genero plataformas de accion, 255 pantallas en 4KB. | Pac-Man vendio mas — algunos priorizarian ventas sobre critica. |
| 2 | Pac-Man | El mas vendido de toda la consola (8M+). | La conversion es objetivamente mala frente al arcade — polemico ponerlo tan arriba. |
| 3 | Adventure | Primer Easter egg de la historia de los videojuegos. | Jugablemente es tosco hoy — entra por impacto historico, no por diversion actual. |
| 4 | Yars' Revenge | El original (no-port) mas vendido de la consola. | Menos conocido para audiencia joven que Pac-Man o Space Invaders. |
| 5 | River Raid | Carol Shaw, primera disenadora mujer reconocida. | Podria subir mas por el peso del dato historico. |
| 6 | Space Invaders | Primer killer app de la industria. | Hoy se siente muy simple comparado con lo que vino despues. |
| 7 | Raiders of the Lost Ark | Licencia de pelicula tomada en serio para 1982. | Complejidad de la epoca lo hace dificil de disfrutar sin guia hoy. |
| 8 | Missile Command | Tension estrategica real, dato de las pesadillas del creador. | Menos "divertido" que otros del top segun estandares modernos. |
| 9 | Kaboom! | Control de paddle unico, muy adictivo. | Simplicidad puede leerse como poco memorable para quien no lo vivio. |
| 10 | Combat | El primer videojuego de millones de personas (pack-in). | Calidad de diseno es basica — entra por impacto cultural, no por profundidad. |

---

## Decisiones duras (que quedo afuera)

- **Berzerk (1982)**: pionero del voice synthesis en consola (fue de los primeros juegos con voz digitalizada), pero menos icononico que los elegidos. Mencionable en vivo.
- **Frogger (1982, port de Parker Brothers)**: masivo en ventas, pero la conversion casera se considera inferior — igual que Pac-Man, pero Pac-Man gana por el peso cultural mas grande.
- **Chopper Command / Demon Attack (Activision)**: buenos shooters, pero no marcan un "primero" historico como los elegidos.
- **E.T. the Extra-Terrestrial (1982)**: HISTORICO por razones opuestas — se le atribuye (parcialmente, es mito exagerado) el crash de 1983. No entra al top de calidad, pero es tema obligado para el contexto de la industria en general.

---

## Dato tecnico para lucirse en vivo

- **Adventure** escondia el nombre de su creador, Warren Robinett, en una sala secreta -protesta silenciosa porque Atari no daba credito a los disenadores en esa epoca. Un chico de 15 anios lo descubrio. De ahi nacio el termino "Easter egg" en los videojuegos.
- **River Raid** lo programo y diseno SOLA Carol Shaw -sin equipo- y es reconocida como la primera disenadora de videojuegos mujer de la historia. El exito del juego (1M+ copias) le permitio retirarse joven.
- **Yars' Revenge** no es un port de arcade: se diseno especificamente para el Atari 2600, algo poco comun en esa epoca donde casi todo venia de las maquinas.
- **Pitfall!** metio 255 pantallas completas de selva en apenas 4 kilobytes de memoria -una hazana de programacion que David Crane logro con trucos de reutilizacion de datos.

---

## Anecdotas para Luis y Coco

- **Luis**: la historia de Warren Robinett y el Easter egg de Adventure -contar como Atari no daba credito a los disenadores en los cartuchos.
- **Coco**: si tuvo o jugo alguna vez un Atari 2600 real, o si su primer contacto con estos juegos fue via emulacion/compilaciones.
- **Compartida**: la decepcion historica de Pac-Man -Atari vendio 8 millones de copias de un juego que parpadeaba y se veia mal, y aun asi fue un exito comercial.
- **Compartida**: "River Raid lo hizo una sola persona" como gancho para hablar de cuan chicos eran los equipos de desarrollo en 1982.

---

## Decisiones de armado (2026-07-29)

1. Ranking de **consenso critico + hitos verificables**, no opinion personal (se dice explicito).
2. Años en **release US** (audiencia Latam referencia NTSC).
3. Se prioriza impacto historico ("el primer X") por sobre solo nostalgia pura, porque el Atari 2600 es la consola donde nacieron casi todas las convenciones del medio.
4. Deck generado con `scripts/top_deck.py`. Box art real para los 10 juegos, descargada de Wikipedia y verificada visualmente una por una antes de commitear.
5. **Bug real encontrado y corregido en `_auto_img` (top_deck.py):** buscaba las imagenes en la raiz plana `studio/img/<slug>/` en vez de la carpeta categorizada `studio/rankings/top-mundial/img/<slug>/` donde realmente vive el HTML -bug arrastrado desde la migracion de carpetas por categoria. Las cajas no cargaban en captura hasta corregirlo. Afecta a CUALQUIER top-mundial/top-precios nuevo generado desde esa migracion, no solo Atari 2600.
6. JSON TarroBot con 10 datos #10→#1 + reaccion_short por juego (reacciones con tildes para el TTS).

---

## Riesgos y como mitigarlos

| Riesgo | Mitigacion |
|--------|------------|
| "Tu ranking esta mal" en comentarios | Enmarcar como consenso critico + invitar al debate (engagement). |
| Publico joven no conoce estos juegos | Cada "por que" explica el impacto en terminos de lo que vino despues (ej. "el primer Easter egg"). |
| Datos tecnicos erroneos (fechas, cifras) | Verificados con 2+ fuentes cada uno (Wikipedia + prensa retro). Si hay duda en vivo, no afirmar cifra exacta. |

---

**Ultima actualizacion:** 2026-07-29
**Pauta asociada:** `docs/pauta-atari-2600-top-mundial.md`
**HTML:** `studio/rankings/top-mundial/atari-2600-top-mundial.html`
