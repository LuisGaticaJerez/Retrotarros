# Bitácora de decisiones — Retrotarros

> Memoria cronológica de acuerdos y decisiones con Luis. Cada entrada apunta a dónde vive el detalle
> (para no duplicar). Sirve para reconstruir el "por qué" cuando pasa tiempo entre sesiones.
> Se agrega al final; no se reescribe la historia. Última entrada: 2026-07-20.

## Cómo leer esto

- **CLAUDE.md** (raíz del repo) = reglas operativas vigentes, siempre la verdad actual.
- **Esta bitácora** = el registro de CUÁNDO y POR QUÉ se decidió cada cosa. Si una regla del CLAUDE.md te sorprende, acá está el contexto.
- **convenciones-tarroshorts.md** = el estilo vigente de los shorts en detalle.

---

## 2026-05-14 — Fundaciones

- **Claude ejecuta git directamente.** `git add/commit/push` y scripts los corre Claude en el sandbox; Luis solo confirma operaciones remotas o destructivas. Se estableció porque pasarle comandos para copiar/pegar bajaba el ritmo. → `CLAUDE.md` § Git workflow.
- **Convención de pautas:** tres archivos por episodio con mismo slug (`pauta-{slug}.md` + `discusion-{slug}.md` + `studio/{slug}.html`). → `CLAUDE.md` § Convención de pautas.
- **Repo ya no vive en OneDrive.** Casa canónica: `D:\Recursos Retrotarros\repo\`, backup en GitHub. → `CLAUDE.md` § Ubicaciones canónicas.

## 2026-06-07 — Top precios y entrega

- **Top precios en 3 bloques:** Top 10 retail (CIB, #10→#1) + apartado rarezas/no-retail (etiqueta, no número) + santo grial (slide único). → `CLAUDE.md` § Convención del TOP PRECIOS.
- **Precio grande arriba-derecha** en cada slide de precios; posición arriba-izquierda.
- **Regla de entrega:** al cerrar un kit de publicación, **pegar en el chat** el texto listo para YouTube (título + descripción + comentario fijado + tags), no solo dejarlo en el `.md`.
- **Sync = los DOS scripts, siempre:** `sync-to-drive.ps1` (pautas/HTML/capturas del estudio) + `sync-tarrobot-to-drive.ps1` (app TarroBot). → `CLAUDE.md` § Workflow obligatorio al cerrar.

## 2026-06-08 — Generadores y lane TarroBot

- **Lista de paneo automática** por colección (`lista-paneo-<slug>.md` con las 3 joyas ⭐). → `CLAUDE.md`.
- **TarroShorts de DATOS** (lane TarroBot, tema curioso libre, 5 datos + reacción). Slug `datos-*`. → `CLAUDE.md` § TarroShorts de DATOS.

## 2026-06-10 — Sagas

- **Criterio de línea de tiempo SAGA:** solo mainline en orden de lanzamiento; spin-offs a "EN LA VITRINA"; remakes sin nodo propio; entra aunque no lo tengamos; corte ~16 juegos. → `CLAUDE.md` § Criterio de la línea de tiempo SAGA.

## 2026-06-15 — La colección es del canal + notas

- **La colección es de RETROTARROS, no de una persona.** En pantalla/guion: "EN LA COLECCIÓN / NO ESTÁ EN LA COLECCIÓN", nunca "Coco lo tiene / le falta". Presentadores = Luis y Coco (el nombre correcto es **Coco**, no "Koko"; los paths internos heredados no se renombran). → `CLAUDE.md` § REGLA colección.
- **Notas teleprompter dan MÁS info que la pantalla**, para elegir qué decir en cámara — no repetir el "por qué" visible. → `CLAUDE.md` § Capa de notas.

## 2026-06-17 — Estrategia de shorts

- **El short es embudo, no contenido suelto.** Tipos que convierten: precios > ranking polémico > datos. **Música de juegos descartada** como formato (Content ID). → `convenciones-tarroshorts.md` § Estrategia.

## 2026-06-19 — Infraestructura Drive / TarroBot

- **Arquitectura de 3 lugares:** repo git (fuente) → Drive sync `Studio\tarrobot\` (lo que TarroBot lee) → Drive producción `Studio\<slug>\` (carpetas de trabajo de Luis). → `reference-tarrobot-installer-drive` (memoria) + `CLAUDE.md`.
- **TarroBot se instala LOCAL, nunca dentro de la carpeta de sync** (el `.venv` de ~600 MB se subiría/bajaría en cada sync). Instalador oficial único vigente **v1.5.3** en `Studio\TarroBot-Instalador\`.
- **Desfase de carpetas de producción resuelto** (commit `be9324d`): el sync refresca `<slug>.html` + gameboxes en cada `Studio\<slug>\` desde el repo.

## 2026-06-25 — Reglas visuales de episodios/shorts

- **Letras grandes** para la info del público (no se leía con gameplay encima).
- **Notas activables con tecla `N` Y con botón clickeable**; el botón NO sale en captura (`.no-capture`).
- **Box arts completas** descargadas de libretro-thumbnails (`object-fit:contain` + blur de fondo).
- **Plan SEGA completo:** 8 episodios (Master System, Mega Drive, Dreamcast, Saturn) × (top-mundial + top-precios), con HTML + pauta MD + box arts. → `reference-retrotarros-episode-formats` (memoria).

## 2026-07-20 — Estilo de shorts consolidado + esta carpeta

- **Estilo `item-tag` confirmado como estándar de TarroShorts** (PUESTO + dato juntos, escalada cyan → `ye` → `gold`), reemplaza el viejo `rank-badge` + `item-price`. Se detectó porque un short SEGA salió con el molde viejo y hubo que rehacerlo. → `convenciones-tarroshorts.md`.
- **Shorts de precios SEGA:** box arts reales + enfoque **teaser** (guardar el grial para el canal). Decisión de Luis.
- **Gotcha padding-hack:** `aspect-ratio` colapsa el `item-photo` a altura 0 en flex-item columna → usar `::before{padding-top:100%}` + imgs `position:absolute`. Verificar siempre a 1080×1920 (a media resolución el flex-shrink da falso negativo). → `convenciones-tarroshorts.md`.
- **Nace `docs/modus-operandi/`** (esta carpeta) para consolidar memoria + convenciones de estilo y que no se pierdan entre sesiones. Fuente canónica en el repo, respaldo al Drive.
