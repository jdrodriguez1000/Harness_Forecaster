# FARO — Forecasting Agentic Results & Operations

Sistema agéntico de pronóstico de demanda B2B operado por **Sabbia Solutions & Software (Triple S)**.

---

## ¿Qué es FARO?

FARO es un conjunto de agentes de IA que guían a Triple S en el proceso de onboarding y pronóstico de demanda para clientes manufactureros. Opera como **harnesses** — flujos de trabajo agénticos secuenciales con checkpoints de aprobación humana.

El harness actualmente construido y listo para usar es el **010 Discovery**, que captura el contexto del cliente, calcula su tamaño operativo (ITO) y genera los artefactos de configuración del servicio.

---

## Requisitos previos

### Una sola vez por máquina

Ejecutar el script de setup desde la carpeta del repositorio:

```powershell
.\faro-setup.ps1
```

Esto crea una junction `~/.claude/commands/` → `commands/` del repo y configura `~/.faro/faro.config.json`. Los comandos `/faro-*` quedan disponibles **globalmente** en todas las sesiones de Claude Code de la máquina. Solo se necesita hacer una vez por máquina.

> **Importante:** sin este paso los comandos `/faro-*` no estarán disponibles. El deploy del proyecto no instala comandos — esa es responsabilidad exclusiva de `faro-setup.ps1`.

---

## Iniciar un proyecto nuevo

### 1. Crear la carpeta del proyecto cliente

```powershell
New-Item -ItemType Directory "C:\ruta\a\MiCliente"
```

### 2. Deployar el harness

Desde la carpeta del repositorio `Harness_Forecaster`:

```powershell
# Para desarrollo (recomendado) — junctions al repo, cambios inmediatos:
.\deploy-harness.ps1 -Harness 010 -Destino "C:\ruta\a\MiCliente" -Dev

# Para producción o pruebas aisladas — copia los archivos:
.\deploy-harness.ps1 -Harness 010 -Destino "C:\ruta\a\MiCliente"
```

El deploy instala agentes, skills, commands, CLAUDE.md, settings y la estructura de carpetas del proyecto.

### 3. Completar el brief del cliente

Abrir `800_inputs/brief.md` en la carpeta del proyecto y completarlo con los datos del cliente: nombre, sector, stakeholders conocidos y cualquier contexto inicial relevante.

### 4. Abrir Claude Code en la carpeta del proyecto

Abrir Claude Code apuntando a la carpeta del cliente (NO a `Harness_Forecaster`). Todos los comandos `/faro-*` y los agentes operan desde ahí.

### 5. Lanzar el harness

```
/faro-init
```

El governor genera el **Sprint Contract** en `700_contract/sc_010_discovery.md`. Revisarlo y aprobarlo:

```
/faro-discovery sprint_contract_approved: true
```

---

## Flujo completo del harness 010

```
/faro-init
    └── Governor genera Sprint Contract
          └── Operador aprueba → /faro-discovery sprint_contract_approved: true
                └── Governor retorna INTERVIEWER_REQUIRED
                      └── Operador lanza entrevista (interviewer interactivo)
                            └── Entrevistas completadas → /faro-discovery interviewer_complete: true
                                  └── Governor spawnea Synthesizer (automático)
                                        └── Governor spawnea Analyst (automático)
                                              └── Governor spawnea Configurator DRAFT (automático)
                                                    └── Operador revisa borradores → CP-03
                                                          └── /faro-discovery cp03_approved: true
                                                                └── Configurator COMMIT (automático)
                                                                      └── Evaluator → veredicto APPROVED/REJECTED
```

### Artefactos finales (si veredicto APPROVED)

| Archivo | Descripción |
|---|---|
| `010_discovery/deliverables/client_profile.json` | Perfil del cliente con ITO, categoría y plan |
| `010_discovery/deliverables/onboarding_config.json` | Configuración del servicio para el tenant |
| `010_discovery/deliverables/data_intake_guide.md` | Guía de entrega de datos en lenguaje de negocio |
| `600_persistence/pending_email.json` | Correo de bienvenida listo para enviar |
| `010_discovery/storage_local/tenants/{id}/` | Carpetas Bronce/Plata/Oro del tenant |

---

## Comandos disponibles

| Comando | Cuándo usarlo |
|---|---|
| `/faro-init` | Primera vez — arranca el harness desde cero |
| `/faro-discovery <señal>` | Enviar señales al governor (aprobaciones, continuaciones) |
| `/faro-restart` | Retomar tras reinicio de sesión de Claude Code |
| `/faro-continue` | Reanudar un harness suspendido |
| `/faro-suspend` | Pausar el harness de forma ordenada |
| `/faro-save` | Guardar estado parcial de entrevista en curso (emergencia) |
| `/faro-override <instrucción>` | Inyectar una restricción o corrección al harness activo |

---

## Estructura de carpetas del proyecto cliente

```
MiCliente/
├── CLAUDE.md                        ← Instrucciones para Claude Code en este proyecto
├── 800_inputs/
│   └── brief.md                     ← Brief del cliente (completar antes de /faro-init)
├── 700_contract/
│   └── sc_010_discovery.md          ← Sprint Contract (BORRADOR → APROBADO)
├── 010_discovery/
│   ├── deliverables/                ← Artefactos finales del Discovery
│   ├── support/                     ← Artefactos de trabajo interno
│   ├── templates/                   ← Plantillas de soporte
│   └── storage_local/tenants/       ← Carpetas de datos por tenant
├── 600_persistence/
│   ├── harness-state.json           ← Estado del governor (A)
│   ├── execution-state.json         ← Plan del orchestrator (B)
│   └── claude-progress.txt          ← Bitácora legible
├── 605_eval/
│   ├── verdict.json                 ← Veredicto del evaluador (C)
│   └── metrics_summary.json         ← Scores por dimensión
└── 610_knowledge/
    ├── decisions_library.md         ← Decisiones del ciclo
    └── lessons_learned.md           ← Lecciones registradas
```

---

## Deploy: ¿cuándo hacerlo?

| Situación | Acción |
|---|---|
| Proyecto nuevo (primera vez) | Deploy obligatorio |
| Modo `-Dev` + cambio en agentes/skills/commands | **No re-deployar** — las junctions lo reflejan automáticamente |
| Modo `-Dev` + cambio en CLAUDE.md, templates o scripts | Re-deployar para actualizar esos archivos |
| Modo normal (copia) + cualquier cambio en el repo | Re-deployar |

---

## Estructura de este repositorio (`Harness_Forecaster`)

```
Harness_Forecaster/
├── .claude/agents/        ← Agentes FARO (discovery-governor, interviewer, etc.)
├── .claude/skills/        ← Skills de soporte (schemas, rúbricas)
├── commands/              ← Comandos slash /faro-*
├── harnesses/             ← Documentación funcional de cada harness
├── brief/                 ← Planes de Construcción por harness
├── templates/             ← Templates deployables al proyecto cliente
├── scripts/               ← Scripts Python de soporte (ito_calculator, etc.)
├── flows/                 ← Diagramas de flujo de cada harness
├── progress/              ← Estado del proyecto, tareas, decisiones y lecciones
├── deploy-harness.ps1     ← Script de deploy
└── faro-setup.ps1         ← Setup por máquina (ejecutar una vez)
```
