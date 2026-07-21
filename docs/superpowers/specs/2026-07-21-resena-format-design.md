# Formato RESEÑA — diseño aprobado

> Diseñado con Luis via brainstorming interactivo (mockup real revisado en el navegador,
> no solo descrito). Aprobado 2026-07-21. Implementado el mismo dia: `scripts/resena_deck.py`
> + primera tanda de 5 reseñas en `studio/resenas/`.

## Qué es

Playlist nueva del canal: "Reseñas". Un video = un juego, revisado individualmente con
angulo **retrospectivo** ("¿envejecio bien?"), maximo 10 minutos. Distinto de los
Rankings (que comparan N juegos) — acá se profundiza en uno solo.

## Decisiones clave (por qué, no solo qué)

- **Talento alterna Luis/Koko 1 y 1, nunca juntos.** Decisión de Luis: cadencia de
  producción sin depender de que ambos estén disponibles a la vez.
- **Portada NUNCA muestra el nombre del presentador** — solo dice "RESEÑA
  RETROTARRISTICA" + el título del juego. El presentador se identifica hablando.
  Corrección de Luis sobre la primera versión del mockup (que sí tenía un tag "CON
  LUIS").
- **Nunca cierra con Koko tocando batería** (la firma de los episodios largos). Decisión
  explícita de Luis: mantiene el formato corto y no depende de que Koko esté disponible
  cuando el video lo presenta Luis.
- **Ángulo retrospectivo, no crítica clásica.** Contexto de época → cómo se juega HOY →
  veredicto. Encaja con el tagline del canal (Nostalgia + Juegos + Música) y no compite
  con reseñas genéricas de lanzamiento.
- **Veredicto = etiqueta cualitativa**, no nota numérica (a diferencia del "nota chilena
  1-7" ya usado en el especial Día del Padre). Tags usados: IMPRESCINDIBLE / ENVEJECIO
  BIEN / SOLO NOSTALGIA / PASALO.
- **Deck completo (7 slides), no minimo.** Luis prefirió esto sobre mi recomendación
  inicial de un deck de 3-4 slides — el criterio fue tener "de dónde hablar" durante los
  10 minutos, no solo un monitor de apoyo mínimo.
- **Texto público más grande que el resto de los decks de episodio** (feedback: "algunos
  nos ven desde la tv"). Subido de ~18px a ~22-26px según el bloque, sin llegar a
  "grotesco" (palabra textual de Luis).
- **Capa de notas (tecla N) copiada 1:1 del patrón ya usado en los episodios SEGA**
  (`studio/rankings/top-mundial/master-system-top-mundial.html`) — mismo CSS/JS, no se reinventó. Las notas
  dan MÁS información de la que se ve en pantalla (anécdotas, datos duros, cues de
  reacción), nunca repiten el texto visible.
- **Navegación triple:** botones ◀▶, flechas de teclado, y click en el deck (mitad
  derecha avanza, mitad izquierda retrocede). Click dentro del panel de notas NO cambia
  de slide (para poder leer/hacer scroll sin querer avanzar). Pedido explícito de Luis
  para grabación — no depender de apuntar a un botón chico.
- **Carpeta de salida separada:** `studio/resenas/<slug>.html` (no en la raíz plana de
  `studio/` como el resto de los formatos). Pedido explícito de Luis. Esto obligó a
  ajustar las rutas relativas de imagen (`../img/resenas/<key>.jpg` en vez de
  `img/resenas/<key>.jpg`) — bug real que se encontró y corrigió durante la
  implementación (verificado con Playwright, screenshots de las 5 reseñas confirmando
  que la caja carga).
- **Sin box art real → fallback de tarjeta de color, NUNCA logo.** Regla general del
  canal (`CLAUDE.md` § Imágenes en HTMLs de ranking) aplicada acá también: Wikipedia
  para "Mortal Kombat" solo tiene el logo/arte promocional del dragón, no una foto de
  caja física, así que esa reseña usa `.ficha-fallback` (tarjeta magenta con el nombre)
  en vez de forzar el logo en el espacio de la caja.

## Estructura del deck (7 slides fijas)

1. Portada — "RESEÑA RETROTARRISTICA" + título del juego + subtítulo gancho.
2. Ficha técnica — box art (o fallback) + consola/año/desarrollador/género + tag EN LA
   COLECCION / NO ESTA EN LA COLECCION.
3. Contexto de época — qué prometía el juego cuando salió.
4. TarroVision · Jugabilidad hoy — placeholder de gameplay + dato.
5. TarroVision · Gráficos y sonido hoy — mismo molde, segundo ángulo.
6. Veredicto — etiqueta cualitativa grande + resumen.
7. Cierre — suscríbete + campana (sin batería).

## Implementación

- `scripts/resena_deck.py` — `generar_resena(data, out_slug)`, adaptado de
  `scripts/saga_deck.py` (reutiliza CSS/JS de portada, ficha tipo saga-detail,
  TarroVision, divider — no se reinventó nada que ya funcionara).
- Driver por tanda en `.cache/gen_resenas_batch.py` (gitignored, patrón estándar del
  repo).
- Box art en `studio/img/resenas/<key>.jpg`, descargada con `scripts/fetch_boxart_wiki.py`
  cuando no existía ya en el repo (reutilizada de episodios previos cuando sí existía).

## Primera tanda (5 reseñas, 2026-07-21)

Super Mario Bros. 3 (NES), Sonic the Hedgehog 2 (Mega Drive), Killer Instinct Gold
(N64 — se reseñó esta versión y no la original SNES/arcade porque es la que tiene box
art real disponible), Mortal Kombat (SNES — usa el fallback de tarjeta, sin box art
real), Donkey Kong Country (SNES). Todos verificados en la colección real
(`data/coleccion/coleccion-retrotarros.csv`) — Sonic 2 es el único que NO está en la
colección, marcado correctamente en pantalla.

## Pendiente

- Crear la playlist "Reseñas" en YouTube Studio (Claude no puede crear playlists).
- Escribir `pauta-resena-<slug>.md` / `discusion-resena-<slug>.md` si se quiere el trío
  completo de documentos de producción (por ahora solo existe el HTML + los datos en el
  driver).
- Decidir orden de publicación y quién presenta cada una (Luis/Koko).
