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
CONTROL DE OBS POR VOZ (Sprint 9)
============================================================

TarroBot puede cambiar escenas y reaccionar a tomas cercanas
hablando con OBS por su WebSocket interno.

ACTIVAR EN OBS (una vez):
1. Abre OBS, menu Tools -> WebSocket Server Settings
2. Marca "Enable WebSocket server"
3. Puerto: 4455 (default)
4. Marca "Enable Authentication" y pon una password
5. Click "Show Connect Info" para verificar

ARMAR ESCENAS EN OBS (recomendado):
Con nombres claros para que los alias funcionen:
   cam-cenital       (toma general de la mesa)
   cam-luis          (camara apuntando a ti)
   cam-koko          (camara apuntando a Koko)
   tarrobot-full     (TarroBot pantalla completa)
   closeup-cartucho  (zoom a un cartucho)
   closeup-caja      (zoom a una caja)
   closeup-consola   (zoom a la consola)
   intro / outro

CONECTAR TARROBOT:
1. En el panel de control, busca la card "CONTROL OBS"
2. Pon host (localhost), puerto (4455) y la password
3. Click CONECTAR
4. Veras la escena actual y un dropdown con todas las escenas

COMANDOS POR VOZ:
   "TarroBot, camara a Koko"            -> cambia a cam-koko
   "TarroBot, camara a Luis"            -> cambia a cam-luis
   "TarroBot, vamos a camara cenital"   -> cambia a cam-cenital
   "TarroBot, toma cercana al cartucho" -> close-up + frase WOW
   "TarroBot, primer plano a la caja"   -> close-up + frase WOW
   "TarroBot, gracias"                  -> vuelve a la toma anterior
   "TarroBot, muestra el logo"          -> activa la fuente logo
   "TarroBot, saca el logo"             -> oculta la fuente logo

REACCION "TOMA CERCANA":
Cuando dices "toma cercana al cartucho":
  1. OBS cambia a la escena closeup-cartucho
  2. TarroBot dice una frase tipo "Wow, miren esa joyita"
  3. Queda con cara excited mientras dura la toma
  4. Cuando dices "gracias TarroBot", vuelve a la toma general

AUTO-ESCENA AL HABLAR:
Toggle "Auto-escena al hablar" en la card:
  - TarroBot habla  -> OBS corta a tarrobot-full automatico
  - TarroBot calla  -> vuelve a la escena previa
Util cuando quieres que aparezca grande cada vez que comenta.

CONFIGURAR ALIAS:
Si tus escenas tienen otros nombres, edita:
   studio\obs-aliases.json
Mapea alias_por_voz -> nombre_real_en_OBS. El archivo se
sincroniza con el Drive como el resto del repo.

NOTA: si OBS no esta abierto cuando hablas, TarroBot ignora los
comandos de camara silenciosamente. Todo lo demas funciona igual.


============================================================
CONCENTRADOR DE CHAT MULTI-PLATAFORMA (Sprint 13)
============================================================

TarroBot escucha el chat de Twitch, Discord y YouTube Live en
tiempo real y muestra todo en un solo feed unificado en el panel
control. Util para streams/podcasts donde el publico escribe en
varias plataformas y no queres tener 4 pestañas abiertas.

CONECTORES DISPONIBLES:

1. TWITCH (sin setup, auth anonima)
   - Solo pone el nombre del canal y conecta.
   - No requiere registrar bot ni OAuth.

2. DISCORD (requiere setup previo del bot)
   - Ver docs/discord-bot-setup.md para crear la app Discord.
   - Variables de entorno necesarias:
       DISCORD_BOT_TOKEN
       DISCORD_GUILD_ID
       DISCORD_CHANNEL_IDS (comma-separated)
   - El bot tiene que estar invitado al servidor.

3. YOUTUBE LIVE (read-only, sin OAuth)
   - Variables de entorno:
       YOUTUBE_API_KEY (de Google Cloud Console)
   - Pegar el video_id del stream activo en el panel
     (o setear YOUTUBE_VIDEO_ID en .env como default).

USAR EN VIVO:
1. Abre el panel: http://localhost:8765/control
2. Card "SESION DE STREAM": pone slug + titulo y click INICIAR.
3. Card "CONECTORES SOCIALES":
   - Twitch: pone canal y CONECTAR (por defecto: retrotarros)
   - Discord: CONECTAR (lee env vars)
   - YouTube: opcional, video_id + CONECTAR
4. Card "FEED DE CHAT" se llena con mensajes en tiempo real.
   - Filtros: TODO / TWITCH / DISCORD / YT
   - Click PIN en un mensaje para responderlo en camara.
   - Panel lateral PINNED muestra los pinneados destacados.

PERSISTENCIA:
Todo se guarda en data/tarrobot-messages.db (SQLite local).
Cada sesion queda etiquetada con el slug. Post-grabacion podes
exportar los pinned como pinned comment de YouTube o highlights
de la transmision (futuro).

PRIVACIDAD:
- Todo corre LOCAL en tu PC. No hay servicios cloud.
- Discord bot solo lee canales del servidor RetroTarros.
- Twitch usa auth anonima (no se ve quien escucha).
- YouTube usa API key publica (solo lee chat publico).

LIMITACIONES:
- Instagram Live, Facebook Live, WhatsApp: NO implementados.
  Estos requieren Social Stream Ninja como puente. Futuro sprint.


============================================================
AUTO-RESPOND TOGGLE (Sprint 16)
============================================================

Hasta Sprint 15, TarroBot solo respondia al chat cuando tu
clickeabas 🧠 RESPOND en un mensaje. A partir del Sprint 16
puedes activar AUTO-RESPOND y TarroBot responde solo.

Card "AUTO-RESPOND" en el panel con:
  - Switch principal ON/OFF (default OFF)
  - Toggle "solo si mencionan a TarroBot" (default ON):
    el mensaje tiene que contener "tarrobot", "@tarrobot",
    "tarro bot", "@retrotarros" o similares.
  - Toggle "no auto-responder si TarroBot esta hablando":
    evita que se solapen respuestas.
  - Slider cooldown por user (10-300s, default 60s):
    max 1 respuesta a cada viewer cada X segundos.
  - Slider cooldown global (5-60s, default 15s):
    max 1 respuesta total cada X segundos (anti spam de chat).
  - Checks de plataformas habilitadas (Twitch/Discord/YouTube).
  - Contador de respuestas automaticas esta sesion.

CONFIG PERSISTIDA:
La config se guarda en data/tarrobot-auto-respond.json. Sobrevive
reinicios. Si pones AUTO-RESPOND ON, TarroBot lo mantiene ON la
proxima vez que arranques (por seguridad: REVISA antes de salir
al aire si esta o no activo).

WORKFLOW RECOMENDADO:
- Streams casuales con audiencia chica: AUTO-RESPOND ON +
  mention_only ON. TarroBot solo habla cuando lo llaman.
- Podcasts grabados (no en vivo): AUTO-RESPOND OFF para
  controlar manualmente cada respuesta.
- Sesion de Q&A con audiencia grande: AUTO-RESPOND OFF, vos
  pin los mejores y los respondes manual con RESPOND/DICTATE.

COSTO:
Cada auto-respuesta usa Claude haiku (~$0.001). Con cooldown
global 15s, max 4 respuestas/min = ~240 calls/hora =
~$0.24/hora de stream. Si el MODO BARATO esta ON, AUTO-RESPOND
bloquea las llamadas Claude (igual no responde).


============================================================
MINIMIZAR GASTO LLM (Sprint 15)
============================================================

Cada llamada a Claude cuesta ~$0.001 USD. Para minimizar el
gasto durante grabaciones, TarroBot pre-genera TODO el contenido
LLM al crear la pauta:

CUANDO HACES "GENERAR PAUTA AUTO" CON UN TEMA:
TarroBot ahora genera EN LA MISMA LLAMADA (1 call de Claude):
  - 10 datos curiosos del top
  - 3 opiniones alternativas por dato (para boton "opinar")
  - 5 comentarios cortos por dato (color entre items)
  - 2 preguntas quiz por dato (para "/api/quiz/pregunta")
  - 8 catchphrases especificas del episodio
  - 3 intros de cold open
  - 3 outros con cliffhanger
  - Publicacion completa: 3 titulos + descripcion + 15-20
    hashtags + 5 prompts thumbnail + ig_post

Esto significa: durante grabacion, NO se llama a Claude para
opinar/quiz/exportar-descripcion porque YA ESTA todo en la pauta.

CAPA DE CACHE LOCAL:
Para temas fuera de la pauta, las respuestas que TarroBot
genera con Claude se cachean en data/tarrobot-cache-llm.json
con TTL de 30 dias. Si Luis pide "opinar Mario Galaxy" 5 veces
en una semana, solo se llama a Claude una vez (las otras 4
salen del cache).

CARD "LLM GASTO Y AHORRO" EN EL PANEL:
Muestra en vivo:
  - Llamadas a Claude esta sesion (por endpoint)
  - Costo estimado USD acumulado
  - Cache local: keys + respuestas
  - Toggle MODO BARATO

MODO BARATO:
Cuando esta ON, TarroBot bloquea TODAS las llamadas a Claude.
Solo responde con pauta pre-generada + cache local. Util para:
  - Grabar sin presupuesto LLM
  - Probar el flujo sin gastar
  - Si te quedaste sin creditos Anthropic

En modo barato, opinar/quiz/respond a chat con LLM devuelven
error 503. Lo que sigue funcionando:
  - Cuentame con datos curados de la DB
  - SAY (lectura literal) de mensajes
  - DICTATE (vos escribes la respuesta)
  - Pauta cargada con material pre-generado

WORKFLOW RECOMENDADO PARA AHORRO MAXIMO:
1. Cuando preparas un episodio, usa "GENERAR PAUTA AUTO" con
   modo enriquecido (default). Costo: ~$0.05 una vez.
2. Durante grabacion, casi todas las opiniones/quiz/comentarios
   salen de la pauta. Costo: $0.
3. Para chat de streams: usa SAY o DICTATE (gratis) en lugar de
   RESPOND. Si necesitas respond, va al cache despues de la
   primera vez.
4. Al exportar la descripcion del episodio: ya esta lista en
   la pauta, costo $0.

Costo mensual estimado:
  - 4 episodios/mes × $0.05 = $0.20 USD en pautas
  - ~20 respuestas LLM ad-hoc/mes × $0.001 = $0.02
  - Total: ~$0.22 USD/mes para uso normal del canal


============================================================
TARROBOT RESPONDE AL CHAT (Sprint 14)
============================================================

A partir del Sprint 14, TarroBot no solo lee el chat: tambien
responde con voz (TTS) y opcionalmente escribe en el canal de
Discord. Cada mensaje del feed tiene 3 botones:

1. 🔊 SAY - TarroBot lee el mensaje literal en voz alta
   ("Marcos dice: ¿que opinas de Mario Galaxy?"). Util para
   pasar la pregunta al aire sin tu intervencion.

2. 🧠 RESPOND - TarroBot pide a Claude que arme una respuesta
   personalizada al viewer (chileno neutro, max 220 chars, tono
   acorde al canal). Tarda 2-4 seg. Rate limit 3s entre respuestas.

3. ✍ DICTATE - Abre un modal donde TU escribis la respuesta y
   TarroBot la lee con su voz. Util cuando queres respuesta
   espontanea o personalizada.

Si el mensaje es de Discord, podes ademas tildar "publicar en
Discord" y la respuesta se publica en el canal de origen (TarroBot
escribe ahi). Twitch/YouTube todavia no soportan write-back por
limitaciones de auth.

COLA "LEER PINNED EN ORDEN":
En la card FEED hay un boton "▶ LEER PINNED EN COLA". TarroBot
lee todos los pinneados uno por uno, esperando que termine el
TTS de cada uno antes del siguiente. Boton de nuevo para detener.

WORKFLOW TIPICO EN STREAM:
1. Empieza el stream, conectas Twitch + Discord + YouTube.
2. Mientras grabas, las preguntas interesantes las haces PIN.
3. En el segmento "preguntas del publico", click LEER PINNED EN
   COLA. TarroBot va leyendo las preguntas.
4. Para cada una: o decis tu respuesta a camara, o le das RESPOND
   (Claude responde) o DICTATE (vos lo escribis).
5. Si era de Discord, podes hacer que TarroBot conteste tambien
   en el canal Discord directamente.

ANTI-SPAM Y SEGURIDAD:
- Rate limit 3s en RESPOND para no quemar creditos Claude.
- Filtro chilenizar() postproceso en TODA respuesta LLM.
- Discord write-back solo a canales donde el bot ya tiene
  permiso send_messages (configurado en el setup del bot).
- Maximo 2000 chars en cada post Discord (limite plataforma).

TROUBLESHOOTING:
- "Twitch no conecta": revisa que no haya firewall bloqueando
  el puerto 6697 (IRC SSL). Tipico en redes corporativas.
- "Discord no conecta": verifica que el bot este invitado al
  servidor y que el token sea valido. Ver discord-bot-setup.md.
- "YouTube no encuentra video": el video_id debe ser de un
  stream EN VIVO (no de un video grabado). Tambien verifica
  que la API key tenga YouTube Data API v3 habilitada.


============================================================
FUNCIONES AVANZADAS (Sprint 12)
============================================================

PRESENTADOR ASISTENTE (reordenar pauta):
Card "PRESENTADOR ASISTENTE" en el panel. Pide a Claude que
analice la pauta cargada y sugiera un nuevo orden con maxima
retencion (gancho fuerte primero, climax al final). Te muestra
una preview antes de aplicar. Click APLICAR ORDEN y la cola
queda reordenada (la pauta JSON tambien se guarda con el nuevo
orden, asi queda persistente).

EXPORTAR PUBLICACION (titulo + descripcion automatica):
Card "EXPORTAR PUBLICACION". Cuando termines de grabar, click
"GENERAR DESCRIPCION" y Claude analiza la pauta + el session_log
(timestamps reales de cuando apretaste NEXT durante la grabacion)
y genera:
   - 3 opciones de titulo optimizadas CTR YouTube
   - Descripcion completa con timestamps reales
   - 15-20 hashtags retrogaming
   - 5 prompts de texto en ingles para generar thumbnails con IA
   - Texto corto para Instagram/Reels

Se guarda en  studio\exports\<slug>-publicacion.txt  para que
lo abras y copies/pegues al subir el video.

QUIZ TRIVIA EN VIVO:
Card "QUIZ TRIVIA". Click TIRAR y TarroBot pregunta una trivia
retro relacionada con la pauta del dia. Aparece la respuesta
esperada (visible solo para ti). Click ACERTÓ o ERRÓ segun
respondan en el programa, y TarroBot reacciona acorde. Lleva
score acumulado de la sesion.

MUSICA DE FONDO OBS:
Card "MUSICA DE FONDO". Controla el volumen de un input llamado
"musica-fondo" en OBS (configurable en obs-aliases.json):
   - Botones -3dB / +3dB / Mute
   - Presets -30 / -20 / -10 dB
Comandos por voz:
   "TarroBot pon musica"          -> unmute
   "TarroBot sube la musica"      -> +3 dB
   "TarroBot baja la musica"      -> -3 dB
   "TarroBot para la musica"      -> mute

Para usar musica de fondo en OBS:
   1. Agrega un Media Source o Audio Input Capture en OBS
   2. Renombralo a "musica-fondo" (o el nombre que configures
      en obs-aliases.json > musica_fondo > input_name)
   3. Pon tu playlist retro como source (Media Source con
      Local File + bucle)

EXPORTAR DATO COMO SHORT:
Endpoint /api/queue/short-export que copia el MP3 de un dato
puntual + genera SRT individual a:
   studio\shorts\<slug>-<NN>-<tema>.mp3
   studio\shorts\<slug>-<NN>-<tema>.srt
Pensado para alimentar CapCut/DaVinci con audio + subs sincros
para hacer Shorts/Reels verticales. No genera video del avatar
(eso se monta en el editor).


============================================================
GENERAR PAUTA AUTO DESDE UN TEMA (Sprint 11)
============================================================

TarroBot puede armar una pauta completa para un episodio nuevo
solo pidiendoselo. Le das un tema, le dice cuantos datos
quieres y Claude genera todo + MP3s listos para grabar.

DESDE EL PANEL:
1. Abre el panel control en el browser.
2. Busca la card "GENERAR PAUTA AUTO".
3. Escribe el tema (ej: "Top SNES exclusivos japoneses").
4. Opcional: consola (ej: "SNES"), cantidad de datos (default 10),
   slug del archivo (default: derivado del tema).
5. Click "GENERAR PAUTA". Tarda 1-3 min (LLM + TTS).
6. Cuando termina, te pregunta si quieres cargarla en la cola.

DESDE LA TERMINAL (CMD/PowerShell):
   python scripts\tarrobot.py --pauta-tema "Mega Drive raros"
   python scripts\tarrobot.py --pauta-tema "Joyas N64 PAL" ^
       --n-datos 8 --consola N64 --slug n64-joyas-pal
   python scripts\tarrobot.py --pauta-tema "Arcade japones 80s" ^
       --no-preload         (solo genera JSON, sin MP3s)

OPCIONES:
   --n-datos N    : 3 a 20, default 10
   --slug S       : nombre del archivo, default se deriva del tema
   --consola C    : hint al LLM (SNES, N64, Genesis, etc.)
   --episodio E   : titulo del episodio (default lo elige Claude)
   --voice V      : preset de voz (catalina, dalia, etc.)
   --no-preload   : NO generar los MP3s (mas rapido pero hay
                    que correr --pauta-preload despues)
   --force        : sobreescribe si ya existe el slug
   --no-sync      : no sincronizar con Drive al terminar

Despues de generar, la pauta queda en:
   studio\pautas\<slug>.tarrobot.json
   studio\pautas\audio\<slug>\<id>.mp3   (si hubo preload)


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
TARROTEASER · GENERAR SHORTS DESDE EL MASTER (v1.4+)
============================================================

A partir de v1.4 podes generar teasers verticales (1080x1920) listos
para YouTube Shorts / Reels / TikTok directamente desde el master del
episodio. TarroTeaser usa Whisper para detectar los mejores momentos
del video y los corta automaticamente.

Tres formas de usarlo:

1) DESDE EL MENU INICIO (lo mas comodo)
   - Abri el Menu Inicio > TarroBot Studio > "TarroTeaser (genera Short vertical)"
   - Te pide la ruta del MP4 (podes arrastrar el archivo sobre el bat)
   - Te pide el slug del episodio (ej. n64-top-precios)
   - Espera 5-10 min (Whisper transcribe + ffmpeg corta y verticaliza)
   - Te abre la carpeta de salida al terminar

2) DESDE EL PANEL CONTROL (web)
   - Abri el panel control (mismo navegador donde manejas TarroBot)
   - Busca la card "TARROTEASER · SHORT VERTICAL"
   - Pega la ruta del MP4 + slug. Si tenes una pauta cargada, el slug
     viene autollenado.
   - Click GENERAR. La barra de progreso muestra Whisper transcribiendo,
     deteccion de momentos, cortes, concatenacion.
   - Al terminar te muestra link a la carpeta y boton re-generar.

3) DESDE LA TERMINAL (control fino)
   python scripts\tarroteaser.py <video.mp4> --slug <slug> [opciones]

   Opciones:
     --num-highlights N      cantidad de clips del centro (default 3)
     --clip-duration N       duracion MIN del clip en seg (default 3)
     --max-clip-duration N   duracion MAX del clip en seg (default 6)
     --model small|medium    modelo Whisper (default small)
     --type ranking|archivo|...   forzar tipo de episodio
     --out-dir <ruta>        override directorio salida

Output: studio\teasers\<slug>\<slug>-tarroteaser-YYYYMMDD.mp4

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
