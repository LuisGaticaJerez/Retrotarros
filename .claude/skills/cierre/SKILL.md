---
name: cierre
description: Ritual de cierre de un ranking o tanda de trabajo del canal Retrotarros. Mide el contexto, deja HANDOFF.md, bitacora, arco y memoria al dia, hace el commit local, ofrece push y syncs a Drive (solo con el dale de Luis) y abre la sesion siguiente con un resumen. Usar al terminar un ranking, al llegar a 300.000 tokens de contexto, o cuando Luis diga "cierra", "cierre" o "/cierre".
---

# Cierre de sesion (Retrotarros)

Objetivo: que lo decidido quede escrito en archivos y la proxima sesion arranque sin perder nada. Se habla en chileno neutro con tuteo, sin voseo. Sin emojis ni guiones largos en commits y archivos de docs.

## Pasos (en orden)

1. **Medir el contexto.** Llamar a `mcp__ccd_session_mgmt__get_usage` (cargarla con ToolSearch si esta diferida). Reportar a Luis: tokens usados, porcentaje, y los limites del plan (5 horas y semanal). Criterio de `HANDOFF.md`: menos de 300.000 sigue el siguiente ranking aqui; 300.000 a 400.000 se cierra el ranking en curso y se abre sesion nueva; mas de 400.000 se abre sesion nueva despues de cerrar. Si el limite de 5 horas pasa de 85 %, avisar.
2. **Revisar el estado de git.** `git status -sb` y `git log origin/master..HEAD --oneline`. Informar commits sin pushear. En un worktree `.git` es un archivo: escribir el mensaje del commit en un archivo del scratchpad y usar `git commit -F`.
3. **Dejar los archivos al dia:**
   - `HANDOFF.md`: estado actual, pendientes (quitar lo hecho), decisiones vigentes y fecha de "Ultima actualizacion". Es el unico archivo de "estado"; no duplicar estado en otros.
   - `docs/modus-operandi/bitacora-decisiones.md`: una entrada fechada solo si hubo una decision o regla nueva (con el porque).
   - `docs/modus-operandi/flujo-rankings.md`: solo si cambio una receta o aparecio una trampa nueva.
   - `docs/arcos/<consola>.md`: estado del episodio y proximo paso del arco.
   - `docs/canal/inventario-contenido.md`: solo si cambio el estado publicado o programado de algo.
4. **Memoria.** Si Luis dio una regla o preferencia nueva, guardarla en `C:\Users\Balbr\.claude\projects\D--Recursos-Retrotarros-repo\memory\` (un archivo por hecho, con el indice en `MEMORY.md`). Antes de crear, buscar si ya existe uno que cubra el tema y actualizarlo en vez de duplicar. No guardar lo que ya esta en el repo.
5. **Commit local.** Sin `Co-Authored-By` (regla de Luis del canal). Mensaje corto con prefijo (`feat(rankings):`, `docs(estudio):`).
6. **Push y syncs.** Preguntar a Luis. Solo con su "dale":
   - Llevar la rama a master (`git merge --ff-only <rama>` en el repo principal) y `git push origin master`.
   - Si se capturaron slides en un worktree, copiar `studio/**/captures/<slug>` al repo principal (estan en `.gitignore`).
   - `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/sync-to-drive.ps1 -Episodios <slug>` y `... scripts/sync-tarrobot-to-drive.ps1 -Rapido`, ejecutados desde el repo principal.
7. **Abrir la sesion siguiente** (si corresponde por el criterio de contexto o si Luis lo pide). **Nombre de la sesion (Luis, 2026-10-22): `Canal Retrotarros · AAAA-MM-DD · <tarea>`**, por ejemplo `Canal Retrotarros · 2026-10-22 · Xbox Top Mundial` (maximo 60 caracteres; usar `name` corto tipo `retrotarros-xbox-top-mundial`). Tambien renombrar la sesion actual con `set_session_title` al cerrarla, para que la barra lateral quede ordenada por fecha. Usar `mcp__ccd_session__start_session` con `initiation` "user_asked" (Luis autorizo el 2026-10-22 que Claude cree las sesiones), `context` "fresh", un `prompt` que nombre la tarea y el slug, y un `background` con las reglas vigentes y que lea `HANDOFF.md`, `CLAUDE.md` y `docs/modus-operandi/flujo-rankings.md` antes de actuar. Decir que no haga push ni syncs sin el dale de Luis.
8. **Sesiones viejas.** Con `list_sessions` revisar las que ya terminaron y quedaron sin trabajo pendiente. Proponer a Luis cuales borrar, con una linea de que contienen; **nunca borrar (ni archivar) sin su visto bueno explicito, y solo tras revisar que no tengan cambios sin commitear ni ramas sin mergear.**

## Reglas fijas

- Nunca push, force push, ni syncs a Drive sin el "dale" de Luis en el mismo turno.
- No tocar un ranking publicado o grabado sin preguntar: ver `data/youtube/estado-canal.json` y `docs/canal/inventario-contenido.md`.
- Al cerrar un episodio nuevo, pegar el kit de YouTube en el chat ademas de dejarlo en el `.md`.
- Terminar con un resumen corto: que quedo hecho, que no se verifico, y el SHA del ultimo commit.
