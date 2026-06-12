#Requires -Version 5.1
param(
    [string]$Harness = '010',
    [Parameter(Mandatory)][string]$Destino,
    [switch]$Dev
)

$ErrorActionPreference = 'Stop'

$mapa = @{
    '010' = 'discovery'
    '015' = 'intake'
    '020' = 'diagnosis'
    '025' = 'refinery'
    '030' = 'trainer'
    '035' = 'predictor'
    '040' = 'publisher'
    '045' = 'monitor'
    '050' = 'lifecycle'
    '055' = 'command'
    '060' = 'simulator'
}

# --- Validaciones ---

if (-not $mapa.ContainsKey($Harness)) {
    Write-Error "Harness '$Harness' no reconocido. Harnesses validos: $($mapa.Keys | Sort-Object | Join-String -Separator ', ')"
    exit 1
}

if (-not (Test-Path $Destino -PathType Container)) {
    New-Item -ItemType Directory -Path $Destino -Force | Out-Null
    Write-Host "Carpeta destino creada: $Destino" -ForegroundColor Green
}

$prefijo         = $mapa[$Harness]
$origenAgentes   = Join-Path $PSScriptRoot '.claude\agents'
$origenSkills    = Join-Path $PSScriptRoot '.claude\skills'
$origenTemplates = Join-Path $PSScriptRoot 'templates'

$destinoAgentes  = Join-Path $Destino '.claude\agents'
$destinoSkills   = Join-Path $Destino '.claude\skills'
$destinoClaude   = Join-Path $Destino '.claude'

Write-Host ""
Write-Host "=== deploy-harness.ps1 ===" -ForegroundColor Cyan
Write-Host "Harness : $Harness ($prefijo-*)"
Write-Host "Destino : $Destino"
if ($Dev) { Write-Host "Modo    : DEV (junctions al repo)" -ForegroundColor Magenta }
Write-Host ""

# --- Crear directorio .claude (necesario en ambos modos) ---

New-Item -ItemType Directory -Force $destinoClaude | Out-Null

if ($Dev) {

    # En modo Dev: junctions directas al repo (cambios en el repo son inmediatos)
    # Los dirs destino deben NO existir antes de crear el junction.

    $agentesEliminados = @()
    $skillsEliminadas  = @()

    foreach ($dir in @($destinoAgentes, $destinoSkills)) {
        if (Test-Path $dir) {
            $item = Get-Item $dir
            if ($item.LinkType -eq 'Junction') {
                Remove-Item $dir -Force
            } else {
                Remove-Item $dir -Recurse -Force
            }
        }
    }

    New-Item -ItemType Junction -Path $destinoAgentes -Target $origenAgentes | Out-Null
    New-Item -ItemType Junction -Path $destinoSkills  -Target $origenSkills  | Out-Null

    $agentesCargados = @("[junction] → $origenAgentes")
    $skillsCargadas  = @("[junction] → $origenSkills")

} else {

    # --- Crear estructura de directorios ---
    # Si las carpetas destino son junctions (de un deploy -Dev previo), eliminar solo el
    # link antes de crear el directorio real — nunca borrar contenido a través del junction.

    foreach ($dir in @($destinoAgentes, $destinoSkills)) {
        if (Test-Path $dir) {
            $item = Get-Item $dir -Force
            if ($item.LinkType -eq 'Junction') {
                Remove-Item $dir -Force
            }
        }
    }

    New-Item -ItemType Directory -Force $destinoAgentes | Out-Null
    New-Item -ItemType Directory -Force $destinoSkills  | Out-Null

    # --- Hot-swap: limpiar archivos del harness en destino ---

    $agentesEliminados = @()
    $skillsEliminadas  = @()

    $agentesExistentes = Get-ChildItem "$destinoAgentes\$prefijo-*.md" -ErrorAction SilentlyContinue
    foreach ($f in $agentesExistentes) {
        Remove-Item $f.FullName -Force
        $agentesEliminados += $f.Name
    }

    $skillsExistentes = Get-ChildItem $destinoSkills -Directory -Filter "$prefijo-*" -ErrorAction SilentlyContinue
    foreach ($d in $skillsExistentes) {
        Remove-Item $d.FullName -Recurse -Force
        $skillsEliminadas += $d.Name
    }

    # --- Copiar agentes ---

    $agentesCargados = @()
    $agentesOrigen = Get-ChildItem "$origenAgentes\$prefijo-*.md" -ErrorAction SilentlyContinue

    if ($agentesOrigen.Count -eq 0) {
        Write-Warning "No se encontraron agentes con prefijo '$prefijo-*' en $origenAgentes"
    } else {
        foreach ($f in $agentesOrigen) {
            Copy-Item $f.FullName -Destination $destinoAgentes
            $agentesCargados += $f.Name
        }
    }

    # --- Copiar skills ---

    $skillsCargadas = @()
    $skillsOrigen = Get-ChildItem $origenSkills -Directory -Filter "$prefijo-*" -ErrorAction SilentlyContinue

    if ($skillsOrigen.Count -eq 0) {
        Write-Warning "No se encontraron skills con prefijo '$prefijo-*' en $origenSkills"
    } else {
        foreach ($d in $skillsOrigen) {
            Copy-Item $d.FullName -Destination $destinoSkills -Recurse
            $skillsCargadas += $d.Name
        }
    }

}

# --- Copiar scripts del harness (Python u otros) ---
# scripts/{NNN}_{nombre}/*.py → {destino}/{NNN}_{nombre}/

$carpetaHarness    = "${Harness}_${prefijo}"
$origenScripts     = Join-Path $PSScriptRoot "scripts\$carpetaHarness"
$destinoHarness    = Join-Path $Destino $carpetaHarness
$destinoTemplHarn  = Join-Path $destinoHarness 'templates'

$scriptsCargados = @()

if (Test-Path $origenScripts) {
    New-Item -ItemType Directory -Force $destinoHarness | Out-Null
    $scriptsOrigen = Get-ChildItem "$origenScripts\*" -File -ErrorAction SilentlyContinue
    foreach ($f in $scriptsOrigen) {
        Copy-Item $f.FullName -Destination $destinoHarness -Force
        $scriptsCargados += $f.Name
    }
}

# --- Copiar templates del harness ---
# templates/{NNN}_{nombre}/session_template.md → {destino}/{NNN}_{nombre}/
# templates/{NNN}_{nombre}/(resto)             → {destino}/{NNN}_{nombre}/templates/

$origenTemplHarn = Join-Path $PSScriptRoot "templates\$carpetaHarness"
$templatesSesion  = @()
$templatesGuias   = @()
$templatesSubs    = @()   # archivos en subdirectorios (ej: schemas/)

if (Test-Path $origenTemplHarn) {
    New-Item -ItemType Directory -Force $destinoHarness   | Out-Null
    New-Item -ItemType Directory -Force $destinoTemplHarn | Out-Null

    # Harness 010: crear 800_inputs/, 700_contract/ y subcarpetas de 010_discovery/
    $inputsCreados = @()
    if ($Harness -eq '010') {
        $destinoInputs = Join-Path $Destino '800_inputs'
        New-Item -ItemType Directory -Force $destinoInputs | Out-Null
        New-Item -ItemType Directory -Force (Join-Path $Destino '700_contract') | Out-Null
        New-Item -ItemType Directory -Force (Join-Path $Destino '010_discovery\deliverables') | Out-Null
        New-Item -ItemType Directory -Force (Join-Path $Destino '010_discovery\support') | Out-Null
    }

    $templatesOrigen = Get-ChildItem "$origenTemplHarn\*" -File -ErrorAction SilentlyContinue
    foreach ($f in $templatesOrigen) {
        if ($f.Name -eq 'session_template.md') {
            Copy-Item $f.FullName -Destination $destinoHarness -Force
            $templatesSesion += $f.Name
        } elseif ($f.Name -eq 'brief_template.md' -and $Harness -eq '010') {
            Copy-Item $f.FullName -Destination (Join-Path $destinoInputs 'brief.md') -Force
            $inputsCreados += 'brief.md'
        } else {
            Copy-Item $f.FullName -Destination $destinoTemplHarn -Force
            $templatesGuias += $f.Name
        }
    }

    # Copiar subdirectorios de templates (ej: schemas/) → {destino}/{NNN}/schemas/
    $subDirsOrigen = Get-ChildItem "$origenTemplHarn\*" -Directory -ErrorAction SilentlyContinue
    foreach ($d in $subDirsOrigen) {
        $destinoSub = Join-Path $destinoHarness $d.Name
        New-Item -ItemType Directory -Force $destinoSub | Out-Null
        Get-ChildItem "$($d.FullName)\*" -File -ErrorAction SilentlyContinue | ForEach-Object {
            Copy-Item $_.FullName -Destination $destinoSub -Force
            $templatesSubs += "$($d.Name)\$($_.Name)"
        }
    }
}

# --- Copiar templates (solo primer deployment) ---

$settingsAplicado = $false
$claudeMdAplicado = $false
$settingsOmitido  = $false
$claudeMdOmitido  = $false

$destinoSettings = Join-Path $destinoClaude 'settings.json'
$origenSettings  = Join-Path $origenTemplates 'client-project-settings.json'

if (-not (Test-Path $destinoSettings)) {
    if (Test-Path $origenSettings) {
        Copy-Item $origenSettings $destinoSettings
        $settingsAplicado = $true
    } else {
        Write-Warning "Template 'client-project-settings.json' no encontrado en $origenTemplates"
    }
} else {
    $settingsOmitido = $true
}

$destinoClaudeMd = Join-Path $Destino 'CLAUDE.md'
$origenClaudeMd  = Join-Path $origenTemplates 'client-project-CLAUDE.md'

# CLAUDE.md se sobreescribe siempre: el template evoluciona con cada harness.
# settings.json en cambio se omite si ya existe (el cliente puede haberlo personalizado).
if (Test-Path $origenClaudeMd) {
    Copy-Item $origenClaudeMd $destinoClaudeMd -Force
    $claudeMdAplicado = $true
} else {
    Write-Warning "Template 'client-project-CLAUDE.md' no encontrado en $origenTemplates"
}

# --- Copiar workflows (siempre sobreescribir, igual que CLAUDE.md) ---

$origenWorkflows  = Join-Path $origenTemplates 'workflows'
$destinoWorkflows = Join-Path $destinoClaude 'workflows'

New-Item -ItemType Directory -Force $destinoWorkflows | Out-Null

$workflowsCargados = @()
$workflowsOrigen = Get-ChildItem "$origenWorkflows\*.md" -ErrorAction SilentlyContinue
foreach ($f in $workflowsOrigen) {
    Copy-Item $f.FullName -Destination $destinoWorkflows -Force
    $workflowsCargados += $f.Name
}


# --- Crear/actualizar settings.local.json (hooks + env específicos de la máquina) ---

$settingsLocalPath = Join-Path $destinoClaude 'settings.local.json'
$notifyScriptPath = Join-Path $env:USERPROFILE '.claude\ccnotify.ps1'

$settingsLocalObj = [PSCustomObject]@{
    hooks = [PSCustomObject]@{
        Stop = @(
            [PSCustomObject]@{
                hooks = @(
                    [PSCustomObject]@{
                        type = "command"
                        command = "powershell -NonInteractive -WindowStyle Hidden -File `"$notifyScriptPath`" -Event Stop"
                    }
                )
            }
        )
        Notification = @(
            [PSCustomObject]@{
                hooks = @(
                    [PSCustomObject]@{
                        type = "command"
                        command = "powershell -NonInteractive -WindowStyle Hidden -File `"$notifyScriptPath`" -Event Notification"
                    }
                )
            }
        )
    }
    env = [PSCustomObject]@{
        HARNESS_DEPLOY_SCRIPT = $PSCommandPath
    }
}

$settingsLocalObj | ConvertTo-Json -Depth 10 | Set-Content $settingsLocalPath -Encoding utf8

# --- Inyectar path del deploy script en settings.json (backward compat) ---

$settingsPath = Join-Path $destinoClaude 'settings.json'
if (Test-Path $settingsPath) {
    $settingsObj = Get-Content $settingsPath -Raw | ConvertFrom-Json
} else {
    $settingsObj = [PSCustomObject]@{ permissions = [PSCustomObject]@{ allow = @() } }
}
if (-not ($settingsObj.PSObject.Properties['env'])) {
    $settingsObj | Add-Member -NotePropertyName 'env' -NotePropertyValue ([PSCustomObject]@{}) -Force
}
$settingsObj.env | Add-Member -NotePropertyName 'HARNESS_DEPLOY_SCRIPT' -NotePropertyValue $PSCommandPath -Force
$settingsObj | ConvertTo-Json -Depth 10 | Set-Content $settingsPath -Encoding utf8

# --- Reporte final ---

if ($Dev) {

    Write-Host "--- Modo DEV: junctions creadas ---" -ForegroundColor Magenta
    Write-Host "  [junction] .claude\agents → $origenAgentes"
    Write-Host "  [junction] .claude\skills → $origenSkills"

} else {

    Write-Host "--- Limpieza (hot-swap) ---" -ForegroundColor Yellow
    if ($agentesEliminados.Count -gt 0) {
        $agentesEliminados | ForEach-Object { Write-Host "  [eliminado] agentes\$_" }
    } else {
        Write-Host "  (ningun agente previo del harness $Harness en destino)"
    }
    if ($skillsEliminadas.Count -gt 0) {
        $skillsEliminadas | ForEach-Object { Write-Host "  [eliminada]  skills\$_" }
    } else {
        Write-Host "  (ninguna skill previa del harness $Harness en destino)"
    }

    Write-Host ""
    Write-Host "--- Agentes copiados ($($agentesCargados.Count)) ---" -ForegroundColor Green
    $agentesCargados | ForEach-Object { Write-Host "  [OK] .claude\agents\$_" }

    Write-Host ""
    Write-Host "--- Skills copiadas ($($skillsCargadas.Count)) ---" -ForegroundColor Green
    $skillsCargadas | ForEach-Object { Write-Host "  [OK] .claude\skills\$_" }

}

Write-Host ""
Write-Host "--- Templates ---" -ForegroundColor Green
if ($settingsAplicado) { Write-Host "  [OK]      .claude\settings.json (creado)" }
if ($settingsOmitido)  { Write-Host "  [omitido] .claude\settings.json (ya existia - no sobreescrito)" }
if ($claudeMdAplicado) { Write-Host "  [OK]      CLAUDE.md (aplicado)" }


Write-Host ""
Write-Host "--- Workflows copiados ($($workflowsCargados.Count)) ---" -ForegroundColor Green
if ($workflowsCargados.Count -gt 0) {
    $workflowsCargados | ForEach-Object { Write-Host "  [OK] .claude\workflows\$_" }
} else {
    Write-Warning "No se encontraron workflows en $origenWorkflows"
}

Write-Host ""
if ($scriptsCargados.Count -gt 0) {
    Write-Host "--- Scripts del harness copiados ($($scriptsCargados.Count)) ---" -ForegroundColor Green
    $scriptsCargados | ForEach-Object { Write-Host "  [OK] $carpetaHarness\$_" }
}

if ($templatesSesion.Count -gt 0 -or $templatesGuias.Count -gt 0 -or $templatesSubs.Count -gt 0) {
    Write-Host ""
    Write-Host "--- Templates del harness copiados ---" -ForegroundColor Green
    $templatesSesion | ForEach-Object { Write-Host "  [OK] $carpetaHarness\$_" }
    $templatesGuias  | ForEach-Object { Write-Host "  [OK] $carpetaHarness\templates\$_" }
    $templatesSubs   | ForEach-Object { Write-Host "  [OK] $carpetaHarness\$_" }
}

if ($Harness -eq '010') {
    Write-Host ""
    Write-Host "--- Carpeta 800_inputs/ (harness 010) ---" -ForegroundColor Green
    if ($inputsCreados.Count -gt 0) {
        $inputsCreados | ForEach-Object { Write-Host "  [OK] 800_inputs\$_" }
    }
    Write-Host "  *** Completar 800_inputs\brief.md antes de lanzar el harness ***" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "--- Configuración ---" -ForegroundColor Green
Write-Host "  [OK] .claude\settings.local.json (hooks + env)"

Write-Host ""
Write-Host "=== Deployment completado ===" -ForegroundColor Cyan
Write-Host "Siguiente paso: abrir Claude Code en '$Destino'"
Write-Host ""
