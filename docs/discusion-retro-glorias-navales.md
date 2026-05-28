# Discusion editorial · `retro-glorias-navales`

> Documento de decisiones que se tomaron al armar el episodio. Lectura
> obligatoria antes de grabar para no abrir debates resueltos.

---

## 1. Por que un especial de fecha

El canal vive de episodios "tipo arco" (ranking de calidad, ranking de precios, coleccion, hardware raro, etc). Los **especiales de fecha** son una linea paralela:

- **Pro:** alta viralidad en su semana (gente busca contenido tematico).
- **Pro:** algoritmo YouTube favorece contenido fechado en su contexto.
- **Pro:** humor + fecha + nostalgia = combo retroactivo para audiencia chilena.
- **Contra:** vida util limitada (post-21 de Mayo decae el interes).
- **Mitigacion:** subir el especial **el dia 20** para que llegue al algoritmo del **21**.

Este es el piloto. Si funciona, se replican otras fechas (ver pauta MD).

---

## 2. Por que humor y no homenaje serio

El 21 de Mayo es fecha solemne en Chile (Combate Naval de Iquique, muerte de Arturo Prat). Pero el canal Retrotarros NO es academico ni patriotico. El homenaje SOLEMNE seria fuera de tono.

Solucion: **homenaje lateral con humor cariñoso.** No homenajeamos a Prat ni a la Esmeralda directamente, sino a "los marineros retro." El chiste es la **transposicion burocratica**: tratamos a Big the Cat (que pesca a Froggy) como si fuera un funcionario real con "FOJA DE SERVICIOS."

Eso preserva el tono del canal sin ofender la fecha real.

**Riesgo:** que la audiencia chilena tradicional lo lea como burla a la fecha. Mitigacion: en el cold open Luis aclara que es "homenaje a los nuestros, los retro" y NO compara con personajes historicos reales.

---

## 3. Criterios de seleccion del top 10

Filtros aplicados:
1. **Personaje tiene rol naval visible** (capitan, marinero, buzo, pirata, pescador, piloto naval, rescatista oceanico).
2. **Cubre era retro** (NES a Dreamcast, no posterior).
3. **Reconocible.** No incluir cosas oscuras que requieran demasiado contexto.
4. **Humor inherente.** Si el personaje no permite chiste, queda fuera.

Descartados (con razon):
- **Captain N: The Game Master** — anime mas que juego, no tiene gameplay propio.
- **Submarine (1982)** — muy antiguo, sin personajes con nombre.
- **Sub-zero (Mortal Kombat)** — el "sub" no es naval, es de temperatura. Trampa lexica.
- **Sonic en Sonic Adventure** — corre por la playa, NO es naval. Big the Cat si entra (pesca).
- **Captain Falcon (F-Zero)** — pilota carro de carrera, NO es naval.

---

## 4. Por que Kaptain K. Rool al #1

Discusion mas dura. Los candidatos serios para #1 fueron:

| Candidato | Argumentos pro | Argumentos contra |
|-----------|----------------|---------------------|
| **Kaptain K. Rool** | CEO + capitan, Kremlings S.A., 4 juegos consecutivos, comercio pirata, minas, explotacion laboral kremling | Es villano (algunos prefieren heroes al #1) |
| **Pirates! Captain** | Sandbox completo de vida pirata, multioficio, eleccion del jugador | Generico, sin nombre fijo |
| **Guybrush Threepwood** | Persistencia legendaria, postulante eterno, esgrima de insultos | "Postulante" suena debil para #1 |

Eleccion: **Kaptain K. Rool** porque maximiza el chiste burocratico. "CEO + capitan + 4 juegos" es la mayor cantidad de "responsabilidades simultaneas" del top entero. Encaja perfecto con el tono "RRHH naval imaginario."

---

## 5. Por que NO se incluyen estos otros candidatos

- **Link en Wind Waker** (GameCube 2002): cumple definicion de marinero, pero el episodio cubre RETRO y Wind Waker es post-N64. Si extendieramos a era 6, podria ir.
- **Dolphin del juego Iggy's Reckin' Balls**: muy oscuro, no aporta humor.
- **Sub-Marine de los juegos Atari**: vehiculo, no personaje.
- **El barco de Final Fantasy I**: no es personaje.

---

## 6. Estructura narrativa por bloques

El episodio NO se siente como un ranking serio (porque NO lo es). Es mas bien una **sucesion de skits cortos** ligados por la fecha 21 de Mayo. Por eso:

- Los items van mas rapido (~1:30 cada uno) que un top mundial.
- El top 3 puede estirarse a 2:30 si hay anecdota visual buena.
- El #1 K. Rool debe tener "redoble de tambores" + reaccion visual fuerte.

---

## 7. Decision sobre TarroBot

**Recomendacion editorial: USAR TARROBOT** para leer las HOJAS DE SERVICIOS.

Razones:
1. **Tono burocratico-fingido funciona mejor con voz sintetica.** Es lo que el chiste pide.
2. **Luis NO tiene que contener la risa** mientras lee. Reacciona normal.
3. **Catalina (es-CL-CatalinaNeural)** tiene tono perfecto: chilena, formal, un poco robotica.
4. **Replica del SII naval imaginario** mejorado: voz oficial real, no parodia humana.

La pauta JSON (`studio/pautas/retro-glorias-navales.tarrobot.json`) tiene los 10 textos pre-cargados. Si se decide NO usar TarroBot, Luis lee directo del slide HTML (la hoja esta visible).

---

## 8. Cita del cold open · texto cerrado

Texto definitivo del cold open (Luis con tono solemne fingido, NO sobreactuado):

> *"En este 21 de Mayo, mientras Chile recuerda a Prat y a la Esmeralda, en Retrotarros tambien queremos homenajear a los nuestros. A los que tambien se la jugaron en el mar. A los que tambien soportaron tormenta y enemigo. A los que tambien... tuvieron contratos de mierda. Top 10 Glorias Navales Retro."*

**Notas:**
- "Contratos de mierda" es el quiebre tonal. Debe sonar inesperado.
- NO decir "los heroes anonimos" (cliche).
- La palabra "Prat" se menciona UNA SOLA VEZ y como punto de contraste, no comparacion.

---

## 9. Reglas inmutables aplicadas

- **TarroVisiones VACIAS** en HTMLs (regla canal). Las hojas de servicio aparecen FUERA de la TV (en `.game-why`).
- **Sin tildes** en HTML visible.
- **Sin emojis** en titulos / labels.
- **Chileno neutro con tuteo** en pauta + discusion.

---

## 10. Material a grabar (checklist resumido)

- [ ] Clips gameplay de los 10 personajes en accion (8-12s c/u).
- [ ] Imagenes/sprites de cada personaje destacado.
- [ ] Decision: ¿imagen del Combate Naval de Iquique al inicio? Eleccion editorial pendiente.
- [ ] Musica fondo naval (sugerencias en pauta MD).
- [ ] (Opcional) MP3s pre-generados de TarroBot leyendo las 10 hojas.

---

## 11. Para el futuro · plantilla de "Especial de fecha"

Si este especial funciona, el formato canonico de "Especial de fecha" del canal es:

1. **Portada con tag de fecha** (ej. "ESPECIAL · 21 DE MAYO").
2. **Cold open con disclaimer de tono** (no academico, no solemne).
3. **Top 10 personajes tematicos** del catalogo retro (no juegos).
4. **Cada slide tiene HOJA DE SERVICIOS o equivalente burocratico** segun la fecha.
5. **Tarrobot opcional** para narrar con voz formal.
6. **Cierre con CTA + invitacion al proximo especial.**

Fechas candidatas para 2026-2027:
- **18 de Septiembre** (Independencia) — "Top 10 Heroes Patrios Retro."
- **1 de Mayo** (Trabajador) — "Top 10 Empleos Mas Crueles del Retro."
- **31 de Octubre** (Halloween) — "Top 10 Jefes Finales Aterradores."
- **24 de Diciembre** (Navidad) — "Top 10 Personajes Retro que Necesitan Vacaciones."

---

*Discusion cerrada · 2026-05-24 · Luis Balbrigame*
