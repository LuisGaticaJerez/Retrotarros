# Índice de slugs — Retrotarros

> Documento de referencia rápida. Para cada episodio, el slug es la clave que abre los tres archivos del trío (pauta + discusion + html) y la carpeta de imágenes.

---

## Cómo se usa un slug

Para el episodio con slug `n64-top-mundial`, los archivos asociados son:

```
docs/pauta-n64-top-mundial.md          ← pauta operativa (Claude)
docs/discusion-n64-top-mundial.md      ← reunión previa (Luis + Koko)
studio/n64-top-mundial.html            ← monitor visual del estudio
studio/img/n64-top-mundial/            ← box arts del episodio
G:\Mi unidad\Studio\n64-top-mundial\   ← versión en Drive (HTML + img)
G:\Mi unidad\Studio\pautas\pauta-n64-top-mundial.docx  ← DOCX para imprimir/leer
```

---

## Slugs activos

### Arco Nintendo 64 (Gen 5)

| Slug | Episodio | Estado | Tablero |
|------|----------|--------|---------|
| `n64-top-mundial` | Top 10 N64 según la crítica (Parte 1 de 2) | ✓ Grabado, en edición | [arco](arcos/n64.md) |
| `n64-top-precios` | Top 10 N64 más caros (Parte 2 de 2) | ✓ Grabado, en edición | [arco](arcos/n64.md) |
| `n64-retrotarros-vs-mundo` | Game show · Koko vs la crítica | ✓ Grabado, en edición | [arco](arcos/n64.md) |
| `n64-archivo-koko` | La colección N64 entera de Koko (58 cartuchos) | ✓ Grabado, en edición | [arco](arcos/n64.md) |
| `n64-hardware-raro` | Consolas y periféricos más raros | ✓ Cerrado para grabar | [arco](arcos/n64.md) |
| `n64-no-latam` | Juegos que nunca llegaron a Latam | ✓ Cerrado para grabar | [arco](arcos/n64.md) |
| `n64-joyas-ocultas` | 10 olvidados Metacritic 84+ de la colección de Koko | ✓ Cerrado — pendiente reunión Koko | [arco](arcos/n64.md) |
| `n64-kirkhope-rare` | Grant Kirkhope + era dorada de Rare 1995-2008 | ✓ Cerrado para grabar | [arco](arcos/n64.md) |
| `n64-nintendo-vs-playstation` | Cómo perdió Nintendo la generación 5 (tanque del arco) | ✓ Cerrado para grabar | [arco](arcos/n64.md) |
| `n64-ost-bateria` | OST en batería · Gen 5 (serie paralela) | ☐ Pendiente | [arco](arcos/n64.md) |

### Arco PS Vita (Gen 8 portátil)

| Slug | Episodio | Estado | Tablero |
|------|----------|--------|---------|
| `psvita-archivo-koko` | Los 91 cartuchos · €2,601 CIB | ✓ Cerrado para grabar | [arco](arcos/psvita.md) |
| `psvita-top-mundial` | Top 10 PS Vita según la crítica | ✓ Cerrado para grabar | [arco](arcos/psvita.md) |
| `psvita-top-precios` | Top 10 PS Vita más caros del mundo | ✓ Cerrado para grabar | [arco](arcos/psvita.md) |
| `psvita-retrotarros-vs-mundo` | Game show · Koko vs la crítica | ✓ Cerrado para grabar | [arco](arcos/psvita.md) |
| `psvita-joyas-ocultas` | Curaduría de joyas de la colección | ☐ Pendiente | [arco](arcos/psvita.md) |
| `psvita-no-latam` | La consola que Sony abandonó en Latam | ☐ Pendiente | [arco](arcos/psvita.md) |
| `psvita-vs-3ds` | Cómo Sony perdió la guerra portátil | ☐ Pendiente | [arco](arcos/psvita.md) |
| `psvita-biografico` | Compositor o studio japonés (TBD) | ☐ Pendiente | [arco](arcos/psvita.md) |
| `psvita-ost-bateria` | OST en batería · Gen 8 (serie paralela) | ☐ Pendiente | [arco](arcos/psvita.md) |

### Otros (futuros)

| Slug | Episodio | Estado |
|------|----------|--------|
| `snes-ranking` | Top SNES (mismo formato que N64) | ☐ Futuro |
| `snes-hardware-raro` | Consolas y periféricos SNES | ☐ Futuro |
| `snes-no-latam` | Juegos SNES que no llegaron a Latam | ☐ Futuro |
| `snes-ost-bateria` | OST en batería · Gen 4 SNES | ☐ Futuro |
| `ps1-ranking` | Top PS1 | ☐ Futuro |
| `indie-lat-001` | Primer episodio Indie Lat (TBD) | ☐ Futuro |

---

## Convención de naming

- **Plataforma + tipo:** `<plataforma>-<tipo>` (ej. `n64-ranking`, `snes-hardware-raro`).
- **Minúsculas, kebab-case** (guiones entre palabras).
- **Sin caracteres especiales** (sin acentos, ñ, etc.).
- **Tipos estándar del canal:**
  - `ranking` — top de juegos por crítica + precios
  - `hardware-raro` — consolas y periféricos
  - `no-latam` — exclusivos regionales / cancelados
  - `archivo-koko` — la colección física de Koko
  - `ost-bateria` — episodio musical (serie paralela)
  - `kirkhope-rare` / `uematsu-square` / etc. — biográficos de compositor + estudio
  - `nintendo-vs-playstation` / `sega-vs-nintendo` / etc. — contexto histórico generacional
- **Para Indie Lat:** `indie-lat-NNN` con número correlativo.

---

## Cómo buscar rápido

**Desde el repo (terminal):**
```powershell
# Listar todos los slugs cerrados:
ls docs/pauta-*.md | foreach { $_.Name -replace 'pauta-(.+)\.md','$1' }

# Abrir el monitor de un episodio en Chrome:
start "studio\n64-ranking.html"

# Abrir la pauta en Word desde Drive:
start "G:\Mi unidad\Studio\pautas\pauta-n64-ranking.docx"
```

**Desde Drive (en estudio):**
- Abrir `G:\Mi unidad\Studio\` → ver carpetas por slug.
- HTML de cada slug está en `<slug>\<slug>.html` — doble clic abre Chrome.
- DOCX de cada slug está en `pautas\pauta-<slug>.docx` y `pautas\discusion-<slug>.docx`.

---

*Si agregás un episodio nuevo, actualizá este índice. Mantenelo corto.*
