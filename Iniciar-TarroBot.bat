@echo off
chcp 65001 >nul
cd /d "%~dp0"
title TarroBot - PC de Edicion

REM ============================================================
REM  TarroBot desde el repo (PC de EDICION)
REM ============================================================
REM  Este PC ya tiene Python + Playwright + ffmpeg + edge-tts, asi
REM  que NO necesita el instalador. Corre TarroBot directo del repo.
REM
REM  Sirve para generar TarroShort / TarroTeaser / publicaciones
REM  mientras el OTRO PC (estudio) graba en vivo. Puertos separados
REM  por ser maquinas distintas: no hay conflicto.
REM ============================================================

echo ============================================================
echo   TARROBOT - PC de Edicion
echo ============================================================
echo.
echo   Panel de control:  http://localhost:8765/control
echo   (se abre solo en unos segundos)
echo.
echo   Deja esta ventana abierta mientras trabajas.
echo   Cierrala (o Ctrl+C) para apagar TarroBot.
echo.

REM Abrir el panel en el browser cuando el server este arriba (~5s)
start "" cmd /c "timeout /t 5 >nul & start http://localhost:8765/control"

REM Levantar el server con el Python de sistema (consola visible = ves logs)
python scripts\tarrobot-live.py

echo.
echo TarroBot se detuvo.
pause
