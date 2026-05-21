@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM Modo silencioso: arranca tarrobot-tray.py con pythonw (sin cmd visible).
REM Si necesitas ver logs, usa TarroBot-debug.bat en lugar de este.

set "ROOT=%~dp0"
set "ROOT=%ROOT:~0,-1%"
cd /d "%ROOT%"

REM Verificar que el setup este hecho
if not exist ".venv\Scripts\pythonw.exe" (
    echo [ERROR] El entorno virtual no existe. Corre install.bat primero.
    pause
    exit /b 1
)

REM Cargar RETROTARROS_REPO User si esta definida (modo Drive)
for /f "tokens=*" %%r in ('powershell -NoProfile -Command "[Environment]::GetEnvironmentVariable('RETROTARROS_REPO','User')"') do set "RETROTARROS_REPO=%%r"

REM Decidir desde donde corren los scripts: Drive si esta configurado, sino local
if defined RETROTARROS_REPO (
    if exist "!RETROTARROS_REPO!\scripts\tarrobot-tray.py" (
        set "SCRIPT_DIR=!RETROTARROS_REPO!\scripts"
    ) else (
        set "SCRIPT_DIR=%ROOT%\scripts"
        set "RETROTARROS_REPO="
    )
) else (
    set "SCRIPT_DIR=%ROOT%\scripts"
)

if not exist "!SCRIPT_DIR!\tarrobot-tray.py" (
    echo [ERROR] Faltan archivos. Reinstala o configura RETROTARROS_REPO.
    pause
    exit /b 1
)

REM Agregar bin\ (ffmpeg, fluidsynth) al PATH si existe
if exist "bin\ffmpeg.exe" set "PATH=%ROOT%\bin;%PATH%"

REM Cargar la API key User si esta
for /f "tokens=*" %%k in ('powershell -NoProfile -Command "[Environment]::GetEnvironmentVariable('ANTHROPIC_API_KEY','User')"') do set "ANTHROPIC_API_KEY=%%k"

REM Arrancar TarroBot en modo tray (sin ventana cmd visible)
REM pythonw.exe no muestra consola. El icono aparece en la bandeja del sistema.
start "" ".venv\Scripts\pythonw.exe" "!SCRIPT_DIR!\tarrobot-tray.py"

endlocal
