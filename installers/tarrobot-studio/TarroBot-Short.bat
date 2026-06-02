@echo off
REM ============================================================
REM TarroShort - genera un MP4 vertical 1080x1920 para redes
REM Sprint 19 - Retrotarros Studio Suite
REM ============================================================
REM
REM Toma un HTML de short (studio\tarroshort-<tema>.html), hace que
REM TarroBot lo lea con su voz y su cara moviendose, y arma el video
REM vertical listo para llevar a CapCut (tu le pones la musica).
REM
REM Output: <app>\studio\shorts\<slug>.mp4
REM
REM Tip: la voz de cada escena queda en studio\shorts\audio\<slug>\.
REM      Si reemplazas un MP3 por tu propia narracion y vuelves a correr,
REM      usa ese audio en vez de regenerarlo.
REM ============================================================

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo =====================================================
echo   TARROSHORT - Retrotarros Studio Suite
echo =====================================================
echo.

REM Detectar python (venv de install.bat o sistema)
set PYEXE=python
if exist ".venv\Scripts\python.exe" set PYEXE=.venv\Scripts\python.exe

REM Listar shorts disponibles
echo Shorts disponibles en studio\:
echo ----------------------------------------
if exist "studio" (
    for %%f in (studio\tarroshort-*.html) do (
        set FNAME=%%~nf
        echo   - !FNAME!
    )
) else (
    echo   (no hay shorts; copia studio\_template-tarroshort.html primero)
)
echo ----------------------------------------
echo.

if "%~1"=="" (
    set /p SLUG="Slug del short (ej. tarroshort-snes-top-precios): "
    set SLUG=!SLUG:"=!
) else (
    set SLUG=%~1
)

if "!SLUG!"=="" (
    echo ERROR: slug requerido
    pause
    exit /b 1
)

echo.
echo =====================================================
echo   Generando el video... TarroBot leyendo cada escena.
echo =====================================================
echo   Slug: !SLUG!
echo.
echo   Esto demora un par de minutos (graba cada escena + voz).
echo   La primera vez puede bajar el navegador de Playwright.
echo.

"%PYEXE%" scripts\tarroshort_render.py "!SLUG!"
set EXITCODE=%ERRORLEVEL%

echo.
if !EXITCODE!==0 (
    echo =====================================================
    echo   LISTO. El video quedo en studio\shorts\!SLUG!.mp4
    echo =====================================================
    if exist "studio\shorts" (
        start "" "studio\shorts"
    )
) else (
    echo =====================================================
    echo   ERROR: TarroShort fallo (codigo !EXITCODE!)
    echo =====================================================
    echo Revisa el log de arriba para detalles.
)

echo.
pause
endlocal
