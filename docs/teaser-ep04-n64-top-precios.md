# Teaser EP 04 · Los N64 mas caros

> Short vertical 9:16 · 30s · YouTube Shorts / Reels / TikTok
>
> Asset HTML: `studio/teaser-n64-top-precios.html`
> Capturas: `studio/captures/teaser-n64-top-precios/` (6 PNGs 1080x1920) + mirror en Drive.

## Concepto

Spoiler editorial puro: el cartucho N64 mas caro NO es Mario ni Zelda. Es uno que casi nadie jugo. Tres bombas de precio + CTA al ranking completo del EP 04.

Ritmo: 3 segundos hook, 3 bombas de 6-7 segundos cada una, CTA final. Total 30s.

## Estructura · 6 cortes

| # | Slide PNG | Duracion | Voz en off (VO) | B-roll sugerido |
|---|-----------|----------|-----------------|-----------------|
| 01 | `slide-01.png` | 0.0 - 4.0s | "El N64 mas caro... no es Mario. No es Zelda." | Cartuchos clasicos pasando rapido + tachados con magenta |
| 02 | `slide-02.png` | 4.0 - 11.0s | "Es ClayFighter 63 y un tercio. Cuatro mil ochocientos dolares la copia completa. Y solo se vendio en Blockbuster." | Foto del cartucho ClayFighter Sculptor's Cut + cinta de video VHS de Blockbuster (logo amarillo/azul) |
| 03 | `slide-03.png` | 11.0 - 17.0s | "Pero espera. La version sellada cerro en nueve mil ciento noventa y nueve dolares. Record mundial del Nintendo 64." | Imagen del sealed + emoji boom o efecto de impacto sonoro |
| 04 | `slide-04.png` | 17.0 - 23.0s | "Y el resto del top cinco? Nombres que ni tu te acuerdas. Stunt Racer. Super Bowling. F1 que solo llego a Brasil." | Lista subiendo en pantalla, sin B-roll detras (deja respirar) |
| 05 | `slide-05.png` | 23.0 - 28.0s | "El kicker: un cartucho gris de Majora que jamas se vendio. Ocho mil quinientos dolares." | Imagen Majora gris NFR o silueta cartucho gris con scanlines |
| 06 | `slide-06.png` | 28.0 - 30.0s | "EP cuatro. Ya disponible. Link abajo." | Logo Retrotarros + flecha apuntando a descripcion |

**Duracion total VO:** 28-30 segundos. Si queda apretado, sacar slide 04 (top 5) y meterlo solo como cartela de 2s sin VO.

## Pauta TarroBot · si se hace con voz TTS

Cargar como pauta JSON en el panel del estudio para que TarroBot dicte cada linea:

```json
{
  "slug": "teaser-n64-top-precios",
  "titulo": "Teaser EP04 N64 mas caros",
  "secciones": [
    { "id": 1, "texto": "El N64 más caro no es Mario. No es Zelda." },
    { "id": 2, "texto": "Es ClayFighter 63 y un tercio. Cuatro mil ochocientos dólares la copia completa. Y solo se vendió en Blockbuster." },
    { "id": 3, "texto": "Pero espera. La versión sellada cerró en nueve mil ciento noventa y nueve dólares. Récord mundial del Nintendo 64." },
    { "id": 4, "texto": "El resto del top cinco. Nombres que ni tú te acuerdas. Stunt Racer. Super Bowling. F1 que solo llegó a Brasil." },
    { "id": 5, "texto": "El kicker. Un cartucho gris de Majora's Mask que jamás se vendió en una tienda. Ocho mil quinientos dólares." },
    { "id": 6, "texto": "Episodio cuatro. Ya disponible. Link abajo." }
  ]
}
```

**Nota:** los textos para TTS SI llevan tildes (regla canal). Los PNG en pantalla NO. El locutor humano usa el guion de arriba (sin tildes en pantalla pero pronunciado normal).

## Workflow CapCut / DaVinci

1. Importa las 6 PNGs como capas de imagen full-frame 1080x1920.
2. Pista de audio musica de fondo: usar loop synthwave bajo (-12 dB respecto a la voz). Sugerencia: misma libreria que el cap principal.
3. Pista de VO encima. Duck musica -6dB cuando habla.
4. Transicion entre slides: cut duro + flash blanco de 2 frames. No fade.
5. Slide 01 -> 02: zoom rapido al precio.
6. Slide 03: el `$9,199` puede animarse con scale 0.5 -> 1.0 en 4 frames + shake horizontal.
7. Slide 05: el `$8,500` con glow magenta pulsante.
8. Slide 06: subtitulo "YA DISPONIBLE" parpadeando (CSS ya lo hace, pero en video reforzar con keyframes opacidad).
9. Footer fijo "RETROTARROS · NOSTALGIA · JUEGOS · MUSICA" se mantiene en todos los slides.

## Variantes para A/B test

- **Variante A (hook precio):** arrancar directo en slide 02 con `$4,800` enorme y la pregunta "POR ESTE CARTUCHO?".
- **Variante B (hook negacion):** la actual (no es Mario, no es Zelda).
- **Variante C (hook record):** arrancar en slide 03 con `$9,199 RECORD MUNDIAL` y despues backtrack.

Probar A vs B en Shorts/Reels durante 48h y quedarse con la que mejor retencion en los primeros 3 segundos.

## Distribucion

- **YouTube Shorts:** vertical, descripcion link al EP 04 largo.
- **TikTok:** mismo asset, hashtags `#nintendo64 #retrogaming #coleccionismo #retrotarros`.
- **Instagram Reels:** mismo asset, llamada en stories al link en bio.
- **Twitter/X:** GIF de 6s (slides 01 + 02 + 06 encadenados) + link al short de YouTube.

## Copy descripcion del Short

```
El N64 mas caro del mundo NO es Mario ni Zelda.

Es un cartucho que solo se vendio en Blockbuster.

Episodio 4 ya disponible: [link]

#nintendo64 #retrogaming #coleccionismo #retrotarros
```

---

*Pauta del teaser · generada para EP 04 · arco N64*
