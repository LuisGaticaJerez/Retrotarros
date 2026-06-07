# Coleccion Retrotarros (export GameEye)

Inventario REAL de la coleccion del estudio Retrotarros, exportado desde la app
**GameEye**. Es la fuente de verdad para armar pautas (coleccion, top mundial,
top precios) — no inventar listas: consultar aqui primero.

## Archivos

| Archivo | Que es |
|---|---|
| `coleccion-retrotarros.csv` | **Copia estable** (siempre apunta al ultimo export). Usar esta para consultar. |
| `2026_06_05_ge_collection.csv` | Snapshot con fecha de export (historico, no tocar). |

**Ultimo export:** 2026-06-05 · **Total:** 898 juegos.

Para actualizar: exportar de nuevo desde GameEye, copiar el CSV nuevo a esta
carpeta con su fecha, y pisar `coleccion-retrotarros.csv` con el contenido nuevo.

## Desglose por plataforma (2026-06-05)

```
114  SNES/Super Famicom        18  Nintendo DS
 92  Sony PS Vita              13  Sony PlayStation 5
 87  Nintendo Switch          12  Sony PlayStation
 76  Sony PlayStation 4        8  Nintendo Game Boy
 64  Nintendo 64               6  Nintendo Game Boy Advance
 52  Sony PlayStation 2        6  Microsoft Xbox Series X
 51  Sony PlayStation 3        4  Microsoft Xbox
 46  Nintendo 3DS              3  Nintendo Game Boy Color
 44  Microsoft Xbox 360        3  Nintendo Game & Watch
 39  Nintendo Wii U            3  Nintendo Switch 2
 38  Sony PSP                  2  Sega Dreamcast
 36  NES/Famicom               1  PC
 32  Nintendo Wii
 27  Nintendo GameCube
 21  Microsoft Xbox One
```

> El nombre EXACTO de plataforma importa al filtrar: `NES/Famicom`,
> `SNES/Super Famicom`, `Nintendo 64`, etc.

## Columnas del CSV

`Platform, Category, UserRecordType, Title, Country, ReleaseType, Publisher,
Developer, Genre, CreatedAt, Ownership, PriceLoose, PriceCIB, PriceNew,
YourPrice, PricePaid, ItemCondition, BoxCondition, ManualCondition, Notes,
Tags, metacritic`

Notas:
- **Precios** en formato europeo con coma decimal (ej. `16,14`). Moneda segun GameEye (EUR).
- `Ownership`: `Loose` (suelto), `Boxed` (con caja), `CIB` (completo en caja).
- `metacritic`: puede venir `Missing Field` (sin nota; comun en juegos retro previos a Metacritic).
- `PricePaid = -1.0` significa "no registrado".

## Como consultar (ejemplos)

```python
import csv
from collections import Counter
rows = list(csv.DictReader(open(r'data/coleccion/coleccion-retrotarros.csv', encoding='utf-8')))

# juegos de una plataforma
nes = [r for r in rows if r['Platform'] == 'NES/Famicom']

# ordenar por precio loose (coma decimal -> float)
def precio(r, col='PriceLoose'):
    try: return float((r[col] or '0').replace('.', '').replace(',', '.'))
    except: return 0.0
caros = sorted(nes, key=lambda r: precio(r, 'PriceCIB'), reverse=True)

# por genero
Counter(r['Genre'].split(',')[0].strip() for r in nes)
```
