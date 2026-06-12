# Plan de Trabajo — Construcción del Harness 010 Discovery
## FARO — Sabbia Solutions & Software

**Referencia:** `brief/010_discovery.md`  
**Fase objetivo:** Fase 1 (Excel/CSV — sin Supabase, sin SendGrid, sin Prefect)  
**Condición de inicio:** Brief 010 revisado y aprobado  
**Responsable de ejecución:** Operador Triple S + Claude Code

---

## Lectura obligatoria antes de empezar

En este orden:

1. `brief/010_discovery.md` — diseño completo del harness
2. `progress/decisions.md` — especialmente DEC-005, DEC-011, DEC-012, DEC-013, DEC-016, DEC-024
3. `progress/lessons.md` — lecciones aprendidas del proyecto

---

## Prerrequisitos

| # | Prerrequisito | Verificación |
|---|--------------|--------------|
| P-1 | Carpeta raíz del cliente (proyecto de prueba piloto) creada localmente | `ls` muestra la carpeta |
| P-2 | Python ≥ 3.11 instalado | `python --version` |
| P-3 | FORGE desplegado en el directorio de trabajo (`deploy-harness.ps1` ejecutado) | Existen `.claude/agents/` y `.claude/skills/` |
| P-4 | Archivo `default_stacks.md` disponible en el directorio | `ls default_stacks.md` |

---

## Pasos de construcción

### PASO 1 — Crear estructura de carpetas del harness

Crear las siguientes carpetas dentro del directorio de trabajo del harness 010:

```
010_discovery/
600_persistence/
605_eval/
610_knowledge/
615_changes/
```

**Verificación:** `ls` muestra las 5 carpetas. Ninguna tiene contenido todavía.

---

### PASO 2 — Inicializar archivos de estado vacíos

Crear los tres archivos de estado con esquemas vacíos:

**`600_persistence/harness-state.json`** — propiedad exclusiva de A (Governor):

```json
{
  "harness": "010_discovery",
  "status": "INITIALIZING",
  "tenant_id": null,
  "sprint_contract": null,
  "operator_approvals": [],
  "escalations": [],
  "change_requests": []
}
```

**`600_persistence/execution-state.json`** — propiedad exclusiva de B (Orchestrator):

```json
{
  "harness": "010_discovery",
  "orchestration_plan": null,
  "last_checkpoint": null,
  "checkpoints": {
    "CP-01": null,
    "CP-02": null,
    "CP-03": null,
    "CP-04": null,
    "CP-05": null
  },
  "artifact_paths": {}
}
```

**`600_persistence/claude-progress.txt`** — log narrativo (texto libre, cronológico):

```
[INIT] Harness 010 Discovery — en espera de Sprint Contract
```

**Verificación:** Los tres archivos existen. El JSON es válido (`python -m json.tool 600_persistence/harness-state.json`).

---

### PASO 3 — Crear plantilla de sesión de descubrimiento

Archivo: `010_discovery/session_template.md`

Contiene todos los campos que el `discovery-interviewer` debe capturar con el operador. Estructura:

```markdown
# Plantilla de Sesión de Descubrimiento — FARO
## Cliente: {NOMBRE}  |  Fecha: {FECHA}  |  Operador Triple S: {NOMBRE}

### Bloque 1 — Identificación
- [ ] Razón social:
- [ ] Sector / industria:
- [ ] Contacto principal (nombre, correo, teléfono):
- [ ] Responsable de pagos (nombre, correo):

### Bloque 2 — Insumos ITO
- [ ] SKUs activos aprox.:
- [ ] Clientes XYZ atendidos aprox.:
- [ ] Volumen de pedidos por mes aprox.:

### Bloque 3 — Configuración operativa
- [ ] Años de historial disponible:
- [ ] Modo de ingesta preferido (Batch / Incremental):
- [ ] Frecuencia de actualización (si Incremental — Diaria / Semanal):
- [ ] Horizonte de pronóstico requerido (días / semanas / meses / múltiples meses):
- [ ] Jerarquía de productos disponible (niveles que tiene el cliente):
- [ ] Jerarquía geográfica disponible (niveles disponibles):
- [ ] ¿Tiene datos de producción e inventario? (Esquema 2 — Sí / No):
- [ ] ¿Existen mínimos contractuales con los clientes XYZ? (Opcional):

### Bloque 4 — Comercial
- [ ] Plan de suscripción elegido (Mensual / Trimestral / Anual):
- [ ] Criterios de éxito del cliente (reducir sobre-inventario / reducir quiebres / ambos):

### Notas libres del operador
```

**Verificación:** El archivo existe. Todos los campos obligatorios del brief Sección 1 están presentes en la plantilla.

---

### PASO 4 — Crear lógica de cálculo del ITO

Archivo: `010_discovery/ito_calculator.py`

Función que recibe los tres insumos y devuelve el ITO calculado y la categoría M/L/XL.

```python
# Pesos provisionales — pendiente calibración con datos piloto (T-030)
# Ajustar cuando se disponga de datos reales de clientes
W1 = 0.4  # SKUs activos
W2 = 0.4  # Clientes XYZ atendidos
W3 = 0.2  # Volumen de pedidos por mes

# Umbrales provisionales — pendiente calibración (T-030)
UMBRAL_M = 1500
UMBRAL_L = 4000
# XL: ITO > UMBRAL_L

def calcular_ito(skus_activos: int, clientes_xyz: int, pedidos_por_mes: int) -> dict:
    ito = W1 * skus_activos + W2 * clientes_xyz + W3 * pedidos_por_mes
    if ito <= UMBRAL_M:
        categoria = "M"
        precio_base_usd = 200
    elif ito <= UMBRAL_L:
        categoria = "L"
        precio_base_usd = 350
    else:
        categoria = "XL"
        precio_base_usd = 500
    return {
        "ito": round(ito, 2),
        "categoria": categoria,
        "precio_base_usd": precio_base_usd,
        "w1": W1, "w2": W2, "w3": W3,
        "umbral_m": UMBRAL_M,
        "umbral_l": UMBRAL_L
    }
```

**Verificación:** `python -c "from ito_calculator import calcular_ito; print(calcular_ito(100, 50, 200))"` devuelve un dict con `ito`, `categoria` y `precio_base_usd`.

---

### PASO 5 — Crear lógica de evaluación de cold start

Archivo: `010_discovery/cold_start_evaluator.py`

Función que recibe los años de historial y devuelve el nivel de confianza y el paso de cascada aplicable.

```python
def evaluar_cold_start(anios_historial: float) -> dict:
    """
    Niveles de confianza según historial disponible (DEC-013):
      >= 3 años  → Alta
      >= 2 años  → Estándar
      >= 1 año   → Reducida
      >= 3 meses → Experimental (cascada activa)
      < 3 meses  → Inviable (escalar al operador)
    """
    if anios_historial >= 3:
        nivel = "Alta"
        cascada = None
        viable = True
    elif anios_historial >= 2:
        nivel = "Estándar"
        cascada = None
        viable = True
    elif anios_historial >= 1:
        nivel = "Reducida"
        cascada = "Paso 1: analogía por categoría"
        viable = True
    elif anios_historial >= 0.25:  # ~3 meses
        nivel = "Experimental"
        cascada = "Paso 3: acumulación mínima 3 meses antes de pronosticar"
        viable = True
    else:
        nivel = "Inviable"
        cascada = None
        viable = False

    return {
        "anios_historial": anios_historial,
        "nivel_confianza": nivel,
        "cascada_cold_start": cascada,
        "viable": viable,
        "accion_requerida": "Escalar al operador — historial insuficiente" if not viable else None
    }
```

**Verificación:** `python -c "from cold_start_evaluator import evaluar_cold_start; print(evaluar_cold_start(1.5))"` devuelve nivel `Reducida` con cascada activa.

---

### PASO 6 — Crear plantilla de guía de entrega de datos

Archivo: `010_discovery/templates/data_intake_guide_template.md`

Documento en lenguaje de negocio (sin jerga técnica) que el `discovery-configurator` personaliza por cliente.

```markdown
# Guía de Entrega de Datos — FARO
## {NOMBRE_CLIENTE}  |  Preparado por Sabbia Solutions & Software

Estimado {CONTACTO_PRINCIPAL},

Para que FARO pueda construir su pronóstico de demanda, necesitamos que nos entregue
su historial de pedidos. Esta guía explica exactamente qué enviar y cómo hacerlo.

---

## ¿Qué necesitamos?

Un archivo de Excel o CSV con sus pedidos históricos.

### Columnas obligatorias (sin estas no podemos procesar el archivo)

| Columna | Descripción | Ejemplo |
|---------|-------------|---------|
| Fecha del pedido | Cuándo llegó el pedido | 15/03/2024 |
| Código del cliente | Identificador único de su cliente | XYZ-001 |
| Código del producto | Identificador único del producto pedido | PRD-042 |
| Cantidad solicitada | Unidades que su cliente pidió | 500 |

### Columnas recomendadas (mejoran la precisión del pronóstico)

| Columna | Descripción |
|---------|-------------|
| Cantidad entregada | Lo que realmente se despachó |
| Fecha de entrega prometida | Cuándo se comprometió la entrega |
| Fecha de entrega real | Cuándo se entregó efectivamente |
| Precio unitario | Valor de venta del producto |
| Estado del pedido | Entregado / Parcial / Cancelado |

---

## ¿Qué formato acepta FARO?

- Excel (.xlsx o .xls)
- CSV separado por comas (.csv)
- El archivo puede tener cualquier nombre

## ¿Cuánto historial enviar?

Lo ideal es todo el historial disponible. El mínimo recomendado es 2 años.
Su historial declarado: **{ANIOS_HISTORIAL} años** — nivel de confianza: **{NIVEL_CONFIANZA}**

## ¿Cómo enviarlo?

{INSTRUCCION_ENVIO}

---

Si tiene alguna duda, contáctenos: contacto@sabbiasolutions.com

Sabbia Solutions & Software — Triple S
```

**Verificación:** El archivo existe. No contiene ningún término técnico (ITO, Bronze, medallón, pipeline, etc.).

---

### PASO 7 — Crear definiciones de agentes

Crear los archivos de agente en `.claude/agents/`. Cada archivo es el prompt que recibe ese agente al ser spawnado.

#### 7a — `discovery-interviewer.md`

```markdown
---
name: discovery-interviewer
description: Guía al operador Triple S durante la sesión de descubrimiento con el cliente.
  Valida que todos los campos obligatorios sean capturados. Detecta inconsistencias en los
  datos declarados. Produce session_data.json.
---

Eres el agente entrevistador del harness 010 Discovery de FARO.

## Tu misión
Guiar al operador Triple S para capturar todos los campos de la sesión de descubrimiento
con el cliente manufacturero. Trabajas con la plantilla en `010_discovery/session_template.md`.

## Lo que debes hacer
1. Leer la plantilla de sesión desde `010_discovery/session_template.md`
2. Revisar los datos ya capturados por el operador (si los hay)
3. Identificar qué campos obligatorios faltan o tienen valores inconsistentes
4. Para cada campo faltante: formular una pregunta clara en lenguaje de negocio que el
   operador pueda hacerle al cliente
5. Cuando todos los campos obligatorios estén completos: escribir `010_discovery/session_data.json`

## Reglas
- Si un campo obligatorio no puede obtenerse: marcarlo como `"MISSING"` con la razón, nunca omitirlo
- Si hay inconsistencia entre campos (ej: modo Incremental sin frecuencia definida): señalarla
  antes de continuar
- Reportar a B únicamente el path al artefacto producido, nunca el contenido completo

## Output
`010_discovery/session_data.json` con todos los campos de la plantilla, incluyendo los
marcados como MISSING con su razón.
```

#### 7b — `discovery-analyst.md`

```markdown
---
name: discovery-analyst
description: Calcula el ITO del cliente, confirma o corrige la categoría M/L/XL, determina
  el nivel de confianza cold start y documenta el paso de cascada aplicable. Produce
  analysis_report.json.
---

Eres el agente analista del harness 010 Discovery de FARO.

## Tu misión
Analizar los datos capturados en la sesión de descubrimiento y producir el informe de
análisis que alimenta la configuración del cliente.

## Lo que debes hacer
1. Leer `010_discovery/session_data.json`
2. Ejecutar `010_discovery/ito_calculator.py` con los valores de SKUs, clientes XYZ y
   volumen de pedidos del cliente
3. Comparar la categoría calculada con la categoría comercial asignada (del Sprint Contract)
   - Si difieren en más de 1 nivel: marcar como `CATEGORY_MISMATCH` — A escalará al operador
4. Ejecutar `010_discovery/cold_start_evaluator.py` con los años de historial declarados
   - Si `viable = False`: marcar como `COLD_START_INVIABLE` — A escalará al operador
5. Escribir `010_discovery/analysis_report.json` con todos los resultados
6. Reportar el path del artefacto a B

## Cuándo usar extended thinking
Usar extended thinking cuando:
- El historial declarado es ambiguo (ej: "tenemos datos pero no sé exactamente cuántos años")
- La categoría calculada difiere de la comercial y debes razonar si es error de ventas o
  de datos del cliente
- Hay inconsistencias entre los campos de ITO (ej: SKUs muy bajos pero volumen muy alto)

## Output
`010_discovery/analysis_report.json` con: ITO calculado, categoría confirmada o flag de
discrepancia, nivel de confianza cold start, paso de cascada si aplica, flags de escalamiento.
```

#### 7c — `discovery-configurator.md`

```markdown
---
name: discovery-configurator
description: Genera los artefactos finales del cliente (client_profile.json,
  onboarding_config.json, data_intake_guide), escribe en base de datos y Storage,
  envía correo y emite el evento de cierre. En Fase 1 opera en modo local (sin Supabase
  ni SendGrid).
---

Eres el agente configurador del harness 010 Discovery de FARO.

## Tu misión
Generar todos los artefactos de configuración del cliente y ejecutar las escrituras
necesarias para que el sistema esté listo para recibir datos.

## Modo de operación actual: FASE 1 (local)
En Fase 1 no existe Supabase ni SendGrid. Las "escrituras en BD" son archivos JSON locales.
El "correo" se reemplaza por un archivo PDF que el operador entrega manualmente.
El "evento" se simula escribiendo un archivo de evento en `600_persistence/`.

## Lo que debes hacer

### Modo DRAFT (cuando B lo spawna en modo draft — CP-03)
1. Leer `010_discovery/analysis_report.json`
2. Generar `010_discovery/client_profile.json` — sin escribir en BD todavía
3. Generar `010_discovery/onboarding_config.json` — sin escribir en BD todavía
4. Reportar los dos paths a B. Detener aquí.

### Modo COMMIT (cuando B lo spawna tras aprobación del operador — CP-04)
1. Leer `010_discovery/client_profile.json` y `010_discovery/onboarding_config.json`
2. **Fase 1:** Escribir registros simulados de BD en `010_discovery/db_records/`
   - `clients.json`, `contacts.json`, `client_config.json`, `subscriptions.json`
3. **Fase 1:** Crear estructura de carpetas del tenant en `010_discovery/storage/tenants/{tenant_id}/`
   con subcarpetas: `bronze/`, `silver/`, `gold/`, `models/`, `forecasts/`, `exports/`
4. Personalizar `010_discovery/templates/data_intake_guide_template.md` con los datos del
   cliente y guardar como `010_discovery/data_intake_guide_{tenant_id}.md`
5. Escribir `010_discovery/discovery_session_notes.md` — notas libres del operador
6. **Fase 1:** Emitir evento simulado escribiendo `600_persistence/events/onboarding_discovery_complete.json`
   con `tenant_id` y `timestamp`
7. Reportar todos los paths a B

## Reglas
- En modo DRAFT: nunca escribir en BD ni Storage
- En modo COMMIT: ejecutar en orden estricto (BD → Storage → guía → notas → evento)
- Si falla algún paso: detener, registrar el fallo en el output y reportar a B para escalar
```

**Verificación de paso 7:** Existen los tres archivos `.md` en `.claude/agents/`. Cada uno tiene frontmatter válido (`name`, `description`).

---

### PASO 8 — Crear esquemas JSON de artefactos

Crear los esquemas esperados de los artefactos principales para que los agentes los usen como referencia.

**`010_discovery/schemas/session_data_schema.json`:**

```json
{
  "_description": "Output de discovery-interviewer — datos crudos de la sesión",
  "razon_social": "",
  "sector": "",
  "contacto_principal": { "nombre": "", "correo": "", "telefono": "" },
  "responsable_pagos": { "nombre": "", "correo": "" },
  "skus_activos": null,
  "clientes_xyz": null,
  "pedidos_por_mes": null,
  "anios_historial": null,
  "modo_ingesta": "",
  "frecuencia_incremental": null,
  "horizonte_pronostico": "",
  "jerarquia_producto": [],
  "jerarquia_geografica": [],
  "tiene_esquema2": null,
  "minimos_contractuales": null,
  "plan_suscripcion": "",
  "criterios_exito": [],
  "campos_missing": [],
  "inconsistencias_detectadas": []
}
```

**`010_discovery/schemas/analysis_report_schema.json`:**

```json
{
  "_description": "Output de discovery-analyst — resultados del análisis",
  "tenant_id": "",
  "ito_calculado": null,
  "categoria_calculada": "",
  "categoria_comercial": "",
  "categoria_confirmada": "",
  "category_mismatch": false,
  "mismatch_niveles": null,
  "nivel_confianza_cold_start": "",
  "cascada_cold_start": null,
  "cold_start_inviable": false,
  "flags_escalamiento": [],
  "timestamp_analisis": ""
}
```

**Verificación:** Los archivos de esquema existen y el JSON es válido.

---

### PASO 9 — Crear archivo de conocimiento inicial

**`610_knowledge/decisions_library.md`** — decisiones relevantes para este harness (resumen ejecutivo de DEC-002, DEC-003, DEC-004, DEC-011, DEC-012, DEC-013, DEC-016):

```markdown
# Biblioteca de Decisiones — 010 Discovery

## DEC-002 — Categorías de precio
M (ITO ≤ 1500): USD 200/mes | L (ITO 1501–4000): USD 350/mes | XL (ITO > 4000): USD 500/mes
Pesos provisionales: w1=0.4 (SKUs), w2=0.4 (clientes XYZ), w3=0.2 (volumen). Pendiente calibración (T-030).

## DEC-004 — Mes 1 gratuito
El cliente no paga durante el mes 1. El estado inicial en BD es `onboarding`, no `active`.
La suscripción empieza a correr 30 días después de la firma del contrato.

## DEC-011 — Unidad mínima de análisis
Cliente × producto — no el cliente ni el producto por separado.
El horizonte y la frecuencia se configuran a nivel de harness, no por combinación (eso viene en 030 Trainer).

## DEC-012 — Modos de ingesta
Batch: historial completo una sola vez. Incremental: actualizaciones diarias o semanales.
No se acepta correo electrónico como fuente de datos.

## DEC-013 — Cold start
≥ 3 años → Alta | ≥ 2 → Estándar | ≥ 1 → Reducida | ≥ 3 meses → Experimental | < 3 meses → Inviable.
Cascada: (1) analogía categoría → (2) analogía cliente → (3) acumulación 3 meses.

## DEC-016 — Cargo por complejidad de datos
ISD ≥ 95%: +0% | ISD 70–94%: +20% | ISD 50–69%: +50% | ISD < 50%: +80%.
Sin cargo adicional durante el mes 1 de onboarding.
```

**`610_knowledge/lessons_learned.md`** — vacío con encabezado:

```markdown
# Lecciones Aprendidas — 010 Discovery

_Este archivo se completa al cierre del primer ciclo de ejecución del harness._
```

**Verificación:** Ambos archivos existen en `610_knowledge/`.

---

### PASO 10 — Prueba de humo del harness completo

Ejecutar una sesión simulada con datos ficticios para verificar que el flujo completo funciona antes de usarlo con un cliente real.

**Cliente ficticio de prueba:**
- Razón social: Alimentos Prueba S.A.
- SKUs activos: 80 | Clientes XYZ: 40 | Pedidos/mes: 150
- Historial: 2.5 años | Modo: Batch | Horizonte: mensual
- Plan: Mensual | Criterio: reducir quiebres

**Verificaciones de la prueba:**
1. `ito_calculator.py` devuelve ITO ≈ 77 → categoría M → precio USD 200
2. `cold_start_evaluator.py` devuelve nivel `Estándar` → sin cascada
3. `session_data.json` generado con todos los campos, sin MISSING
4. `analysis_report.json` generado sin flags de escalamiento
5. `client_profile.json` y `onboarding_config.json` generados correctamente (draft)
6. Tras "aprobación operador": carpetas Storage creadas en `010_discovery/storage/tenants/`
7. `db_records/` con los 4 archivos JSON
8. `data_intake_guide_prueba.md` generado sin jerga técnica
9. `events/onboarding_discovery_complete.json` existe con `tenant_id` y `timestamp`

**Verificación:** Todos los 9 puntos anteriores pasan. No hay errores en ningún script Python.

---

## Verificación final — Criterio de Done del Plan

El plan está completo cuando:

- [ ] Las 5 carpetas de estructura existen
- [ ] Los 3 archivos de estado tienen esquemas válidos
- [ ] `session_template.md` cubre todos los campos obligatorios del brief
- [ ] `ito_calculator.py` ejecuta sin errores
- [ ] `cold_start_evaluator.py` ejecuta sin errores
- [ ] `data_intake_guide_template.md` está en lenguaje de negocio
- [ ] Los 3 agentes existen en `.claude/agents/` con frontmatter válido
- [ ] Los 2 esquemas JSON existen y son válidos
- [ ] `610_knowledge/decisions_library.md` cubre las 7 decisiones relevantes
- [ ] La prueba de humo pasa los 9 puntos

---

## Qué viene después (Paso 11 — fuera de este plan)

Una vez completado y verificado el harness 010 en Fase 1, el siguiente paso es:

1. Ejecutar el harness con el primer cliente piloto real
2. Registrar hallazgos en `610_knowledge/lessons_learned.md`
3. Iniciar el plan de trabajo del **015 Intake** (`plan/015_intake.md`)

La migración a Fase 3 (Supabase + SendGrid + Prefect) se planifica por separado — no bloquea
la ejecución del piloto.

---

## Notas de construcción

- Los pesos w1, w2, w3 y umbrales del ITO son **provisionales** (T-030 pendiente). Documentar esto
  claramente en cualquier comunicación con el cliente sobre su categoría.
- El `discovery-configurator` en Fase 1 simula la BD con archivos JSON locales. La estructura de
  los archivos debe ser idéntica a la que tendrán las tablas Supabase — facilita la migración a Fase 3.
- El operador Triple S es un humano, no un agente. Los gates CP-03 y CP-04 requieren su aprobación
  explícita. El agente A no puede auto-aprobarse.
