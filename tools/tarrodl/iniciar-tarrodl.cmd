@echo off
rem Abre TarroDL sin ventana de consola usando el Python instalado.
rem Alternativa al TarroDL.exe: Smart App Control de Windows puede bloquear un .exe sin firma.
rem Los argumentos se pasan tal cual (ej. --no-browser --port 8765 para pruebas).
cd /d "%~dp0"
where pythonw >nul 2>nul
if %errorlevel%==0 (
    start "" pythonw tarrodl.py %*
    exit /b 0
)
where pyw >nul 2>nul
if %errorlevel%==0 (
    start "" pyw tarrodl.py %*
    exit /b 0
)
echo No encuentro Python (pythonw). Instala Python o usa dist\TarroDL.exe.
pause
