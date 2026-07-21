# Retrotarros — Handoff Doc

> Estado de sesión a sesión. **Leer ANTES de cualquier acción**, después leer `CLAUDE.md`,
> `docs/modus-operandi/` y los docs relevantes al escenario.

## Estado actual (2026-07-20)

Canal en pre-lanzamiento con una base grande de contenido armado. Arco **SEGA cerrado** (8 episodios listos para grabar) y **TarroShorts de embudo de precios SEGA — ronda completa** (los 4). Infraestructura del repo, Drive sync y app TarroBot operativas.

**En qué estamos ahora mismo:**
- **Arco SEGA — 8 episodios cerrados** (HTML + pauta MD + box arts reales): Master System, Mega Drive, Dreamcast, Saturn, cada uno en top-mundial + top-precios. Falta grabarlos/renderizarlos en el estudio.
- **TarroShorts de precios SEGA — LOS 4 CERRADOS Y PUSHEADOS:** `mega-drive-top-precios`, `master-system-top-precios`, `dreamcast-top-precios` y `saturn-top-precios`, todos al estilo VIGENTE (`item-tag` PUESTO 10→6, box arts reales con padding-hack, enfoque teaser que guarda el grial SIN nombrarlo + invita a suscribirse/campana). Verificados a 1080×1920 real Y frame-por-frame en el MP4 renderizado (contact sheets), renderizados, commiteados (`0092a96`..`6df1ff3`) y pusheados a GitHub. Sincronizados a Drive (ambos scripts).
  - En el camino se corrigieron **2 bugs reales del pipeline** `scripts/tarroshort_render.py` (afectan a cualquier TarroShort, no solo estos 4): intro filtrándose entre escenas (timing de fuentes por red) y glitch en el corte de escena (concat `-c copy` → ahora siempre re-encode). Detalle y regla de verificación en `docs/modus-operandi/convenciones-tarroshorts.md` § "Bugs corregidos en el pipeline de render".
  - **Pendiente siguiente:** los shorts de top-mundial de la saga Sega (mismo molde, otro enfoque de contenido a definir con Luis).
- **Nace `docs/modus-operandi/`** — carpeta canónica de convenciones de estilo + bitácora de decisiones, para que las mejoras no se pierdan entre sesiones.

## Decidido y cerrado (vigente)

- Nombre del canal: **Retrotarros**. Tagline público: `Nostalgia + Juegos + Música`.
- Identidad visual base (paleta synthwave/arcade). Detalle en `docs/identidad-visual.md`.
- **La colección es del canal, no de una persona.** Presentadores: Luis y **Coco**. → `CLAUDE.md`.
- **Convención de pautas:** tres archivos por episodio con mismo slug (`pauta` + `discusion` + `html`).
- **Convención de arcos:** un MD por generación en `docs/arcos/{generación}.md`.
- **Top precios en 3 bloques** (retail #10→#1 + rarezas + santo grial). → `CLAUDE.md`.
- **Estilo de TarroShorts:** `item-tag` (PUESTO+dato, cyan→amarillo→dorado) + box arts con padding-hack + teaser/top directo. → `docs/modus-operandi/convenciones-tarroshorts.md`.
- **Git workflow:** Claude ejecuta commits/push/scripts; Luis confirma solo remotas o destructivas.
- **Drive sync:** los DOS scripts (`sync-to-drive.ps1` + `sync-tarrobot-to-drive.ps1`). Arquitectura de 3 lugares (repo → Drive sync → Drive producción).
- **Generadores de decks reutilizables:** `coleccion_deck.py`, `top_deck.py`, `saga_deck.py`.

## Historia de arcos

- **Arco N64** — 3 de 7 episodios cerrados en mayo 2026 (ranking, hardware-raro, no-latam). Tablero en [`docs/arcos/n64.md`](docs/arcos/n64.md). Ideas pendientes: kirkhope-rare, nintendo-vs-playstation, archivo-koko, ost-bateria.
- **Arcos NES / SNES / PS Vita** — episodios y colecciones armados (top-mundial, top-precios, colección, etc.). Ver `docs/pauta-*.md`.
- **12 sagas** (Mario, Zelda, Metroid, Metal Gear, Sonic, Street Fighter, etc.) — líneas de tiempo cerradas.
- **Arco SEGA** — cerrado 2026 (ver Estado actual).

## En proceso / por resolver

- **Shorts de top-mundial SEGA** (Master System, Mega Drive, Dreamcast, Saturn) — mismo molde `item-tag`, falta definir enfoque de contenido con Luis.
- **Grabar los episodios cerrados en el estudio con Coco** — falta feedback de cámara.
- **Más episodios largos** con el mismo molde de ranking (ideas: Game Boy, PS1, arcade).
- Reserva de handles, logo final, calendario editorial, primer dev Indie Lat.

## Cómo arrancar la próxima sesión

1. Leer este archivo + `CLAUDE.md` completo.
2. Leer `docs/modus-operandi/README.md` (estilo de shorts + bitácora de decisiones).
3. Si vas a un arco → leer su `docs/arcos/{gen}.md`. Si vas a un episodio → su `docs/pauta-{slug}.md`.
4. Si vas a tocar un TarroShort → leer `docs/modus-operandi/convenciones-tarroshorts.md` ANTES de copiar cualquier molde (evita usar el estilo viejo).
5. Antes de generar contenido nuevo, confirmar con Luis qué se ataca.

## Archivos clave del repo

| Archivo | Rol |
|---------|-----|
| `CLAUDE.md` | Reglas operativas, convenciones, workflow Git, sync Drive. |
| `docs/modus-operandi/` | Convenciones de estilo de shorts + bitácora de decisiones. |
| `docs/estrategia.md` | Documento maestro del canal. |
| `docs/formatos.md` | Formatos (largos, shorts por lane, Indie Lat). |
| `docs/briefings-compositores.md` | Fichas de compositores. |
| `data/coleccion/coleccion-retrotarros.csv` | Colección física — fuente de verdad (export GameEye, ~898 juegos). |
| `scripts/top_deck.py` · `saga_deck.py` · `coleccion_deck.py` | Generadores de decks. |
| `scripts/tarroshort_render.py` | Render MP4 de los TarroShorts. |
| `scripts/sync-to-drive.ps1` · `sync-tarrobot-to-drive.ps1` | Sincronización con el Drive del estudio. |

---

*Última actualización: 2026-07-20 · Ronda completa de TarroShorts de precios SEGA (4/4), 2 bugs de render corregidos, pusheado a GitHub*
