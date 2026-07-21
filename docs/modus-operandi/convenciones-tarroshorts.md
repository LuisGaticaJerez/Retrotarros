# Convenciones de TarroShorts — estilo y mejoras aplicadas en el tiempo

> Doc canónico del **estilo actual** de los TarroShorts (verticales 1080×1920 narrados por TarroBot).
> Vive en el repo, se respalda al Drive. Si el estilo mejora, se actualiza ACÁ — no en la cabeza de nadie.
> Última revisión: 2026-07-20.

## Por qué existe este doc

Los TarroShorts fueron mejorando ronda a ronda, pero las mejoras vivían solo en el último HTML hecho y en la memoria de Claude. Resultado: al volver después de semanas, es fácil copiar un molde **viejo** sin darse cuenta (pasó el 2026-07-20 con el short de Mega Drive precios, que salió con el estilo viejo `rank-badge` y hubo que rehacerlo). Este doc fija el molde vigente para que no se pierda entre sesiones.

**Referencias vivas del estilo correcto:** `studio/tarroshort-mas-caros-historia.html` y `studio/tarroshort-mejor-consola-retro.html` (junio 2026). Cuando dudes, mira esos dos, no un short más antiguo.

---

## Anatomía del short (estándar vigente)

Deck vertical 1080×1920, safe zones `--safe-top:235px --safe-bottom:345px --safe-right:160px --safe-left:60px`. Estructura:

1. **Intro** — TarroBot grande + `RETROTARROS` + título + saludo. Arranca presentándose ("Soy TarroBot...").
2. **N slides de item** — mascota mini + etiqueta + foto + nombre + meta + línea.
3. **Cierre** — TarroBot grande + CTA + gancho al canal.

Paleta: magenta `#FF2E88`, cyan `#00E5FF`, amarillo `#FFD23F`, morado `#2D1B69`, hueso `#F5F0E8`, fondo `#06030f`. Fuentes: Press Start 2P (etiquetas), Orbitron (títulos), Share Tech Mono (texto).

---

## Etiqueta de posición + dato: `item-tag` (NO `rank-badge`)

**Estilo VIGENTE:** una sola etiqueta arriba a la derecha que junta la posición y el dato (precio), con escalada de color según sube el valor.

```css
.item-tag { font-family:'Press Start 2P'; font-size:22px; color:var(--cy); border:2px solid var(--cy);
  padding:12px 18px; letter-spacing:1px; text-shadow:0 0 14px rgba(0,229,255,.5);
  background:rgba(0,229,255,.06); text-align:right; line-height:1.5; }
.item-tag .pos { display:block; font-size:13px; color:rgba(255,255,255,.7); letter-spacing:2px; margin-bottom:6px; }
.item-tag.ye   { color:var(--ye); border-color:var(--ye); text-shadow:0 0 14px rgba(255,210,63,.5); background:rgba(255,210,63,.06); }
.item-tag.gold { color:#FFE57A; border-color:#FFD23F; text-shadow:0 0 18px rgba(255,210,63,.8); background:rgba(255,210,63,.1); box-shadow:0 0 26px rgba(255,210,63,.25); }
```

```html
<div class="item-tag"><span class="pos">PUESTO 9 · CIB</span>US$316</div>
<div class="item-tag ye"><span class="pos">PUESTO 5 · CIB</span>US$442</div>
<div class="item-tag gold"><span class="pos">PUESTO 1</span>US$100.000+</div>
```

- **Cyan** por defecto → **amarillo (`ye`)** a medida que sube el precio → **dorado (`gold`)** para el grial / #1.
- El precio va en el cuerpo del tag; el contexto (`CIB`, etc.) va en el `.pos`.

**Estilo VIEJO (no usar):** `rank-badge` con el `#N` gigante + una caja `.item-price` separada. Es el molde de `nes-top-precios` (marzo). Reemplazado por `item-tag`.

---

## Foto del item: box art real con padding-hack (gotcha crítico)

Para shorts de precios/rankings la foto es **box art real** (regla del canal: siempre la caja, nunca el logo — ver `CLAUDE.md`). Dos `<img>`: fondo blureado + primer plano `object-fit:contain` (se ve COMPLETA).

```css
.item-photo { width:100%; max-width:720px; position:relative; display:block; border-radius:10px;
  overflow:hidden; background:var(--pu); box-shadow:0 0 0 4px rgba(0,229,255,.2), 0 24px 70px rgba(0,0,0,.7); margin:0 auto 24px; }
.item-photo::before { content:""; display:block; padding-top:100%; }   /* cuadrado */
.item-photo img     { position:absolute; inset:0; width:100%; height:100%; display:block; }
.item-photo img.bg  { object-fit:cover; filter:blur(26px) brightness(.5) saturate(1.2); transform:scale(1.15); z-index:0; }
.item-photo img.fg  { object-fit:contain; z-index:1; }
```

```html
<div class="item-photo">
  <img class="bg" src="img/<slug>/skeleton-krew.png" alt="" aria-hidden="true" onerror="this.style.display='none'">
  <img class="fg" src="img/<slug>/skeleton-krew.png" alt="" onerror="this.style.display='none'">
</div>
```

### ⚠️ Gotcha: NO usar `aspect-ratio:1/1` para el cuadrado

El `item-photo` es un flex-item dentro del `.slide` (flex column). En ese contexto, **`aspect-ratio` no genera altura** — el main-size del flex-item se resuelve por contenido, y como los `<img>` colapsan, la foto queda en **altura 0** (se ve solo el borde cyan como una barra fina). Por eso se usa el **padding-hack** (`::before { padding-top:100% }` + imgs `position:absolute`), que es a prueba de balas.

### ⚠️ Gotcha de verificación: verificar a 1080×1920, NO a media resolución

Con las safe zones (235+345 = 580px verticales), si previsualizas el short a media resolución (ej. 540×960) el flex-shrink **aplasta la foto a 0** aunque el CSS esté bien. Es un falso negativo del preview chico. **Siempre verificar a 1080×1920 reales** antes de concluir que algo está roto.

---

## Info que ve el público: letras grandes

Regla de Luis (2026-06-25): con gameplay encima, la letra chica no se lee. Tamaños vigentes en shorts:

- `.item-name` 48px (Orbitron 900) · `.item-meta` 24px (cyan) · `.item-line` 32px.
- Intro `.titulo` ~78px · cierre `.cta` ~70px.

---

## Botón de notas — no debe salir en captura/grabación

Los HTML de estudio llevan capa de notas de teleprompter (tecla `N` + botón clickeable). El botón y su hotzone van con `opacity:0` y clase `.no-capture`; `capture-slides.py` oculta todo `.no-capture`. Las notas NUNCA aparecen en los PNG/render. (Aplica sobre todo a los HTML de episodio; los shorts teaser suelen no llevar notas, pero si las llevan, misma regla.)

---

## Enfoque de contenido: teaser vs top directo

Dos moldes válidos, se elige según el objetivo:

- **Teaser (guardar el grial):** muestra los accesibles y **NO revela el #1**; el cierre tienta con "el grial está en el canal". Genera clic al episodio largo. Es el enfoque elegido para los shorts de precios SEGA (2026-07-20).
- **Top directo (con grial destacado):** muestra el top completo (#4→#1) con el grial en dorado. Auto-contenido y potente. Es el de `mas-caros-historia`.

Decidir con Luis cuál va según el short. Ambos cierran apuntando al canal.

### REGLA — El teaser SIEMPRE empieza en PUESTO 10 y termina en PUESTO 6 (Luis, 2026-07-20)

Los 5 items mostrados en un short teaser se etiquetan **PUESTO 10 → PUESTO 6**, sin excepción, aunque la pauta del episodio solo liste 9 items en su tabla retail CIB (caso Mega Drive y Saturn, que arrancan en #9 en la pauta). El rótulo del short es una convención de display para que toda la serie se vea uniforme — **no** es una re-numeración real del ranking oficial de la pauta (esa sigue siendo la fuente de verdad para el episodio largo). No se inventan items ni precios nuevos para "completar" el 10: se toman los mismos 5 juegos accesibles ya documentados y se corren las etiquetas de posición hacia arriba en 1 si la pauta arrancaba en #9.

---

## Estrategia (por qué hacemos shorts) — embudo, no contenido suelto

Acordado con Luis (2026-06-17):

- El short es **embudo**: (1) tiene que verse completo, (2) que el desconocido haga clic al canal. Cada short cierra apuntando a un episodio largo.
- **Tipos que mejor convierten** (orden de potencia): 1) "¿Cuánto vale hoy?" (precios — nostalgia + shock), 2) ranking polémico (genera comentarios → algoritmo empuja), 3) datos curiosos (serie `datos-*` — funcionan pero NO llevan al canal, se consumen y listo).
- **Música de juegos DESCARTADA como formato de short:** Content ID de YouTube detecta la composición aun en chiptune/covers (protege la melodía, no solo la grabación); Nintendo reclama casi todo. Retrotarros es editorial, no un canal de covers → regalaría monetización y alcance sin retorno.

---

## Render y sync

- **Render MP4:** `python scripts/tarroshort_render.py <slug> --render` → `studio/shorts/<slug>.mp4` (gitignored, va al Drive por sync). TarroBot narra con edge-tts es-CL-CatalinaNeural.
- **Texto hablado con tildes (`data-say`):** el display va SIN tildes (regla del canal), el hablado va aparte CON tildes y pausas para que el TTS pronuncie bien. Ver `CLAUDE.md` sección "TarroShorts de DATOS".
- **Re-render = limpiar audio:** si cambian los textos hablados, borrar `studio/shorts/audio/<slug>/` antes de re-rendir o queda la voz vieja.
- **Sync al Drive:** `scripts/sync-tarrobot-to-drive.ps1` (sube el short MP4 + HTML a `G:\Mi unidad\Studio\tarrobot`). Ver `CLAUDE.md` sección "Workflow obligatorio al cerrar cambios".

---

## Checklist al crear/editar un TarroShort

1. Usar `item-tag` (no `rank-badge`) con escalada cyan → `ye` → `gold`.
2. Box art real con el padding-hack (no `aspect-ratio`).
3. Letras grandes (item-name 48 / meta 24 / line 32).
4. Verificar visualmente **a 1080×1920** (no a media resolución).
5. Definir enfoque teaser vs top directo con Luis.
6. Render MP4, commit, y sync a Drive (ambos scripts si tocaste episodios).
