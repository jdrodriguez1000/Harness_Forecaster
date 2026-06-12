# Guía de Preguntas — Rol Técnico
## Harness 010 Discovery | FARO / Sabbia Solutions & Software

> **Para el discovery-interviewer:**
> El rol técnico es quien conoce los datos reales, los sistemas que los generan y los problemas de calidad que existen. No asumas que tiene los mismos datos que el rol negocio dijo tener — frecuentemente difieren. Escucha señales de problemas de calidad que el stakeholder de negocio no mencionó o no sabe que existen.
>
> El rol técnico cubre: qué sistemas usan, qué datos existen, cuántos años de historial hay realmente, con qué calidad, y qué esquemas de datos pueden entregar.

---

## Bloque 1 — Sistemas y fuentes de datos

### Pregunta de apertura
> "¿Qué sistema o sistemas usa la empresa para registrar los pedidos de sus clientes? ¿Trabajan con un ERP, con Excel, con algún software específico?"

**Por qué abrir así:** Define el punto de partida técnico. Un ERP establecido suele significar datos más estructurados. Excel o software propio significa variabilidad alta en calidad y formato.

**Sondas de seguimiento:**
- "¿Desde cuándo usan ese sistema?"
- "¿Hubo algún cambio de sistema en los últimos 3–4 años? ¿Migraron de algo anterior?"
- "¿Toda la operación registra pedidos en ese mismo sistema, o hay áreas o sedes que llevan sus propios registros?"

**Señales a escuchar:**
- Cambio de ERP reciente → puede haber un corte en el historial; el historial real puede ser menor al que mencionó el negocio
- Múltiples sistemas coexistiendo → los datos están fragmentados; implica trabajo de consolidación antes del Intake
- "Todo en Excel" → estructura libre; el mapeo de campos va a requerir más trabajo en la guía de datos

---

### Pregunta sobre acceso a los datos
> "¿Usted puede exportar el historial de pedidos desde ese sistema? ¿O necesita involucrar a alguien más para hacerlo?"

**Sondas de seguimiento:**
- "¿En qué formato se exporta normalmente? ¿Excel, CSV, algo más?"
- "¿Hay restricciones de seguridad o TI para compartir esos datos con un tercero?"
- "¿Cuánto tiempo tardaría en preparar un archivo de historial si se lo solicitamos mañana?"

**Señales a escuchar:**
- Necesita autorización de TI → hay una persona más que involucrar; identificar quién
- Dice "nunca hemos exportado eso" → el proceso de entrega será nuevo para ellos; la guía de datos va a ser muy importante
- Tiene listo un archivo de muestra → buena señal; si puede compartirlo en la sesión o después, hacerlo

---

## Bloque 2 — Historial disponible

### Pregunta sobre antigüedad del historial
> "¿Desde cuándo tienen registros de pedidos en ese sistema? ¿Pueden llegar a 3 años de historial, más, o menos?"

**Por qué es crítico:** El nivel de confianza del cold start depende directamente de esto. Con menos de 3 meses no se puede operar. Con menos de 2 años el modelo trabaja con más incertidumbre. Con 3 o más años el pronóstico tiene máxima confianza.

**Sondas de seguimiento:**
- "¿Esos registros están completos, o hay períodos en los que hay datos faltantes o poco confiables?"
- "Si hubo algún cambio de sistema, ¿el historial anterior fue migrado o está en el sistema viejo?"
- "¿El volumen de clientes y productos en ese historial es similar al de hoy, o el negocio ha cambiado mucho?"

**Señales a escuchar:**
- Historial < 1 año → nivel Experimental; activar cascada cold start; registrar con claridad
- Historial ≥ 3 años pero con quiebre de sistema → puede ser 2 años reales; confirmar el período continuo más largo
- "Ha cambiado mucho el negocio" → los patrones históricos tienen menor relevancia; registrar en notas

---

## Bloque 3 — Calidad de los datos

### Pregunta sobre calidad conocida
> "¿Tiene una idea de cómo está la calidad de esos datos? Por ejemplo, ¿hay pedidos mal registrados, duplicados, campos vacíos frecuentes?"

**Por qué es clave:** Prepara al equipo para el diagnóstico ISD. Si el técnico ya sabe que hay problemas, es probable que el ISD inicial sea bajo. Las expectativas de MAPE deben ajustarse.

**Sondas de seguimiento:**
- "¿Hay productos o clientes específicos donde la calidad sea notoriamente peor?"
- "¿Saben cuál es la causa de esos problemas? ¿Es el proceso de captura, el sistema, o algo más?"
- "¿Alguien en la empresa está trabajando actualmente en mejorar eso?"

**Señales a escuchar:**
- Conoce el problema con detalle → hay conciencia técnica; buen punto de partida
- "Los datos están bien" sin más detalle → probable que no han analizado la calidad formalmente; el ISD va a revelar cosas
- Menciona problemas de duplicados o registros manuales → banderas rojas para el harness 020 Diagnosis

---

### Pregunta sobre campos disponibles
> "Cuando exportan un pedido, ¿qué información viene en ese registro? Por ejemplo: fecha, cliente, producto, cantidad, ¿algo más?"

**Por qué importa:** El Esquema 1 mínimo necesita 4 campos: fecha del pedido, identificador del cliente, identificador del producto, cantidad pedida. El ideal tiene 17 campos. Más campos = mejor pronóstico.

**Campos ideales a preguntar si no los menciona:**
- Fecha de entrega prometida o real
- Precio unitario o valor total del pedido
- Unidad de medida
- Canal de venta (si hay más de uno)
- Región o sede del cliente
- Categoría o subcategoría del producto

**Sondas de seguimiento:**
- "¿Tienen registrado cuándo se entregó realmente el pedido, o solo cuándo se hizo?"
- "¿Los clientes tienen identificadores únicos en el sistema, o se registran solo por nombre?"
- "¿Los productos tienen un código único (SKU o referencia), o también solo por nombre?"

**Señales a escuchar:**
- Solo fecha + producto + cantidad → mínimo viable; funciona pero el pronóstico tendrá menos riqueza
- Identificadores por nombre libre → hay que hacer normalización; el Refinery va a trabajar más
- Tiene precio y fechas de entrega → buena señal para análisis de ciclos de entrega y valor de cliente

---

## Bloque 4 — Jerarquías disponibles en los datos

### Pregunta sobre jerarquía de productos
> "¿Sus productos están organizados en alguna jerarquía en el sistema? Por ejemplo: categoría → subcategoría → SKU, o algo similar?"

**Por qué importa:** FARO puede generar pronósticos a múltiples niveles simultáneamente (SKU + categoría). Si el cliente no tiene categorías en sus datos, el pronóstico es solo a nivel SKU.

**Sondas de seguimiento:**
- "¿Esa organización está en el sistema, o es algo que manejan en la cabeza o en Excel aparte?"
- "¿Las categorías han cambiado en el historial? ¿Había productos en categorías distintas antes?"

**Señales a escuchar:**
- Solo SKUs, sin categorías → pronóstico posible pero solo a nivel SKU; registrar en jerarquías disponibles
- Categorías existen en el sistema → confirmar si están en el campo exportable

---

### Pregunta sobre jerarquía geográfica
> "¿Los pedidos de sus clientes tienen alguna ubicación geográfica registrada? Por ejemplo, ¿por ciudad, región, o punto de venta?"

**Sondas de seguimiento:**
- "¿El cliente tiene una o varias sedes que compran por separado?"
- "¿Los pedidos de diferentes sedes del mismo cliente se registran como el mismo cliente o como clientes distintos?"

**Señales a escuchar:**
- Todos los pedidos son de una sola ubicación → jerarquía geográfica no aplica; marcar "no aplica"
- Clientes con múltiples sedes registradas como uno → los pronósticos no pueden ser por sede; registrar la limitación

---

## Bloque 5 — Esquema 2: producción e inventario

### Pregunta sobre datos adicionales
> "Además del historial de pedidos, ¿tienen registros de cuánto producen por período y cuánto inventario tienen disponible?"

**Por qué importa:** El Esquema 2 permite a FARO detectar quiebres de stock reales (no hubo pedido porque no había producto) versus demanda genuinamente baja. Sin estos datos, esa distinción no es posible.

**Sondas de seguimiento:**
- "¿Esos datos están en el mismo sistema o en otro?"
- "¿Están al mismo nivel de detalle que los pedidos (por SKU, por período), o son más agregados?"
- "¿Esos datos tienen la misma antigüedad que el historial de pedidos?"

**Señales a escuchar:**
- Sí tienen datos de producción e inventario → activar Esquema 2 en la configuración
- Los datos existen pero son muy agregados o manuales → Esquema 2 posible pero con limitaciones; registrar
- No tienen esos datos → Esquema 2 no aplica; marcar en configuración

---

## Bloque 6 — Modo de entrega de datos

### Pregunta sobre actualización
> "Una vez que empecemos a trabajar, ¿cómo prefieren entregarnos las actualizaciones de datos? ¿Cada día, cada semana, o prefieren entregar un archivo completo una sola vez al inicio?"

**Opciones a presentar:**
- **Modo Batch:** un archivo histórico completo al inicio, sin actualizaciones posteriores. El modelo trabaja con eso.
- **Modo Incremental:** actualizaciones periódicas (diarias o semanales) que van alimentando el sistema. El modelo mejora con el tiempo.

**Sondas de seguimiento:**
- "¿Tienen alguien que pueda automatizar esa entrega o siempre sería manual?"
- "¿Hay restricciones de sistema que hagan difícil generar exportaciones frecuentes?"

**Señales a escuchar:**
- "Lo haríamos manual cada vez" → modo Incremental puede ser pesado para ellos; Batch puede ser más realista
- "Podemos automatizar la exportación" → modo Incremental es viable; confirmar frecuencia

---

## Bloque 7 — Snowball

### Pregunta de cierre de sesión
> "¿Hay alguien más en el equipo técnico o de sistemas que debería estar informado de este proyecto, o que pueda tener información que no cubrimos hoy?"

**Sondas de seguimiento:**
- "¿Hay alguien de TI o sistemas que deba aprobar el compartir datos con nosotros?"
- "¿La persona que realmente saca los reportes del ERP es usted, u otra persona?"

---

## Campos que este rol ayuda a completar

| Campo en session_data.json | Bloque de conversación |
|---------------------------|----------------------|
| `años_historial` | Bloque 2 |
| `modo_ingesta` | Bloque 6 |
| `frecuencia_actualizacion` | Bloque 6 (si modo Incremental) |
| `jerarquia_producto` | Bloque 4 |
| `jerarquia_geografica` | Bloque 4 |
| `esquema_2_disponible` | Bloque 5 |
| `skus_activos` (confirmar) | Bloque 1 — confirmar contra lo que dijo el rol negocio |
| `clientes_xyz` (confirmar) | Bloque 1 — confirmar contra lo que dijo el rol negocio |
| `pedidos_por_mes` (confirmar) | Bloque 1 — confirmar contra lo que dijo el rol negocio |
| `minimos_contractuales` | Bloque 3 (emerge si mencionan compromisos de compra) |

---

## Verificación al cerrar la sesión

Antes de despedirse, confirmar:

- [ ] Se sabe en qué sistema viven los datos y si son exportables
- [ ] Se tiene la antigüedad real del historial continuo
- [ ] Se tiene claridad sobre los campos disponibles (al menos los 4 mínimos del Esquema 1)
- [ ] Se tiene la preferencia de modo de entrega (Batch / Incremental) y frecuencia si aplica
- [ ] Las jerarquías de producto y geográfica están identificadas
- [ ] Se sabe si el Esquema 2 (producción/inventario) está disponible
- [ ] Se preguntó por stakeholders adicionales (snowball)

---

*Guía v1.0 — Rol Técnico — Harness 010 Discovery — FARO / Sabbia Solutions & Software*
