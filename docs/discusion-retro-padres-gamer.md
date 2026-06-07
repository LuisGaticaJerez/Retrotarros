# Discusion · Especial Dia del Padre (El Club de Padres Gamer)

Documento de trabajo: el "detras de escena". NO es la pauta.

---

## Por que este especial

Es junio: Dia del Padre en Chile (3er domingo, el 21). Ya validamos el formato de personajes con ficha (glorias navales, cuadrilla del frio). Aca el device es una **evaluacion escolar con nota chilena del 1 al 7** — local, gracioso e inmediato de entender para la audiencia chilena/latam.

Idea: los "videogame dads" son un tema muy querido y memeable. El gancho es el contraste (Heihachi tira a su hijo por un acantilado vs Harry Mason cruza el infierno por su hija).

---

## El device: la nota chilena

- Cada papa recibe una **nota del 1,0 al 7,0** (sistema escolar chileno) que va GRANDE en la esquina superior derecha (reusamos el slot del precio de los top, ya quedo en `top_deck.py`).
- Luis = profesor jefe leyendo el informe de cada papa con seriedad.
- Koko = el apoderado que reacciona.
- Orden de peor a mejor para cerrar en el padrazo (Harry Mason 7,0) justo antes del mensaje sincero.

---

## Por que estos 10 (criterio)

Mezcla de buenos / ausentes / terribles, retro-icono y memeable:

- **Terribles (humor):** Heihachi (el clasico "peor papa"), Dr. Wily, Big Boss.
- **Ausentes con asterisco:** el papa de Ness (proveedor por telefono, meme querido), Norman (el unico papa real de Pokemon, ironia del "papa rival").
- **Padrazos:** Harry Mason (el techo emocional), Dr. Light, James McCloud, Bowser (el giro inesperado: el villano es buen papa).
- **Comodin:** Cranky Kong (mas abuelo que papa, rompe la cuarta pared).

---

## Banca (por si se cambia uno)

- **Kratos** (God of War "BOY") — el papa moderno por excelencia, pero es muy actual para un canal retro. Mencionable de pasada.
- **Rey de Hyrule / Daphnes** (Zelda) — papa real pero menos memeable.
- **Professor Oak** (abuelo figura).
- **Ethan Mars** (Heavy Rain, "JASON!") — meme grande pero no tan retro.

---

## El cierre (lo importante de la fecha)

El humor abre, pero el especial CIERRA sincero: mensaje real de Dia del Padre ("para todos los que nos pasaron el control por primera vez") + Koko tocando un tema dedicado. Ese giro de tono es lo que convierte un video de chistes en un video de fecha que la gente comparte con su papa. CTA: "etiqueta a tu viejo gamer".

---

## Decisiones de armado (2026-06-07)

1. Reusa formato de fichas (slide-hybrid) via `top_deck.py` con `badge_text` (rol/evaluacion) + `price` (la nota, grande a la derecha).
2. Foja sin tildes (HTML); textos TTS de TarroBot CON tildes.
3. Orden peor->mejor para el arco emocional.
4. Cierre sincero + musical (sello de especial).

---

## Riesgos

| Riesgo | Mitigacion |
|--------|------------|
| El chiste se vuelve cruel | Tono cariñoso; nadie queda mal de verdad; cierre sincero. |
| La nota chilena no la cacha el publico no-chileno | Se explica en el setup; igual se entiende 1=malo, 7=excelente. |
| Personaje desconocido (el papa de Ness, James McCloud) | La ficha da el contexto; son memes conocidos en el nicho. |

---

**Ultima actualizacion:** 2026-06-07
**Pauta asociada:** `docs/pauta-retro-padres-gamer.md`
**HTML:** `studio/retro-padres-gamer.html`
