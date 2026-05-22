# 01 · Identidad visual Retrotarros

## Paleta de colores

Definida como CSS custom properties. Usar SIEMPRE estos tokens, no colores hardcodeados:

```css
:root {
  --mg: #FF2E88;   /* MAGENTA NEON - color principal/marca */
  --cy: #00E5FF;   /* CYAN NEON - acentos, info, links */
  --ye: #FFD23F;   /* AMARILLO - destacados, names, joyas */
  --pu: #2D1B69;   /* VIOLETA PROFUNDO - fondo secundario */
  --bo: #F5F0E8;   /* HUESO/CREMA - texto principal */
  --dk: #06030f;   /* OSCURO CASI NEGRO - fondo principal */
  --card-bg: rgba(12, 6, 32, 0.92);  /* fondo de cards */
}
```

### Cuando usar cada color

| Color | Token | Uso |
|-------|-------|-----|
| Magenta | `--mg` | Logo, marca, REC LED, numeros 01 02 etc, titulos "fuertes" |
| Cyan | `--cy` | Banners de categoria, info secundaria, bordes neutros, "HINT" en footer |
| Amarillo | `--ye` | Nameboxes con titulos de juegos, "EN VIVO" en header, joyas destacadas |
| Violeta `pu` | `--pu` | Fondo secundario, gradientes |
| Hueso | `--bo` | Texto general body |
| Oscuro `dk` | `--dk` | Fondo de slides, fondo body |

### Variante DOCX (documentos exportados)

Para documentos profesionales exportados via pandoc (en `studio/templates/reference.docx`):

- Magenta oscuro: `#B8175E`
- Teal oscuro: `#006B7A`
- Gris oscuro: `#333`

Mas sobrios que la paleta de pantalla.

## Tipografias

3 familias de Google Fonts. Importar SIEMPRE las 3 con este link al inicio del `<style>`:

```css
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap');
```

### Uso por tipografia

| Familia | Uso | Tamaño tipico |
|---------|-----|---------------|
| **Press Start 2P** | Etiquetas pequeñas, labels, numeros de slide, "EN VIVO", tags. Estetica 8-bit muy reconocible. | 8-16px |
| **Orbitron** (700/900) | Titulos grandes, nombres de juegos en nameboxes, headlines. Sci-fi futurista. | 32-72px |
| **Share Tech Mono** | Body, subtitulos, metadata, info secundaria. Tipografia monoespaciada limpia. | 11-18px |

### Letter-spacing

Casi todos los textos llevan letter-spacing de **2-5px**. Especialmente los Press Start 2P y los subtitulos. Da la sensacion "consola retro".

```css
font-family: 'Press Start 2P'; letter-spacing: 4px;
```

## Efectos visuales recurrentes

### Glow / text-shadow

Los textos de marca tienen `text-shadow` con el mismo color:

```css
/* Glow magenta */
text-shadow: 0 0 14px rgba(255, 46, 136, 0.6);

/* Glow cyan */
text-shadow: 0 0 14px rgba(0, 229, 255, 0.4);

/* Glow amarillo */
text-shadow: 0 0 18px rgba(255, 210, 63, 0.5);
```

### Scanlines (lineas CRT)

Todo el body tiene grid de scanlines sutil:

```css
body {
  background-image:
    radial-gradient(ellipse 100% 50% at 50% -5%, rgba(255,46,136,.12) 0%, transparent 65%),
    repeating-linear-gradient(0deg, transparent 0px, transparent 39px, rgba(255,255,255,.014) 39px, rgba(255,255,255,.014) 40px),
    repeating-linear-gradient(90deg, transparent 0px, transparent 39px, rgba(255,255,255,.014) 39px, rgba(255,255,255,.014) 40px);
}
```

### Animacion blink (parpadeo)

Para LEDs y cursores en menus tipo "PRESS START":

```css
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.15} }
.dot { animation: blink 1.2s ease-in-out infinite; }
```

## Componentes visuales fundamentales

### Header con marca

```html
<header>
  <div class="hdr-logo">RETROTARROS</div>
  <div class="hdr-tag">ESTUDIO · COLECCION SNES</div>
  <div class="hdr-rec"><div class="dot"></div>EN VIVO</div>
</header>
```

- Logo magenta neon a la izquierda.
- Tag amarillo al centro con el contexto del episodio.
- Indicador EN VIVO con dot parpadeante a la derecha.
- Borde inferior magenta de 2px.

### TarroVision (TV virtual)

Es el componente mas representativo. Es una **TV CRT estilizada** que envuelve un video/imagen.

```html
<div class="tarrovision">
  <div class="tv-controls-top">
    <span class="tv-led"></span>
    <span class="tv-brand">TARROVISION</span>
    <span class="tv-channel">CH 01</span>
  </div>
  <div class="tv-screen">
    <div class="tv-screen-inner">
      <!-- aqui va el video o imagen -->
    </div>
  </div>
  <div class="tv-controls-bottom">
    <div class="tv-knob"></div>
    <div class="tv-knob cy"></div>
    <div class="tv-speaker"></div>
  </div>
</div>
```

Estructura: marco gris oscuro con LED magenta, brand amarillo, channel cyan, pantalla CRT con scanlines + glow, perillas y speaker abajo.

### Footer de navegacion

```html
<nav class="footer">
  <button class="nav-btn" id="prevBtn">◀ ANTERIOR</button>
  <div class="nav-center">
    <div class="nav-counter">01 / 23</div>
    <div class="nav-progress"><div class="bar"></div></div>
  </div>
  <div class="nav-hint"><kbd>←</kbd> <kbd>→</kbd> NAVEGAR</div>
  <button class="nav-btn" id="nextBtn">SIGUIENTE ▶</button>
</nav>
```

- Botones cyan con borde, hover invierte colores.
- Contador magenta + barra de progreso gradiente magenta→cyan.
- Hint a la derecha con kbd amarillo.

## Reglas inmutables del look

1. **Sin tildes en HTMLs y assets visuales del canal.** Esto es una regla del canal Retrotarros: TODO el contenido visible (titulos, nameboxes, etiquetas, subtitulos) va SIN tildes ortograficas. *Excepcion: textos para TTS de TarroBot, que SI llevan tildes para que el sintetizador pronuncie bien.*
2. **No agregar emojis al canal.** El estilo es texto + iconografia retro (▶ ◀ etc). No usar emojis modernos en titulos, nameboxes ni descripciones.
3. **No usar colores fuera de la paleta.** Si necesitas un color nuevo, proponerlo a Luis primero.
4. **Mantener consistencia de fuentes.** No introducir tipografias nuevas sin razon.
5. **Letter-spacing presente.** Es parte del lenguaje visual.

## Logo

Tres opciones en evaluacion (no decidido aun):
- Neon puro: "RETROTARROS" en Orbitron magenta con glow.
- Lockup dos pisos: "RETRO" arriba en Orbitron + "TARROS" abajo mas pequeño en Share Tech.
- Texto + icono: nombre + cartucho estilizado.

Por ahora en HTML usamos solo el texto "RETROTARROS" en `.hdr-logo`.

## Material fotografico de referencia

Cuando se necesite imagen real:
- Box arts: buscar en MobyGames, IGDB o LaunchBox.
- Capturas gameplay: emuladores propios (no copiar de YouTube).
- Lomos de cartuchos: idealmente fotos del estudio fisico de Luis.

NO usar:
- Imagenes con marcas de agua de terceros.
- Renders fan-made sin atribucion.
- AI-generated que parezca real.
