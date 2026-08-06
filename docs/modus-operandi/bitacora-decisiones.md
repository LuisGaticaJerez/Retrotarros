# Bitácora de decisiones — Retrotarros

> Memoria cronológica de acuerdos y decisiones con Luis. Cada entrada apunta a dónde vive el detalle
> (para no duplicar). Sirve para reconstruir el "por qué" cuando pasa tiempo entre sesiones.
> Se agrega al final; no se reescribe la historia. Última entrada: 2026-07-29.

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
- **Ronda de TarroShorts de precios SEGA cerrada (4/4):** Master System, Mega Drive, Dreamcast, Saturn. → `convenciones-tarroshorts.md`.
- **REGLA — el teaser siempre PUESTO 10 → PUESTO 6**, aunque la pauta del episodio solo liste 9 items (Mega Drive y Saturn arrancaban en #9; se corrió la etiqueta, no se inventaron items). Es una convención de display, no una renumeración del ranking oficial. → `convenciones-tarroshorts.md`.
- **REGLA — el cierre nunca nombra el santo grial + siempre invita a suscribirse y activar la campana.** Se detectó porque los cierres de Mega Drive ("un Tetris prohibido") y Saturn ("un Daytona online") revelaban el nombre sin querer. → `convenciones-tarroshorts.md`.
- **Dos bugs reales del pipeline de render encontrados por Luis mirando el MP4 final** (no visibles en capturas de pantalla del navegador): (1) la intro se filtraba al arranque de la escena del item 1 por timing de carga de fuentes vía red; (2) glitch/estática en el frame del corte hacia el cierre por usar `-c copy` al concatenar streams codificados por separado. Ambos corregidos en `scripts/tarroshort_render.py` (`LOOP_TRIM_START`/`REC_SECONDS` más generosos + concat siempre re-encodea). **Lección de proceso:** las capturas de pantalla del navegador (`mcp__Claude_Browser`) verifican el HTML/CSS pero NO el pipeline de grabación — un short nuevo solo se da por bueno tras revisar el MP4 real frame por frame (contact sheet con `ffmpeg -vf fps=N` + `tile=`), sobre todo en las transiciones entre escenas. → `convenciones-tarroshorts.md` § Render y sync.

## 2026-07-21 — Playlist Reseñas (nuevo formato)

- **Nace la playlist "Reseñas":** un juego por video, ángulo retrospectivo, máximo 10 min, talento alterna Luis/Koko 1 y 1, nunca cierra con batería, portada nunca muestra el nombre del presentador. Diseñado con Luis via brainstorming + mockup real revisado en navegador antes de escribir el generador. → `docs/superpowers/specs/2026-07-21-resena-format-design.md`.
- **Primera tanda: 5 reseñas armadas** (SMB3, Sonic 2, Killer Instinct Gold, Mortal Kombat, Donkey Kong Country) via `scripts/resena_deck.py`, salida en `studio/resenas/<slug>.html` (carpeta aparte — pedido de Luis, distinto al resto de formatos que van en la raíz de `studio/`). Cero publicadas — falta crear la playlist en YouTube Studio.
- **Bug real encontrado en la implementación (no en el diseño):** al mover la salida a una subcarpeta, las rutas relativas de box art quedaron rotas (`img/resenas/...` en vez de `../img/resenas/...`). Se detectó verificando con Playwright (el navegador interactivo se puso inestable esa sesión) — capturas confirmaron el bug y el fix. **Lección:** cuando un generador cambia de carpeta de salida, revisar TODAS las rutas relativas del HTML, no asumir que siguen siendo válidas.
- **Regla del canal (nunca logo) aplicada de nuevo:** Mortal Kombat no tiene box art real disponible en Wikipedia (solo el logo del dragón) → se usó un fallback de tarjeta de color en vez de forzar el logo. → `CLAUDE.md` § Imágenes en HTMLs de ranking (misma regla, aplicada acá).

## 2026-07-29 — Comparativa sin dato, tono vendedor, criterio de selección y fixes de reseñas

- **Slide COMPARATIVA rediseñado:** sin texto/dato en pantalla, solo las 2 TarroVision + VS ocupando todo el alto disponible — el contexto se cuenta hablado mientras se muestra gameplay. Ajuste post-captura: la primera versión con dato dejaba las pantallas chicas y descentradas. → `scripts/resena_deck.py`, `CLAUDE.md` § Reseñas.
- **Regla de tono del contexto/veredicto:** la reseña de Mortal Kombat generó rechazo en la comunidad por comparar demasiado con Street Fighter II y por un veredicto que vendía el juego "para abajo". Corregidas Killer Instinct, Altered Beast y Donkey Kong Country (Mortal Kombat se dejó igual, decisión de Luis). → `CLAUDE.md` § REGLA Tono del contexto y el veredicto.
- **Criterio de selección de candidatos a reseña, en este orden: nostalgia > historia > diferencias tecnológicas entre versiones.** No es excluyente — un juego mono-plataforma sigue siendo buen candidato. → `CLAUDE.md` § REGLA Criterio de selección de candidatos.
- **Bug real: las capturas de reseñas nunca se copiaban a Drive.** El bloque de sync de reseñas (agregado 2026-07-21) copiaba HTML + box art pero nunca tuvo la lógica de `captures/` que sí tiene el bloque genérico — las 17 reseñas del canal nunca tuvieron sus PNGs en `G:\Mi unidad\Studio\Resenas\`. Detectado por Luis revisando el Drive real, no por el log del script (que decía "sincronización completa"). Corregido en `scripts/sync-to-drive.ps1`. **Lección:** un script que reporta éxito no garantiza que copió todo — verificar contra el destino real de vez en cuando, no solo contra su propio log.
- **Ficha de reseña con ancho dinámico para la caja:** el contenedor tenía 380px fijos pensado solo para cajas verticales NTSC (3:4). Cambiado a `minmax(320px,440px)` + `object-fit:contain` para que cajas horizontales (algunas ediciones/plataformas) no se compriman. → `scripts/resena_deck.py`.
- **Los kits de YouTube (`docs/descripcion-*.md`) SÍ llevan tildes y Ñ correctas** — a diferencia de los HTML on-screen del canal (que van sin tildes por diseño visual), la descripción que se pega en YouTube es prosa normal para el público y debe tener ortografía completa. Se encontró voseo argentino real ("elegís vos", "defendés") en 3 kits de TarroShorts y falta sistemática de tildes/Ñ (ej. "anios" en vez de "años") en todos los kits de reseñas — corregidos los 22 archivos existentes. → `CLAUDE.md` § REGLA INMUTABLE Tono y lengua.

## 2026-07-29 — Arranca el arco Atari 2600 (top mundial + top precios)

- **Primeros episodios Atari 2600: top-mundial + top-precios**, mismo día, siguiendo el patrón estándar del canal (3 bloques obligatorios en precios: retail + rarezas/no-retail + santo grial). Sin `coleccion` todavía — no hay Atari 2600 en la colección física de Retrotarros, ambos rankings son puramente de investigación (crítica + mercado). → `docs/pauta-atari-2600-top-mundial.md` + `docs/pauta-atari-2600-top-precios.md`.
- **Bug real encontrado y corregido: `_auto_img()` en `scripts/top_deck.py` buscaba las box art en la raíz plana `studio/img/<slug>/` en vez de la carpeta categorizada donde realmente vive el HTML** (`studio/rankings/top-mundial/img/<slug>/`, vía `episode_category()`). Bug arrastrado desde la migración de carpetas por categoría — nunca se actualizó `_auto_img` para reflejar la nueva estructura. Las cajas no cargaban en captura (fondo morado con alt-text roto) hasta corregirlo. **Afecta a cualquier top-mundial/top-precios nuevo** generado desde esa migración, no solo Atari 2600 — revisar si `coleccion_deck.py`/`saga_deck.py` tienen el mismo patrón de bug si alguna vez generan cajas "chicas o ausentes" sin explicación.
- **9 de 15 box arts de Wikipedia resultaron incorrectas** en el top-precios de Atari 2600 (resolución de artículo equivocada): el juego "Control" (2019) en vez de "Out of Control", la serie de TV "Eli Stone" en vez de "Eli's Ladder", una foto de la consola misma en vez de "Gamma Attack", el arcade "Gauntlet" (1985) en vez del mail-order homónimo de Atari 2600, "Karate Champ" en vez de "Karate" [Ultravision], un pin promocional en vez de la caja de "Pepsi Invaders", un flyer de arcade japonés en vez de "River Patrol", una imagen de 7MB no relacionada para "Cakewalk". Todas descartadas tras verificación visual una por una, reemplazadas por fallback de color. **Lección:** con juegos poco documentados/de nicho, la tasa de error de `fetch_boxart_wiki.py` sube mucho — verificar SIEMPRE cada imagen antes de commitear, nunca asumir que "encontrado" significa "correcto".
