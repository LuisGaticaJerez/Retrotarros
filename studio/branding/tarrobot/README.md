# Kit de branding · TarroBot

Set visual de la mascota TarroBot (la TV synthwave) para redes sociales.
Todo generado desde el SVG vectorial canonico, en la paleta del canal
(cyan #00E5FF, magenta #FF2E88, amarillo #FFD23F, fondo #06030f).

## Contenido

| Archivo | Tamano | Uso |
|---|---|---|
| `avatar-800.png` | 800x800 | Foto de perfil (TikTok, IG, YouTube, X). Anillo synthwave + pill, listo para recorte circular. |
| `logo-horizontal-dark.png` / `-transparent.png` | 1200x520 | Logo mascota + wordmark en fila. Fondo oscuro o transparente. |
| `logo-stacked-dark.png` / `-transparent.png` | 760x840 | Logo apilado (mascota arriba, texto abajo). |
| `banner-youtube-2560x1440.png` | 2560x1440 | Banner de canal YouTube (zona segura central respetada). |
| `banner-x-1500x500.png` | 1500x500 | Header de X / Twitter. |
| `post-1080.png` | 1080x1080 | Plantilla post cuadrado (IG/FB). |
| `story-1080x1920.png` | 1080x1920 | Cover de story / portada de short. |
| `expresiones/*.png` | 512x512 | Sticker pack transparente: neutral, feliz, wow, pensando, guino, sospecha. |
| `endcards/endcard-2videos.png` | 1920x1080 | Pantalla final YouTube: 2 slots de video + suscripcion. Zonas vacias para montar los elementos clicables encima. |
| `endcards/endcard-1video.png` | 1920x1080 | Pantalla final con 1 video grande + suscripcion. |
| `mascota.svg` | vectorial | Fuente escalable de la mascota (para editar o exportar a cualquier tamano). |
| `contact-sheet.png` | — | Hoja de contacto con todo el kit de un vistazo. |

## Regenerar

```bash
python scripts/branding_tarrobot.py          # genera todo el kit
python scripts/branding_tarrobot.py --sheet  # solo la hoja de contacto
```

Las expresiones se definen en `FACES` dentro de `scripts/branding_tarrobot.py`.
Para agregar una nueva expresion, suma una entrada ahi (ojos + boca dentro de
la pantalla, viewBox 0 0 64 64) y vuelve a correr el script.

## Nota de uso

- Los PNG con fondo (`-dark`, banners, post, story, avatar) van directo a subir.
- Los `-transparent` y las expresiones sirven para montar encima de gameplay,
  miniaturas o composiciones en CapCut / editores.
- El wordmark es siempre **TARROBOT** (sin tildes, regla de assets del canal).
