# RETROTARROS — Pauta de episodio especial

*Nostalgia + Juegos + Música*

**Especial de Invierno — La Cuadrilla del Frio**

*El sindicato de los personajes helados del retro*

Documento de trabajo · Luis Balbrigame & Koko

---

## Proposito de esta pauta

Segundo especial conmemorativo del canal (despues de `retro-glorias-navales`). Toma **10 personajes helados/del frio** del catalogo retro y los presenta como una **cuadrilla de trabajadores del invierno**, cada uno con su **foja de servicio** y su "puesto" en el gremio. Tono **humoristico-divulgativo**: Luis hace de RRHH del invierno, Koko aporta el factor humano.

Es un especial de **temporada** (invierno chileno, junio-agosto), no de fecha exacta. Mezcla villanos, heroes y mascotas heladas para variedad y humor.

**Cierra con Koko tocando una melodia de nivel de nieve** (pilar Musica).

> Mismo device que glorias navales (foja burocratica fingida). Si funciona, se replica cada temporada/fecha.

---

## Concepto del episodio

HTML del estudio (`studio/specials/retro-cuadrilla-frio.html`): 14 slides. Portada → intro (el gremio) → 10 fichas (personaje + puesto + foja + TarroVision para gameplay) → balance del gremio → cierre con Koko.

**Duracion objetivo:** 12-16 minutos (mas agil que un episodio largo).

**Tono:** humor carinoso, seriedad burocratica fingida. Cada ficha se lee como un legajo de RRHH.

---

## La cuadrilla (10 fichas)

| # | Personaje | Juego | Puesto en el gremio |
|---|-----------|-------|---------------------|
| 1 | Sub-Zero | Mortal Kombat | Jefe de congelacion |
| 2 | Mr. Freeze | Batman | Refrigeracion industrial |
| 3 | Ice Man | Mega Man | Mantenimiento robotico (DLN-005) |
| 4 | Glacius | Killer Instinct | Contratista externo |
| 5 | Articuno | Pokemon | Transporte aereo (turno noche) |
| 6 | Snow Bros (Nick y Tom) | Snow Bros | Operarios de nieve |
| 7 | Ice Climbers (Popo y Nana) | Ice Climber | Cuadrilla de altura |
| 8 | Mr. Frosty | Kirby | Delegado sindical |
| 9 | Lord Fredrik | DKC Tropical Freeze | Gerencia |
| 10 | El Yeti de SkiFree | SkiFree | Seguridad del cerro |

Cada uno trae su **foja de servicio**: antiguedad, especialidad e "incidente laboral" (el chiste).

---

## Estructura (12-16 min)

- **Cold open (0:00-0:30):** Luis con un cafe caliente: "Llego el invierno, asi que abrimos las fichas del gremio mas frio del retro. Diez trabajadores del hielo. Sientense, hace frio afuera."
- **Setup (0:30-1:00):** explica el device (RRHH del invierno, foja por foja).
- **Las 10 fichas (1:00-13:00):** ~1:10 por ficha. Luis lee la foja con seriedad burocratica, Koko reacciona genuino. Gameplay del personaje en la TarroVision.
- **Balance del gremio (13:00-14:00):** planilla cerrada, cero renuncias.
- **Cierre con Koko (14:00-16:00):** Koko toca una melodia de nivel de nieve (Ice Cap Zone, Snowman's Land, etc.). Cierre + pregunta a la audiencia.

---

## Reglas de ejecucion

- Cada ficha max 1:30. El humor seco funciona mejor corto.
- Mantener el personaje de "RRHH serio" — no romper el chiste explicandolo.
- Koko es el contrapunto: reacciona como humano al absurdo burocratico.
- Mezclar el tono villano/heroe: Sub-Zero da miedo, Snow Bros da ternura.

### Lo que SI se dice
- "Antiguedad en el cargo", "incidente laboral", "RRHH le aprobo X" (lenguaje de oficina).

### Lo que NO se dice
- No spoilear el chiste antes de leer la foja.
- No mencionar precios ni rankings (es especial humoristico).

---

## Material visual

- [ ] 10 clips de gameplay (uno por personaje, mostrando su "trabajo": Sub-Zero congelando, Snow Bros tirando bolas, etc.).
- [ ] Idealmente arte/sprite de cada personaje para el cart (sino, etiqueta de color).
- [ ] Melodia de nivel de nieve para el cierre de Koko.

El HTML usa placeholders `tv-noscreen` + `cart-fallback`.

---

## Estado

| Item | Estado |
|------|--------|
| HTML (`studio/specials/retro-cuadrilla-frio.html`) | ✓ 14 slides |
| JSON TarroBot | ✓ 10 fichas |
| Pauta MD (este) | ✓ |
| Discusion MD | ✓ |
| Gameplay + melodia cierre | ☐ Pendiente |

---

**Ultima actualizacion:** 2026-06-07
**Slug:** `retro-cuadrilla-frio`
**HTML:** `studio/specials/retro-cuadrilla-frio.html`
**Discusion:** `docs/discusion-retro-cuadrilla-frio.md`
