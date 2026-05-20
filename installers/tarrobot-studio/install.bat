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
echo   6. Crear acceso directo en escritorio
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
echo [1/6] Verificando Python...
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
echo [2/6] Creando entorno virtual (.venv)...
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
echo [3/6] Instalando dependencias Python (puede tardar 2-5 min)...
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
echo [4/6] Verificando ffmpeg...
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
echo [5/6] Configurando API key de Anthropic...
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

REM ─── Paso 6: Crear shortcut en escritorio ─────────────────────
echo.
echo [6/6] Creando acceso directo en escritorio...
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
