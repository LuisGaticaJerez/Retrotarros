# Migración de las reseñas sin grabar a la gráfica nueva: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Pasar a la gráfica nueva las reseñas del backlog que Luis confirmó sin grabar (2026-10-29), con sus campos nuevos completos, HTML y capturas regenerados y sincronizados a Drive.

**Architecture:** Cada driver de `.cache/gen_resena_<juego>.py` (gitignored, copia de trabajo en el worktree y copia canónica en `D:\Recursos Retrotarros\repo\.cache\`) recibe un bloque `DATA.update({...})` antes de la llamada a `generar_resena` con `grafica="nueva"`, `plataformas`, `jugabilidad_vinetas` y `audiovisual_compositor`. Se regenera el HTML y las capturas, se revisa un montaje de las 8 slides por reseña y se commitean los HTML. Los drivers no se commitean.

**Tech Stack:** Python 3.14, Playwright (capturas), Pillow (montajes de revisión).

**Spec:** `docs/superpowers/specs/2026-10-29-resena-grafica-design.md` (sección "Fase 2: migración").

## Global Constraints

- Solo estas 23 reseñas (Luis confirmó el 2026-10-29 que ninguna está grabada): God of War, Halo: Combat Evolved, Counter-Strike, Need for Speed: Underground 2, Kingdom Hearts, Age of Empires II, Diablo, Commandos: Behind Enemy Lines, The Sims, Aladdin, Contra, Crash Bandicoot, Earthworm Jim, Fatal Fury, Final Fight, Star Fox, Yoshi's Island, JoJo's Bizarre Adventure (pedida), Altered Beast, Earthbound, Kirby Super Star, A Link to the Past, Sonic the Hedgehog. **Nunca** una reseña publicada o grabada (Melee, Montezuma, MMPR, Metal Warriors, ISS ni ninguna otra fuera de esta lista).
- Sonic the Hedgehog 2 queda fuera: tiene HTML pero su driver ya no existe en `.cache`; se anota como pendiente.
- Textos nuevos en pantalla: sin tildes débiles, sin crítica, sin inventar datos: salen de las notas ya verificadas del propio driver; si un dato falta o es dudoso, no se pone (compositor) o va a `por_confirmar` (años).
- Orden de `plataformas`: de lanzamiento real, igual que `consola`.
- `jugabilidad_vinetas`: exactamente 3 pares `[TITULO, texto]` basados en `jugabilidad_dato` y en las líneas de `notas.jugabilidad` (mecánicas reales, no trivia).
- Cuando el lint marca errores en una reseña sin grabar (TRAMA RESUMIDA, mención de arcade, tildes en pantalla, veredicto fuera de la escala), se ponen al día con las reglas vigentes: primero las notas ocultas; el texto de pantalla solo si el lint lo exige, y se registra qué cambió.
- `proxima` no se completa.
- Sin emojis ni guiones largos en código, comentarios y commits. Commits sin `Co-Authored-By`.

## Review Focus

1. Una reseña con año de plataforma que las notas no respaldan: no se inventa, se omite el año o va a `por_confirmar`.
2. Un tag de veredicto histórico fuera de la escala en una reseña sin grabar: hay que elegir una categoría de la escala y decirlo.
3. Un driver con más de una llamada a `generar_resena` o sin el patrón esperado antes de la llamada: el bloque se inserta en el lugar correcto.
4. HTML regenerado que cambia texto de pantalla además de los campos nuevos: solo se permite lo que el lint exigía.
5. Capturas con desbordes (chips en dos líneas, títulos de viñeta largos).

---

### Task 1: Herramientas y línea base

**Files:**
- Create (scratchpad, no se commitean): `volcar.py` (imprime por driver consola, año, notas de ficha, `jugabilidad_dato`, primeras líneas de `notas.jugabilidad`, `audiovisual_dato` y líneas de audiovisual que nombren compositores), `aplicar.py` (inserta un bloque `DATA.update` antes de la llamada a `generar_resena`), `montaje.py` (junta las 8 capturas de una reseña en una imagen 4x2).

**Interfaces:**
- Produces: `aplicar.py <driver> <archivo_json>` reemplaza un bloque previo marcado `# MIGRACION-GRAFICA` si existe (idempotente) y no toca el resto del driver.

- [ ] **Step 1: Write** las tres herramientas y probarlas con The Sims (volcar, aplicar con un JSON de prueba, montaje sobre las capturas existentes).
- [ ] **Step 2: Verify** que `aplicar.py` aplicado dos veces deja un solo bloque, y que `python scripts/resena_lint.py` sobre el driver sigue funcionando.
- [ ] **Step 3:** Registrar la línea base de lint de las 23 (errores y avisos por reseña) en el ledger.

### Task 2: Lote A, las 9 reseñas recientes (sin errores de lint)

Reseñas: God of War, Halo, Counter-Strike, NFS Underground 2, Kingdom Hearts, Age of Empires II, Diablo, Commandos, The Sims.

- [ ] **Step 1: Volcar** los datos de las 9 y preparar un JSON por reseña con `grafica`, `plataformas` (años de las notas de la ficha), `jugabilidad_vinetas` y `audiovisual_compositor` (si las notas lo nombran).
- [ ] **Step 2: Aplicar** a cada driver; `python scripts/resena_lint.py <driver>`: 0 errores y sin avisos de `grafica`, `jugabilidad_vinetas` ni `plataformas`.
- [ ] **Step 3: Regenerar** los 9 HTML (`python .cache/gen_resena_<juego>.py`) y las capturas (`python scripts/capture-slides.py resena-<slug>`), generar el montaje de cada una y revisarlo (desbordes, texto cortado).
- [ ] **Step 4: Commit** de los HTML: `feat(resenas): gráfica nueva en 9 reseñas del backlog (lote A)`.

### Task 3: Lote B, las antiguas sin errores de lint

Reseñas: Aladdin, Contra, Crash Bandicoot, Earthworm Jim, Fatal Fury, Final Fight, Star Fox, Yoshi's Island, JoJo's Bizarre Adventure (pedida).

- [ ] **Step 1 a 4:** igual que el lote A. En JoJo (pedida) conservar el slug `-pedido` y la slide de pedido.
- [ ] **Step 5: Commit** `feat(resenas): gráfica nueva en 9 reseñas del backlog (lote B)`.

### Task 4: Lote C, las antiguas con errores de lint

Reseñas: Altered Beast, Earthbound, Kirby Super Star, A Link to the Past, Sonic the Hedgehog.

- [ ] **Step 1: Volcar** y listar los errores de lint de cada una (`python scripts/resena_lint.py`).
- [ ] **Step 2: Poner al día** cada reseña: línea de TRAMA RESUMIDA y mención de arcade en las notas (con datos verificados de las propias notas o de una búsqueda cruzada de dos fuentes), tildes en pantalla si las hay, y `veredicto_tag` a la escala si estaba fuera. Registrar cada cambio de texto de pantalla en el ledger.
- [ ] **Step 3 a 4:** campos de gráfica nueva, regenerar, capturar y revisar el montaje como en el lote A.
- [ ] **Step 5: Commit** `feat(resenas): gráfica nueva y reglas al día en 5 reseñas del backlog (lote C)`.

### Task 5: Cierre

- [ ] **Step 1:** Copiar los drivers modificados a `D:\Recursos Retrotarros\repo\.cache\` (canónico).
- [ ] **Step 2:** Comprobar que ninguna reseña fuera de la lista cambió (`git status` limpio de otros HTML) y que las suites siguen verdes.
- [ ] **Step 3:** Actualizar `docs/canal/inventario-contenido.md` y `HANDOFF.md` (migración hecha, Sonic 2 pendiente por driver perdido).
- [ ] **Step 4:** Con el "dale" de Luis: merge a master, push, `sync-to-drive.ps1 -Episodios <las 23>` y `sync-tarrobot-to-drive.ps1 -Rapido`.
