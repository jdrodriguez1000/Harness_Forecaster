Crea la estructura de carpetas y archivos de soporte del harness 010 Discovery en el proyecto actual.

## Pasos

1. Crear las carpetas de runtime y de soporte del harness con PowerShell:

   ```powershell
   @(
     '600_persistence',
     '605_eval',
     '610_knowledge',
     '615_changes',
     '700_contract',
     '010_discovery\deliverables',
     '010_discovery\support',
     '010_discovery\templates',
     '010_discovery\schemas'
   ) | ForEach-Object { New-Item -ItemType Directory -Force $_ | Out-Null }
   ```

2. Copiar los archivos de soporte desde el repo usando `$env:FARO_HOME`:

   ```powershell
   $src = $env:FARO_HOME

   # Scripts Python → 010_discovery/
   Copy-Item "$src\scripts\010_discovery\*.py" -Destination '010_discovery\' -Force

   # session_template.md → 010_discovery/
   Copy-Item "$src\templates\010_discovery\session_template.md" -Destination '010_discovery\' -Force

   # Templates de guía y preguntas por rol → 010_discovery/templates/
   $incluir = @(
     'data_intake_guide_template.md',
     'data_intake_guide_esquema2_block.md',
     'preguntas_rol_negocio.md',
     'preguntas_rol_tecnico.md',
     'preguntas_rol_usuario.md'
   )
   Get-ChildItem "$src\templates\010_discovery" -File |
     Where-Object { $_.Name -in $incluir } |
     ForEach-Object { Copy-Item $_.FullName -Destination '010_discovery\templates\' -Force }

   # Schemas JSON → 010_discovery/schemas/
   Copy-Item "$src\templates\010_discovery\schemas\*" -Destination '010_discovery\schemas\' -Force
   ```

3. Mostrar este mensaje exacto:

   ```
   FARO: Proyecto inicializado correctamente.
   Siguiente paso: completa 800_inputs\brief.md y ejecuta /faro-discovery para iniciar el harness.
   ```

## Notas

- No invocar ningún agente.
- No modificar archivos existentes.
- Si las carpetas ya existen, continuar sin error (`-Force` es idempotente).
- `$env:FARO_HOME` es inyectado por `faro-setup.ps1` en `settings.local.json`.
