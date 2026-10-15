# Pauta — GameCube Top Precios

> Episodio: Los discos de GameCube que hoy valen una fortuna (retail CIB + rarezas + santo grial)
> HTML: `studio/rankings/top-precios/gamecube-top-precios.html`
> Formato: ranking hibrido por precio CIB · 19 slides
> Reforge 2026-10-15: top 10 rehecho con el listado completo de PriceCharting (ver `docs/discusiones/discusion-gamecube-top-precios.md`)
> Arco GameCube junto a `gamecube-top-mundial` (ver `docs/arcos/gamecube.md`)

## Gancho / Cold open

En GameCube lo caro tampoco es lo famoso: un juego de basquetbol con personajes de Disney, Disney Sports Basketball, cuesta mas de mil dolares completo. Mas que Metroid Prime y que Resident Evil 4. Del piso del retail a un santo grial que solo se vendia en una tienda de Nueva York.

## Metodologia

Precios CIB (Complete In Box, NTSC USA) leidos directo del listado de PriceCharting el 2026-10-15, con las columnas exactas (suelto, CIB, sellado) y fichas individuales para los juegos nuevos. Sin fuentes secundarias. Grial confirmado como el item mas caro del episodio; rarezas confirmadas como genuinamente no-retail.

## Retail CIB (#10 → #1)

| # | Juego | CIB | Por que |
|---|---|---|---|
| 10 | Fire Emblem: Path of Radiance | USD 220 | Unico Fire Emblem de GameCube, introdujo a Ike. Empata con Samurai Jack: Shadow of Aku (USD 220) |
| 9 | Disney Sports Football | USD 221 | Licencia Disney de Konami que nadie guardo |
| 8 | Zatch Bell! Mamodo Fury | USD 250 | Pelea basada en el anime, Bandai |
| 7 | Phantasy Star Online Episode I & II Plus | USD 250 | RPG online de Sega, quedo el disco |
| 6 | NCAA College Basketball 2K3 | USD 251 | Deportivo anual, pocos completos |
| 5 | Resident Evil Code: Veronica X | USD 300 | Dos discos, completo con caja y manual |
| 4 | Go! Go! Hypergrind | USD 513 | Atlus, tirada corta de nicho |
| 3 | Gotcha Force | USD 516 | Capcom, marketing casi nulo |
| 2 | Cubivore: Survival of the Fittest | USD 665 | Atlus, tirada minima |
| 1 | Disney Sports Basketball | USD 1.025 | Licencia Disney de Konami, el retail NTSC USA mas caro de la consola |

## Rarezas / No-Retail (de menos a mas caro)

- **The Legend of Zelda: Collector's Edition** (~USD 80): disco promocional con 4 Zelda clasicos, la caja dice PROMOTIONAL DISC · NOT FOR RESALE. Se conseguia via Nintendo Power o registrando el GameCube y dos juegos.
- **Interactive Multi-Game Demo Disc Version 16** (~USD 488): disco de kiosko de tiendas, nunca se vendio al publico. Traia el parche del Zigzagoon shiny para Pokemon Ruby y Zafiro.
- **Animal Crossing [Not For Resale]** (~USD 1.045, suelto USD 758): copia promocional, nunca destinada a la venta. Cuidado: en el slide va la portada normal, la NFR lleva el sello.

## Santo Grial

- **Pokemon Box [Big Box]** (~USD 4.443, pocas ventas registradas): Pokemon Box: Ruby & Sapphire en caja grande. Segun PriceCharting, en Norteamerica solo se vendia en el Pokemon Center de Nueva York; en Europa venia en el paquete Pokemon Colosseum Mega Pak. La version de caja normal ronda USD 2.500 completa. Es mas de cuatro veces el #1 del retail y mas que cualquier rareza.

## Puntos polemicos (para comentarios)

- Un juego de basquetbol con personajes de Disney es el retail mas caro de GameCube, por encima de Cubivore y Gotcha Force.
- Los deportivos y juegos de licencia dominan el piso del top: Disney Sports Football, NCAA 2K3 y Disney Sports Basketball valen poco sueltos y mucho completos porque nadie los guardaba.
- Metroid Prime y Resident Evil 4 estandar (del Top Mundial) no aparecen aca.

## Veredicto (slide 18)

En GameCube lo caro no es lo famoso: tirada corta, licencia que nadie guardo y venta en una sola tienda mandan sobre la fama.

## Cierre / CTA (slide 19)

¿Sabian que el retail mas caro de GameCube es un juego de basquetbol de Disney? ¿Tienen algun disco de esta lista guardado? Comenten. Suscribete a Retrotarros.

## Notas de produccion

- Box arts: 13 de 14 ítems con caja real (libretro / Wikipedia). Excepcion: PSO Plus usa por ahora la portada PAL (se ve el sello PAL y ELSPA en la imagen); conviene reemplazarla por la NTSC USA si aparece. Las rarezas Animal Crossing NFR y Pokemon Box usan la portada de la edicion normal como referencia (se aclara en las notas). Demo Disc Version 16 va con `cart-fallback` (sin caja retail).
- Anos sin verificar con segunda fuente: Disney Sports Football (2002) y Zatch Bell! Mamodo Fury (2005). Confirmar antes de decirlos en camara.
- Notas teleprompter: tecla N o boton (no-capture).
- Capturas regeneradas el 2026-10-15 (`python scripts/capture-slides.py gamecube-top-precios`).
