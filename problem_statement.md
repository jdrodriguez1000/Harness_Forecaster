# Planteamiento del Problema — FARO
## Sistema de Pronóstico de Demanda B2B para Manufactura
### Sabbia Solutions & Software (Triple S)

---

## Parte 1: Situación Actual

### Quiénes Somos

**Sabbia Solutions & Software** — conocida comercialmente como **Triple S** — es la empresa que diseña, construye y comercializa esta solución. Triple S no es el usuario final del sistema; es la empresa de software que lo desarrolla y lo vende.

El modelo de negocio es **Service as a Software (SaaSw)**: Triple S no le entrega un software al cliente para que lo opere — Triple S entrega el **resultado** como servicio. El software y los agentes de inteligencia artificial son el motor interno que hace posible escalar y automatizar ese servicio. El cliente deposita su confianza en Triple S de punta a punta, y Triple S se hace responsable de todo el ciclo: ingesta de datos, procesamiento, pronóstico y entrega de resultados.

Esta distinción es clave:

| Dimensión | Software as a Service (SaaS) | **Service as a Software (Triple S)** |
|---|---|---|
| ¿Qué recibe el cliente? | Una herramienta para operar | Un **servicio** con resultados concretos |
| ¿Quién opera el sistema? | El propio cliente | **Triple S** |
| ¿Qué aprende el cliente? | A usar el software | Solo a interpretar y usar los pronósticos |
| ¿Dónde está la responsabilidad? | En el cliente que configura | **En Triple S** de principio a fin |
| ¿Qué escala? | Usuarios del software | **Capacidad de servicio de Triple S** |

El valor que Triple S entrega a cada empresa que contrata el servicio incluye:

- **Reducción de costos** por sobre-inventario y agotamientos de stock
- **Incremento de ingresos** al no perder ventas por falta de producto disponible
- **Mejora en la gestión de inventarios** con niveles más precisos y eficientes
- **Mejor relacionamiento con clientes** al cumplir con mayor confiabilidad y oportunidad los pedidos
- **Planeación de producción más eficiente** al anticipar la demanda con mayor exactitud

### El Cliente Tipo de Triple S

La empresa **ABC** es el arquetipo del cliente al que Triple S le vende la solución. ABC representa a cualquier empresa del sector manufactura que:

- Produce un portafolio de productos (PRD1, PRD2, PRD3, …, PRDn)
- Vende exclusivamente a otras empresas — sus clientes corporativos (XYZ1, XYZ2, XYZ3, …, XYZn)
- Opera en una relación comercial puramente B2B (empresa a empresa)
- Enfrenta variabilidad impredecible en los pedidos que sus clientes le realizan

### Jerarquía de Productos

Los productos no son una lista plana. Pertenecen a una estructura jerárquica:

```
Categoría
└── Subcategoría
    └── Producto (PRD1, PRD2, ..., PRDn)
```

Esta jerarquía permite analizar y pronosticar la demanda en múltiples niveles de agregación — desde referencias individuales (SKU) hasta familias de productos.

### Jerarquía Geográfica

Los pedidos y los clientes también están estructurados geográficamente:

```
Región
└── País
    └── Ciudad
        └── Sede
```

Esto significa que una misma empresa cliente (XYZn) puede realizar pedidos desde diferentes sedes ubicadas en distintas ciudades, países o regiones, y cada sede puede tener un comportamiento de compra independiente.

### El Problema Central

La demanda que las empresas clientes generan sobre ABC es **volátil y difícil de anticipar**. Esta volatilidad se manifiesta en dos situaciones operativas costosas:

| Escenario | Lo que ocurre | Impacto en el negocio |
|---|---|---|
| El cliente pide **menos** de lo esperado | ABC produjo en exceso | Sobre-inventario, capital inmovilizado, costos de almacenamiento |
| El cliente pide **más** de lo esperado | ABC produjo de menos | Agotamiento de stock, ventas perdidas, deterioro de la relación comercial |

La causa raíz es que ABC no cuenta hoy con un mecanismo confiable y basado en datos para anticipar **cuánto** pedirá cada cliente, **de qué producto**, **en qué ubicación** y **en qué momento**.

### La Visión del Producto

Triple S construirá **FARO** (Forecasting Agentic Results & Operations) — un sistema basado en agentes de inteligencia artificial que operan bajo un harness coordinado, donde agentes especializados colaboran para:

1. Ingerir y procesar el historial de pedidos en todas las dimensiones de producto y geografía
2. Identificar patrones de demanda por combinación cliente × producto × ubicación
3. Generar pronósticos de demanda con niveles de confianza asociados
4. Detectar anomalías y señalar comportamientos de pedido inusuales
5. Entregar inteligencia accionable a los equipos de planeación e inventario de cada empresa cliente de Triple S

---

## Parte 2: Preguntas Abiertas

Estas preguntas guiarán el diseño e implementación del sistema. Se irán respondiendo progresivamente a medida que avanza el proyecto.

### 2.1 Modelo de Servicio y Suscripción

El servicio de Triple S opera bajo una **suscripción mensual de valor fijo**. Este pago no es un detalle administrativo externo — es una **regla de negocio central del sistema**: sin pago activo, no hay servicio. El harness debe ser consciente del estado de suscripción de cada cliente y actuar en consecuencia.

Esto implica que el sistema debe gestionar el ciclo de vida del cliente en sus distintos estados:

```
Prospecto → Onboarding → Activo (suscripción al día) → En mora → Suspendido → Reactivado / Cancelado
```

Las preguntas abiertas sobre este componente son:

- **[RESUELTO]** ¿Cuál es el valor fijo mensual y cómo se determina?
  El modelo es un **valor único mensual por empresa**, determinado por el tamaño operativo de la empresa ABC contratante. Las empresas se clasifican en tres categorías — **M, L y XL**:

  | Categoría | Descripción | Precio mensual (USD) | Equivalente COP (aprox.) |
  |---|---|---|---|
  | **M** | Empresa mediana | USD 200 | ~ COP 800.000 |
  | **L** | Empresa grande | USD 350 | ~ COP 1.400.000 |
  | **XL** | Empresa muy grande | USD 500 | ~ COP 2.000.000 |

  **Fórmula de clasificación:** se calcula un **Índice de Tamaño Operativo (ITO)** como combinación ponderada de tres variables:

  ```
  ITO = (Nº de productos activos × w1) + (Nº de clientes XYZn atendidos × w2) + (Volumen mensual de pedidos × w3)

  ITO bajo   →  M  →  USD 200 / mes
  ITO medio  →  L  →  USD 350 / mes
  ITO alto   →  XL →  USD 500 / mes
  ```

  *Pendiente definir:* los pesos (w1, w2, w3) y los umbrales exactos de cada rango, a partir de datos reales de empresas piloto.

  **Planes de pago disponibles:** el cliente elige uno de tres planes al momento de contratar el servicio:

  | Plan | Frecuencia de pago | Descuento | Ejemplo para categoría M (USD 200/mes) |
  |---|---|---|---|
  | **Mensual** | Mes a mes | Sin descuento | USD 200 / mes |
  | **Trimestral** | Por adelantado cada 3 meses | Hasta 8% | USD 552 por 3 meses (ahorra USD 48) |
  | **Anual** | Por adelantado 12 meses | 18% | USD 1.968 por 12 meses (ahorra USD 432) |

  El descuento premia el compromiso anticipado: a mayor horizonte de pago, mayor ahorro para el cliente y mayor flujo de caja garantizado para Triple S.

  **[RESUELTO]** El descuento es fijo y aplica igual para todas las categorías (M, L y XL). No hay reembolsos por cancelación anticipada — el período pagado por adelantado se consume en su totalidad independientemente de si el cliente decide no continuar.

  **Implicación para el sistema:** el harness debe gestionar tres ciclos de vencimiento distintos. Las reglas de notificación y suspensión (mensajes verdes, amarillos, suspensión) aplican sobre la fecha de vencimiento del período contratado, independientemente de si ese período es de 1, 3 o 12 meses. La regla de renovación de fecha (atraso ≤ 2 días conserva fecha original, atraso ≥ 3 días renueva desde el día del pago) aplica igualmente para los tres planes.

  **Argumento de valor clave:** USD 500 equivale aproximadamente a un salario mínimo legal vigente en Colombia (COP 2.000.000). Un profesional experto en pronóstico de demanda cuesta como mínimo el triple de ese valor. Triple S le entrega al cliente un servicio especializado, continuo y basado en IA por **1/3 del costo mínimo de una persona** que hiciera lo mismo — sin riesgos de rotación, curva de aprendizaje ni ausencias.
- **[RESUELTO]** ¿Qué ocurre exactamente cuando un cliente entra en mora?

  El ciclo de pago y suspensión funciona así (usando como ejemplo un cliente que pagó el día 6 del mes):

  ```
  Día 6 del mes actual → PAGO REALIZADO
  │
  │   [Período de servicio activo: 30 días]
  │
  ▼
  Día 5 del mes siguiente → FIN DEL PERÍODO PAGADO
  │
  ├─ Día 2 del mes siguiente → Mensaje verde NO FIJO en pantalla: "Recuerda renovar tu suscripción"
  │                             + Correo al responsable del cliente (empresa ABC)
  ├─ Día 3 del mes siguiente → Mensaje verde NO FIJO en pantalla: "Recuerda renovar tu suscripción"
  │                             + Correo al responsable del cliente (empresa ABC)
  ├─ Día 5 del mes siguiente → Mensaje verde FIJO en pantalla: "Hoy vence tu período de servicio. Renueva ahora."
  │                             + Correo al responsable del cliente (empresa ABC)
  │
  │   [Período de gracia: días 6, 7 y 8]
  │
  ├─ Días 6, 7 y 8            → Mensaje AMARILLO FIJO en pantalla: "Tu suscripción ha vencido. Tienes hasta el día 8 para renovar."
  │                             + Correo al responsable del cliente (empresa ABC)
  │
  │   [Suspensión]
  │
  └─ Día 9 sin pago registrado → El cliente puede ingresar al sistema pero ve únicamente
                                  un mensaje de SUSPENSIÓN POR NO PAGO.
                                  No tiene acceso a ninguna funcionalidad hasta regularizar el pago.
  ```

  **Resumen de colores y comportamiento de mensajes:**

  | Día | Color | Tipo de mensaje | Canal adicional |
  |---|---|---|---|
  | 2, 3 del mes siguiente | Verde | No fijo (puede cerrarse) | Correo al responsable |
  | 5 del mes siguiente | Verde | Fijo (no se puede cerrar) | Correo al responsable |
  | 6, 7, 8 | Amarillo | Fijo (no se puede cerrar) | Correo al responsable |
  | 9 en adelante | Rojo | Pantalla de suspensión total | — |

  **[RESUELTO]** ¿Qué fecha de renovación aplica si el cliente paga después del día 5?

  Se adopta un modelo **híbrido** que combina fecha fija para pagos con atraso menor y fecha rodante para atrasos significativos:

  | Días de atraso sobre la fecha de vencimiento | Regla de renovación | Ejemplo (vencía el día 5) |
  |---|---|---|
  | **1 o 2 días** (pagó el día 6 o 7) | La fecha original se conserva | Próximo vencimiento: día 5 del mes siguiente |
  | **3 o más días** (pagó el día 8 en adelante) | La fecha se renueva 30 días desde el día del pago | Pagó el día 9 → próximo vencimiento: día 9 del mes siguiente |

  **Lógica detrás de la regla:**
  - Un atraso de 1 o 2 días se considera dentro de un margen razonable — el cliente no pierde su fecha original y no sufre consecuencias más allá del mensaje de alerta.
  - Un atraso de 3 o más días es un atraso real y deliberado — la fecha de renovación se desplaza hacia adelante desde el día del pago efectivo. El cliente no pierde los días pagados, pero su ciclo de vencimiento cambia.
  - Este mecanismo crea un incentivo natural: quien se atrasa frecuentemente verá su fecha de vencimiento moverse hacia días menos convenientes del mes, motivándolo a regularizarse.

  **Implicación para el sistema:** el harness debe calcular y actualizar automáticamente la fecha de próximo vencimiento en el momento en que registra cada pago, aplicando esta regla sin intervención manual.
- **[RESUELTO]** ¿Qué pasa con los datos del cliente si cancela definitivamente?

  Cuando un cliente cancela o no renueva su suscripción, se activa el siguiente ciclo de retención y eliminación de datos:

  ```
  Día 0: Cancelación o no renovación definitiva
  │
  ├─── Meses 1 a 3 → Período de solicitud de exportación
  │    · Los datos se conservan internamente en Triple S
  │    · El cliente PUEDE solicitar la exportación de sus datos de pronóstico
  │    · Solo se exportan los datos generados por las predicciones
  │    · NUNCA se exportan datos de las capas Bronce, Plata u Oro
  │    · Una vez solicitada la exportación, Triple S tiene hasta 3 meses para entregarla
  │
  ├─── Meses 4 a 6 → Período de retención sin exportación
  │    · Los datos se conservan internamente en Triple S
  │    · El cliente ya NO puede solicitar exportaciones
  │    · Triple S completa entregas de exportaciones ya solicitadas en el período anterior
  │
  └─── Mes 6 completo → ELIMINACIÓN DEFINITIVA
       · Todos los datos del cliente son eliminados permanentemente del sistema
       · Sin posibilidad de recuperación
  ```

  **Reglas clave:**

  | Regla | Detalle |
  |---|---|
  | Retención total | 6 meses desde la cancelación |
  | Ventana de solicitud de exportación | Solo durante los primeros 3 meses |
  | Plazo de entrega de la exportación | Hasta 3 meses después de recibida la solicitud |
  | Qué se exporta | Únicamente datos de pronósticos y predicciones generadas |
  | Qué NO se exporta | Datos en capas Bronce, Plata y Oro — nunca |
  | Eliminación | Permanente al completarse el mes 6, sin excepciones |

  **[RESUELTO] Caso borde:** si el cliente solicita la exportación en el mes 3 y la entrega aún no se ha completado al llegar el mes 6, **la eliminación queda bloqueada hasta que se confirme la entrega de la exportación al cliente**. Solo después de esa confirmación el sistema procede con la eliminación definitiva. El harness debe gestionar este bloqueo automáticamente y nunca eliminar datos con una exportación pendiente de confirmación.
- **[RESUELTO]** ¿Quién gestiona el cobro?
  El cobro se gestiona mediante una **pasarela de pagos automatizada**. Triple S no interviene manualmente en el proceso de cobro. La pasarela notifica al sistema en tiempo real cuando un pago es confirmado, lo que permite al harness actualizar de forma inmediata y exacta el estado de suscripción de cada cliente — sin ambigüedad sobre quién pagó y en qué momento. *Pendiente definir:* qué pasarela de pagos se utilizará (Stripe, PayU, MercadoPago, u otra).
- **[RESUELTO]** ¿El sistema debe generar automáticamente alertas y notificaciones ante pagos vencidos? Sí. El comportamiento completo está definido en la regla de ciclo de pago y suspensión documentada anteriormente: mensajes en pantalla (verde no fijo, verde fijo, amarillo fijo, suspensión) y correos electrónicos al responsable del cliente, activados automáticamente por el harness según los días transcurridos desde el vencimiento.
- **[RESUELTO]** ¿Cuál es el proceso de onboarding de un nuevo cliente?

  El onboarding tiene un plazo máximo de **3 meses** desde la primera conexión con los datos del cliente hasta la entrega del primer pronóstico. Este plazo reconoce que la calidad de los datos es desconocida al inicio y que el proceso de transformación puede requerir tiempo variable.

  **Estructura del onboarding:**

  ```
  MES 1 — GRATUITO (el cliente no paga)
  ────────────────────────────────────────────────────
  · Triple S se conecta con los datos del cliente
    (puede ser un archivo plano CSV u otra fuente)
  · Se realiza la ingesta y copia a capa Bronce
  · Se genera el Diagnóstico de Salud de Datos
  · Se presenta al cliente el estado de sus datos
  · Se inicia el proceso de transformación Bronce → Plata
  · Triple S comienza a construir conocimiento del negocio
    del cliente

  MES 2 — PRIMER PAGO / SERVICIO ACTIVO
  ────────────────────────────────────────────────────
  · El cliente realiza su primer pago
  · Se continúa el proceso Plata → Oro
  · Se afinan los modelos de pronóstico
  · Triple S consolida la confianza con el cliente

  MES 3 — PRIMER PRONÓSTICO (límite máximo)
  ────────────────────────────────────────────────────
  · El cliente recibe su primer pronóstico de demanda
  · Si la calidad de datos lo permite, puede ocurrir
    antes del mes 3
  ```

  **Propósito estratégico del mes gratuito:**

  | Beneficio para el cliente | Beneficio para Triple S |
  |---|---|
  | Conoce el servicio sin compromiso económico inicial | Genera confianza antes del primer cobro |
  | Recibe el diagnóstico de salud de sus datos — algo que nadie le había mostrado antes | Demuestra expertise técnico desde el primer contacto |
  | Entiende el valor del servicio antes de pagar | Aprende el negocio del cliente para mejorar el pronóstico |

  El primer mes gratuito no es un descuento — es la estrategia de Triple S para que el cliente **vea valor real antes de pagar**, reduciendo la fricción de venta y acelerando la decisión de continuar.
- **[RESUELTO]** ¿Cómo entrega Triple S los resultados al cliente?

  Se utilizan **tres canales combinados**, cada uno con un propósito distinto:

  | Canal | Descripción | Propósito |
  |---|---|---|
  | **Dashboard de solo lectura** | Canal principal. El cliente visualiza pronósticos, evolución de salud de datos y estado de suscripción de forma visual e intuitiva | Consumo diario sin capacitación técnica |
  | **Correo electrónico automático** | Al publicar cada nuevo pronóstico, el responsable del cliente recibe un resumen ejecutivo por correo | Garantiza que el cliente reciba valor aunque no ingrese al dashboard |
  | **Archivo exportable (Excel / CSV)** | Desde el dashboard, el cliente descarga el pronóstico en formato tabular para usarlo en sus propias herramientas de planeación o ERP | Permite al planificador de demanda trabajar con el número en su entorno habitual |

  **Lo que no se ofrece:** API de consulta — requiere capacidad técnica en el cliente, lo cual contradice el modelo Service as a Software donde el cliente consume resultados sin operar el sistema.

  El dashboard es de **solo lectura**: el cliente no puede modificar parámetros del modelo, cargar datos ni configurar el sistema. Toda la operación interna es responsabilidad exclusiva de Triple S.
- **[RESUELTO]** ¿Qué acuerdos de nivel de servicio (SLA) se establecen con el cliente?

  **SLA 1 — Frecuencia de entrega del pronóstico**
  Mensual, entregado dentro de los primeros **5 días hábiles** de cada mes, alineado con el ciclo natural de planeación de una empresa manufacturera.

  **SLA 2 — Precisión del pronóstico (MAPE)**
  La precisión está condicionada al índice de salud de datos del cliente — Triple S no puede comprometer precisión sobre datos de mala calidad:

  | Salud de datos | Compromiso de precisión (MAPE) |
  |---|---|
  | ≥ 95% | ≤ 15% de error |
  | 70% – 94% | ≤ 25% de error |
  | < 70% | Sin garantía de precisión — período de mejora activa de datos |

  Esta vinculación crea un incentivo directo: a mejor salud de datos, mayor precisión garantizada y mayor valor del servicio.

  **SLA 3 — Disponibilidad del dashboard**
  **99% mensual** — equivale a menos de 7 horas de caída al mes.

  **SLA 4 — Tiempo de respuesta y resolución ante incidentes**

  | Severidad | Ejemplo | Respuesta | Resolución |
  |---|---|---|---|
  | **Crítica** | Dashboard caído, pronóstico no entregado en fecha | 4 horas hábiles | 24 horas hábiles |
  | **Alta** | Pronóstico entregado con datos incorrectos | 8 horas hábiles | 48 horas hábiles |
  | **Media** | Correo automático no enviado, exportación fallida | 24 horas hábiles | 72 horas hábiles |

  **SLA 5 — Actualización del diagnóstico de salud de datos**
  Mensual, entregado junto con el pronóstico dentro de los primeros 5 días hábiles del mes.

  **SLA 6 — Tiempo de respuesta a consultas generales del cliente**
  **24 horas hábiles** para cualquier consulta no clasificada como incidente.
- **[RESUELTO]** ¿La solución tendrá una etapa piloto o prueba de concepto antes del contrato formal? El **mes 1 gratuito del onboarding cumple esta función**. No hay un piloto separado previo al contrato — el cliente firma, entrega sus datos, y el primer mes sin costo es su experiencia real del servicio antes de comprometer el primer pago.

### 2.2 Gestión y Salud de Datos del Cliente

#### Principios inamovibles

El tratamiento de datos del cliente se rige por principios no negociables:

1. **Los datos originales del cliente son intocables.** Triple S nunca modifica, corrige ni elimina la información en su estado original. Lo que el cliente entrega se conserva exactamente como llegó.
2. **El cliente entrega sus datos en el estado en que los tiene.** Triple S no impone requisitos de calidad mínima para iniciar el servicio — recibe lo que hay.
3. **Triple S trabaja siempre sobre una copia.** Sobre esa copia se aplica el proceso de transformación y mejora progresiva.

#### Flujo Concreto: del Dato Original al Pronóstico

El proceso completo, desde que el cliente entrega sus datos hasta que Triple S genera pronósticos, sigue este flujo:

```
  CLIENTE
  ───────
  Entrega sus datos tal como los tiene
  (ejemplo: archivo CSV con historial de pedidos)
        │
        ▼
  ┌─── BRONCE ────────────────────────────────────────┐
  │  Triple S realiza una copia exacta del archivo     │
  │  Sin ninguna modificación. Preservación total.     │
  │                                                    │
  │  ► Se genera el DIAGNÓSTICO DE SALUD DE DATOS      │
  │    y se presenta al cliente                        │
  └────────────────────────────────────────────────────┘
        │
        ▼
  ┌─── PLATA ──────────────────────────────────────────┐
  │  Triple S transforma la copia Bronce               │
  │  · Corrección de formatos y tipos de dato          │
  │  · Eliminación de duplicados                       │
  │  · Tratamiento de valores vacíos o nulos           │
  │  · Normalización de jerarquías (producto, geografía│
  │  · Estandarización de identificadores de cliente   │
  └────────────────────────────────────────────────────┘
        │
        ▼
  ┌─── ORO ────────────────────────────────────────────┐
  │  Datos listos para modelado y pronóstico            │
  │  · Enriquecidos y agregados según dimensiones       │
  │  · Estructurados para los agentes de IA             │
  │  · Sobre esta capa operan los modelos de demanda    │
  └────────────────────────────────────────────────────┘
        │
        ▼
  PRONÓSTICO DE DEMANDA
  Entregado al cliente como servicio
```

#### Diagnóstico de Salud de Datos

Al recibir los datos del cliente (capa Bronce), Triple S genera un **diagnóstico de salud de datos** que se presenta al cliente de forma clara y sin tecnicismos. Este diagnóstico muestra:

- El **índice de salud global** de los datos recibidos (expresado en porcentaje)
- Las dimensiones evaluadas: completitud, consistencia, unicidad, vigencia y trazabilidad
- Los problemas específicos encontrados y su impacto en la calidad del pronóstico
- El nivel de esfuerzo de transformación que requieren los datos
- La **evolución histórica** del índice — cada vez que el cliente entrega nuevos datos, se actualiza y se compara con entregas anteriores

Este diagnóstico cumple dos funciones:

| Función | Descripción |
|---|---|
| **Transparencia** | El cliente ve en qué condición están sus datos, algo que en la mayoría de los casos nunca nadie le había mostrado |
| **Hoja de ruta** | Triple S le muestra exactamente qué mejorar y en qué orden — el cliente decide si lo hace solo o con asesoría de Triple S |

#### Objetivo de Salud: 95%

Triple S trabaja en conjunto con el cliente, bajo un esquema de **asesoría continua**, para mejorar progresivamente la calidad de sus datos hasta alcanzar y superar el **95% de salud** (es decir, 5% o menos de errores o inconsistencias).

Este umbral no es arbitrario — es el nivel a partir del cual los pronósticos alcanzan su máxima confiabilidad y el cliente obtiene el mayor valor del servicio.

Este proceso de mejora conjunta genera tres beneficios estratégicos para Triple S:

1. **Fidelización:** Un cliente que mejora su salud de datos con la ayuda de Triple S difícilmente abandona el servicio — la relación se profundiza con el tiempo.
2. **Confianza:** El cliente ve resultados tangibles y medibles en la calidad de sus propios datos, no solo en los pronósticos.
3. **Conocimiento del negocio:** Triple S aprende en profundidad la operación del cliente — sus ciclos, sus productos, sus clientes, sus excepciones — lo que enriquece la calidad del servicio de forma continua.

#### Complejidad de Datos y Precio

La calidad de los datos no es solo un problema técnico — es una **variable de precio**. El esfuerzo de transformación que requiere llevar los datos de Bronce a Oro determina un cargo adicional sobre la suscripción mensual fija:

```
Precio del servicio = Suscripción mensual fija + Cargo por complejidad de datos
```

A mayor desorden, vacíos, inconsistencias o volumen de transformación requerido, mayor es el cargo adicional. Esto crea un **incentivo económico directo** para que el cliente trabaje en mejorar la calidad de sus datos: a mejor salud de datos, menor cargo adicional y mayor calidad de pronóstico.

#### Preguntas Abiertas sobre Datos

- **[RESUELTO]** ¿Qué fuentes de datos entrega típicamente una empresa ABC?

  El sistema acepta las siguientes fuentes, organizadas en tres rutas de ingesta:

  | Ruta | Fuente | Clientes |
  |---|---|---|
  | **Estándar** | Archivo plano CSV / Excel | Todos — obligatoria para la primera versión |
  | **Avanzada** | Conexión directa a base de datos (SQL Server, MySQL, PostgreSQL) | Clientes L y XL |
  | **Enterprise** | ERP (SAP, Oracle, Dynamics) / API | A definir en fases posteriores |

  **Fuente no aceptada:** correo electrónico — no es una fuente estructurada y no puede integrarse al pipeline de datos.

  **Modos de entrega de datos:**

  El sistema soporta dos modos que pueden coexistir entre distintos clientes:

  ```
  MODO 1 — BATCH (histórico estático)
  ─────────────────────────────────────────────────────────
  El cliente entrega un archivo completo una sola vez
  (ej: 01/01/2022 al 31/12/2025)
  Triple S trabaja con ese universo fijo
  Reentrenamiento del modelo: solo si el cliente entrega un nuevo archivo completo
  Pronóstico al cliente: mensual

  MODO 2 — INCREMENTAL (actualización continua)
  ─────────────────────────────────────────────────────────
  El cliente entrega el historial inicial + actualizaciones periódicas (diaria o semanal)
  (ej: entrega hasta el 07/01/2026 hoy, mañana entrega hasta el 08/01/2026)
  El sistema detecta registros nuevos y los incorpora sin reprocesar todo desde cero
  Deduplicación automática por fecha y clave cliente × producto
  Reentrenamiento del modelo: semanal (independiente de la frecuencia de entrega del cliente)
  Pronóstico al cliente: mensual (igual que Modo 1)
  ```

  **Tolerancia a gaps:** si el cliente no entrega datos un día o una semana, el sistema lo registra en el diagnóstico de salud pero no se interrumpe el servicio.
- **[RESUELTO]** ¿Cuántos años de historial de pedidos son suficientes para generar pronósticos confiables?

  **Rangos de historial y su impacto en la confianza del pronóstico:**

  | Historial disponible | Nivel de confianza | Acción del sistema |
  |---|---|---|
  | ≥ 3 años | Alta confianza | Pronóstico estándar sin advertencias |
  | 2 – 3 años | Confianza estándar | Pronóstico estándar — rango ideal mínimo |
  | 1 – 2 años | Confianza reducida | Pronóstico generado con advertencia visible al cliente |
  | < 1 año | Confianza experimental | Pronóstico generado con alerta de baja confianza |
  | Sin historial | Sin pronóstico directo | Se aplica estrategia de arranque en frío (ver abajo) |

  El historial se evalúa por combinación **cliente × producto** — no todos los productos de un cliente tendrán el mismo volumen de historia, y el sistema lo gestiona de forma independiente para cada combinación.

  **Estrategia de arranque en frío (cold start) para productos sin historial:**

  Cuando un producto no tiene historial propio se aplica una estrategia en cascada:

  ```
  PASO 1 — Analogía por categoría
  ¿Existen otros productos de la misma subcategoría/categoría con historial?
  → Sí: usar su comportamiento promedio como pronóstico proxy
  → No: ir al Paso 2

  PASO 2 — Analogía por cliente
  ¿El mismo cliente tiene historial con otros productos similares?
  → Sí: usar el patrón de compra de ese cliente como proxy
  → No: ir al Paso 3

  PASO 3 — Acumulación mínima
  Ningún referente disponible → esperar 3 meses de pedidos reales
  antes de generar un pronóstico formal
  ```

  En todos los casos el dashboard muestra al cliente que el producto está en **modo arranque**, el paso de la cascada que se está aplicando, y el tiempo estimado para obtener un pronóstico de mayor confianza.
- **[RESUELTO]** ¿Los datos incluyen de forma separada los campos clave del historial de pedidos?

  El sistema trabaja con dos esquemas de datos complementarios:

  **Esquema 1 — Historial de Pedidos (fuente principal, obligatoria)**

  *Campos mínimos requeridos — sin estos no hay pronóstico posible:*

  | Campo | Descripción | Ejemplo |
  |---|---|---|
  | `fecha_pedido` | Fecha en que el cliente XYZ realizó el pedido | 2024-03-15 |
  | `id_cliente` | Identificador único del cliente XYZ | XYZ001 |
  | `id_producto` | Identificador único del producto PRD | PRD042 |
  | `cantidad_solicitada` | Cantidad pedida por el cliente | 500 |

  *Campos del esquema ideal — permiten pronósticos de alta precisión y análisis completo:*

  | Grupo | Campo | Descripción | Por qué importa |
  |---|---|---|---|
  | **Pedido** | `fecha_pedido` | Fecha del pedido | Base del modelo temporal |
  | | `fecha_entrega_solicitada` | Fecha en que el cliente pide que llegue | Revela el lead time esperado |
  | | `fecha_entrega_real` | Fecha en que realmente se entregó | Revela incumplimientos de ABC |
  | | `estado_pedido` | Entregado / Parcial / Cancelado / Pendiente | Distingue demanda real de demanda atendida |
  | **Cantidades** | `cantidad_solicitada` | Lo que el cliente pidió | La demanda real |
  | | `cantidad_entregada` | Lo que ABC realmente entregó | Revela agotamientos |
  | | `cantidad_cancelada` | Lo que se anuló | Demanda perdida |
  | **Cliente** | `id_cliente` | Identificador del cliente XYZ | Dimensión de análisis |
  | | `id_sede` | Sede o sucursal del cliente | Granularidad geográfica del cliente |
  | **Producto** | `id_producto` | Identificador del producto PRD | Dimensión de análisis |
  | | `subcategoria` | Subcategoría del producto | Para cold start y agregación |
  | | `categoria` | Categoría del producto | Para cold start y agregación |
  | **Geografía** | `ciudad` | Ciudad de la sede del cliente | Jerarquía geográfica |
  | | `pais` | País | Jerarquía geográfica |
  | | `region` | Región | Jerarquía geográfica |
  | **Contexto** | `unidad_medida` | Unidad de la cantidad (unidades, kg, cajas) | Normalización |
  | | `tipo_pedido` | Regular / Urgente / Promocional | Detecta pedidos atípicos |

  **Esquema 2 — Producción e Inventario de ABC (fuente complementaria, opcional)**

  Habilita el análisis de agotados y desperdicios con impacto financiero:

  | Campo | Descripción | Ejemplo | Qué habilita |
  |---|---|---|---|
  | `fecha` | Fecha del registro | 2024-03-15 | Ubicación temporal del dato |
  | `id_producto` | Producto al que corresponde | PRD042 | Cruce con el esquema principal |
  | `cantidad_producida` | Unidades producidas en ese período | 800 | Cálculo de sobre-inventario |
  | `stock_disponible` | Unidades en inventario a esa fecha | 320 | Detección de riesgo de agotado preventivo |
  | `costo_unitario` | Costo de producción por unidad (USD) | 12.50 | Impacto financiero del desperdicio y el agotado |
  | `stock_minimo` | Nivel mínimo de seguridad definido por ABC | 100 | Alerta cuando el stock baja del umbral seguro |

  Con estos dos esquemas combinados el sistema puede calcular:

  ```
  Sobre-inventario       = cantidad_producida - cantidad_entregada
  Agotado                = cantidad_solicitada - cantidad_entregada
  Costo del desperdicio  = sobre-inventario × costo_unitario
  Ingreso perdido        = agotado × costo_unitario
  Alerta preventiva      = stock_disponible < stock_minimo → riesgo de agotado inminente
  ```

  Cada campo faltante del esquema ideal se refleja como limitante en el índice de salud de datos y como restricción en la precisión del pronóstico.
- **[RESUELTO]** ¿Cuáles son las dimensiones exactas del índice de salud de datos?

  El **Índice de Salud de Datos (ISD)** se compone de 6 dimensiones ponderadas que producen un puntaje de 0 a 100%:

  | # | Dimensión | Qué mide | Peso |
  |---|---|---|---|
  | 1 | **Completitud** | % de registros con todos los campos mínimos requeridos completos — sin nulos ni vacíos | 25% |
  | 2 | **Consistencia** | Coherencia lógica de valores: cantidad_entregada ≤ cantidad_solicitada, fechas en orden correcto, sin cantidades negativas | 20% |
  | 3 | **Continuidad** | Ausencia de brechas temporales en combinaciones cliente × producto activas — detecta meses o semanas sin registros donde debería haberlos | 20% |
  | 4 | **Unicidad** | Ausencia de registros duplicados por clave (cliente + producto + fecha + cantidad) | 15% |
  | 5 | **Cobertura temporal** | Qué tan cerca está el historial disponible del ideal de 2–3 años por combinación cliente × producto | 10% |
  | 6 | **Exactitud** | Valores dentro de rangos esperados — detecta outliers extremos que sugieren errores de digitación | 10% |

  **Fórmula:**
  ```
  ISD = (Completitud × 0.25) + (Consistencia × 0.20) + (Continuidad × 0.20)
      + (Unicidad × 0.15) + (Cobertura × 0.10) + (Exactitud × 0.10)

  Resultado: 0% (datos inutilizables) → 100% (datos perfectos)
  Meta:      ≥ 95%
  ```

  **Presentación al cliente — el dashboard muestra puntaje global + detalle por dimensión:**
  ```
  ÍNDICE DE SALUD DE DATOS — Marzo 2026
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Puntaje global:     81% ▲ (+4% vs mes anterior)

  Completitud         94%  ████████████████████░░  ✓
  Consistencia        88%  █████████████████░░░░░  ✓
  Continuidad         72%  ██████████████░░░░░░░░  ⚠
  Unicidad            96%  ████████████████████░░  ✓
  Cobertura temporal  85%  █████████████████░░░░░  ✓
  Exactitud           91%  ██████████████████░░░░  ✓

  Problema principal: 28% de combinaciones cliente×producto
  tienen brechas temporales de más de 6 semanas.
  Acción sugerida: revisar registros de pedidos entre
  agosto y octubre 2025.
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ```
- **[RESUELTO]** ¿Con qué frecuencia se recalcula y presenta al cliente el diagnóstico de salud de datos?

  Dos reglas complementarias gobiernan el ciclo del ISD:

  | Evento | Acción |
  |---|---|
  | **Entrega mensual** (primeros 5 días hábiles) | Se presenta el diagnóstico formal al cliente junto con el pronóstico |
  | **Actualización de datos por el cliente** (Modo Incremental) | El ISD se recalcula inmediatamente — el dashboard muestra el valor actualizado |

  El valor que aparece en el dashboard es siempre **el más reciente calculado**. Si el cliente entregó datos el día 18 del mes, el ISD del dashboard ya refleja esa actualización — no espera al próximo reporte mensual para mostrarlo.

  El reporte mensual formal captura el valor del ISD en el momento de su emisión, incluyendo cualquier recálculo previo por actualizaciones de datos durante ese período.
- **[RESUELTO]** ¿Cómo se define la escala de complejidad que determina el cargo adicional?

  La escala tiene **4 niveles** vinculados directamente al ISD. A menor ISD, mayor esfuerzo de transformación y mayor cargo:

  | Nivel | Nombre | Rango ISD | Descripción | Cargo adicional |
  |---|---|---|---|---|
  | 🟢 | **Óptimo** | ≥ 95% | Datos en excelente condición — transformación mínima | 0% — incluido en la suscripción |
  | 🟡 | **Moderado** | 70% – 94% | Datos con problemas tratables — transformación estándar | +20% sobre la suscripción |
  | 🟠 | **Significativo** | 50% – 69% | Datos con problemas importantes — transformación intensiva | +50% sobre la suscripción |
  | 🔴 | **Crítico** | < 50% | Datos en mal estado — transformación de alta complejidad | +80% sobre la suscripción |

  **Precio total por categoría según nivel de complejidad:**

  | Categoría | Base | 🟢 Óptimo | 🟡 Moderado | 🟠 Significativo | 🔴 Crítico |
  |---|---|---|---|---|---|
  | M | USD 200 | USD 200 | USD 240 | USD 300 | USD 360 |
  | L | USD 350 | USD 350 | USD 420 | USD 525 | USD 630 |
  | XL | USD 500 | USD 500 | USD 600 | USD 750 | USD 900 |

  **Reglas de operación:**

  1. El cargo se evalúa **mensualmente** con base en el ISD vigente — si el cliente mejora sus datos, el cargo baja automáticamente al mes siguiente
  2. Durante el **mes 1 de onboarding** no aplica cargo adicional — es parte del período gratuito
  3. El dashboard muestra siempre el nivel actual, el cargo vigente y cuántos puntos de ISD necesita ganar para bajar al nivel siguiente

  ```
  COMPLEJIDAD DE DATOS — Marzo 2026
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Nivel actual:     🟡 MODERADO  (ISD: 81%)
  Cargo adicional:  +20%  →  USD 240 / mes (categoría M)

  Para bajar a nivel ÓPTIMO necesita: +14 puntos de ISD
  Acción principal: corregir brechas temporales en Continuidad (72%)
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ```
- **[RESUELTO]** ¿El maestro de datos lo mantiene el cliente o lo construye Triple S?

  **Triple S construye y mantiene el maestro de datos** automáticamente a partir de los datos crudos del cliente — no se le pide al cliente ningún archivo adicional. Durante la transformación Bronce → Plata los agentes extraen, estandarizan y consolidan tres maestros:

  | Maestro | Campos que contiene |
  |---|---|
  | **Productos** | id_producto, nombre, subcategoría, categoría, unidad_medida |
  | **Clientes XYZ** | id_cliente, nombre, id_sede, ciudad, país, región |
  | **Geográfico** | región, país, ciudad, sede |

  **Reglas de operación:**

  | Situación | Acción de Triple S |
  |---|---|
  | Producto o cliente nuevo aparece en los datos | Se incorpora automáticamente al maestro |
  | Mismo elemento con nombres distintos en el historial (ej: "PRD01" y "Producto 1") | Se detecta como inconsistencia, se unifica y se reporta en el diagnóstico de salud de datos |
  | El cliente detecta un error en el maestro | Lo notifica a Triple S — Triple S aplica la corrección |

  El cliente puede **consultar el maestro en el dashboard** (solo lectura) pero nunca puede editarlo directamente. Triple S mantiene el control total de la consistencia del maestro.

### 2.3 Alcance del Pronóstico

- **[RESUELTO]** ¿Cuál es el horizonte de pronóstico?

  El horizonte **no es fijo** — cada empresa ABC define el suyo según su ciclo de negocio. El sistema soporta cualquiera de estos horizontes de forma independiente por cliente:

  | Horizonte | Ejemplo de uso |
  |---|---|
  | **Días** | Empresas con pedidos muy frecuentes o ciclos cortos de producción |
  | **Semanas** | Empresas con ciclos de reabastecimiento semanales |
  | **Meses** | Empresas con planeación mensual de producción |
  | **Múltiples meses** | Empresas que planean producción con varios meses de anticipación |

  El horizonte se configura por cliente durante el onboarding y puede ajustarse en el tiempo. El sistema genera el pronóstico para el horizonte definido por cada cliente — no hay un horizonte global único.

- **[RESUELTO]** ¿Se pronostica a nivel de SKU, categoría, o ambos?

  **Ambos niveles simultáneamente.** El sistema genera pronósticos en dos granularidades:

  ```
  Nivel 1 — SKU (Producto individual)
  Pronóstico por cada combinación cliente × producto × sede

  Nivel 2 — Agregado (Subcategoría / Categoría)
  Pronóstico consolidado por familia de productos
  Útil para decisiones de planeación de alto nivel
  ```

  Los pronósticos de nivel agregado se derivan de la suma de los pronósticos a nivel SKU — garantizando consistencia entre ambos niveles.

- **[RESUELTO]** ¿El pronóstico es por cliente, por sede, o ambos?

  **Ambos niveles simultáneamente.** El sistema genera pronósticos en dos granularidades de cliente:

  ```
  Nivel 1 — Sede
  Pronóstico por cada combinación cliente × producto × sede específica
  Refleja el comportamiento de compra de cada punto de entrega

  Nivel 2 — Cliente consolidado
  Suma de todas las sedes del mismo cliente
  Útil para negociaciones comerciales y visión global del cliente
  ```

- **[RESUELTO]** ¿La jerarquía geográfica estará completamente poblada desde el inicio?

  No necesariamente. La jerarquía geográfica es **flexible y parcial por diseño** — el sistema se adapta a lo que cada empresa tenga disponible:

  | Escenario | Ejemplo | Cómo lo maneja el sistema |
  |---|---|---|
  | Jerarquía completa | Región → País → Ciudad → Sede | Pronóstico en todos los niveles geográficos |
  | Jerarquía parcial | Solo País → Ciudad → Sede | Pronóstico en los niveles disponibles |
  | Empresa local | Solo una Ciudad y una Sede | Sin jerarquía geográfica — pronóstico directo por sede |
  | Un solo país | País → varias Ciudades → Sedes | Pronóstico por ciudad y sede, sin nivel de región |

  Los niveles geográficos faltantes no bloquean el pronóstico — simplemente no aparecen como dimensión de análisis en el dashboard. A medida que el cliente enriquece su información geográfica, el sistema incorpora los nuevos niveles automáticamente.

### 2.4 Patrones de Pedido y Tiempos de Entrega

#### [RESUELTO] Variabilidad de frecuencias y tiempos — regla estructural del sistema

La frecuencia de pedido y el tiempo de entrega **no son propiedades de la empresa cliente ni del producto de forma independiente — son propiedades de cada combinación cliente × producto**. Esto es una regla estructural del sistema: no existe un ciclo estándar global.

Ejemplos que ilustran esta regla:

| Empresa cliente | Producto | Frecuencia de pedido | Tiempo de entrega |
|---|---|---|---|
| XYZ1 | PRD1 | Cada 3 meses | 30 días |
| XYZ1 | PRD2 | Mensual | 15 días |
| XYZ2 | PRD1 | Mensual | 10 días |
| XYZ2 | PRD2 | Mensual | 10 días |
| XYZ3 | PRD1, PRD2, PRD3 | Mensual (todos) | 30 días (todos) |

**Implicación para el harness:** el sistema debe modelar, almacenar y pronosticar de forma independiente cada combinación cliente × producto, respetando su frecuencia y tiempo de entrega propios. No se puede asumir ningún ciclo por defecto.

Esto también significa que:
- El pronóstico de cuándo llegará el próximo pedido es en sí mismo una variable a predecir, no un dato fijo
- Un mismo cliente puede tener productos en ventanas de pronóstico completamente distintas de forma simultánea
- El sistema debe alertar cuando una combinación cliente × producto se desvía de su patrón histórico de frecuencia

#### Preguntas resueltas sobre patrones

- **[RESUELTO]** ¿Existen patrones de estacionalidad conocidos?

  La estacionalidad **puede o no existir** según el cliente y su industria — no se asume ningún patrón por defecto. Su identificación es una tarea del **mes 1 de onboarding**: durante ese período los agentes analizan el historial del cliente para detectar si existen ciclos repetibles (festivos, cierres de año fiscal, temporadas de ventas, ciclos de industria). El resultado queda registrado en el perfil del cliente y se incorpora al modelo de pronóstico.

  Si durante el onboarding no se detecta estacionalidad significativa, el modelo opera sin ese componente. Si aparece nueva estacionalidad en períodos posteriores (detectada en actualizaciones de datos), el modelo se ajusta en el siguiente ciclo de reentrenamiento.

- **[RESUELTO]** ¿Los clientes XYZn comparten señales de demanda anticipadas?

  Por lo general **no**. Las empresas XYZn no acostumbran comunicar sus intenciones de compra con anticipación a ABC. Por lo tanto, el sistema no puede depender de señales externas de demanda — debe construir el pronóstico exclusivamente a partir del historial de pedidos observado. Detectar señales implícitas de demanda en el comportamiento histórico del cliente XYZn es precisamente uno de los valores del servicio de Triple S.

- **[RESUELTO]** ¿Existen cantidades mínimas de pedido contractuales?

  Algunas empresas ABC operan con **cantidades mínimas contractuales** (línea base) acordadas con sus clientes XYZn. Sin embargo, este mínimo **no siempre se respeta** en la práctica — a veces el cliente pide por encima, otras por debajo o no pide. El sistema las trata como:

  | Situación | Tratamiento |
  |---|---|
  | Pedido ≥ mínimo contractual | Registro normal |
  | Pedido < mínimo contractual | Se registra y se señala como desviación respecto a la línea base |
  | Período sin pedido (debería haberlo) | Se registra como brecha — afecta la dimensión de Continuidad del ISD |

  Si el cliente ABC proporciona los mínimos contractuales, el sistema los incorpora como variable adicional al modelo de pronóstico.

- **[RESUELTO]** ¿Cómo se detecta y trata un pedido extraordinario o atípico?

  Los pedidos atípicos pueden ser **legítimos** (campañas de ventas, temporadas especiales, primas de fin de año) o **errores de datos** (digitación incorrecta). El sistema los distingue así:

  ```
  DETECCIÓN
  Un pedido es marcado como atípico cuando su cantidad supera
  N desviaciones estándar del promedio histórico de esa combinación
  cliente × producto (umbral a calibrar por cliente)

  CLASIFICACIÓN
  ┌─ ¿Coincide con un evento conocido?
  │   (fin de año, festivo, campaña registrada)
  │   → SÍ: Pedido extraordinario legítimo
  │         Se incorpora al modelo como evento estacional
  │
  └─ ¿No hay evento que lo explique?
      → Se marca como anomalía y se presenta al cliente ABC
        para que confirme si es real o un error de datos
  ```

  **Ejemplo real:** empresas XYZn que aumentan sus pedidos a finales de año por campañas de ventas más agresivas asociadas a primas navideñas. El sistema aprende este patrón y lo anticipa en el pronóstico del siguiente año.

### 2.5 Arquitectura del Sistema

- **[RESUELTO]** ¿Cuál es el stack tecnológico?

  El desarrollo se divide en **tres fases progresivas**:

  **Fase 1 — Excel / CSV**
  Sin tecnología adicional. Los agentes procesan datos y entregan pronósticos en archivos estructurados. El cliente los consume en su herramienta habitual. Objetivo: validar el modelo con datos reales.

  **Fase 2 — Streamlit**
  Aplicación web ligera en Python. El cliente visualiza pronósticos, índice de salud de datos y alertas de forma interactiva. Objetivo: educar al cliente y demostrar el valor del servicio.

  **Fase 3 — Solución Definitiva**

  ```
  ┌─────────────────────────────────────────────────────────────┐
  │  CAPA DE PRESENTACIÓN                                        │
  │  Dashboard cliente:  React + Recharts                        │
  │  Portal interno TS:  Streamlit (operaciones de Triple S)     │
  ├─────────────────────────────────────────────────────────────┤
  │  CAPA DE APLICACIÓN                                          │
  │  API backend:        FastAPI (Python)                        │
  │  Autenticación:      Supabase Auth (multi-tenant)            │
  │  Notificaciones:     SendGrid (correos automáticos)          │
  │  Pagos:              Stripe (suscripciones y cargos)         │
  ├─────────────────────────────────────────────────────────────┤
  │  CAPA DE AGENTES / IA                                        │
  │  Harness agentico:   Python + Claude API (Anthropic)         │
  │  Pronóstico:         Prophet + statsforecast + scikit-learn  │
  │  Orquestación:       Prefect (pipelines y schedules)         │
  ├─────────────────────────────────────────────────────────────┤
  │  CAPA DE DATOS                                               │
  │  Bronce (archivos):  Supabase Storage (S3-compatible)        │
  │  Plata / Oro:        DuckDB (analítico, embebido)            │
  │  Transaccional:      Supabase PostgreSQL                     │
  ├─────────────────────────────────────────────────────────────┤
  │  INFRAESTRUCTURA                                             │
  │  Contenedores:       Docker + Docker Compose                 │
  │  Despliegue inicial: Railway o Render (simple y económico)   │
  │  Despliegue futuro:  AWS ECS (cuando la escala lo requiera)  │
  └─────────────────────────────────────────────────────────────┘
  ```

  **Supabase como plataforma central:** consolida autenticación, base de datos PostgreSQL y almacenamiento de archivos en un solo proveedor — una sola factura, una sola plataforma para el equipo de Triple S. Supabase Storage es compatible con la API de S3, lo que facilita la migración a AWS S3 en el futuro si el volumen lo requiere, sin cambios en el código.

  | Componente | Tecnología | Razón |
  |---|---|---|
  | Lenguaje | Python (todas las fases) | Consistencia entre fases — el equipo no cambia de lenguaje |
  | Backend | FastAPI | Ligero, rápido, nativo en Python |
  | Datos analíticos | DuckDB | Sin servidor que mantener — ideal para el medallón Bronce/Plata/Oro |
  | Datos transaccionales | Supabase PostgreSQL | Robusto y estándar para clientes, pagos y maestros |
  | Almacenamiento archivos | Supabase Storage | S3-compatible, integrado con auth y sin cuenta AWS inicial |
  | Orquestación | Prefect | Más simple que Airflow para equipos pequeños |
  | Pagos | Stripe | Líder global en suscripciones, documentación excelente |
- **[RESUELTO]** ¿Cómo consume el cliente los resultados? Ver bloque 2.1 — tres canales: dashboard de solo lectura, correo automático y archivo exportable Excel/CSV.

- **[RESUELTO]** ¿Cuáles son los requisitos de latencia del servicio?

  | Proceso | Latencia comprometida |
  |---|---|
  | Carga del dashboard | < 3 segundos |
  | Procesamiento de datos recibidos del cliente | < 24 horas desde la recepción |
  | Recálculo del ISD tras actualización de datos | < 4 horas |
  | Envío de correo automático al publicar pronóstico | < 1 hora desde la publicación |
  | Notificaciones de pago (alertas verdes/amarillas) | Inmediato — disparado por la pasarela |
  | Entrega del pronóstico mensual | Primeros 5 días hábiles del mes |

- **[RESUELTO]** ¿Existen restricciones de seguridad o residencia de datos?

  | Capa | Medida |
  |---|---|
  | **Transporte** | HTTPS/TLS en todas las comunicaciones — sin excepciones |
  | **Autenticación** | Supabase Auth con JWT — sesiones seguras por cliente |
  | **Contraseñas** | Hashing con bcrypt — nunca almacenadas en texto plano |
  | **Acceso interno Triple S** | Roles diferenciados — acceso mínimo necesario por función |
  | **Auditoría** | Log de accesos a datos sensibles — quién accedió, cuándo y qué consultó |
  | **Datos en reposo** | Cifrado en Supabase Storage y PostgreSQL |

  Residencia de datos: sin restricciones estrictas en la fase inicial. GDPR y normativas locales se abordan cuando lleguen clientes en jurisdicciones que lo requieran.

- **[RESUELTO]** ¿Cómo se garantiza el aislamiento de datos entre clientes?

  Tres capas de aislamiento complementarias:

  ```
  CAPA 1 — PostgreSQL (datos transaccionales)
    Row Level Security (RLS) de Supabase
    Cada registro tiene un tenant_id
    Política RLS: cada cliente solo ve sus propios registros
    → Imposible acceder a datos de otro cliente

  CAPA 2 — Supabase Storage (archivos Bronce)
    Carpeta dedicada: /clientes/{tenant_id}/bronce/
    Políticas de acceso por carpeta
    → Archivos de un cliente no visibles para otros

  CAPA 3 — DuckDB (datos analíticos Plata/Oro)
    Archivo DuckDB independiente por cliente
    → Separación física de datos analíticos
    → Sin riesgo de contaminación entre modelos
  ```

  Ningún cliente puede ver, acceder ni interferir con los datos de otro — ni por error ni intencionalmente.

### 2.6 Usuarios y Partes Interesadas

- **[RESUELTO]** ¿Quiénes son los usuarios principales dentro de cada empresa ABC?

  El dashboard tiene **cinco perfiles de usuario**, con el planificador de demanda como usuario central:

  | Rol | Tipo de uso | Frecuencia |
  |---|---|---|
  | **Planificador de demanda** | Usuario principal — construye el plan mensual directamente a partir del pronóstico por SKU | Diaria |
  | **Jefe de compras / materiales** | Programa órdenes de materia prima usando el pronóstico + lead time por combinación cliente × producto | Semanal |
  | **Gerente de producción** | Define la carga de producción mensual con el pronóstico como insumo | Mensual |
  | **Gerente de supply chain** | Vista estratégica — pronósticos agregados por categoría y cliente consolidado | Mensual |
  | **Directivo / gerencia general** | Consumo ocasional — resumen ejecutivo sin detalle SKU | Mensual |

  **Implicación para el dashboard:** se requieren vistas diferenciadas por rol. El planificador necesita detalle SKU por combinación cliente × producto. El directivo necesita agregados con indicadores de alerta. No todos los roles necesitan ver el mismo nivel de granularidad.

- **[RESUELTO]** ¿Qué decisiones concretas toma el cliente a partir del pronóstico?

  Los cinco beneficios del servicio declarados en la visión del producto se traducen en cinco decisiones operativas concretas:

  | Decisión | Quién la toma | Insumo del pronóstico |
  |---|---|---|
  | **¿Cuánto producir?** | Gerente de producción | Pronóstico por SKU para el horizonte configurado |
  | **¿Cuándo comprar materia prima?** | Jefe de compras | Pronóstico + lead time por combinación cliente × producto (DEC-011) |
  | **¿Qué nivel de inventario mantener?** | Planificador / supply chain | Pronóstico + stock_minimo del Esquema 2 → punto de reorden |
  | **¿Qué comprometer con el cliente XYZ?** | Equipo comercial de ABC | Pronóstico de demanda esperada → promesas de entrega más confiables |
  | **¿Qué productos o clientes priorizar si hay restricción de capacidad?** | Gerencia / producción | Pronóstico por categoría → priorización cuando no se puede producir todo |

- **[RESUELTO]** ¿Qué nivel de explicabilidad se requiere?

  **Nivel intermedio: interpretable pero no técnico.** El cliente no es un equipo de ciencia de datos — el dashboard está diseñado para consumo sin capacitación técnica. El patrón ya establecido en el ISD (número global + causa principal + acción sugerida) se aplica de la misma forma al pronóstico.

  **Qué se muestra junto al pronóstico:**

  | Elemento | Ejemplo |
  |---|---|
  | Número del pronóstico | 820 unidades de PRD1 para julio |
  | Nivel de confianza | Alta confianza (historial ≥ 3 años) |
  | Tendencia reciente | La demanda de PRD1 lleva 3 meses en descenso |
  | Evento activo (si existe) | Este mes incluye efecto de fin de año detectado en historial |
  | Anomalía reciente (si existe) | El pedido de XYZ3 del mes pasado fue atípico y fue excluido del modelo |

  **Qué no se muestra:**
  - Coeficientes o parámetros del modelo (Prophet, statsforecast)
  - Feature importances
  - Intervalos de confianza estadísticos en formato técnico

  El nivel de explicabilidad es suficiente para que el cliente **entienda por qué el número es ese** y pueda actuar con confianza, sin necesitar entender el modelo.

- **[RESUELTO]** ¿Existen KPIs internos de Triple S adicionales a los SLAs del contrato?

  Los SLAs (MAPE, disponibilidad, tiempos de respuesta) son compromisos con el cliente. Los KPIs internos son métricas de salud del negocio de Triple S:

  | KPI | Qué mide | Por qué importa para Triple S |
  |---|---|---|
  | **Tasa de conversión onboarding → activo** | % de clientes mes 1 gratuito que pagan mes 2 | Valida si el mes gratuito convierte — es la principal palanca de crecimiento |
  | **Tiempo promedio de primer pronóstico** | Días desde la ingesta hasta el primer pronóstico entregado | Mide eficiencia operativa del harness — el objetivo es antes del mes 3 |
  | **Tasa de retención mensual (churn)** | % de clientes activos que no renuevan | KPI central de cualquier modelo de suscripción |
  | **Evolución promedio del ISD por cohorte** | ISD promedio a mes 1, 3 y 6 de cada cohorte de clientes | Valida que el servicio mejora la calidad de datos del cliente — proxy de fidelización |
  | **MAPE real vs. comprometido** | Precisión real del modelo vs. el SLA firmado | Triple S debe detectar desviaciones antes que el cliente las note |
  | **Distribución de planes (mensual / trimestral / anual)** | % de clientes en cada plan de pago | Plan mensual genera churn más fácil; plan anual da estabilidad de flujo de caja |

### 2.7 Diseño de Agentes

- **[RESUELTO]** ¿Qué agentes especializados requerirá el harness?

  El sistema se divide en **11 harnesses operacionales**, cada uno con responsabilidad única (ver DEC-024):

  | # | Nombre | Responsabilidad |
  |---|--------|----------------|
  | 010 | Discovery | Contexto del cliente, criterios de éxito, configuración de onboarding |
  | 015 | Intake | Recepción y validación de datos, copia Bronze |
  | 020 | Diagnosis | Cálculo del ISD desde Bronze (6 dimensiones) |
  | 025 | Refinery | Limpieza Bronze→Silver→Gold + extracción de maestros |
  | 030 | Trainer | Feature engineering + entrenamiento de modelos |
  | 035 | Predictor | Inferencia mensual + detección y clasificación de anomalías |
  | 040 | Publisher | Dashboard + correo automático + exportable |
  | 045 | Monitor | MAPE real vs. comprometido, deriva de modelos, salud del pipeline |
  | 050 | Lifecycle | Ciclo de vida del cliente, pagos, alertas, suspensión |
  | 055 | Command | Operaciones internas Triple S, 6 KPIs |
  | 060 | Simulator | Escenarios what-if predefinidos (Opción C — ver DEC-025) |

- **[RESUELTO]** ¿Cómo deben coordinarse los agentes?

  Tres patrones de coordinación coexisten según la naturaleza de cada harness:

  **Pipeline secuencial con fork paralelo** (flujo principal de datos):
  ```
  015 Intake → { 020 Diagnosis ∥ 025 Refinery } → 030 Trainer → 035 Predictor → 040 Publisher
  ```
  020 y 025 corren en paralelo porque ambos leen desde Bronze de forma independiente. 020 no espera a 025 — el diagnóstico de salud se hace sobre los datos originales, no sobre los datos limpios.

  **Event-driven** (disparados por eventos externos, no por el pipeline):
  - 050 Lifecycle: se activa ante eventos de pago (Stripe webhook), verificación diaria de vencimientos
  - 055 Command: se actualiza ante cualquier evento del sistema (pronóstico publicado, pago recibido, cancelación)
  - 050 puede bloquear a 040 Publisher si el cliente está suspendido

  **On-demand** (ejecutado por solicitud interna de Triple S):
  - 060 Simulator: corre mensualmente junto al ciclo de 035 → 040, pero sus artefactos son independientes de los pronósticos oficiales

- **[RESUELTO]** ¿Cuál es la cadencia de reentrenamiento y repronóstico?

  | Harness | Cadencia | Condición |
  |---------|----------|-----------|
  | 030 Trainer (reentrenamiento) | Semanal | Solo en clientes con Modo Incremental activo |
  | 030 Trainer (reentrenamiento) | On-demand | Cuando el cliente entrega un nuevo archivo Batch completo |
  | 035 Predictor (inferencia) | Mensual | Primeros 5 días hábiles del mes, para todos los clientes |
  | 020 Diagnosis (ISD) | Por ingesta + mensual | Recálculo inmediato ante cada actualización de datos |

  El reentrenamiento (030) y la inferencia (035) tienen ciclos independientes: el modelo puede reentrenarse un miércoles y la inferencia mensual ocurrir el siguiente lunes — usa el modelo más reciente disponible en ese momento.

- **[RESUELTO]** ¿Cómo maneja el sistema el cold start?

  Ver sección 2.2 — estrategia en cascada ya definida: (1) analogía por categoría, (2) analogía por cliente, (3) acumulación mínima de 3 meses. El harness 030 Trainer evalúa el historial disponible por combinación cliente × producto y selecciona el nivel de la cascada correspondiente. El nivel activo se comunica al 040 Publisher para mostrarlo en el dashboard con el nivel de confianza ajustado.

- **[RESUELTO]** ¿En qué orden se construyen los harnesses?

  Los 11 harnesses se construyen en 5 bloques ordenados por valor entregable (ver DEC-026):

  | Bloque | Harnesses | Hito |
  |--------|-----------|------|
  | **A** | 010 → 015 → 020 | Primer piloto ejecutable: recibir datos y entregar ISD al cliente |
  | **C** | 050 Lifecycle | Listo para cobrar: gestión de pagos y estados operativa antes del primer pago |
  | **B** | 025 → 030 → 035 → 040 | Ciclo de valor completo: primer pronóstico entregado |
  | **D** | 045 → 055 | Excelencia operativa: monitoreo y KPIs internos activos |
  | **E** | 060 Simulator | Funcionalidad avanzada: escenarios what-if disponibles |

  El Bloque C (050 Lifecycle) se construye después del Bloque A y en paralelo con el inicio del Bloque B — el mes 1 gratuito de onboarding provee el margen de tiempo necesario para tenerlo listo antes del primer cobro.

### 2.8 Integración y Operaciones

- **[RESUELTO]** ¿El pronóstico necesita escribirse de vuelta en el ERP del cliente automáticamente?

  **No en el alcance inicial.** El modelo Service as a Software no contempla integración bidireccional con sistemas del cliente — Triple S entrega resultados, el cliente los consume. La integración con ERP (SAP, Oracle, Dynamics) se define como ruta Enterprise en fases posteriores (ver sección 2.2 — fuentes de datos). El canal de exportación Excel/CSV del 040 Publisher cubre el caso de uso de importación manual al ERP del cliente sin requerir integración técnica.

- **[RESUELTO]** ¿Quién monitorea la salud de los agentes y la deriva del pronóstico?

  **Triple S es el único responsable** — coherente con el modelo Service as a Software. El cliente no tiene visibilidad de la salud interna del sistema, solo de sus resultados. Dos harnesses cubren esta responsabilidad:

  | Harness | Qué monitorea | Audiencia |
  |---------|--------------|-----------|
  | 045 Monitor | MAPE real vs. comprometido, deriva de modelos, fallos de pipeline, latencias vs. SLA | Triple S (operaciones técnicas) |
  | 055 Command | 6 KPIs de negocio: conversión, churn, tiempo primer pronóstico, evolución ISD, distribución de planes | Triple S (gerencia y producto) |

- **[RESUELTO]** ¿Cuál es el protocolo de escalamiento ante un resultado sospechoso?

  El 045 Monitor detecta anomalías en los outputs del 035 Predictor antes de que lleguen al 040 Publisher. El protocolo tiene tres niveles:

  ```
  NIVEL 1 — Alerta automática (045 Monitor)
  MAPE de validación supera el umbral del SLA comprometido para ese cliente
  → Bloqueo de publicación automática
  → Notificación al equipo técnico de Triple S

  NIVEL 2 — Revisión humana (equipo Triple S)
  Triple S revisa el pronóstico, identifica la causa
  → Opción A: corregir y re-ejecutar 035 Predictor
  → Opción B: publicar con nota de alerta al cliente si el plazo SLA está en riesgo

  NIVEL 3 — Notificación al cliente (si impacta el SLA)
  Si la resolución supera los 5 días hábiles del SLA de entrega
  → Triple S notifica al cliente con tiempo estimado de resolución
  → Se registra como incidente en el contrato de servicio
  ```

- **[PENDIENTE]** ¿Se requiere aprobación humana antes de publicar un pronóstico al cliente?

  Decisión pendiente. Las opciones son:

  | Opción | Descripción | Implicación operativa |
  |--------|-------------|----------------------|
  | **A — Publicación automática** | Si 045 Monitor no bloquea, 040 Publisher publica sin intervención | Escala sin fricción — no requiere operador disponible |
  | **B — Aprobación manual siempre** | Un operador de Triple S revisa y aprueba cada pronóstico antes de publicar | Control total pero requiere capacidad operativa por cliente |
  | **C — Híbrido por confianza** | Auto-publicación si confianza alta y sin alertas; revisión manual si confianza reducida, primer pronóstico del cliente, o alerta activa | Balance entre escala y control |

  La Opción C es la recomendada para la Fase 3. Para la Fase 1 (Excel/CSV) con pocos clientes piloto, la Opción B es práctica.

---

---

**Nombre del sistema:** FARO — **F**orecasting **A**gentic **R**esults & **O**perations  
**Decisión registrada:** DEC-029 en `progress/decisions.md`

*Este documento es un artefacto vivo. Las secciones se actualizarán a medida que se confirmen respuestas y se tomen decisiones de diseño.*
