# Comparativo: Datup.ai vs FARO (Triple S)

> **Fecha:** 11 de junio de 2026  
> **Propósito:** Análisis comparativo entre la solución de Datup.ai y la propuesta de FARO por Sabbia Solutions & Software (Triple S)

---

## 1. Perfil de Datup.ai — Resumen Ejecutivo

| Atributo | Detalle |
|---|---|
| **Nombre** | Datup |
| **Fundación** | 2019, Bogotá, Colombia |
| **Modelo** | B2B SaaS — AI as a Service (AIaaS) |
| **Empleados** | ~20 personas |
| **ARR** | ~$2.2M USD (sept. 2025) |
| **Valoración** | ~$6.6M USD |
| **Financiamiento** | Bootstrapped + AWS GenAI Accelerator 2024 |
| **Fundadores** | Felipe Hernández Anzola, Paola Serna, Jullie Torres, Ramiro Chaparro Vargas |
| **Mercado** | LATAM y Europa |
| **Idiomas** | Español, Inglés, Portugués |

### Qué ofrece Datup

Datup es una plataforma SaaS de **Supply Chain Analytics con IA** que permite a empresas de manufactura, retail, consumo masivo y farmacéutica:

1. **Planificar la demanda** con pronósticos de deep learning (+95% precisión, +200 variables externas)
2. **Gestionar inventarios** con puntos de reorden y stock de seguridad dinámico
3. **Optimizar compras** con órdenes basadas en pronósticos
4. **Distribuir inventario** entre ubicaciones priorizando demanda
5. **Rankear el portafolio** con clasificación ABC/FSN/XYZ
6. **Colaborar en S&OP/S&OE** cross-funcional
7. **Consultar vía IA** a través de "Alaia", asistente con notificaciones por WhatsApp/email

### Clientes notables de Datup

Grupo Bimbo, Juan Valdez, Colgate, Colsubsidio, Crepes & Waffles, Edgewell, Nutresa, Procaps, L'Occitane, Faber-Castell, Simoniz, Disfarma, Prebel, Gabrica.

### Resultados documentados

| Cliente | Resultado |
|---|---|
| Simoniz | +85% precisión en pronósticos |
| Casa Limpia | +10% calidad de entregas (8 semanas de implementación) |
| Comfandi | Optimización de capital de trabajo |
| Juan Valdez | Monitoreo de mercado, precio competitivo |

### Integraciones

SAP (S/4HANA, Business One), Oracle (Cloud, NetSuite), Microsoft Dynamics 365, Siesa, Odoo.

---

## 2. Perfil de FARO (Triple S) — Resumen Ejecutivo

| Atributo | Detalle |
|---|---|
| **Nombre** | FARO — Forecasting Agentic Results & Operations |
| **Empresa** | Sabbia Solutions & Software (Triple S) |
| **Modelo** | **Service as a Software (SaaSw)** — el cliente recibe el resultado, no la herramienta |
| **Etapa** | Pre-lanzamiento (en diseño y construcción) |
| **Mercado objetivo** | Empresas manufactureras B2B en LATAM |
| **Enfoque** | Pronóstico de demanda B2B puro (cliente × producto × ubicación) |

### Qué ofrece FARO

FARO es un **servicio gestionado** de pronóstico de demanda donde Triple S opera todo el ciclo:

1. **Ingesta y diagnóstico de datos** con Índice de Salud de Datos (ISD) de 6 dimensiones
2. **Transformación Bronce → Plata → Oro** con arquitectura medallion
3. **Pronósticos por combinación** cliente × producto × sede × horizonte
4. **Detección de anomalías** y clasificación de pedidos atípicos
5. **Estrategia de cold start** en cascada para productos sin historial
6. **Escenarios what-if** (simulador)
7. **Dashboard de solo lectura** + correo automático + exportación Excel/CSV

### Modelo de agentes (11 harnesses)

| # | Harness | Responsabilidad |
|---|---|---|
| 010 | Discovery | Contexto del cliente, onboarding |
| 015 | Intake | Recepción y validación de datos |
| 020 | Diagnosis | Cálculo del ISD |
| 025 | Refinery | Limpieza Bronce→Plata→Oro |
| 030 | Trainer | Feature engineering + entrenamiento |
| 035 | Predictor | Inferencia + detección de anomalías |
| 040 | Publisher | Dashboard + correo + exportación |
| 045 | Monitor | MAPE, deriva, salud del pipeline |
| 050 | Lifecycle | Pagos, alertas, suspensión |
| 055 | Command | KPIs internos de Triple S |
| 060 | Simulator | Escenarios what-if |

---

## 3. Comparación por Dimensiones

### 3.1 Modelo de Negocio

| Dimensión | **Datup.ai** | **FARO (Triple S)** |
|---|---|---|
| **Modelo** | SaaS tradicional — el cliente opera la plataforma | **SaaSw** — Triple S opera todo, el cliente consume resultados |
| **Quién opera** | El propio equipo del cliente | **Triple S exclusivamente** |
| **Responsabilidad** | Compartida — el cliente configura y usa | **De punta a punta** — Triple S es responsable del resultado |
| **Lo que recibe el cliente** | Acceso a una plataforma con herramientas | **Pronósticos listos para usar** |
| **Curva de aprendizaje para el cliente** | Media — debe aprender la plataforma | **Mínima** — solo interpretar pronósticos |

> **🏆 Ventaja FARO:** El modelo SaaSw elimina la fricción operativa del cliente. No necesita personal técnico ni capacitación en la herramienta. Esto es especialmente valioso para empresas manufactureras B2B que no tienen equipos de data science.

> **🏆 Ventaja Datup:** El modelo SaaS da más control al cliente. Puede explorar datos, ajustar pronósticos y colaborar internamente dentro de la plataforma.

---

### 3.2 Alcance del Producto

| Funcionalidad | **Datup.ai** | **FARO (Triple S)** |
|---|---|---|
| **Pronóstico de demanda** | ✅ Deep learning + 200 variables externas | ✅ Prophet + statsforecast + scikit-learn |
| **Gestión de inventarios** | ✅ Puntos de reorden, stock de seguridad dinámico | ⚠️ Indirecto — calcula sobre-inventario/agotados con datos opcionales |
| **Órdenes de compra automatizadas** | ✅ | ❌ No está en el alcance |
| **Distribución entre ubicaciones** | ✅ Priorización por demanda | ❌ No está en el alcance |
| **Ranking de portafolio (ABC/FSN/XYZ)** | ✅ | ❌ No está en el alcance |
| **S&OP / S&OE colaborativo** | ✅ Multi-equipo | ❌ No está en el alcance — dashboard solo lectura |
| **Asistente IA conversacional** | ✅ "Alaia" con WhatsApp/email | ❌ No incluido |
| **Detección de anomalías** | ⚠️ Implícito en la plataforma | ✅ Explícito con clasificación (legítimo vs. error de datos) |
| **Diagnóstico de salud de datos (ISD)** | ❌ No mencionado | ✅ 6 dimensiones, 0-100%, evolución histórica |
| **Escenarios what-if** | ❌ No mencionado públicamente | ✅ Simulador (Harness 060) |
| **Cold start / productos nuevos** | ✅ Pronóstico de productos nuevos | ✅ Cascada en 3 pasos con transparencia al cliente |
| **Gestión de suscripción y pagos** | ❌ Es un proceso externo | ✅ Integrado al sistema (Harness 050 Lifecycle) |
| **Variables externas (clima, inflación)** | ✅ +200 variables | ❌ No explícito — basado solo en historial de pedidos |
| **Pronóstico por cliente×producto×sede** | ✅ Por producto × ubicación | ✅ Por cliente × producto × sede (mayor granularidad B2B) |

> **🏆 Ventaja Datup:** Alcance mucho más amplio — cubre toda la cadena de suministro (demanda → inventario → compras → distribución → portafolio → S&OP). Es una plataforma "todo en uno".

> **🏆 Ventaja FARO:** Mayor profundidad en el pronóstico B2B puro. La granularidad cliente × producto × sede y la estrategia de cold start en cascada son más sofisticadas para el caso B2B específico. El ISD es un diferenciador claro que genera valor desde el día 1.

---

### 3.3 Tecnología

| Dimensión | **Datup.ai** | **FARO (Triple S)** |
|---|---|---|
| **IA / ML** | Deep learning propietario | Prophet + statsforecast + scikit-learn |
| **Variables externas** | +200 (inflación, clima, lead times, política) | Solo historial de pedidos del cliente |
| **Infraestructura** | Cloud-native (AWS) | Docker → Railway/Render → AWS ECS (progresivo) |
| **Base de datos** | No público | Supabase PostgreSQL + DuckDB (medallion) |
| **Almacenamiento** | No público | Supabase Storage (S3-compatible) |
| **Backend** | No público | FastAPI (Python) |
| **Frontend** | Webflow (sitio) + plataforma propietaria | React + Recharts (dashboard) + Streamlit (interno) |
| **Orquestación** | No público | Prefect |
| **Pagos** | Pasarela no especificada | Stripe |
| **Autenticación** | No público | Supabase Auth (multi-tenant, JWT, RLS) |
| **Agentes de IA** | No mencionado como arquitectura | 11 harnesses especializados con Claude API (Anthropic) |
| **Aislamiento de datos** | No público | 3 capas (RLS + Storage por tenant + DuckDB por cliente) |

> **🏆 Ventaja Datup:** Deep learning propietario + 200 variables externas es una capacidad técnica significativa que enriquece los pronósticos más allá del historial del cliente.

> **🏆 Ventaja FARO:** Arquitectura transparente, moderna y bien documentada. Los 11 harnesses con orquestación específica (pipeline + event-driven + on-demand) son un diseño arquitectónico sofisticado. El aislamiento de datos en 3 capas es robusto.

---

### 3.4 Gestión de Datos

| Dimensión | **Datup.ai** | **FARO (Triple S)** |
|---|---|---|
| **Diagnóstico de calidad de datos** | No mencionado como servicio explícito | ✅ ISD con 6 dimensiones ponderadas |
| **Arquitectura de datos** | Integración plug & play | Medallion (Bronce → Plata → Oro) |
| **Datos originales del cliente** | Se integran a la plataforma | **Intocables** — Triple S trabaja siempre sobre copias |
| **Maestro de datos** | El cliente lo tiene en su ERP | **Triple S lo construye automáticamente** |
| **Fuentes aceptadas** | ERP, CRM, WMS, TMS (integración directa) | CSV/Excel → Base de datos → ERP (progresivo, 3 fases) |
| **Modos de ingesta** | Integración continua | Batch (archivo completo) + Incremental (actualizaciones) |
| **Transparencia al cliente sobre sus datos** | El cliente ve dashboards de la plataforma | ISD detallado + evolución mensual + acción sugerida |
| **Incentivo para mejorar datos** | Implícito | **Explícito** — a mejor ISD, menor cargo de complejidad |

> **🏆 Ventaja Datup:** Integración directa con ERPs desde el día 1. El cliente no tiene que exportar archivos — Datup se conecta a sus sistemas.

> **🏆 Ventaja FARO:** El ISD es un concepto original que genera valor independiente del pronóstico. Crear un incentivo económico directo (menor cargo por mejor salud de datos) es brillante como mecanismo de fidelización y mejora continua.

---

### 3.5 Precios y Modelo Comercial

| Dimensión | **Datup.ai** | **FARO (Triple S)** |
|---|---|---|
| **Precio base** | No público (suscripción mensual) | USD 200 – 500 / mes según tamaño (M, L, XL) |
| **Usuarios** | **Sin límite** | 5 perfiles de usuario por empresa |
| **Permanencia** | **Sin cláusula** | Sin permanencia (pero planes trimestrales y anuales con descuento) |
| **Descuentos** | No especificados | 8% trimestral, 18% anual |
| **Cargo variable** | No mencionado | Cargo por complejidad de datos (0% – 80% según ISD) |
| **Mes gratuito** | No mencionado | ✅ Primer mes de onboarding sin costo |
| **Pasarela de pagos** | No especificada | Stripe (automatizada) |
| **Gestión de mora** | No detallada | Ciclo completo: verde→amarillo→suspensión con reglas claras |
| **Retención post-cancelación** | No pública | 6 meses con ventana de exportación de 3 meses |

> **🏆 Ventaja Datup:** Usuarios ilimitados elimina la fricción de adopción interna. El cliente no tiene que elegir quién accede.

> **🏆 Ventaja FARO:** Precios públicos y transparentes (USD 200–500). El argumento de valor es poderoso: USD 500 ≈ 1 salario mínimo colombiano, vs. el triple para un profesional de pronóstico. El mes gratuito reduce la fricción de venta dramáticamente. El cargo variable por complejidad de datos es un modelo innovador.

---

### 3.6 Implementación y Onboarding

| Dimensión | **Datup.ai** | **FARO (Triple S)** |
|---|---|---|
| **Tiempo de implementación** | **5 semanas** | Hasta **3 meses** (mes 1 gratuito + mes 2 primer pago + mes 3 primer pronóstico) |
| **Qué hace el cliente** | Conectar su ERP y comenzar a usar | Entregar datos → recibir diagnóstico → esperar pronóstico |
| **Primer valor entregado** | Al conectar datos (~5 semanas) | Diagnóstico de salud de datos (mes 1, gratuito) |
| **Primer pronóstico** | ~5 semanas | Antes del mes 3 |
| **Período de prueba** | No mencionado | Mes 1 gratuito funciona como piloto |

> **🏆 Ventaja Datup:** 5 semanas es significativamente más rápido que hasta 3 meses. En ventas enterprise, la velocidad de time-to-value es un factor crítico.

> **🏆 Ventaja FARO:** El mes gratuito con diagnóstico de salud de datos entrega valor real antes del primer pago. Nadie más ofrece esto.

---

### 3.7 Clientes Objetivo y Go-to-Market

| Dimensión | **Datup.ai** | **FARO (Triple S)** |
|---|---|---|
| **Industrias** | Manufactura, retail, consumo masivo, farmacéutica, distribución, food service | **Solo manufactura B2B** |
| **Tipo de venta** | B2C y B2B (retail + manufactura) | **Exclusivamente B2B** |
| **Geografía** | LATAM + Europa | LATAM (inicio en Colombia) |
| **Tamaño de empresa** | Medianas y grandes | M, L y XL (definidas por ITO) |
| **Canales de adquisición** | Content marketing, SEO, blog, calculadoras, demos interactivas, partners ERP, LinkedIn | En diseño |
| **Clientes existentes** | +15 empresas notables documentadas | 0 (pre-lanzamiento) |
| **Track record** | 7 años de operación, $2.2M ARR | Sin historial |

> **🏆 Ventaja Datup:** 7 años de track record, clientes reconocidos, revenue probado. En ventas B2B enterprise, la credibilidad es todo.

> **🏆 Ventaja FARO:** Enfoque quirúrgico en manufactura B2B. No diluye su propuesta intentando servir retail, food service, etc. La granularidad cliente × producto × sede es nativa del diseño B2B.

---

### 3.8 Entrega de Resultados

| Dimensión | **Datup.ai** | **FARO (Triple S)** |
|---|---|---|
| **Canal principal** | Plataforma SaaS interactiva (el cliente opera) | Dashboard de solo lectura (el cliente consume) |
| **Correo automático** | ⚠️ No detallado como canal | ✅ Resumen ejecutivo al publicar cada pronóstico |
| **Exportación** | Implícito en la plataforma | ✅ Excel / CSV descargable |
| **API** | No mencionado | **Explícitamente excluida** por diseño (contradice el modelo SaaSw) |
| **WhatsApp** | ✅ Notificaciones proactivas vía Alaia | ❌ No incluido |
| **Frecuencia** | Continua (plataforma siempre activa) | **Mensual** (primeros 5 días hábiles) |
| **Explicabilidad** | No detallada | ✅ Nivel intermedio: número + confianza + tendencia + eventos + anomalías |
| **SLAs** | No públicos | 6 SLAs documentados (MAPE, disponibilidad, tiempos de respuesta) |

---

## 4. Matriz Comparativa Resumida

| Criterio | **Datup.ai** | **FARO (Triple S)** | ¿Quién gana? |
|---|:---:|:---:|:---:|
| Modelo de negocio (SaaS vs SaaSw) | SaaS | SaaSw | **Depende del cliente** |
| Amplitud de producto | 🟢🟢🟢🟢🟢 | 🟢🟢🟢 | **Datup** |
| Profundidad en pronóstico B2B | 🟢🟢🟢 | 🟢🟢🟢🟢🟢 | **FARO** |
| Variables externas (+200) | 🟢🟢🟢🟢🟢 | 🟢 | **Datup** |
| Diagnóstico de salud de datos | 🟢 | 🟢🟢🟢🟢🟢 | **FARO** |
| Velocidad de implementación | 🟢🟢🟢🟢🟢 | 🟢🟢🟢 | **Datup** |
| Precio accesible y transparente | 🟢🟢🟢 | 🟢🟢🟢🟢🟢 | **FARO** |
| Integraciones ERP nativas | 🟢🟢🟢🟢🟢 | 🟢🟢 | **Datup** |
| Track record / credibilidad | 🟢🟢🟢🟢🟢 | 🟢 | **Datup** |
| Asistente IA (Alaia/WhatsApp) | 🟢🟢🟢🟢🟢 | 🟢 | **Datup** |
| Detección de anomalías | 🟢🟢 | 🟢🟢🟢🟢🟢 | **FARO** |
| Cold start sofisticado | 🟢🟢🟢 | 🟢🟢🟢🟢🟢 | **FARO** |
| Gestión del ciclo de vida cliente | 🟢🟢 | 🟢🟢🟢🟢🟢 | **FARO** |
| Explicabilidad del pronóstico | 🟢🟢 | 🟢🟢🟢🟢 | **FARO** |
| Arquitectura agentic | 🟢 | 🟢🟢🟢🟢🟢 | **FARO** |
| Documentación de SLAs | 🟢🟢 | 🟢🟢🟢🟢🟢 | **FARO** |

---

## 5. Conclusiones Estratégicas

### 5.1 No son competidores directos (todavía)

Datup y FARO operan en **filosofías fundamentalmente distintas**:

| | Datup | FARO |
|---|---|---|
| **Filosofía** | "Te damos la herramienta para que planifiques" | "Te damos el resultado listo para usar" |
| **El cliente necesita** | Equipo interno que opere la plataforma | Solo alguien que lea y use el pronóstico |
| **Lo que escala** | Usuarios dentro de la plataforma | La capacidad de servicio de Triple S |

### 5.2 Lo que FARO debe aprender de Datup

1. **Variables externas:** Incorporar datos como inflación, clima, lead times de proveedores, eventos macroeconómicos. Esto enriquecería significativamente los pronósticos más allá del historial de pedidos.

2. **Velocidad de implementación:** 5 semanas vs. hasta 3 meses es una brecha real. Evaluar si el proceso de onboarding de FARO puede comprimirse sin sacrificar la calidad del diagnóstico.

3. **Asistente IA conversacional:** Un canal de WhatsApp/email proactivo con alertas y recomendaciones sería un diferenciador poderoso. El harness 040 Publisher podría integrar notificaciones inteligentes.

4. **Content marketing como motor de adquisición:** Datup usa calculadoras de ROI, herramientas gratuitas, cursos, blog e informes como generadores de leads. FARO debería replicar esta estrategia.

5. **Integraciones ERP nativas:** Aunque la Fase 1 de FARO es CSV, acelerar la ruta Enterprise (SAP, Oracle, Dynamics) es crítico para competir en el mercado mid-market.

6. **Demos interactivas en el sitio:** Datup usa Arcade y Supademo para demos embebidas. Esto reduce la fricción de venta significativamente.

### 5.3 Lo que FARO ya hace mejor que Datup

1. **Modelo SaaSw:** Para empresas sin equipo técnico, recibir el resultado listo es radicalmente más valioso que recibir una herramienta que deben aprender a operar. Es un posicionamiento audaz y diferenciado.

2. **Transparencia de precios:** Datup no publica precios. FARO publica rangos claros con una fórmula transparente (ITO). Esto genera confianza y reduce el ciclo de venta.

3. **Índice de Salud de Datos (ISD):** Nadie más ofrece un diagnóstico estructurado de la calidad de datos del cliente como servicio. Esto entrega valor desde el día 1 — incluso antes del primer pronóstico.

4. **Incentivo económico por calidad de datos:** El cargo variable por complejidad (0%–80%) es un modelo de pricing innovador que no existe en el mercado.

5. **Granularidad B2B nativa:** La combinación cliente × producto × sede × horizonte como unidad atómica de pronóstico es más granular y adecuada para manufactura B2B que el modelo producto × ubicación de Datup.

6. **Arquitectura agentic con 11 harnesses:** Es una arquitectura más sofisticada y especializada que una plataforma monolítica tradicional.

7. **SLAs explícitos y documentados:** 6 SLAs con métricas concretas (MAPE condicionado al ISD, 99% uptime, tiempos de respuesta por severidad) generan confianza contractual.

### 5.4 Oportunidades de diferenciación para FARO

| Oportunidad | Cómo aprovecharla |
|---|---|
| **"Nosotros hacemos todo, tú solo usas el número"** | Mensajería central. El cliente de manufactura B2B no quiere operar software — quiere que le digan cuánto producir |
| **El ISD como caballo de Troya** | El diagnóstico gratuito del mes 1 es el hook de venta. Nadie más le muestra al cliente el estado real de sus datos |
| **Pricing transparente** | "USD 200–500/mes vs. el costo de un profesional" es un argumento imbatible |
| **Enfoque B2B puro** | No intentar ser todo para todos. Datup diluye al cubrir retail, food service, etc. FARO es cirujano: manufactura B2B |
| **Cargo variable = alianza con el cliente** | "A mejores datos, menos pagas" alinea los incentivos cliente-proveedor como nadie más lo hace |

---

## 6. Riesgos Competitivos para FARO

| Riesgo | Severidad | Mitigación |
|---|:---:|---|
| Datup tiene 7 años de ventaja en mercado, clientes y reputación | 🔴 Alta | Diferenciarse por modelo (SaaSw), no competir en features |
| Datup ya tiene integraciones ERP nativas | 🟠 Media | Acelerar ruta Enterprise en FARO |
| Datup ofrece más funcionalidades (inventario, compras, distribución, S&OP) | 🟠 Media | No intentar replicar — mantener el foco en pronóstico B2B puro |
| 3 meses de onboarding puede ser lento vs. 5 semanas de Datup | 🟠 Media | Acelerar onboarding sin sacrificar ISD |
| Sin track record ni clientes existentes | 🔴 Alta | Primer cliente piloto es prioridad absoluta |
| Datup tiene variables externas (+200) que FARO no incluye | 🟡 Baja-Media | Evaluar incorporación incremental de variables externas relevantes para B2B |

---

*Documento generado como parte del análisis competitivo para el proyecto FARO de Sabbia Solutions & Software (Triple S).*
