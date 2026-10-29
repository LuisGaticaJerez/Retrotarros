# Esqueleto del kit de YouTube Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Un comando que crea el esqueleto del kit de YouTube de una reseña (parte mecánica rellena, parte humana con marcadores `[REDACTAR: ...]`) y otro que revisa el kit terminado.

**Architecture:** Script nuevo `scripts/resena_kit.py` con funciones puras (`hashtags`, `tags`, `esqueleto`, `revisar_kit`) y un CLI. Para leer el DATA de un driver sin generar la reseña reutiliza la captura del lint, factorizada como `capturar_driver` en `scripts/resena_lint.py`.

**Tech Stack:** Python 3.14, sin pytest (pruebas con asserts simples ejecutables con `python`).

**Spec:** `docs/superpowers/specs/2026-10-28-resena-kit-design.md`

## Global Constraints

- El código no redacta prosa: todo texto humano queda como marcador `[REDACTAR: ...]`.
- `crear` nunca sobrescribe un kit existente: sale con código 2.
- Receta de hashtags: `#RetroReseñas #<Juego> #<Consola> #Retrogaming #Retrotarros`.
- Tags: entre 15 y 20, bloque de máximo 500 caracteres. Cola fija: `retroreseñas, reseña retro, retrogaming, juegos retro, nostalgia gamer, ¿envejeció bien?, retrotarros`.
- CTA fijo: `🔔 Suscríbete a RETROTARROS para más reseñas retro: nostalgia + juegos + música.`
- Pie: `**Formato:** Reseña (horizontal, hasta 10 min)`.
- Sin emojis ni guiones largos en código, comentarios, mensajes y commits, salvo los emojis que van dentro del texto del kit (🎮, 🔔, 👇).
- Commits sin `Co-Authored-By` (regla del `CLAUDE.md` del canal).
- Pruebas: `PYTHONIOENCODING=utf-8 python scripts/test_resena_lint.py` (30 pruebas, no deben romperse) y `PYTHONIOENCODING=utf-8 python scripts/test_resena_kit.py`.

## Review Focus

1. Juegos con caracteres especiales o puntuación (`Pokémon Rojo/Azul`, `Disney's Aladdin`, `Zombies Ate My Neighbors`): el hashtag sale sin símbolos y sin romperse.
2. `consola`, `developer` o `genero` ausentes o vacíos: no hay excepción y simplemente no aportan tags.
3. Un driver que llama dos veces a `generar_resena`: se procesa cada llamada; si un kit ya existe y el otro no, crea el nuevo y devuelve 2.
4. Kit con saltos de línea `\r\n` (Windows): `revisar_kit` lo acepta igual.
5. Bloque de tags repartido en varias líneas: se cuenta por comas y el tope de 500 caracteres incluye los saltos.

---

### Task 1: Factorizar la captura de drivers en el lint

**Files:**
- Modify: `scripts/resena_lint.py` (función `main`)
- Modify: `scripts/test_resena_lint.py`

**Interfaces:**
- Produces: `capturar_driver(ruta: str) -> list[tuple[dict, str]]` en `scripts/resena_lint.py`. Ejecuta el driver con `resena_deck.generar_resena` reemplazada por una función que solo anota `(data, out_slug)` y la restaura al terminar; devuelve las llamadas capturadas (lista vacía si el driver no llamó a `generar_resena`). `main` pasa a usarla.

- [ ] **Step 1: Write the failing test** `test_capturar_driver` en `scripts/test_resena_lint.py`: con un driver temporal (reutilizar `_driver_temporal` con `T._data()`), `L.capturar_driver(str(ruta))` devuelve una lista de un elemento cuyo `[0][1] == "resena-prueba"`, `[0][0]["juego"] == "Juego de Prueba"`, y no existe `studio/resenas/resena-prueba.html`; con un driver que no llama a `generar_resena` (archivo con solo `x = 1`) devuelve `[]`.
- [ ] **Step 2: Run** `PYTHONIOENCODING=utf-8 python scripts/test_resena_lint.py`. Expected: falla con `AttributeError` por `capturar_driver`.
- [ ] **Step 3: Implement** `capturar_driver` moviendo a ella la lógica de captura que hoy está dentro de `main`, y haz que `main` la use sin cambiar su comportamiento ni sus códigos de salida.
- [ ] **Step 4: Run** `PYTHONIOENCODING=utf-8 python scripts/test_resena_lint.py`. Expected: `OK 31 pruebas`.
- [ ] **Step 5: Commit** `refactor(resenas): capturar_driver reutilizable en el lint`.

### Task 2: Generar el esqueleto del kit

**Files:**
- Create: `scripts/resena_kit.py`
- Create: `scripts/test_resena_kit.py`

**Interfaces:**
- Consumes: `capturar_driver` de Task 1.
- Produces, en `scripts/resena_kit.py`:
  - `CARPETA_KITS: Path` = `docs/descripciones` del repo (las pruebas pasan otra carpeta por parámetro).
  - `hashtag_juego(data: dict) -> str` y `hashtag_consola(data: dict) -> str`: cada uno devuelve un hashtag con `#`.
  - `hashtags(data: dict) -> str`: la línea completa de cinco hashtags.
  - `tags(data: dict) -> str`: la línea de tags separada por `, `, sin duplicados, que termina con el marcador `[REDACTAR: sumar tags propios del juego: personas, secuela, términos]`.
  - `esqueleto(data: dict, out_slug: str, hoy: str) -> str`: el `.md` completo.
  - `crear(ruta_driver: str, carpeta: Path | None = None, hoy: str | None = None) -> int`: escribe un kit por cada llamada capturada y devuelve 0 si creó todos, 2 si alguno ya existía (sin tocarlo).
  - `main(argv: list[str]) -> int`.
- En `scripts/test_resena_kit.py`: runner igual al de `test_resena_lint.py` e importa `DATA_VALIDA` y `_data` de ese módulo.

- [ ] **Step 1: Write failing tests** en `scripts/test_resena_kit.py`: `test_hashtag_juego` (`"Commandos: Behind Enemy Lines"` da `#Commandos`; `"The Sims"` da `#TheSims`; `"Pokémon Rojo/Azul"` da `#PokémonRojoAzul`; `"Disney's Aladdin"` da `#DisneysAladdin`; con `hashtag_juego="#Doom2"` en el DATA da `#Doom2`), `test_hashtag_consola` (`"SNES · Sega Genesis"` da `#SNES`; `"PC · Mac · PlayStation 2"` da `#PC`; `"Sega Genesis"` da `#SegaGenesis`; `consola` ausente da cadena vacía), `test_hashtags_linea` (con `DATA_VALIDA`: `#RetroReseñas #JuegoDePrueba #PC #Retrogaming #Retrotarros`), `test_tags` (con `DATA_VALIDA`: contiene `juego de prueba reseña`, `juego de prueba 1999`, `estudio ejemplo`, la cola fija completa y termina con el marcador; sin duplicados; con `developer="Pyro Studios (publica Eidos Interactive)"` aparece `pyro studios` y no `eidos`; con `developer`, `genero` y `consola` ausentes no lanza excepción), `test_esqueleto_estructura` (con fecha `2026-10-28`: contiene los títulos con marcador, la línea `Volvemos a 1999 para revisar Juego de Prueba`, el CTA fijo, la línea de hashtags, `**Slug:** `resena-juego``, `**Última actualización:** 2026-10-28`, y al menos 6 apariciones de `[REDACTAR`; sin `pedido` no aparece `agradecer a quien lo pidió`, con `pedido` sí), `test_crear_no_sobrescribe` (con driver temporal y carpeta temporal: la primera llamada devuelve 0 y el archivo `descripcion-resena-prueba.md` existe; tras modificar su contenido, la segunda devuelve 2 y el contenido modificado sigue igual), `test_crear_dos_llamadas` (un driver que llama dos veces a `generar_resena` con slugs distintos crea dos archivos; si uno ya existe, crea el otro y devuelve 2).
- [ ] **Step 2: Run** `PYTHONIOENCODING=utf-8 python scripts/test_resena_kit.py`. Expected: falla con `ModuleNotFoundError: resena_kit`.
- [ ] **Step 3: Implement** el módulo. El nombre del archivo es `descripcion-<out_slug>.md`. El hashtag convierte cada palabra a mayúscula inicial y descarta signos (conserva letras con tilde y la ñ), corta el nombre del juego en el primer `:`, y toma como consola la primera plataforma separando `consola` por `·` o `/`. Los tags se escriben en minúsculas, el developer sin el paréntesis, el género sin paréntesis, y cada plataforma de `consola` por separado. El CLI `main` acepta una ruta de driver (llama a `crear`); sin argumentos devuelve 2 con un mensaje de uso. El formato del `.md` sigue el de `docs/descripciones/descripcion-resena-the-sims.md` (secciones `## Títulos sugeridos`, `## Descripción`, `## Tags YouTube (keywords)`, `## Comentario fijado`, pie), con `[REDACTAR: ...]` en título 1, sufijo del título 2, frase de apertura, párrafo de contexto, pregunta, y comentario fijado.
- [ ] **Step 4: Run** `PYTHONIOENCODING=utf-8 python scripts/test_resena_kit.py`. Expected: `OK 7 pruebas`.
- [ ] **Step 5: Commit** `feat(resenas): esqueleto del kit de YouTube`.

### Task 3: Revisar el kit terminado, documentación y prueba real

**Files:**
- Modify: `scripts/resena_kit.py`
- Modify: `scripts/test_resena_kit.py`
- Modify: `CLAUDE.md` (sección "Kit de publicación YouTube automático")
- Modify: `HANDOFF.md`

**Interfaces:**
- Consumes: `esqueleto`, `main` de Task 2.
- Produces: `revisar_kit(texto: str) -> list[str]` (lista de errores) y la opción `--revisar <archivo>` en `main` (código 0 sin errores, 1 con errores, 2 si el archivo no existe).

- [ ] **Step 1: Write failing tests**: `test_revisar_esqueleto_falla` (el esqueleto recién generado da un error que nombra `[REDACTAR`), `test_revisar_kit_completo` (el esqueleto con cada marcador reemplazado por `uno, dos, tres, cuatro` da `[]`), `test_revisar_tags_largos` (un bloque de tags de más de 500 caracteres da error que nombra `500`), `test_revisar_cantidad_tags` (menos de 15 y más de 20 dan error cada uno), `test_revisar_hashtags` (cuatro hashtags válidos no dan error; seis dan error; primer hashtag distinto de `#RetroReseñas` da error; último distinto de `#Retrotarros` da error), `test_revisar_falta_cta_o_comentario` (quitar el CTA da error; quitar la sección de comentario fijado da error), `test_revisar_voseo` (insertar `tenés` o `vos` en la descripción da error que nombra `voseo`; `voz` no da error), `test_revisar_crlf_y_tags_en_varias_lineas` (el kit completo con `\r\n` y el bloque de tags partido en varias líneas da `[]`), `test_cli_revisar` (`main(["--revisar", ruta])` devuelve 1 con el esqueleto, 0 con el kit completo escrito en un archivo temporal, 2 con una ruta inexistente).
- [ ] **Step 2: Run** `PYTHONIOENCODING=utf-8 python scripts/test_resena_kit.py`. Expected: fallan las pruebas nuevas.
- [ ] **Step 3: Implement** `revisar_kit` y `--revisar`. Los bloques se leen de los bloques de código bajo cada encabezado `##`; la línea de hashtags es la última línea que empieza con `#` en el bloque de descripción; los tags se cuentan por comas sobre el bloque de la sección `Tags YouTube`, y el tope de 500 caracteres incluye los saltos de línea; el voseo se busca por palabra completa, sin distinguir mayúsculas (`tenés`, `querés`, `sabés`, `decime`, `elegís`, `defendés`, `vos`).
- [ ] **Step 4: Run** ambas suites: `PYTHONIOENCODING=utf-8 python scripts/test_resena_lint.py` (`OK 31 pruebas`) y `PYTHONIOENCODING=utf-8 python scripts/test_resena_kit.py` (`OK 16 pruebas`).
- [ ] **Step 5: Prueba real** sobre un driver existente con una carpeta temporal para no ensuciar `docs/`: ejecutar `crear(".cache/gen_resena_the-sims.py", carpeta=<temporal>)` desde Python, abrir el `.md` resultante y comprobar que se parece al kit vigente de The Sims en estructura. Luego `revisar_kit` sobre el kit real `docs/descripciones/descripcion-resena-the-sims.md` y `...commandos-behind-enemy-lines.md`; anotar en el HANDOFF cualquier error que detecte (no corregir esos kits aquí, solo informar).
- [ ] **Step 6: Edit** `CLAUDE.md` con una regla corta en la sección del kit de publicación (el comando para crear el esqueleto y el de revisar antes de pegar en el chat, y que lo humano lo escribe Claude a mano) y `HANDOFF.md` con una nota breve del cambio y del resultado del Step 5.
- [ ] **Step 7: Commit** `feat(resenas): revisar el kit terminado y documentacion`.
