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
| Razón social `*` | Limpro Industrial S.A. de C.V. |
| Sector / industria `*` | Manufactura — productos de limpieza y sanitización industrial |
| Ciudad / país `*` | León, Guanajuato, México |
| Sitio web (referencia) | www.limpro.com.mx |

---

## 2. Contexto comercial

**¿Cómo llegó este cliente a Triple S?**

Referido por un cliente existente. El Director de Operaciones de Limpro asistió a una reunión sectorial en León donde otro fabricante mencionó a FARO. Contactó a Triple S a la semana siguiente porque reconoció el problema de desabasto en sus líneas de mayor rotación.

**¿Cuál es su nivel de urgencia percibido?**

- [x] Alta — tiene un problema activo
- [ ] Media — quiere mejorar algo que ya funciona
- [ ] Baja — está explorando opciones

**¿Qué espera lograr con FARO?** _(en sus propias palabras, si lo expresó)_

"Tenemos desengrasante industrial y desinfectante de manos que siempre se nos agotan antes de que llegue el pedido de la planta que lo necesita con urgencia. Y al mismo tiempo tenemos bodega llena de limpiador de pisos que nadie nos pide. Queremos saber qué producir y cuándo, no adivinar."

---

## 3. Stakeholders iniciales `*`

> Listar al menos un stakeholder. El interviewer puede descubrir más durante las sesiones (mecanismo snowball).
> Un stakeholder puede tener más de un rol FARO — marcar todos los que apliquen.

### Stakeholder 1

| Campo | Valor |
|-------|-------|
| Nombre `*` | Ing. Carlos Hernández Reyes |
| Cargo en la empresa `*` | Director de Operaciones |
| Correo `*` | chernandez@limpro.com.mx |
| Teléfono / WhatsApp | +52 477 123 4567 |

**Rol(es) FARO asignado(s) `*`:**
- [x] Negocio — conoce el problema, los objetivos y los criterios de éxito
- [ ] Técnico — conoce los datos, los sistemas y la calidad de la información
- [x] Usuario — usa los pronósticos para tomar decisiones

**Notas de contexto previo:**

Es el sponsor del proyecto y quien toma la decisión final. Lleva 6 años en Limpro. Conoce bien la estacionalidad del negocio: los clientes del sector alimentos (plantas empacadoras, rastros) elevan pedidos antes de auditorías NOM/HACCP en junio-julio; el sector hotelero sube en noviembre-diciembre. Le interesa sobre todo tener un pronóstico por SKU con al menos 6 semanas de horizonte para planear producción y compra de materias primas.

---

### Stakeholder 2

| Campo | Valor |
|-------|-------|
| Nombre | Lic. Patricia Méndez Torres |
| Cargo en la empresa | Coordinadora de Sistemas y TI |
| Correo | pmendez@limpro.com.mx |
| Teléfono / WhatsApp | +52 477 123 4568 |

**Rol(es) FARO asignado(s):**
- [ ] Negocio
- [x] Técnico
- [ ] Usuario

**Notas de contexto previo:**

Administra el ERP (Microsip Enterprise) y los reportes de ventas en Excel. En la llamada de presentación mencionó que el historial de pedidos está en Microsip desde 2020, y que antes llevaban todo en hojas de cálculo que "ya nadie sabe dónde están". Advirtió que en 2022 migraron de módulo dentro de Microsip y algunos registros del año anterior pueden estar duplicados. Disponible para extraer reportes pero prefiere hacerlo en bloque, no en solicitudes parciales frecuentes.

---

### Stakeholder 3

| Campo | Valor |
|-------|-------|
| Nombre | Lic. Jorge Avilés Sánchez |
| Cargo en la empresa | Gerente de Ventas |
| Correo | javiles@limpro.com.mx |
| Teléfono / WhatsApp | +52 477 123 4569 |

**Rol(es) FARO asignado(s):**
- [ ] Negocio
- [ ] Técnico
- [x] Usuario

**Notas de contexto previo:**

Lleva 10 años en la empresa. Conoce a los clientes B2B uno por uno — sabe cuáles piden de forma irregular, cuáles tienen contratos con volumen mínimo y cuáles cambian de producto según el precio. Es quien recibe las quejas cuando hay desabasto. No estuvo en la demo pero Carlos lo señaló como la persona que mejor conoce los patrones de compra de los clientes. Puede ser fuente de señales cualitativas importantes (cambios de cliente, licitaciones ganadas/perdidas, nuevos competidores de bajo precio).

---

## 4. Contexto de datos conocido de antemano

| Campo | Lo que dijo el cliente |
|-------|----------------------|
| Sistema(s) que usa (ERP, Excel, otro) | Microsip Enterprise para pedidos y facturación. Excel para planificación de producción y seguimiento de inventario. |
| Años de historial de pedidos (aprox.) | ~5 años en Microsip (desde 2020). Antes de eso, Excel con calidad incierta. Posibles duplicados en datos de 2022 por migración de módulo. |
| Escala aproximada (SKUs, clientes XYZ) | ~95 SKUs activos (desengrasantes, desinfectantes, jabones industriales, limpiadores de piso, sanitizantes). ~70 clientes B2B (plantas industriales, empacadoras, hoteles, rastros, distribuidores de limpieza). |
| ¿Mencionó problemas de calidad de datos? | Sí: posibles duplicados en 2022 por migración de módulo. Patricia no tiene certeza sobre la completitud del historial pre-2020. |

---

## 5. Restricciones y riesgos conocidos

- [ ] Historial posiblemente corto (menos de 2 años)
- [x] Datos probablemente dispersos en múltiples sistemas
- [ ] Hay resistencia interna al proyecto (indicar quién si se sabe)
- [ ] Hay una fecha límite comprometida con el cliente
- [x] Otro: Posibles registros duplicados en el año 2022 por migración de módulo en Microsip

**Detalle adicional:**

El historial en Microsip cubre desde 2020 (~5 años) — suficiente para el modelo. El riesgo principal es la duplicación de pedidos en 2022 que Patricia mencionó sin cuantificar. Dependiendo del volumen de duplicados, el ISD podría estar por debajo del 95% al inicio. El sector de limpieza industrial tiene estacionalidad fuerte ligada a calendarios de auditorías (HACCP, BRC, NOM) de los clientes del sector alimentos — esto puede no estar documentado como señal en el ERP y habría que capturarlo en la entrevista.

---

## 6. Objetivos prioritarios de este discovery

1. **Cuantificar el problema de duplicados 2022** — ¿cuántos registros están afectados? ¿Es puntual (un mes, un cliente) o sistémico? Esto define si necesitamos cargo por complejidad de datos.
2. **Entender la estacionalidad ligada a auditorías** — los picos de demanda de desengrasante y desinfectante parecen estar atados a calendarios de certificación de los clientes del sector alimentos. Necesitamos confirmar si Jorge conoce esos calendarios y si hay forma de capturarlos como señal anticipada.
3. **Validar el catálogo de SKUs activos** — con ~95 SKUs, necesitamos entender si todos tienen historial continuo o si hay SKUs nuevos (menos de 12 meses) que entrarían en modo cold start. Impacto directo en la estrategia de modelo.

---

*Brief template v1.0 — Harness 010 Discovery — FARO / Sabbia Solutions & Software*
