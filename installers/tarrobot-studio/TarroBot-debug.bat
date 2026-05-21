@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

title TarroBot Studio - DEBUG (consola visible)
color 0E

REM Modo DEBUG: muestra la consola con todos los logs del server + Whisper.
REM Usar cuando algo no anda y necesitas ver que pasa.
REM Para el dia a dia, usa TarroBot.bat (modo silencioso con tray icon).

set "ROOT=%~dp0"
set "ROOT=%ROOT:~0,-1%"
cd /d "%ROOT%"

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] El entorno virtual no existe. Corre install.bat primero.
    pause
    exit /b 1
)

REM Cargar RETROTARROS_REPO User si esta definida (modo Drive)
for /f "tokens=*" %%r in ('powershell -NoProfile -Command "[Environment]::GetEnvironmentVariable('RETROTARROS_REPO','User')"') do set "RETROTARROS_REPO=%%r"

if defined RETROTARROS_REPO (
    if exist "!RETROTARROS_REPO!\scripts\tarrobot-live.py" (
        set "SCRIPT_DIR=!RETROTARROS_REPO!\scripts"
        echo [INFO] Usando repo desde Drive: !RETROTARROS_REPO!
    ) else (
        set "SCRIPT_DIR=%ROOT%\scripts"
    )
) else (
    set "SCRIPT_DIR=%ROOT%\scripts"
)

if not exist "!SCRIPT_DIR!\tarrobot-live.py" (
    echo [ERROR] Faltan archivos. Reinstala o configura RETROTARROS_REPO.
    pause
    exit /b 1
)

if exist "bin\ffmpeg.exe" set "PATH=%ROOT%\bin;%PATH%"

for /f "tokens=*" %%k in ('powershell -NoProfile -Command "[Environment]::GetEnvironmentVariable('ANTHROPIC_API_KEY','User')"') do set "ANTHROPIC_API_KEY=%%k"

if "!ANTHROPIC_API_KEY!"=="" (
    echo [WARN] ANTHROPIC_API_KEY no esta configurada.
    echo        Vas a poder usar datos curados pero no opinar ni cuentame.
    echo.
    timeout /t 3 >nul
)

echo.
echo ============================================================
echo   TARROBOT STUDIO - MODO DEBUG (logs visibles)
echo ============================================================
echo.

REM Detectar IP local
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

REM Arrancar browser en kiosk despues de 4s
start "" /b cmd /c "timeout /t 4 >nul && start chrome --new-window --kiosk http://localhost:8765/?mode=fullscreen"

call .venv\Scripts\activate.bat
python "!SCRIPT_DIR!\tarrobot-live.py"

echo.
echo TarroBot detenido.
pause
endlocal
