# RETROTARROS — Pauta de episodio especial

*Nostalgia + Juegos + Música*

**Top 10 Gatos Mas Recordados del Retrogaming**

*Especial · Mes del Gato (Dia Internacional del Gato, 8 de agosto) · Multi-consola*

Documento de trabajo · Luis Balbrigame & Koko

---

## Proposito de esta pauta

Segundo episodio especial de fecha conmemorativa del canal, replicando el formato piloto de **Top 10 Glorias Navales Retro** (21 de mayo). Toma 10 personajes gato (y un bobcat honorario) del catalogo retro y los presenta como pacientes de un consultorio veterinario ficticio, con su **FICHA CLINICA VETERINARIA** oficial. Tono **humoristico-divulgativo**, no academico.

Atado al **Dia Internacional del Gato (8 de agosto)** pero enmarcado como "mes del gato" en vez de fecha exacta, ya que la produccion/publicacion cae despues del 8.

**Tono editorial:** humor cariñoso, mismo molde que Glorias Navales. Cada personaje es presentado con seriedad clinica fingida (como si Luis fuera el veterinario de cabecera del consultorio). Koko aporta reacciones genuinas.

---

## Concepto del episodio

Formato presentacion visual con HTML del estudio (`studio/specials/retro-dia-del-gato.html`), generado con el nuevo generador reusable `scripts/special_deck.py` (clonado del HTML de Glorias Navales, primer uso del patron "especial" como generador en vez de HTML a mano):

- 14 slides navegables del 01 al 14.
- Portada "Top 10 Gatos Mas Recordados del Retrogaming" con paleta canal, palabra "GATOS" destacada en magenta.
- 10 slides de personajes #10 → #1, cada uno con:
  - Box art / artwork del juego (`.cart`)
  - TarroVision al lado con el clip del personaje en accion
  - Nombre del personaje + rol + meta (consola/año/editor/dato extra)
  - **Bloque "FICHA CLINICA"** (o "PODIO FELINO" en #2-#3, "DIRECTOR DEL CONSULTORIO" en #1) con diagnostico/antecedentes/temperamento con humor
- Analisis + cierre.

**Duracion objetivo:** 18-22 minutos, igual que el piloto naval.

---

## El Top 10 Gatos Mas Recordados del Retrogaming

| # | Personaje | Juego | Consola | Año | Editor/Dev |
|---|-----------|-------|---------|-----|------------|
| **1** | Toro Inoue | Doko Demo Issyo | PlayStation | 1999 | Bomber Express / Sony |
| **2** | Cait Sith | Final Fantasy VII | PlayStation | 1997 | Square |
| **3** | Meowth | Pokemon Rojo y Azul | Game Boy | 1996 (JP) / 1998 (occ.) | Game Freak / Nintendo |
| **4** | Garfield | Garfield: Caught in the Act | Genesis | 1995 | Sega |
| **5** | Hello Kitty | Hello Kitty World | Famicom | 1992 | Character Soft (Sanrio) |
| **6** | Sylvester | Sylvester and Tweety in Cagey Capers | Genesis | 1994 | Time Warner Interactive |
| **7** | Tom | Tom & Jerry: The Ultimate Game of Cat and Mouse! | NES | 1991 | Software Creations |
| **8** | Felix the Cat | Felix the Cat | NES | 1992 | Hudson Soft |
| **9** | Willy the Cat | Rockin' Kats | NES | 1991 | Atlus |
| **10** | Bubsy | Bubsy in Claws Encounters of the Furred Kind | SNES / Genesis | 1993 | Accolade |

**Lectura del ranking:**

- **No es ranking de calidad de juego.** Es ranking de **cuanto marco el personaje al imaginario retro** (fama + asociacion con el gaming especificamente).
- El criterio de ordenamiento prioriza cuanto el personaje esta ligado AL GAMING por sobre su fama general fuera de los videojuegos: por eso Toro Inoue (mascota nativa de PlayStation) cierra en el #1 por sobre Garfield o Hello Kitty, que son mas famosos en general pero llegaron al gaming como licencia secundaria.
- **Candidatos descartados en el proceso de seleccion** (documentado para referencia futura, no repetir sin revision):
  - **Big the Cat** (Sonic Adventure, Dreamcast 1998) — YA aparecio en Glorias Navales (#9, "Pescador zen"). Regla del canal: no vuelve a aparecer en contenido nuevo.
  - **Blinx: The Time Sweeper** (Xbox, 2002) — descartado por Luis por sentirse "muy nuevo" frente al resto de la lista (8/16-bit + PS1).
  - **Cheshire Cat** (candidato inicial, supuesto juego "Capcom NES 1990") — **descartado en investigacion**, no existe tal juego documentado. Reemplazado por Willy the Cat (Rockin' Kats), que si tiene respaldo solido.

---

## Estructura del episodio (18-22 min)

### Bloque 1 · Cold open (0:00 – 0:30)

Plano cerrado de cartucho random (idealmente Rockin' Kats o Felix the Cat). Luis con tono de veterinario fingido:

> *"Agosto es el mes del gato -el 8 se celebra el Dia Internacional del Gato-, y en Retrotarros tambien queremos hacerles su chequeo anual a los felinos que marcaron el catalogo retro. Bienvenidos al consultorio. Top 10 Gatos Mas Recordados del Retrogaming."*

Cut al logo Retrotarros.

### Bloque 2 · Setup (0:30 – 1:30)

- Luis explica el concepto: "no es top de mejores juegos con gatos, es top de gatos que mas marcaron el imaginario retro."
- Aclara el tono: "cada uno tiene su FICHA CLINICA VETERINARIA oficial."
- Koko: "ya entiendo, vamos a hablar como si fueramos del consultorio veterinario del barrio."

### Bloque 3 · Recorrido #10 → #1 (1:30 – 18:00)

16:30 min para 10 personajes = ~1:40 por personaje.

**Estructura por slide:**
- Luis lee la FICHA CLINICA con tono profesional fingido.
- Koko reacciona desde lo natural.
- 1:30-1:45 por item base, 2:30 para top 3.

**Items donde NO ahorrar tiempo:**
- **#1 Toro Inoue** — desplegar bien por que un gato de un juego de chat se volvio mascota no oficial de PlayStation en Japon.
- **#5 Hello Kitty** — el gancho de "oficialmente no es un gato" merece su beat completo.
- **#2 Cait Sith** — la mecanica del muñeco operado a control remoto + auto-destruccion es rara y vale la pena explicarla bien.

**Items para acortar:**
- **#10 Bubsy** — chiste rapido de "el que todos quieren olvidar", fluir al #9.
- **#7 Tom** — cumplir, no estirar (todo el mundo conoce a Tom y Jerry).

### Bloque 4 · Balance + cierre (18:00 – 22:00)

- Recap visual de los 10.
- Cita: "Eso es todo por hoy en el consultorio. Salud para los diez."
- Cierre con CTA: "Si te falto algun gato retro, escribilo en los comentarios."

---

## Reglas de ejecucion en vivo

### Ritmo

- **Cada personaje max 1:45**. El tono clinico solemne pierde fuerza si se estira.
- **Los del top 3** pueden ir a 2:30 cada uno.
- **Importante: Luis debe leer la ficha clinica con seriedad fingida.** Koko hace de contrapeso espontaneo.

### Lo que NO se dice

- No hacer chistes sobre maltrato animal real, ni siquiera en broma (linea roja del formato).
- No comparar con otros canales que hayan hecho un top similar.
- No repetir a Big the Cat (ver seccion de candidatos descartados).

### Lo que SI se dice

- "FICHA CLINICA" / "diagnostico" / "temperamento" / "antecedentes" como mantra recurrente.
- Bromas de consultorio: "sin alta medica", "pronostico reservado", "segunda opinion".

---

## Material visual necesario

### Para grabar (antes del episodio)

- [ ] 10 clips de gameplay de cada personaje (8-12 seg cada uno).
- [ ] Box arts de los 10 juegos — **ya conseguidos y verificados** en `studio/specials/img/retro-dia-del-gato/` (Wikipedia REST summary + LaunchBox Games Database para los casos donde Wikipedia traia imagen incorrecta: Hello Kitty World, Toro Inoue, Tom & Jerry, Meowth).
- [ ] Banda sonora de fondo (sugerencia: algo ligero/juguetón, no invasivo).

## Estado de la pauta

| Item | Estado |
|------|--------|
| Generador reusable (`scripts/special_deck.py`) | ✓ Nuevo, clonado de retro-glorias-navales.html |
| HTML estudio (`studio/specials/retro-dia-del-gato.html`) | ✓ Cerrado para grabar (14 slides) |
| Capturas (`studio/specials/captures/retro-dia-del-gato/`) | ✓ 14 PNGs |
| Imagenes (`studio/specials/img/retro-dia-del-gato/`) | ✓ 10 box arts verificados |
| Pauta MD (este archivo) | ✓ |
| Discusion MD (`docs/discusiones/discusion-retro-dia-del-gato.md`) | ✓ |
| Descripcion YouTube (`docs/descripciones/descripcion-retro-dia-del-gato.md`) | ✓ |

---

## Notas finales

- Segundo episodio del formato "especial de fecha/tema", confirmando que el molde de Glorias Navales es reutilizable. El generador `scripts/special_deck.py` queda disponible para el tercero (candidatos ya sugeridos en la pauta naval: 18 de Septiembre, Dia del Trabajador, Halloween).
- El tono "documento oficial con humor" es la firma del formato — cambia el nombre del documento por tema (Hoja de Servicios → Ficha Clinica), pero la estructura y el registro se mantienen.
- Datos verificados via busqueda cruzada (Wikipedia + fuentes secundarias) para cada uno de los 10 personajes — varios candidatos iniciales tenian datos incorrectos de memoria (Cheshire Cat sin juego real, Tom & Jerry con año/desarrollador equivocado, Sylvester con plataforma equivocada, Garfield con plataforma SNES inexistente) y fueron corregidos antes de cerrar la pauta.

---

**Ultima actualizacion:** 2026-08-17
**Slug:** `retro-dia-del-gato`
**HTML asociado:** `studio/specials/retro-dia-del-gato.html`
**Discusion:** `docs/discusiones/discusion-retro-dia-del-gato.md`
