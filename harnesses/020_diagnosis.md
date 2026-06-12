# Harness 020 — Diagnosis

**Tipo:** Pipeline  
**Bloque de construcción:** A (posición 3 de 11)  
**Hito al que pertenece:** Hito A — Primer piloto ejecutable  
**Disparador:** Evento `intake_complete` emitido por 015 Intake — corre en PARALELO con 025 Refinery

---

## Propósito

Calcular el Índice de Salud de Datos (ISD) del cliente a partir de la copia Bronze — los datos tal como el cliente los entregó, sin ninguna corrección. El ISD es la medida objetiva de la calidad de los datos del cliente. Determina el nivel de garantía del pronóstico (DEC-009), el cargo adicional por complejidad (DEC-016), y la hoja de ruta de mejora que Triple S le presenta al cliente mensualmente.

Este harness **nunca modifica datos**. Solo mide, califica y reporta.

---

## Entradas

| Entrada | Descripción | Fuente |
|---------|-------------|--------|
| Copia Bronze — Esquema 1 | Historial de pedidos sin modificar | 015 Intake / `tenants/{id}/bronze/` |
| Copia Bronze — Esquema 2 | Producción e inventario sin modificar (si aplica) | 015 Intake / `tenants/{id}/bronze/` |
| `intake_report.json` | Conteos preliminares de errores de tipo, duplicados y campos faltantes detectados en ingesta | 015 Intake |
| `client_profile.json` | Jerarquías declaradas por el cliente, nivel de confianza cold start | 010 Discovery |
| `onboarding_config.json` | Esquemas activos, modo de ingesta, horizonte de pronóstico | 010 Discovery |
| Evento `intake_complete` | Señal de inicio con path al Bronze | 015 Intake |

---

## Procesos

### P1 — Carga del Bronze en memoria de análisis

El harness carga la copia Bronze en DuckDB (archivo del tenant, DEC-021) para ejecutar las consultas de las 6 dimensiones. No se escribe nada en Bronze — es acceso de solo lectura.

### P2 — Dimensión 1: Completitud (peso 25%)

Mide qué fracción de los datos esperados está presente.

**Sub-métricas:**

| Sub-métrica | Descripción | Peso interno |
|-------------|-------------|--------------|
| Campos mínimos con valores nulos | Porcentaje de filas donde `fecha_pedido`, `id_cliente`, `id_producto` o `cantidad_solicitada` son nulos o vacíos | 60% |
| Campos ideales faltantes en el esquema | Porcentaje de los 17 campos ideales que el cliente no entregó en absoluto | 40% |

**Fórmula:**
```
Completitud = 100 × (1 - tasa_de_nulos_en_campos_mínimos × 0.6
                       - fracción_de_campos_ideales_ausentes × 0.4)
```

### P3 — Dimensión 2: Consistencia (peso 20%)

Mide si los mismos datos se representan de la misma forma a lo largo del archivo.

**Sub-métricas:**

| Sub-métrica | Descripción |
|-------------|-------------|
| Inconsistencias de maestro de productos | Mismo `id_producto` con nombres distintos, o mismo nombre con IDs distintos |
| Inconsistencias de maestro de clientes | Mismo `id_cliente` con nombres o sedes distintas, o viceversa |
| Inconsistencias de jerarquía | Un SKU asignado a dos categorías diferentes en distintas filas |
| Inconsistencias de unidad | Misma combinación cliente × producto con unidades distintas en diferentes pedidos |

Las inconsistencias de maestro detectadas aquí son también el insumo principal para que 025 Refinery construya el maestro de datos (DEC-017).

**Fórmula:**
```
Consistencia = 100 × (1 - total_inconsistencias / total_pares_evaluados)
```

### P4 — Dimensión 3: Continuidad (peso 20%)

Mide si la serie temporal de pedidos tiene brechas que el modelo no puede explicar.

**Sub-métricas:**

| Sub-métrica | Descripción |
|-------------|-------------|
| Brechas temporales en combinaciones activas | Períodos sin ningún pedido para una combinación cliente × producto que históricamente sí pedía — más allá de su frecuencia habitual |
| Irregularidad de frecuencia | Desviación de la frecuencia de pedido por combinación cliente × producto respecto a su patrón histórico |

**Nota:** Una combinación sin pedidos durante un período largo puede ser una brecha real (dato faltante) o una cancelación real del cliente XYZ. El harness registra las brechas; la clasificación como dato faltante vs. comportamiento real la hace el operador al revisar el reporte.

**Fórmula:**
```
Continuidad = 100 × (1 - combinaciones_con_brechas / total_combinaciones_activas)
```

### P5 — Dimensión 4: Unicidad (peso 15%)

Mide qué fracción de los registros son duplicados exactos o cuasi-duplicados.

| Sub-métrica | Descripción |
|-------------|-------------|
| Duplicados exactos | Filas idénticas en todos los campos |
| Duplicados de clave | Misma clave `(fecha_pedido, id_cliente, id_producto)` con valores distintos en otros campos |

Los duplicados ya fueron detectados en 015 Intake (P4). Este proceso los cuantifica en porcentaje sobre el total para la dimensión del ISD.

**Fórmula:**
```
Unicidad = 100 × (1 - total_duplicados / total_filas)
```

### P6 — Dimensión 5: Cobertura temporal (peso 10%)

Mide si el historial disponible es suficiente para producir pronósticos confiables.

| Cobertura | Puntuación |
|-----------|------------|
| ≥ 3 años | 100% |
| 2–3 años | 80% |
| 1–2 años | 50% |
| < 1 año | 20% |

La puntuación se calcula por combinación cliente × producto, y el resultado de la dimensión es el promedio ponderado por volumen de pedidos.

### P7 — Dimensión 6: Exactitud (peso 10%)

Mide si los valores numéricos son plausibles en el contexto del negocio.

| Sub-métrica | Descripción |
|-------------|-------------|
| Cantidades negativas | `cantidad_solicitada` < 0 sin ser una devolución explícita |
| Cantidades extremas | Valores que superan 5 desviaciones estándar del promedio histórico de esa combinación cliente × producto — marcados como posibles errores de digitación |
| Fechas futuras | `fecha_pedido` posterior a la fecha de entrega del archivo |
| Fechas incoherentes | `fecha_entrega_real` anterior a `fecha_pedido` (si ambos campos existen) |

**Nota:** Los outliers detectados aquí se registran como posibles errores de exactitud. Los outliers reales (pedidos extraordinarios legítimos) se distinguirán en 035 Predictor durante la clasificación de anomalías (DEC-019). En esta etapa, todo outlier extremo se penaliza conservadoramente.

**Fórmula:**
```
Exactitud = 100 × (1 - total_valores_inexactos / total_valores_evaluados)
```

### P8 — Cálculo del ISD global

```
ISD = Completitud × 0.25
    + Consistencia × 0.20
    + Continuidad × 0.20
    + Unicidad × 0.15
    + Cobertura_temporal × 0.10
    + Exactitud × 0.10
```

Resultado: valor entre 0 y 100.

**Clasificación resultante:**

| ISD | Nivel | Cargo adicional | SLA de precisión |
|-----|-------|-----------------|-----------------|
| ≥ 95% | Óptimo | +0% | MAPE ≤ 15% |
| 70–94% | Moderado | +20% | MAPE ≤ 25% |
| 50–69% | Significativo | +50% | Sin garantía |
| < 50% | Crítico | +80% | Sin garantía |

### P9 — Identificación del problema principal y acción sugerida

El harness identifica la dimensión con el puntaje más bajo (la que más arrastra el ISD) y genera un texto de acción sugerida en lenguaje de negocio.

**Ejemplos de acciones sugeridas:**

| Dimensión débil | Texto sugerido |
|-----------------|----------------|
| Completitud | "El 8% de los pedidos no tiene cantidad registrada. Revisar el proceso de cierre de pedidos en su sistema." |
| Consistencia | "23 productos aparecen con dos códigos diferentes. Estandarizar el catálogo de productos eliminará esta inconsistencia." |
| Continuidad | "Se detectan 4 meses sin pedidos en 12 combinaciones activas. Confirmar si corresponden a cierres de temporada o datos faltantes." |
| Unicidad | "El 3% de los pedidos aparece duplicado. Revisar el proceso de exportación del sistema de ventas." |
| Cobertura temporal | "Solo 14 meses de historial disponible. Con 24 meses o más el pronóstico mejorará significativamente." |
| Exactitud | "47 pedidos tienen cantidades superiores a 5 veces el promedio histórico. Verificar si son correctos o errores de digitación." |

### P10 — Generación del reporte de diagnóstico

El harness produce dos versiones del reporte:

**Versión JSON** (`diagnosis_report.json`) — consumida por otros harnesses:
```json
{
  "tenant_id": "...",
  "timestamp": "...",
  "isd_global": 78.4,
  "nivel": "Moderado",
  "cargo_adicional_pct": 20,
  "sla_mape": "≤ 25%",
  "dimensiones": {
    "completitud":        { "score": 91.2, "peso": 0.25, "aporte": 22.8 },
    "consistencia":       { "score": 64.3, "peso": 0.20, "aporte": 12.9 },
    "continuidad":        { "score": 82.5, "peso": 0.20, "aporte": 16.5 },
    "unicidad":           { "score": 97.0, "peso": 0.15, "aporte": 14.6 },
    "cobertura_temporal": { "score": 80.0, "peso": 0.10, "aporte":  8.0 },
    "exactitud":          { "score": 37.0, "peso": 0.10, "aporte":  3.7 }
  },
  "problema_principal": {
    "dimension": "exactitud",
    "score": 37.0,
    "accion_sugerida": "47 pedidos tienen cantidades superiores a 5 veces el promedio histórico. Verificar si son correctos o errores de digitación."
  },
  "inconsistencias_maestro": {
    "productos": 23,
    "clientes": 4,
    "jerarquia": 7
  }
}
```

**Versión PDF** (`diagnosis_report.pdf`) — entregada al cliente por 040 Publisher:
- Puntaje global en grande con semáforo de color (verde / amarillo / rojo)
- Gráfico de barras con las 6 dimensiones
- Problema principal en lenguaje de negocio
- Acción sugerida concreta
- Comparación con el mes anterior (si existe)

### P11 — Registro del ISD en base de datos

El harness persiste el resultado en la base de datos para alimentar la evolución histórica del ISD y el KPI interno de Triple S (DEC-023, KPI #4: Evolución promedio del ISD por cohorte).

### P12 — Emisión del evento de completitud

```
EVENT: diagnosis_complete
  tenant_id: {id}
  timestamp: {ISO-8601}
  isd_global: 78.4
  nivel: "Moderado"
  cargo_adicional_pct: 20
  diagnosis_report_path: tenants/{id}/bronze/diagnosis_report.json
```

---

## Salidas

### Archivos generados

| Archivo | Descripción | Destino |
|---------|-------------|---------|
| `diagnosis_report.json` | ISD global + 6 dimensiones + problema principal + acción sugerida + inconsistencias de maestro | `tenants/{id}/bronze/` |
| `diagnosis_report.pdf` | Versión visual para el cliente — puntaje, gráfico, causa, acción | `tenants/{id}/bronze/` (publicado al cliente por 040) |

### Registros actualizados en base de datos

| Tabla | Actualización |
|-------|--------------|
| `isd_history` | Nueva fila: tenant_id, timestamp, ISD global, 6 dimensiones, nivel, cargo adicional |
| `clients` | `current_isd`, `current_nivel`, `cargo_adicional_pct` actualizados |
| `master_inconsistencies` | Lista de inconsistencias detectadas — insumo para 025 Refinery |

### Evento emitido

```
diagnosis_complete → consumido por 040 Publisher (para entrega del reporte al cliente)
                  → consumido por 050 Lifecycle (para actualizar el monto de cobro)
```

---

## Condiciones de completitud

El harness 020 se considera **completo** cuando:

1. Las 6 dimensiones fueron calculadas y sus scores están registrados
2. El ISD global fue calculado y el nivel determinado
3. El problema principal y la acción sugerida fueron generados
4. El `diagnosis_report.json` existe en Storage
5. El `diagnosis_report.pdf` existe en Storage
6. El registro en `isd_history` fue creado en base de datos
7. El campo `current_isd` del cliente fue actualizado
8. El evento `diagnosis_complete` fue emitido

**SLA de ejecución:** El ISD debe estar calculado en menos de 4 horas desde la recepción del archivo (DEC-021).

---

## Lo que este harness NO hace

- No modifica ningún dato — ni Bronze, ni Silver, ni Gold
- No limpia inconsistencias — eso es trabajo de 025 Refinery
- No clasifica si un outlier es una anomalía legítima o un error — eso lo hace 035 Predictor
- No genera pronósticos
- No envía el reporte directamente al cliente — lo publica 040 Publisher

---

## Dependencias

| Tipo | Harness / Sistema | Detalle |
|------|-------------------|---------|
| Anterior | 015 Intake | Lee desde Bronze — no puede correr sin Bronze válido |
| Paralelo | 025 Refinery | Ambos leen desde Bronze simultáneamente — ninguno espera al otro |
| Posterior | 040 Publisher | Recibe `diagnosis_report.pdf` para entregarlo al cliente mensualmente |
| Posterior | 050 Lifecycle | Recibe el cargo adicional calculado para ajustar el monto de la próxima factura |

---

## Notas de diseño

- El ISD se calcula siempre desde Bronze, nunca desde Silver ni Gold. Si se calculara desde Silver (datos ya limpios), el puntaje reflejaría el trabajo de Triple S, no la calidad real de los datos del cliente. Esto desnaturalizaría tanto el diagnóstico como el cargo adicional por complejidad (DEC-024).
- Las inconsistencias de maestro detectadas en P3 (Consistencia) se exportan a la tabla `master_inconsistencies`. 025 Refinery las consume para tomar decisiones de unificación al construir el maestro. Es el único punto de comunicación de datos entre 020 y 025.
- El ISD se recalcula en cada entrega de datos (en Modo Incremental: potencialmente semanal). La evolución del puntaje a lo largo del tiempo es uno de los KPIs internos clave de Triple S (KPI #4).
- La versión PDF del reporte sigue el mismo patrón de presentación definido en DEC-022: número global + causa principal + acción sugerida. El cliente no necesita entender las 6 dimensiones — necesita saber qué hacer.
