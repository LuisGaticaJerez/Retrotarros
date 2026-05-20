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

Se abre solo:
   - Una ventana cmd con el server corriendo
   - Una ventana de Chrome con TarroBot en pantalla completa

Para controlarlo:
   - En el celu (mismo wifi): http://IP-DEL-PC:8765/control
     (el TarroBot.bat te muestra la IP local cuando arranca)
   - Desde la misma PC: http://localhost:8765/control en otra
     pestana del browser

Para cerrar: cierra la ventana del cmd negro (o Ctrl+C ahi).

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

  F1   ->  NEXT en la cola del episodio
  F2   ->  PREV en la cola
  F3   ->  Saludo random
  F4   ->  Despedida random
  F5   ->  RESET cola (vuelve al primer item)
  F6   ->  Catchphrase Retrotarros (frase de marca random)

Si en tu PC los hotkeys no responden, cierra TarroBot y vuelve a abrir
TarroBot.bat haciendo click derecho -> Ejecutar como administrador.
(la libreria 'keyboard' a veces necesita privilegios elevados)

============================================================
LISTA DE COMANDOS POR VOZ
============================================================

Manten apretado el boton "MIC" en el panel control y di:

  "Hola TarroBot"               -> saludo random geek
  "Chao TarroBot"               -> despedida
  "Cuentame de Super Mario 64"  -> dato curioso
  "Que opinas de Sonic 06"      -> opinion con Claude
  "Este vale 5000 dolares"      -> reaccion al precio
  "Dame un dato random"         -> dato al azar
  "Dame un dato random de musica" -> filtrado por categoria

Si el mic no funciona en el celu (en algunos browsers
necesita HTTPS), usa el panel desde el PC en localhost.

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
