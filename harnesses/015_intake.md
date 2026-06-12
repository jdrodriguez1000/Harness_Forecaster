# Harness 015 — Intake

**Tipo:** Pipeline  
**Bloque de construcción:** A (posición 2 de 11)  
**Hito al que pertenece:** Hito A — Primer piloto ejecutable  
**Disparador:** El cliente entrega su(s) archivo(s) de datos al sistema

---

## Propósito

Recibir los archivos de datos del cliente, validar que tienen la estructura mínima requerida, y crear la copia Bronze — inmutable y exacta — de los datos originales. A partir de este momento el sistema tiene datos con qué trabajar. Lo que entra aquí es lo más cercano posible a la realidad del cliente; nada se corrige, nada se interpreta.

---

## Entradas

### Archivos del cliente

| Entrada | Descripción | Obligatorio |
|---------|-------------|-------------|
| Archivo de historial de pedidos | CSV o Excel con los datos históricos de pedidos (Esquema 1, DEC-014) | Sí |
| Archivo de producción e inventario | CSV o Excel con datos de producción e inventario de ABC (Esquema 2, DEC-014) | Solo si el cliente tiene Esquema 2 activo |

**Campos mínimos requeridos — Esquema 1 (rechazo si faltan):**
- `fecha_pedido` — fecha en que XYZ realizó el pedido
- `id_cliente` — identificador del cliente XYZ
- `id_producto` — identificador del producto / SKU
- `cantidad_solicitada` — unidades pedidas

**Campos ideales — Esquema 1 (no rechazan pero afectan el ISD):**
Hasta 17 campos documentados en DEC-014 — precio unitario, cantidad entregada, fecha de entrega prometida, fecha de entrega real, motivo de cancelación, región, sede, categoría, subcategoría, y otros.

**Campos mínimos — Esquema 2 (rechazo si faltan cuando Esquema 2 está activo):**
- `fecha`
- `id_producto`
- `cantidad_producida`
- `stock_disponible`
- `costo_unitario`
- `stock_minimo`

### Entradas del sistema (generadas por 010 Discovery)

| Entrada | Descripción | Fuente |
|---------|-------------|--------|
| `client_profile.json` | Perfil del cliente: tenant_id, categoría, jerarquías declaradas | 010 Discovery |
| `onboarding_config.json` | Modo de ingesta (Batch / Incremental), frecuencia, esquemas activos | 010 Discovery |
| Evento `onboarding_discovery_complete` | Señal de que el sistema está listo para recibir datos de este cliente | 010 Discovery |

---

## Procesos

### P1 — Recepción del archivo

El cliente sube su(s) archivo(s) a través del canal definido (en Fase 1: entrega directa al operador; en Fase 3: carga a la carpeta del tenant en Supabase Storage). El sistema detecta automáticamente el formato (CSV o Excel) y el encoding.

- Si el archivo no es CSV ni Excel → rechazo inmediato con mensaje al operador
- Si el archivo está vacío o corrupto → rechazo inmediato con mensaje al operador

### P2 — Validación de estructura

El harness verifica que el archivo tenga los campos mínimos obligatorios según el esquema correspondiente.

**Resultado posible:**

| Resultado | Condición | Acción |
|-----------|-----------|--------|
| Aprobado | Todos los campos mínimos presentes | Continúa al P3 |
| Rechazado | Falta al menos un campo mínimo obligatorio | Se detiene; se notifica al operador con lista de campos faltantes |

Los campos ideales faltantes no detienen el proceso — se registran como déficit para el cálculo del ISD en 020 Diagnosis.

### P3 — Validación de tipos de dato

Para cada campo mínimo se verifica que el tipo de dato sea coherente con lo esperado:

| Campo | Tipo esperado | Tolerancia |
|-------|---------------|------------|
| `fecha_pedido` | Fecha parseable (múltiples formatos aceptados) | Se registra el formato detectado; fechas no parseables se cuentan como errores |
| `id_cliente` | Texto no vacío | Valores nulos o vacíos se cuentan como errores |
| `id_producto` | Texto no vacío | Valores nulos o vacíos se cuentan como errores |
| `cantidad_solicitada` | Numérico ≥ 0 | Negativos y no numéricos se cuentan como errores |

La validación de tipos no detiene el proceso. Los errores encontrados se registran en el `intake_report.json` y alimentan el ISD en 020 Diagnosis.

### P4 — Detección de duplicados

El harness identifica filas duplicadas usando la clave compuesta `(fecha_pedido, id_cliente, id_producto)`.

**Comportamiento según modo de ingesta:**

| Modo | Comportamiento |
|------|---------------|
| **Batch** | Los duplicados internos del archivo se registran como anomalías en el `intake_report.json`. No se eliminan — se copian tal cual a Bronze. 020 Diagnosis los contabilizará en la dimensión Unicidad del ISD. |
| **Incremental** | Además de duplicados internos, se compara contra el Bronze acumulado. Los registros ya existentes (misma clave) se marcan como duplicados y se excluyen de la actualización. Solo los registros nuevos se agregan a Bronze. El `intake_report.json` indica cuántos fueron nuevos y cuántos fueron duplicados. |

### P5 — Evaluación del rango temporal

El harness calcula:
- Fecha del pedido más antiguo en el archivo
- Fecha del pedido más reciente en el archivo
- Total de días cubiertos
- Comparación con el historial declarado por el cliente en 010 Discovery

Si el rango real difiere significativamente del historial declarado (más de 20% de diferencia), se registra la discrepancia como nota en el `intake_report.json`. No detiene el proceso.

### P6 — Creación de la copia Bronze

Una vez superadas las validaciones de estructura (P2), el harness crea la copia Bronze:

- **En Modo Batch:** se guarda el archivo completo como recibido, sin ninguna modificación
- **En Modo Incremental:** se concatena el archivo nuevo al Bronze acumulado, marcando cada fila con el `timestamp` de la entrega en que fue recibida

La copia Bronze es **inmutable después de su creación**. Ningún harness posterior tiene permiso de escribir en `tenants/{id}/bronze/`. Es la evidencia de lo que el cliente entregó.

**Convención de nombres en Storage:**
```
tenants/{tenant_id}/bronze/
├── orders_batch_20260608.csv          ← Modo Batch (único archivo)
├── orders_incremental_20260608.csv    ← Modo Incremental (primera entrega)
├── orders_incremental_20260615.csv    ← Modo Incremental (segunda entrega)
└── inventory_batch_20260608.csv       ← Esquema 2 (si aplica)
```

### P7 — Generación del reporte de ingesta

El harness produce el `intake_report.json` con un resumen cuantificado de todo lo encontrado:

```json
{
  "tenant_id": "...",
  "timestamp": "...",
  "mode": "batch | incremental",
  "schema_1": {
    "file_received": true,
    "total_rows": 45230,
    "date_range": { "min": "2023-01-01", "max": "2026-05-31" },
    "days_covered": 1246,
    "missing_optional_fields": ["precio_unitario", "fecha_entrega_prometida"],
    "type_errors": { "cantidad_solicitada": 12, "fecha_pedido": 0 },
    "duplicates_internal": 34,
    "duplicates_vs_bronze": 0
  },
  "schema_2": {
    "file_received": false
  },
  "status": "bronze_created",
  "warnings": ["Historial real (3.4 años) difiere del declarado (2 años)"]
}
```

### P8 — Emisión del evento de completitud

Al crear exitosamente la copia Bronze, el harness emite el evento que dispara los dos harnesses siguientes en paralelo:

```
EVENT: intake_complete
  tenant_id: {id}
  timestamp: {ISO-8601}
  bronze_path: tenants/{id}/bronze/
  intake_report_path: tenants/{id}/bronze/intake_report.json
  next_harnesses: [020_diagnosis, 025_refinery]  ← corren en PARALELO
```

---

## Salidas

### Archivos generados

| Archivo | Descripción | Destino |
|---------|-------------|---------|
| Copia Bronze del Esquema 1 | Réplica exacta del archivo de pedidos recibido | `tenants/{id}/bronze/` |
| Copia Bronze del Esquema 2 | Réplica exacta del archivo de producción/inventario (si aplica) | `tenants/{id}/bronze/` |
| `intake_report.json` | Reporte cuantificado: conteo de filas, rango de fechas, errores de tipo, duplicados, campos faltantes, advertencias | `tenants/{id}/bronze/` |

### Registros actualizados en base de datos

| Tabla | Actualización |
|-------|--------------|
| `clients` | `last_intake_at` = timestamp actual |
| `intake_log` | Nueva fila por cada entrega: modo, conteo de filas, path del Bronze, estado |

### Evento emitido

```
intake_complete → dispara 020 Diagnosis y 025 Refinery en PARALELO
```

---

## Condiciones de completitud

El harness 015 se considera **completo** cuando:

1. El archivo pasó la validación de estructura (P2) — o fue rechazado con notificación al operador
2. La validación de tipos fue ejecutada y sus resultados registrados
3. La detección de duplicados fue ejecutada y sus resultados registrados
4. La copia Bronze existe en Storage y es inmutable
5. El `intake_report.json` fue generado y almacenado junto al Bronze
6. El registro en `intake_log` fue creado en base de datos
7. El evento `intake_complete` fue emitido

---

## Comportamiento ante rechazo

Si el archivo falla la validación de estructura (P2), el harness:
1. No crea ninguna copia Bronze
2. Genera un `intake_rejection.json` con la lista de campos mínimos faltantes
3. Notifica al operador de Triple S (no directamente al cliente)
4. El operador contacta al cliente con la guía de corrección
5. El cliente vuelve a entregar el archivo desde P1

El sistema no avanza a 020 ni 025 hasta que exista un Bronze válido.

---

## Lo que este harness NO hace

- No corrige ni transforma datos — eso es exclusivo de 025 Refinery
- No calcula el ISD — ese es el trabajo de 020 Diagnosis
- No modifica los datos originales del cliente bajo ninguna circunstancia
- No notifica directamente al cliente — toda comunicación pasa por el operador (en Fase 1) o por 040 Publisher (en Fase 3)
- No entrena modelos ni genera pronósticos

---

## Dependencias

| Tipo | Harness / Sistema | Detalle |
|------|-------------------|---------|
| Anterior | 010 Discovery | Requiere `client_profile.json` y `onboarding_config.json` para saber qué validar y qué modo de ingesta aplicar |
| Siguiente (paralelo) | 020 Diagnosis | Lee desde Bronze para calcular el ISD — se dispara con `intake_complete` |
| Siguiente (paralelo) | 025 Refinery | Lee desde Bronze para limpiar y transformar — se dispara con `intake_complete` |

---

## Notas de diseño

- El Bronze es la fuente de verdad del estado real de los datos del cliente. 020 Diagnosis lo lee tal cual para medir la salud real — si 025 Refinery lo modificara primero, el diagnóstico estaría midiendo datos ya corregidos y el ISD sería artificialmente mejor de lo real. Por eso 020 y 025 corren en paralelo, ambos leyendo desde Bronze (DEC-024).
- En Modo Incremental cada entrega lleva un timestamp propio. Esto permite auditar qué datos existían en qué momento — útil si un pronóstico necesita ser explicado o auditado en retrospectiva.
- El `intake_report.json` es el primer documento de la cadena de evidencia del ISD. 020 Diagnosis lo tomará como punto de partida para el cálculo detallado de las 6 dimensiones.
