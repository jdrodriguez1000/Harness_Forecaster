# Harness 040 — Publisher

**Tipo:** Pipeline  
**Bloque de construcción:** B (posición 8 de 11)  
**Hito al que pertenece:** Hito B — Ciclo de valor completo  
**Disparadores:**
- Evento `predictor_complete` — pronóstico del mes listo para publicar
- Evento `diagnosis_complete` — reporte de salud de datos listo (puede correr antes que el pronóstico en el mes 1 de onboarding)

---

## Propósito

Tomar los artefactos producidos por 035 Predictor y 020 Diagnosis y entregarlos al cliente a través de los tres canales definidos: dashboard de solo lectura, correo automático y archivo exportable. Es el único punto de contacto del sistema con el cliente. Todo lo que el cliente ve y consume pasa por aquí.

El Publisher no genera datos — los presenta. Su responsabilidad es la entrega correcta, en tiempo, al destinatario correcto, en el formato correcto.

---

## Entradas

| Entrada | Descripción | Fuente |
|---------|-------------|--------|
| `forecast_skus.parquet` | Pronósticos nivel SKU × Sede | 035 Predictor |
| `forecast_clients.parquet` | Pronósticos nivel SKU × Cliente consolidado | 035 Predictor |
| `forecast_categories.parquet` | Pronósticos nivel Categoría × Sede | 035 Predictor |
| `forecast_summary.parquet` | Pronósticos nivel máximo de agregación | 035 Predictor |
| `anomalies.parquet` | Anomalías detectadas con clasificación y estado | 035 Predictor |
| `explainability.parquet` | Metadatos de explicabilidad por combinación | 035 Predictor |
| `diagnosis_report.json` | ISD global + 6 dimensiones + acción sugerida | 020 Diagnosis |
| `diagnosis_report.pdf` | Versión visual del reporte de salud de datos | 020 Diagnosis |
| `client_profile.json` | Contactos registrados, roles de usuario, jerarquías | 010 Discovery |
| `onboarding_config.json` | Esquemas activos, horizonte, granularidad | 010 Discovery |
| Evento `predictor_complete` o `diagnosis_complete` | Señal de inicio | 035 Predictor / 020 Diagnosis |

---

## Procesos

### P1 — Determinación del tipo de publicación

El harness identifica qué está publicando en este ciclo:

| Tipo | Condición | Canales activados |
|------|-----------|-------------------|
| **Publicación completa** | Llega `predictor_complete` (pronóstico + diagnóstico disponibles) | Dashboard + correo + exportable |
| **Publicación parcial — solo ISD** | Llega `diagnosis_complete` sin `predictor_complete` (mes 1 de onboarding: aún no hay modelo entrenado) | Dashboard (sección ISD únicamente) + correo simplificado |

En el mes 1 de onboarding el cliente recibe el diagnóstico de salud de datos pero no el pronóstico. A partir del mes 2 o 3 (cuando 030 Trainer ya tiene modelos listos) la publicación es completa.

### P2 — Preparación del dashboard

El harness materializa las vistas del dashboard en la base de datos PostgreSQL. Cada rol de usuario tiene una vista diferente (DEC-022):

**Vista: Planificador de demanda** (uso diario — máximo detalle)
- Pronóstico SKU × Sede, período a período, con intervalos de confianza
- Semáforo de nivel de confianza por combinación (Alta → verde / Estándar → azul / Reducida → amarillo / Experimental → gris)
- Tendencia reciente (3 períodos: flecha arriba / abajo / estable)
- Evento activo si existe (etiqueta sobre el período)
- Anomalías pendientes de confirmación con botones "Es correcto" / "Es un error"
- Comparación contra pronóstico del mes anterior

**Vista: Jefe de compras** (uso semanal — nivel categoría)
- Pronóstico por categoría × Sede
- Top 10 productos por volumen pronosticado
- Anomalías sin clasificar pendientes de acción
- ISD global con tendencia histórica (gráfico de línea — últimos 6 meses)

**Vista: Gerente de producción** (uso mensual — volúmenes de producción)
- Pronóstico agregado por categoría × Cliente consolidado
- Si Esquema 2 activo: proyección de agotados (`stock_disponible < demanda_pronosticada`) y desperdicios estimados
- Comparación demanda pronosticada vs. capacidad de producción declarada (si el cliente la informó)

**Vista: Gerente de Supply Chain** (uso mensual — visión integrada)
- Pronóstico por cliente XYZ consolidado, todos los niveles
- KPIs de servicio: cobertura de inventario proyectada, riesgo de agotado por SKU
- Reporte ISD completo con 6 dimensiones y evolución mensual

**Vista: Directivo** (uso ocasional — resumen ejecutivo)
- Número único: demanda total pronosticada del mes (unidades y monto estimado si hay precio)
- Semáforo verde / amarillo / rojo según cumplimiento del SLA de precisión (MAPE real del mes anterior)
- ISD global con estado: Óptimo / Moderado / Significativo / Crítico
- Una alerta máxima: la anomalía o el problema de datos más relevante del período

**Latencia del dashboard:** < 3 segundos por carga de vista (DEC-021). Las vistas se materializan aquí y se cachean — el dashboard lee desde vistas pre-computadas, no ejecuta queries ad-hoc sobre los Parquet.

### P3 — Actualización de la sección de ISD en el dashboard

Independientemente del tipo de publicación (completa o parcial), el harness actualiza la sección "Salud de Datos" del dashboard:

- Puntaje global del ISD en grande, con semáforo de color
- Gráfico de barras con las 6 dimensiones y su puntaje individual
- Problema principal + acción sugerida en lenguaje de negocio (sin tecnicismos)
- Evolución del ISD en los últimos 6 ciclos (gráfico de línea)
- Nivel de cargo adicional vigente y su impacto en la factura del mes

### P4 — Publicación del maestro de datos en el dashboard

El harness expone el maestro de datos (productos, clientes XYZ, geográfico) en el dashboard en modo solo lectura. El cliente puede consultarlo, buscar elementos y solicitar correcciones al operador de Triple S mediante un formulario de solicitud. No puede editarlo directamente (DEC-017).

### P5 — Generación del correo automático

Al completar la actualización del dashboard, el harness genera y envía el correo automático de notificación a través de SendGrid.

**Destinatarios:** Todos los contactos registrados del cliente con rol activo.

**Asunto:** `[Harness Forecaster] Tu pronóstico de {mes} está listo — {razón_social}`

**Contenido del correo — Publicación completa:**

```
Hola {nombre_contacto},

Tu pronóstico de demanda para {mes} ya está disponible en el dashboard.

PRONÓSTICO DEL MES
──────────────────
Demanda total proyectada: {X} unidades
Nivel de confianza predominante: {Alta / Estándar / Reducida}
{Si hay anomalías sin clasificar}: ⚠ {N} pedidos atípicos requieren tu confirmación

SALUD DE DATOS
──────────────
Índice de Salud de Datos (ISD): {X}% — {Óptimo / Moderado / Significativo / Crítico}
{Si ISD < 95%}: Acción sugerida: {texto de acción del diagnosis_report}

Ver pronóstico completo → [Ir al dashboard]

Triple S — Harness Forecaster
```

**Contenido del correo — Publicación parcial (solo ISD, mes 1):**

```
Hola {nombre_contacto},

Completamos el diagnóstico inicial de tus datos. Aquí están los resultados.

SALUD DE DATOS
──────────────
Índice de Salud de Datos (ISD): {X}% — {nivel}
Dimensión con más oportunidad de mejora: {dimensión} ({score}%)
Acción sugerida: {texto}

Tu primer pronóstico estará listo en las próximas semanas, mientras 
construimos los modelos con tus datos históricos.

Ver diagnóstico completo → [Ir al dashboard]

Triple S — Harness Forecaster
```

**SLA de correo:** enviado en menos de 1 hora desde que el dashboard está actualizado (DEC-021).

### P6 — Generación del exportable

El harness genera el archivo Excel/CSV de descarga disponible desde el dashboard. Se genera en este momento (no on-demand) para garantizar que la descarga sea instantánea cuando el cliente la solicite.

**Contenido del exportable (Excel con múltiples hojas):**

| Hoja | Contenido |
|------|-----------|
| `Pronóstico_SKU` | Pronósticos por SKU × Sede con intervalos de confianza |
| `Pronóstico_Categoría` | Pronósticos agregados por categoría |
| `Pronóstico_Cliente` | Pronósticos por cliente XYZ consolidado |
| `Anomalías` | Lista de anomalías detectadas con clasificación |
| `Salud_de_Datos` | ISD global + 6 dimensiones + acción sugerida |
| `Maestro_Productos` | Catálogo de productos canónico |
| `Maestro_Clientes` | Catálogo de clientes XYZ canónico |

**Lo que el exportable NUNCA incluye:** datos Bronze, Silver ni Gold. Solo datos de pronóstico y diagnóstico (DEC-010).

El exportable está disponible en el dashboard con botones "Descargar Excel" y "Descargar CSV". La versión CSV exporta solo la hoja `Pronóstico_SKU` (la más usada por sistemas externos del cliente).

```
tenants/{tenant_id}/exports/
└── {YYYY_MM}/
    ├── forecast_export_{YYYY_MM}.xlsx
    └── forecast_export_{YYYY_MM}.csv
```

### P7 — Registro de entrega y verificación de SLA

El harness registra el timestamp exacto de cada acción de entrega y verifica el cumplimiento del SLA de entrega (DEC-009: primeros 5 días hábiles del mes):

```json
{
  "tenant_id": "...",
  "periodo": "2026-07",
  "dashboard_updated_at": "2026-07-01T09:14:32Z",
  "email_sent_at": "2026-07-01T09:47:18Z",
  "export_generated_at": "2026-07-01T09:14:55Z",
  "dia_habil": 1,
  "sla_entrega_cumplido": true,
  "tipo_publicacion": "completa",
  "destinatarios_correo": 3,
  "correo_enviado": true
}
```

Si la publicación ocurre después del día 5 hábil, el harness registra el incumplimiento de SLA en la tabla `sla_violations`. Esto alimenta los KPIs internos de Triple S (DEC-023, KPI #2: Tiempo promedio de primer pronóstico).

### P8 — Emisión del evento de completitud

```
EVENT: publisher_complete
  tenant_id: {id}
  timestamp: {ISO-8601}
  periodo: "2026-07"
  tipo_publicacion: "completa"
  dashboard_updated: true
  email_sent: true
  export_ready: true
  sla_cumplido: true
  next: [045_monitor, 050_lifecycle]
```

---

## Salidas

### Archivos generados

| Archivo | Descripción | Destino |
|---------|-------------|---------|
| `forecast_export_{YYYY_MM}.xlsx` | Exportable Excel multicapa para descarga desde dashboard | `tenants/{id}/exports/{YYYY_MM}/` |
| `forecast_export_{YYYY_MM}.csv` | Exportable CSV (solo SKUs) para descarga desde dashboard | `tenants/{id}/exports/{YYYY_MM}/` |
| `publisher_report.json` | Reporte de entrega: timestamps, SLA, destinatarios, tipo de publicación | `tenants/{id}/forecasts/{YYYY_MM}/` |

### Registros actualizados en base de datos

| Tabla | Actualización |
|-------|--------------|
| `dashboard_views` | Materialización de las 5 vistas por rol |
| `publication_log` | Nueva fila: tenant_id, período, tipo, timestamps de cada canal, SLA status |
| `sla_violations` | Nueva fila si se incumplió el SLA de entrega (solo en caso de incumplimiento) |
| `clients` | `last_published_at`, `current_forecast_period` |
| `email_log` | Registro de cada correo enviado: destinatario, timestamp, estado SendGrid |

### Evento emitido

```
publisher_complete → consumido por 045 Monitor (para registrar el ciclo de entrega)
                  → consumido por 050 Lifecycle (para actualizar el estado de entrega en el perfil del cliente)
```

---

## Condiciones de completitud

El harness 040 se considera **completo** cuando:

1. Las 5 vistas del dashboard están materializadas y disponibles
2. La sección de ISD está actualizada en el dashboard
3. El correo fue enviado a todos los destinatarios registrados (confirmación de SendGrid)
4. El exportable Excel y CSV existen en Storage
5. El `publisher_report.json` está generado con timestamps de cada canal
6. El registro en `publication_log` fue creado
7. El SLA fue evaluado y registrado (cumplido o incumplido)
8. El evento `publisher_complete` fue emitido

**SLA de entrega:** El dashboard debe estar actualizado dentro de los primeros 5 días hábiles del mes (DEC-009).

---

## Lo que este harness NO hace

- No genera pronósticos — eso es 035 Predictor
- No calcula el ISD — eso es 020 Diagnosis
- No calcula el MAPE real del período anterior — eso es 045 Monitor
- No gestiona pagos ni acceso de usuarios — eso es 050 Lifecycle
- No permite que el cliente edite o configure nada — el dashboard es de solo lectura (DEC-001)

---

## Dependencias

| Tipo | Harness / Sistema | Detalle |
|------|-------------------|---------|
| Anterior | 035 Predictor | Requiere artefactos de pronóstico completos |
| Anterior | 020 Diagnosis | Requiere `diagnosis_report.json` y `.pdf` |
| Posterior | 045 Monitor | Recibe el evento de publicación para auditar el ciclo |
| Posterior | 050 Lifecycle | Actualiza el estado de entrega en el registro del cliente |
| Externo | SendGrid | API de envío de correos transaccionales |
| Externo | Supabase Auth | Controla el acceso de los usuarios al dashboard por rol |

---

## Notas de diseño

- **Vistas materializadas, no queries en vivo:** El dashboard nunca ejecuta queries directas sobre los Parquet de pronóstico. El Publisher pre-computa todo y lo escribe en tablas PostgreSQL optimizadas. Esto garantiza la latencia < 3s comprometida (DEC-021) sin importar cuántas combinaciones tenga el cliente.
- **La anomalía sin clasificar no bloquea la publicación:** Si hay anomalías pendientes de confirmación del cliente, se publican en el dashboard con su estado `pendiente`. El cliente responde desde el dashboard cuando quiera — no se le pide nada antes de ver el pronóstico.
- **Correo como garantía de entrega de valor:** El modelo de servicio asume que el cliente no entra al dashboard todos los días. El correo garantiza que el cliente recibe el pronóstico aunque nunca abra el sistema — el resumen en el cuerpo del correo es suficiente para que el planificador de demanda tome una decisión básica.
- **Exportable pre-generado:** Se genera en el momento de la publicación, no cuando el cliente hace clic. Esto garantiza que la descarga sea instantánea y que el exportable refleje exactamente los datos del momento de publicación — no una snapshot posterior que podría diferir si hubo correcciones.
- **Publicación parcial en mes 1:** Durante el onboarding, el cliente recibe el diagnóstico de salud de datos aunque el pronóstico no esté listo. Esto cumple el compromiso del mes 1 gratuito (DEC-004): el cliente obtiene valor inmediato (diagnóstico) sin esperar el ciclo completo de ML.
