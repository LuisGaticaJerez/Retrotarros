@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

title TarroBot Studio - Arrancando...
color 0B

set "ROOT=%~dp0"
set "ROOT=%ROOT:~0,-1%"
cd /d "%ROOT%"

REM Verificar que el setup este hecho
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] El entorno virtual no existe. Corre install.bat primero.
    pause
    exit /b 1
)

REM Cargar RETROTARROS_REPO User si esta definida (modo Drive)
for /f "tokens=*" %%r in ('powershell -NoProfile -Command "[Environment]::GetEnvironmentVariable('RETROTARROS_REPO','User')"') do set "RETROTARROS_REPO=%%r"

REM Decidir desde donde corren los scripts: Drive si esta configurado, sino local
if defined RETROTARROS_REPO (
    if exist "!RETROTARROS_REPO!\scripts\tarrobot-live.py" (
        set "SCRIPT_DIR=!RETROTARROS_REPO!\scripts"
        echo [INFO] Usando repo desde Drive: !RETROTARROS_REPO!
    ) else (
        echo [WARN] RETROTARROS_REPO definido pero la ruta no es valida.
        echo        Fallback a paquete local.
        set "SCRIPT_DIR=%ROOT%\scripts"
        set "RETROTARROS_REPO="
    )
) else (
    set "SCRIPT_DIR=%ROOT%\scripts"
)

if not exist "!SCRIPT_DIR!\tarrobot-live.py" (
    echo [ERROR] Faltan los archivos del repo. Reinstala el paquete completo
    echo         o configura RETROTARROS_REPO apuntando a un repo valido.
    pause
    exit /b 1
)

REM Agregar ffmpeg al PATH si existe
if exist "bin\ffmpeg.exe" set "PATH=%ROOT%\bin;%PATH%"

REM Cargar la API key User si esta
for /f "tokens=*" %%k in ('powershell -NoProfile -Command "[Environment]::GetEnvironmentVariable('ANTHROPIC_API_KEY','User')"') do set "ANTHROPIC_API_KEY=%%k"

if "!ANTHROPIC_API_KEY!"=="" (
    echo [WARN] ANTHROPIC_API_KEY no esta configurada.
    echo        Vas a poder usar datos curados pero no opinar ni cuentame con Claude.
    echo        Para configurarla: setx ANTHROPIC_API_KEY "sk-ant-..."
    echo.
    timeout /t 3 >nul
)

echo.
echo ============================================================
echo   TARROBOT STUDIO - EN VIVO
echo ============================================================
echo.
echo Arrancando server FastAPI...
echo.
echo Cuando aparezca "Application startup complete":
echo   - Se abrira el browser con TarroBot en pantalla completa
echo   - Para controlarlo: http://localhost:8765/control
echo.
echo Para cerrar: Ctrl+C en esta ventana.
echo.

REM Detectar IP local para mostrarla
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr /R /C:"IPv4.*192\.168" /C:"IPv4.*10\." ^| findstr /V "169\.254"') do (
    set "LOCALIP=%%i"
    set "LOCALIP=!LOCALIP: =!"
    goto :found_ip
)
:found_ip
if defined LOCALIP (
    echo Tu IP local: !LOCALIP!
    echo Panel desde el celu: http://!LOCALIP!:8765/control
    echo.
)

REM Arrancar el browser en pantalla completa despues de 4s (en paralelo)
start "" /b cmd /c "timeout /t 4 >nul && start chrome --new-window --kiosk http://localhost:8765/?mode=fullscreen"

REM Arrancar server (bloqueante - el bat se cierra cuando matas el server)
call .venv\Scripts\activate.bat
python "!SCRIPT_DIR!\tarrobot-live.py"

echo.
echo TarroBot detenido.
pause
endlocal
