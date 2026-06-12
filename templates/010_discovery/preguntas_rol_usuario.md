# Guía de Preguntas — Rol Usuario
## Harness 010 Discovery | FARO / Sabbia Solutions & Software

> **Para el discovery-interviewer:**
> El rol usuario es quien consume los pronósticos en su trabajo diario. No siempre es la misma persona que el rol negocio (que definió el problema) ni el rol técnico (que maneja los datos). El usuario es quien va a abrir el dashboard, leer el correo o descargar el Excel cada mes. Su perspectiva define qué tan útil es el resultado en la práctica.
>
> El rol usuario cubre: cómo toman decisiones hoy, qué información necesitan, en qué formato la consumen, a qué nivel de detalle la necesitan y con qué frecuencia.

---

## Bloque 1 — Cómo deciden hoy

### Pregunta de apertura
> "Cuéntame sobre tu semana típica: ¿en qué momento del mes necesitas saber cuánto se va a pedir o cuánto hay que producir? ¿Cómo obtienes esa información hoy?"

**Por qué abrir así:** Entiende el flujo de trabajo real, no el ideal. La respuesta revela cuándo se usa el pronóstico, quién lo genera hoy y qué fricción existe.

**Sondas de seguimiento:**
- "¿Cuánto tiempo te lleva hoy conseguir esa información?"
- "¿Esa información te llega de alguien más o la produces tú mismo?"
- "¿Qué tan confiable es esa información cuando la recibes? ¿Alguna vez te ha fallado?"

**Señales a escuchar:**
- "Yo hago el Excel todos los lunes" → el usuario es quien produce la estimación hoy; FARO reemplaza ese trabajo; confirmar su disposición
- "Me llega de [nombre]" → hay una fuente centralizada hoy; ese proceso va a cambiar
- "No tengo esa información, me entero después" → el usuario no toma decisiones proactivas; el valor de FARO para ellos es diferente

---

### Pregunta sobre decisiones concretas
> "¿Para qué usas exactamente esa estimación? ¿Qué decisión tomas con ella?"

**Por qué importa:** Define el horizonte de pronóstico y el nivel de detalle necesario. Alguien que ordena producción necesita SKU × semana. Alguien que aprueba presupuesto mensual puede necesitar solo totales por categoría.

**Sondas de seguimiento:**
- "¿Con cuánto tiempo de anticipación necesitas esa estimación para poder actuar?"
- "¿Hay una reunión o proceso específico donde uses ese número?"
- "¿Si el número está 15% desviado, eso te causa un problema real o lo absorbes?"

**Señales a escuchar:**
- "Planifico producción" → necesita SKU, horizonte semanal o mensual, con anticipación
- "Apruebo compras al proveedor" → necesita agregados, horizonte según lead time del proveedor
- "Reviso con la gerencia" → usa el pronóstico para reportar, no para operar; formato de resumen es suficiente
- Tolera 15% de error → expectativas alineadas con MAPE estándar; registrar
- No tolera ningún error → expectativas de MAPE necesitan conversación; registrar como señal de riesgo

---

## Bloque 2 — Formato y canal preferido

### Pregunta sobre formato
> "Si tuvieras el pronóstico en tus manos hoy, ¿en qué formato lo usarías? ¿Preferirías una pantalla donde consultarlo, un archivo Excel que puedas descargar, o un correo que te llegue cuando esté listo?"

**Por qué importa:** Confirma qué canal de FARO va a usar realmente este stakeholder. FARO ofrece tres: dashboard de solo lectura, correo automático y archivo exportable.

**Sondas de seguimiento:**
- "¿Trabajas habitualmente desde el computador o más desde el celular?"
- "¿Eres el único que necesita ese pronóstico, o hay varias personas que también lo usan?"
- "¿Necesitas hacer cálculos adicionales con esos datos, o solo los lees?"

**Señales a escuchar:**
- "Excel porque lo proceso" → necesita el exportable; registrar en canales preferidos
- "Me llega un correo y ya" → el correo automático es suficiente; registrar
- "Una pantalla sería lo mejor" → usará el dashboard; registrar
- Hace cálculos adicionales → el exportable es el canal crítico para este usuario; asegurarse de que el configurator lo active

---

## Bloque 3 — Nivel de detalle necesario

### Pregunta sobre granularidad
> "¿Necesitas ver el pronóstico por cada producto específico, por grupo de productos, o un total general es suficiente para lo que haces?"

**Por qué importa:** Define si el usuario necesita el nivel SKU, categoría o totales. Un usuario que necesita SKU va a usar el dashboard diferente a uno que solo quiere totales.

**Sondas de seguimiento:**
- "¿Y por cliente? ¿Te importa saber qué va a pedir cada cliente específico, o solo el total del mercado?"
- "¿Hay productos o clientes que monitoreas más de cerca que otros?"

**Señales a escuchar:**
- Necesita SKU × cliente → nivel más granular; FARO lo soporta; registrar
- Solo totales por categoría → puede usar la vista agregada del dashboard; registrar
- "Solo los 10 productos más importantes" → hay una jerarquía de atención; registrar en notas para el configurator

---

## Bloque 4 — Horizonte de pronóstico

### Pregunta sobre tiempo
> "¿Con cuánta anticipación necesitas saber lo que va a pasar? ¿Te basta con el mes siguiente, o necesitas ver 2–3 meses adelante?"

**Opciones posibles:**
- Días (ej: planificación de producción diaria)
- Semanas (ej: planificación de compras con lead time corto)
- Meses (ej: presupuesto mensual, planeación de capacidad)
- Múltiples meses (ej: negociaciones con proveedores, capacidad de planta)

**Sondas de seguimiento:**
- "¿Cuánto tarda tu proveedor en entregar desde que haces el pedido? ¿Ese tiempo influye en cuánto anticipas necesitas?"
- "¿Hay temporadas en tu negocio donde necesitas anticipar más tiempo?"

**Señales a escuchar:**
- Lead time de proveedor > 1 mes → el horizonte de pronóstico debe ser mayor que ese lead time
- "El año completo" → horizonte largo; registrar pero ajustar expectativas de precisión (a más horizonte, mayor incertidumbre)
- Horizonte distinto al que mencionó el rol negocio → contradicción; registrar para que el synthesizer la resuelva

---

## Bloque 5 — Contexto del proceso actual

### Pregunta sobre fricción actual
> "¿Qué es lo que más te frustra de cómo consigues esta información hoy?"

**Por qué importa:** Revela el dolor real del usuario, que puede ser diferente al dolor del rol negocio. El negocio puede hablar de pérdidas económicas; el usuario puede hablar de tiempo perdido, decisiones apresuradas o información poco confiable.

**Sondas de seguimiento:**
- "¿Ha habido alguna vez que tomaste una mala decisión porque la información llegó tarde o estaba mal?"
- "¿Qué pasaría si ese proceso mejorara? ¿Qué podrías hacer diferente?"

**Señales a escuchar:**
- "Me llevo trabajo a la casa para esto" → el proceso actual consume demasiado tiempo; FARO tiene valor claro
- "Siempre le pregunto a [nombre] y a veces no sabe" → dependencia de persona; FARO consolida la información
- "En realidad no usamos mucho ese número" → el pronóstico no es crítico para este usuario; puede haber sobre-expectativa en el proyecto

---

## Bloque 6 — Snowball

### Pregunta de cierre de sesión
> "¿Hay alguien más que use esa información de demanda en su día a día, aunque sea de manera informal?"

**Sondas de seguimiento:**
- "¿Hay alguien en producción, compras o ventas que también tome decisiones con base en esas estimaciones?"
- "¿Hay alguien que tenga que aprobar lo que tú decides con esos números?"

**Señales a escuchar:**
- Nombra al jefe directo → hay un aprobador; puede ser stakeholder de negocio no identificado
- Nombra a alguien de producción o compras → usuarios adicionales con perspectivas propias; agregar a la cola si su rol es diferente al de este stakeholder

---

## Campos que este rol ayuda a completar

| Campo en session_data.json | Bloque de conversación |
|---------------------------|----------------------|
| `horizonte_pronostico` | Bloque 4 |
| `canales_preferidos` (dashboard / correo / exportable) | Bloque 2 |
| `nivel_detalle_requerido` (SKU / categoría / total) | Bloque 3 |
| `criterios_exito` (perspectiva del usuario) | Bloque 5 — complementa lo que dijo el rol negocio |
| Stakeholders adicionales | Bloque 6 (snowball) |

---

## Verificación al cerrar la sesión

Antes de despedirse, confirmar:

- [ ] Se entiende qué decisión toma este usuario con el pronóstico
- [ ] Se sabe con cuánta anticipación necesita el pronóstico (horizonte)
- [ ] Se tiene la preferencia de formato/canal (dashboard, correo, exportable)
- [ ] Se tiene el nivel de detalle requerido (SKU, categoría, total)
- [ ] Se preguntó por stakeholders adicionales (snowball)
- [ ] Si el horizonte declarado difiere del que mencionó el rol negocio → registrar contradicción en notas

---

*Guía v1.0 — Rol Usuario — Harness 010 Discovery — FARO / Sabbia Solutions & Software*
