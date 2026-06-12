# Harness 010 — Discovery

**Tipo:** Semi-humano  
**Bloque de construcción:** A (posición 1 de 11)  
**Hito al que pertenece:** Hito A — Primer piloto ejecutable  
**Disparador:** Un prospecto firma el contrato y pasa a estado *Onboarding*

---

## Propósito

Capturar todo el contexto necesario para que el sistema pueda operar con un cliente nuevo. Es el único harness donde un operador de Triple S conduce activamente una sesión con el cliente. Al completarse, el sistema tiene suficiente información para recibir datos, calcular el ISD y gestionar el ciclo de vida del cliente desde el primer día.

---

## Entradas

### Entradas humanas (capturadas por el operador Triple S)

| Entrada | Descripción | Obligatorio |
|---------|-------------|-------------|
| Nombre y razón social del cliente ABC | Identificador legal de la empresa | Sí |
| Sector / industria | Contexto del negocio (alimentos, químicos, textil, etc.) | Sí |
| Nombre del contacto principal | Planificador de demanda o coordinador del onboarding | Sí |
| Correo y teléfono del contacto principal | Canal de comunicación durante onboarding | Sí |
| Nombre y correo del responsable de pagos | Receptor de alertas de cobro (DEC-003) | Sí |
| Número aproximado de SKUs activos | Insumo para estimación preliminar del ITO | Sí |
| Número aproximado de clientes XYZ atendidos | Insumo para estimación preliminar del ITO | Sí |
| Volumen aproximado de pedidos por mes | Insumo para estimación preliminar del ITO | Sí |
| Años de historial de pedidos disponible | Para evaluar cold start (DEC-013) | Sí |
| Modo de entrega de datos preferido | Batch o Incremental (DEC-012) | Sí |
| Frecuencia de actualización de datos (si Incremental) | Diaria o semanal | Condicional |
| Horizonte de pronóstico requerido | Días / semanas / meses / múltiples meses (DEC-018) | Sí |
| Jerarquía de productos disponible | Categoría → Subcategoría → SKU — niveles que tiene el cliente | Sí |
| Jerarquía geográfica disponible | Región → País → Ciudad → Sede — niveles que tiene el cliente | Sí |
| ¿Tiene Esquema 2 (producción e inventario)? | Si el cliente puede entregar datos de producción e inventario (DEC-014) | Sí |
| Mínimos contractuales con sus clientes XYZ | Si existen, si se cumplen habitualmente (DEC-019) | Opcional |
| Plan de suscripción elegido | Mensual / Trimestral / Anual (DEC-002) | Sí |
| Criterios de éxito del cliente | Qué le importa reducir: sobre-inventario, quiebres, ambos | Sí |

### Entradas del sistema (pre-existentes)

| Entrada | Descripción | Fuente |
|---------|-------------|--------|
| Contrato firmado | Evidencia de que el cliente está en estado Onboarding | CRM / archivo |
| Fecha de firma del contrato | Punto de partida para el temporizador del mes gratuito (DEC-004) | CRM / archivo |
| Categoría tarifaria asignada (M / L / XL) | Determinada durante el proceso comercial con ITO preliminar (DEC-002) | CRM / archivo |

---

## Procesos

### P1 — Sesión de descubrimiento con el cliente

El operador de Triple S conduce una videollamada o reunión presencial usando la plantilla de preguntas del harness. Captura todas las entradas humanas listadas arriba. Duración estimada: 60–90 minutos.

### P2 — Estimación del ITO y confirmación de categoría

Con el número de SKUs, clientes XYZ y volumen de pedidos capturados, el operador calcula el Índice de Tamaño Operativo (ITO) preliminar y verifica que la categoría asignada durante la venta (M / L / XL) sea correcta. Si hay discrepancia, se ajusta la categoría antes de continuar.

> Fórmula ITO: `ITO = w1 × SKUs_activos + w2 × clientes_XYZ + w3 × pedidos_por_mes`  
> Pesos w1, w2, w3 y umbrales de corte: pendientes de calibración (T-030)

### P3 — Evaluación de cold start por cliente

Con el historial disponible declarado, el sistema determina el modo de arranque de cada combinación cliente × producto:

| Historial disponible | Nivel de confianza asignado |
|----------------------|-----------------------------|
| ≥ 3 años | Alta |
| 2–3 años | Estándar |
| 1–2 años | Reducida |
| < 1 año | Experimental — activa cascada cold start |

Si el historial < 1 año, se documenta qué paso de la cascada aplicará:
1. Analogía por categoría de producto
2. Analogía por cliente XYZ
3. Acumulación de 3 meses antes de pronosticar

### P4 — Configuración de parámetros del cliente

El operador registra en el sistema los parámetros operativos del cliente:
- Modo de ingesta (Batch / Incremental + frecuencia)
- Horizonte de pronóstico
- Niveles de jerarquía de producto disponibles
- Niveles de jerarquía geográfica disponibles
- Si tiene Esquema 2 activo
- Si tiene mínimos contractuales registrables

### P5 — Generación de instrucciones de entrega de datos

El harness produce una guía personalizada para el cliente, en lenguaje no técnico, que explica:
- Qué archivo(s) entregar
- En qué formato (CSV / Excel)
- Qué columnas son obligatorias y qué columnas son opcionales (basado en DEC-014)
- Cómo y dónde subir el archivo
- Qué esperar en los próximos días (diagnóstico ISD)

### P6 — Registro del cliente en el sistema

El harness crea el registro del cliente en la base de datos con:
- Estado inicial: `onboarding`
- Fecha de inicio del mes gratuito
- Todos los parámetros configurados en P4
- Contactos registrados (principal + pagos)
- Plan de suscripción

### P7 — Creación de la carpeta del cliente en Storage

El harness crea la estructura de carpetas en Supabase Storage:
```
tenants/
└── {tenant_id}/
    ├── bronze/
    ├── silver/
    ├── gold/
    ├── models/
    ├── forecasts/
    └── exports/
```
Este es el aislamiento físico por tenant (DEC-021).

---

## Salidas

### Archivos generados

| Archivo | Descripción | Destino |
|---------|-------------|---------|
| `client_profile.json` | Perfil completo del cliente: razón social, contactos, categoría, ITO, nivel de confianza cold start, parámetros operativos | Base de datos + Storage `tenants/{id}/` |
| `onboarding_config.json` | Parámetros de operación: modo ingesta, horizonte, jerarquías, esquemas activos, mínimos contractuales | Base de datos |
| `data_intake_guide.pdf` | Instrucciones de entrega de datos personalizadas para el cliente (en lenguaje de negocio, no técnico) | Enviado al contacto principal por correo |
| `discovery_session_notes.md` | Notas libres del operador durante la sesión | Storage `tenants/{id}/` |

### Registros creados en base de datos

| Tabla | Registro creado |
|-------|----------------|
| `clients` | Fila nueva con tenant_id, razón social, estado `onboarding`, fecha inicio, plan, categoría |
| `contacts` | Contacto principal + responsable de pagos |
| `client_config` | Parámetros operativos del cliente (horizonte, modo ingesta, jerarquías) |
| `subscriptions` | Suscripción con plan, monto base, fecha de inicio del primer cobro (mes 2) |

### Evento disparado al completarse

```
EVENT: onboarding_discovery_complete
  tenant_id: {id}
  timestamp: {ISO-8601}
  next_harness: 015_intake
```

Este evento lo escucha el harness **015 Intake**, que queda en espera de la primera entrega de datos del cliente.

---

## Condiciones de completitud

El harness 010 se considera **completo** cuando:

1. Todos los campos obligatorios de la sesión de descubrimiento están registrados
2. El ITO está calculado y la categoría está confirmada
3. La carpeta del tenant existe en Storage
4. El registro del cliente existe en la base de datos con estado `onboarding`
5. La guía de entrega de datos fue enviada al contacto principal
6. El evento `onboarding_discovery_complete` fue emitido

---

## Lo que este harness NO hace

- No recibe ni valida archivos de datos del cliente (→ 015 Intake)
- No calcula el ISD (→ 020 Diagnosis)
- No limpia ni transforma datos (→ 025 Refinery)
- No gestiona pagos ni alertas de cobro (→ 050 Lifecycle)
- No produce pronósticos (→ 035 Predictor)

---

## Dependencias

| Tipo | Harness / Sistema | Detalle |
|------|-------------------|---------|
| Anterior | Ninguno | Es el primer harness del sistema |
| Siguiente | 015 Intake | Queda en espera tras recibir el evento de completitud |
| Transversal | 050 Lifecycle | Debe registrar la suscripción para que 050 pueda gestionar el ciclo de cobro |

---

## Notas de diseño

- Este es el único punto donde un humano (el operador Triple S) tiene rol activo en la captura de información. Todos los harnesses siguientes son automatizados o semi-automatizados.
- La guía de entrega de datos (`data_intake_guide.pdf`) es el primer entregable tangible que el cliente recibe — debe estar en lenguaje de negocio, sin terminología técnica.
- El ITO calculado aquí es preliminar. Será recalibrado cuando los datos reales estén disponibles (después de 015 y 020).
- La estructura de carpetas en Storage se crea aquí y nunca se recrea — los harnesses posteriores solo escriben dentro de ella.
