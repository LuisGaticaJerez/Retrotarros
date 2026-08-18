# RETROTARROS — Pauta de RetroNota

*Nostalgia + Juegos + Música*

**Las Localizaciones Perdidas — Por que estos juegos gigantes en Japon nunca llegaron a Sudamerica**

*RetroNota · Reportaje tematico · 15-20 min*

Documento de trabajo · Luis Balbrigame & Koko

---

## Proposito de esta pauta

Primer episodio del formato nuevo **RetroNota** (ver diseño en
`docs/superpowers/specs/2026-08-17-retronota-format-design.md`). Reportaje sobre juegos
japoneses de los 90 que nunca tuvieron traduccion/localizacion oficial a NINGUN idioma
occidental durante decadas -y que por lo tanto nunca llegaron a Sudamerica, sin importar
el canal de distribucion. Angulo elegido a proposito por ser el mas verificable: en vez
de reconstruir que vendian las tiendas chilenas en 1994 (dificil de documentar), se
enfoca en la barrera de idioma, que aplica igual a toda audiencia no japonesa-parlante.

**Tono editorial:** investigativo-conversacional, Luis y Coco revisando el tema juntos.
NO cierra con bateria.

---

## Los 4 casos (verificados, con fuentes)

| Juego | Consola/Año | Nunca salio de Japon hasta | Razon documentada |
|---|---|---|---|
| Seiken Densetsu 3 | SNES, 1995 | Remake Trials of Mana, 2020 (25 años) | Costo de traduccion, bugs de certificacion, ventas flojas de Secret of Mana, timing con la llegada de PS1/Saturn |
| Live A Live | SNES, 1994 | Remake HD-2D, 2022 (28 años) | Ventas locales no prometedoras, "se perdio en las grietas" segun staff de Square |
| Bahamut Lagoon | SNES, 1996 | NUNCA oficialmente (solo fan translations, 2002 y 2021) | Nunca licenciado fuera de Japon, sin explicacion oficial publicada |
| Fire Emblem (saga completa) | Famicom/SNES/GBA, 1990-2002 | Fire Emblem GBA, 2003 (13 años, 6 juegos) | Nintendo no confiaba en el publico occidental; cambio de opinion tras Marth/Roy en Smash Melee (2001) + exito de Advance Wars |

Fuentes cruzadas: Nintendo Life, Time Extension, Square Enix (declaraciones de staff),
Vice, Inverse, ResetEra, The Gamer, Game Informer.

---

## Estructura (5 capitulos, HTML `studio/retronotas/retronota-lost-localizations.html`)

1. **Gancho** — Marth y Roy en Smash Bros. Melee (2001): jugamos con ellos sin conocer
   su juego de origen.
2. **Origen/contexto** — por que la traduccion de RPGs era tan cara, y por que
   Sudamerica quedaba doblemente atras (ni operacion oficial fuerte hasta los 90s, ni
   el juego existia en idioma comprensible).
3. **Desarrollo** — los 4 casos, uno por slide, con box art real + fuente citada en
   pantalla.
4. **Impacto/legado** — el rol de los fan translators (Aeon Genesis, DeJap) como unica
   via de acceso por decadas, y el reconocimiento tardio via remakes oficiales.
5. **Cierre** — reflexion + pregunta a la audiencia + CTA.

14 slides totales (portada + 13 de contenido/capitulo + cierre).

---

## Notas de grabacion

- Ritmo sugerido: ~1:15-1:30 por slide de contenido para llegar a 15-20 min con 14 slides.
- El capitulo 3 (los 4 casos) es el cuerpo central — no acortar.
- Badge verde "HECHO VERIFICADO" en pantalla en todos los slides de dato -- no hay
  contenido de folclore/mito en este episodio, asi que no aplica el badge rojo.
- Fuente citada en pantalla en los 4 casos (regla del formato: mostrar de donde sale
  el dato cuando el reportaje hace una afirmacion factual fuerte).

---

## Estado de la pauta

| Item | Estado |
|------|--------|
| Generador (`scripts/retronota_deck.py`) | ✓ Nuevo, primer uso |
| HTML estudio (`studio/retronotas/retronota-lost-localizations.html`) | ✓ Cerrado (14 slides) |
| Capturas | ✓ 14 PNGs |
| Imagenes | ✓ 4 box arts verificados |
| Pauta MD | ✓ |
| Discusion MD | ✓ |
| Descripcion YouTube | ✓ |

---

**Ultima actualizacion:** 2026-08-17
**Slug:** `retronota-lost-localizations`
**HTML asociado:** `studio/retronotas/retronota-lost-localizations.html`
**Discusion:** `docs/discusiones/discusion-retronota-lost-localizations.md`
