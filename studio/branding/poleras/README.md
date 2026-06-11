# Kit de poleras · Retrotarros

Artes print-ready para estampado DTF/DTG full color (PNG transparente, 300 DPI).
Generados con `python scripts/merch_poleras.py`.

## Estructura

- `print/` — los 20 artes listos para imprimir (10 diseños × `-dark`/`-light`).
- `poleras-contact-sheet.png` — catálogo: los 20 mockups sobre tela negra y blanca.

`-dark` = arte para **polera oscura** (blancos + neón + glow).
`-light` = arte para **polera clara** (tinta oscura, sin glow).

## REGLA DE COLOR (obligatoria) — Luis

> El **cyan** (#00E5FF) SOLO puede aparecer cuando el diseño incluye la
> **mascota TarroBot** (o su cara, ej. en la pantalla del Game Boy) **o** la
> **palabra "TARROBOT"**. Es el color que acompaña a TarroBot, no decora.
>
> Si el diseño NO trae mascota ni la palabra TARROBOT, se usa la paleta base
> del canal **sin cyan**: negro/morado de fondo, **magenta** y **amarillo** de
> acento. El wordmark en esos casos va **RETRO (blanco) + TARROS (magenta)**.

Base general: fondo negro/morado dominante, morado (`#7C2FF0`) para grids,
líneas de perspectiva y cuerpos de dispositivo. Magenta y amarillo de acento.
Halo morado radial detrás de TarroBot (igual a los assets de redes).

En el generador esto es el flag de clase `.nc` (no-cyan) sobre el wordmark/tag.

## Diseños

| Diseño | Lleva TarroBot | Cyan |
|---|:---:|:---:|
| pecho-mascota | mascota | sí |
| pecho-wordmark | — | no |
| pecho-gameboy | cara en pantalla | sí |
| espalda-stacked | mascota + palabra TARROBOT | sí |
| espalda-synthwave | mascota | sí |
| espalda-crt | — | no |
| espalda-arcade | mascota (guiño) | sí |
| espalda-gameboy | cara en pantalla | sí |
| espalda-wordmark-synthwave | — | no |
| espalda-tarrovision | — | no |

## Para cotizar (imprenta)

DTF full color · pecho ~9 cm ancho · espalda ~30 cm ancho · PNG 300 DPI fondo
transparente (ya vienen en ese formato exacto en `print/`).

## Regenerar / editar

```bash
python scripts/merch_poleras.py
```

Tamaños, frases, expresión de TarroBot y colores se editan en
`scripts/merch_poleras.py`. Las expresiones disponibles de la mascota están en
`FACES` de `scripts/branding_tarrobot.py` (neutral, feliz, guino, pensando,
sospecha; **wow descartada para merch** por decisión de Luis).
