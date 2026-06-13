# Brief de Contexto — Harness 010 Discovery
## FARO / Sabbia Solutions & Software

> **Instrucciones para el operador de Triple S:**
> - Completar este archivo **antes** de lanzar el harness 010 Discovery.
> - El `discovery-interviewer` lee este archivo al inicio de cada sesión.
> - Los campos marcados con `*` son **obligatorios** — sin ellos el interviewer no puede arrancar.
> - Ser breve y directo. Este no es un formulario de ventas — es un mapa de trabajo para el agente.
> - Guardar como `800_inputs/brief.md` en el proyecto cliente.

---

## 1. Identificación del cliente

| Campo | Valor |
|-------|-------|
| Razón social `*` | Conservas del Pacífico S.A.S. |
| Sector / industria `*` | Manufactura — conservas y alimentos procesados (pescado enlatado, vegetales, salsas, granos, dulces) |
| Ciudad / país `*` | Cali, Valle del Cauca, Colombia |
| Sitio web (referencia) | www.conservasdelpacifico.com.co |

---

## 2. Contexto comercial

**¿Cómo llegó este cliente a Triple S?**

Prospección directa. La Gerente de Cadena de Suministro de Conservas del Pacífico vio una presentación de FARO en un foro de la ANDI sobre planeación de demanda en el sector alimentos. Escribió a Triple S porque la empresa viene de dos temporadas con quiebres de stock en sus líneas de mayor rotación (atún y mayonesa) y, al mismo tiempo, exceso de inventario en líneas estacionales (mermeladas, bocadillo).

**¿Cuál es su nivel de urgencia percibido?**

- [x] Alta — tiene un problema activo
- [ ] Media — quiere mejorar algo que ya funciona
- [ ] Baja — está explorando opciones

**¿Qué espera lograr con FARO?** _(en sus propias palabras, si lo expresó)_

"Cada fin de mes adivinamos cuánto van a pedir las cadenas y los distribuidores. Se nos agota el atún en aceite justo cuando un supermercado grande hace un pedido fuerte, y nos quedamos con bodega llena de mermelada que sale lento. Queremos saber qué producir por referencia y por cliente, con varias semanas de anticipación, no reaccionar cuando ya es tarde."

---

## 3. Stakeholders iniciales `*`

> Listar al menos un stakeholder. El interviewer puede descubrir más durante las sesiones (mecanismo snowball).
> Un stakeholder puede tener más de un rol FARO — marcar todos los que apliquen.

### Stakeholder 1

| Campo | Valor |
|-------|-------|
| Nombre `*` | Adriana Restrepo Vélez |
| Cargo en la empresa `*` | Gerente de Cadena de Suministro |
| Correo `*` | arestrepo@conservasdelpacifico.com.co |
| Teléfono / WhatsApp | +57 318 540 2211 |

**Rol(es) FARO asignado(s) `*`:**
- [x] Negocio — conoce el problema, los objetivos y los criterios de éxito
- [ ] Técnico — conoce los datos, los sistemas y la calidad de la información
- [x] Usuario — usa los pronósticos para tomar decisiones

**Notas de contexto previo:**

Es la patrocinadora del proyecto y quien toma la decisión de compra. Lleva 4 años en la empresa. Conoce bien la estacionalidad: las conservas de pescado suben en Semana Santa y fin de año; las mermeladas y el bocadillo se mueven sobre todo en noviembre-diciembre; los granos (lenteja, garbanzo) tienen demanda más estable. Le interesa un pronóstico por **referencia (SKU) y por cliente** con al menos 6 semanas de horizonte, para coordinar producción y compra de hojalata e insumos importados (cuyo lead time es largo).

---

### Stakeholder 2

| Campo | Valor |
|-------|-------|
| Nombre | Mauricio Lozano Caicedo |
| Cargo en la empresa | Jefe de TI y Sistemas |
| Correo | mlozano@conservasdelpacifico.com.co |
| Teléfono / WhatsApp | +57 315 778 9043 |

**Rol(es) FARO asignado(s):**
- [ ] Negocio
- [x] Técnico
- [ ] Usuario

**Notas de contexto previo:**

Administra el sistema de gestión comercial (Siigo Nube) y consolida los reportes de pedidos. En la llamada inicial mencionó que el historial de pedidos confiable arranca a comienzos de **2024**, cuando estandarizaron el registro de pedidos en el sistema actual; calcula que tienen "como tres años" de datos, aunque al revisar reconoció que el arranque real fue enero de 2024. Advirtió dos cosas: (1) que el reporte se exporta a **CSV separado por punto y coma con acentos** (configuración regional de Colombia en Excel), y (2) que a veces aparecen **pedidos repetidos** cuando un asesor registra dos veces la misma orden, y **cantidades en negativo** que el área comercial usa para anotar devoluciones y ajustes. Prefiere entregar el histórico completo de una sola vez (Batch), no en cargas parciales.

---

### Stakeholder 3

| Campo | Valor |
|-------|-------|
| Nombre | Julián Mosquera Hurtado |
| Cargo en la empresa | Director Comercial |
| Correo | jmosquera@conservasdelpacifico.com.co |
| Teléfono / WhatsApp | +57 300 221 6655 |

**Rol(es) FARO asignado(s):**
- [ ] Negocio
- [ ] Técnico
- [x] Usuario

**Notas de contexto previo:**

Lleva 8 años en la empresa. Conoce a los 45 clientes B2B uno por uno — cadenas de supermercados regionales, distribuidores mayoristas y tiendas de barrio grandes en Bogotá, Medellín, Cali, Barranquilla, Bucaramanga y Pereira. Sabe cuáles piden de forma irregular, cuáles tienen acuerdos de volumen y cuáles cambian de marca según promociones. Es quien recibe el reclamo cuando hay agotado. Adriana lo señaló como la persona que mejor conoce los patrones de compra y las señales cualitativas (entrada de un competidor de bajo precio, licitaciones con cadenas, aperturas de punto de venta).

---

## 4. Contexto de datos conocido de antemano

| Campo | Lo que dijo el cliente |
|-------|----------------------|
| Sistema(s) que usa (ERP, Excel, otro) | Siigo Nube para pedidos y facturación. Excel para planeación de producción y seguimiento de inventario. Exportan los pedidos a CSV (separado por `;`, con acentos). |
| Años de historial de pedidos (aprox.) | "Como tres años." Al revisar, el registro estandarizado y confiable arranca en **enero de 2024**; antes de eso los datos están incompletos. (El rango real del archivo entregado es ~2,2 años.) |
| Escala aproximada (SKUs, clientes XYZ) | ~350 referencias activas (atún y sardinas, vegetales enlatados, salsas y aderezos, granos, mermeladas/dulces). ~45 clientes B2B (cadenas, distribuidores, tiendas grandes). |
| ¿Mencionó problemas de calidad de datos? | Sí: pedidos duplicados por doble registro de asesores, y cantidades negativas usadas para devoluciones/ajustes. Sin cuantificar. |

---

## 5. Restricciones y riesgos conocidos

- [ ] Historial posiblemente corto (menos de 2 años)
- [ ] Datos probablemente dispersos en múltiples sistemas
- [ ] Hay resistencia interna al proyecto (indicar quién si se sabe)
- [ ] Hay una fecha límite comprometida con el cliente
- [x] Otro: El cliente cree tener "~3 años" de historial, pero el registro confiable arranca en enero de 2024 (~2,2 años reales). Posibles duplicados por doble registro y cantidades negativas por devoluciones.

**Detalle adicional:**

El historial confiable cubre desde enero de 2024 — algo más de dos años, suficiente para un primer modelo pero por debajo de los "tres años" que el cliente percibe; conviene confirmar la fecha de inicio real con TI antes de fijar expectativas de precisión. El riesgo de calidad principal son los duplicados por doble registro y las cantidades negativas (devoluciones/ajustes) que Mauricio mencionó sin cuantificar — dependiendo del volumen, el ISD podría arrancar por debajo del 95% y habría que mostrar el diagnóstico al cliente. La estacionalidad es fuerte y ligada al calendario comercial (Semana Santa para pescado, fin de año para dulces y mermeladas), señal que puede no estar registrada en el sistema y habría que capturar en la entrevista.

---

## 6. Objetivos prioritarios de este discovery

1. **Confirmar la ventana real de historial** — el cliente percibe "~3 años" pero el registro confiable parece arrancar en enero de 2024 (~2,2 años). Fijar la fecha de inicio real con TI: afecta directamente las expectativas de precisión y la estrategia de modelo.
2. **Dimensionar el problema de calidad de datos** — ¿qué tan frecuentes son los duplicados por doble registro y las cantidades negativas por devoluciones? ¿Es puntual o sistémico? Esto define si aplica cargo por complejidad de datos y si el ISD inicial estará bajo el 95%.
3. **Capturar la estacionalidad comercial** — los picos de conservas de pescado (Semana Santa) y de dulces/mermeladas (fin de año) parecen no estar documentados como señal en el sistema. Confirmar si Julián conoce el calendario y si puede capturarse como señal anticipada para el pronóstico por SKU y por cliente.

---

*Brief template v1.0 — Harness 010 Discovery — FARO / Sabbia Solutions & Software*
