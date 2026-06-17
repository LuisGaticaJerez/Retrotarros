@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM ============================================================
REM  TarroBot Studio - Instalador automatico para Windows 10/11
REM  Retrotarros - doble click y listo
REM  Version 1.5.3 hotfix (fix ffmpeg: URL BtbN "latest" no resolvia con curl
REM                 --> reemplazado por gyan.dev con fallback a version pinneada;
REM                 deteccion previa de ffmpeg en sistema (OBS/winget/scoop);
REM                 eliminado goto-dentro-de-for-dentro-de-else (fragil en CMD)).
REM                 Ver CHANGELOG-tarrobot-studio.md
REM ============================================================

title TarroBot Studio - Configuracion
color 0B

REM ============================================================
REM  CONSTANTES
REM ============================================================
set "ROOT=%~dp0"
set "ROOT=%ROOT:~0,-1%"
cd /d "%ROOT%"

REM Variables que llenamos en FASE 1 y aplicamos en FASE 2
set "CFG_REPO_PATH="
set "CFG_API_KEY="
set "CFG_INTERNET_OK=no"
set "CFG_DISK_OK=no"

REM ============================================================
REM  LOG PERSISTENTE  (para diagnosticar si algo falla)
REM  - install-log.txt : bitacora de fases + diagnosticos
REM  - install-pip.txt : log detallado de pip (deps), donde mas falla
REM ============================================================
set "LOGFILE=%ROOT%\install-log.txt"
set "PIPLOG=%ROOT%\install-pip.txt"
> "%LOGFILE%" echo === TarroBot install log ===
>>"%LOGFILE%" echo Fecha: %DATE% %TIME%
>>"%LOGFILE%" echo ROOT:  %ROOT%
>>"%LOGFILE%" echo Usuario: %USERNAME%
>>"%LOGFILE%" echo.

REM ============================================================
REM  BIENVENIDA
REM ============================================================
cls
echo.
echo ============================================================
echo   TARROBOT STUDIO - INSTALADOR
echo ============================================================
echo.
echo Este instalador funciona en DOS fases:
echo.
echo   FASE 1 (configuracion): preguntas + validaciones
echo     - Ubicacion del repo Retrotarros (Drive o local)
echo     - API key de Anthropic (opcional)
echo     - Internet + espacio en disco
echo     - Confirmacion antes de tocar nada
echo.
echo   FASE 2 (instalacion automatica, ~5-10 minutos)
echo     - Python + dependencias
echo     - ffmpeg + FluidSynth portable
echo     - Acceso directo en escritorio
echo.
echo Espacio en disco necesario: ~800 MB
echo Conexion a internet requerida (primera vez)
echo.
pause

REM ============================================================
REM  FASE 1.1 - DETECTAR / PEDIR RUTA DEL REPO RETROTARROS
REM ============================================================
cls
echo.
echo ============================================================
echo   FASE 1/2  -  CONFIGURACION
echo ============================================================
echo.
echo [Paso 1 de 4] Ubicacion del repo Retrotarros
echo ------------------------------------------------------------
echo.
echo TarroBot necesita saber donde estan las pautas, datos y
echo melodias del canal. Dos opciones:
echo.
echo   A) Drive sincronizado: TarroBot lee las pautas nuevas que
echo      Luis genera en su PC automaticamente.
echo   B) Paquete local: TarroBot usa lo que vino en este ZIP,
echo      autocontenido pero sin actualizaciones automaticas.
echo.

REM Auto-deteccion del Drive en paths comunes
echo Buscando Drive sincronizado en ubicaciones tipicas...
set "DETECTED="
for %%P in (
    "G:\Mi unidad\Studio\tarrobot"
    "H:\Mi unidad\Studio\tarrobot"
    "F:\Mi unidad\Studio\tarrobot"
    "D:\Mi unidad\Studio\tarrobot"
    "C:\Users\%USERNAME%\Google Drive\Studio\tarrobot"
    "%USERPROFILE%\Google Drive\Studio\tarrobot"
    "G:\Mi unidad\Recursos Retrotarros\repo"
    "%USERPROFILE%\Google Drive\Recursos Retrotarros\repo"
) do (
    if not defined DETECTED (
        if exist "%%~P\scripts\tarrobot-live.py" (
            if exist "%%~P\data\tarrobot-database.json" (
                set "DETECTED=%%~P"
            )
        )
    )
)

if defined DETECTED (
    echo.
    echo [OK] Encontre repo Drive en:
    echo      !DETECTED!
    echo.
    set /p USE_DETECTED="Usar esa ruta? (S/n): "
    if /i "!USE_DETECTED!"=="n" (
        set "DETECTED="
        echo.
        echo Manual entonces.
    ) else (
        set "CFG_REPO_PATH=!DETECTED!"
        echo [OK] Repo Retrotarros configurado.
    )
) else (
    echo.
    echo [INFO] No encontre Drive sincronizado en ubicaciones tipicas.
)

REM Si no quedo seteado (no se detecto o usuario dijo no), preguntar
if not defined CFG_REPO_PATH (
    echo.
    echo Opciones:
    echo   - Pega la ruta del repo en Drive ^(acepta drag and drop^)
    echo   - O dejalo vacio para usar el paquete local
    echo.
    echo Ejemplos validos:
    echo   G:\Mi unidad\Studio\tarrobot
    echo   C:\Users\Estudio\Google Drive\Studio\tarrobot
    echo.
    set /p REPOMANUAL="Ruta al repo Retrotarros (Enter = paquete local): "
    if defined REPOMANUAL (
        REM Limpiar comillas si las pego con drag-drop
        set "REPOMANUAL=!REPOMANUAL:"=!"
        if exist "!REPOMANUAL!\scripts\tarrobot-live.py" (
            if exist "!REPOMANUAL!\data\tarrobot-database.json" (
                set "CFG_REPO_PATH=!REPOMANUAL!"
                echo [OK] Repo Retrotarros configurado: !REPOMANUAL!
            ) else (
                echo [WARN] La ruta no tiene data\tarrobot-database.json
                echo        Voy a usar el paquete local.
            )
        ) else (
            echo [WARN] La ruta no tiene scripts\tarrobot-live.py
            echo        Voy a usar el paquete local.
        )
    ) else (
        echo [OK] Usando paquete local.
    )
)

REM ============================================================
REM  FASE 1.2 - API KEY ANTHROPIC
REM ============================================================
echo.
echo ------------------------------------------------------------
echo [Paso 2 de 4] API key de Anthropic
echo ------------------------------------------------------------
echo.
echo TarroBot usa Claude (Anthropic) para:
echo   - Opinar sobre juegos (modo opinion)
echo   - Generar pautas de episodios desde un tema
echo   - Reordenar pautas para retencion
echo   - Trivia interactiva
echo   - Generar descripciones de YouTube post-grabacion
echo.
echo SIN api key, TarroBot funciona pero limitado (solo datos
echo curados de la DB, sin LLM en vivo).
echo.
echo Para conseguir una key:
echo   1. Ve a https://console.anthropic.com/settings/keys
echo   2. Crea una llamada "tarrobot-studio"
echo   3. Empieza con sk-ant-api03-...
echo.
set /p CFG_API_KEY="Pega tu API key (Enter = configurar despues): "

if defined CFG_API_KEY (
    REM Limpiar espacios y comillas
    set "CFG_API_KEY=!CFG_API_KEY:"=!"
    echo [OK] API key recibida.
) else (
    echo [INFO] OK, podes configurarla despues con:
    echo        setx ANTHROPIC_API_KEY "sk-ant-..."
)

REM ============================================================
REM  FASE 1.3 - VERIFICAR INTERNET
REM ============================================================
echo.
echo ------------------------------------------------------------
echo [Paso 3 de 4] Verificar conexion a internet
echo ------------------------------------------------------------
echo.
echo Probando conexion a python.org...
curl -s -o nul -w "" --max-time 5 https://www.python.org/ 2>nul
if !errorlevel! equ 0 (
    echo [OK] Internet OK.
    set "CFG_INTERNET_OK=yes"
) else (
    echo [WARN] No se puede acceder a internet.
    echo        La instalacion necesita bajar Python, ffmpeg y FluidSynth.
    echo        Verifica tu conexion antes de continuar.
)

REM ============================================================
REM  FASE 1.4 - VERIFICAR ESPACIO EN DISCO
REM ============================================================
echo.
echo ------------------------------------------------------------
echo [Paso 4 de 4] Verificar espacio en disco
echo ------------------------------------------------------------
echo.
for /f "tokens=3" %%a in ('dir /-c "%ROOT%" ^| findstr /R /C:"libres" /C:"bytes free"') do set FREE=%%a
if defined FREE (
    echo Espacio libre en este disco: %FREE% bytes
    set "CFG_DISK_OK=yes"
) else (
    echo [INFO] No pude leer el espacio libre, pero seguramente esta OK.
    set "CFG_DISK_OK=yes"
)
echo TarroBot necesita ~800 MB libres.

REM ============================================================
REM  CONFIRMACION FINAL
REM ============================================================
echo.
echo ============================================================
echo   RESUMEN DE CONFIGURACION
echo ============================================================
echo.
echo Carpeta de instalacion:
echo   %ROOT%
echo.
if defined CFG_REPO_PATH (
    echo Repo Retrotarros: Drive sincronizado
    echo   !CFG_REPO_PATH!
) else (
    echo Repo Retrotarros: Paquete local autocontenido
)
echo.
if defined CFG_API_KEY (
    echo API key Anthropic: Configurada
) else (
    echo API key Anthropic: NO configurada ^(podes hacerlo despues^)
)
echo.
echo Internet: %CFG_INTERNET_OK%
echo Disco:    %CFG_DISK_OK%
echo.
echo Voy a:
echo   - Instalar Python 3.12 si no esta (silencioso)
echo   - Crear entorno virtual (.venv) en esta carpeta
echo   - Instalar dependencias Python (FastAPI, Whisper, edge-tts, etc)
echo   - Descargar ffmpeg portable (~70 MB)
echo   - Descargar FluidSynth portable (~25 MB)
echo   - Guardar configuracion (variables de entorno)
echo   - Crear acceso directo en escritorio
echo.
echo Tiempo estimado: 5-10 minutos (depende de tu conexion).
echo.
set /p CONFIRM="Continuar con la instalacion? (S/n): "
if /i "!CONFIRM!"=="n" (
    echo.
    echo Cancelado. Nada se modifico.
    pause
    exit /b 0
)

REM ============================================================
REM  FASE 2 - INSTALACION AUTOMATICA (sin preguntas)
REM ============================================================
cls
echo.
echo ============================================================
echo   FASE 2/2  -  INSTALACION AUTOMATICA
echo ============================================================
echo.

REM ============================================================
REM  Paso 1 - Python
REM ============================================================
echo.
echo [1/7] Verificando Python...
set "PYEXE="

REM Detectar Python REAL ignorando el alias de la Microsoft Store.
REM El stub en WindowsApps responde a 'where python' pero NO es Python:
REM al invocarlo abre la tienda y cuelga el instalador en el paso del venv.
for /f "delims=" %%i in ('where python 2^>nul') do (
    echo %%i | findstr /I "WindowsApps" >nul
    if errorlevel 1 if not defined PYEXE set "PYEXE=%%i"
)

REM Respaldo: el py launcher suele apuntar al Python real (no al stub).
if not defined PYEXE (
    for /f "delims=" %%i in ('py -3.12 -c "import sys;print(sys.executable)" 2^>nul') do set "PYEXE=%%i"
)
if not defined PYEXE (
    for /f "delims=" %%i in ('py -3 -c "import sys;print(sys.executable)" 2^>nul') do set "PYEXE=%%i"
)

REM Rechazar Python demasiado nuevo: whisper/torch/numba no tienen wheels para
REM 3.13+, y pip se cuelga resolviendo/compilando. Solo aceptamos 3.10/3.11/3.12.
if defined PYEXE (
    for /f "tokens=2" %%v in ('"!PYEXE!" --version 2^>^&1') do set "PY_VER=%%v"
    echo !PY_VER! | findstr /R "^3\.1[012]\." >nul
    if errorlevel 1 (
        echo [INFO] Python !PY_VER! es muy nuevo para Whisper/torch.
        echo [INFO] Voy a instalar un Python 3.12.7 dedicado.
        set "PYEXE="
    )
)

if defined PYEXE (
    echo [OK] Python real compatible encontrado: !PY_VER!
    echo      !PYEXE!
    >>"!LOGFILE!" echo [python] usando !PYEXE! ver !PY_VER!
) else (
    echo [INFO] No hay Python real ^(solo el alias de la tienda, o nada^).
    echo [INFO] Descargando Python 3.12.7...
    curl -L -o python-installer.exe https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe
    if !errorlevel! neq 0 (
        echo [ERROR] No se pudo descargar Python. Verifica tu conexion.
        pause
        exit /b 1
    )
    echo [INFO] Instalando Python ^(silencioso, solo para tu usuario^)...
    python-installer.exe /quiet InstallAllUsers=0 PrependPath=1 Include_test=0 Include_pip=1
    if !errorlevel! neq 0 (
        echo [ERROR] La instalacion de Python fallo.
        pause
        exit /b 1
    )
    del python-installer.exe
    REM Usar la ruta COMPLETA del python recien instalado, NO 'python' a secas
    REM (asi no volvemos a caer en el stub de la tienda).
    set "PYEXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    if not exist "!PYEXE!" (
        echo [ERROR] Python se instalo pero no aparece en:
        echo         !PYEXE!
        echo         Reinicia el PC y vuelve a correr install.bat.
        pause
        exit /b 1
    )
    echo [OK] Python instalado: !PYEXE!
)

REM ============================================================
REM  Paso 2 - venv
REM ============================================================
echo.
echo [2/7] Creando entorno virtual (.venv)...
if exist ".venv\Scripts\python.exe" (
    echo [OK] .venv ya existe y es valido, saltando.
) else (
    REM Si quedo un .venv a medias de un intento anterior, lo borramos.
    if exist ".venv" (
        echo [INFO] Habia un .venv incompleto, lo recreo...
        rmdir /s /q ".venv"
    )
    "!PYEXE!" -m venv .venv
    if !errorlevel! neq 0 (
        echo [ERROR] No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
    if not exist ".venv\Scripts\python.exe" (
        echo [ERROR] El venv se creo pero falta .venv\Scripts\python.exe
        echo         Probablemente Python quedo a medias. Reinstala Python.
        pause
        exit /b 1
    )
    echo [OK] .venv creado.
)

REM ============================================================
REM  Paso 3 - Dependencias Python
REM ============================================================
echo.
echo [3/7] Instalando dependencias Python (puede tardar 3-8 min)...
REM Usamos el python del venv por ruta directa (mas confiable que activate.bat
REM y evita cualquier interferencia del alias de la tienda).
set "VPY=.venv\Scripts\python.exe"

echo [INFO] Actualizando pip...
"!VPY!" -m pip install --upgrade pip

REM PyTorch (dependencia de openai-whisper) PRIMERO y desde el indice CPU.
REM Sin esto, pip intenta resolver wheels gigantes (variante CUDA ~2.5 GB) o
REM compilar desde fuente, y el instalador parece colgado sin dar error.
echo [INFO] Instalando PyTorch (CPU) - el paso mas pesado, paciencia...
echo [INFO] (detalle completo se guarda en install-pip.txt)
"!VPY!" -m pip install torch --index-url https://download.pytorch.org/whl/cpu --log "!PIPLOG!"
if !errorlevel! neq 0 (
    echo [WARN] Fallo el torch CPU dedicado. Intento via requirements normal...
    >>"!LOGFILE!" echo [pip] torch CPU fallo - ver install-pip.txt
)

echo [INFO] Instalando el resto de dependencias (FastAPI, Whisper, edge-tts...)...
"!VPY!" -m pip install -r requirements.txt --log "!PIPLOG!"
if !errorlevel! neq 0 (
    echo [ERROR] Fallo la instalacion de dependencias.
    echo         Detalle del error en:
    echo           !PIPLOG!
    echo           !LOGFILE!
    >>"!LOGFILE!" echo [pip] requirements fallo - ver install-pip.txt
    pause
    exit /b 1
)

REM Smoke-test: que las dependencias clave IMPORTEN de verdad. Asi el fallo
REM aparece aca (ruidoso) y no despues al arrancar TarroBot con pythonw (mudo).
echo [INFO] Verificando que las dependencias clave importen...
"!VPY!" -c "import fastapi, uvicorn, jinja2, edge_tts, anthropic, whisper, pystray, PIL, discord; print('imports OK')" 2>>"!LOGFILE!"
if !errorlevel! neq 0 (
    echo [ERROR] Las dependencias se instalaron pero alguna NO importa.
    echo         El detalle del import que fallo quedo en:
    echo           !LOGFILE!
    echo         Suele arreglarse corriendo install.bat de nuevo.
    >>"!LOGFILE!" echo [smoke] fallo import de dependencias
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas y verificadas.
>>"!LOGFILE!" echo [smoke] imports OK

REM ============================================================
REM  Paso 4 - ffmpeg
REM ============================================================
echo.
echo [4/7] Verificando ffmpeg...
set "FFMPEG_OK=no"

REM Primero: portable local
if exist "bin\ffmpeg.exe" (
    echo [OK] ffmpeg portable en bin\ffmpeg.exe
    set "FFMPEG_OK=yes"
)

REM Segundo: ffmpeg instalado en el sistema (OBS, winget, scoop, etc)
if "!FFMPEG_OK!"=="no" (
    set "FFMPEG_SYS="
    for /f "delims=" %%i in ('where ffmpeg 2^>nul') do (
        if not defined FFMPEG_SYS set "FFMPEG_SYS=%%i"
    )
    if defined FFMPEG_SYS (
        echo [OK] ffmpeg encontrado en el sistema: !FFMPEG_SYS!
        if not exist "bin" mkdir bin
        copy "!FFMPEG_SYS!" "bin\ffmpeg.exe" >nul
        echo [OK] copiado a bin\ffmpeg.exe
        set "FFMPEG_OK=yes"
        >>"!LOGFILE!" echo [ffmpeg] copiado del sistema: !FFMPEG_SYS!
    )
)

REM Tercero: descargar si no hay ninguno
if "!FFMPEG_OK!"=="no" (
    echo [INFO] ffmpeg no encontrado. Descargando portable desde gyan.dev ~25 MB...
    if not exist "bin" mkdir bin
    curl -L --max-time 120 -o ffmpeg-essentials.zip "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip" 2>>"!LOGFILE!"
    if !errorlevel! neq 0 (
        echo [WARN] Fallo descarga de gyan.dev. Intentando con version fija de GitHub...
        curl -L --max-time 120 -o ffmpeg-essentials.zip "https://github.com/GyanD/codexffmpeg/releases/download/7.1.1/ffmpeg-7.1.1-essentials_build.zip" 2>>"!LOGFILE!"
        if !errorlevel! neq 0 (
            echo [ERROR] No se pudo descargar ffmpeg.
            echo         Opciones manuales:
            echo           winget install Gyan.FFmpeg
            echo           o baja de https://www.gyan.dev/ffmpeg/builds/
            echo           y pon ffmpeg.exe en la carpeta bin\ de TarroBot
            >>"!LOGFILE!" echo [ffmpeg] descarga fallida - instalar manual
            pause
            exit /b 1
        )
    )
    echo [INFO] Extrayendo ffmpeg...
    powershell -NoProfile -Command "Expand-Archive -Path ffmpeg-essentials.zip -DestinationPath ffmpeg-temp -Force"
    set "FFEXE="
    for /r "ffmpeg-temp" %%f in (ffmpeg.exe) do (
        if not defined FFEXE set "FFEXE=%%f"
    )
    if defined FFEXE (
        copy "!FFEXE!" "bin\ffmpeg.exe" >nul
        set "FFMPEG_OK=yes"
    )
    rmdir /s /q ffmpeg-temp 2>nul
    del ffmpeg-essentials.zip 2>nul
    if "!FFMPEG_OK!"=="yes" (
        echo [OK] ffmpeg listo en bin\ffmpeg.exe
        >>"!LOGFILE!" echo [ffmpeg] instalado OK
    ) else (
        echo [ERROR] No se pudo extraer ffmpeg.
        echo         Instala manual: winget install Gyan.FFmpeg
        >>"!LOGFILE!" echo [ffmpeg] extraccion fallida
        pause
        exit /b 1
    )
)

REM ============================================================
REM  Paso 5 - FluidSynth + DLLs
REM ============================================================
echo.
echo [5/7] Configurando FluidSynth para tocar melodias MIDI...
if exist "bin\fluidsynth.exe" (
    echo [OK] FluidSynth ya esta en bin\fluidsynth.exe
) else (
    echo [INFO] Descargando FluidSynth 2.3.5 portable ^(~25 MB^)...
    if not exist "bin" mkdir bin
    curl -L -o fluidsynth.zip https://github.com/FluidSynth/fluidsynth/releases/download/v2.3.5/fluidsynth-2.3.5-win10-x64.zip
    if !errorlevel! neq 0 (
        echo [WARN] No se pudo descargar FluidSynth. Las melodias MIDI no van a funcionar.
        goto :fluidsynth_done
    )
    echo [INFO] Extrayendo FluidSynth...
    powershell -NoProfile -Command "Expand-Archive -Path fluidsynth.zip -DestinationPath fluidsynth-temp -Force"
    for /r "fluidsynth-temp" %%f in (fluidsynth.exe) do (
        copy "%%~dpf*.exe" "bin\" >nul 2>&1
        copy "%%~dpf*.dll" "bin\" >nul 2>&1
        goto :fluidsynth_extracted
    )
    :fluidsynth_extracted
    rmdir /s /q fluidsynth-temp 2>nul
    del fluidsynth.zip 2>nul
    if exist "bin\fluidsynth.exe" (
        echo [OK] FluidSynth listo en bin\fluidsynth.exe
    ) else (
        echo [WARN] No se pudo extraer FluidSynth correctamente.
    )
)
:fluidsynth_done

REM ============================================================
REM  Paso 6 - Guardar configuracion (variables de entorno)
REM ============================================================
echo.
echo [6/7] Guardando configuracion...

if defined CFG_API_KEY (
    setx ANTHROPIC_API_KEY "!CFG_API_KEY!" >nul
    echo [OK] ANTHROPIC_API_KEY guardada como variable de usuario.
)

if defined CFG_REPO_PATH (
    setx RETROTARROS_REPO "!CFG_REPO_PATH!" >nul
    echo [OK] RETROTARROS_REPO guardada: !CFG_REPO_PATH!
)

REM ============================================================
REM  Paso 7 - Shortcut en escritorio
REM ============================================================
echo.
echo [7/7] Creando acceso directo en escritorio...
powershell -NoProfile -Command ^
    "$ws = New-Object -ComObject WScript.Shell;" ^
    "$sc = $ws.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\TarroBot.lnk');" ^
    "$sc.TargetPath = '%ROOT%\TarroBot.bat';" ^
    "$sc.WorkingDirectory = '%ROOT%';" ^
    "$sc.IconLocation = '%SystemRoot%\System32\shell32.dll,13';" ^
    "$sc.Description = 'TarroBot Studio - Asistente Retrotarros';" ^
    "$sc.Save()"

if exist "%USERPROFILE%\Desktop\TarroBot.lnk" (
    echo [OK] Acceso directo creado: %USERPROFILE%\Desktop\TarroBot.lnk
) else (
    echo [WARN] No se pudo crear shortcut. Podes arrancar manual desde TarroBot.bat
)

REM ============================================================
REM  Soundfont para melodias MIDI (instruccion solamente)
REM ============================================================
echo.
echo ------------------------------------------------------------
echo NOTA: Soundfont para melodias MIDI
echo ------------------------------------------------------------
echo Para que TarroBot toque melodias MIDI necesitas un soundfont
echo .sf2. NO se incluye por temas de derechos (las melodias son
echo transcripciones fan de juegos comerciales).
echo.
echo Opciones recomendadas:
echo   - GeneralUser GS (CC0, libre):
echo     https://www.schristiancollins.com/generaluser.php
echo   - SNES soundfont: buscar en archive.org
echo.
echo Una vez bajado:
echo   1. Renombralo a "soundfont.sf2"
echo   2. Copialo a: %ROOT%\studio\melodias\soundfont.sf2
echo      (o al repo en Drive si usas modo Drive)
echo.
echo Sin soundfont, TarroBot anda perfecto para todo lo demas.
echo (Esto es opcional, podes hacerlo despues sin reinstalar.)
echo.

REM ============================================================
REM  FIN
REM ============================================================
echo.
>>"!LOGFILE!" echo [fin] instalacion completa OK
echo ============================================================
echo   INSTALACION COMPLETA
echo ============================================================
echo.
echo Bitacora de esta instalacion guardada en:
echo   %LOGFILE%
echo   %PIPLOG%  (detalle de dependencias)
echo.
echo Para arrancar TarroBot:
echo   - Doble click en el acceso directo TarroBot del escritorio
echo   - O doble click en TarroBot.bat
echo.
echo Al arrancar:
echo   - Aparece un icono en la bandeja del sistema (al lado del reloj)
echo   - Click derecho en el icono para abrir TV / panel / overlay OBS
echo   - O abre manual http://localhost:8765 en el browser
echo.
echo Nota importante:
echo   - Las variables de entorno (API key, repo path) se aplican en
echo     NUEVAS terminales. Si abriste algo antes, cerralo y vuelve a abrir.
echo.
echo Documentacion completa: README-ESTUDIO.txt en esta carpeta.
echo.
pause
endlocal
