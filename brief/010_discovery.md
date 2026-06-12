# Plan de Construcción — 010 Discovery Harness
## Harness Forecaster — Sabbia Solutions & Software

**Tipo de harness:** Semi-humano  
**Bloque de construcción:** A (posición 1 de 11)  
**Hito:** A — Primer piloto ejecutable  
**Disparador:** Un prospecto firma el contrato y pasa a estado *Onboarding*

---

### Checklist de completitud

El harness completo debe contener estas 7 secciones:
- [x] Sección 1 — Fase 0: Definición Estructural
- [x] Sección 2 — Fase 1: Diseño Agéntico (6 sub-secciones)
- [x] Sección 3 — Sprint Contract (plantilla)
- [x] Sección 4 — Rúbrica de Evaluación (con few-shot y anclas)
- [x] Sección 5 — Handoff Artifact → 015 Intake
- [x] Sección 6 — Flujo del Arnés (12.1–12.5)
- [x] Sección 7 — Notas de Construcción

---

## Sección 1 — Fase 0: Definición Estructural

### Propósito

Capturar todo el contexto necesario para que el sistema pueda operar con un cliente manufacturero nuevo durante el mes 1 gratuito de onboarding. Es el único harness donde un operador de Triple S conduce activamente una sesión con el cliente (empresa ABC). Al completarse, el sistema tiene suficiente información para: recibir los datos del cliente, calcular el ISD, gestionar el ciclo de vida y emitir el primer pronóstico en el mes 3.

### Inputs

| # | Input | Descripción | Obligatorio |
|---|-------|-------------|-------------|
| I-1 | Contrato firmado | Evidencia de que el prospecto pasó a estado Onboarding | Sí |
| I-2 | Fecha de firma del contrato | Punto de partida del temporizador del mes gratuito | Sí |
| I-3 | Categoría tarifaria preliminar (M/L/XL) | Asignada durante el proceso comercial con ITO estimado | Sí |
| I-4 | Datos del cliente capturados en sesión | Razón social, sector, contactos, parámetros operativos, plan de suscripción | Sí |

**Datos capturados en la sesión (por el operador Triple S con el cliente):**

| Campo | Descripción | Obligatorio |
|-------|-------------|-------------|
| Nombre y razón social | Identificador legal de la empresa ABC | Sí |
| Sector / industria | Contexto del negocio (alimentos, químicos, textil, etc.) | Sí |
| Contacto principal | Nombre, correo y teléfono del planificador de demanda | Sí |
| Responsable de pagos | Nombre y correo — receptor de alertas de cobro | Sí |
| SKUs activos aprox. | Insumo ITO | Sí |
| Clientes XYZ atendidos aprox. | Insumo ITO | Sí |
| Volumen de pedidos por mes aprox. | Insumo ITO | Sí |
| Años de historial disponible | Para evaluar cold start | Sí |
| Modo de ingesta preferido | Batch o Incremental | Sí |
| Frecuencia de actualización (si Incremental) | Diaria o semanal | Condicional |
| Horizonte de pronóstico requerido | Días / semanas / meses / múltiples meses | Sí |
| Jerarquía de productos disponible | Categoría → Subcategoría → SKU — niveles que tiene el cliente | Sí |
| Jerarquía geográfica disponible | Región → País → Ciudad → Sede — niveles disponibles | Sí |
| ¿Tiene Esquema 2? | Si puede entregar datos de producción e inventario | Sí |
| Mínimos contractuales con XYZ | Si existen, si se cumplen habitualmente | Opcional |
| Plan de suscripción elegido | Mensual / Trimestral / Anual | Sí |
| Criterios de éxito del cliente | Qué le importa reducir: sobre-inventario, quiebres, ambos | Sí |

### Proceso (7 pasos)

1. **Sesión de descubrimiento** — El operador Triple S conduce videollamada/reunión con el cliente capturando todos los campos de I-4. Duración estimada: 60–90 minutos.
2. **Cálculo ITO y confirmación de categoría** — Con SKUs, clientes XYZ y volumen, el sistema calcula el ITO y verifica que la categoría comercial (M/L/XL) sea correcta. Si hay discrepancia, se ajusta antes de continuar.
3. **Evaluación de cold start** — Con el historial declarado, el sistema determina el nivel de confianza inicial y documenta el paso de cascada aplicable si historial < 1 año.
4. **Configuración de parámetros operativos** — Se registran: modo de ingesta, horizonte de pronóstico, niveles de jerarquía de producto y geográfica, Esquema 2 activo/inactivo, mínimos contractuales.
5. **Generación de guía de entrega de datos** — Documento personalizado en lenguaje de negocio (sin jerga técnica) explicando qué entregar, en qué formato, qué columnas son obligatorias y opcionales, cómo y dónde subir el archivo.
6. **Registro del cliente en la base de datos** — Creación de filas en tablas `clients`, `contacts`, `client_config`, `subscriptions` con estado inicial `onboarding`.
7. **Creación de carpeta del tenant en Storage** — Estructura `tenants/{tenant_id}/{bronze,silver,gold,models,forecasts,exports}/` en Supabase Storage. Nunca se recrea — los harnesses posteriores solo escriben dentro de ella.

### Outputs (artefactos)

| Artefacto | Path | Descripción |
|-----------|------|-------------|
| `client_profile.json` | `010_discovery/` + Supabase tabla `clients` | Razón social, contactos, categoría, ITO, nivel de confianza cold start, parámetros operativos |
| `onboarding_config.json` | `010_discovery/` + Supabase tabla `client_config` | Modo ingesta, horizonte, jerarquías, Esquema 2, mínimos contractuales |
| `data_intake_guide.pdf` | `010_discovery/` + enviado por correo al contacto principal | Instrucciones de entrega de datos personalizadas — lenguaje de negocio |
| `discovery_session_notes.md` | `010_discovery/` | Notas libres del operador durante la sesión |

**Evento disparado al completarse:**
```
EVENT: onboarding_discovery_complete
  tenant_id: {id}
  timestamp: {ISO-8601}
  next_harness: 015_intake
```

### Criterio de Done

El harness 010 se considera **completo** cuando:

1. Todos los campos obligatorios de la sesión de descubrimiento están registrados en la BD
2. El ITO está calculado y la categoría M/L/XL está confirmada
3. El nivel de confianza cold start está asignado y documentado
4. La guía de entrega de datos (`data_intake_guide.pdf`) fue enviada al contacto principal por correo
5. La carpeta del tenant existe en Supabase Storage con las 6 subcarpetas
6. El registro del cliente existe en la BD con estado `onboarding`
7. El evento `onboarding_discovery_complete` fue emitido

### Tipo de artefacto y ciclo adaptado

El 010 Discovery produce **registros en BD y artefactos de configuración**, no código ni pronósticos. El ciclo se adapta así:

| Ciclo estándar | Adaptación para 010 Discovery |
|----------------|-------------------------------|
| SPEC | Plantilla de sesión de descubrimiento a validar con el operador |
| HUMAN REVIEW | Operador Triple S aprueba los campos capturados en sesión |
| RED | Checklist: ¿están todos los campos obligatorios? ¿ITO calculado? ¿carpeta creada? |
| GREEN | Workers generan guía PDF, crean registros BD y carpeta Storage |
| REFACTOR | Validación de consistencia entre `client_profile.json` y `onboarding_config.json` |
| EVAL | Auditoría de C con rúbrica de completitud y consistencia |

---

## Sección 2 — Fase 1: Diseño Agéntico

### 2.1 Instancias y Roles

| Instancia | Rol | Responsabilidades | Escribe en |
|-----------|-----|-------------------|------------|
| A — Governor | Director del Onboarding | Define Sprint Contract; gestiona gates; decide Avanzar/Repetir; reporta al operador Triple S | `600_persistence/harness-state.json` |
| B — Phase Orchestrator | Coordinador Técnico | Lee contrato; coordina Workers; persiste `orchestration_plan` antes de spawnear; actualiza checkpoints | `600_persistence/execution-state.json` · `600_persistence/claude-progress.txt` |
| C — Phase Evaluator | Auditor Independiente | Lee artefactos sin contexto de ejecución; aplica rúbrica de completitud; emite APPROVED/REJECTED | `605_eval/verdict.json` · `605_eval/metrics_summary.json` · `600_persistence/claude-progress.txt` |

**Regla de Escritor Único (Single Writer Rule):** Cada archivo de estado tiene un único responsable de escritura. Ninguna otra instancia puede modificarlo:
- `600_persistence/harness-state.json` → **solo A**. C nunca escribe en este archivo aunque el veredicto sea APPROVED.
- `600_persistence/execution-state.json` → **solo B**.
- `600_persistence/claude-progress.txt` → el orquestador activo en cada momento (A, B o C).

Jerarquía de llamadas (nunca se viola):
- A → B (para ejecutar), A → C (para auditar). Nunca simultáneo.
- A NO llama Workers directamente.
- B es el único que spawna Workers.
- C NO llama a nadie. Solo lee del filesystem y la BD.
- B comunica completitud a A únicamente a través del filesystem (`600_persistence/execution-state.json` con estado `EXECUTION_COMPLETE`). No existe canal directo B → A.

### 2.2 Workers Especializados

| Worker | Micro-tarea | Inputs que recibe | Output (path) |
|--------|-------------|-------------------|---------------|
| `discovery-interviewer` | Guía al operador en la sesión, valida que todos los campos obligatorios estén capturados, detecta inconsistencias en los datos declarados | I-1, I-2, I-3, plantilla de sesión | `/010_discovery/session_data.json` |
| `discovery-analyst` | Calcula el ITO, confirma/corrige la categoría M/L/XL, determina el nivel de confianza cold start, identifica el paso de cascada aplicable | Path a `session_data.json` | `/010_discovery/analysis_report.json` |
| `discovery-configurator` | Genera `client_profile.json` y `onboarding_config.json`, crea registros en BD, crea carpeta del tenant en Storage, genera `data_intake_guide.pdf`, envía correo al contacto principal, emite el evento `onboarding_discovery_complete` | Path a `analysis_report.json` | `010_discovery/client_profile.json`, `010_discovery/onboarding_config.json`, `010_discovery/data_intake_guide.pdf`, `010_discovery/discovery_session_notes.md` + registros BD + estructura Storage + evento |

**Secuenciación:** `discovery-interviewer` → `discovery-analyst` → `discovery-configurator` (dependencia estricta, no paralela).

> **Nota E7 — Paralelización:** Los tres Workers de este harness tienen dependencia secuencial estricta (cada uno requiere el output del anterior). No aplica paralelización. En harnesses futuros con Workers independientes (ej: 020 Diagnosis ejecuta las 6 dimensiones ISD en paralelo), E7 sí aplica.

> **Nota E8 — Extended Thinking:** El `discovery-analyst` debe usar extended thinking para el cálculo del ITO y la evaluación de cold start cuando el historial declarado es ambiguo o cuando la categoría calculada difiere de la comercial. Reservar para estos pasos de reasoning crítico, no aplicar de forma indiscriminada.

Cada Worker escribe su artefacto al filesystem y reporta a B **solo el path**, nunca el contenido (Regla E6 — Referencias Ligeras).

### 2.3 Política de Herramientas

Herramientas permitidas por Worker:

| Worker | Herramientas permitidas |
|--------|------------------------|
| `discovery-interviewer` | `Read`, `Write` (artefactos locales) |
| `discovery-analyst` | `Read`, `Write` (cálculos y análisis) |
| `discovery-configurator` | `Read`, `Write`, Supabase SDK (BD + Storage), SendGrid API (correo), Prefect (emisión de evento) |

Política de Fallback ante fallo de herramienta (3 niveles):
1. **Reintento** (hasta 2×): reintentar si falla por error transitorio (timeout de red, BD busy)
2. **Fallback local**: si falla el correo SendGrid, guardar `010_discovery/data_intake_guide.pdf` en Storage y registrar la entrega como pendiente manual en `600_persistence/harness-state.json`
3. **Escalamiento**: si falla la creación de estructura en Storage o la escritura en BD, marcar como `BLOCKED` en `600_persistence/execution-state.json`, detener flujo y escalar al operador con contexto completo

### 2.4 Política de Escalamiento

Escalar al operador Triple S (detener flujo) en los siguientes casos:

1. El cliente no puede proveer algún campo obligatorio durante la sesión → registrar campo como `MISSING` en `session_data.json`, escalar al operador para obtenerlo antes de continuar
2. La categoría calculada por ITO difiere en más de un nivel de la categoría comercial asignada (ej: ITO dice XL pero se vendió como M) → escalar para revisión comercial antes de confirmar
3. El historial declarado < 3 meses → el sistema no puede operar con cascada cold start; escalar para evaluación de viabilidad del cliente
4. Fallo irrecuperable en Storage o BD tras 2 reintentos → escalar con log de error completo

En todos los casos: A registra el bloqueo en `600_persistence/harness-state.json` bajo `escalations` con campo, razón y próxima acción propuesta.

### 2.5 Checkpoints Canónicos

| ID | Momento | Qué persiste B |
|----|---------|----------------|
| CP-01 | Tras `discovery-interviewer` | Path a `session_data.json` en `600_persistence/execution-state.json`; campos faltantes identificados |
| CP-02 | Tras `discovery-analyst` | Path a `analysis_report.json`; ITO calculado, categoría confirmada, nivel cold start asignado |
| CP-03 | Tras draft de artefactos | Paths a `010_discovery/client_profile.json` y `010_discovery/onboarding_config.json`; A presenta al operador para aprobación |
| CP-04 | Operador aprueba artefactos | A registra aprobación en `600_persistence/harness-state.json`; `discovery-configurator` ejecuta escrituras en BD y Storage |
| CP-05 | Escrituras completadas | Confirmación de: registros BD creados, carpeta Storage creada, correo enviado, evento emitido |

### 2.6 Trigger de Context Reset

Criterios (el que ocurra primero):

- **Conductual (primario):** señales de degradación durante la coordinación de sesión: saltarse campos obligatorios en `session_data.json`, no verificar consistencia entre ITO calculado y categoría asignada, marcar CP sin que el Worker haya terminado, declarar "configurador listo" sin confirmar el evento emitido.
- **Cuantitativo (secundario):** ≥ 70% de tokens usados.

Acción ante reset: continuar desde el último checkpoint guardado en `600_persistence/execution-state.json`. Nunca reiniciar desde cero. Si el fallo ocurre entre CP-04 y CP-05 (escrituras en BD/Storage a medias), ejecutar rollback: eliminar registros creados parcialmente y reintentar desde CP-04.

---

## Sección 3 — Sprint Contract (Plantilla)

Template que A propone al operador Triple S antes de spawnear B. Requiere aprobación explícita.

```
SPRINT CONTRACT — 010 Discovery
================================
Objetivo    : Capturar el contexto completo del cliente {NOMBRE_CLIENTE} y configurar el
              sistema para iniciar el onboarding
Fase        : 010 — Discovery
Modo        : [INICIO | CONTINUACIÓN]
Cliente     : {razón_social} — Categoría preliminar: {M|L|XL}

Inputs disponibles:
  - Contrato firmado       : {path o referencia}
  - Fecha de firma         : {fecha}
  - Categoría comercial    : {M|L|XL}
  - Datos de sesión        : [PENDIENTE de captura | path a session_data.json]

Workers activados (en orden):
  1. discovery-interviewer  → /010_discovery/session_data.json
  2. discovery-analyst      → /010_discovery/analysis_report.json
  3. discovery-configurator → 010_discovery/client_profile.json
                              010_discovery/onboarding_config.json
                              010_discovery/data_intake_guide.pdf
                              010_discovery/discovery_session_notes.md
                              Registros BD: clients, contacts, client_config, subscriptions
                              Carpeta Storage: tenants/{id}/{bronze,silver,gold,models,forecasts,exports}/
                              Correo a contacto principal
                              Evento: onboarding_discovery_complete

Checkpoints  : CP-01, CP-02, CP-03, CP-04, CP-05
Criterio Done: (1) todos los campos obligatorios registrados, (2) ITO calculado y categoría
               confirmada, (3) guía PDF enviada al contacto principal, (4) carpeta Storage creada,
               (5) registros BD creados con estado onboarding, (6) evento emitido

Riesgos identificados:
  - [campos que el cliente no pudo proveer en sesión]
  - [discrepancia entre ITO calculado y categoría comercial asignada]
  - [historial disponible < 1 año → cascada cold start activa]

Próxima acción: spawnear discovery-interviewer con plantilla de sesión y datos comerciales
```

---

## Sección 4 — Rúbrica de Evaluación (Instancia C)

### Dimensiones de evaluación

| ID | Dimensión | Descripción | Score |
|----|-----------|-------------|-------|
| D1 | Completitud de campos | Todos los campos obligatorios están presentes y no nulos en `session_data.json` | 0.0–1.0 |
| D2 | Consistencia ITO-Categoría | La categoría registrada (M/L/XL) es consistente con el ITO calculado (o la discrepancia fue escalada y resuelta) | 0.0–1.0 |
| D3 | Nivel cold start documentado | El nivel de confianza está asignado y, si historial < 1 año, el paso de cascada está especificado | 0.0–1.0 |
| D4 | Registros BD creados | Las 4 tablas (`clients`, `contacts`, `client_config`, `subscriptions`) tienen las filas del cliente con todos los campos requeridos | 0.0–1.0 |
| D5 | Storage creado | La carpeta del tenant existe en Supabase Storage con las 6 subcarpetas correctas | 0.0–1.0 |
| D6 | Guía enviada | `data_intake_guide.pdf` fue enviado al correo del contacto principal (o está pendiente con registro de entrega manual) | 0.0–1.0 |
| D7 | Evento emitido | El evento `onboarding_discovery_complete` existe en el registro de eventos con `tenant_id` y `timestamp` correctos | 0.0–1.0 |

**Gate de paso:** Score ≥ 0.80 en promedio de todas las dimensiones.  
**Reglas de veto:**
- Si D4 = 0.0 → rechazo automático (sin registros BD no hay onboarding posible)
- Si D5 = 0.0 → rechazo automático (sin carpeta Storage los harnesses 015 y 020 no pueden escribir)
- Si D7 = 0.0 → rechazo automático (sin evento el 015 Intake no se activa)

### Anclas de calibración (few-shot)

**Score 0.2** — Solo algunos campos opcionales capturados, campos obligatorios faltantes. ITO no calculado. Categoría sin confirmar. Sin registros en BD. Sin carpeta en Storage. Sin correo enviado. Sin evento emitido.

> Ejemplo: Se capturó el nombre de la empresa y el contacto principal, pero faltan SKUs, clientes XYZ y volumen de pedidos. La categoría sigue siendo la comercial sin verificar. No existe nada en BD ni Storage.

**Score 0.5** — Todos los campos obligatorios capturados en `session_data.json`. ITO calculado y categoría confirmada. Cold start evaluado. Pero los registros en BD están incompletos (solo tabla `clients` creada, falta `subscriptions`). Sin carpeta en Storage. Sin evento emitido.

> Ejemplo: La sesión fue completa y el análisis correcto, pero el `discovery-configurator` falló a mitad de camino: creó el cliente en BD pero no la suscripción ni la carpeta. El correo no fue enviado. El evento no fue emitido.

**Score 0.8** — Todos los campos obligatorios presentes. ITO calculado. Categoría confirmada (o discrepancia escalada y resuelta). Nivel cold start documentado. Las 4 tablas BD creadas correctamente. Carpeta Storage con las 6 subcarpetas. Evento emitido. El correo al contacto fue enviado pero no hay confirmación de entrega (ej: SendGrid no retornó 202).

> Ejemplo: Todo el flujo completado correctamente. El correo se envió pero el webhook de SendGrid no confirmó apertura. La guía PDF existe en Storage como respaldo.

**Score 1.0** — Todos los campos obligatorios presentes y validados (sin nulos, sin valores fuera de rango). ITO calculado con los valores exactos declarados por el cliente. Categoría confirmada o discrepancia resuelta con registro del ajuste. Nivel cold start documentado con el paso de cascada especificado si aplica. Las 4 tablas BD creadas con todos los campos requeridos y sin valores por defecto incorrectos. Carpeta Storage completa con las 6 subcarpetas. `data_intake_guide.pdf` enviado con confirmación de entrega de SendGrid. Evento `onboarding_discovery_complete` emitido con `tenant_id` y `timestamp` correctos y escuchado por 015 Intake.

> Ejemplo: La sesión fue completa. El ITO calculó 1.240 y la categoría M fue confirmada (umbral M: ITO ≤ 1.500). Historial de 2.5 años → nivel Estándar documentado. Tablas BD: `clients` (tenant_id, razón social, estado=onboarding, fecha_inicio, plan=mensual, categoría=M), `contacts` (principal + pagos), `client_config` (modo=batch, horizonte=mensual, esquema2=no), `subscriptions` (monto=200 USD, inicio_cobro=fecha_inicio+30d). Carpeta `tenants/abc123/` con 6 subcarpetas creadas. PDF enviado — SendGrid retornó 202. Evento emitido y confirmado por 015.

### Output de C

```json
// /605_eval/verdict.json
{
  "phase": "010_discovery",
  "tenant_id": "",
  "verdict": "APPROVED | REJECTED",
  "scores": {
    "D1_field_completeness": 0.0,
    "D2_ito_category_consistency": 0.0,
    "D3_cold_start_documented": 0.0,
    "D4_db_records_created": 0.0,
    "D5_storage_created": 0.0,
    "D6_guide_sent": 0.0,
    "D7_event_emitted": 0.0
  },
  "average": 0.0,
  "veto_triggered": false,
  "veto_dimension": null,
  "rejection_reasons": [],
  "recommendations": []
}
```

```json
// /605_eval/metrics_summary.json  (estructura mínima requerida por metodologia.md §8.2)
{
  "pipeline_data": {
    "phase": "010_discovery",
    "tenant_id": "",
    "started_at": "",
    "execution_complete_at": "",
    "audit_complete_at": ""
  },
  "artifact_status": {
    "session_data_json": { "version": 1, "revisions": 0, "status": "APPROVED | REJECTED", "score": 0.0 },
    "analysis_report_json": { "version": 1, "revisions": 0, "status": "APPROVED | REJECTED", "score": 0.0 },
    "client_profile_json": { "version": 1, "revisions": 0, "status": "APPROVED | REJECTED", "score": 0.0 },
    "onboarding_config_json": { "version": 1, "revisions": 0, "status": "APPROVED | REJECTED", "score": 0.0 },
    "data_intake_guide_pdf": { "version": 1, "revisions": 0, "status": "SENT | PENDING_MANUAL" },
    "db_records": { "tables_created": [], "status": "COMPLETE | PARTIAL | MISSING" },
    "storage_structure": { "path": "", "subfolders": [], "status": "COMPLETE | MISSING" },
    "event_emitted": { "event": "onboarding_discovery_complete", "status": "CONFIRMED | MISSING" }
  },
  "timeline_metrics": {
    "interview_duration_min": 0,
    "total_phase_duration_min": 0,
    "cp01_to_cp02_min": 0,
    "cp02_to_cp03_min": 0,
    "cp04_to_cp05_min": 0
  },
  "change_requests": []
}
```

---

## Sección 5 — Handoff Artifact → 015 Intake

El 010 Discovery entrega al 015 Intake los siguientes artefactos. El 015 no puede iniciarse sin ellos.

```
Registros en BD (lectura por tenant_id):
  ├── clients.tenant_id          → identidad del cliente en el sistema
  ├── client_config.mode         → batch | incremental
  ├── client_config.frequency    → daily | weekly (si incremental)
  ├── client_config.schema2      → true | false
  └── client_config.hierarchies  → niveles de producto y geográficos disponibles

Archivos en Storage:
  └── tenants/{tenant_id}/
      └── bronze/                → carpeta donde 015 depositará la copia exacta de los datos

Evento escuchado por 015:
  └── onboarding_discovery_complete
      ├── tenant_id
      └── timestamp
```

**Condición de activación del 015:** El evento `onboarding_discovery_complete` debe existir en el registro de eventos con `tenant_id` válido y `600_persistence/harness-state.json` del 010 debe tener `"status": "PHASE_COMPLETE"`. Sin ambas condiciones, el 015 no se activa.

**Lo que el 015 NO recibe del 010:**
- No recibe los datos del cliente (archivos de ventas/pedidos) — esos los entrega el cliente directamente
- No recibe instrucciones sobre cómo validar los datos — esas están en el `onboarding_config.json`

---

## Sección 6 — Flujo del Arnés (12.1–12.5)

### 12.1 Inicialización (Instancia A)

**Determinación del modo:**
- No existe `600_persistence/harness-state.json` → **Inicio** (Ritual E10-A)
- Existe e íntegro → **Continuación** (Ritual E10-B)
- Existe pero corrupto → `git restore 600_persistence/harness-state.json`; si persiste, detener y reportar al operador

**Ritual E10-A — Inicio:**
1. Verificar directorio de trabajo y estado del ambiente (herramientas disponibles, dependencias)
2. Crear la jerarquía de carpetas: `/010_discovery/`, `/600_persistence/`, `/605_eval/`, `/610_knowledge/`, `/615_changes/`
3. Inicializar `600_persistence/harness-state.json`, `600_persistence/execution-state.json`, `600_persistence/claude-progress.txt` con esquemas vacíos
4. Ejecutar `git init` y enlazar inmediatamente a un remote en GitHub (`git remote add origin <url>`). Sin este enlace, la trazabilidad (E1/P8) queda en riesgo ante fallos locales
5. Ejecutar verificación de conectividad: BD Supabase + Storage + SendGrid + Prefect
6. Registrar arranque en `600_persistence/claude-progress.txt` con timestamp y datos del cliente
7. Presentar Sprint Contract al operador Triple S

**Ritual E10-B — Continuación:**
1. Verificar directorio y ambiente
2. Leer `600_persistence/claude-progress.txt` (estado narrativo)
3. Cargar `600_persistence/harness-state.json` (Sprint Contract vigente)
4. Leer `600_persistence/execution-state.json` (último checkpoint alcanzado)
5. Seleccionar siguiente tarea según último CP registrado
6. Verificar integridad de artefactos ya producidos (paths existen en filesystem)

**Reporte al operador (obligatorio tras inicialización):**
1. Estado encontrado (modo, integridad, conectividad de servicios)
2. Sprint Contract propuesto (Inicio) o vigente (Continuación)
3. Próxima acción concreta

**Gate de aprobación del operador:**
- Aprobado → A escribe Sprint Contract en `600_persistence/harness-state.json` y spawnea B
- Ajuste requerido → A incorpora cambios, vuelve a presentar
- Cancelación → A registra en `600_persistence/claude-progress.txt`, detiene flujo

### 12.2 Ejecución Técnica (Instancia B + Workers)

1. B lee Sprint Contract desde `600_persistence/harness-state.json` (referencia al archivo, nunca contenido inline)
2. B consulta **obligatoriamente** `/610_knowledge/decisions_library.md` y `/610_knowledge/lessons_learned.md` para ajustar el enfoque según lecciones y decisiones previas. Esta consulta no es opcional — si los archivos no existen aún (primer proyecto), B lo registra en `600_persistence/execution-state.json` y continúa
3. B persiste `orchestration_plan` completo en `600_persistence/execution-state.json` **antes de spawnear ningún Worker** (E12). Si el contexto crece durante la ejecución y B pierde el hilo, relee el plan desde el filesystem sin reconstruirlo
4. B spawnea `discovery-interviewer` con: plantilla de sesión, datos comerciales del cliente (I-1, I-2, I-3)
4. `discovery-interviewer` valida campos de sesión, escribe `/010_discovery/session_data.json`, reporta path a B
   - Si hay campos obligatorios faltantes: `discovery-interviewer` los marca como `MISSING`, escala a operador antes de continuar
5. B registra CP-01 en `600_persistence/execution-state.json`
6. B spawnea `discovery-analyst` con path a `session_data.json`
7. `discovery-analyst` calcula ITO, confirma categoría, asigna nivel cold start, escribe `analysis_report.json`, reporta path a B
   - Si la discrepancia de categoría es > 1 nivel: escalar al operador antes de registrar CP-02
8. B registra CP-02 en `600_persistence/execution-state.json`
9. B spawnea `discovery-configurator` en modo DRAFT: genera `010_discovery/client_profile.json` y `010_discovery/onboarding_config.json` (sin escribir en BD ni Storage aún), reporta paths a B
10. B registra CP-03, marca `DRAFT_COMPLETE` en `600_persistence/execution-state.json`
11. B actualiza `600_persistence/claude-progress.txt` con el estado de la ejecución — esta es la señal que A lee para detectar que los drafts están listos. No existe canal directo B → A

### 12.3 Auditoría y Gate de Aprobación (Instancia C + A)

**Paso 1 — Gate intermedio (A):**
- A verifica que `600_persistence/execution-state.json` tiene `DRAFT_COMPLETE`
- A presenta `010_discovery/client_profile.json` y `010_discovery/onboarding_config.json` al operador para revisión
- Operador aprueba → A registra aprobación en `600_persistence/harness-state.json` (CP-04)
- A retoma B para que `discovery-configurator` ejecute las escrituras reales

**Paso 2 — Escrituras reales (B + `discovery-configurator`):**
- `discovery-configurator` ejecuta en este orden: BD (clients → contacts → client_config → subscriptions) → Storage (carpeta del tenant) → PDF (generación) → correo (envío) → evento (emisión)
- Si cualquier paso falla: activar política de fallback o escalar (Sección 2.3)
- Al completar todos los pasos: B registra CP-05 en `600_persistence/execution-state.json`

**Paso 3 — Auditoría (C):**
- A spawnea C pasando paths a todos los artefactos (nunca contenido inline)
- C verifica: artefactos en filesystem, registros en BD (consulta directa), estructura en Storage, registro del evento
- C evalúa contra rúbrica (Sección 4), aplica anclas de calibración
- C escribe únicamente en sus archivos propios — **C nunca escribe en `600_persistence/harness-state.json`**:
  - `/605_eval/metrics_summary.json` (estructura definida en Sección 4)
  - `/605_eval/verdict.json` (APPROVED/REJECTED con scores por dimensión)
- C registra auditoría en `600_persistence/claude-progress.txt`

**Paso 4 — Decisión final (A — GateKeeper):**
- A lee `/605_eval/verdict.json`
- **APPROVED** → A es el único que actualiza `600_persistence/harness-state.json` marcando `"status": "PHASE_COMPLETE"`; notifica al operador con resumen de lo creado
- **REJECTED** → A activa protocolo 12.4

### 12.4 Protocolo de Rechazo y Reintento

**Rechazo Técnico** (artefacto no cumple rúbrica — C emite REJECTED):

- C escribe el rechazo detallado en `/605_eval/verdict.json`. C no contacta a B directamente.
- A lee el veredicto, marca `IN_REWORK` en `600_persistence/harness-state.json` y spawna B de nuevo, pasándole solo la referencia al archivo de rechazo.
- B lee el informe de rechazo y consulta `/610_knowledge/lessons_learned.md` para evitar repetir errores previos.
- B re-ejecuta **solo los Workers que producen los artefactos fallidos** — nunca todo desde cero.

Casos específicos:
- **D1 < 0.80 (campos faltantes):** A retoma sesión con operador → B re-spawna `discovery-interviewer` en modo complementario (solo campos faltantes) → ciclo desde CP-01
- **D4 = 0.0 o D4 < 1.0 (BD incompleta):** B re-spawna `discovery-configurator` en modo reparación, solo tablas fallidas → si persiste tras 2 reintentos: escalar al operador con log de error
- **D5 = 0.0 o D7 = 0.0 (Storage o evento):** Misma lógica — modo reparación, máximo 2 reintentos, luego escalar

**Rechazo Estratégico** (el operador rechaza los artefactos draft en CP-03):
- A detiene el flujo, marca `HOLD` en `600_persistence/harness-state.json`
- A actualiza el Sprint Contract con el ajuste solicitado
- A requiere nueva aprobación explícita del operador antes de continuar
- Sin aprobación nueva, el harness no avanza

**Protocolo de Gestión de Cambios (CR):**

Cuando el operador solicita un cambio sobre artefactos ya aprobados:
1. A registra el CR en `600_persistence/harness-state.json` bajo `change_requests` con ID (ej: `CR_001`) y estado `OPEN`
2. B crea `/615_changes/CR_001_Descripcion.md` con: alcance del cambio, artefactos afectados, análisis de impacto técnico
3. A presenta el impacto al operador para aprobación; si aprobado, los artefactos afectados se marcan `DEPRECATED` o `PENDING_REWORK` en `600_persistence/harness-state.json`
4. B re-ejecuta solo los componentes afectados; C re-audita
5. A cierra el CR (`CLOSED`) una vez que C aprueba

**Registro de aprendizaje:**
- Todo rechazo (técnico o estratégico) registrado por C en `/610_knowledge/lessons_learned.md` al cierre del harness: qué falló, en qué Worker, cuántos reintentos requirió, regla para evitar repetirlo.

### 12.5 Cierre

1. A marca `"status": "PHASE_COMPLETE"` en `600_persistence/harness-state.json`
2. C actualiza `/610_knowledge/lessons_learned.md` con hallazgos del ciclo: qué funcionó, qué no, reglas para futuros agentes
3. A consolida las decisiones de arquitectura tomadas en `/610_knowledge/decisions_library.md`
4. A notifica al operador: lista de artefactos producidos, registros creados en BD, carpeta Storage, correo enviado, evento confirmado
5. A registra cierre en `600_persistence/claude-progress.txt` con timestamp, resumen y tenant_id
6. A hace commit final: `feat(010-discovery): onboarding complete — {tenant_id} configurado`

---

## Sección 7 — Notas de Construcción

### Agentes a crear

| Nombre | Tipo | Descripción |
|--------|------|-------------|
| `discovery-interviewer` | Worker | Guía al operador, valida campos de la sesión, detecta inconsistencias |
| `discovery-analyst` | Worker | Calcula ITO, confirma categoría M/L/XL, asigna nivel cold start |
| `discovery-configurator` | Worker | Genera artefactos, escribe en BD/Storage, envía correo, emite evento |

### Skills requeridos

- Acceso a Supabase PostgreSQL (CRUD en tablas `clients`, `contacts`, `client_config`, `subscriptions`)
- Acceso a Supabase Storage (creación de carpetas por tenant)
- Acceso a SendGrid (envío de correo con adjunto PDF)
- Acceso a Prefect (emisión del evento `onboarding_discovery_complete`)
- Generación de PDF desde plantilla Jinja2 o equivalente

### Consideraciones de implementación

- El ITO usa la fórmula `ITO = w1 × SKUs_activos + w2 × clientes_XYZ + w3 × pedidos_por_mes`. Los pesos w1, w2, w3 y umbrales M/L/XL están pendientes de calibración (T-030). Para la Fase 1 (Excel), el operador puede calcular el ITO manualmente y registrar el resultado.
- En **Fase 1** (Excel/CSV), el `discovery-configurator` no requiere Supabase: escribe los registros en archivos locales y los artefactos en carpetas locales. La arquitectura de Workers es la misma.
- La `data_intake_guide.pdf` es el primer entregable tangible que el cliente recibe — su lenguaje debe ser 100% de negocio, sin terminología técnica. Usar plantilla con: qué es el archivo, qué columnas son obligatorias (marcadas claramente), qué columnas son opcionales y para qué sirven, formato aceptado (CSV / Excel), dónde subir el archivo (URL del dashboard o instrucción de envío por correo en Fase 1).
- La estructura de carpetas en Storage (`tenants/{id}/...`) se crea aquí y **nunca se recrea**. Los harnesses 015 y posteriores solo escriben dentro de ella.
- Este es el único harness donde el operador Triple S tiene un rol activo y presencial con el cliente. El operador NO es un agente — es un humano que aprueba los gates.
