Inicia el harness 010 Discovery de FARO en el proyecto actual y lo conduce de punta a punta.

## Rol de esta sesión: CONDUCTOR

El `discovery-governor` es el cerebro del harness pero es un subagente, y un subagente no puede
spawnear otros subagentes. Por eso el governor **no invoca a nadie**: decide el próximo paso y
retorna un bloque `GOVERNOR_RESULT`. **Esta sesión principal es el conductor** — la única que
puede spawnear subagentes (vía la herramienta `Agent`). Tu trabajo es spawnear lo que el governor
pida y re-invocarlo, en bucle, hasta un estado terminal o un gate del operador.

## Pasos

### 1. Verificar disponibilidad del governor

Comprobar que `.claude/agents/discovery-governor.md` existe en el directorio actual. Si no existe,
informar "FARO: discovery-governor.md no está disponible. Ejecuta `faro-setup` en esta carpeta." y
detener.

### 2. Cargar la lógica del bucle conductor

Leer `.claude/workflows/conductor_loop.md`. Ese archivo define el bucle completo, la tabla de
acciones por `status` y el manejo de cada gate del operador. **Seguir ese bucle al pie de la letra.**

### 3. Arrancar el bucle

Spawnear `discovery-governor` (herramienta `Agent`, `subagent_type: discovery-governor`) con el prompt:

```
MODO: INIT
```

Extraer el `GOVERNOR_RESULT` retornado y entrar al bucle conductor de `conductor_loop.md`:
- En INIT, el camino típico es `SPRINT_CONTRACT_READY` → gate de aprobación del operador →
  `MODO: EXECUTE` con `sprint_contract_approved: true` → despachos de workers/orchestrator →
  gates CP-03/CP-04 → auditoría → cierre.
- Si es una reanudación, el governor (ritual E10-B) retornará un `RESUME_AT_*` o `SUSPEND_DETECTED`;
  manejarlos según la tabla del bucle.

No agregar texto innecesario entre spawns. Mantener al operador informado solo en los gates y al
cerrar.
