============================================================
TARROBOT STUDIO · INSTRUCCIONES RAPIDAS
============================================================

QUE ES:
TarroBot es la mascota del canal Retrotarros. Vive dentro de
una TV virtual y reacciona en vivo cuando lo invocas con voz
o desde el celu, contando datos curiosos retro.

============================================================
PRIMERA VEZ (instalar)
============================================================

1. Asegurate de tener conexion a internet.

2. Doble click en  install.bat
   El instalador va a:
   - Instalar Python 3.12 si no esta (silencioso)
   - Crear entorno virtual en esta carpeta
   - Instalar dependencias (Whisper, FastAPI, edge-tts, anthropic)
   - Descargar ffmpeg portable
   - Pedirte la API key de Anthropic
   - Crear acceso directo en escritorio
   Tarda 5 a 10 minutos depende de tu conexion.

3. Cuando te pida la API key, pegala (la generaste en
   https://console.anthropic.com/settings/keys
   con nombre tipo "tarrobot-studio").

4. Cuando termine, vas a tener un acceso directo TarroBot
   en el escritorio. Listo.

============================================================
USO DIARIO
============================================================

Doble click en TarroBot (del escritorio o en TarroBot.bat).

Modo NORMAL (TarroBot.bat):
   - Sin ventana cmd visible
   - Aparece un icono en la bandeja del sistema (al lado del reloj)
   - Click derecho en el icono:
       * Abrir TarroBot (TV)        -> Chrome en kiosk con TarroBot
       * Abrir panel control        -> Chrome con el panel
       * Abrir overlay (OBS)        -> URL para OBS Browser Source
       * IP local: 192.168.x.x:8765 -> info
       * Panel desde el celu        -> abre la URL en tu browser
       * Salir TarroBot             -> cierra todo

Modo DEBUG (TarroBot-debug.bat):
   - Ventana cmd visible con todos los logs del server y Whisper
   - Usalo si algo no anda y quieres ver que pasa
   - Para cerrar: Ctrl+C en la ventana

URLs directas para abrir manual:
   - http://localhost:8765/?mode=fullscreen  (TV)
   - http://localhost:8765/?mode=overlay     (OBS, fondo transparente)
   - http://localhost:8765/control           (panel desde la PC)
   - http://IP-DEL-PC:8765/control           (panel desde el celu)

============================================================
USAR EN OBS
============================================================

Agrega un Browser Source con:
   URL:    http://localhost:8765/?mode=overlay
   Ancho:  600
   Alto:   600
   (fondo transparente, lo metes en una esquina)

============================================================
HOTKEYS GLOBALES (funcionan desde cualquier app)
============================================================

Mientras TarroBot esta corriendo, puedes apretar estas teclas en
OBS, navegador, o donde sea sin tocar el celu:

  F1   ->  NEXT en la cola de datos
  F2   ->  PREV en la cola de datos
  F3   ->  Saludo random
  F4   ->  Despedida random (+ acelera somnolencia hacia sleep)
  F5   ->  RESET cola (vuelve al primer item)
  F6   ->  Catchphrase Retrotarros (frase de marca random)
  F7   ->  Tocar una melodia random de la cola de musica
  F8   ->  Despertar TarroBot (si esta dormido o aburrido)

Si en tu PC los hotkeys no responden, cierra TarroBot y vuelve a abrir
TarroBot.bat haciendo click derecho -> Ejecutar como administrador.
(la libreria 'keyboard' a veces necesita privilegios elevados)

============================================================
LISTA DE COMANDOS POR VOZ
============================================================

Manten apretado el boton "MIC" en el panel control y di:

  "Hola TarroBot"               -> saludo random geek
  "Chao TarroBot"               -> despedida + se va a dormir solo
  "Cuentame de Super Mario 64"  -> dato curioso
  "Que opinas de Sonic 06"      -> opinion con Claude
  "Este vale 5000 dolares"      -> reaccion al precio
  "Dame un dato random"         -> dato al azar
  "Dame un dato random de musica" -> filtrado por categoria
  "TarroBot estas con nosotros?" -> despierta si estaba dormido
  "TarroBot, despierta"         -> idem
  "Sigues ahi?"                 -> idem

Si el mic no funciona en el celu (en algunos browsers
necesita HTTPS), usa el panel desde el PC en localhost.

============================================================
MELODIAS MIDI (tocar musica retro en vivo)
============================================================

TarroBot puede tocar snippets de musica retro durante el programa,
estilo: "Koko, te acuerdas de la cancion de DKC? - Yo si, era como..."
y suena 5-10 segundos de la melodia con sonido SNES.

REQUISITOS (una vez):
1. FluidSynth ya viene en bin\fluidsynth.exe (install.bat lo baja).
2. Un soundfont .sf2 (no incluido por temas de derechos).
   Bajalo de uno de estos sitios:
     - GeneralUser GS (CC0, libre):  schristiancollins.com/generaluser.php
     - SNES soundfont:               buscar en archive.org / musescore.com
   Renombralo a "soundfont.sf2" y copialo en:
     studio\melodias\soundfont.sf2

USAR:
1. Baja el MIDI de un sitio de partituras fan:
     - Ichigos:        ichigos.com         (Final Fantasy y mas)
     - Ninsheetmusic:  ninsheetmusic.org   (Nintendo)

   Guardalo en una SUBCARPETA por consola/contexto (recomendado):
     studio\melodias\snes\<nombre>.mid    (DKC, Chrono Trigger, etc.)
     studio\melodias\n64\<nombre>.mid     (DK64, Zelda OoT, Mario 64...)
     studio\melodias\mario\<nombre>.mid   (Super Mario de cualquier consola)
     studio\melodias\arcade\<nombre>.mid  (DK arcade, Pac-Man, etc.)

   Asi cuando carga melodias a una pauta, puedes filtrar por
   contexto y solo cargar las que tengan sentido con el episodio.

2. Agrega la melodia a una pauta del episodio. Opciones:

   A) UN MIDI especifico con recorte custom (--desde y --segundos):
     python scripts\tarrobot.py --melodia-add <slug-pauta> ^
         --midi studio\melodias\snes\dkc-aquatic.mid ^
         --desde 0:14 --segundos 8 ^
         --titulo "DKC Aquatic Ambience" ^
         --consola SNES --ano 1994 --editor Rare

   B) BULK de una subcarpeta entera (todos los MIDIs ahi):
     python scripts\tarrobot.py --melodia-bulk <slug-pauta> ^
         --folder snes --segundos 8

   C) BORRAR las melodias de una pauta (para reorganizar):
     python scripts\tarrobot.py --melodia-clean <slug-pauta>

   Esto renderiza MP3s con sonido SNES y los agrega como items
   tipo=melodia a la pauta. Aparecen automatico en la card MUSICA
   DEL EPISODIO del panel control.

3. Durante grabacion, NEXT en la cola hace que TarroBot toque la
   melodia con estado "whistling" (boca tipo O + notas musicales
   saliendo) en lugar de hablar.

NOTA LEGAL:
Las partituras de Ichigos y Ninsheetmusic son transcripciones por fans,
no son samples originales de Nintendo/Capcom. Tocar 5-15 segundos como
referencia en un programa de YouTube es razonablemente fair use (es
comentario sobre el material). Recomendacion:
  - Snippets cortos (max 15s)
  - NUNCA canciones completas
  - Mencionar el juego de origen (lo vas a hacer natural en el comentario)

============================================================
PROBLEMAS COMUNES
============================================================

"Falta la API key"
  -> Reinstala o ejecuta en CMD:
     setx ANTHROPIC_API_KEY "sk-ant-tu-key-aqui"
     y reabre TarroBot.

"El navegador no abre"
  -> Abrelo manual en http://localhost:8765/?mode=fullscreen

"Whisper tarda mucho"
  -> Es normal la primera vez (descarga modelo ~244 MB).
     Despues queda en cache (%USERPROFILE%\.cache\whisper).

"No me reconoce la voz"
  -> Asegurate que el mic este bien configurado en Windows.
     Hablar claro y cerca. Si sigue mal: usa el panel manual.

"Puerto 8765 ocupado"
  -> Cierra otras instancias de TarroBot. Si persiste, edita
     scripts\tarrobot-live.py y cambia PORT a 8766.

"FluidSynth no esta instalado" o "soundfont no encontrado"
  -> Revisa que bin\fluidsynth.exe existe y que tienes
     studio\melodias\soundfont.sf2 (o el .sf2 que prefieras).
     Sin esto las melodias MIDI no andan pero TarroBot anda
     perfecto en todo lo demas.

"La melodia suena muy distinta a la original"
  -> Es por el soundfont que usaste. GeneralUser GS suena bien pero
     no es identico a SNES. Para sonido SNES real, busca un
     "Super Nintendo Soundfont" especifico.

============================================================
ESPACIO EN DISCO
============================================================

Despues de instalar:
   .venv/        ~ 350 MB  (Python + dependencias)
   bin/          ~  70 MB  (ffmpeg)
   ~/.cache/     ~ 244 MB  (modelo Whisper, se baja al usar mic)
   Total:        ~ 670 MB

============================================================
SOPORTE
============================================================

Repo: github.com/LuisGaticaJerez/Retrotarros
Sobre: D:\Recursos Retrotarros\repo\

Contacto: luis.gatica.jerez@gmail.com
============================================================
