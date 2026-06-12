# Harness 055 — Command

**Tipo:** Event-driven  
**Bloque de construcción:** D (posición 10 de 11)  
**Hito al que pertenece:** Hito D — Excelencia operativa  
**Disparadores:** Eventos de todos los demás harnesses + acciones manuales del operador de Triple S

---

## Propósito

Ser el centro de operaciones internas de Triple S. Mientras 045 Monitor observa y alerta, 055 Command es donde el operador actúa: gestiona clientes, resuelve conflictos de datos, controla el pipeline, ajusta modelos y toma decisiones que el sistema no puede tomar de forma autónoma.

Es el único harness que tiene una interfaz de usuario para el equipo interno de Triple S. El cliente nunca lo ve ni lo toca.

La diferencia con 045 Monitor es fundamental: **Monitor detecta, Command resuelve**.

---

## Audiencia

Operadores de Triple S — las personas que entregan el servicio al cliente. No es para el cliente ABC, no es para el cliente XYZ. Es para el equipo interno que opera el sistema de punta a punta.

---

## Eventos que escucha

| Evento | Origen | Acción que dispara en Command |
|--------|--------|-------------------------------|
| `onboarding_discovery_complete` | 010 Discovery | Abre la ficha del cliente nuevo en el portal |
| `intake_complete` | 015 Intake | Notifica al operador que los datos llegaron |
| `diagnosis_complete` | 020 Diagnosis | Actualiza la vista de salud de datos en el portal |
| `refinery_complete` | 025 Refinery | Actualiza el conteo de combinaciones y maestros |
| `trainer_complete` | 030 Trainer | Notifica si hay modelos con advertencia de SLA |
| `predictor_complete` | 035 Predictor | Notifica si hay anomalías sin clasificar |
| `publisher_complete` | 040 Publisher | Confirma entrega al cliente; actualiza semáforo del ciclo |
| `monitoring_report` | 045 Monitor | Actualiza KPIs y alertas activas en el portal |
| `client_suspended` | 050 Lifecycle | Notificación urgente al operador |
| `client_cancelled` | 050 Lifecycle | Inicia el proceso manual de exportación si el cliente lo solicita |
| Acción manual del operador | Portal Command | Ejecuta la operación solicitada |

---

## Procesos

### P1 — Portal de operaciones: vista global de clientes

El portal muestra al operador una tabla de todos los clientes activos con su estado en tiempo real:

| Columna | Descripción |
|---------|-------------|
| Cliente | Razón social |
| Estado | `onboarding` / `activo` / `en_mora` / `suspendido` / `cancelado` |
| Días de mora | Si aplica — con semáforo de color |
| ISD actual | Puntaje y nivel |
| Último pronóstico | Fecha de la última publicación |
| MAPE real | Último MAPE real calculado vs. umbral SLA |
| Pipeline | Semáforo: todos los harnesses OK / advertencia / error |
| Acciones | Botones contextuales según el estado del cliente |

El operador puede filtrar por estado, categoría (M/L/XL), plan, nivel de ISD o condición de alerta. Desde esta vista accede a la ficha individual de cada cliente.

### P2 — Ficha individual del cliente

Al seleccionar un cliente, el operador ve:

- **Datos de contacto:** contacto principal + responsable de pagos
- **Suscripción:** categoría, plan, monto actual (base + cargo complejidad), próximo vencimiento
- **Pipeline:** estado de cada harness (última ejecución, latencia, resultado)
- **Modelos:** número de combinaciones por estrategia, MAPE promedio holdout, fecha del último entrenamiento
- **Anomalías pendientes:** combinaciones con anomalías sin clasificar esperando confirmación del cliente
- **Maestros de datos:** acceso de lectura a los tres maestros del cliente
- **Conflictos sin resolver:** aliases que 025 Refinery no pudo unificar automáticamente por empate
- **Historial de ISD:** gráfico de tendencia de los últimos 6 ciclos
- **Historial de pagos:** facturas, fechas, montos, estado

### P3 — Operaciones de gestión del cliente

Acciones manuales que el operador puede ejecutar desde la ficha del cliente:

| Operación | Descripción | Efecto en el sistema |
|-----------|-------------|---------------------|
| **Cambiar categoría** | Corregir M/L/XL si el ITO preliminar estuvo mal | Actualiza `subscriptions.next_invoice_amount`; notifica a 050 Lifecycle |
| **Cambiar plan** | Mover al cliente de mensual a trimestral o anual | Actualiza `subscriptions`; recalcula próximo vencimiento en 050 |
| **Registrar cancelación** | Iniciar el proceso de baja del cliente | Dispara P8 de 050 Lifecycle |
| **Aprobar exportación post-cancelación** | Confirmar que se procesará la exportación solicitada | Actualiza `export_requests`; genera el archivo exportable |
| **Extender período de gracia** | Dar días adicionales antes de suspender (decisión comercial discrecional) | Actualiza `clients.suspension_date` manualmente |
| **Reactivar cliente suspendido manualmente** | En casos donde el pago se confirmó por fuera de Stripe | Dispara P7 de 050 Lifecycle con `payment_source = manual` |

### P4 — Operaciones de pipeline

El operador puede intervenir en el pipeline de cualquier cliente:

| Operación | Cuándo usarla | Efecto |
|-----------|---------------|--------|
| **Re-ejecutar un harness** | Cuando un harness falló y el problema subyacente fue corregido | Dispara el evento de inicio del harness correspondiente |
| **Forzar re-ingesta** | Cuando el cliente entregó un archivo corregido | Ejecuta 015 Intake sobre el nuevo archivo, reemplaza el Bronze si el operador lo aprueba explícitamente |
| **Forzar re-diagnóstico** | Después de que el cliente mejoró sus datos | Ejecuta 020 Diagnosis sobre el Bronze actual |
| **Forzar reentrenamiento** | Cuando los modelos derivaron o el cliente tuvo un cambio estructural | Ejecuta 030 Trainer con los modelos actuales de Gold |
| **Forzar re-predicción** | Para generar un pronóstico corregido mid-month | Ejecuta 035 Predictor con los modelos actuales |
| **Publicar corrección** | Después de re-predicción aprobada | Ejecuta 040 Publisher con el pronóstico corregido |

Toda intervención manual queda registrada en `command_log` con el operador, timestamp, razón y resultado. Esto garantiza trazabilidad completa de toda operación no automática.

### P5 — Resolución de conflictos de maestros de datos

Cuando 025 Refinery detecta aliases en empate (dos nombres con la misma frecuencia para el mismo ID), los escala aquí para resolución manual:

El portal muestra al operador una cola de conflictos pendientes:

```
Producto ID: PRD-0421
  Alias A: "ACEITE VEGETAL 5L"   → aparece en 234 pedidos
  Alias B: "ACEITE VEG. 5 LTS"  → aparece en 234 pedidos
  ¿Cuál es el nombre canónico?  [Elegir A] [Elegir B] [Escribir nombre correcto]
```

Una vez que el operador resuelve el conflicto, el harness:
1. Actualiza el maestro de productos en `master_products`
2. Aplica el cambio retroactivamente en Silver (re-etiquetando los registros afectados)
3. Marca el conflicto como resuelto en `master_conflicts`
4. Si el Gold depende de la combinación afectada, programa un reentrenamiento parcial

### P6 — Gestión del registro de eventos

El harness mantiene la tabla `events_registry` que 035 Predictor usa para clasificar anomalías como extraordinarias legítimas.

El operador registra eventos que afectan la demanda del cliente:

| Campo | Descripción |
|-------|-------------|
| `tenant_id` | Cliente al que aplica el evento |
| `event_type` | `temporada_alta` / `temporada_baja` / `cierre_planta` / `promocion` / `otro` |
| `description` | Texto libre descriptivo |
| `date_start` | Inicio del período afectado |
| `date_end` | Fin del período afectado |
| `products_affected` | Lista de IDs de producto afectados (vacío = todos) |
| `clients_affected` | Lista de IDs de cliente XYZ afectados (vacío = todos) |

Los eventos pueden registrarse hacia el futuro (para períodos próximos) o retroactivamente (para clasificar anomalías pasadas sin explicación en ese momento).

### P7 — Operaciones de modelos

El operador puede intervenir en la gestión de los modelos de ML:

| Operación | Descripción |
|-----------|-------------|
| **Ver detalle de un modelo** | Metadatos completos de cualquier combinación: versión, algoritmo, MAPE holdout, features usados, hiperparámetros |
| **Comparar versiones de un modelo** | Comparar el modelo actual vs. el anterior en MAPE holdout |
| **Rollback de modelo** | Revertir una combinación al modelo anterior si el nuevo deterioró el MAPE real |
| **Excluir períodos del entrenamiento** | Marcar períodos específicos como errores de datos para que 030 Trainer los ignore | 
| **Ajustar estrategia de cold start** | Cambiar manualmente la estrategia de una combinación (ej. forzar analogía de categoría) |

El rollback no elimina el modelo nuevo — lo marca como `status = 'rolled_back'` en `model_registry` y restaura el anterior como activo. Si el modelo nuevo mejora en el siguiente ciclo, el operador puede volver a activarlo.

### P8 — Dashboard de KPIs internos

El portal muestra los 6 KPIs calculados por 045 Monitor con visualizaciones de tendencia:

**Vista de portada del portal Command:**

```
┌─────────────────────────────────────────────────────────┐
│  TRIPLE S — HARNESS FORECASTER — PORTAL INTERNO         │
├──────────────┬──────────────┬──────────────┬────────────┤
│ Conversión   │ Tiempo 1er   │ Retención    │ ISD medio  │
│ Onboarding   │ Pronóstico   │ Mensual      │ Cohorte 3m │
│   87%  ↑     │   48 días ↓  │   96.2% →    │   81% ↑    │
├──────────────┴──────────────┴──────────────┴────────────┤
│ MAPE vs SLA: 91% clientes OK  │  Planes: 40% M / 35% L  │
├──────────────────────────────────────────────────────────┤
│ ALERTAS ACTIVAS (3)                                      │
│ 🔴 CLI-004: sin pronóstico — día 7 hábil del mes        │
│ 🟡 CLI-011: drift en 18 combinaciones — 3 meses         │
│ 🟡 CLI-019: datos sin llegar — 12 días en modo diario   │
└──────────────────────────────────────────────────────────┘
```

Cada KPI tiene un gráfico de tendencia de los últimos 6 meses y un umbral meta visible. Las alertas activas son clickeables y llevan directamente a la ficha del cliente afectado.

### P9 — Registro de toda operación manual

Toda acción ejecutada desde el portal Command queda registrada en `command_log`:

```json
{
  "operation_id": "CMD-20260608-0047",
  "operator": "juan@triplesolutions.com",
  "timestamp": "2026-06-08T14:23:11Z",
  "tenant_id": "CLI-011",
  "operation_type": "force_retrain",
  "reason": "Drift detectado en 18 combinaciones — posible cambio de temporada",
  "result": "success",
  "harness_triggered": "030_trainer",
  "trigger_event_id": "EVT-20260608-0193"
}
```

Este log es la fuente de verdad de todo lo que el equipo de Triple S hizo fuera del flujo automático. Es indispensable para auditoría y para entender por qué el sistema se desvió de su comportamiento normal en un período dado.

---

## Salidas

### Registros actualizados en base de datos

| Tabla | Actualización |
|-------|--------------|
| `command_log` | Toda operación manual ejecutada |
| `master_conflicts` | Estado de resolución de conflictos de maestros |
| `events_registry` | Eventos registrados por el operador |
| `model_registry` | Rollbacks, ajustes de estrategia cold start |
| `excluded_periods` | Períodos excluidos del entrenamiento por decisión del operador |
| `clients` | Cambios de categoría, plan, o extensiones de gracia |

### Eventos emitidos

| Evento | Cuándo |
|--------|--------|
| `manual_retrain_triggered` | Al forzar reentrenamiento — recibido por 030 Trainer |
| `manual_rerun_triggered` | Al forzar re-ejecución de un harness — recibido por el harness correspondiente |
| `master_conflict_resolved` | Al resolver un conflicto — recibido por 025 Refinery |
| `event_registered` | Al agregar un evento al registro — recibido por 035 Predictor |
| `model_rolled_back` | Al revertir un modelo — recibido por 035 Predictor |

---

## Lo que este harness NO hace

- No genera pronósticos ni calcula métricas — consume lo que producen los demás
- No tiene contacto con el cliente ABC — toda comunicación al cliente pasa por 040 Publisher
- No toma decisiones de negocio automáticas — facilita que el operador las tome
- No reemplaza el juicio humano — es una herramienta para ejercerlo con información completa

---

## Dependencias

| Tipo | Harness / Sistema | Detalle |
|------|-------------------|---------|
| Datos | Todos los harnesses | Consume eventos y tablas de todos para construir la vista del portal |
| Dispara | 030 Trainer | Cuando el operador fuerza reentrenamiento |
| Dispara | 025 Refinery | Cuando el operador resuelve un conflicto de maestro |
| Dispara | 035 Predictor | Cuando el operador fuerza re-predicción |
| Dispara | 040 Publisher | Cuando el operador aprueba la publicación de una corrección |
| Dispara | 050 Lifecycle | Cuando el operador registra una cancelación o reactivación manual |

---

## Notas de diseño

- **055 se construye después de 045 Monitor, no antes:** El portal Command solo tiene valor cuando hay datos reales que mostrar — KPIs, alertas de drift, conflictos de maestros. Sin un ciclo completo de pronóstico ejecutado, el portal estaría vacío. Por eso va en el Bloque D junto a Monitor (DEC-026).
- **`command_log` como herramienta de diagnóstico:** Cuando un cliente reporta que su pronóstico "cambió" sin explicación, el primer lugar donde mirar es el `command_log`. Si un operador forzó un reentrenamiento o un rollback, ahí está el registro de quién, cuándo y por qué.
- **El portal no es el producto:** El cliente nunca ve el portal Command. Es una herramienta interna de operación. En Fase 1 puede ser tan simple como un script Python con menú de opciones. En Fase 2 es Streamlit. En Fase 3 es una interfaz FastAPI + React. La lógica es la misma en todas las fases — solo cambia la interfaz.
- **Separación Command / Monitor por responsabilidad:** Monitor calcula y alerta. Command actúa. Mezclarlos crearía un harness con dos responsabilidades distintas y acoplaría la observabilidad con la operación. Si el portal Command falla, Monitor sigue funcionando — las métricas no se pierden aunque el operador no pueda actuar desde la interfaz.
