# Decisiones del Proyecto — Harness Forecaster

Registro de decisiones importantes tomadas durante el desarrollo del proyecto.
Leer antes de proponer nuevas arquitecturas o enfoques.

---

## Índice (catálogo)

> Escanea esta tabla y abre solo la entrada que necesites (busca `## DEC-NNN`). **Alcance:** `Fundacional` = transversal al producto / aplica a todos los harnesses; `H-010` = mecánica específica del harness 010 Discovery. Las entradas no están en orden numérico estricto en el cuerpo — usa el buscador.

| ID | Título | Alcance |
|---|---|---|
| DEC-001 | Modelo de negocio: Service as a Software | Fundacional |
| DEC-002 | Categorías de precio y planes de pago | Fundacional |
| DEC-003 | Regla de renovación de fecha por pago tardío | Fundacional |
| DEC-004 | Mes 1 de onboarding gratuito | Fundacional |
| DEC-005 | Arquitectura medallón de datos (Bronce / Plata / Oro) | Fundacional |
| DEC-006 | Precio variable por complejidad de datos | Fundacional |
| DEC-007 | Canales de entrega de resultados | Fundacional |
| DEC-008 | Objetivo de salud de datos: 95% | Fundacional |
| DEC-009 | SLAs de precisión vinculados a salud de datos | Fundacional |
| DEC-010 | Retención y exportación de datos al cancelar | Fundacional |
| DEC-011 | Unidad mínima de análisis: cliente × producto | Fundacional |
| DEC-012 | Modos de ingesta de datos: Batch e Incremental | Fundacional (clave para 015) |
| DEC-013 | Historial mínimo y estrategia cold start | Fundacional |
| DEC-014 | Esquema de datos: dos tablas complementarias | Fundacional (clave para 015) |
| DEC-015 | Índice de Salud de Datos (ISD): 6 dimensiones ponderadas | Fundacional |
| DEC-016 | Escala de complejidad de datos y cargo adicional | Fundacional |
| DEC-017 | Maestro de datos: construido y mantenido por Triple S | Fundacional |
| DEC-018 | Alcance del pronóstico: horizonte, granularidad y geografía | Fundacional |
| DEC-019 | Patrones de pedido: estacionalidad, señales, mínimos y atípicos | Fundacional |
| DEC-020 | Stack tecnológico: tres fases progresivas | Fundacional |
| DEC-021 | Latencia, seguridad y aislamiento de datos | Fundacional |
| DEC-022 | Roles de usuario del dashboard y nivel de explicabilidad | Fundacional |
| DEC-023 | KPIs internos de Triple S | Fundacional |
| DEC-024 | Arquitectura de harnesses operacionales del producto | Fundacional |
| DEC-025 | Simulaciones y escenarios what-if: Opción C (escenarios predefinidos) | Fundacional (060) |
| DEC-026 | Orden de construcción de los harnesses operacionales | Fundacional |
| DEC-027 | Convención de nombres para archivos de brief | Fundacional |
| DEC-028 | Estructura de carpetas numeradas dentro de cada harness | Fundacional |
| DEC-029 | Nombre del sistema: FARO | Fundacional |
| DEC-030 | Arquitectura de agentes del 010: governor spawna workers vía CLI | H-010 — **OBSOLETA, reemplazada por DEC-051** |
| DEC-031 | Skills como directorios con SKILL.md (schemas de referencia) | Fundacional |
| DEC-032 | Estructura de carpetas fuente para scripts y templates de harness | Fundacional |
| DEC-033 | Archivos workflows como guías de navegación livianas | Fundacional |
| DEC-034 | default_stacks.md descartado (el stack vive en los agentes) | H-010 |
| DEC-035 | Rediseño del discovery-interviewer: entrevista directa a stakeholders | H-010 |
| DEC-036 | Nuevo agente: discovery-synthesizer | H-010 |
| DEC-037 | Carpeta 800_inputs/ para artefactos de entrada humana | Fundacional |
| DEC-038 | Guardado incremental por bloque en interviewer + /faro-save | H-010 |
| DEC-039 | Skills del synthesizer renombradas a prefijo discovery-* | H-010 |
| DEC-056 | Estrategia de prueba automatizada del harness 010 Discovery | H-010 *(antes DEC-039 duplicado)* |
| DEC-040 | Estrategia de validación del harness 010 en tres fases | H-010 |
| DEC-041 | Sprint Contract persiste en 700_contract/sc_010_discovery.md | Fundacional (patrón) |
| DEC-042 | Subcarpetas dentro de 010_discovery/: deliverables/ y support/ | H-010 |
| DEC-043 | `pending_email.json` vive en 600_persistence/ | H-010 |
| DEC-044 | Convención de nombres para carpetas de datos y salidas | Fundacional |
| DEC-045 | Interviewer presenta todas las preguntas del bloque de una vez | H-010 |
| DEC-046 | Deploy en modo dev: junctions en lugar de copias | Fundacional (infra) |
| DEC-047 | El governor genera el tenant_id; los workers lo leen de harness-state | Fundacional (patrón) |
| DEC-048 | Instalación a nivel de proyecto | Fundacional (infra) |
| DEC-049 | El interviewer arranca con un turno de setup antes de preguntar | H-010 |
| DEC-050 | Marcador no-checkpoint del tramo interactivo + governor_mode vivo | Fundacional (capa de estado) |
| DEC-051 | Modelo conductor: la sesión principal es el único spawner de agentes | Fundacional (patrón crítico) |
| DEC-052 | responsable_pagos: pregunta dirigida del interviewer | H-010 |
| DEC-053 | Allowlist de permisos cubre la herramienta PowerShell (Opción A) | Fundacional (infra) |
| DEC-054 | Permisos por proyecto: bypassPermissions en el template de settings | Fundacional (infra) |
| DEC-055 | Cerrado el 010; sigue el 015, con persistencia Capa 1 acoplada | Fundacional (rumbo) |

---

## DEC-001 — Modelo de negocio: Service as a Software
**Fecha:** 2026-06-08
**Decisión:** El modelo de negocio es Service as a Software, no SaaS. Triple S opera el sistema de punta a punta. El cliente no toca el software — solo recibe resultados.
**Razón:** El cliente confía en Triple S para que le resuelva el problema completo. El software es el motor interno del servicio, no el producto que se le vende al cliente.
**Impacto:** El cliente no necesita capacitación técnica. Toda la operación es responsabilidad de Triple S. El dashboard es de solo lectura — sin configuración por parte del cliente.

---

## DEC-002 — Categorías de precio y planes de pago
**Fecha:** 2026-06-08
**Decisión:** Tres categorías (M: USD 200, L: USD 350, XL: USD 500/mes) clasificadas por ITO. Tres planes: Mensual, Trimestral (8% dto.), Anual (18% dto.). Descuentos fijos para todas las categorías. Sin reembolsos.
**Razón:** Precio único simplifica la venta. El rango USD 200–500 posiciona el servicio en 1/3 del costo mínimo de un experto humano. Los descuentos por compromiso anticipado mejoran el flujo de caja de Triple S.
**Impacto:** El harness debe conocer la categoría y el plan de cada cliente para calcular fechas de vencimiento y montos.

---

## DEC-003 — Regla de renovación de fecha por pago tardío
**Fecha:** 2026-06-08
**Decisión:** Atraso ≤ 2 días → conserva la fecha original de vencimiento. Atraso ≥ 3 días → nueva fecha de vencimiento = día de pago + 30 días.
**Razón:** Protege al cliente ocasionalmente tardío sin consecuencias, pero desplaza la fecha de quien se atrasa de forma deliberada, creando un incentivo natural a pagar puntual.
**Impacto:** El harness calcula y actualiza la fecha de vencimiento automáticamente al registrar cada pago.

---

## DEC-004 — Mes 1 de onboarding gratuito
**Fecha:** 2026-06-08
**Decisión:** El primer mes del servicio es gratuito. El cliente paga desde el mes 2. El mes 1 gratuito es el piloto — no hay piloto separado previo al contrato.
**Razón:** Elimina la fricción de pago inicial, permite demostrar expertise con el diagnóstico de salud de datos, y construye confianza antes del primer cobro.
**Impacto:** El harness debe gestionar el estado "onboarding gratuito" como un estado diferenciado del estado "activo con pago".

---

## DEC-005 — Arquitectura medallón de datos (Bronce / Plata / Oro)
**Fecha:** 2026-06-08
**Decisión:** Los datos del cliente pasan por tres capas: Bronce (copia exacta e intocable), Plata (limpieza y normalización), Oro (listo para modelos). Los datos originales nunca se modifican. Los agentes de IA operan solo sobre la capa Oro.
**Razón:** Garantiza trazabilidad completa, protege la integridad del dato original, y permite auditar cualquier transformación aplicada.
**Impacto:** Requiere almacenamiento para tres versiones de los datos de cada cliente. El pipeline de transformación es parte central del harness.

---

## DEC-006 — Precio variable por complejidad de datos
**Fecha:** 2026-06-08
**Decisión:** El precio total = suscripción fija mensual + cargo adicional por complejidad de transformación de datos. A mayor desorden en los datos, mayor cargo.
**Razón:** Crea un incentivo económico directo para que el cliente mejore la calidad de sus datos. Compensa a Triple S por el esfuerzo adicional de transformación.
**Impacto:** El harness debe calcular y comunicar el cargo por complejidad con base en el índice de salud de datos de cada cliente.

---

## DEC-007 — Canales de entrega de resultados
**Fecha:** 2026-06-08
**Decisión:** Tres canales: (1) Dashboard de solo lectura, (2) Correo automático al publicar pronóstico, (3) Archivo exportable Excel/CSV desde el dashboard. Sin API pública.
**Razón:** El dashboard es el canal principal de consumo visual. El correo garantiza que el cliente reciba valor sin necesidad de recordar entrar al sistema. El exportable permite al planificador trabajar en su entorno habitual. La API fue descartada por requerir capacidad técnica en el cliente, incompatible con el modelo de servicio.
**Impacto:** El harness debe gestionar la publicación del pronóstico en los tres canales de forma coordinada.

---

## DEC-008 — Objetivo de salud de datos: 95%
**Fecha:** 2026-06-08
**Decisión:** El umbral objetivo de salud de datos es ≥ 95% (≤ 5% de errores). Por debajo de ese umbral Triple S trabaja activamente con el cliente para mejorar la calidad.
**Razón:** A partir del 95% los pronósticos alcanzan su máxima confiabilidad. Es el nivel en que Triple S puede garantizar MAPE ≤ 15%.
**Impacto:** Los SLAs de precisión están vinculados al índice de salud de datos — ver DEC-009.

---

## DEC-009 — SLAs de precisión vinculados a salud de datos
**Fecha:** 2026-06-08
**Decisión:** MAPE ≤ 15% si salud ≥ 95% / MAPE ≤ 25% si salud 70–94% / sin garantía si salud < 70%.
**Razón:** Protege a Triple S de comprometerse con precisión imposible cuando los datos del cliente son de mala calidad. Hace transparente la relación entre calidad de datos y calidad del pronóstico.
**Impacto:** El contrato de servicio debe incluir esta vinculación explícitamente.

---

## DEC-010 — Retención y exportación de datos al cancelar
**Fecha:** 2026-06-08
**Decisión:** Retención de 6 meses. Exportación disponible solo en los primeros 3 meses (solo datos de pronóstico, nunca Bronce/Plata/Oro). Entrega de exportación en máximo 3 meses desde la solicitud. Eliminación bloqueada si hay exportación pendiente de confirmar.
**Razón:** Protege al cliente con un período razonable de acceso a sus resultados. Protege a Triple S de exponer datos propietarios de su proceso (capas medallón). La regla de bloqueo ante exportación pendiente evita eliminar datos comprometidos.
**Impacto:** El harness debe gestionar el estado del cliente cancelado con su temporizador de retención y el estado de exportaciones pendientes.

---

## DEC-021 — Latencia, seguridad y aislamiento de datos
**Fecha:** 2026-06-08
**Decisión:** Latencias comprometidas: dashboard < 3s, procesamiento de datos < 24h, recálculo ISD < 4h, correo < 1h, notificaciones de pago inmediatas. Seguridad: HTTPS/TLS, Supabase Auth JWT, bcrypt, roles internos, auditoría, cifrado en reposo. Aislamiento: tres capas — RLS en PostgreSQL, carpetas por tenant en Supabase Storage, archivo DuckDB físico por cliente.
**Razón:** El aislamiento físico en DuckDB es la garantía más fuerte para datos analíticos — no hay política que configurar mal. RLS en PostgreSQL es el estándar para multi-tenant en Supabase. La combinación de las tres capas elimina cualquier riesgo de contaminación entre clientes.
**Impacto:** Todo nuevo modelo de datos en PostgreSQL debe incluir tenant_id y su política RLS correspondiente. El pipeline de datos debe crear y gestionar un archivo DuckDB por cliente. Supabase Storage debe estructurarse con carpetas por tenant_id desde el inicio.

---

## DEC-020 — Stack tecnológico: tres fases progresivas
**Fecha:** 2026-06-08
**Decisión:** Desarrollo en tres fases: Fase 1 (Excel/CSV), Fase 2 (Streamlit), Fase 3 (solución definitiva). Stack Fase 3: Python + FastAPI + Supabase (Auth + PostgreSQL + Storage) + DuckDB + Prefect + Stripe + SendGrid + Docker + Railway. Supabase Storage reemplaza AWS S3 inicialmente — es S3-compatible y permite migración futura sin cambios de código.
**Razón:** Supabase consolida autenticación, base de datos y almacenamiento en un solo proveedor, reduciendo la complejidad operativa para un equipo pequeño. Las tres fases permiten entregar valor al cliente desde el inicio sin esperar la solución completa.
**Impacto:** Todo el código se escribe en Python. El equipo de Triple S solo necesita aprender una plataforma (Supabase) para auth + datos + storage. DuckDB maneja el medallón analítico sin infraestructura de servidor adicional.

---

## DEC-019 — Patrones de pedido: estacionalidad, señales, mínimos y atípicos
**Fecha:** 2026-06-08
**Decisión:** (1) Estacionalidad: se detecta durante el mes 1 de onboarding — puede o no existir, no se asume por defecto. (2) Señales anticipadas de XYZn: generalmente no existen — el modelo se construye solo con historial observado. (3) Mínimos contractuales: algunos clientes los tienen pero no siempre se cumplen — se registran como variable adicional si el cliente los proporciona. (4) Pedidos atípicos: se detectan por desviación estadística del promedio histórico, se clasifican como extraordinarios legítimos (si coinciden con un evento conocido) o anomalías (si no tienen explicación), y se presentan al cliente para confirmación.
**Razón:** La demanda B2B tiene patrones implícitos que el cliente no comunica explícitamente. El valor de Triple S está precisamente en detectar esos patrones desde los datos, no en depender de información que el cliente raramente comparte.
**Impacto:** El agente de análisis debe incluir detección de estacionalidad en el onboarding. El motor de pronóstico debe incorporar eventos conocidos como variable. El agente de anomalías debe clasificar pedidos atípicos antes de pasarlos al modelo.

---

## DEC-018 — Alcance del pronóstico: horizonte, granularidad y geografía
**Fecha:** 2026-06-08
**Decisión:** (1) Horizonte variable por cliente: días, semanas, meses o múltiples meses — configurado en onboarding. (2) Pronóstico en dos niveles simultáneos: SKU y agregado por categoría/subcategoría. (3) Pronóstico en dos niveles de cliente simultáneos: por sede y por cliente consolidado. (4) Jerarquía geográfica flexible y parcial — el sistema opera con los niveles disponibles sin requerir jerarquía completa.
**Razón:** Cada empresa ABC tiene ciclos de negocio diferentes. Imponer un horizonte o granularidad único produciría pronósticos incorrectos o inutilizables para muchos clientes. La flexibilidad geográfica reconoce que muchas empresas operan solo en un país o ciudad.
**Impacto:** El motor de pronóstico debe parametrizarse por cliente. El modelo de datos debe soportar jerarquías geográficas incompletas sin errores. Los pronósticos agregados deben derivarse de los SKU para garantizar consistencia.

---

## DEC-017 — Maestro de datos: construido y mantenido por Triple S
**Fecha:** 2026-06-08
**Decisión:** Triple S construye y mantiene los tres maestros (Productos, Clientes XYZ, Geográfico) automáticamente a partir de los datos crudos del cliente durante la transformación Bronce → Plata. El cliente no entrega archivos de maestro separados. El cliente puede consultar el maestro en el dashboard (solo lectura) y solicitar correcciones a Triple S, pero nunca edita directamente.
**Razón:** Coherente con el modelo Service as a Software — el cliente no opera nada. Triple S mantiene el control total de la consistencia, evitando que el cliente introduzca errores en el maestro. Las inconsistencias detectadas (mismo elemento con nombres distintos) se reportan en el diagnóstico de salud de datos.
**Impacto:** El agente de transformación Bronce → Plata debe incluir lógica de extracción y consolidación de maestros. Las inconsistencias de maestro cuentan como errores en la dimensión de Consistencia del ISD.

---

## DEC-016 — Escala de complejidad de datos y cargo adicional
**Fecha:** 2026-06-08
**Decisión:** 4 niveles vinculados al ISD: Óptimo (≥95%, +0%), Moderado (70–94%, +20%), Significativo (50–69%, +50%), Crítico (<50%, +80%). El cargo se aplica sobre la suscripción mensual base y se evalúa mensualmente. Sin cargo adicional durante el mes 1 de onboarding.
**Razón:** El porcentaje de cargo refleja el esfuerzo real de transformación. El nivel Crítico al +80% crea un incentivo económico fuerte para que el cliente mejore sus datos. La escala es objetiva — está atada al ISD, no a criterios subjetivos.
**Impacto:** El harness debe calcular el cargo total (suscripción + complejidad) mensualmente y comunicarlo al cliente en el dashboard. La pasarela de pagos debe recibir el monto correcto según el nivel vigente de cada cliente.

---

## DEC-015 — Índice de Salud de Datos (ISD): 6 dimensiones ponderadas
**Fecha:** 2026-06-08
**Decisión:** El ISD se calcula con 6 dimensiones: Completitud (25%), Consistencia (20%), Continuidad (20%), Unicidad (15%), Cobertura temporal (10%), Exactitud (10%). Resultado de 0 a 100%. Meta: ≥ 95%. El dashboard muestra el puntaje global y el detalle por dimensión con la acción sugerida para el problema principal.
**Razón:** Las 6 dimensiones cubren los tipos de error más comunes en datos de pedidos B2B. La ponderación prioriza completitud y continuidad por ser las más críticas para modelos de series de tiempo. El detalle por dimensión le da al cliente una hoja de ruta accionable, no solo un número.
**Impacto:** El agente de diagnóstico de salud debe calcular las 6 dimensiones independientemente para cada entrega de datos. El resultado se vincula directamente con el SLA de precisión del pronóstico (ver DEC-009) y con el cargo adicional por complejidad de datos.

---

## DEC-014 — Esquema de datos: dos tablas complementarias
**Fecha:** 2026-06-08
**Decisión:** El sistema trabaja con dos esquemas de datos. Esquema 1 (obligatorio): historial de pedidos con 4 campos mínimos (fecha_pedido, id_cliente, id_producto, cantidad_solicitada) y 17 campos en el esquema ideal. Esquema 2 (opcional): producción e inventario de ABC con 6 campos (fecha, id_producto, cantidad_producida, stock_disponible, costo_unitario, stock_minimo) que habilitan análisis de agotados, desperdicios e impacto financiero.
**Razón:** El Esquema 1 cubre la demanda desde el lado del cliente XYZ. El Esquema 2 cubre la oferta desde el lado de ABC. Juntos permiten cerrar el ciclo completo: demanda real vs. producción real vs. inventario disponible.
**Impacto:** El pipeline de ingesta debe manejar dos fuentes de datos con estructuras distintas. Los campos faltantes del esquema ideal se reflejan en el índice de salud de datos. Los cálculos de agotado y desperdicio requieren cruzar ambos esquemas.

---

## DEC-013 — Historial mínimo y estrategia cold start
**Fecha:** 2026-06-08
**Decisión:** Historial mínimo recomendado: 2 años. Ideal: 3 años. El nivel de confianza del pronóstico se ajusta según el historial disponible por combinación cliente × producto (alta / estándar / reducida / experimental). Para productos sin historial se aplica una cascada: (1) analogía por categoría, (2) analogía por cliente, (3) acumulación de 3 meses antes de pronosticar. El dashboard muestra siempre el nivel de confianza y el modo de arranque activo.
**Razón:** No todos los productos tienen el mismo historial. Imponer un mínimo rígido excluiría productos válidos. La cascada de cold start permite pronosticar incluso productos nuevos, siendo transparente sobre la confianza del resultado.
**Impacto:** El motor de pronóstico debe evaluar el historial disponible por combinación cliente × producto antes de seleccionar el modelo. El dashboard debe comunicar el nivel de confianza junto a cada pronóstico.

---

## DEC-012 — Modos de ingesta de datos: Batch e Incremental
**Fecha:** 2026-06-08
**Decisión:** El sistema soporta dos modos de entrega de datos coexistentes. Modo 1 (Batch): el cliente entrega un archivo histórico completo una sola vez. Modo 2 (Incremental): el cliente actualiza sus datos periódicamente (diario o semanal) y el sistema incorpora solo los registros nuevos con deduplicación automática. En ambos modos el pronóstico se entrega mensualmente. En Modo 2 el modelo se reentrena semanalmente. No se acepta correo electrónico como fuente de datos.
**Razón:** La realidad de las empresas manufactureras es heterogénea — algunas tienen datos históricos estáticos y otras actualizan sus sistemas continuamente. El sistema debe adaptarse a ambas sin imponer una forma única de trabajo.
**Impacto:** El pipeline de ingesta debe detectar el modo de operación de cada cliente y gestionar deduplicación por clave (fecha, cliente, producto) en el Modo Incremental. El scheduler de reentrenamiento de modelos debe operar de forma independiente a la frecuencia de entrega de datos.

---

## DEC-023 — KPIs internos de Triple S
**Fecha:** 2026-06-08
**Decisión:** Triple S mide la salud del negocio con seis KPIs internos: (1) Tasa de conversión onboarding → activo, (2) Tiempo promedio de primer pronóstico, (3) Tasa de retención mensual (churn), (4) Evolución promedio del ISD por cohorte (a mes 1, 3 y 6), (5) MAPE real vs. comprometido, (6) Distribución de clientes por plan (mensual / trimestral / anual).
**Razón:** Los SLAs son compromisos con el cliente. Los KPIs internos son la señal temprana que permite a Triple S detectar problemas antes que el cliente los note — especialmente la deriva del MAPE y el churn.
**Impacto:** El portal interno de Triple S (Streamlit) debe mostrar estos KPIs de forma agregada. El harness debe registrar los eventos que los alimentan: fecha de primer pronóstico, renovaciones, cancelaciones, MAPE calculado por ciclo.

---

## DEC-022 — Roles de usuario del dashboard y nivel de explicabilidad
**Fecha:** 2026-06-08
**Decisión:** Cinco roles de usuario: planificador de demanda (principal, uso diario), jefe de compras (semanal), gerente de producción (mensual), gerente de supply chain (mensual), directivo (ocasional). El nivel de explicabilidad del pronóstico es intermedio — interpretable pero no técnico: número + nivel de confianza + tendencia reciente + evento activo si existe + anomalía reciente si existe. No se muestran coeficientes ni parámetros del modelo.
**Razón:** El cliente no es un equipo técnico — el dashboard está diseñado para consumo sin capacitación. El nivel de explicabilidad es suficiente para actuar con confianza sin requerir entender el modelo. El patrón de presentación es el mismo ya establecido para el ISD: número global + causa principal + acción sugerida.
**Impacto:** El dashboard requiere vistas diferenciadas por rol — el planificador necesita detalle SKU, el directivo necesita agregados con alertas. El pipeline de pronóstico debe generar, además del número, los metadatos de explicabilidad: nivel de confianza, tendencia, eventos activos y anomalías recientes.

---

## DEC-011 — Unidad mínima de análisis: cliente × producto
**Fecha:** 2026-06-08
**Decisión:** La frecuencia de pedido y el tiempo de entrega son propiedades de cada combinación cliente × producto, no del cliente ni del producto por separado. El sistema trata cada combinación de forma independiente.
**Razón:** En la realidad B2B un mismo cliente puede pedir PRD1 cada 3 meses y PRD2 mensualmente. Asumir un ciclo estándar produciría pronósticos incorrectos.
**Impacto:** El modelo de datos y los agentes de pronóstico deben operar a nivel de combinación cliente × producto, no a nivel de cliente o producto individual.

---

## DEC-024 — Arquitectura de harnesses operacionales del producto
**Fecha:** 2026-06-08
**Decisión:** El sistema Harness Forecaster se divide en 11 harnesses operacionales, numerados de 010 a 060 en incrementos de 5:

| # | Nombre | Responsabilidad | Tipo |
|---|--------|----------------|------|
| 010 | Discovery | Contexto del cliente, criterios de éxito, configuración de onboarding | Semi-humano |
| 015 | Intake | Recepción y validación de datos, copia Bronze | Pipeline |
| 020 | Diagnosis | Cálculo del ISD desde Bronze (6 dimensiones) | Pipeline |
| 025 | Refinery | Limpieza Bronze→Silver→Gold + extracción de maestros | Pipeline |
| 030 | Trainer | Feature engineering (sub-proceso interno) + entrenamiento de modelos | Pipeline |
| 035 | Predictor | Inferencia mensual + detección y clasificación de anomalías | Pipeline |
| 040 | Publisher | Dashboard + correo automático + exportable | Pipeline |
| 045 | Monitor | MAPE real vs. comprometido, deriva de modelos, salud del pipeline | Pipeline |
| 050 | Lifecycle | Ciclo de vida del cliente, pagos, alertas, suspensión | Event-driven |
| 055 | Command | Operaciones internas Triple S, 6 KPIs | Event-driven |
| 060 | Simulator | Escenarios what-if predefinidos | On-demand |

Tres decisiones de diseño clave:
1. **020 Diagnosis corre en PARALELO con 025 Refinery** — ambos leen desde Bronze. El diagnóstico sobre datos limpios invalidaría la medición real de la salud.
2. **Detección de anomalías vive dentro de 035 Predictor** — son conceptualmente inseparables: la anomalía se detecta en el contexto del modelo de demanda.
3. **Feature engineering es sub-proceso interno de 030 Trainer** — comparten estado (el pipeline de transformación ajustado forma parte del artefacto del modelo).

Cadena de dependencias del pipeline principal:
```
015 → { 020 ∥ 025 } → 030 → 035 → 040
```

**Razón:** La separación de concerns es clara y cada harness tiene una sola responsabilidad. El paralelismo 020/025 garantiza que el ISD mide el estado real de los datos originales. Los harnesses event-driven (050, 055) y on-demand (060) son transversales al pipeline.
**Impacto:** Toda nueva funcionalidad debe asignarse al harness correspondiente antes de implementarse. La numeración en incrementos de 5 permite insertar harnesses intermedios sin renumerar si el diseño evoluciona.

---

## DEC-026 — Orden de construcción de los harnesses operacionales
**Fecha:** 2026-06-08
**Decisión:** Los 11 harnesses se construyen en el siguiente orden, agrupados en 5 bloques por valor entregable:

| Posición | Harness | Bloque | Razón |
|----------|---------|--------|-------|
| 1 | 010 Discovery | A | Sin dependencias técnicas — plantilla en días |
| 2 | 015 Intake | A | Fundación técnica de todo el sistema |
| 3 | 020 Diagnosis | A | Primer entregable ejecutable con datos reales (ISD) |
| 4 | 050 Lifecycle | C | Independiente del pipeline — construir antes del primer pago |
| 5 | 025 Refinery | B | Produce capa Gold, insumo obligatorio del Trainer |
| 6 | 030 Trainer | B | Motor ML — mayor riesgo técnico del sistema |
| 7 | 035 Predictor | B | Primer número de pronóstico generado |
| 8 | 040 Publisher | B | Cierra el ciclo de valor: entrega al cliente |
| 9 | 045 Monitor | D | Solo tiene sentido con pronósticos reales que monitorear |
| 10 | 055 Command | D | Requiere eventos de todos los demás para calcular KPIs |
| 11 | 060 Simulator | E | Funcionalidad avanzada, depende de 030 Trainer |

**Hitos por bloque:**
- **Hito A** (bloques 1–3): primer piloto ejecutable — recibir datos y entregar diagnóstico ISD
- **Hito C** (bloque 4): listo para cobrar — gestión de pagos y estados operativa
- **Hito B** (bloques 5–8): ciclo de valor completo — primer pronóstico entregado al cliente
- **Hito D** (bloques 9–10): excelencia operativa — monitoreo y KPIs internos activos
- **Hito E** (bloque 11): funcionalidad avanzada — escenarios what-if disponibles

**050 Lifecycle** va en posición 4 (no al final) porque no tiene dependencias técnicas del pipeline de datos y debe estar operativo antes de que el primer cliente pase de onboarding a activo con pago. No va primero porque construir un sistema de cobro sin un producto ejecutable no genera retroalimentación útil.

**Razón:** El orden maximiza el valor entregable en cada etapa. Bloque A valida el pipeline de datos sin ML. Bloque B valida el core del producto. 050 se inserta entre A y B porque el mes 1 gratuito da el margen de tiempo necesario.
**Impacto:** El diseño detallado de cada harness sigue este orden. No se inicia el diseño del siguiente bloque hasta que el anterior tiene su Sprint Contract aprobado.

---

## DEC-027 — Convención de nombres para archivos de brief
**Fecha:** 2026-06-08
**Decisión:** Los archivos de la carpeta `brief/` se nombran `{NNN}_{nombre}.md` — sin el sufijo `_harness`. Ejemplo: `010_discovery.md`, `015_intake.md`. El sufijo `_harness` era redundante porque todos los archivos en esa carpeta son briefs de harnesses.
**Razón:** Nombres más cortos y legibles. La carpeta `brief/` ya provee el contexto suficiente.
**Impacto:** Aplica a todos los briefs del proyecto. El brief ya creado (`010_discovery.md`) sigue esta convención.

---

## DEC-028 — Estructura de carpetas numeradas dentro de cada harness
**Fecha:** 2026-06-08
**Decisión:** Los artefactos del sistema dentro de cada harness se organizan en carpetas con prefijo numérico `6XX` para separarlos visualmente de los artefactos de trabajo (`0XX`):

| Carpeta | Contenido | Escritor |
|---------|-----------|---------|
| `{NNN}_{nombre}/` | Artefactos de trabajo propios del harness (session_data.json, analysis_report.json, etc.) | Workers del harness |
| `600_persistence/` | Archivos de estado: `harness-state.json` (A), `execution-state.json` (B), `claude-progress.txt` (activo) | A, B, orquestador activo |
| `605_eval/` | Resultados de auditoría: `verdict.json`, `metrics_summary.json` | Solo C |
| `610_knowledge/` | Memoria a largo plazo: `lessons_learned.md`, `decisions_library.md` | C (hallazgos), A (consolida) |
| `615_changes/` | Gestión de cambios: `CR_XXXX_Descripcion.md` | B |

**Razón:** Los prefijos numéricos agrupan visualmente las carpetas de infraestructura al final del directorio (600+), separándolas de las carpetas de trabajo de cada harness (010, 015, etc.). Hace obvio de un vistazo qué es artefacto de dominio y qué es infraestructura del harness.
**Impacto:** Esta convención aplica a todos los harnesses del sistema. El brief `010_discovery.md` ya refleja esta estructura.

---

## DEC-029 — Nombre del sistema: FARO
**Fecha:** 2026-06-08
**Decisión:** El sistema se llama **FARO** — **F**orecasting **A**gentic **R**esults & **O**perations. Este nombre se usa en toda comunicación interna de Triple S y en materiales comerciales del producto.
**Razón:** El acrónimo describe con precisión qué hace el sistema (pronosticar, con agentes, entregando resultados operacionales). La palabra "faro" en español añade una metáfora directa al problema que resuelve: guiar a los fabricantes en la incertidumbre de la demanda, igual que un faro guía a los barcos. Funciona de forma natural en español e inglés.
**Impacto:** Todo agente, documento, brief y comunicación debe referirse al sistema como FARO. El nombre del repositorio y el directorio de trabajo permanecen como `Harness_Forecaster` (nombre técnico de la carpeta) pero el nombre de producto es FARO.

---

## DEC-030 — Arquitectura de agentes del harness 010: governor spawna workers vía CLI
**Fecha:** 2026-06-08
**Decisión:** El governor (Instancia A) es el único que spawna workers, usando el CLI de Claude Code (`claude --agent <nombre> --print --dangerously-skip-permissions`). El orchestrator (Instancia B) es un gestor de estado puro con tres modos: PLAN (persistir orchestration_plan), CHECKPOINT (registrar avance de un worker) y WORKER_FAILED (registrar error). El orchestrator no toma decisiones ni spawna nada.
**Razón:** Separación estricta de responsabilidades: A decide qué hacer, B registra qué pasó. Patrón validado en harnesses anteriores (carpeta Temporal). Evita que B tome decisiones estratégicas que le corresponden a A.
**Impacto:** Aplica a todos los harnesses del sistema. El governor de cada harness tiene modos explícitos (INIT, EXECUTE, POST_CPxx, CLOSE, SUSPEND). El orchestrator de cada harness tiene solo PLAN/CHECKPOINT/WORKER_FAILED.

---

## DEC-031 — Skills como directorios con SKILL.md — son schemas de referencia
**Fecha:** 2026-06-08
**Decisión:** Cada skill es un directorio bajo `.claude/skills/` con un archivo `SKILL.md` dentro. Las skills son documentos de referencia (schemas, formatos, reglas de escritura) que los agentes cargan como contexto. No son procedimientos. El `deploy-harness.ps1` copia los directorios de skills con prefijo `discovery-*` al proyecto cliente.
**Razón:** Patrón del Temporal. Separar el "qué estructura tiene este artefacto" (skill) del "cómo procesar ese artefacto" (agente). Permite actualizar schemas sin tocar la lógica de los agentes.
**Impacto:** Al crear una skill, siempre crear el directorio primero. Un agente puede declarar múltiples skills en su frontmatter. Las skills no tienen lógica de ejecución — solo definiciones.

---

## DEC-032 — Estructura de carpetas fuente para scripts y templates de harness
**Fecha:** 2026-06-08
**Decisión:** Los artefactos de soporte de cada harness (scripts Python, plantillas Markdown) se organizan en dos carpetas en el repositorio raíz:
- `scripts/{NNN}_{nombre}/` → scripts de cálculo y lógica de soporte (ej: `ito_calculator.py`)
- `templates/{NNN}_{nombre}/` → plantillas que el configurator personaliza por cliente

El `deploy-harness.ps1` copia automáticamente ambas carpetas al proyecto cliente:
- Scripts → `{destino}/{NNN}_{nombre}/` (raíz de la carpeta de trabajo del harness)
- `session_template.md` → `{destino}/{NNN}_{nombre}/` (raíz, acceso directo para el interviewer)
- Resto de templates → `{destino}/{NNN}_{nombre}/templates/` (subcarpeta para el configurator)

**Razón:** Separar artefactos reutilizables (repositorio) de artefactos de ejecución (proyecto cliente). El patrón es genérico — al agregar scripts o templates para harnesses futuros solo se crean las carpetas correspondientes; el deploy los levanta sin modificaciones.
**Impacto:** Al crear herramientas de soporte para harnesses 015 en adelante, seguir esta misma convención. El deploy ya está preparado para manejarlos automáticamente.

---

## DEC-033 — Archivos workflows como guías de navegación livianas para el CLAUDE.md
**Fecha:** 2026-06-09
**Decisión:** Los archivos `.claude/workflows/ciclo_0XX_*.md` se crean como **guías de navegación livianas** (~80 líneas) que le indican a Claude Code cómo invocar al governor y cómo responder a cada `GOVERNOR_RESULT` status. No extraen lógica del governor ni la duplican. El governor permanece autocontenido. El deploy script copia `templates/workflows/*.md` a `.claude/workflows/` junto con cada harness.
**Razón:** El `client-project-CLAUDE.md` ya referenciaba estos archivos. La alternativa de eliminar las referencias le quitaba al CLAUDE.md la capacidad de delegar el "cómo" de cada ciclo sin mantener lógica inline. Crear los workflows como guías livianas resuelve ambos problemas: las referencias son válidas y el CLAUDE.md se mantiene limpio.
**Impacto:** Al cerrar cada harness futuro, crear `templates/workflows/ciclo_0XX_nombre.md` con la tabla de modos y GOVERNOR_RESULT statuses antes de marcar el harness como listo. El deploy los levanta automáticamente.

---

## DEC-034 — default_stacks.md descartado: el stack tecnológico vive en los agentes
**Fecha:** 2026-06-09
**Decisión:** El archivo `templates/default_stacks.md` (que se deployaría a la raíz del proyecto cliente) fue descartado. La sección correspondiente fue eliminada de `deploy-harness.ps1`. El stack tecnológico de FARO (DEC-020) está embebido directamente en las instrucciones de los agentes que lo necesitan.
**Razón:** El archivo no agregaría valor porque: (1) los agentes especializados ya conocen su stack, (2) Claude Code en el proyecto cliente no debería tomar decisiones de arquitectura — eso es responsabilidad de los governors, (3) crearía deuda de mantenimiento cada vez que el stack evolucione.
**Impacto:** No crear archivos de referencia de stack en proyectos cliente. Si un agente futuro necesita contexto del stack, incluirlo en sus instrucciones o en el CLAUDE.md del cliente de forma puntual.

---

## DEC-035 — Rediseño del discovery-interviewer: entrevista directa a stakeholders del cliente
**Fecha:** 2026-06-09
**Decisión:** El `discovery-interviewer` entrevista directamente a los stakeholders del cliente, no al operador de Triple S. Recibe un archivo `inputs/brief.md` al inicio con contexto de alto nivel del proyecto y los stakeholders identificados inicialmente. Opera con tres roles base: negocio (problema, objetivos, criterios de éxito), técnico (datos, sistemas, calidad), usuario (quién usa los pronósticos, para qué decisiones, en qué formato). Un stakeholder puede tener uno, dos o los tres roles. Las preguntas se adaptan al rol asignado. Al final de cada entrevista activa el mecanismo snowball: pregunta explícitamente si hay otras personas cuya perspectiva sea importante y las agrega a la cola. El harness termina cuando no quedan stakeholders pendientes.
**Razón:** El diseño anterior convertía la sesión de descubrimiento en un formulario guiado por campos, perdiendo el valor real de un discovery: entender el problema desde múltiples perspectivas, detectar contradicciones entre stakeholders y capturar contexto cualitativo que no cabe en campos estructurados.
**Impacto:** El interviewer produce `session_notes.json` (notas por stakeholder) y `stakeholder_map.json` (quién es, qué rol, síntesis de su perspectiva). El `session_data.json` se deriva de estos artefactos, no se llena directamente durante la entrevista. El flujo del governor y la cadena de workers deben actualizarse (ver T-101, T-109).

---

## DEC-036 — Nuevo agente: discovery-synthesizer
**Fecha:** 2026-06-09
**Decisión:** Se agrega un nuevo agente `discovery-synthesizer` a la cadena del harness 010, entre el interviewer y el analyst. Su única responsabilidad es cross-referenciar todas las entrevistas, detectar contradicciones entre stakeholders (ej: negocio dice "3 años de datos", técnico dice "el ERP lleva 8 meses"), identificar vacíos que ninguna persona cubrió, y generar `open_questions.json` con las brechas categorizadas en tres niveles: bloqueantes (sin esto no se puede configurar), importantes (impactan calidad del pronóstico) y registrables (información útil pero no crítica). Si hay preguntas bloqueantes, el governor retorna al interviewer para una segunda ronda acotada con stakeholders específicos. No es responsabilidad del analyst hacer esta síntesis — el analyst solo calcula ITO y cold start sobre datos ya consolidados.
**Razón:** La detección de vacíos y contradicciones es semántica, no estructural — no la puede hacer una validación de schema. Requiere un agente con el cuadro completo de todas las entrevistas. Separar síntesis (synthesizer) de cálculo (analyst) mantiene cada agente con una sola responsabilidad.
**Impacto:** La cadena de workers del 010 pasa de tres pasos (interviewer → analyst → configurator) a cuatro (interviewer → synthesizer → analyst → configurator). El governor debe actualizarse para invocar el synthesizer y manejar el caso de segunda ronda. Ver T-103, T-104, T-109.

---

## DEC-037 — Carpeta 800_inputs/ en la raíz del proyecto cliente para artefactos de entrada humana
**Fecha:** 2026-06-09 (renombrada de `inputs/` a `800_inputs/` — 2026-06-09)
**Decisión:** Los archivos que el operador de Triple S escribe antes de lanzar un harness (como el `brief.md` del 010) viven en la carpeta `800_inputs/` en la raíz del proyecto cliente. El prefijo `800_` la ubica visualmente al final de la estructura de carpetas numeradas, separada de los artefactos del sistema. Esta carpeta es de solo lectura para los agentes — nunca la modifican. El deploy del harness 010 crea la carpeta `800_inputs/` y deposita la plantilla `brief_template.md` para que el operador la complete.
**Razón:** Separar las entradas humanas de los artefactos generados por el sistema. El prefijo numérico mantiene consistencia con la convención de carpetas del proyecto (600_persistence, 605_eval, 610_knowledge) y la ubica al final, fuera del flujo numerado de los harnesses.
**Impacto:** El `discovery-interviewer` lee `800_inputs/brief.md` al inicio. El deploy debe crear `800_inputs/` y copiar la plantilla. Ver T-107, T-108.

---

## DEC-039 — Skills del synthesizer renombradas a prefijo discovery-*
**Fecha:** 2026-06-09
**Decisión:** Las skills `synthesis-report-schema` y `open-questions-schema` se renombraron a `discovery-synthesis-schema` y `discovery-open-questions` respectivamente.
**Razón:** El script `deploy-harness.ps1` copia skills usando el filtro `"discovery-*"`. Las skills sin ese prefijo nunca llegaban al proyecto cliente, por lo que el synthesizer no podía cargarlas al ejecutarse.
**Impacto:** Directorios renombrados en `.claude/skills/`, frontmatter `name:` actualizado en cada SKILL.md, referencias en `discovery-synthesizer.md` actualizadas.

---

## DEC-038 — Guardado incremental por bloque en discovery-interviewer + comando /faro-save de emergencia
**Fecha:** 2026-06-09
**Decisión:** El `discovery-interviewer` guarda en `session_notes.json` al completar cada bloque de preguntas (negocio, técnico, usuario), no al finalizar toda la sesión. Adicionalmente, existe el comando `/faro-save` que el operador puede ejecutar en cualquier momento para forzar un guardado del estado parcial de la entrevista en curso.
**Razón:** Una sesión completa con tres roles puede durar 30–50 intercambios. Si la sesión de Claude Code se interrumpe antes de terminar, se pierde todo lo conversado. El guardado por bloque reduce la pérdida máxima a un solo bloque incompleto (~10 intercambios). El comando `/faro-save` cubre interrupciones dentro de un bloque.
**Impacto:** El interviewer debe guardar un estado parcial después de cada bloque completado, incluso si la sesión continúa. `session_notes.json` crece de forma incremental. Requiere T-111 (modificar interviewer) y T-112 (crear comando /faro-save).

---

## DEC-056 — Estrategia de prueba automatizada del harness 010 Discovery
> *(Originalmente registrada como un segundo "DEC-039" duplicado; renumerada a DEC-056 en sesión 37 para resolver la colisión de ID. Sin referencias externas que actualizar.)*
**Fecha:** 2026-06-09
**Decisión:** La prueba automatizada del harness 010 simula los entregables del interviewer mediante fixtures JSON predefinidos (`session_notes.json` + `stakeholder_map.json` con datos de Alimentos Prueba S.A.) y ejecuta el resto del pipeline de forma completamente automática. Los gates CP-03 y CP-04 que requieren decisión humana se mantienen — el operador los revisa y aprueba como en producción real.
**Razón:** El interviewer es interactivo por diseño y no puede automatizarse sin cambiar su naturaleza. Los fixtures replican fielmente su salida para que synthesizer, analyst, configurator y evaluator corran sin modificaciones. Mantener CP-03 y CP-04 manuales permite verificar que los borradores generados son coherentes con los datos de prueba.
**Impacto:** T-092 (prueba de humo) requiere: (1) crear fixtures JSON para Alimentos Prueba S.A., (2) lanzar el harness con `interviewer_complete: true`, (3) aprobar manualmente CP-03 y CP-04, (4) verificar veredicto APPROVED del evaluator.

---

## DEC-040 — Estrategia de validación del harness 010 en tres fases secuenciales
**Fecha:** 2026-06-09
**Decisión:** El harness 010 se valida en tres fases antes de usarse con clientes reales: (1) Prueba automatizada — fixtures JSON simulan la salida del interviewer, se ejecuta la cadena técnica completa, CP-03 y CP-04 se aprueban manualmente; (2) Prueba de humo — el operador conduce una entrevista real con un cliente ficticio (Alimentos Prueba S.A.) end-to-end; (3) Piloto real — primer cliente manufacturero real con datos reales.
**Razón:** Cada fase valida una capa distinta del sistema. La prueba automatizada detecta bugs técnicos sin involucrar a nadie. La prueba de humo valida la experiencia del interviewer y el guardado incremental. El piloto real valida la calidad del servicio completo. Si algo falla en una fase, se corrige antes de avanzar a la siguiente — nunca se lleva un bug técnico a un cliente real.
**Impacto:** No se ejecuta el piloto real hasta que las dos pruebas previas estén aprobadas. El orden es estrictamente secuencial: automatizada → humo → piloto.

---

## DEC-041 — Sprint Contract persiste en 700_contract/sc_010_discovery.md
**Fecha:** 2026-06-09
**Decisión:** El Sprint Contract del harness 010 se escribe en `700_contract/sc_010_discovery.md` con un encabezado de estado (`ESTADO: BORRADOR` o `ESTADO: APROBADO`). El `harness-state.json` almacena solo el path y el estado, no el contenido. Al aprobar el contrato, el governor reescribe el encabezado a APROBADO con timestamp.
**Razón:** Tener el contrato en un archivo independiente permite que el operador lo lea y revise directamente sin parsear JSON. Separar el contenido del estado también simplifica harness-state.json y evita que el JSON crezca con texto largo.
**Impacto:** La carpeta `700_contract/` se crea en E10-A y en el deploy script. Para harnesses futuros, el sprint contract seguirá la convención `sc_{NNN}_{nombre}.md`. El orchestrator recibe la referencia al archivo, no el contenido inline.

---

## DEC-042 — Estructura de subcarpetas dentro de 010_discovery/: deliverables/ y support/
**Fecha:** 2026-06-10
**Decisión:** Los artefactos de la carpeta `010_discovery/` se reorganizan en dos subcarpetas:
- `010_discovery/deliverables/` → artefactos finales del harness: `client_profile.json`, `onboarding_config.json`, `data_intake_guide.md`
- `010_discovery/support/` → artefactos de trabajo interno: `session_notes.json`, `stakeholder_map.json`, `synthesis_report.json`, `open_questions.json`, `session_data.json`, `analysis_report.json`
- `010_discovery/db_records/` y `010_discovery/storage_local/` → se quedan donde están (simulaciones de Fase 1 de Supabase — desaparecen en Fase 3)
- `pending_email.json` (antes `correo_pendiente.json`) → se mueve a `600_persistence/` — es una nota operativa de Fase 1, no un artefacto del harness
**Razón:** La separación hace inmediatamente evidente qué produce el harness (deliverables/) vs qué usó internamente (support/). Reduce ambigüedad para el operador al revisar la carpeta del proyecto cliente.
**Impacto:** Requiere actualizar rutas en `discovery-configurator.md`, `discovery-analyst.md`, `discovery-evaluator.md`, `discovery-governor.md` y `deploy-harness.ps1`. Ver T-120 a T-124.

---

## DEC-043 — `correo_pendiente.json` se renombra a `pending_email.json` y vive en 600_persistence/
**Fecha:** 2026-06-10
**Decisión:** El archivo que registra el correo pendiente de enviar en Fase 1 se renombra de `correo_pendiente.json` a `pending_email.json` (convención: nombres de archivo en inglés, per CLAUDE.md) y se reubica en `600_persistence/` en lugar de `010_discovery/`.
**Razón:** (1) El CLAUDE.md del proyecto establece que los nombres de archivo deben estar en inglés — `correo_pendiente` es un bug de convención. (2) El archivo es una nota operativa de Fase 1 que desaparece cuando SendGrid esté integrado — no es un artefacto del harness sino infraestructura de soporte de fase. Su lugar natural es junto a los otros archivos de persistencia operativa.
**Impacto:** Actualizar `discovery-configurator.md` y `discovery-evaluator.md` (que verifica su existencia en D6). Ver T-121.

---

## DEC-044 — Convención de nombres para carpetas de datos y salidas en el proyecto cliente
**Fecha:** 2026-06-09
**Decisión:** Las carpetas de datos y salidas que el configurator crea en la raíz del proyecto cliente pasan de nombres planos a nombres numerados con prefijo:
- `bronze/` → `1000_data/005_bronze/`
- `silver/` → `1000_data/007_silver/`
- `gold/` → `1000_data/009_gold/`
- `models/` → `1010_models/`
- `forecasts/` → `1020_forecasts/`
- `exports/` → `1030_exports/`
**Razón:** Los nombres planos no comunican el rol ni el orden de cada carpeta. Los prefijos numéricos ubican visualmente cada carpeta en la secuencia de procesamiento (datos → modelos → pronósticos → exportables), son consistentes con la convención ya establecida para las carpetas del harness (`600_persistence/`, `610_knowledge/`, `800_inputs/`, etc.) y agrupan las tres capas medallón bajo un directorio padre `1000_data/` para dejar clara su relación.
**Impacto:** Requiere actualizar en `discovery-configurator.md` las rutas de creación del `storage_local`. Para los harnesses siguientes (015, 025, 030, 035, 040, 050), todas las rutas de lectura/escritura de datos deben usar las nuevas convenciones. Ver T-128.

---

## DEC-045 — Interviewer presenta todas las preguntas del bloque de una vez
**Fecha:** 2026-06-10
**Decisión:** El `discovery-interviewer` presenta todas las preguntas de cada bloque (negocio, técnico, usuario) juntas en un solo mensaje numerado. El operador responde todas de una vez. Al recibir las respuestas, el interviewer guarda `session_notes.json` inmediatamente antes de pasar al siguiente bloque.
**Razón:** El modelo conversacional (una pregunta a la vez) generaba dos problemas: (1) acumulaba muchos intercambios antes de guardar, aumentando el riesgo de pérdida si la sesión se interrumpía a mitad del bloque; (2) era más lento para operadores que ya conocen al cliente y pueden responder todo el bloque de una vez.
**Impacto:** El guardado ahora ocurre tan pronto como llegan las respuestas del bloque completo, no al finalizar toda la sesión del stakeholder. El `/faro-save` sigue siendo útil como emergencia pero el riesgo de pérdida es mucho menor. Ver T-133.

---

## DEC-046 — Estrategia de deploy en modo dev: junctions en lugar de copias
**Fecha:** 2026-06-10
**Decisión:** Se agregará un parámetro `-Dev` al `deploy-harness.ps1`. En modo dev, en lugar de copiar `.claude/agents/`, `.claude/skills/` y `.claude/commands/` al proyecto destino, se crean junctions que apuntan directamente al repositorio `Harness_Forecaster`. Cualquier cambio en el código fuente es visible al instante en el proyecto de prueba sin re-deploy. En modo producción (sin `-Dev`), el comportamiento sigue siendo copia aislada.
**Razón:** El ciclo actual (editar → re-deploy → probar) interrumpe el flujo de desarrollo. La solución ya existía para los commands globales vía `faro-setup.ps1` (junction `~/.claude/commands/` → repo). DEC-046 extiende el mismo patrón a agents y skills a nivel de proyecto. El modo producción sigue siendo copias para garantizar aislamiento y versioning por proyecto cliente.
**Impacto:** Solo se usa `-Dev` en proyectos de prueba internos de Triple S. Nunca en proyectos de clientes reales. Ver T-135.

---

## DEC-047 — El governor genera el tenant_id; todos los workers lo leen de harness-state.json
**Fecha:** 2026-06-10
**Decisión:** El `tenant_id` se genera una sola vez: en el governor durante la construcción del Sprint Contract (E10-A), derivándolo de la razón social del brief. Se persiste inmediatamente en `harness-state.json["tenant_id"]`. Todos los workers downstream (analyst, configurator y cualquier agente futuro) leen el `tenant_id` de `harness-state.json` — nunca lo generan, infieren ni derivan de forma autónoma.
**Razón:** En Test_002B, el analyst generó `"laboratorios-vita-001"` mientras el resto del sistema usaba `"laboratorios-vita-s-a-de-c-v-2502"`, causando un hallazgo GLOBAL en la primera evaluación. El configurator también generaba su propio tenant_id en DRAFT, con riesgo de divergencia si el timestamp cambiaba entre ejecuciones. La fuente única de verdad elimina cualquier posibilidad de inconsistencia entre artefactos.
**Impacto:** `discovery-governor.md` genera y persiste el tenant_id al construir el Sprint Contract. `discovery-analyst.md` tiene Paso 2 explícito que lee harness-state.json y bloquea si el campo está vacío. `discovery-configurator.md` DRAFT Paso 3 lee harness-state.json en lugar de generar. Ver T-136.
**Actualización (sesión 33):** el rewrite del governor al modelo conductor (T-166a) había **perdido** la generación del tenant_id en E10-A, reintroduciendo la divergencia en Test_004A (`prolimex-mx` en governor vs `prolimex-s-a-de-c-v-4528` en deliverables). Restaurada en **T-167** (nuevo Paso C en la Construcción del Sprint Contract, idempotente). Además se descubrió que el configurator nunca había recibido el fix de T-136 (o se perdió en T-149) y seguía generando su propio tenant_id con `$slug-$ts` — corregido en **T-168** (ahora lee de harness-state.json como el analyst). DEC-047 sigue siendo la regla; estos dos fixes la hacen cumplir en todo el pipeline.

---

## DEC-048 — Nueva arquitectura de instalación: todo a nivel de proyecto (sesión 23)
**Fecha:** 2026-06-10
**Decisión:** Se elimina completamente la instalación a nivel de máquina/usuario. Todo se instala por proyecto. El flujo es:
1. `faro-setup` (alias PowerShell) → ejecuta `Harness_Forecaster/faro-setup.ps1` desde la carpeta del proyecto → instala `.claude/` (agentes, skills, comandos, workflows), `CLAUDE.md`, `settings.json`, `settings.local.json` (con `FARO_HOME`), y `800_inputs/brief.md`
2. `/faro-init` (Claude Code) → crea carpetas de runtime + copia archivos de soporte de `010_discovery/` usando `$env:FARO_HOME`
3. `/faro-discovery` (Claude Code) → arranca el governor en INIT

`deploy-harness.ps1` e `install.ps1` quedan como scripts legacy — ya no son parte del flujo principal.
**Razón:** Los agentes y skills instalados globalmente (vía junctions) se cargaban en todas las sesiones de Claude Code, consumiendo contexto innecesario. El modelo correcto es que cada proyecto tenga su propio `.claude/` completo.
**Impacto:** `faro-setup.ps1` reescrito desde cero. `faro-init.md` actualizado. Junction global `~/.claude/commands/` eliminada. `FARO_HOME` inyectado en `settings.local.json` para que el governor y `/faro-init` sepan dónde está el repo. Ver T-151 a T-154.

---

## DEC-049 — El interviewer arranca con un turno de setup que produce sus dos artefactos antes de cualquier pregunta (sesión 28)
**Fecha:** 2026-06-11
**Decisión:** La sección "Al iniciar" del `discovery-interviewer` se reestructura en un **turno de setup explícito**. El primer turno del agente: (1) lee el brief, (2) garantiza que `stakeholder_map.json` exista en disco — su PRIMER ENTREGABLE —, (3) garantiza que `session_notes.json` exista (array vacío `[]` si es nuevo), (4) muestra una confirmación visible al operador (`[FARO] Setup de entrevistas completado…`), y NO contiene ninguna pregunta de entrevista. La entrevista arranca recién en el turno siguiente. Un **GATE DE ARRANQUE** prohíbe presentar cualquier pregunta hasta que ambos archivos existan en disco. Adicionalmente, se elimina la skill `discovery-session-schema` del frontmatter del interviewer (pertenece al synthesizer) y se reformula el guardado por bloque en lenguaje positivo ("STOP — no generar texto adicional; escribir el archivo; confirmar; luego continuar") en lugar de prohibiciones fuertes.
**Razón:** En Test_003D/003E el interviewer conducía las entrevistas sin crear ninguno de sus dos archivos salvo orden explícita del operador. La causa raíz no era la fuerza del lenguaje sino que el agente corría hacia la entrevista (su tarea percibida) y trataba la escritura como trámite diferible. Separar el setup en su propio turno hace del archivo el entregable visible del turno, no un efecto secundario. Ver LEC-055, LEC-056, LEC-057.
**Impacto:** `discovery-interviewer.md` modificado en el repo fuente `Harness_Forecaster` (frontmatter + sección "Al iniciar" + sección de guardado por bloque + cierre de mapa). Validado en Test_004A: ambos artefactos se crearon sin intervención del operador, con alta calidad de captura. Contrasta con DEC-045 (preguntas por bloque) que sigue vigente. Reemplaza el enfoque fallido de T-157 (LEC-054).

---

## DEC-050 — Marcador no-checkpoint del tramo interactivo + campo governor_mode vivo en la capa de estado (sesión 29)
**Fecha:** 2026-06-11
**Decisión:** Dos cambios coordinados en la capa de estado del harness 010, derivados de LEC-058:

1. **Marcador del tramo interactivo (T-162).** El `discovery-orchestrator` gana un modo nuevo `[MODO: INTERVIEWER_DONE]` que escribe `interviewer_completed_at` (timestamp) + `interviewer_artifacts` (paths de `session_notes.json` y `stakeholder_map.json`) en `execution-state.json`, **sin avanzar `last_checkpoint`**. El governor lo invoca en el Paso 3c de EXECUTE, tras verificar los dos artefactos del interviewer y antes de pasar al synthesizer. Es un marcador de progreso, no un gate de reanudación, y respeta la Single Writer Rule (solo el orchestrator escribe `execution-state.json`). Es idempotente (una segunda ronda sobrescribe el timestamp).

2. **Campo `governor_mode` vivo (T-163).** Se agrega a `harness-state.json` un campo nuevo `governor_mode` (INIT/EXECUTE/POST_CP03/POST_CP04/CLOSE/SUSPEND) que el governor sincroniza al entrar a cada modo, mediante una regla central aplicada inmediatamente tras identificar el modo de invocación. Se conserva el campo `mode` (INICIO/CONTINUACIÓN) intacto, porque el orchestrator lo lee en Modo PLAN para distinguir inicio de reanudación.

**Razón:** Sin el marcador, `execution-state.json` quedaba congelado en `last_checkpoint: null` entre el fin de las entrevistas y la corrida del synthesizer — una reanudación desde ese archivo no sabría que las entrevistas ya ocurrieron. Sin `governor_mode`, el modo de alto nivel quedaba desactualizado (mostraba `INICIO` en plena ejecución EXECUTE). Se eligió un **campo nuevo** (`governor_mode`) en vez de repurposar `mode` para no romper la lectura del orchestrator, que ya depende de la semántica INICIO/CONTINUACIÓN. El nombre coincide con `suspension.governor_mode`, pero son distintos: uno es el modo vivo, el otro el destino de reanudación.
**Impacto:** Modificados `discovery-orchestrator.md` (nuevo modo + campos en el `orchestration_plan` del PLAN), `discovery-governor.md` (regla de sincronización + campo en init E10-A.3 + invocación en Paso 3c de EXECUTE + nota SUSPEND), `discovery-state-schema/SKILL.md` (ambos campos documentados con sus distinciones) y `flows/010_discovery_flow.md` (diagrama + sección de checkpoints). Pendiente de validar en la próxima prueba con el synthesizer. Ver T-162, T-163, LEC-058.

---

## DEC-051 — Modelo conductor: la sesión principal es el único spawner de agentes (sesión 31-32)
**Fecha:** 2026-06-11
**Decisión:** El harness 010 adopta el **modelo conductor**. Un subagente de Claude Code **no puede spawnear otros subagentes**; el governor y el orchestrator son subagentes, así que **ninguno spawnea**. El único componente que spawnea agentes es el **conductor** — la sesión principal en la que corre el comando `/faro-*`. El handshake es:
1. El conductor spawnea al governor en un modo (`INIT`/`EXECUTE`/`POST_CP03`/`POST_CP04`/…).
2. El governor re-deriva su posición leyendo los archivos de estado del disco y retorna **un solo** `GOVERNOR_RESULT`. Cuando hace falta un worker o el orchestrator, ese resultado es `WORKER_REQUIRED` u `ORCHESTRATOR_REQUIRED` con un bloque `dispatch` = `{ agent, prompt (literal), then }`.
3. El conductor spawnea al agente nombrado (herramienta `Agent`, `subagent_type = dispatch.agent`), espera, y verifica los artefactos en disco.
4. El conductor re-invoca al governor con `[MODO: dispatch.then]`. El ciclo se repite hasta un estado terminal.

**Excepción:** el `discovery-interviewer` (interactivo) corre **inline en la sesión principal**, no como subagente aislado. **Manejo de fallo:** si un artefacto esperado no existe tras un despacho, el conductor lo trata como `EXECUTION_FAILED` — nunca espera de forma indefinida.
**Razón:** El governor encadenaba a todos los workers abriendo sub-instancias `claude --print` en background y hacía polling del archivo de salida. En la reanudación de Test_004A el synthesizer así invocado quedó colgado ~19 min sin producir ningún artefacto (4 salidas CLI en 0 bytes), porque `--print` solo emite al terminar y, si la sub-instancia se cuelga, el governor espera indefinidamente. La causa raíz es que un subagente no puede spawnear subagentes — el mecanismo de spawn nunca fue confiable. Mover todo el spawning a la sesión principal (que sí puede usar la herramienta `Agent`) lo resuelve de raíz. Ver T-166, LEC-059.
**Impacto:** `discovery-governor.md` refactorizado a despachador de un solo paso (T-166a); bucle conductor en `templates/workflows/conductor_loop.md` + `faro-discovery.md`/`faro-restart.md`/`faro-continue.md` reescritos como conductores (T-166b); descripciones corregidas en `discovery-orchestrator.md` y `discovery-synthesizer.md` (T-166c); `flows/010_discovery_flow.md` (nueva sección "El modelo conductor" + tabla de actores con fila Conductor + arrows del diagrama + nota de lectura) y `discovery-state-schema/SKILL.md` (nota del modelo conductor + frases "governor spawnea X" reformuladas) actualizados (T-166d). **Validado e2e en T-166e (sesión 32):** Test_004A corrió de principio a fin sin colgarse, APPROVED 0.93, PHASE_COMPLETE.

---

## DEC-052 — El responsable de pagos se captura con una pregunta dirigida del interviewer en el bloque de negocio (sesión 33)
**Fecha:** 2026-06-11
**Decisión:** El campo `responsable_pagos` (nombre + correo de quien recibe los avisos de cobro/pago) se captura mediante una **pregunta dirigida y obligatoria** que el `discovery-interviewer` hace en el bloque de negocio (Bloque 5 — Plan de servicio de `preguntas_rol_negocio.md`), NO se deja que el synthesizer lo marque MISSING para una fase posterior. La pregunta distingue explícitamente al responsable de pagos de "quién aprueba el presupuesto / firma el contrato" — son roles que pueden recaer en personas distintas. Si el stakeholder no lo sabe, se registra como MISSING con nota.
**Razón:** En Test_004A se identificó a Eduardo Morales como aprobador de presupuesto, pero "quién recibe los avisos de cobro/pago" no se capturó, dejando `responsable_pagos` en MISSING y bajando D1 a 0.5. Es un campo obligatorio del schema del synthesizer y alimenta el ciclo de cobro de FARO (avisos de vencimiento, gracia, suspensión). Capturarlo dirigido en la entrevista es más confiable que esperar una segunda ronda. El operador eligió esta opción sobre dejarlo a una fase contractual posterior.
**Impacto:** `templates/010_discovery/preguntas_rol_negocio.md` (nueva pregunta en Bloque 5 + tabla de campos + checklist de cierre) y `discovery-interviewer.md` (nota de campos bloqueantes en Paso 6 menciona `responsable_pagos`). Las guías se copian al proyecto vía `faro-init` (T-156). Ver T-165.

---

## DEC-053 — Allowlist de permisos cubre la herramienta PowerShell (Opción A) (sesión 34)
**Fecha:** 2026-06-12
**Decisión:** El template `templates/client-project-settings.json` (que `faro-setup` instala como `.claude/settings.json` del proyecto) amplía su allowlist con patrones **`PowerShell(...)`** que cubren la plomería real del harness en Windows: `New-Item`, `Get-Content`, `Set-Content`, `Add-Content`, `Out-File`, `Test-Path`, `Get-ChildItem`, `Copy-Item`, `Move-Item`, `Remove-Item`, `Get-Date *`, `git *`, `python *`, `py *`. Se eligió la **Opción A (patrones específicos por comando)** sobre la Opción B (comodín `PowerShell(*)`/`Bash(*)`): cubre >95% de los prompts rutinarios conservando el guardarraíl por comando para algo inesperado.
**Razón:** En Test_005_Flexempaque el operador recibió numerosos prompts de permiso "¿Permitir este comando?" que NO son puntos de control del flujo. Causa raíz: la allowlist heredada tenía casi todas sus entradas en `Bash(...)`, pero en Windows el governor y los workers ejecutan los comandos vía la herramienta **PowerShell**, que no estaba allowlisteada → cada operación de archivos/estado pedía permiso. Esto NO toca los gates del harness (Sprint Contract, CP-03, CP-04, escalamiento, handoff), que permanecen como puntos de control humanos legítimos — solo elimina la fricción de la plomería.
**Impacto:** Toda instalación nueva (incluida Test_006) nace sin el problema, pues `faro-setup` copia el template a proyectos donde `settings.json` aún no existe. Los proyectos ya instalados conservan su `settings.json` (no se sobreescribe) y requieren ajuste manual si se quiere el mismo comportamiento. Ver T-176, LEC-063.

---

## DEC-054 — Permisos por proyecto: bypassPermissions en el template de settings (sesión 36)
**Fecha:** 2026-06-12
**Decisión:** El template `templates/client-project-settings.json` (que `faro-setup` instala como `.claude/settings.json` del proyecto) añade `"defaultMode": "bypassPermissions"` dentro de `permissions`. Cada proyecto cliente FARO nace sin pedir confirmación para comandos de herramienta (Bash/PowerShell/Write/etc.) **dentro de su propia carpeta**. Se conserva la allowlist `allow` existente (DEC-053) como documentación de la plomería esperada, pero el `defaultMode` es lo que elimina los prompts. Es una decisión **a nivel de proyecto**, no global — no se toca `~/.claude/settings.json`.
**Razón:** En Test_006 el operador suspendió por la cantidad de prompts, varios marcados como "script block que puede ejecutar código arbitrario". La allowlist de DEC-053 no bastó porque (1) el harness emite `cd "..." && powershell -NoProfile -Command "<heredoc>"`, que no matchea los patrones por prefijo, y (2) las heurísticas de seguridad de comandos son barreras duras que ignoran la allowlist (LEC-064). El operador pidió explícitamente que el permiso quede puesto por proyecto, instalado por cada `faro-setup`. Se eligió **Opción A (bypass total por proyecto)** sobre atacar la causa raíz (reescribir cómo el harness emite comandos) por urgencia operativa; la causa raíz queda como mejora de fondo.
**Impacto:** Todo proyecto FARO nuevo nace sin prompts de herramienta. Los proyectos ya instalados conservan su `settings.json` (faro-setup no lo sobreescribe) y requieren añadir la línea a mano — se hizo manualmente en Test_006 para poder reanudar. **No afecta los gates Human-in-the-Loop** (aprobación de borradores DRAFT, Sprint Contract, CP-03/CP-04, escalamiento, handoff): viven en la lógica de los agentes y se siguen presentando en la conversación. Riesgo aceptado: dentro de la carpeta del proyecto se pierde la red de seguridad de último recurso ante un comando destructivo. Mejora de fondo pendiente: que los agentes usen `Write`/`Edit` y la herramienta `PowerShell` nativa en vez de heredocs incrustados por Bash. Ver DEC-053, LEC-064, T-182.

---

## DEC-055 — Cerrado el harness 010; el siguiente paso es construir el 015 Intake, con la persistencia Capa 1 acoplada a su diseño (sesión 37)
**Fecha:** 2026-06-12
**Decisión:** Con el harness 010 Discovery **validado end-to-end** (Test_006 APPROVED 1.0, sesión 37), se da por **cerrado** y el siguiente paso del proyecto es **construir el harness 015 Intake** (tarea T-060 = `brief/015_intake.md`, Plan de Construcción de 7 secciones siguiendo el patrón de `brief/010_discovery.md`). La **Capa 1 de persistencia** (esquema operacional Supabase: tenants/contacts/client_config/subscriptions/events + adaptador fallback) **se acopla al diseño del 015**, no se construye antes en aislamiento — el 015 es el primer consumidor real de `client_config`/`tenants`, así que diseñar el 015 define los requisitos reales de la Capa 1. Mientras tanto, los agentes siguen escribiendo JSON local con `_pendiente_supabase: true` (modo Fase 1, P-04), que es el fallback previsto y no genera retrabajo al conmutar. Los ajustes menores pendientes del 010 (T-172, T-178, T-179, T-180) y la validación de T-181 quedan **diferidos como NO bloqueantes**.
**Razón:** El operador eligió avanzar de harness en vez de seguir puliendo el 010 o construir persistencia en aislamiento. La guía `documents/supabase_persistence_guide.md` (D-A) ya recomendaba construir la Capa 1 "después de validar 010 e2e y antes/junto con el diseño del 015" — ambas condiciones se cumplen ahora. Avanzar al 015 mantiene el momentum sobre el handoff limpio que el 010 acaba de producir (`onboarding_config.json` + evento `onboarding_discovery_complete`), y deja que el diseño del consumidor (015) determine el detalle de la persistencia en vez de especularlo. Dos decisiones abiertas frenan parte del detalle de cobro de la Capa 1: T-031 (pasarela de pagos, D-B) y T-030 (pesos del ITO, D-F).
**Impacto:** Próxima tarea de construcción = T-060 (`brief/015_intake.md`). Insumos ya disponibles: documentación funcional del 015 en `harnesses/` (T-048), schema ampliado de `onboarding_config.json` que el 015 consume (T-145), brief de referencia `brief/010_discovery.md`. La persistencia Capa 1 (T-171) se planifica junto al 015. Ver T-060, T-171, `documents/supabase_persistence_guide.md`.

---

## DEC-025 — Simulaciones y escenarios what-if: Opción C (escenarios predefinidos)
**Fecha:** 2026-06-08
**Decisión:** Las simulaciones se implementan como escenarios predefinidos incluidos automáticamente con el pronóstico mensual. Triple S define y ejecuta 3–5 escenarios estándar (ej: optimista, pesimista, inflación +10%, caída de demanda -15%) sin que el cliente los solicite. Mediano plazo (Fase 3): evolucionará a un panel con levers acotados que el cliente ajusta dentro de rangos que Triple S define y controla.
**Razón:** La Opción C no requiere cambios al dashboard ni mecanismo de solicitud — el cliente sigue recibiendo todo sin operar nada. Los escenarios que los clientes realmente necesiten se identificarán con datos reales antes de construir el panel interactivo.
**Impacto:** El harness 060 Simulator produce artefactos separados de los pronósticos oficiales — nunca deben mezclarse. La publicación de escenarios ocurre junto al pronóstico mensual vía 040 Publisher en una sección diferenciada del dashboard.
