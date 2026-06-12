# Guía de Entrega de Datos — FARO
## {NOMBRE_CLIENTE} | Preparado por Sabbia Solutions & Software

---

Estimado/a **{CONTACTO_PRINCIPAL}**,

Gracias por confiar en FARO para mejorar la precisión de sus pronósticos de demanda. Para que el sistema pueda trabajar con sus datos, necesitamos que nos entregue su historial de pedidos siguiendo las instrucciones de esta guía.

Si tiene alguna duda durante el proceso, escríbanos a **contacto@sabbiasolutions.com** y le respondemos en menos de 24 horas.

---

## ¿Qué necesitamos?

Un archivo con el historial de pedidos que sus clientes le han hecho a lo largo del tiempo.

**Formato aceptado:** Excel (.xlsx o .xls) o archivo de texto separado por comas (.csv)

**Cantidad de historial a enviar:** Todo el que tenga disponible. Lo ideal es contar con al menos {ANIOS_HISTORIAL_RECOMENDADO} años de historia. Su nivel de confianza inicial será **{NIVEL_CONFIANZA}**.

---

## Columnas del archivo

### Columnas obligatorias
*Sin estas cuatro columnas no podemos procesar el archivo.*

| Columna | ¿Qué contiene? | Ejemplo |
|---------|----------------|---------|
| **Fecha del pedido** | La fecha en que su cliente realizó el pedido | 15/03/2023 |
| **Código del cliente** | Un identificador único para cada uno de sus clientes | XYZ-001 |
| **Código del producto** | Un identificador único para cada producto pedido | PRD-042 |
| **Cantidad solicitada** | Las unidades que su cliente pidió | 500 |

> El nombre exacto de las columnas no importa — puede llamarlas como quiera en su archivo. Lo que importa es que el contenido sea el correcto.

---

### Columnas recomendadas
*Estas columnas no son obligatorias, pero mejoran significativamente la precisión del pronóstico.*

| Columna | ¿Para qué sirve? |
|---------|-----------------|
| Cantidad entregada | Nos permite detectar si hay diferencia entre lo pedido y lo despachado |
| Fecha de entrega prometida | Ayuda a entender los tiempos de respuesta comprometidos |
| Fecha de entrega real | Permite medir el cumplimiento real de las entregas |
| Precio unitario de venta | Facilita el análisis por valor además de por volumen |
| Estado del pedido | Distingue entre pedidos completos, parciales y cancelados |
| Nombre del producto | Complementa el código con una descripción legible |
| Nombre del cliente | Complementa el código con el nombre de la empresa |
| Categoría del producto | Agrupa los productos por tipo o línea |
| Subcategoría del producto | Permite un nivel adicional de agrupación |
| Región o país del cliente | Útil si sus clientes están en diferentes ubicaciones |
| Ciudad del cliente | Nivel más detallado de ubicación geográfica |
| Sede o sucursal del cliente | Si el mismo cliente opera desde múltiples puntos |
| Unidad de medida | Cajas, kilos, litros, unidades — lo que aplique a su negocio |
| Número de pedido | Para referencia y trazabilidad |

---

{SECCION_ESQUEMA2}

---

## Consejos para preparar el archivo

- **Un pedido por fila:** cada fila del archivo debe representar un producto de un pedido. Si un pedido tiene 5 productos distintos, debe tener 5 filas.
- **Sin totales ni subtotales:** el archivo debe contener solo los datos de los pedidos, sin filas de resumen al final.
- **Fechas en formato consistente:** use siempre el mismo formato de fecha en todo el archivo (por ejemplo, DD/MM/AAAA).
- **Números sin formato:** las cantidades no deben tener puntos separadores de miles ni símbolos de moneda (escriba `1500` no `1.500` ni `$1,500`).
- **Si tiene varios archivos:** puede enviarnos todos, uno por año o como los tenga guardados — nosotros los unificamos.

---

## ¿Cómo enviarnos el archivo?

{INSTRUCCION_ENVIO}

---

## ¿Qué haremos con sus datos?

- Trabajaremos únicamente sobre una **copia** de lo que nos entregue — sus archivos originales nunca serán modificados.
- Sus datos están protegidos y no serán compartidos con terceros.
- Una vez procesados, le enviaremos un reporte con el diagnóstico de calidad de su información antes de emitir el primer pronóstico.

---

*Guía preparada por Sabbia Solutions & Software — FARO v1.0*  
*Fecha de emisión: {FECHA_EMISION}*
