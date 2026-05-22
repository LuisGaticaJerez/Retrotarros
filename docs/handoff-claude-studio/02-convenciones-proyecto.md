# 02 · Convenciones del proyecto Retrotarros

## Estructura del repo

```
repo-retrotarros/
├── CLAUDE.md                 # instrucciones globales para Claude (en repo principal)
├── HANDOFF.md                # estado canal (en repo principal)
├── docs/
│   ├── pauta-{slug}.md       # pauta de cada episodio
│   ├── discusion-{slug}.md   # decisiones editoriales del episodio
│   ├── arcos/                # tableros por generacion (n64.md, snes.md, etc)
│   ├── briefings-compositores.md
│   ├── guiones-shorts.md
│   └── handoff-claude-studio/  # ESTE BUNDLE (sub-repo de contexto)
├── studio/
│   ├── {slug}.html           # HTML del episodio (lo que se proyecta en grabacion)
│   ├── _template-*.html      # templates de TarroBot (no editar)
│   ├── pautas/               # JSON pautas TarroBot + MP3 precargados
│   └── melodias/             # MIDIs por consola
├── data/
│   └── tarrobot-database.json
├── scripts/                  # scripts Python (TarroBot, sync, etc)
├── installers/               # instaladores TarroBot Studio
└── assets/                   # imagenes y recursos
```

## Convencion de slug

El **slug** es el identificador unico de un episodio. Reglas:

- Todo minusculas.
- Separador: guion (-).
- Estructura: `{consola}-{tema}` o `{tema}` si es transversal.
- Sin tildes, sin caracteres especiales.

Ejemplos validos:

- `n64-ranking`
- `n64-hardware-raro`
- `n64-no-latam`
- `snes-top-mundial`
- `snes-top-precios`
- `snes-coleccion`
- `kirkhope-rare-briefing`

## Convencion de pautas

Cada episodio largo tiene **3 archivos con el mismo slug**:

1. **`studio/{slug}.html`** — la presentacion visual que se ve en pantalla durante la grabacion (es lo que el espectador ve en el video final). Slides navegables con flechas izq/der.
2. **`docs/pauta-{slug}.md`** — el guion/pauta del episodio: estructura por bloques, voz off, transiciones, lista de items.
3. **`docs/discusion-{slug}.md`** — el "detras de escena": por que se eligieron esos items, descartados, riesgos, anecdotas para Luis y Koko.

### Cuando crear los 3 archivos

- Si es un **episodio largo (>10 min)**: SI, los 3.
- Si es un **short (<60 seg)**: NO, se documenta en `docs/guiones-shorts.md`.
- Si es un **briefing** (material de apoyo): NO, se documenta en `docs/briefings-*.md`.

## Convencion de arcos

Un MD por generacion en `docs/arcos/{generacion}.md`. Es el **tablero de control** del arco:

- Lista de episodios planeados.
- Estado de cada uno (idea / pauta cerrada / grabado / publicado).
- Notas de coordinacion entre episodios.

Ejemplo: `docs/arcos/n64.md` tiene los 7 episodios del arco N64.

## Idioma · Reglas inmutables

**Chileno neutro con tuteo.** Aplica a TODOS los outputs (chat, codigo, comments, commits, pautas, descripciones, titulos):

### Usar (chileno OK)

- tú / tienes / quieres / dime / puedes / sabes / mira / fíjate / espérate
- Marcas chilenas suaves: "po", "te tinca", "déjanos", "suscríbete"

### NO usar (PROHIBIDO)

- Voseo argentino: `vos sabés / tenés / querés / decime / pegás / navegás / armás / bajás / sos / podés / sabés / decís / fijate (voseo)`
- Pronombre `vos`, `che`, `boludo`
- Mexicanismos: `órale / güey / chido / ándale`
- Españolismos: `vale` (sentido sí), `tío / guay / molar`

### Si Claude se equivoca

Si Luis señala que sono argentino:
1. Disculparse breve.
2. Reescribir el ultimo mensaje correcto en chileno neutro.
3. Seguir aplicando la regla.

### Excepcion para HTMLs y assets visuales del canal

**SIN tildes ortograficas** en TODO el contenido visible del canal (titulos, nameboxes, etiquetas, subtitulos en pantalla). Esto es regla de proyecto.

**Excepcion:** los textos para TTS de TarroBot SI llevan tildes (para que el sintetizador pronuncie bien). Pero TarroBot es proyecto aparte, lo aclaro por completitud.

## Git workflow

### Quien hace que

- **Luis es PM/CTO**: aprueba decisiones, da el OK, revisa.
- **Claude ejecuta** commits, push, scripts directamente. Pide confirmacion SOLO para:
  - Operaciones remotas a otros repos.
  - Operaciones destructivas (force push, reset hard).
  - Cambios de schema en produccion (no aplica al canal).

### Convencion de commits

Formato:

```
{categoria}: {descripcion corta en imperativo, chileno neutro}

Detalle opcional en parrafos si el commit es grande.
Bullets con cosas importantes.
```

Categorias tipicas:
- `pauta:` cambios en una pauta especifica
- `studio:` HTMLs del estudio
- `tarrobot:` codigo o configs de TarroBot
- `docs:` documentacion
- `scripts:` scripts utilitarios
- `fix:` correccion de bug
- `arco:` cambios en el tablero de un arco

### Ramas

- `master` (no `main`): rama principal.
- No usar feature branches para pautas — directo a master.
- Feature branches OK para refactors grandes de scripts.

### Commits + emojis

NO usar emojis en mensajes de commit. NO usar `Co-Authored-By` ni firmas automatizadas. Mantener todo limpio y sobrio.

## Drive sync

El estudio sincroniza ciertos archivos al Drive del usuario en `G:\Mi unidad\Studio\` (Windows). Scripts:

- `scripts/sync-to-drive.ps1` — sincroniza pautas + HTMLs + DOCX generados.
- `scripts/sync-tarrobot-to-drive.ps1` — sincroniza solo lo de TarroBot.

NO ejecutar estos scripts desde el Claude del estudio. Son responsabilidad del repo principal en el PC de Luis.

## Naming de archivos en general

- Lower-case con guiones (`-`).
- Sin espacios.
- Extension al final segun tipo (`.md`, `.html`, `.json`, etc).
- Si es un asset multimedia: incluir slug del episodio en el nombre (`snes-coleccion-portada.png`).

## Configuracion local

Si Claude del estudio necesita variables de entorno:
- `RETROTARROS_REPO` apunta a la ruta del repo sincronizado (Drive o local).
- `ANTHROPIC_API_KEY` para llamadas LLM (TarroBot la usa).

NO commitear nunca:
- `.env` o `.env.local`
- API keys
- Credenciales de cualquier servicio

Si Claude detecta que alguien intenta commitear secrets: **rechazar y avisar a Luis inmediatamente**.
