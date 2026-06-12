# Harness 050 — Lifecycle

**Tipo:** Event-driven  
**Bloque de construcción:** C (posición 4 de 11 — se construye antes del Bloque B)  
**Hito al que pertenece:** Hito C — Listo para cobrar  
**Disparadores:** Múltiples — eventos de Stripe, timer diario, eventos internos del sistema

---

## Propósito

Gestionar el ciclo de vida completo del cliente: desde que entra en onboarding hasta que cancela o es suspendido. Esto incluye calcular y cobrar la factura mensual, escalar alertas de pago, aplicar las reglas de mora y suspensión, gestionar la retención de datos al cancelar, y mantener el estado del cliente actualizado en todo momento.

Es el único harness que toca dinero. Todo lo relacionado con cobros, fechas de vencimiento, alertas y acceso bloqueado pasa por aquí.

---

## Estados del cliente

```
Prospecto → Onboarding → Activo → En mora → Suspendido → Cancelado
                                ↑___________↓ (reactivación)
```

| Estado | Descripción | Acceso al dashboard |
|--------|-------------|---------------------|
| `onboarding` | Mes 1 gratuito — recibiendo datos, construyendo modelos | Sí (parcial — solo ISD) |
| `activo` | Servicio completo, pagos al día | Sí (completo) |
| `en_mora` | Pago vencido, dentro del período de gracia (días 1–8) | Sí (con banner de alerta) |
| `suspendido` | Día 9 sin pago — acceso bloqueado | No (pantalla de suspensión) |
| `cancelado` | Cliente canceló el servicio | No (hasta fin del período de retención) |

---

## Disparadores y eventos que escucha

| Evento / Disparador | Origen | Acción que dispara |
|--------------------|--------|--------------------|
| `onboarding_discovery_complete` | 010 Discovery | Inicia el temporizador del mes gratuito |
| `diagnosis_complete` | 020 Diagnosis | Actualiza el cargo por complejidad para la próxima factura |
| `publisher_complete` | 040 Publisher | Registra la entrega del pronóstico en el historial del cliente |
| `payment_received` (webhook) | Stripe | Procesa el pago, actualiza fecha de vencimiento, cambia estado |
| `payment_failed` (webhook) | Stripe | Registra el fallo, inicia conteo de días de mora |
| `subscription_cancelled` | Operador Triple S | Inicia el proceso de cancelación y retención de datos |
| Timer diario (00:00 UTC) | Prefect scheduler | Evalúa el estado de cada cliente y escala alertas si corresponde |

---

## Procesos

### P1 — Inicio del mes gratuito de onboarding

**Disparador:** `onboarding_discovery_complete`

Al recibir este evento, el harness:
1. Registra la fecha de inicio del onboarding como `onboarding_start_date`
2. Calcula `first_billing_date` = `onboarding_start_date` + 30 días
3. Crea la suscripción en estado `onboarding` — sin cargo aún
4. Programa en Prefect la generación de la primera factura para `first_billing_date`

No se toca Stripe durante el mes gratuito. La suscripción existe solo en la base de datos interna hasta el primer cobro.

### P2 — Cálculo del monto mensual

**Ejecutado en:** generación de cada factura mensual, y cada vez que llega `diagnosis_complete` con un nuevo ISD

El monto total se calcula con dos componentes (DEC-002, DEC-016):

```
monto_base = precio_categoría × descuento_plan

precio_categoría:  M = USD 200 / L = USD 350 / XL = USD 500

descuento_plan:
  Mensual     → sin descuento (factor 1.00)
  Trimestral  → 8% de descuento (factor 0.92) — cobro único cada 3 meses
  Anual       → 18% de descuento (factor 0.82) — cobro único cada 12 meses

cargo_complejidad:
  ISD ≥ 95%  → +0%
  ISD 70–94% → +20%
  ISD 50–69% → +50%
  ISD < 50%  → +80%

monto_total = monto_base × (1 + cargo_complejidad)
```

El ISD que determina el cargo es el del último `diagnosis_complete` registrado. Si el ISD mejoró o empeoró desde la factura anterior, el ajuste se refleja en la próxima factura — nunca retroactivamente.

**Ejemplos:**

| Categoría | Plan | ISD | Cálculo | Total/mes |
|-----------|------|-----|---------|-----------|
| M | Mensual | 97% | 200 × 1.00 × 1.00 | USD 200 |
| L | Mensual | 82% | 350 × 1.00 × 1.20 | USD 420 |
| XL | Trimestral | 65% | 500 × 0.92 × 1.50 | USD 690 |
| M | Anual | 45% | 200 × 0.82 × 1.80 | USD 295 |

### P3 — Generación y cobro de la factura

**Ejecutado en:** `first_billing_date` y cada período de renovación

1. El harness calcula el monto final (P2)
2. Crea un PaymentIntent en Stripe con el monto correspondiente
3. Registra la factura en la tabla `invoices` con estado `pending`
4. Stripe intenta el cobro sobre el método de pago registrado del cliente
5. Stripe emite webhook `payment_received` o `payment_failed`

**Plan Trimestral / Anual:** El cobro es único por período completo. El monto mensual equivalente se muestra en el dashboard (transparencia), pero el cargo real es el total del período:
- Trimestral: `monto_mensual × 3 × 0.92` cobrado una sola vez
- Anual: `monto_mensual × 12 × 0.82` cobrado una sola vez

### P4 — Procesamiento del pago recibido

**Disparador:** webhook `payment_received` de Stripe

1. Actualiza la factura en `invoices` a estado `paid`
2. Calcula el atraso en días: `atraso = fecha_pago - fecha_vencimiento_original`
3. Aplica la regla de fecha de vencimiento (DEC-003):

| Atraso | Nueva fecha de vencimiento |
|--------|---------------------------|
| ≤ 0 días (pago puntual o anticipado) | `vencimiento_original + duración_del_plan` |
| 1–2 días | `vencimiento_original + duración_del_plan` (se conserva la fecha original) |
| ≥ 3 días | `fecha_pago + duración_del_plan` (fecha se desplaza) |

4. Actualiza el estado del cliente a `activo` (si estaba `en_mora` o `suspendido`)
5. Si el cliente estaba suspendido, restaura el acceso al dashboard
6. Elimina todos los banners y alertas de mora activos
7. Emite el evento `payment_processed` con el nuevo `vencimiento`

### P5 — Evaluación diaria y escalada de alertas

**Disparador:** Timer diario a las 00:00 UTC (Prefect scheduler)

El harness evalúa el estado de cada cliente activo y determina si hay vencimientos próximos o vencidos:

```
dias_de_mora = fecha_actual - fecha_vencimiento  (si fecha_actual > fecha_vencimiento)
```

**Protocolo de alertas (DEC-003):**

| Días de mora | Tipo de alerta en dashboard | Fijado | Correo al responsable |
|-------------|----------------------------|--------|-----------------------|
| 0 (puntual) | Sin alerta | — | No |
| 2 | Banner verde informativo | No fijo (cierra solo) | No |
| 3 | Banner verde informativo | No fijo | No |
| 5 | Banner verde informativo | **Fijo** (no se puede cerrar) | Sí |
| 6 | Banner amarillo — Período de gracia | **Fijo** | Sí |
| 7 | Banner amarillo — Período de gracia | **Fijo** | Sí |
| 8 | Banner amarillo — Período de gracia | **Fijo** | Sí |
| 9+ | **Suspensión** — pantalla de bloqueo | N/A | Sí |

Los días 2 y 3 el banner es amigable: "Tu período de servicio vence pronto. Asegúrate de tener el método de pago al día."

Los días 6–8 el banner es urgente: "Estás en período de gracia. El acceso se suspenderá si no recibimos el pago."

El correo al responsable de pagos (registrado en 010 Discovery) se envía desde el día 5. El correo del día 9 informa la suspensión.

**Estado del cliente durante el período de alerta:** permanece en `activo` durante días 1–8 — el cliente sigue viendo el dashboard con el banner. Solo en el día 9 pasa a `suspendido`.

### P6 — Suspensión del acceso

**Disparador:** El timer diario detecta `dias_de_mora = 9`

1. Cambia el estado del cliente a `suspendido`
2. Revoca los tokens de sesión activos de todos los usuarios del cliente (Supabase Auth)
3. El dashboard muestra una pantalla de suspensión con el monto adeudado y el botón de pago
4. Envía correo de suspensión al responsable de pagos y al contacto principal
5. Los harnesses 015, 020, 025, 030, 035 continúan ejecutándose en su cadencia normal — la suspensión solo afecta el acceso al dashboard, no el procesamiento interno. Esto garantiza que cuando el cliente reactive, el pronóstico esté al día.
6. Emite evento `client_suspended`

### P7 — Reactivación tras suspensión

**Disparador:** `payment_received` cuando el estado del cliente es `suspendido`

1. Procesa el pago (P4)
2. Calcula la nueva fecha de vencimiento (atraso ≥ 3 días → `fecha_pago + duración_plan`)
3. Restaura el acceso al dashboard (nuevos tokens via Supabase Auth)
4. Remueve la pantalla de suspensión
5. Emite evento `client_reactivated`
6. El dashboard muestra inmediatamente el pronóstico más reciente (ya estaba procesado)

### P8 — Procesamiento de cancelación

**Disparador:** Solicitud de cancelación recibida por el operador de Triple S

La cancelación no puede ser iniciada por el cliente desde el dashboard — debe pasar por el operador (modelo de servicio, DEC-001).

1. Cambia el estado del cliente a `cancelado`
2. Registra `cancellation_date` = fecha actual
3. Calcula los períodos clave de retención (DEC-010):

```
export_window_end  = cancellation_date + 90 días   ← último día para solicitar exportación
retention_end      = cancellation_date + 180 días   ← eliminación definitiva de datos
```

4. Revoca acceso al dashboard para todos los usuarios del cliente
5. Cancela la suscripción en Stripe (sin reembolso — DEC-002)
6. Notifica al cliente por correo con las fechas de retención y la ventana de exportación
7. Emite evento `client_cancelled`

**Sin reembolsos:** Si el cliente cancela a mitad de un período (mensual, trimestral o anual), el período ya cobrado no se reembolsa.

### P9 — Gestión de la ventana de exportación post-cancelación

**Ejecutado en:** Solicitudes de exportación dentro de los 90 días post-cancelación

Si el cliente solicita exportación de sus datos de pronóstico (DEC-010):

1. Verifica que `fecha_solicitud ≤ export_window_end`
2. Verifica que no haya una exportación previa pendiente de confirmación (el sistema bloquea una segunda solicitud hasta que la primera esté confirmada)
3. Genera el archivo exportable con datos de pronóstico históricos (nunca Bronze/Silver/Gold)
4. Establece `export_delivery_deadline` = `fecha_solicitud + 90 días`
5. Bloquea la eliminación definitiva hasta que el cliente confirme recepción de la exportación
6. Actualiza el estado de la solicitud en la tabla `export_requests`

### P10 — Eliminación definitiva de datos

**Disparador:** Timer diario detecta `fecha_actual = retention_end` (180 días post-cancelación)

**Condición de bloqueo:** Si hay una exportación pendiente de confirmación (`export_requests.status = 'pending_confirmation'`), la eliminación se pospone hasta que el cliente confirme o hasta que pasen 90 días adicionales sin respuesta.

Cuando procede:
1. Elimina los archivos del tenant en Supabase Storage (`tenants/{id}/` completo)
2. Elimina el archivo DuckDB del tenant
3. Elimina todos los registros del tenant en PostgreSQL (cascade)
4. Registra la eliminación en `deletion_log` con timestamp y razón
5. Emite evento `client_data_deleted`

### P11 — Actualización del monto tras cambio de ISD

**Disparador:** `diagnosis_complete` con nuevo ISD

1. Calcula el nuevo nivel de cargo por complejidad
2. Si el nivel cambió respecto al período anterior, actualiza `next_invoice_amount` en la tabla `subscriptions`
3. Muestra en el dashboard de Triple S el nuevo monto que se cobrará en la próxima factura
4. El cliente ve en su dashboard el nuevo nivel de cargo y su impacto (DEC-016)

---

## Salidas

### Registros actualizados en base de datos

| Tabla | Actualización |
|-------|--------------|
| `clients` | `status`, `last_payment_at`, `next_billing_date`, `dias_mora` |
| `subscriptions` | `current_isd_nivel`, `next_invoice_amount`, `plan`, `billing_date` |
| `invoices` | Nueva fila por cada factura generada: monto, estado, timestamp de pago |
| `alerts_log` | Una fila por cada alerta disparada: tipo, día de mora, canal (dashboard / correo) |
| `export_requests` | Estado de cada solicitud de exportación post-cancelación |
| `deletion_log` | Registro de eliminaciones definitivas con timestamp |

### Eventos emitidos

| Evento | Cuándo |
|--------|--------|
| `client_activated` | Al completarse el mes gratuito y recibir el primer pago |
| `client_suspended` | Al llegar al día 9 sin pago |
| `client_reactivated` | Al recibir pago de un cliente suspendido |
| `client_cancelled` | Al procesar la cancelación |
| `client_data_deleted` | Al completar la eliminación definitiva |
| `payment_processed` | En cada pago exitoso (incluye nueva fecha de vencimiento) |

---

## Condiciones de completitud por proceso

Este harness no tiene un estado "completado" único — es permanentemente activo mientras haya clientes en el sistema. Cada proceso individual completa cuando:

- **P3 (Factura):** Stripe confirmó el intento de cobro (exitoso o fallido)
- **P5 (Alertas):** Todos los clientes del día fueron evaluados y las alertas correspondientes disparadas
- **P6 (Suspensión):** Acceso revocado y correo enviado confirmado
- **P7 (Reactivación):** Acceso restaurado y nueva fecha de vencimiento registrada
- **P8 (Cancelación):** Estado `cancelado`, Stripe actualizado y correo de retención enviado
- **P10 (Eliminación):** Todos los datos del tenant eliminados y `deletion_log` registrado

---

## Lo que este harness NO hace

- No genera pronósticos ni procesa datos de demanda
- No calcula el ISD — solo consume el resultado de 020 Diagnosis para ajustar el cargo
- No envía el pronóstico al cliente — eso es 040 Publisher
- No gestiona los roles de usuario del dashboard — eso es Supabase Auth (configurado en 010 Discovery)
- No cobra directamente — delega en Stripe; solo registra el resultado

---

## Dependencias

| Tipo | Harness / Sistema | Detalle |
|------|-------------------|---------|
| Entrada | 010 Discovery | Perfil del cliente, contactos, plan, categoría para iniciar la suscripción |
| Entrada | 020 Diagnosis | ISD para calcular el cargo por complejidad |
| Entrada | 040 Publisher | Confirma entrega del pronóstico para el registro del ciclo |
| Externo | Stripe | Pasarela de pagos — genera cargos, recibe webhooks de confirmación |
| Externo | SendGrid | Envío de correos de alerta, suspensión y cancelación |
| Externo | Supabase Auth | Revocación y restauración de acceso al dashboard |
| Scheduler | Prefect | Timer diario para evaluación de mora y generación de facturas |

---

## Notas de diseño

- **050 Lifecycle se construye antes del Bloque B (DEC-026):** No tiene dependencias técnicas del pipeline de ML. Se construye en posición 4 porque el mes 1 gratuito da el margen de tiempo para tenerlo listo antes del primer cobro real. Si se construyera después, el primer cliente podría llegar al mes 2 sin sistema de cobro.
- **La suspensión no detiene el pipeline de datos:** Los harnesses 015–035 continúan ejecutándose para el cliente suspendido. Esto tiene dos razones: (1) los datos siguen llegando en Modo Incremental y no conviene perder esa continuidad, y (2) cuando el cliente reactive el acceso, el pronóstico ya está al día — no hay período muerto de servicio.
- **Sin acceso directo del cliente a cancelar:** Coherente con el modelo Service as a Software. La cancelación pasa por el operador de Triple S, quien puede identificar si el cliente tiene un problema resolvible antes de cancelar.
- **Webhook de Stripe como fuente de verdad de pagos:** El harness nunca asume que un pago ocurrió sin la confirmación del webhook. Esto evita estados inconsistentes donde el sistema cree que se cobró pero Stripe no procesó el cargo.
