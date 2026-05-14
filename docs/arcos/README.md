# `docs/arcos/` — Tableros de control por generación

Esta carpeta contiene **un archivo Markdown por arco de generación** del canal. Cada arco es el conjunto de episodios largos que cubre una consola/generación específica.

## Convención de naming

- `n64.md` — Nintendo 64 (Gen 5)
- `snes.md` — Super Nintendo (Gen 4)
- `ps1.md` — PlayStation (Gen 5)
- `genesis.md` — Sega Genesis / Mega Drive (Gen 4)
- `gamecube.md` — GameCube (Gen 6)
- etc.

Slug en minúscula, sin guiones intermedios cuando es una sola palabra, sin sufijos de tipo. El archivo del arco **no es la pauta de un episodio** — es el tablero de control de toda la generación.

## Qué contiene cada arco

1. **Resumen** — qué generación, cuántos episodios planeados, objetivo narrativo.
2. **Inventario de episodios** — tabla con slug, estado (idea / pauta / grabado / publicado), tipo (ranking, hardware, biográfico, musical, etc.) y archivos asociados.
3. **Orden de producción** vs **orden de publicación**.
4. **Conexiones cruzadas** — con otros arcos, con la serie paralela de OST en batería, con la sección Indie Lat.
5. **Recursos compartidos** — briefings de compositores aplicables, datos relevantes del catálogo de Koko, fuentes.
6. **Próximo paso concreto** — el episodio del arco en el que estamos trabajando ahora.

## Cómo se usa

- Al arrancar una sesión que toca un arco específico, **abrir primero el `arcos/<slug>.md`** correspondiente. Es el bootstrap del arco.
- Cuando se cierra un episodio (pauta + discusion + html publicados), **actualizar el estado del episodio en el arco**.
- Si surge una idea nueva durante una sesión, agregarla al arco como "idea" sin armar pauta todavía.

## Relación con `docs/pauta-{slug}.md`, `docs/discusion-{slug}.md` y `studio/{slug}.html`

Cada episodio del arco tiene su trío de archivos según la convención de pautas (ver `CLAUDE.md`). El arco solo los **lista y enlaza** — no duplica contenido. Si el episodio cambia, se actualiza en sus 3 archivos y se ajusta la línea del arco.
