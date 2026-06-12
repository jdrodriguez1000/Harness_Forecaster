# Plantilla de Sesión de Descubrimiento — FARO
## Harness 010 Discovery | Sabbia Solutions & Software

**Cliente:** ___________________________________  
**Fecha de sesión:** ___________________________  
**Operador Triple S:** __________________________  
**Duración estimada:** 60–90 minutos

---

> **Instrucciones para el operador:**
> - Completar cada campo durante la sesión con el cliente.
> - Los campos marcados con `*` son **obligatorios** — sin ellos el sistema no puede continuar.
> - Los campos marcados con `†` son **condicionales** — obligatorios solo si aplica.
> - Los campos sin marca son **opcionales** pero mejoran la calidad del pronóstico.
> - Si un campo obligatorio no se puede obtener en la sesión: escribir `MISSING — <razón>`.

---

## Bloque 1 — Identificación de la empresa

| Campo | Valor |
|-------|-------|
| Razón social `*` | |
| Sector / industria `*` | |

**Ejemplos de sector:** alimentos y bebidas, químicos, textil, farmacéutico, plásticos, metalmecánica, cosméticos.

---

## Bloque 2 — Contactos

### Contacto principal (planificador de demanda) `*`

| Campo | Valor |
|-------|-------|
| Nombre `*` | |
| Correo `*` | |
| Teléfono `*` | |

### Responsable de pagos

| Campo | Valor |
|-------|-------|
| Nombre `*` | |
| Correo `*` | |

---

## Bloque 3 — Insumos para el ITO
> Estos tres valores determinan la categoría de precio (M / L / XL). Pedir aproximados — no se requiere exactitud.

| Campo | Valor |
|-------|-------|
| SKUs activos aprox. `*` | |
| Clientes XYZ atendidos aprox. `*` | |
| Volumen de pedidos por mes aprox. `*` | |

**Nota al operador:** Si el cliente no maneja el concepto de "SKU", usar "referencias de producto activas". Si no maneja "pedidos", usar "órdenes de compra recibidas de sus clientes".

---

## Bloque 4 — Historial de datos

| Campo | Valor |
|-------|-------|
| Años de historial de pedidos disponible `*` | |

**Referencia rápida:**
- ≥ 3 años → nivel de confianza Alto
- 2–3 años → nivel Estándar
- 1–2 años → nivel Reducido (modelo de apoyo activo)
- 3 meses – 1 año → nivel Experimental (acumulación previa al primer pronóstico)
- < 3 meses → inviable — escalar antes de continuar

---

## Bloque 5 — Configuración operativa

| Campo | Opciones válidas | Valor |
|-------|-----------------|-------|
| Modo de ingesta preferido `*` | `Batch` / `Incremental` | |
| Frecuencia de actualización `†` | `Diaria` / `Semanal` | |
| Horizonte de pronóstico requerido `*` | `días` / `semanas` / `meses` / `múltiples meses` | |

> `†` Frecuencia de actualización: **obligatorio solo si el modo es Incremental**.

**Nota al operador:** "Modo Batch" significa que el cliente entrega un archivo histórico completo una sola vez. "Modo Incremental" significa que entrega actualizaciones periódicas (cada día o cada semana).

---

## Bloque 6 — Jerarquías disponibles

### Jerarquía de productos `*`
> Marcar los niveles que el cliente **tiene** en sus datos. Mínimo uno.

- [ ] Categoría
- [ ] Subcategoría
- [ ] SKU / referencia de producto
- [ ] Otro: ___________________________

### Jerarquía geográfica `*`
> Marcar los niveles que el cliente **tiene** en sus datos. Mínimo uno.

- [ ] Región
- [ ] País
- [ ] Ciudad
- [ ] Sede / sucursal / punto de venta
- [ ] No aplica (cliente con una sola ubicación)

---

## Bloque 7 — Datos adicionales

| Campo | Opciones válidas | Valor |
|-------|-----------------|-------|
| ¿Tiene datos de producción e inventario? (Esquema 2) `*` | `Sí` / `No` | |
| ¿Existen mínimos contractuales con sus clientes XYZ? | Texto libre o `No aplica` | |

**Esquema 2** = datos de cuánto se produce y cuánto hay en inventario. Si el cliente los tiene, FARO puede detectar quiebres de stock reales vs. pedidos no colocados.

---

## Bloque 8 — Contrato y criterios de éxito

| Campo | Opciones válidas | Valor |
|-------|-----------------|-------|
| Plan de suscripción elegido `*` | `Mensual` / `Trimestral` / `Anual` | |
| Criterios de éxito `*` | `reducir sobre-inventario` / `reducir quiebres` / `ambos` | |

---

## Notas libres del operador

> Registrar aquí observaciones, contexto adicional, dudas del cliente, compromisos asumidos durante la sesión o cualquier información relevante que no encaje en los bloques anteriores.

_______________________________________________
_______________________________________________
_______________________________________________
_______________________________________________
_______________________________________________

---

## Verificación previa al cierre de sesión

Antes de terminar la reunión, confirmar con el cliente:

- [ ] Todos los campos `*` tienen valor (o están marcados como MISSING con razón)
- [ ] Si modo Incremental: frecuencia definida
- [ ] Jerarquía de producto: al menos un nivel marcado
- [ ] Jerarquía geográfica: al menos un nivel marcado (o "no aplica")
- [ ] Plan de suscripción confirmado
- [ ] El cliente sabe que recibirá una guía de entrega de datos por correo

---

*Plantilla v1.0 — Harness 010 Discovery — FARO / Sabbia Solutions & Software*
