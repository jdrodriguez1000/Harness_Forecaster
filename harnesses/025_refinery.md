# Harness 025 — Refinery

**Tipo:** Pipeline  
**Bloque de construcción:** B (posición 5 de 11)  
**Hito al que pertenece:** Hito B — Ciclo de valor completo  
**Disparador:** Evento `intake_complete` emitido por 015 Intake — corre en PARALELO con 020 Diagnosis

---

## Propósito

Transformar los datos Bronze (crudos e intocables) en datos Gold (listos para que los modelos de pronóstico operen sobre ellos). El camino es Bronze → Silver → Gold. Silver es la versión limpia y normalizada. Gold es la versión estructurada como series de tiempo por combinación cliente × producto, con los maestros de datos aplicados. Sin Gold, 030 Trainer no tiene nada con qué entrenar.

Este harness es el único autorizado a escribir en las capas Silver y Gold.

---

## Entradas

| Entrada | Descripción | Fuente |
|---------|-------------|--------|
| Copia Bronze — Esquema 1 | Historial de pedidos sin modificar | 015 Intake / `tenants/{id}/bronze/` |
| Copia Bronze — Esquema 2 | Producción e inventario (si aplica) | 015 Intake / `tenants/{id}/bronze/` |
| Tabla `master_inconsistencies` | Inconsistencias de ID detectadas por 020 Diagnosis (productos, clientes, jerarquías) | 020 Diagnosis (punto de sincronización — ver nota de diseño) |
| `client_profile.json` | Jerarquías disponibles, nivel de cold start | 010 Discovery |
| `onboarding_config.json` | Modo de ingesta, horizonte de pronóstico, esquemas activos | 010 Discovery |
| Evento `intake_complete` | Señal de inicio | 015 Intake |

---

## Procesos

### Fase I — Bronze → Silver (limpieza y normalización)

#### P1 — Carga del Bronze en DuckDB

El harness carga la copia Bronze en el archivo DuckDB del tenant (acceso de solo lectura). Toda la transformación produce registros nuevos en tablas Silver — Bronze nunca se toca.

#### P2 — Normalización de fechas

Todas las columnas de tipo fecha se convierten a ISO-8601 (`YYYY-MM-DD`).

| Situación | Acción |
|-----------|--------|
| Fecha en formato reconocible (DD/MM/YYYY, MM-DD-YYYY, etc.) | Se convierte a ISO-8601 |
| Fecha no parseable | Se conserva el valor original en `fecha_raw`; la celda normalizada se marca como nula con flag `_date_parse_error = true` |
| Fecha futura (posterior a la fecha de entrega del archivo) | Se conserva y se marca con flag `_future_date = true` |

#### P3 — Normalización de identificadores de texto

Para los campos `id_cliente`, `id_producto` y cualquier campo de nombre o categoría:

| Transformación | Descripción |
|---------------|-------------|
| Trim | Eliminación de espacios al inicio y al final |
| Case unificado | Todo a mayúsculas (IDs) o title case (nombres) |
| Caracteres especiales | Eliminación de caracteres no alfanuméricos en campos de ID |
| Encoding | Normalización a UTF-8 |

Estas transformaciones son deterministas — para el mismo input siempre producen el mismo output, lo que garantiza que los maestros sean estables entre ejecuciones.

#### P4 — Manejo de nulos en campos mínimos

Los registros con nulos en campos mínimos **no se eliminan**. Se conservan en Silver con flags:

| Campo nulo | Flag agregado |
|------------|---------------|
| `fecha_pedido` | `_fecha_nula = true` |
| `id_cliente` | `_cliente_nulo = true` |
| `id_producto` | `_producto_nulo = true` |
| `cantidad_solicitada` | `_cantidad_nula = true` |

Estos registros no participan en la construcción de series de tiempo Gold, pero quedan en Silver como evidencia de lo que se recibió.

#### P5 — Deduplicación

| Modo | Comportamiento |
|------|---------------|
| **Batch** | Los duplicados exactos (todas las columnas iguales) se colapsan en un solo registro con flag `_duplicado = true` y `_n_duplicados = N`. Los duplicados de clave `(fecha, cliente, producto)` con valores distintos se conservan todos, marcados con `_clave_duplicada = true` — no se decide cuál es el correcto. |
| **Incremental** | Solo los registros cuya clave `(fecha, cliente, producto)` no existe ya en Silver se agregan. Los que ya existen se descartan silenciosamente (ya fueron procesados en una entrega anterior). |

#### P6 — Construcción de los maestros de datos

Con el Bronze normalizado (post P2–P4) y las inconsistencias detectadas por 020 Diagnosis (`master_inconsistencies`), el harness construye los tres maestros. Este es el punto de sincronización con 020: si `master_inconsistencies` aún no está disponible (020 no terminó), 025 espera hasta 30 minutos antes de calcular sus propias inconsistencias.

**Maestro de Productos:**

| Campo | Descripción |
|-------|-------------|
| `product_id` | ID canónico (el más frecuente entre variantes detectadas) |
| `product_aliases` | Lista de IDs alternativos encontrados en Bronze |
| `product_name` | Nombre canónico |
| `category` | Categoría (si está disponible) |
| `subcategory` | Subcategoría (si está disponible) |
| `first_seen` | Fecha del primer pedido histórico |
| `last_seen` | Fecha del último pedido histórico |

**Maestro de Clientes XYZ:**

| Campo | Descripción |
|-------|-------------|
| `client_id` | ID canónico |
| `client_aliases` | IDs alternativos encontrados |
| `client_name` | Nombre canónico |
| `sede` | Sede (si está disponible) |
| `region` / `ciudad` | Jerarquía geográfica disponible |
| `first_order` | Fecha del primer pedido histórico |

**Maestro Geográfico:**
Derivado de la jerarquía geográfica declarada en `client_profile.json` y los valores observados en los datos. Opera con los niveles disponibles sin requerir jerarquía completa (DEC-018).

**Criterio de resolución de inconsistencias:**
Cuando un mismo elemento tiene dos IDs o dos nombres, se elige como canónico el que aparece con mayor frecuencia en los datos históricos. Las alternativas quedan en `aliases`. Si hay empate, el operador de Triple S decide manualmente.

#### P7 — Aplicación de maestros al Silver

Con los maestros construidos, el harness reemplaza en Silver todos los IDs y nombres alternativos por sus versiones canónicas. Cada registro reemplazado lleva el flag `_master_applied = true` para indicar que fue normalizado.

#### P8 — Escritura de la capa Silver

Silver se escribe en el DuckDB del tenant y en Supabase Storage:

```
tenants/{tenant_id}/silver/
├── orders_silver.parquet       ← Esquema 1 limpio y normalizado
├── inventory_silver.parquet    ← Esquema 2 limpio (si aplica)
├── master_products.parquet     ← Maestro de productos
├── master_clients.parquet      ← Maestro de clientes XYZ
└── master_geography.parquet    ← Maestro geográfico
```

---

### Fase II — Silver → Gold (estructuración para modelos)

#### P9 — Construcción de series de tiempo por combinación cliente × producto

Esta es la transformación más importante del harness. El Gold no es una tabla de pedidos — es una tabla de tiempo donde cada combinación cliente × producto tiene una fila por período.

**Granularidad temporal:**
Determinada por el horizonte de pronóstico configurado en `onboarding_config.json`:

| Horizonte de pronóstico | Granularidad Gold |
|------------------------|-------------------|
| Días | Diaria |
| Semanas | Semanal (lunes a domingo) |
| Meses | Mensual |
| Múltiples meses | Mensual (agregado) |

**Agregación:** Para cada período, la `cantidad_solicitada` se suma por combinación cliente × producto.

**Períodos sin pedidos:**
Si una combinación activa no tiene pedidos en un período, se crea la fila con `cantidad = 0` y flag `_periodo_sin_pedido = true`. Esto es crítico para que el modelo de series de tiempo vea el patrón real de demanda, incluyendo los períodos de silencio.

**Combinaciones activas vs. inactivas:**
Una combinación se considera activa si tuvo al menos un pedido en los últimos 6 meses del historial disponible. Las combinaciones con más de 6 meses sin pedidos se marcan como `_combinacion_inactiva = true` y se excluyen del Gold operativo (pero se conservan en Silver).

#### P10 — Enriquecimiento con contexto de cold start

Para cada combinación cliente × producto, el harness calcula:

| Métrica | Descripción |
|---------|-------------|
| `meses_de_historial` | Cantidad de meses con al menos un pedido |
| `frecuencia_promedio_dias` | Promedio de días entre pedidos consecutivos |
| `nivel_confianza` | Alta / Estándar / Reducida / Experimental (según DEC-013) |
| `modo_cold_start` | `none` / `analogia_categoria` / `analogia_cliente` / `acumulacion` |

Estos metadatos viajan con cada combinación en Gold y los usa 030 Trainer para seleccionar el modelo apropiado.

#### P11 — Cruce con Esquema 2 (si aplica)

Si el cliente tiene Esquema 2 activo (producción e inventario), el harness cruza los datos de pedidos Gold con los datos de inventario por `(fecha, id_producto)`:

Columnas adicionales añadidas a Gold por producto:
- `stock_disponible` al final del período
- `cantidad_producida` en el período
- `stock_minimo`
- `agotado` = `true` si `stock_disponible < stock_minimo`
- `desperdicio_estimado` = `max(0, cantidad_producida - cantidad_solicitada - variacion_stock)`

#### P12 — Escritura de la capa Gold

```
tenants/{tenant_id}/gold/
├── timeseries_gold.parquet     ← Series de tiempo por combinación cliente × producto
├── combinations_metadata.parquet ← Metadatos de cada combinación: historial, confianza, cold start
└── inventory_gold.parquet      ← Cruce con Esquema 2 (si aplica)
```

#### P13 — Generación del reporte de refinería

```json
{
  "tenant_id": "...",
  "timestamp": "...",
  "silver": {
    "total_registros_bronze": 45230,
    "registros_silver": 44891,
    "registros_con_flags": 872,
    "duplicados_colapsados": 34,
    "fechas_normalizadas": 45230,
    "ids_normalizados": 45230,
    "master_applied_count": 1240
  },
  "masters": {
    "productos_canonicos": 312,
    "aliases_resueltos": 23,
    "clientes_canonicos": 87,
    "aliases_resueltos_clientes": 4
  },
  "gold": {
    "combinaciones_activas": 1847,
    "combinaciones_inactivas": 203,
    "periodos_por_combinacion_promedio": 28.4,
    "periodos_sin_pedido_inferidos": 4521,
    "granularidad": "mensual",
    "esquema_2_activo": false
  }
}
```

#### P14 — Emisión del evento de completitud

```
EVENT: refinery_complete
  tenant_id: {id}
  timestamp: {ISO-8601}
  gold_path: tenants/{id}/gold/
  combinaciones_activas: 1847
  refinery_report_path: tenants/{id}/silver/refinery_report.json
  next_harness: 030_trainer
```

---

## Salidas

### Archivos generados

| Archivo | Descripción | Destino |
|---------|-------------|---------|
| `orders_silver.parquet` | Historial de pedidos limpio y normalizado | `tenants/{id}/silver/` |
| `inventory_silver.parquet` | Producción e inventario limpio (si aplica) | `tenants/{id}/silver/` |
| `master_products.parquet` | Maestro canónico de productos | `tenants/{id}/silver/` |
| `master_clients.parquet` | Maestro canónico de clientes XYZ | `tenants/{id}/silver/` |
| `master_geography.parquet` | Maestro geográfico | `tenants/{id}/silver/` |
| `timeseries_gold.parquet` | Series de tiempo por combinación cliente × producto | `tenants/{id}/gold/` |
| `combinations_metadata.parquet` | Metadatos de confianza y cold start por combinación | `tenants/{id}/gold/` |
| `inventory_gold.parquet` | Cruce con Esquema 2 (si aplica) | `tenants/{id}/gold/` |
| `refinery_report.json` | Reporte de transformación: conteos, aliases resueltos, combinaciones | `tenants/{id}/silver/` |

### Registros actualizados en base de datos

| Tabla | Actualización |
|-------|--------------|
| `clients` | `last_refinery_at`, `combinaciones_activas`, `gold_ready = true` |
| `masters` | Upsert completo de los tres maestros |
| `refinery_log` | Nueva fila por ejecución: timestamp, conteos, estado |

### Evento emitido

```
refinery_complete → dispara 030 Trainer
```

---

## Condiciones de completitud

El harness 025 se considera **completo** cuando:

1. Las capas Silver y Gold existen en Storage con todos sus archivos
2. Los tres maestros de datos están construidos y persisitidos
3. Las series de tiempo Gold cubren todas las combinaciones activas con granularidad correcta
4. Los metadatos de cold start por combinación están calculados
5. El `refinery_report.json` existe en Storage
6. El registro en `refinery_log` fue creado
7. El campo `gold_ready = true` está actualizado en la tabla `clients`
8. El evento `refinery_complete` fue emitido

---

## Lo que este harness NO hace

- No modifica Bronze bajo ninguna circunstancia
- No calcula el ISD — ese es el trabajo de 020 Diagnosis
- No hace feature engineering — eso es interno a 030 Trainer (DEC-024)
- No entrena modelos ni genera pronósticos
- No toma decisiones sobre qué datos son "correctos" cuando hay ambigüedad — las registra y las flags

---

## Dependencias

| Tipo | Harness / Sistema | Detalle |
|------|-------------------|---------|
| Anterior | 015 Intake | Lee desde Bronze — no puede correr sin Bronze válido |
| Sincronización | 020 Diagnosis | Espera hasta 30 min por `master_inconsistencies` antes de calcularlas de forma autónoma |
| Siguiente | 030 Trainer | Lee desde Gold — no puede entrenar sin Gold válido |

---

## Notas de diseño

- **Paralelismo con 020:** Ambos harnesses arrancan con `intake_complete`. 025 puede iniciar P1–P5 inmediatamente. Solo P6 (construcción de maestros) tiene una espera suave de hasta 30 minutos por `master_inconsistencies` de 020. En la práctica, 020 termina primero porque solo analiza; 025 hace transformaciones más pesadas.
- **Parquet como formato de Gold:** Parquet es columnar, comprimido y optimizado para consultas analíticas con DuckDB. Cada lectura de 030 Trainer sobre Gold será significativamente más rápida que sobre CSV o Excel.
- **Períodos sin pedido inferidos (`_periodo_sin_pedido = true`):** Son filas que no existían en Bronze pero que el modelo necesita ver para entender que la demanda fue cero en ese período, no que el dato está faltante. Sin ellas, el modelo interpretaría gaps como datos ausentes y produciría estimaciones incorrectas.
- **Modo Incremental:** En cada entrega nueva, 025 recorre el mismo proceso completo sobre el Bronze acumulado actualizado. Silver y Gold se reconstruyen desde cero cada vez (no se hace merge incremental en Silver/Gold). Esto garantiza consistencia y evita estados intermedios corruptos.
- **Los maestros son propiedad de Triple S:** El cliente puede consultarlos en el dashboard (solo lectura) y solicitar correcciones al operador, pero nunca los edita directamente (DEC-017).
