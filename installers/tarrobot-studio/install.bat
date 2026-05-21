@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM ============================================================
REM  TarroBot Studio - Instalador automatico para Windows 10/11
REM  Retrotarros · doble click y listo
REM ============================================================

title TarroBot Studio - Instalando...
color 0B

echo.
echo ============================================================
echo   TARROBOT STUDIO - INSTALADOR
echo ============================================================
echo.
echo Esto va a hacer:
echo   1. Instalar Python si no esta (silencioso)
echo   2. Crear entorno virtual aislado en esta carpeta
echo   3. Instalar dependencias (FastAPI, Whisper, edge-tts, anthropic)
echo   4. Descargar ffmpeg portable
echo   5. Pedirte tu API key de Anthropic
echo   6. Configurar el repo Retrotarros (Drive sincronizado o local)
echo   7. Descargar FluidSynth portable (para tocar melodias MIDI)
echo   8. Crear acceso directo en escritorio
echo.
echo Espacio en disco necesario: ~800 MB
echo Tiempo estimado: 5-10 minutos (depende de tu conexion)
echo.
pause

REM ─── Carpeta de instalacion = la carpeta del .bat ─────────────
set "ROOT=%~dp0"
set "ROOT=%ROOT:~0,-1%"
cd /d "%ROOT%"

REM ─── Paso 1: Python ───────────────────────────────────────────
echo.
echo [1/8] Verificando Python...
where python >nul 2>nul
if !errorlevel! equ 0 (
    for /f "tokens=2" %%v in ('python --version 2^>^&1') do set "PY_VER=%%v"
    echo [OK] Python ya instalado: !PY_VER!
) else (
    echo [INFO] Python no encontrado. Descargando Python 3.12.7...
    curl -L -o python-installer.exe https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe
    if !errorlevel! neq 0 (
        echo [ERROR] No se pudo descargar Python. Verifica tu conexion a internet.
        pause
        exit /b 1
    )
    echo [INFO] Instalando Python (modo silencioso, solo para tu usuario)...
    python-installer.exe /quiet InstallAllUsers=0 PrependPath=1 Include_test=0 Include_pip=1
    if !errorlevel! neq 0 (
        echo [ERROR] La instalacion de Python fallo.
        pause
        exit /b 1
    )
    del python-installer.exe
    REM Agregar Python al PATH de esta sesion
    set "PATH=%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts;!PATH!"
    echo [OK] Python instalado.
)

REM ─── Paso 2: Crear entorno virtual ────────────────────────────
echo.
echo [2/8] Creando entorno virtual (.venv)...
if exist ".venv" (
    echo [OK] .venv ya existe, saltando.
) else (
    python -m venv .venv
    if !errorlevel! neq 0 (
        echo [ERROR] No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
    echo [OK] .venv creado.
)

REM ─── Paso 3: Instalar dependencias Python ─────────────────────
echo.
echo [3/8] Instalando dependencias Python (puede tardar 2-5 min)...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul
pip install -r requirements.txt
if !errorlevel! neq 0 (
    echo [ERROR] Fallo la instalacion de dependencias.
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas.

REM ─── Paso 4: ffmpeg portable ──────────────────────────────────
echo.
echo [4/8] Verificando ffmpeg...
if exist "bin\ffmpeg.exe" (
    echo [OK] ffmpeg ya esta.
) else (
    echo [INFO] Descargando ffmpeg portable (~70 MB)...
    if not exist "bin" mkdir bin
    curl -L -o ffmpeg.zip https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip
    if !errorlevel! neq 0 (
        echo [ERROR] No se pudo descargar ffmpeg.
        pause
        exit /b 1
    )
    echo [INFO] Extrayendo...
    powershell -NoProfile -Command "Expand-Archive -Path ffmpeg.zip -DestinationPath ffmpeg-temp -Force"
    REM Buscar ffmpeg.exe en cualquier subcarpeta
    for /r "ffmpeg-temp" %%f in (ffmpeg.exe) do (
        copy "%%f" "bin\ffmpeg.exe" >nul
        goto :ffmpeg_done
    )
    :ffmpeg_done
    rmdir /s /q ffmpeg-temp
    del ffmpeg.zip
    if exist "bin\ffmpeg.exe" (
        echo [OK] ffmpeg listo en bin\ffmpeg.exe
    ) else (
        echo [ERROR] No se pudo extraer ffmpeg. Bajalo manual de github.com/BtbN/FFmpeg-Builds
        pause
        exit /b 1
    )
)

REM ─── Paso 5: API Key de Anthropic ─────────────────────────────
echo.
echo [5/8] Configurando API key de Anthropic...
echo.
echo Necesitas una API key de https://console.anthropic.com/settings/keys
echo Te recomiendo crear una llamada "tarrobot-studio" especifica para este PC.
echo La key empieza con sk-ant-api03-...
echo.
set /p ANTKEY="Pega tu API key (o presiona Enter para configurarla despues): "
if defined ANTKEY (
    setx ANTHROPIC_API_KEY "!ANTKEY!" >nul
    echo [OK] API key guardada como variable de entorno User.
    echo      Tendras que reabrir CMD/PowerShell para que tome efecto.
) else (
    echo [WARN] API key no configurada. Solo podras usar datos curados de la DB,
    echo        sin opinar ni cuentame con LLM. Configurala manual con:
    echo        setx ANTHROPIC_API_KEY "sk-ant-..."
)

REM ─── Paso 6: Configurar repo Retrotarros ──────────────────────
echo.
echo [6/8] Configurando ubicacion del repo Retrotarros...
echo.
echo TarroBot puede leer pautas, datos y templates desde:
echo   A) El paquete local (esta carpeta) - autocontenido, sin internet
echo   B) Tu repo en Google Drive sincronizado - se actualiza solo
echo.
echo Si pegas la ruta del repo en Drive, vas a ver automaticamente
echo las pautas y datos nuevos que Luis genere en su PC.
echo.
echo Ejemplos de ruta valida:
echo   G:\Mi unidad\Recursos Retrotarros\repo
echo   C:\Users\Estudio\Google Drive\Retrotarros\repo
echo   D:\Drive\Retrotarros\repo
echo.
set /p REPOPATH="Ruta al repo Retrotarros (o presiona Enter para usar local): "
if defined REPOPATH (
    REM Limpiar comillas si las pego con drag-drop
    set "REPOPATH=!REPOPATH:"=!"
    if exist "!REPOPATH!\scripts\tarrobot-live.py" (
        if exist "!REPOPATH!\data\tarrobot-database.json" (
            setx RETROTARROS_REPO "!REPOPATH!" >nul
            echo [OK] Repo Retrotarros configurado: !REPOPATH!
            echo      TarroBot va a leer scripts, pautas y datos desde ahi.
        ) else (
            echo [WARN] La ruta no parece un repo valido (falta data\tarrobot-database.json^).
            echo        Usando paquete local.
        )
    ) else (
        echo [WARN] La ruta no parece un repo valido (falta scripts\tarrobot-live.py^).
        echo        Usando paquete local.
    )
) else (
    echo [OK] Usando paquete local. Puedes configurarlo despues con:
    echo      setx RETROTARROS_REPO "ruta al repo"
)

REM ─── Paso 7: FluidSynth portable + soundfont (melodias MIDI) ──
echo.
echo [7/8] Configurando FluidSynth para tocar melodias MIDI...
if exist "bin\fluidsynth.exe" (
    echo [OK] FluidSynth ya esta en bin\fluidsynth.exe
) else (
    echo [INFO] Descargando FluidSynth 2.3.5 portable (~25 MB)...
    if not exist "bin" mkdir bin
    curl -L -o fluidsynth.zip https://github.com/FluidSynth/fluidsynth/releases/download/v2.3.5/fluidsynth-2.3.5-win10-x64.zip
    if !errorlevel! neq 0 (
        echo [WARN] No se pudo descargar FluidSynth. Las melodias MIDI no van a funcionar.
        echo        Puedes bajarlo manual de github.com/FluidSynth/fluidsynth/releases
        echo        y copiar bin\fluidsynth.exe + las DLLs en esta carpeta\bin\
        goto :fluidsynth_done
    )
    echo [INFO] Extrayendo FluidSynth...
    powershell -NoProfile -Command "Expand-Archive -Path fluidsynth.zip -DestinationPath fluidsynth-temp -Force"
    REM Copiar fluidsynth.exe + todas las DLLs necesarias a bin\
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

REM ─── Soundfont SNES (no se baja automatico por temas de derechos) ─
echo.
echo Para tocar melodias necesitas un soundfont .sf2 ^(formato estandar^).
echo Opciones recomendadas ^(libres / fair use^):
echo   - GeneralUser GS:  schristiancollins.com/generaluser.php  ^(~30 MB, CC0^)
echo   - SNES soundfont:  buscar "Super Nintendo Soundfont" sf2
echo.
echo Una vez que tengas el .sf2:
echo   1. Renombralo a "soundfont.sf2"
echo   2. Copialo a:  %ROOT%\studio\melodias\soundfont.sf2
echo      ^(o al repo en Drive si usas modo Drive^)
echo.
echo Sin el soundfont, las melodias MIDI no van a funcionar pero el
echo resto de TarroBot anda perfecto.
echo.
pause

REM ─── Paso 8: Crear shortcut en escritorio ─────────────────────
echo.
echo [8/8] Creando acceso directo en escritorio...
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
    echo [WARN] No se pudo crear shortcut. Podes arrancar manualmente desde TarroBot.bat
)

REM ─── Fin ──────────────────────────────────────────────────────
echo.
echo ============================================================
echo   INSTALACION COMPLETA
echo ============================================================
echo.
echo Para arrancar TarroBot:
echo   - Doble click en el acceso directo del escritorio
echo   - O doble click en TarroBot.bat
echo.
echo Al arrancar:
echo   - Se abre el navegador con TarroBot en pantalla completa
echo   - Para controlarlo, abre http://localhost:8765/control en otra pestana
echo     (o desde el celu: http://[IP-DE-ESTA-PC]:8765/control)
echo.
echo Nota: la primera vez que uses voz, Whisper descarga el modelo
echo       (244 MB) y tarda un poco. Despues queda en cache.
echo.
pause
endlocal
