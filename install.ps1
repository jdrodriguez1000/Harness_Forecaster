# FARO - Script de instalacion en maquina nueva
# Uso: irm https://raw.githubusercontent.com/jdrodriguez1000/Harness_Forecaster/main/install.ps1 | iex

$repo   = "https://github.com/jdrodriguez1000/Harness_Forecaster.git"
$folder = "Harness_Forecaster"

Write-Host "=== FARO Installer ===" -ForegroundColor Cyan
Write-Host "Destino: $(Get-Location)\$folder"
Write-Host ""

# --- Clonar repo ---
if (Test-Path $folder) {
    Write-Host "[SKIP] '$folder' ya existe - omitiendo clone" -ForegroundColor Yellow
} else {
    Write-Host "Clonando FARO desde GitHub..." -ForegroundColor White
    git clone $repo $folder
    if (-not $?) {
        Write-Host "[ERROR] git clone fallo. Verifica tu conexion y que git este instalado." -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# --- Ejecutar setup ---
$faroHome    = Join-Path (Get-Location).Path $folder
$setupScript = Join-Path $faroHome "faro-setup.ps1"

Write-Host "Ejecutando faro-setup.ps1..." -ForegroundColor White
& $setupScript -FaroHome $faroHome

Write-Host ""
Write-Host "=== FARO instalado correctamente ===" -ForegroundColor Green
Write-Host "Abre Claude Code en la carpeta de un proyecto cliente y escribe /faro-init" -ForegroundColor Cyan
