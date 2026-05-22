# Bundle Claude Studio · Retrotarros

> Paquete autocontenido de documentos para darle todo el contexto del canal **Retrotarros** a un Claude nuevo (proyecto separado, sin acceso al repo principal).

## Quien usa esto

Un Claude que vive en el **proyecto Retrotarros del PC del estudio**, sin acceso al repo en Drive ni a internet. Necesita entender:

- Que es Retrotarros (canal, equipo, tono).
- Convenciones del proyecto (naming, idioma, identidad visual).
- Como se arman las pautas y los HTMLs del estudio.
- Como editar/extender la pauta del episodio en curso.
- Que NO debe hacer (reglas inmutables).

## Como usar este bundle

1. Luis copia esta carpeta entera al proyecto Claude del estudio.
2. Al abrir una conversacion con Claude en el estudio, le dice: **"lee todos los archivos numerados de docs/handoff-claude-studio/ en orden, despues podemos trabajar".**
3. Claude lee los 7 archivos (~15 min de lectura).
4. Listo para iterar pautas sin preguntar contexto basico.

## Indice de archivos

| # | Archivo | Que cubre |
|---|---------|-----------|
| 00 | `00-contexto-canal.md` | Que es Retrotarros, equipo, plan, tono |
| 01 | `01-identidad-visual.md` | Paleta, tipografias, marca, look and feel |
| 02 | `02-convenciones-proyecto.md` | Slugs, naming, git workflow, Drive sync, idioma chileno neutro |
| 03 | `03-estructura-pautas.md` | Como se hacen las pautas (HTML + MD), convencion de slides |
| 04 | `04-componentes-html.md` | Reference de los bloques HTML que se reusan entre pautas |
| 05 | `05-pauta-snes-coleccion.md` | La pauta especifica del episodio actual |
| 06 | `06-discusion-snes-coleccion.md` | Decisiones editoriales detras de la pauta SNES |
| 99 | `99-instrucciones-claude.md` | Lo que Claude debe y NO debe hacer en el estudio |

## Estado del proyecto al exportar este bundle

- Fecha: 2026-05-21
- Episodio en grabacion: **SNES Coleccion** (110 juegos, 9 categorias, 23 slides)
- HTML: `studio/snes-coleccion.html` (60 KB, listo para grabar)
- Pauta MD: `docs/pauta-snes-coleccion.md`
- TarroBot version: v1.2 (instalado en el PC del estudio)

## Si el Claude del estudio te pregunta...

> "¿Donde guardo cambios?"

Si esta editando una pauta del episodio actual: tipicamente sera el `studio/<slug>.html` o el `docs/pauta-<slug>.md`. Si la duda persiste, preguntarle a Luis antes de tocar nada.

> "¿Puedo modificar archivos del bundle?"

NO. El bundle es solo lectura para contexto. Cambios al canal/convenciones se hacen en el repo principal (PC de Luis), no aca.

> "¿Que pasa si me piden crear una pauta nueva desde cero?"

Seguir el modelo de `05-pauta-snes-coleccion.md` y los componentes HTML de `04-componentes-html.md`. Avisar a Luis al terminar que tiene que sincronizar al repo principal.

---

**Generado por:** Claude (sesion del 2026-05-21).
**Para regenerar:** ejecutar el script de export desde el repo principal cuando exista. Por ahora es regeneracion manual.
