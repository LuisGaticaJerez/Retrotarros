# Discusion editorial · `retro-dia-del-gato`

> Documento de decisiones que se tomaron al armar el episodio. Lectura
> obligatoria antes de grabar para no abrir debates resueltos.

---

## 1. Por que un especial de "mes del gato"

Segundo especial de fecha/tema del canal, despues de Glorias Navales (21 de mayo). A diferencia del naval, esta fecha (Dia Internacional del Gato, 8 de agosto) no es chilena ni patria — es un tema global, mas liviano, que sirve para probar si el formato "especial de fecha" funciona tambien fuera de efemerides nacionales.

- **Pro:** tema universal, sin riesgo de sonar irreverente con una fecha solemne (a diferencia del 21 de mayo).
- **Pro:** contenido de gatos tiene tiro largo en YouTube todo el año, no solo la semana de la fecha.
- **Contra:** publicacion cae despues del 8 de agosto real (se decidio el tema el 17). Mitigacion: encuadrar como "mes del gato" en vez de atarlo al dia exacto — sigue siendo agosto.

---

## 2. Por que humor veterinario y no un top serio

Mismo patron que Glorias Navales: el canal no es un canal de curiosidades academicas, es humor cariñoso. La "FICHA CLINICA VETERINARIA" cumple la misma funcion que la "HOJA DE SERVICIOS" naval — transponer a cada personaje a un rol burocratico-profesional (aqui, paciente de consultorio) para que el chiste tenga estructura repetible episodio a episodio.

No hay riesgo de tono como el naval (no hay fecha solemne que respetar), asi que el humor puede ser mas libre. Unica linea roja: nunca burlarse de maltrato animal real, ni en chiste.

---

## 3. Criterios de seleccion del top 10

Filtros aplicados:
1. **Personaje gato (o felino cercano) con juego propio real y documentado** — no vale un cameo menor sin protagonismo.
2. **Cubre era retro** (NES/Famicom a PS1, no posterior).
3. **Reconocible** para audiencia amplia, no solo nicho.
4. **Dato verificable** — cero personajes/juegos inventados de memoria.

Proceso real de seleccion (documentado porque cambio varias veces):

- **Big the Cat** (Sonic Adventure, Dreamcast) — propuesto inicialmente, **descartado por Luis**: ya aparecio en Glorias Navales (#9), regla del canal es que no vuelve a repetirse.
- **Blinx: The Time Sweeper** (Xbox, 2002) — propuesto como reemplazo, **descartado por Luis** por sentirse "muy nuevo" (6ta gen) frente al resto de la lista, que es puro 8/16-bit + PS1.
- **Cheshire Cat** (candidato inicial, supuesto "Alice in Wonderland, Capcom NES 1990") — **descartado en la fase de investigacion**: ese juego no existe documentado en ninguna fuente. Reemplazado por **Willy the Cat** (Rockin' Kats, NES 1991, Atlus), que si tiene respaldo solido (Wikipedia + multiples fuentes secundarias).
- **Hello Kitty** — propuesta como reemplazo final de Blinx, **aprobada por Luis** explicitamente ("metamos a hello kitty").

Otros datos corregidos durante la investigacion (varios candidatos SI se mantuvieron en la lista pero con datos que estaban mal de memoria y se corrigieron con fuentes):
- **Tom** — se penso "NES 1989" de memoria; el juego real es *Tom & Jerry: The Ultimate Game of Cat and Mouse!* (NES, **1991**, Software Creations/Hi-Tech Expressions).
- **Sylvester** — se penso "SNES/Genesis 1995"; el juego real (*Cagey Capers*) es **solo Genesis, 1994** (Alexandria/Time Warner Interactive) — hubo una version SNES planeada por TecMagik pero se **cancelo**.
- **Garfield** — se penso "Genesis/SNES 1995"; no existe version SNES confirmada, es **Genesis/Game Gear/Windows** unicamente (Sega, animaciones de Paws Inc).

---

## 4. Por que Toro Inoue al #1

El criterio de ordenamiento NO es fama general — es cuanto el personaje esta ligado especificamente al mundo gaming (por sobre su fama en TV/comics/merchandising).

| Candidato | Argumentos pro | Argumentos contra |
|-----------|----------------|---------------------|
| **Toro Inoue** | Nacio EN un videojuego, se volvio mascota no oficial de una consola entera (PlayStation Japon), sin vida previa fuera del gaming | Poco conocido en occidente/Latam fuera del circulo gamer duro |
| **Garfield** | Fama masiva, reconocible instantaneo | Su juego es secundario a su fama de comic/TV, no "nacio" gamer |
| **Hello Kitty** | Fama masiva + gancho de dato curioso fuerte | Igual que Garfield: la marca es previa al gaming |

Eleccion: **Toro Inoue** porque es el unico candidato de la lista cuya fama ENTERA proviene del gaming — nacio en un juego de PlayStation y se convirtio en mascota de la marca. Es el cierre logico de un top que se llama "mas recordados DEL RETROGAMING", no "mas famosos en general."

---

## 5. Estructura narrativa por bloques

Mismo ritmo que Glorias Navales: sucesion de skits cortos (~1:40 c/u), top 3 puede estirarse a 2:30. El #1 Toro Inoue necesita el beat mas largo porque requiere mas contexto (quien es, por que es mascota "no oficial", que es Doko Demo Issyo) que el resto, que la audiencia ya conoce de entrada.

---

## 6. Decision sobre TarroBot

Misma recomendacion que el naval: **usar TarroBot** para leer las fichas clinicas si se quiere el efecto "voz oficial fingiendo seriedad." Si no, Luis lee directo del slide (visible en pantalla).

Pendiente: generar `studio/pautas/retro-dia-del-gato.tarrobot.json` si se decide usar TarroBot (no generado en esta sesion, no fue pedido explicito).

---

## 7. Cita del cold open · texto sugerido

> *"Agosto es el mes del gato -el 8 se celebra el Dia Internacional del Gato-, y en Retrotarros tambien queremos hacerles su chequeo anual a los felinos que marcaron el catalogo retro. Bienvenidos al consultorio. Top 10 Gatos Mas Recordados del Retrogaming."*

**Notas:**
- Tono profesional-fingido desde la primera linea, no hace falta escalar como el naval (no hay fecha solemne de fondo).
- "Bienvenidos al consultorio" es el quiebre que instala el gag recurrente.

---

## 8. Reglas inmutables aplicadas

- **TarroVisiones VACIAS** en el HTML (regla canal) — el gameplay se inserta en edicion.
- **Sin tildes** en HTML visible.
- **Chileno neutro con tuteo** en esta pauta + discusion (tildes OK en chat/docs internos).
- **Box art real siempre** — se corrigieron 4 imagenes que Wikipedia entrego mal (Hello Kitty World traia la caja de "Balloon Kid" por error del articulo, Toro Inoue traia solo el logo en japones sin el personaje) via LaunchBox Games Database.

---

## 9. Material a grabar (checklist resumido)

- [ ] Clips gameplay de los 10 personajes en accion (8-12s c/u).
- [ ] Musica de fondo (sugerencia: algo ligero, no invasivo — el tono ya lo pone el texto).
- [ ] (Opcional) MP3s pre-generados de TarroBot leyendo las 10 fichas clinicas.

---

## 10. Generador reusable — nota tecnica

Este es el primer special que usa un **generador Python reusable** (`scripts/special_deck.py`) en vez de HTML escrito a mano (que fue como se hizo Glorias Navales). El generador clona 1:1 el CSS/JS del naval y parametriza:
- El nombre del "documento oficial" por rango (`doc_label`, `doc_label_podio`, `doc_label_top`).
- Los 10 items (nombre, rol, juego, consola, año, editor, ficha, box art, paleta de color).
- Los slides de intro/analisis/cierre.

Para el proximo especial de fecha (candidatos ya sugeridos en la pauta naval: 18 de septiembre, Halloween, etc.), el driver es un archivo nuevo en `.cache/gen_special_<slug>.py` siguiendo el patron de `.cache/gen_special_retro-dia-del-gato.py` — no hace falta tocar el generador salvo que se necesite un layout de slide distinto.

---

*Discusion cerrada · 2026-08-17 · Luis Balbrigame*
