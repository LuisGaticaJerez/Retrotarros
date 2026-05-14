# Retrotarros — Handoff Doc

> Estado de sesión a sesión. **Leer ANTES de cualquier acción**, después leer `CLAUDE.md` y los docs relevantes al escenario.

## Estado actual (2026-05-14)

Canal en fase de pre-lanzamiento. Tres episodios del arco N64 cerrados (pauta + discusion + html), listos para grabar con Koko. Infraestructura del repo, Drive sync y plantilla DOCX profesional operativos.

## Decidido y cerrado

- Nombre del canal: **Retrotarros**.
- Dominio registrado.
- Identidad visual base (paleta synthwave/arcade retro). Variante "documento" para DOCX: magenta oscuro `#B8175E` / teal oscuro `#006B7A` / gris oscuro `#333`.
- Plan inicial de 3 meses con bloques de IPs universales + Indie Lat.
- Estructura de shorts por lane (Luis / Koko).
- **Convención de pautas:** tres archivos por episodio con mismo slug — `docs/pauta-{slug}.md` + `docs/discusion-{slug}.md` + `studio/{slug}.html`. Detalle en `CLAUDE.md`.
- **Convención de arcos:** un MD por generación en `docs/arcos/{generación}.md` como tablero de control.
- **Git workflow:** Claude ejecuta commits/push/scripts directamente; Luis confirma solo operaciones remotas o destructivas. Detalle en `CLAUDE.md` sección "Git workflow".
- **Drive sync:** `G:\Mi unidad\Studio\` con subcarpetas por slug + `pautas/` con DOCX generados via pandoc. Script: `scripts/sync-to-drive.ps1`. Template: `studio/templates/reference.docx`.
- Short #001 "Mabel Addis / primer juego con plantas" y Short #002 redactados en `docs/guiones-shorts.md`.

## Arco N64 — estado

**3 de 7 episodios cerrados** (43%). Tablero completo en [`docs/arcos/n64.md`](docs/arcos/n64.md).

| # | Slug | Estado | Notas |
|---|------|--------|-------|
| 1 | `n64-ranking` | ✓ Cerrado para grabar | Top mundial vs Retrotarros, ranking + precios. 20 box arts reales (excepto 6 sospechosas — ver Commits notables). |
| 2 | `n64-hardware-raro` | ✓ Cerrado para grabar | Consolas + periféricos. 18 ítems con placeholders estilizados (sin fotos reales todavía). |
| 3 | `n64-no-latam` | ✓ Cerrado para grabar | Juegos que nunca llegaron a Latam. 9 box arts reales + Animal Forest con placeholder. |
| 4 | `n64-kirkhope-rare` | ☐ Idea | Briefing del compositor ya listo en `docs/briefings-compositores.md`. Próximo episodio recomendado. |
| 5 | `n64-nintendo-vs-playstation` | ☐ Idea | Episodio "tanque" / contexto histórico. |
| 6 | `n64-archivo-koko` | ☐ Idea | Episodio íntimo, requiere armar lista completa con Koko. |
| 7 | `n64-ost-bateria` | ☐ Idea | Serie paralela "OST en batería por generación". Inaugura con N64. |

## En proceso / por resolver

- Reserva de handles `@retrotarros` en YouTube, Instagram, TikTok, X.
- Elección de dirección final de logo (neón puro / lockup dos pisos / texto + ícono).
- Identificación de primer dev para sección Indie Lat.
- Calendario editorial detallado Q1.
- Inventario de equipo (cámaras, mics, captura gameplay, mics batería).
- **Grabar al menos uno de los 3 episodios cerrados con Koko antes de seguir armando pautas** — feedback de cámara antes de invertir más en preproducción.
- 6 box arts del ranking N64 sin scan N64 específico (superbowling, worms, f1racing, iss2000, transformers, ratattack) — buscar manualmente en MobyGames / GameFAQs / PriceCharting cuando se quiera mejorar.
- Animal Forest del episodio no-latam sin box art N64 disponible en Wikipedia.

## Próximas pautas a desarrollar

1. **`n64-kirkhope-rare`** (próximo recomendado) — briefing del compositor ya listo, menos investigación previa.
2. **`n64-nintendo-vs-playstation`** — episodio narrativo de contexto generacional.
3. **`n64-ost-bateria`** — primer episodio de la serie musical paralela del canal.
4. Más shorts lane Luis para mantener cadencia 2–3/semana.
5. Pauta primer Indie Lat.

## Cómo arrancar la próxima sesión

1. Leer este archivo + `CLAUDE.md` completo.
2. Si vamos a tocar el arco N64 → leer [`docs/arcos/n64.md`](docs/arcos/n64.md) como bootstrap del arco.
3. Si vamos a un episodio específico → leer su `docs/pauta-{slug}.md`.
4. Antes de generar contenido nuevo, confirmar con Luis qué episodio se ataca.

## Archivos clave del repo

| Archivo | Rol |
|---------|-----|
| `CLAUDE.md` | Reglas operativas, convenciones, workflow Git, sync Drive. |
| `docs/arcos/n64.md` | Tablero de control del arco N64. |
| `docs/estrategia.md` | Documento maestro del canal. |
| `docs/briefings-compositores.md` | Fichas de compositores (Kondo, Kirkhope, Uematsu, etc.). |
| `docs/guiones-shorts.md` | Guiones lane Luis con timings y B-roll. |
| `data/coleccion_koko.csv` | Colección física de Koko — fuente de verdad (899 ítems, 26 plataformas). |
| `studio/templates/reference.docx` | Template pandoc para DOCX profesional. |
| `scripts/sync-to-drive.ps1` | Sincronización con `G:\Mi unidad\Studio\`. |

---

*Última actualización: 2026-05-14 · Cierre sesión*
