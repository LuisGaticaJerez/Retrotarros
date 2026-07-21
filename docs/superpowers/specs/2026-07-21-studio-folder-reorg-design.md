# Reorganización de `studio/` en carpetas unificadas — diseño aprobado

> Diseñado con Luis 2026-07-21. Objetivo: hoy `studio/` tiene 47 episodios largos +
> 32 TarroShorts todos sueltos en la raíz (identificables solo por el prefijo del
> nombre de archivo). Se reorganizan en carpetas por tipo, tanto en el repo como en
> el Drive (`G:\Mi unidad\Studio\`), para que sea fácil encontrar "todos los top de
> precios" sin tener que leer 79 nombres de archivo.

## Alcance

- **Incluye:** los 47 episodios largos + los 32 TarroShorts (`tarroshort-*.html`).
  Decisión de Luis: reorganizar todo junto, no solo los episodios largos.
- **No incluye:** `studio/resenas/` (ya vive en su propia carpeta desde ayer, se
  mantiene igual — se convierte en una categoría más al mismo nivel que las demás).
  `studio/shorts/` (carpeta de MP4 renderizados, nombre distinto, no se toca).
  `studio/pautas/`, `studio/melodias/`, `studio/branding/`, templates (`_template-*`).

## Taxonomía final

### Episodios largos → `studio/<categoria>/[<subcategoria>/]<slug>.html`

| Carpeta | Slugs (47 total) |
|---|---|
| `rankings/top-mundial/` | dreamcast, master-system, mega-drive, n64, nes, psvita, saturn, snes `-top-mundial` (8) |
| `rankings/top-precios/` | mismas 8 consolas `-top-precios` (8) |
| `rankings/retrotarros-vs-mundo/` | n64, psvita `-retrotarros-vs-mundo` (2) |
| `colecciones/` | n64, nes, psvita, snes `-coleccion` (4) |
| `sagas/` | donkey-kong, kirby, mario, mega-man, metal-gear, metroid, mortal-kombat, resident-evil, smash-bros, sonic, street-fighter, zelda (12, prefijo `saga-`) |
| `specials/` | retro-cuadrilla-frio, retro-dia-trabajador, retro-glorias-navales, retro-padres-gamer (4) |
| `curaduria-n64/` | n64-hardware-raro, n64-joyas-ocultas, n64-kirkhope-rare, n64-nintendo-vs-playstation, n64-no-latam (5) |
| `archivo-koko/` | n64-archivo-koko, psvita-archivo-koko (2) |
| `teasers/` | teaser-n64-top-precios, teaser-snes-top-mundial (2) |
| `abriendo-el-tarro/` | vacía por ahora (solo vive el template en la raíz) |

`resenas/` ya existe tal cual, queda como categoría hermana de las de arriba (no se mueve).

### TarroShorts → `studio/shorts-html/<categoria>/[<subcategoria>/]tarroshort-*.html`

Nombre `shorts-html` (no `shorts/`, que ya existe y guarda los MP4 renderizados —
nombres distintos para no confundir).

| Carpeta | Slugs (32 total) |
|---|---|
| `rankings/top-mundial/` | tarroshort-n64-top-mundial, -nes-top-mundial, -snes-top-mundial (3) |
| `rankings/top-precios/` | tarroshort-dreamcast/-master-system/-mega-drive/-n64/-nes/-saturn/-snes `-top-precios` (7) |
| `colecciones/` | tarroshort-n64-coleccion, -nes-coleccion, -snes-coleccion (3) |
| `specials/` | tarroshort-retro-glorias-navales, -retro-padres-gamer (2) |
| `datos/` | los 15 `tarroshort-datos-*` (no derivan de un episodio) |
| `cross-console/` | tarroshort-mas-caros-historia, tarroshort-mejor-consola-retro (2) |

## Cómo se mueven los assets (la parte que puede romper todo si se hace mal)

**Regla:** cada `.html` se mueve JUNTO con su propia carpeta `img/<slug>/` y
`captures/<slug>/` como una unidad — no se separan en un árbol de imágenes aparte.
Ejemplo concreto:

```
ANTES:
  studio/n64-top-precios.html          (<img src="img/n64-top-precios/xxx.jpg">)
  studio/img/n64-top-precios/*.jpg
  studio/captures/n64-top-precios/*.png

DESPUES:
  studio/rankings/top-precios/n64-top-precios.html   (MISMO <img src="img/n64-top-precios/xxx.jpg">)
  studio/rankings/top-precios/img/n64-top-precios/*.jpg
  studio/rankings/top-precios/captures/n64-top-precios/*.png
```

**Por qué esto y no un árbol único `studio/img/<categoria>/.../<slug>/`:** si el
árbol de imágenes se separara del HTML, cada archivo movido necesitaría que se le
reescriba el `<img src="...">` con la cantidad exacta de `../` según su profundidad
(distinta por categoría: `rankings/top-precios/` son 2 niveles, `colecciones/` es 1).
Eso es exactamente el tipo de bug que rompió las cajas de las Reseñas ayer. Moviendo
`img/` y `captures/` como sub-carpetas del mismo lugar donde queda el HTML, el
`src="img/<slug>/..."` sigue siendo válido tal cual — cero strings que tocar dentro
de cada archivo, cero riesgo de ruta relativa mal calculada.

**Caso especial — TarroShorts que reusan cajas del episodio padre:** algunos
`tarroshort-*.html` no tienen su propio `img/<slug>/`, sino que referencian el
`img/<slug-del-episodio>/` del episodio del que derivan (mismo box art reciclado).
Antes de mover cada TarroShort hay que revisar su HTML para saber si tiene imágenes
propias o si apunta a las de su episodio — y si apunta afuera, copiar esas imágenes
también dentro de su nueva carpeta (duplicar, no symlink — Drive no sincroniza
symlinks de Windows de forma confiable) para no dejar una referencia rota.

## Qué más hay que actualizar (blast radius real)

1. **10 scripts** que asumen `studio/*.html` plano o `studio/img/<slug>/` plano:
   `capture-slides.py`, `coleccion_deck.py`, `saga_deck.py`, `tarrobot.py`,
   `tarroshort_datos.py`, `tarroshort_render.py`, `thumbnail.py`, `top_deck.py`,
   `sync-tarrobot-to-drive.ps1`, `sync-to-drive.ps1`.
2. **Los DOS scripts de sync a Drive, con foco especial** (pedido explícito de
   Luis): deben reflejar la nueva estructura de carpetas para que la carpeta de
   Drive quede como espejo exacto, y el chequeo de verificación de
   `sync-to-drive.ps1` (que hoy falla ruidoso si un episodio no llegó) debe seguir
   cubriendo el 100% de los archivos con las rutas nuevas.
3. **~81 referencias en `docs/*.md` y `docs/arcos/*.md`** a `studio/<slug>.html` —
   se actualizan con un mapeo slug→ruta-nueva aplicado en bloque.
4. **Drive (`G:\Mi unidad\Studio\`)**: mismo árbol de carpetas, movido después de
   que el repo + sync scripts estén verificados funcionando — nunca antes (el
   repo es la fuente de verdad; si algo sale mal en el repo, no se propaga a Drive).

## Orden de ejecución (para minimizar riesgo)

1. Escribir un script de migración en Python (`.cache/migrate_studio_folders.py`,
   gitignored — es one-shot, no un generador reutilizable) que aplique el mapeo
   completo vía `git mv` (preserva historial) para HTML + `img/` + `captures/` de
   cada slug.
2. Correr el script, revisar `git status` que nada quedó huérfano.
3. Actualizar los 10 scripts con las rutas nuevas.
4. **Verificación automática total:** abrir las 79 páginas movidas con Playwright y
   confirmar que cada `<img>` cargó (no solo una muestra — todas, como se hizo con
   las 5 Reseñas). Cualquier imagen rota se corrige antes de seguir.
5. Actualizar los ~81 links en `docs/`.
6. Commit + push.
7. Correr `sync-to-drive.ps1` y `sync-tarrobot-to-drive.ps1` actualizados — esto
   mueve/recrea la estructura en Drive. Verificar en el Drive real (no asumir).
8. Avisar a Luis con el resumen de qué carpetas quedaron dónde.

## Riesgos aceptados

- Historial de git: `git mv` preserva el historial de cada archivo individual, pero
  el diff del commit va a ser grande (79 archivos movidos + 10 scripts + 81 docs).
  Un solo commit grande, no varios — más fácil de revisar y revertir si algo falla.
- Mientras el Drive se reorganiza, si Luis tiene alguna carpeta de `Studio\` abierta
  en el Explorador o algún HTML abierto en el navegador, puede ver rutas rotas
  momentáneamente hasta que Drive Desktop termine de sincronizar. No hay forma de
  evitar esto del todo — se avisa antes de correr el paso 7.
