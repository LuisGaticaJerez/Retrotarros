# Kit de poleras · Retrotarros

Artes print-ready para estampado DTF/DTG full color (PNG transparente, 300 DPI).
Generados con `python scripts/merch_poleras.py`.

## Estructura

- `print/` — los 20 artes listos para imprimir (10 diseños × `-dark`/`-light`).
- `poleras-contact-sheet.png` — catálogo: los 20 mockups sobre tela negra y blanca.

`-dark` = arte para **polera oscura** (blancos + neón + glow).
`-light` = arte para **polera clara** (tinta oscura, sin glow).
`-flat` = mismo look que `-dark` (blanco + cyan + amarillo) pero **plano**: sin
glow neón, sin halo de fondo y sin sombras. Solo conserva el contorno oscuro de
las letras (para que no se pierdan). Pensado para polera oscura con estampado
liso. Se generan con `python scripts/merch_poleras.py --flat` (o
`--flat <filtro>` para uno solo, ej. `--flat banner`).

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

### Letras de los diseños SIN TarroBot, según la tela (que no se camuflen)

- **Polera BLANCA (`-light`):** letras **negras + moradas**. (Nada de amarillo
  ni blanco: se camuflan con el fondo claro.) → RETRO negro + TARROS morado.
- **Polera NEGRA (`-dark`):** letras **naranjas**. (Nada de negro plano: se
  camufla con el fondo.) → RETRO naranja claro + TARROS naranja fuerte.

Principio general de no-camuflaje: en tela clara evitar amarillo/blanco para
texto y líneas finas; en tela oscura evitar negro/morado muy oscuro. Los textos
DENTRO de un dispositivo (EN VIVO, TARROVISION) tienen fondo oscuro propio, así
que van en amarillo y se ven bien en ambas telas.

### Contorno "chrome" synthwave (obligatorio en todo wordmark/tagline)

Todo wordmark y tagline lleva un **contorno oscuro** (text-shadow multidir,
`#150026`) — el clásico texto delineado synthwave. Despega la palabra de
CUALQUIER fondo (el sol, la tela clara, los dispositivos) para que **nunca se
pierda con el fondo**. En tela negra se suma el glow neón. Regla de diseño:
ningún título debe camuflarse con lo que tiene detrás; si igual cae sobre una
imagen saturada (sol), va en zona limpia o sobre placa/cápsula.

En el generador esto es el flag de clase `.nc` (no-cyan) sobre el wordmark/tag;
los colores se resuelven solos según `-dark`/`-light`.

### Cyan de texto según el fondo (que no se lave)

El cyan brillante (`#00E5FF`) se lava sobre blanco. Por eso:
- **Texto cyan sobre la TELA** (TARROS, taglines): brillante en negra, **teal más
  oscuro** (`#0782A0`) en blanca. El **cuerpo de TarroBot** sigue cyan brillante
  (es una forma con detalles magenta/amarillo, se reconoce).
- **Texto sobre una CÁPSULA/pill** (badge, pecho-pill): clase `.od` → siempre
  blanco + cyan brillante, porque el pill es oscuro aunque la polera sea blanca
  (si no, el RETRO negro desaparecía sobre el pill).

## Diseños

| Diseño | Inspiración | Lleva TarroBot | Cyan |
|---|---|:---:|:---:|
| pecho-mascota | logo | mascota | sí |
| pecho-wordmark | wordmark | — | no |
| pecho-gameboy | Game Boy | cara en pantalla | sí |
| pecho-pill | avatar (cápsula) | palabra TARROBOT | sí |
| espalda-badge | **avatar** (emblema + anillos) | mascota + palabra | sí |
| espalda-banner | **banner YouTube/X** (horizontal) | mascota | sí |
| espalda-stacked | logo apilado | mascota + palabra | sí |
| espalda-synthwave | synthwave + mascota | mascota | sí |
| espalda-crt | TV retro | — | no |
| espalda-arcade | HUD arcade (guiño) | mascota | sí |
| espalda-gameboy | Game Boy synthwave | cara en pantalla | sí |
| espalda-wordmark-synthwave | sol + grid | — | no |
| espalda-tarrovision | TarroVisión de los decks | — | no |

**13 diseños × 2 telas = 26 artes.** Las inspiraciones salen del kit de
`studio/branding/tarrobot/` (avatar, banners, logos, expresiones).

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
