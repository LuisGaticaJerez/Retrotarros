# 03 · Estructura de pautas

## Anatomia de una pauta del canal

Cada episodio largo tiene **3 archivos** (ver `02-convenciones-proyecto.md`). Aca explicamos cada uno.

---

## 1. HTML del estudio (`studio/{slug}.html`)

Es lo que se proyecta en pantalla durante la grabacion. **Es el principal output visual del video.**

### Caracteristicas tecnicas

- Archivo HTML standalone (todo embebido: CSS + JS + assets).
- Sin dependencias externas mas que Google Fonts y los videos/imagenes en `../assets/`.
- Funciona offline cuando los assets ya estan en disco.
- Navegacion con flechas izq/der del teclado.
- Atajos: Home (primer slide), End (ultimo slide).
- Cada slide es un `<section class="slide">`. Solo uno tiene `.active` en cada momento.
- Footer con boton anterior/siguiente + contador + barra de progreso.

### Estructura general

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>RETROTARROS · {Nombre episodio}</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap');

    :root {
      --mg: #FF2E88; --cy: #00E5FF; --ye: #FFD23F;
      --pu: #2D1B69; --bo: #F5F0E8; --dk: #06030f;
      --card-bg: rgba(12, 6, 32, 0.92);
    }

    /* ...estilos compartidos: header, footer, animaciones, scanlines... */
    /* ...estilos especificos del episodio... */
  </style>
</head>
<body>

  <header>
    <div class="hdr-logo">RETROTARROS</div>
    <div class="hdr-tag">ESTUDIO · {CONTEXTO EPISODIO}</div>
    <div class="hdr-rec"><div class="dot"></div>EN VIVO</div>
  </header>

  <div class="deck" id="deck">

    <!-- 01 PORTADA -->
    <section class="slide active">
      <span class="slide-num">01</span>
      <div class="portada">...</div>
    </section>

    <!-- 02 ... N -->
    <!-- slides intermedios segun el formato del episodio -->

    <!-- N CIERRE -->
    <section class="slide">
      <span class="slide-num">N</span>
      <div class="divider">...</div>
    </section>

  </div>

  <nav class="footer">
    <button class="nav-btn" id="prevBtn">◀ ANTERIOR</button>
    <div class="nav-center">
      <div class="nav-counter" id="counter">01 / N</div>
      <div class="nav-progress"><div class="bar" id="bar"></div></div>
    </div>
    <div class="nav-hint"><kbd>←</kbd> <kbd>→</kbd> NAVEGAR</div>
    <button class="nav-btn" id="nextBtn">SIGUIENTE ▶</button>
  </nav>

  <script>
    /* navegacion standard, copiar del template */
  </script>

</body>
</html>
```

### Tipos de slides recurrentes

Ver `04-componentes-html.md` para el HTML especifico de cada tipo.

- **Portada**: titulo grande + tag de generacion + subtitulo.
- **Indice / menu**: lista de categorias o items, estilo "PRESS START" de consola.
- **Divider**: separador grande entre bloques con titulo destacado.
- **Item / juego destacado**: layout 2 columnas (TV virtual + datos).
- **Slide paneo**: 1 TV grande con video paneando.
- **Slide triple**: 3 TVs en grilla con joyas destacadas.
- **Numbers cards**: 2-3 cards con numeros grandes (totales, stats).
- **Cierre**: texto centrado + CTA suscribete.

---

## 2. Pauta MD (`docs/pauta-{slug}.md`)

Es el guion del episodio. Lo que Luis y Koko leen antes de grabar para tener la estructura clara.

### Estructura tipica

```markdown
# RETROTARROS — Pauta de episodio largo

*Nostalgia + Juegos + Música*

**{Titulo del episodio}**

*{Generacion} · {Consola} · {Parte X de Y si aplica}*

Documento de trabajo · Luis Balbrigame & Koko

---

## Proposito de esta pauta

{Por que este episodio. Que cubre. Que NO cubre. Decisiones editoriales.}

---

## Concepto del episodio

{Como se va a ver. Cuantos slides. Que formato (ranking? coleccion? duelo? entrevista?). Duracion objetivo.}

---

## El contenido (tabla o lista de items)

{Tabla con los juegos/items + datos curados.}

---

## Estructura del episodio (X-Y min)

### Bloque 1 · Cold open (0:00 – 0:30)
### Bloque 2 · Setup (0:30 – 1:30)
### Bloque 3 · {cuerpo del episodio} (1:30 – 17:00)
### Bloque 4 · Cierre (17:00 – 20:00)

---

## Reglas de ejecucion en vivo

{Ritmo, lo que NO se dice, lo que SI se dice.}

---

## Material visual necesario

### Para grabar (antes del episodio)
### Para el HTML (post)

---

## Estado de la pauta

| Item | Estado |
|------|--------|
| HTML estudio | ✓ / ☐ |
| Material grabado | ✓ / ☐ |
| Pauta MD | ✓ |
| Discusion MD | ✓ / ☐ |

---

**Ultima actualizacion:** YYYY-MM-DD
**Slug:** `{slug}`
**HTML asociado:** `studio/{slug}.html`
**Discusion:** `docs/discusion-{slug}.md`
```

### Reglas para escribir pautas

- **No copiar texto literal del HTML.** El HTML es lo visual. El MD es lo narrativo.
- **Bloques con tiempos** (`0:00 – 0:30`). Ayuda al ritmo.
- **Distincion clara entre Luis y Koko**: que dice cada uno.
- **Lista de material visual** al final, marcable con checkboxes.
- **Tabla de estado** al final con items marcados.

---

## 3. Discusion MD (`docs/discusion-{slug}.md`)

Es el "detras de escena". Por que se tomaron las decisiones, descartados, anecdotas para tener a mano, riesgos.

### Estructura tipica

```markdown
# Discusion · {Titulo del episodio}

---

## Por que este episodio y por que ahora

{Contexto del momento del canal. Por que ahora y no antes/despues.}

---

## Por que X items y no otros

{Iteraciones de la lista. Que se descarto y por que.}

---

## Decisiones de items destacados

### Categoria X · Las decisiones

- **Item 1**: razon de inclusion.
- **Item 2**: razon.
- **Item 3**: razon.

Descartados: ... porque ...

---

## Anecdotas y momentos clave

### Para Luis
### Para Koko
### Compartidas

---

## Cosas que cambiamos hoy (YYYY-MM-DD)

{Si se hicieron cambios respecto a una version anterior.}

---

## Riesgos y como mitigarlos

| Riesgo | Mitigacion |
|--------|------------|

---

**Ultima actualizacion:** YYYY-MM-DD
**Pauta asociada:** `docs/pauta-{slug}.md`
**HTML:** `studio/{slug}.html`
```

### Reglas para escribir discusion

- **Justificacion clara**: por que un item esta y otro no.
- **Anecdotas separadas** para cada presentador.
- **Tabla de riesgos** ayuda mucho en el dia de grabacion.
- **Honesto sobre debilidades**: si la categoria tiene riesgos (monotonia, items debiles), decirlo.

---

## Flujo de trabajo tipico

1. Luis trae idea de episodio → discusion verbal con Claude.
2. Claude crea `docs/discusion-{slug}.md` con propuesta de lista.
3. Iteran: Luis aprueba/rechaza items, Claude actualiza.
4. Cuando la lista esta cerrada → Claude crea `docs/pauta-{slug}.md` con estructura.
5. Luis revisa pauta MD.
6. Claude crea `studio/{slug}.html` con todos los slides.
7. Luis abre el HTML en navegador, valida visualmente.
8. Iteran sobre el HTML (ajustes de copy, tamaños, orden de slides).
9. Cuando esta cerrado: marcar en `docs/arcos/{generacion}.md` como "✓ Cerrado para grabar".
10. Grabacion → post produccion.

## Templates de TarroBot — NO TOCAR

Los archivos `studio/_template-tarrobot-*.html` son del sistema TarroBot, NO son pautas del canal. NO modificarlos desde el proyecto del estudio. Si necesitan cambios, eso vive en el repo principal.
