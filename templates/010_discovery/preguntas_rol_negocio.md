# Guía de Preguntas — Rol Negocio
## Harness 010 Discovery | FARO / Sabbia Solutions & Software

> **Para el discovery-interviewer:**
> Este archivo es una guía de conversación, no un formulario. El objetivo es entender el problema real, no llenar campos. Haz una pregunta a la vez. Si la respuesta es vaga, usa la sonda de seguimiento. Si el stakeholder se desvía a un tema interesante, síguelo — puede revelar más que la respuesta directa.
>
> El rol negocio cubre: el problema que tienen, por qué importa ahora, qué han intentado, cómo miden el éxito y qué plan de servicio les conviene.

---

## Bloque 1 — El problema

### Pregunta de apertura
> "Antes de hablar de pronósticos, cuéntame cómo funciona hoy la gestión de demanda en su empresa. ¿Cómo deciden cuánto producir o tener en stock?"

**Por qué abrir así:** Empieza desde su mundo, no desde el nuestro. La respuesta revela si hay proceso formal, si depende de una persona clave, o si simplemente "se pide lo que se cree que se va a necesitar".

**Sondas de seguimiento:**
- "¿Quién toma esas decisiones normalmente?"
- "¿Qué pasa cuando esa estimación falla? ¿Me puede dar un ejemplo reciente?"
- "¿Cuánto tiempo dedica esa persona a esto en una semana típica?"

**Señales a escuchar:**
- Menciona sobre-inventario o agotamiento de stock → profundiza cuál es más doloroso
- Nombra a una persona específica como "el que sabe" → es un riesgo operativo (dependencia)
- Dice que "más o menos funciona" → hay resistencia o no ven el problema tan grave

---

### Pregunta sobre el dolor
> "¿Cuál es la situación que más le duele hoy en términos de demanda? ¿El exceso de producto acumulado, quedarse sin stock, o algo distinto?"

**Sondas de seguimiento:**
- "¿Tiene un ejemplo concreto de los últimos 6 meses donde eso haya causado un problema real?"
- "¿Sabe cuánto le costó ese problema, aunque sea de forma aproximada?"
- "¿Cuántas veces al año diría que pasa algo así?"

**Señales a escuchar:**
- Cita números (aunque sean estimados) → el dolor es real y medible; registrarlos
- Se queda en abstracto → pedir el ejemplo concreto con insistencia amable
- Menciona un cliente o producto específico → anotar, puede ser caso de prueba para el piloto

---

### Pregunta sobre urgencia
> "¿Por qué están considerando esto ahora? ¿Hubo algo que detonó la búsqueda de una solución?"

**Sondas de seguimiento:**
- "¿Hay alguna fecha límite o evento en los próximos meses que haga esto más urgente?"
- "¿Hay alguien en la empresa que esté presionando para resolver esto pronto?"

**Señales a escuchar:**
- Menciona un evento concreto (auditoría, pérdida de cliente, decisión de directivo) → registrar en notas
- No tiene urgencia clara → onboarding puede ser tranquilo; no forzar el ritmo
- La urgencia viene de arriba (directivo) pero él no la siente → riesgo de adopción bajo

---

## Bloque 2 — Lo que han intentado antes

### Pregunta sobre soluciones previas
> "¿Han intentado antes resolver este problema de alguna forma? ¿Con herramientas, consultores, procesos internos?"

**Sondas de seguimiento:**
- "¿Qué funcionó de eso, aunque sea parcialmente?"
- "¿Qué no funcionó y por qué?"
- "¿Qué les dejó esa experiencia en términos de expectativas para lo que viene?"

**Señales a escuchar:**
- Tuvieron una mala experiencia previa → hay desconfianza; necesitan ver resultados rápido
- Ya usan Excel o algo manual → están acostumbrados a operar ellos mismos; recordarles que FARO opera por nosotros
- Dicen "nada ha funcionado" → o el problema es más complejo de lo que parece, o las expectativas son difusas

---

## Bloque 3 — Escala del negocio (insumos ITO)

> **Nota para el interviewer:** Estos datos son **críticos** — sin ellos el analyst no puede calcular el ITO y clasificar al cliente. Si el stakeholder de negocio no los sabe exactamente, pedir aproximaciones. Si definitivamente no los tiene, registrarlos como `MISSING` con la nota "confirmar con rol técnico".

### Pregunta sobre escala
> "Para entender la dimensión de su operación: ¿cuántos productos o referencias activas tienen hoy en venta, de manera aproximada?"

**Sondas de seguimiento:**
- "¿Y cuántos clientes distintos les compran en un mes típico?"
- "¿Y cuántos pedidos o líneas de pedido reciben al mes, aunque sea una estimación?"

**Señales a escuchar:**
- Responde con rangos amplios (ej: "entre 50 y 200") → anotar el rango, el analyst usa el punto medio
- Dice "no sé exactamente" → registrar `MISSING` con nota y asignar al técnico confirmarlo
- Los números son muy distintos de lo que se manejó en la venta → puede haber discrepancia de categoría; reportarla en notas

---

## Bloque 4 — Criterios de éxito

### Pregunta sobre el resultado esperado
> "Si FARO funciona como esperan, ¿cómo se va a ver ese éxito dentro de 6 meses? ¿Qué va a ser diferente?"

**Sondas de seguimiento:**
- "¿Cómo van a medir eso? ¿Tienen algún indicador que hoy midan y quieran mejorar?"
- "¿Cuál de estos dos les importa más: reducir el sobre-inventario o reducir los agotamientos? ¿O ambos igual?"
- "¿Hay alguien en la empresa que tenga que ver este resultado para considerar que el proyecto fue exitoso?"

**Señales a escuchar:**
- Define criterios medibles → buena señal; registrar las métricas que mencionan
- Habla solo de "sentir que mejora" → los criterios son cualitativos; puede ser difícil demostrar valor
- Menciona a un directivo que debe ver el resultado → hay un sponsor, identificar si es el mismo stakeholder o alguien más

---

## Bloque 5 — Plan de servicio

### Pregunta sobre compromiso
> "En cuanto al plan de servicio: ¿prefieren empezar mes a mes para ir conociendo el sistema, o ya tienen claridad para comprometerse por un trimestre o un año?"

**Opciones a presentar si pregunta:**
- Mensual: sin descuento, máxima flexibilidad
- Trimestral: 8% de descuento sobre el precio mensual
- Anual: 18% de descuento

**Sondas de seguimiento:**
- "¿Hay algún proceso de aprobación interno para compromisos a más de 3 meses?"
- "¿Quién firma los contratos de servicios en su empresa?"

**Señales a escuchar:**
- Quiere anual de entrada → puede haber presión de directivo o proceso de compra formal; confirmar quién aprueba
- Duda entre mensual y trimestral → no presionar; registrar la preferencia expresada y dejar que decida

---

### Pregunta sobre el responsable de pagos (dirigida — campo obligatorio)

> **Nota para el interviewer:** Esta pregunta es **obligatoria** y debe hacerse de forma explícita. El campo `responsable_pagos` (nombre y correo) alimenta el ciclo de cobro de FARO — es quien recibe los avisos de vencimiento, gracia y suspensión. No confundir con quién aprueba el presupuesto o firma el contrato: es **quién recibe los avisos de cobro/pago**. Si no se captura, el synthesizer lo marca `MISSING` y baja la calidad del discovery.

> "Cuando empiece la facturación después del mes gratuito, ¿quién debería recibir los avisos de cobro y pago? Necesito su nombre y un correo de contacto para las notificaciones de la suscripción."

**Sondas de seguimiento:**
- "¿Es la misma persona que aprueba el presupuesto, o alguien de administración/finanzas?"
- "¿A qué correo deben llegar los recordatorios de vencimiento?"

**Señales a escuchar:**
- Da nombre y correo → registrar en `responsable_pagos` (nombre + correo)
- Dice "yo mismo" → confirmar el correo aunque sea el del contacto principal
- No lo sabe aún → registrar `MISSING` con nota "definir responsable de pagos antes de la fase contractual"

---

## Bloque 6 — Snowball

### Pregunta de cierre de sesión
> "Antes de terminar, ¿hay otras personas en la empresa cuya perspectiva sea importante para este proyecto? ¿Alguien que trabaje con los datos, que use los pronósticos, o que haya que tener en cuenta aunque no esté en esta sesión?"

**Sondas de seguimiento:**
- "¿Cómo se llama? ¿Me puede conectar con esa persona?"
- "¿Qué rol tiene en la empresa y qué perspectiva traería que nosotros aún no tenemos?"

**Señales a escuchar:**
- Nombra al responsable de sistemas o TI → agregar como stakeholder técnico si no está en el brief
- Nombra a quien usa los reportes hoy → agregar como stakeholder usuario
- Dice "nadie más" rápidamente → puede estar protegiendo el proceso; no insistir, pero registrarlo

---

## Campos que este rol ayuda a completar

| Campo en session_data.json | Bloque de conversación |
|---------------------------|----------------------|
| `razon_social` | Bloque 3 (confirmar en apertura) |
| `sector` | Bloque 1 (emerge al hablar del negocio) |
| `skus_activos` | Bloque 3 |
| `clientes_xyz` | Bloque 3 |
| `pedidos_por_mes` | Bloque 3 |
| `criterios_exito` | Bloque 4 |
| `plan_suscripcion` | Bloque 5 |
| `responsable_pagos` (nombre + correo) | Bloque 5 (pregunta dirigida) |
| Stakeholders adicionales | Bloque 6 (snowball) |

---

## Verificación al cerrar la sesión

Antes de despedirse, confirmar mentalmente:

- [ ] Se entiende cuál es el problema principal (sobre-inventario, agotamientos, o ambos)
- [ ] Se capturaron aproximados de SKUs, clientes XYZ y pedidos por mes (o se marcaron como MISSING con responsable)
- [ ] Se tienen los criterios de éxito, aunque sean cualitativos
- [ ] Se tiene la preferencia de plan (Mensual / Trimestral / Anual)
- [ ] Se capturó el responsable de pagos (nombre + correo), o se marcó MISSING con nota
- [ ] Se preguntó por stakeholders adicionales (snowball)

---

*Guía v1.0 — Rol Negocio — Harness 010 Discovery — FARO / Sabbia Solutions & Software*
