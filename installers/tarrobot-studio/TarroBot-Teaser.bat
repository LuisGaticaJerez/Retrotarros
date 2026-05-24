@echo off
REM ============================================================
REM TarroTeaser - genera Short vertical 1080x1920 desde master
REM Sprint 17 - Retrotarros Studio Suite
REM ============================================================
REM
REM Te pide el video MP4 del episodio + el slug, y genera un teaser
REM crudo de ~15-30 segundos con clips reales del master detectados
REM por Whisper. Listo para llevar a CapCut / DaVinci.
REM
REM Output: <app>\studio\teasers\<slug>\<slug>-tarroteaser-YYYYMMDD.mp4
REM
REM Tips:
REM   - Podes arrastrar el MP4 sobre este .bat: lo recibe como %1
REM   - Si no pasas argumento, te lo pregunta
REM ============================================================

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo =====================================================
echo   TARROTEASER - Retrotarros Studio Suite
echo =====================================================
echo.

REM Detectar python (de install.bat venv o sistema)
set PYEXE=python
if exist ".venv\Scripts\python.exe" set PYEXE=.venv\Scripts\python.exe

REM Detectar video: argumento o prompt
if "%~1"=="" (
    set /p VIDEO="Ruta al video MP4 del episodio: "
    REM Si el usuario pego con comillas, sacalas
    set VIDEO=!VIDEO:"=!
) else (
    set VIDEO=%~1
)

if not exist "!VIDEO!" (
    echo.
    echo ERROR: no existe el archivo "!VIDEO!"
    echo.
    pause
    exit /b 1
)

REM Listar pautas disponibles para sugerir slugs
echo.
echo Pautas disponibles en studio\pautas\:
echo ----------------------------------------
if exist "studio\pautas" (
    for %%f in (studio\pautas\*.tarrobot.json) do (
        set FNAME=%%~nf
        set FNAME=!FNAME:.tarrobot=!
        echo   - !FNAME!
    )
) else (
    echo   (no hay pautas locales, podes pasar cualquier slug kebab-case)
)
echo ----------------------------------------
echo.

set /p SLUG="Slug del episodio (ej. n64-top-precios): "

if "!SLUG!"=="" (
    echo ERROR: slug requerido
    pause
    exit /b 1
)

echo.
echo =====================================================
echo   Lanzando TarroTeaser...
echo =====================================================
echo   Video: !VIDEO!
echo   Slug : !SLUG!
echo.
echo   Esto puede demorar 5-10 min (Whisper transcribe el master).
echo   La primera vez baja el modelo whisper-small (~250 MB).
echo.

"%PYEXE%" scripts\tarroteaser.py "!VIDEO!" --slug !SLUG!
set EXITCODE=%ERRORLEVEL%

echo.
if !EXITCODE!==0 (
    echo =====================================================
    echo   LISTO. El teaser quedo en studio\teasers\!SLUG!\
    echo =====================================================
    REM Abrir el folder de salida
    if exist "studio\teasers\!SLUG!" (
        start "" "studio\teasers\!SLUG!"
    )
) else (
    echo =====================================================
    echo   ERROR: TarroTeaser fallo (codigo !EXITCODE!)
    echo =====================================================
    echo Revisa el log de arriba para detalles.
)

echo.
pause
endlocal
