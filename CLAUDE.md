# CLAUDE.md — Directrices del Proyecto Harness Forecaster

## Quiénes somos

**Sabbia Solutions & Software (Triple S)** es la empresa que diseña, construye y comercializa este producto. Triple S no es el usuario final — es la empresa de software que vende el servicio.

## Nombre del sistema

El sistema se llama **FARO** — **F**orecasting **A**gentic **R**esults & **O**perations.

El nombre tiene doble lectura intencional: en español, *faro* es el faro de luz que guía a los barcos en la incertidumbre — FARO guía a los fabricantes en la incertidumbre de la demanda. El sistema lleva el nombre FARO internamente y en comunicaciones comerciales de Triple S.

## Qué estamos construyendo

**FARO** es un sistema agéntico de pronóstico de demanda B2B. El modelo de negocio es **Service as a Software**: Triple S opera el sistema de punta a punta y entrega pronósticos de demanda como servicio a empresas manufactureras. El cliente no opera el software — recibe los resultados.

## El problema que resolvemos

Empresas manufactureras (tipo ABC) venden productos a otras empresas (tipo XYZ). La demanda de esos clientes es volátil e impredecible, lo que genera sobre-inventarios y agotamientos de stock. Triple S pronostica esa demanda usando agentes de IA.

## Reglas de negocio fundamentales — leer antes de cualquier implementación

### Modelo de servicio
- Service as a Software: Triple S opera todo, el cliente solo consume resultados
- El cliente recibe resultados vía: dashboard de solo lectura, correo automático, y archivo exportable (Excel/CSV)
- Sin API pública para el cliente — contradice el modelo de servicio

### Precios y planes
- Tres categorías de empresa: **M** (USD 200/mes), **L** (USD 350/mes), **XL** (USD 500/mes)
- Clasificación por Índice de Tamaño Operativo (ITO): productos activos + clientes atendidos + volumen de pedidos
- Tres planes de pago: **Mensual** (sin descuento), **Trimestral** (8% descuento), **Anual** (18% descuento)
- Descuentos fijos para todas las categorías — sin variación por tamaño
- Sin reembolsos por cancelación anticipada

### Ciclo de pagos y suspensión
- 30 días de servicio desde la fecha de pago
- Días 2, 3, 5 del vencimiento: mensajes verdes (no fijo / no fijo / fijo) + correo al responsable
- Días 6, 7, 8: mensaje amarillo fijo + correo (período de gracia)
- Día 9 sin pago: pantalla de suspensión, acceso bloqueado
- Atraso ≤ 2 días → conserva fecha original de vencimiento
- Atraso ≥ 3 días → nueva fecha = día de pago + 30 días
- Cobro gestionado por pasarela de pagos automatizada (por definir cuál)

### Onboarding
- Mes 1: **gratuito** — ingesta de datos, diagnóstico de salud, construcción de confianza
- Mes 2: primer pago
- Máximo mes 3: entrega del primer pronóstico
- El mes 1 gratuito es el piloto — no hay piloto separado previo

### Datos del cliente — arquitectura medallón
- Los datos originales del cliente son **intocables** — nunca se modifican
- Triple S trabaja siempre sobre una copia
- Tres capas: **Bronce** (copia exacta) → **Plata** (limpieza y normalización) → **Oro** (listo para modelos)
- Los agentes de IA operan únicamente sobre la capa Oro
- Precio = suscripción fija + cargo adicional por complejidad de datos

### Salud de datos
- Objetivo: ≥ 95% de salud (≤ 5% de errores)
- Diagnóstico generado desde la capa Bronce, presentado al cliente mensualmente
- Triple S nunca corrige los datos del cliente en su origen — le muestra el camino

### SLAs
- Pronóstico entregado: primeros 5 días hábiles del mes
- Precisión: MAPE ≤ 15% con salud ≥ 95% / MAPE ≤ 25% con salud 70–94% / sin garantía con salud < 70%
- Disponibilidad del dashboard: 99% mensual
- Respuesta incidente crítico: 4h hábiles / resolución: 24h hábiles
- Respuesta consultas generales: 24h hábiles

### Retención de datos al cancelar
- Datos conservados 6 meses tras cancelación
- Exportación disponible solo en los primeros 3 meses (solo datos de pronóstico — nunca Bronce/Plata/Oro)
- Plazo de entrega de exportación: hasta 3 meses después de la solicitud
- Eliminación bloqueada si hay exportación pendiente de confirmación
- Eliminación definitiva al completar el mes 6

### Variabilidad de pedidos
- La unidad mínima de análisis es **cliente × producto** — no el cliente ni el producto por separado
- Cada combinación cliente × producto tiene su propia frecuencia de pedido y tiempo de entrega
- No existe ciclo estándar global — el sistema trata cada combinación de forma independiente

## Estructura del proyecto

```
Harness_Forecaster/
├── CLAUDE.md                  ← Este archivo
├── problem_statement.md       ← Definición del problema y preguntas abiertas
└── progress/
    ├── progress.md            ← Estado actual y próximas tareas para nuevas sesiones
    ├── tasks.md               ← Registro atómico de tareas con estado
    ├── decisions.md           ← Decisiones importantes tomadas
    └── lessons.md             ← Lecciones aprendidas
```

## Instrucciones para agentes de Claude Code

1. **Leer siempre primero** `progress/progress.md` para entender el estado actual del proyecto
2. **Consultar** `progress/decisions.md` antes de proponer arquitecturas o enfoques — puede haber decisiones ya tomadas
3. **Consultar** `progress/lessons.md` antes de implementar para evitar repetir errores
4. **Registrar** toda tarea nueva en `progress/tasks.md` con estado inicial "no iniciada"
5. **Actualizar** el estado de las tareas en `progress/tasks.md` al iniciarlas y completarlas
6. **Actualizar** `progress/progress.md` al final de cada sesión de trabajo significativa
7. El idioma del proyecto es **español** para toda la documentación — el código puede estar en inglés
8. Todo archivo nuevo debe tener nombre en **inglés**, contenido en **español**
