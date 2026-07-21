# RETROTARROS — Pauta de episodio especial

*Nostalgia + Juegos + Música*

**Especial Dia del Padre — El Club de Padres Gamer**

*Evaluamos a los papas del videojuego con nota chilena del 1 al 7*

Documento de trabajo · Luis Balbrigame & Koko

---

## Proposito de esta pauta

Tercer especial conmemorativo del canal (despues de glorias navales y la cuadrilla del frio). Para el **Dia del Padre** (3er domingo de junio, este año el 21) tomamos **10 papas iconicos del videojuego** y los pasamos por una **evaluacion de paternidad con nota chilena del 1,0 al 7,0**. Luis hace de profesor jefe, Koko reacciona.

Tono **humoristico** con **cierre sincero**: arranca como chiste (papas terribles y padrazos) y termina con un mensaje genuino del Dia del Padre + Koko tocando.

> Mismo device de personajes con ficha (glorias navales / cuadrilla del frio). La **nota va GRANDE en la esquina superior derecha** (reusa el slot del precio de los top).

---

## Concepto del episodio

HTML (`studio/specials/retro-padres-gamer.html`): 14 slides. Portada → intro (reunion de apoderados) → 10 fichas (papa + evaluacion + nota grande) → promedio del curso → cierre sincero con Koko.

**Duracion objetivo:** 12-16 minutos. **Orden: de peor a mejor papa** (cierra en el padrazo).

---

## El curso (10 papas, de peor a mejor)

| Nota | Papa | Juego | Evaluacion (resumen) |
|------|------|-------|----------------------|
| 1,0 | Heihachi Mishima | Tekken | Tiro a su hijo (y nieto) por un acantilado |
| 2,0 | Dr. Wily | Mega Man | Fabrica hijos robot para conquistar el mundo |
| 3,0 | Big Boss | Metal Gear | Clono a sus hijos; origen de todos los daddy issues |
| 4,0 | Papa de Ness | EarthBound | Ausente pero proveedor: llama, deposita plata y guarda partida |
| 4,5 | Cranky Kong | Donkey Kong | El abuelo del "en mis tiempos era mas dificil" |
| 5,0 | Norman | Pokemon | Tu papa que ademas te hace pelear en su gimnasio |
| 5,5 | Bowser | Super Mario | Sorprendente papa soltero dedicado de Bowser Jr. |
| 6,0 | James McCloud | Star Fox | Te guia desde el mas alla en pleno combate |
| 6,5 | Dr. Light | Mega Man | El buen papa nerd, creo a Mega Man con amor |
| 7,0 | Harry Mason | Silent Hill | Cruza el infierno por su hija. Padre del año |

---

## Estructura (12-16 min)

- **Cold open (0:00-0:30):** Luis con lista de notas: "Es Dia del Padre, asi que hoy evaluamos a los papas del videojuego. Con nota, del uno al siete. Y hay varios que repiten el año."
- **Setup (0:30-1:00):** explica el device (reunion de apoderados, nota chilena).
- **Las 10 fichas (1:00-13:00):** ~1:10 por papa, de peor a mejor. Luis lee la evaluacion seria, Koko reacciona. Gameplay del papa en la TarroVision.
- **Promedio del curso (13:00-14:00):** balance, "de todo hay en gaming, igual que en la vida".
- **Cierre sincero + Koko (14:00-16:00):** se rompe el chiste: mensaje real de Dia del Padre ("para todos los que nos pasaron el control por primera vez"). Koko toca un tema dedicado. CTA: "etiqueta a tu viejo gamer".

---

## Reglas de ejecucion

- Cada ficha max 1:30. Humor seco, leer la evaluacion como informe escolar.
- Mantener la nota como gancho visual (va grande arriba a la derecha).
- El cierre SI es sincero: bajar el humor, subir el corazon. Es lo que da el toque de fecha.

### Lo que SI se dice
- Lenguaje escolar: "evaluacion", "reincidente", "no asistio a reuniones", "promedio".

### Lo que NO se dice
- No mancillar de verdad a ningun papa (es cariñoso, no cruel).
- No spoilear la nota antes de leer la ficha.

---

## Material visual

- [ ] 10 clips de gameplay (uno por papa, mostrando su "metodo paternal").
- [ ] Arte/sprite de cada papa para el cart (sino, etiqueta de color).
- [ ] Tema musical para el cierre de Koko (dedicado a los papas).

El HTML usa placeholders `tv-noscreen` + `cart-fallback`. La nota va en la clase `.game-price` (esquina superior derecha).

---

## Estado

| Item | Estado |
|------|--------|
| HTML (`studio/specials/retro-padres-gamer.html`) | ✓ 14 slides |
| JSON TarroBot | ✓ 10 fichas |
| Pauta MD (este) | ✓ |
| Discusion MD | ✓ |
| Gameplay + tema cierre | ☐ Pendiente |

---

**Ultima actualizacion:** 2026-06-07
**Slug:** `retro-padres-gamer`
**HTML:** `studio/specials/retro-padres-gamer.html`
**Discusion:** `docs/discusion-retro-padres-gamer.md`
