#Requires -Version 5.1
# FARO — Instalacion de proyecto
# Uso: & "C:\path\to\Harness_Forecaster\faro-setup.ps1"
# Ejecutar desde la carpeta raiz del nuevo proyecto cliente.

$ErrorActionPreference = 'Stop'

$repo    = $PSScriptRoot
$destino = (Get-Location).Path

Write-Host ""
Write-Host "=== faro-setup.ps1 ===" -ForegroundColor Cyan
Write-Host "Repo   : $repo"
Write-Host "Destino: $destino"
Write-Host ""

# --- Deteccion de estado ---

$claudeDir     = Join-Path $destino '.claude'
$esNuevo       = -not (Test-Path $claudeDir)
$harnessActivo = Test-Path (Join-Path $destino '600_persistence')

# Detectar contenido ajeno a FARO en .claude/agents/
if (-not $esNuevo) {
    $agentsDir = Join-Path $claudeDir 'agents'
    if (Test-Path $agentsDir) {
        $ajenoAgentes = Get-ChildItem $agentsDir -File | Where-Object { $_.Name -notlike 'discovery-*.md' }
        if ($ajenoAgentes) {
            Write-Host "[AVISO] Se detectaron archivos en .claude/agents/ que no pertenecen a FARO:" -ForegroundColor Yellow
            $ajenoAgentes | ForEach-Object { Write-Host "        - $($_.Name)" -ForegroundColor Yellow }
            Write-Host ""
            $resp = Read-Host "Continuar y sobreescribir? (s/n)"
            if ($resp.Trim().ToLower() -ne 's') {
                Write-Host "Instalacion cancelada." -ForegroundColor Red
                exit 0
            }
            Write-Host ""
        }
    }
}

if ($harnessActivo) {
    Write-Host "[AVISO] Harness activo detectado (600_persistence/ existe)." -ForegroundColor Yellow
    Write-Host "        Agentes y skills seran actualizados. Carpetas de runtime no seran tocadas." -ForegroundColor Yellow
    Write-Host ""
}

# --- Crear estructura .claude ---

foreach ($d in @('agents','skills','commands','workflows')) {
    New-Item -ItemType Directory -Force (Join-Path $claudeDir $d) | Out-Null
}

# --- Agentes (siempre sobreescribir) ---

$origenAgentes = Join-Path $repo '.claude\agents'
$destAgentes   = Join-Path $claudeDir 'agents'
$agentes = Get-ChildItem $origenAgentes -File -ErrorAction SilentlyContinue
foreach ($f in $agentes) {
    Copy-Item $f.FullName -Destination $destAgentes -Force
}
Write-Host "[OK] Agentes     : $($agentes.Count) archivos" -ForegroundColor Green

# --- Skills (siempre sobreescribir) ---

$origenSkills = Join-Path $repo '.claude\skills'
$destSkills   = Join-Path $claudeDir 'skills'
$skills = Get-ChildItem $origenSkills -Directory -ErrorAction SilentlyContinue
foreach ($d in $skills) {
    Copy-Item $d.FullName -Destination $destSkills -Recurse -Force
}
Write-Host "[OK] Skills      : $($skills.Count) directorios" -ForegroundColor Green

# --- Comandos (siempre sobreescribir) ---

$origenCommands = Join-Path $repo 'commands'
$destCommands   = Join-Path $claudeDir 'commands'
$commands = Get-ChildItem $origenCommands -File -Filter '*.md' -ErrorAction SilentlyContinue
foreach ($f in $commands) {
    Copy-Item $f.FullName -Destination $destCommands -Force
}
Write-Host "[OK] Comandos    : $($commands.Count) archivos" -ForegroundColor Green

# --- Workflows (siempre sobreescribir) ---

$origenWorkflows = Join-Path $repo 'templates\workflows'
$destWorkflows   = Join-Path $claudeDir 'workflows'
$workflows = Get-ChildItem $origenWorkflows -File -Filter '*.md' -ErrorAction SilentlyContinue
foreach ($f in $workflows) {
    Copy-Item $f.FullName -Destination $destWorkflows -Force
}
Write-Host "[OK] Workflows   : $($workflows.Count) archivos" -ForegroundColor Green

# --- CLAUDE.md (siempre sobreescribir) ---

Copy-Item (Join-Path $repo 'templates\client-project-CLAUDE.md') (Join-Path $destino 'CLAUDE.md') -Force
Write-Host "[OK] CLAUDE.md" -ForegroundColor Green

# --- settings.json (solo si no existe) ---

$destSettings = Join-Path $claudeDir 'settings.json'
if (-not (Test-Path $destSettings)) {
    Copy-Item (Join-Path $repo 'templates\client-project-settings.json') $destSettings
    Write-Host "[OK] settings.json (creado)" -ForegroundColor Green
} else {
    Write-Host "[--] settings.json (ya existe, no sobreescrito)" -ForegroundColor DarkGray
}

# --- settings.local.json (siempre regenerar — rutas especificas de esta maquina) ---

$destSettingsLocal = Join-Path $claudeDir 'settings.local.json'
$notifyScript      = Join-Path $env:USERPROFILE '.claude\ccnotify.ps1'

[PSCustomObject]@{
    env  = [PSCustomObject]@{
        FARO_HOME = $repo
    }
    hooks = [PSCustomObject]@{
        Stop = @(
            [PSCustomObject]@{
                hooks = @(
                    [PSCustomObject]@{
                        type    = "command"
                        command = "powershell -NonInteractive -WindowStyle Hidden -File `"$notifyScript`" -Event Stop"
                    }
                )
            }
        )
        Notification = @(
            [PSCustomObject]@{
                hooks = @(
                    [PSCustomObject]@{
                        type    = "command"
                        command = "powershell -NonInteractive -WindowStyle Hidden -File `"$notifyScript`" -Event Notification"
                    }
                )
            }
        )
    }
} | ConvertTo-Json -Depth 10 | Set-Content $destSettingsLocal -Encoding utf8
Write-Host "[OK] settings.local.json (regenerado)" -ForegroundColor Green

# --- 800_inputs/brief.md (solo si no existe o esta vacio) ---

$destInputs = Join-Path $destino '800_inputs'
New-Item -ItemType Directory -Force $destInputs | Out-Null

$destBrief   = Join-Path $destInputs 'brief.md'
$origenBrief = Join-Path $repo 'templates\010_discovery\brief_template.md'

$briefExiste = Test-Path $destBrief
$briefVacio  = $briefExiste -and (Get-Item $destBrief).Length -eq 0

if (-not $briefExiste -or $briefVacio) {
    Copy-Item $origenBrief $destBrief -Force
    Write-Host "[OK] 800_inputs/brief.md (template copiado)" -ForegroundColor Green
} else {
    Write-Host "[--] 800_inputs/brief.md (ya tiene contenido, no sobreescrito)" -ForegroundColor DarkGray
}

# --- Resumen final ---

Write-Host ""
if ($harnessActivo) {
    Write-Host "[AVISO] Harness activo: agentes y skills actualizados. Carpetas de runtime sin cambios." -ForegroundColor Yellow
    Write-Host ""
}
Write-Host "=== Setup completado ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Siguientes pasos:" -ForegroundColor White
Write-Host "  1. Completa 800_inputs\brief.md con los datos del cliente"
Write-Host "  2. Abre (o reinicia) Claude Code en esta carpeta"
Write-Host "  3. Ejecuta /faro-init   -> crea las carpetas del proyecto"
Write-Host "  4. Ejecuta /faro-discovery -> inicia el harness"
Write-Host ""
