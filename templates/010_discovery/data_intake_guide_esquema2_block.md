## Archivo adicional — Producción e Inventario (opcional pero valioso)

Adicionalmente al historial de pedidos, nos indicó que puede compartir información de producción e inventario. Este segundo archivo nos permite detectar si los quiebres de stock son causados por falta de demanda o por falta de producto disponible — lo que hace el pronóstico considerablemente más preciso.

### Columnas de este archivo adicional

| Columna | ¿Qué contiene? | Ejemplo |
|---------|----------------|---------|
| **Fecha** | La fecha del registro de producción o inventario | 01/03/2023 |
| **Código del producto** | El mismo identificador que usa en el archivo de pedidos | PRD-042 |
| **Cantidad producida** | Unidades fabricadas en ese período | 2.000 |
| **Inventario disponible** | Stock en bodega al cierre del período | 350 |
| **Capacidad máxima** | Producción máxima posible en ese período | 3.000 |
| **Unidad de medida** | La misma que usa en el archivo de pedidos | Cajas |

> Este archivo es completamente opcional. Si no lo tiene, el sistema trabajará únicamente con el historial de pedidos.
