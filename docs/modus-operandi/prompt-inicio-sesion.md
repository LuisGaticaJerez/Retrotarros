# Prompt de inicio de sesión (2026-10-22)

Para pegar en una sesión limpia con `D:\Recursos Retrotarros\repo` como carpeta de trabajo. Cuando cambie el estado, actualizar `HANDOFF.md`; este archivo es solo el arranque de esa fecha.

```
Hola. Seguimos con Retrotarros. Esta sesión tiene el repo del canal como carpeta de trabajo (D:\Recursos Retrotarros\repo, rama master).

Antes de hacer cualquier cosa, lee en este orden:
1. HANDOFF.md (estado actual y pendientes)
2. CLAUDE.md (reglas del proyecto)
3. docs/modus-operandi/flujo-rankings.md (recetas para Top Precios e Infravalorados, y trampas del shell)

Luego revisa con git status y git log origin/master..HEAD y avísame cómo estamos.

Estado al cierre de la sesión anterior (2026-10-22):
- Todo está pusheado a origin/master hasta a0d22a2. Los syncs rápidos a Drive también están hechos.
- Quedó hecho Mega Drive Infravalorados (Shining Force II #1): HTML, 10 box arts, 14 capturas, pauta, discusión y kit de YouTube.
- TarroDL se separó del repo del canal. Vive en D:\Recursos Retrotarros\TarroTools\TarroDL (repo privado github.com/LuisGaticaJerez/TarroDL). La carpeta TarroTools agrupa las herramientas que yo te indique que se separen.
- El driver .cache/gen_mega_drive_infravalorados.py está sin versionar (la carpeta .cache es gitignored), igual que los de SNES y PS1.

Reglas que no se negocian:
- Háblame en español chileno neutro con tuteo, sin voseo.
- No hagas push ni syncs a Drive sin mi "dale" explícito. Los commits locales sí los haces tú, sin Co-Authored-By.
- Antes de tocar un ranking, revisa si está publicado o grabado en data/youtube/estado-canal.json y docs/canal/inventario-contenido.md. Si está publicado, pregúntame antes.
- En los Infravalorados pesa más la crítica que el olvido, y van sin precios.
- Trabajamos un ranking por sesión. Para publicar usa el sync rápido: sync-to-drive.ps1 -Episodios <slug> y sync-tarrobot-to-drive.ps1 -Rapido.
- Los box arts de Infravalorados van en studio/rankings/infravalorados/img/<slug>/ (no en studio/img).

Pendientes:
1. Limpiar tools/tarrodl: quedan .venv, build y dist locales sin versionar (están ignorados por git). Puedes borrarlos con mi visto bueno.
2. Auditar los Top Precios publicados que no se han revisado: NES, N64, Master System y Game Boy figuran publicados, así que pregúntame antes de tocarlos. Atari 2600 no aparece con video de precios en estado-canal.json: confirma en el inventario si está grabado antes de auditarlo. En PS1 mirar Einhänder y Castlevania Chronicles contra el #10 (USD 350).
3. Más Infravalorados: GameCube y PS2 (SNES, PS1 y Mega Drive ya están hechos). Receta en flujo-rankings.md sección 2. Con consolas sin Metacritic usa los 3 niveles de fuerza de la crítica, como en Mega Drive.
4. Confirmar conmigo: Wipeout XL #1 y Xenogears #10 en PS1; Tetris Attack #1 en SNES; Shining Force II #1 en Mega Drive (alternativa: Phantasy Star II). Además, en Mega Drive: Thunder Force III (quién lo distribuyó en NA) y Sword of Vermilion (crítica mixta en retrospectiva).
5. Mover otras herramientas a TarroTools cuando yo te indique cuáles.

Para empezar: confírmame el estado de git y dime qué pendiente atacamos primero.
```
