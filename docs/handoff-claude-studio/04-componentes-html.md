# 04 · Componentes HTML reutilizables

> Reference rapido de los bloques HTML que se reusan entre pautas. Copiar/pegar y adaptar.

## Header standard

```html
<header>
  <div class="hdr-logo">RETROTARROS</div>
  <div class="hdr-tag">ESTUDIO · {CONTEXTO}</div>
  <div class="hdr-rec"><div class="dot"></div>EN VIVO</div>
</header>
```

CSS:

```css
header {
  position: fixed; top: 0; left: 0; right: 0;
  height: 56px; z-index: 200;
  background: rgba(6, 3, 15, 0.97);
  border-bottom: 2px solid var(--mg);
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 28px;
}
.hdr-logo { font-family: 'Orbitron'; font-weight: 900; font-size: 20px; color: var(--mg); text-shadow: 0 0 14px rgba(255,46,136,.6); letter-spacing: 3px; }
.hdr-tag { font-family: 'Share Tech Mono'; font-size: 12px; color: var(--ye); letter-spacing: 3px; }
.hdr-rec { display: flex; align-items: center; gap: 8px; font-family: 'Press Start 2P'; font-size: 8px; color: var(--mg); }
.dot { width: 10px; height: 10px; background: var(--mg); border-radius: 50%; animation: blink 1.2s ease-in-out infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.15} }
```

## Footer de navegacion + script

```html
<nav class="footer">
  <button class="nav-btn" id="prevBtn">◀ ANTERIOR</button>
  <div class="nav-center">
    <div class="nav-counter" id="counter">01 / 23</div>
    <div class="nav-progress"><div class="bar" id="bar"></div></div>
  </div>
  <div class="nav-hint"><kbd>←</kbd> <kbd>→</kbd> NAVEGAR</div>
  <button class="nav-btn" id="nextBtn">SIGUIENTE ▶</button>
</nav>

<script>
const slides = document.querySelectorAll('.slide');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const counter = document.getElementById('counter');
const bar = document.getElementById('bar');
let current = 0;
const total = slides.length;
function pad(n) { return String(n).padStart(2, '0'); }
function go(i) {
  if (i < 0 || i >= total) return;
  slides[current].classList.remove('active');
  current = i;
  slides[current].classList.add('active');
  prevBtn.disabled = current === 0;
  nextBtn.disabled = current === total - 1;
  counter.textContent = pad(current + 1) + ' / ' + pad(total);
  bar.style.width = ((current + 1) / total * 100) + '%';
}
prevBtn.addEventListener('click', () => go(current - 1));
nextBtn.addEventListener('click', () => go(current + 1));
document.addEventListener('keydown', (e) => {
  if (e.key === 'ArrowRight' || e.key === ' ') { e.preventDefault(); go(current + 1); }
  if (e.key === 'ArrowLeft') { e.preventDefault(); go(current - 1); }
  if (e.key === 'Home') { go(0); }
  if (e.key === 'End') { go(total - 1); }
});
go(0);
</script>
```

## Slide portada

```html
<section class="slide active">
  <span class="slide-num">01</span>
  <div class="portada">
    <div class="ep-tag">GENERACION 4 · 16 BITS · NINTENDO</div>
    <div class="ep-title"><span class="vs">COLECCION</span> SNES</div>
    <div class="ep-sub">UN PANORAMA POR CATEGORIAS</div>
    <div class="ep-count">110 JUEGOS · 9 CANALES</div>
  </div>
</section>
```

CSS:

```css
.portada {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  text-align: center; height: 100%;
}
.portada .ep-tag {
  font-family: 'Press Start 2P'; font-size: 11px; color: var(--cy);
  letter-spacing: 5px; margin-bottom: 22px;
}
.portada .ep-title {
  font-family: 'Orbitron'; font-weight: 900; font-size: 68px;
  letter-spacing: 1.5px; line-height: 1.05; color: #fff;
  margin-bottom: 18px; max-width: 1100px;
}
.portada .ep-title .vs {
  color: var(--mg); text-shadow: 0 0 22px rgba(255,46,136,.55);
}
.portada .ep-sub {
  font-family: 'Share Tech Mono'; font-size: 18px; color: var(--ye);
  letter-spacing: 4px; margin-bottom: 30px;
}
.portada .ep-count {
  font-family: 'Press Start 2P'; font-size: 16px; color: var(--mg);
  letter-spacing: 4px; text-shadow: 0 0 14px rgba(255,46,136,.5);
}
```

## Slide divider (separador grande)

```html
<section class="slide">
  <span class="slide-num">XX</span>
  <div class="divider">
    <div class="pre cy">PROXIMA COLECCION</div>
    <div class="title cy" style="font-size:58px;">SEGUIMOS</div>
    <div class="sub">Comentanos cual fue tu favorita. Suscribete para no perderte el panorama N64.</div>
  </div>
</section>
```

Variantes de color: `.pre.mg / .ye`, `.title.mg / .ye`. Por default fondo oscuro, texto blanco.

CSS:

```css
.divider {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  text-align: center; height: 100%;
}
.divider .pre {
  font-family: 'Press Start 2P'; font-size: 11px; letter-spacing: 6px; margin-bottom: 24px;
}
.divider .pre.cy { color: var(--cy); }
.divider .pre.mg { color: var(--mg); }
.divider .pre.ye { color: var(--ye); }
.divider .title {
  font-family: 'Orbitron'; font-weight: 900; font-size: 72px;
  letter-spacing: 2px; line-height: 1; color: #fff; margin-bottom: 22px;
}
.divider .title.cy { color: var(--cy); text-shadow: 0 0 22px rgba(0,229,255,.5); }
.divider .title.mg { color: var(--mg); text-shadow: 0 0 22px rgba(255,46,136,.55); }
.divider .sub {
  font-family: 'Share Tech Mono'; font-size: 18px; color: rgba(255,255,255,.7);
  letter-spacing: 2px; max-width: 800px; line-height: 1.6;
}
```

## Slide indice / menu consola

```html
<section class="slide">
  <span class="slide-num">02</span>
  <div class="idx">
    <div class="idx-title">SELECCIONA TU CATEGORIA</div>
    <div class="idx-list">
      <div class="idx-item active">
        <span class="idx-cursor">▶</span>
        <span class="idx-num">01</span>
        <span>PLATAFORMAS <span class="idx-dots">·····································</span></span>
        <span class="idx-count">32 TITULOS</span>
      </div>
      <!-- repetir para cada item -->
    </div>
    <div class="idx-total">─── 110 JUEGOS ───</div>
    <div class="idx-hint">▶ PRESS START TO BEGIN PANORAMA</div>
  </div>
</section>
```

Detalles importantes:
- Solo UN item lleva `.active` (cursor amarillo visible).
- Los `idx-dots` son puntos `·` repetidos para llenar la linea hasta el contador.
- Total y hint cierran el bloque.

## TarroVision (TV virtual) standalone

```html
<div class="tarrovision">
  <div class="tv-controls-top">
    <span class="tv-led"></span>
    <span class="tv-brand">TARROVISION</span>
    <span class="tv-channel">CH 01</span>
  </div>
  <div class="tv-screen">
    <div class="tv-screen-inner">
      <!-- REGLA: las TarroVisiones siempre quedan VACIAS en el HTML del canal.
           El namebox de abajo (tv-namebox) es el unico texto guia para edicion. -->
      <div class="tv-noscreen"></div>
      <!-- O reemplazar por video real (solo si se renderiza con video embebido):
      <video src="../assets/{slug}/super-mario-world.mp4" autoplay loop muted></video>
      -->
    </div>
  </div>
  <div class="tv-controls-bottom">
    <div class="tv-knob"></div>
    <div class="tv-knob cy"></div>
    <div class="tv-speaker"></div>
  </div>
</div>
```

Para el namebox debajo (titulo de la joya):

```html
<div class="tv-namebox ye">
  <div class="tv-title">SUPER MARIO WORLD</div>
  <div class="tv-meta">1990 · NINTENDO</div>
</div>
```

Variantes: `.tv-namebox` (cyan default) o `.tv-namebox.ye` (amarillo).

## Slide paneo (TV grande con video paneando)

```html
<section class="slide">
  <span class="slide-num">03</span>
  <div class="slide-paneo">
    <div class="paneo-banner">
      <div class="paneo-cat-num">CAT 01/09</div>
      <div class="paneo-cat-name">P L A T A F O R M A S</div>
      <div class="paneo-cat-count">32 TITULOS</div>
    </div>
    <div class="paneo-tv-wrap">
      <!-- TarroVision aqui, ocupa el espacio restante -->
      <div class="tarrovision">...</div>
    </div>
  </div>
</section>
```

CSS clave:

```css
.slide-paneo {
  display: grid; grid-template-rows: auto 1fr;
  height: 100%; gap: 14px; padding: 0 20px;
  max-width: 1500px; margin: 0 auto;
}
.paneo-banner {
  display: grid; grid-template-columns: auto 1fr auto;
  align-items: center; gap: 22px; padding: 14px 24px;
  border: 1px solid var(--cy); background: rgba(0,229,255,.05);
  box-shadow: 0 0 22px rgba(0,229,255,.18);
}
.paneo-cat-num {
  font-family: 'Press Start 2P'; font-size: 11px; color: var(--cy);
  letter-spacing: 3px; padding: 6px 12px;
  border: 1px solid var(--cy); background: rgba(0,229,255,.08);
}
.paneo-cat-name {
  font-family: 'Orbitron'; font-weight: 900; font-size: 38px;
  color: #fff; letter-spacing: 4px; text-align: center;
  text-shadow: 0 0 18px rgba(255,255,255,.18);
}
.paneo-cat-count {
  font-family: 'Press Start 2P'; font-size: 13px; color: var(--ye);
  letter-spacing: 2px; text-shadow: 0 0 10px rgba(255,210,63,.4);
}
```

## Slide triple (3 TarroVisiones lado a lado)

```html
<section class="slide slide-triple">
  <span class="slide-num">04</span>
  <div class="slide-triple-inner">
    <div class="triple-head">
      <div class="tv-block-label">PLATAFORMAS · 3 JOYAS DESTACADAS</div>
    </div>
    <div class="triple-grid">
      <div class="triple-cell">
        <div class="tv-fit"><div class="tarrovision">...</div></div>
        <div class="tv-namebox ye">
          <div class="tv-title">SUPER MARIO WORLD</div>
          <div class="tv-meta">1990 · NINTENDO</div>
        </div>
      </div>
      <!-- repetir 2 veces mas -->
    </div>
  </div>
</section>
```

CSS clave: `triple-grid` es grid de 3 columnas. `tv-fit` hace que la TarroVision se ajuste al espacio container.

## Numbers cards (cards con numero grande)

```html
<div class="numbers-grid">
  <div class="num-card mg"><h3>TOTAL</h3><span class="big">110</span><p>juegos en la coleccion</p></div>
  <div class="num-card cy"><h3>CATEGORIAS</h3><span class="big">9</span><p>generos cubiertos</p></div>
  <div class="num-card ye"><h3>JOYAS</h3><span class="big">27</span><p>destacadas en gameplay</p></div>
</div>
```

Variantes: `.num-card.mg` `.num-card.cy` `.num-card.ye`. Cambia el color del borde, la h3 y el numero.

CSS:

```css
.numbers-grid {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px;
  max-width: 1100px; margin: 40px auto 0;
}
.num-card {
  background: var(--card-bg); border: 2px solid; border-radius: 4px;
  padding: 28px 24px; text-align: center;
}
.num-card.mg { border-color: var(--mg); box-shadow: 0 0 22px rgba(255,46,136,.18); }
.num-card.cy { border-color: var(--cy); box-shadow: 0 0 22px rgba(0,229,255,.18); }
.num-card.ye { border-color: var(--ye); box-shadow: 0 0 22px rgba(255,210,63,.18); }
.num-card h3 {
  font-family: 'Press Start 2P'; font-size: 10px;
  letter-spacing: 2px; margin-bottom: 14px;
}
.num-card.mg h3 { color: var(--mg); }
.num-card.cy h3 { color: var(--cy); }
.num-card.ye h3 { color: var(--ye); }
.num-card .big {
  font-family: 'Orbitron'; font-weight: 900; font-size: 56px;
  letter-spacing: 2px; display: block; margin: 14px 0 12px;
}
.num-card.mg .big { color: var(--mg); text-shadow: 0 0 18px rgba(255,46,136,.4); }
.num-card.cy .big { color: var(--cy); text-shadow: 0 0 18px rgba(0,229,255,.4); }
.num-card.ye .big { color: var(--ye); text-shadow: 0 0 18px rgba(255,210,63,.4); }
.num-card p {
  font-family: 'Share Tech Mono'; font-size: 13px;
  color: rgba(255,255,255,.7); letter-spacing: 1px;
}
```

## Slide titulo + h1/h2 (titulos de seccion intermedios)

```html
<section class="slide">
  <span class="slide-num">XX</span>
  <h1>RAREZAS</h1>
  <h2 class="mg">PERIFERICOS DE LA COLECCION</h2>
  <!-- contenido aqui (numbers-grid, lista, etc) -->
</section>
```

CSS:

```css
.slide h1 {
  font-family: 'Press Start 2P'; font-size: 13px;
  color: var(--ye); letter-spacing: 4px; margin-bottom: 6px;
  border-left: 4px solid var(--ye); padding-left: 16px;
}
.slide h2 {
  font-family: 'Orbitron'; font-weight: 900; font-size: 38px;
  color: #fff; letter-spacing: 1px; margin: 8px 0 24px 20px; line-height: 1.05;
}
.slide h2.mg { color: var(--mg); text-shadow: 0 0 18px rgba(255,46,136,.45); }
```

## Reglas comunes

- **`.slide-num`** siempre arriba a la derecha, opacidad baja (es un marcador de slide para debug, casi no se ve).
- **Slide activo** solo uno a la vez (`.active`).
- **`.deck`** envuelve todos los slides, position fixed entre header y footer.
- **No scroll vertical**: cada slide debe caber en pantalla. Si no cabe, partir en 2 slides.

## Reglas de contenido visual

- Sin tildes en cualquier texto visible.
- Sin emojis modernos. Solo iconos retro: ▶ ◀ · ─.
- Letter-spacing siempre presente en titulos y labels.
- Glow/shadow con el mismo color del texto.
- Si dudas, repetir el patron de un slide existente de SNES o N64.
