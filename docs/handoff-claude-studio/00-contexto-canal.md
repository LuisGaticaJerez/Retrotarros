# 00 · Contexto del canal Retrotarros

## Que es Retrotarros

Canal de YouTube sobre **videojuegos retro** (hasta generacion 5: NES, SNES, Genesis, N64, etc). Mezcla:

- **Nostalgia** (anecdotas personales, recuerdos)
- **Juegos** (curaduria, datos curiosos, rankings, coleccion fisica)
- **Musica** (chiptunes, OSTs, eventualmente cubrir cosas en bateria)

## Equipo

- **Luis Balbrigame** (Luis Gatica Jerez) — productor, presentador, coleccionista. Es el dueño del estudio y del repo. Email: luis.gatica.jerez@gmail.com.
- **Koko** — copresentador, reacciones, anecdotas personales. Tiene experiencia de gamer toda la vida pero NO sabe los datos curiosos curados — los descubre en vivo.

**Dinamica:** Luis cura y presenta. Koko reacciona y aporta lo personal. La tension entre "datos verificables" (Luis) y "yo lo jugue, lo recuerdo asi" (Koko) es el motor del canal.

## Tono editorial

- **No academico**: no es museum-curator. Es conversacion entre dos coleccionistas amigos.
- **Verificable**: cada dato debe tener fuente o ser verificable. Nada inventado.
- **Latam-centrico**: contexto chileno + latinoamericano. Mencion casual a precios en pesos, llegada de consolas a la region, etc.
- **Sin postureo**: ni "yo era hardcore" ni "el oldschool de verdad sabe". Honestidad: lo que no sabemos, lo decimos.
- **Cero clickbait barato**: titulos con gancho, OK. Mentirosos, no.

## Idioma

**Chileno neutro con tuteo.** Reglas estrictas:

- Usar: tu/tienes/sabes/dime/puedes/quieres/mira.
- Marcas chilenas suaves OK: "po", "te tinca", "déjanos", "suscríbete".
- PROHIBIDO voseo argentino: `vos sabes`, `tenés`, `decime`, `pegás`, `navegás`, `armás`, `bajás`, `che`, `sos`, `andá`.
- Sin mexicanismos: ni `órale`, `güey`, `chido`.
- Sin españolismos: ni `vale`, `tío`, `guay`, `molar`.

Esto aplica a TODOS los textos: chat con Claude, contenido del canal, codigo (comments + commits).

## Plan general del canal

- **Pre-lanzamiento**: ahora (2026-05). Acumular 4-6 episodios cerrados antes de lanzar publicamente.
- **Arcos por generacion**: bloques de 7-12 episodios por consola. Empezamos por **N64** (3 cerrados, 4 mas en cola) y **SNES** (en curso, este es el primero).
- **Series paralelas**: shorts por lane (Luis vs Koko), briefings de compositores, OST en bateria.
- **Indie Lat**: bloque mensual sobre developers indie latinoamericanos.

## Identidad

- **Nombre canal**: Retrotarros (no separar, no espacio).
- **Dominio**: retrotarros.cl (registrado).
- **Handles redes**: `@retrotarros` (reservados pero no en uso publico todavia).
- **Estetica**: synthwave/arcade retro. Magenta neon + cyan + amarillo + fondo violeta profundo.

## TarroBot

Mascota del canal. Es un **personaje IA** que aparece dentro de una **TV virtual** y reacciona en vivo durante las grabaciones. Cuenta datos curiosos, opina, toca melodias MIDI con sonido SNES, controla las camaras de OBS por voz.

Esta integrado al estudio de grabacion via:
- Servidor local FastAPI en `localhost:8765`
- Panel de control desde el celular (`http://<ip-pc>:8765/control`)
- Browser Source en OBS para que aparezca en pantalla durante el video

**Version actual:** v1.2 (instalado en el PC del estudio).

Si te piden cambios en TarroBot, no los hagas desde el proyecto del estudio — eso vive en el repo principal. Avisar a Luis para que lo trabaje en su PC.

## Decisiones cerradas (NO discutir)

- Nombre del canal: **Retrotarros**.
- Convencion de pautas: 3 archivos por episodio con mismo slug (HTML + pauta MD + discusion MD).
- Convencion de arcos: 1 MD por generacion como tablero de control.
- Identidad visual base: paleta synthwave (ver `01-identidad-visual.md`).
- TarroBot es la mascota oficial. Aparece en todos los episodios largos.

## Decisiones abiertas (puedes proponer)

- Logo final (3 opciones en evaluacion).
- Orden de generaciones despues de N64/SNES (Genesis vs NES vs PSX).
- Primer dev para seccion Indie Lat.
