# install-dev-tools.ps1
# Instala todos los CLIs necesarios para desarrollo con Claude Code
# Ejecutar desde PowerShell como administrador:
#   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
#   .\scripts\install-dev-tools.ps1

param(
    [switch]$Android,   # incluir tools Android/Capacitor
    [switch]$All        # instalar absolutamente todo
)

Write-Host "`n=== Instalando CLIs de desarrollo ===" -ForegroundColor Cyan

# --- Verificar winget ---
if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Host "winget no encontrado. Instálalo desde Microsoft Store: 'App Installer'" -ForegroundColor Red
    exit 1
}

function Install-If-Missing {
    param($Name, $WingetId, $CheckCmd, $PostMsg)
    Write-Host "`n[$Name]" -ForegroundColor Yellow
    if (Get-Command $CheckCmd -ErrorAction SilentlyContinue) {
        $ver = & $CheckCmd --version 2>&1 | Select-Object -First 1
        Write-Host "  ya instalado: $ver" -ForegroundColor Green
    } else {
        winget install --id $WingetId --silent --accept-package-agreements --accept-source-agreements
        if ($PostMsg) { Write-Host "  $PostMsg" -ForegroundColor Cyan }
        Write-Host "  OK" -ForegroundColor Green
    }
}

function Install-Npm-If-Missing {
    param($Name, $Package, $CheckCmd, $PostMsg)
    Write-Host "`n[$Name]" -ForegroundColor Yellow
    if (Get-Command $CheckCmd -ErrorAction SilentlyContinue) {
        $ver = & $CheckCmd --version 2>&1 | Select-Object -First 1
        Write-Host "  ya instalado: $ver" -ForegroundColor Green
    } else {
        npm install -g $Package --legacy-peer-deps
        if ($PostMsg) { Write-Host "  $PostMsg" -ForegroundColor Cyan }
        Write-Host "  OK" -ForegroundColor Green
    }
}

# ============================================================
# CORE — siempre se instalan
# ============================================================

Install-If-Missing "Git" "Git.Git" "git"
Install-If-Missing "GitHub CLI (gh)" "GitHub.cli" "gh" "Pendiente: gh auth login"
Install-If-Missing "Node.js LTS" "OpenJS.NodeJS.LTS" "node"

# Refrescar PATH tras posible instalacion de Node
$env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")

# Supabase CLI: npm global NO soportado. winget o npx.
Write-Host "`n[Supabase CLI]" -ForegroundColor Yellow
$supVer = npx supabase --version 2>&1
if ($supVer -match "\d+\.\d+") {
    Write-Host "  disponible via npx: $supVer" -ForegroundColor Green
    Write-Host "  Agrega alias a tu `$PROFILE: function supabase { npx supabase @args }" -ForegroundColor Cyan
} else {
    winget install --id Supabase.CLI --silent --accept-package-agreements --accept-source-agreements
}
Write-Host "  Pendiente: npx supabase login" -ForegroundColor Cyan
Install-Npm-If-Missing "Netlify CLI" "netlify-cli" "netlify" "Pendiente: netlify login"
Install-Npm-If-Missing "TypeScript (tsc)" "typescript" "tsc"
Install-Npm-If-Missing "Vite" "vite" "vite"

# ============================================================
# FIREBASE — push notifications, FCM
# ============================================================

Write-Host "`n[Firebase CLI]" -ForegroundColor Yellow
if (Get-Command firebase -ErrorAction SilentlyContinue) {
    Write-Host "  ya instalado: $(firebase --version)" -ForegroundColor Green
} else {
    npm install -g firebase-tools --legacy-peer-deps
    Write-Host "  Pendiente: firebase login" -ForegroundColor Cyan
    Write-Host "  OK" -ForegroundColor Green
}

# ============================================================
# ANDROID / CAPACITOR — solo si -Android o -All
# ============================================================

if ($Android -or $All) {
    Write-Host "`n=== Tools Android/Capacitor ===" -ForegroundColor Cyan

    # Java JDK (requerido por Android SDK)
    Install-If-Missing "Java JDK 17" "EclipseAdoptium.Temurin.17.JDK" "java" "Reinicia PowerShell tras instalar"

    # Android Studio (incluye SDK, adb, gradle)
    Write-Host "`n[Android Studio + SDK + adb]" -ForegroundColor Yellow
    if (Get-Command adb -ErrorAction SilentlyContinue) {
        Write-Host "  adb ya disponible: $(adb --version | Select-Object -First 1)" -ForegroundColor Green
    } else {
        Write-Host "  Instalando Android Studio (puede tardar varios minutos)..." -ForegroundColor Yellow
        winget install --id Google.AndroidStudio --silent --accept-package-agreements --accept-source-agreements
        Write-Host "  Tras instalar Android Studio, abre SDK Manager y descarga:" -ForegroundColor Cyan
        Write-Host "    - Android SDK Platform 34" -ForegroundColor Cyan
        Write-Host "    - Android SDK Build-Tools" -ForegroundColor Cyan
        Write-Host "    - Android SDK Platform-Tools (incluye adb)" -ForegroundColor Cyan
    }

    # Capacitor CLI
    Install-Npm-If-Missing "Capacitor CLI" "@capacitor/cli" "cap"
}

# ============================================================
# EXTRAS UTILES — solo si -All
# ============================================================

if ($All) {
    Write-Host "`n=== Extras utiles ===" -ForegroundColor Cyan

    # Deno (desarrollo local de Supabase Edge Functions)
    Install-If-Missing "Deno" "DenoLand.Deno" "deno"

    # jq (procesar JSON en terminal — util para scripts de BD)
    Install-If-Missing "jq" "jqlang.jq" "jq"

    # curl (ya viene en Windows 11 pero por si acaso)
    Write-Host "`n[curl]" -ForegroundColor Yellow
    if (Get-Command curl -ErrorAction SilentlyContinue) {
        Write-Host "  ya instalado" -ForegroundColor Green
    } else {
        winget install --id curl.curl --silent --accept-package-agreements --accept-source-agreements
    }
}

# ============================================================
# RESUMEN
# ============================================================

Write-Host "`n=== Instalacion completada ===" -ForegroundColor Cyan
Write-Host "Cierra y vuelve a abrir PowerShell para actualizar el PATH."
Write-Host "`nPasos de autenticacion pendientes:"
Write-Host "  gh auth login          <- GitHub (elige: HTTPS + browser)"
Write-Host "  supabase login         <- Supabase"
Write-Host "  netlify login          <- Netlify"
Write-Host "  firebase login         <- Firebase/FCM"
Write-Host "`nUso del script:"
Write-Host "  .\install-dev-tools.ps1              <- core solamente"
Write-Host "  .\install-dev-tools.ps1 -Android     <- core + Android/Capacitor"
Write-Host "  .\install-dev-tools.ps1 -All         <- todo"
