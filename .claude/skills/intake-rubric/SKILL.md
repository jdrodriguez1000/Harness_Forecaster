---
name: intake-rubric
description: Rúbrica de integridad y fidelidad de 7 dimensiones con anclas few-shot para la
  Instancia C del harness 015 Intake de FARO. Define los criterios de scoring por dimensión
  (0.0, 0.5, 1.0), las reglas de veto automático (D2, D5, D7), el gate de aprobación (≥ 0.80)
  y cuatro ejemplos globales calibrados (scores 0.2, 0.5, 0.8, 1.0). A diferencia del 010, las
  dimensiones son binarias y verificables (hash, bit-exactitud, conteos), no de razonamiento.
  Usar cuando intake-evaluator audita los artefactos del harness 015.
user-invocable: false
---

## Propósito de esta skill

Proporciona al evaluador (Instancia C) los criterios para auditar una entrega del 015 de
forma **objetiva y reproducible**. El 015 es determinístico: la auditoría es de **integridad
y fidelidad** (Bronce bit-a-bit, hashes, conteos, rechazo correcto), no de juicio.

**Regla de uso:** cargar esta skill ANTES de leer cualquier artefacto. C debe además
**recalcular el SHA-256** del Bronce y compararlo con el manifest, y verificar la
bit-exactitud contra el snapshot de entrada.

---

## Resumen de dimensiones

| ID | Dimensión | Artefacto principal | ¿Veto? |
|----|-----------|--------------------|--------|
| D1 | Detección de formato | `intake_report.json` (`format`) | No |
| D2 | Validación de estructura (GATE) | comportamiento P2 / `intake_rejection.json` | **Sí** |
| D3 | Validación de tipos y conteos | `intake_report.json` (`errores_tipo`, ideales) | No |
| D4 | Detección de duplicados | `intake_report.json` (`duplicados`) + Bronce | No |
| D5 | Fidelidad e inmutabilidad de Bronce | Bronce + `_manifest.json` | **Sí** |
| D6 | Completitud de reportes | `intake_report.json` + `_manifest.json` + `intake_log` | No |
| D7 | Evento emitido | `intake_complete.json` | **Sí** |

**Gate de aprobación:** promedio de D1–D7 ≥ 0.80 **y** ningún veto activo.

---

## Reglas de veto automático

Un veto convierte el veredicto en `REJECTED` sin importar el promedio:

- **Veto D2** — el gate de estructura no funciona: datos inválidos (falta un mínimo) entraron a
  Bronce, **o** datos válidos fueron rechazados. Sin un gate fiable, todo lo demás es ruido.
- **Veto D5** — Bronce no es copia bit-exacta de la entrada, **o** no tiene SHA-256, **o** el
  hash recalculado no coincide con el manifest → todo el medallón aguas abajo es inválido.
- **Veto D7** — `intake_complete` no existe (o está incompleto/emitido antes de Bronce) → 020 y
  025 nunca arrancan, o arrancan sobre datos parciales.

Registrar el veto en `veto_triggered: true` + `veto_dimension` dentro de `verdict.json`.

---

## D1 — Detección de formato

**Artefacto:** `intake_report.json` campo `format`.

**Qué verificar:** que tipo, delimitador (CSV), encoding y (Excel) hoja/fila de cabecera se
detectaron correctamente y se registraron. El criterio crítico: **los acentos no se
corrompieron** (un cp1252 leído como utf-8 corrompe `id_cliente`/`id_producto` y rompe el dedupe).

| Score | Criterio |
|-------|----------|
| **1.0** | Tipo, delimitador y encoding correctos y registrados; acentos intactos en Bronce. Si Excel, hoja y fila de cabecera correctas. |
| **0.5** | Formato detectado pero un campo de `format` quedó vacío/impreciso (p. ej. `encoding` no registrado aunque la lectura fue correcta), sin corromper datos. |
| **0.0** | Encoding/delimitador equivocado: acentos corruptos en Bronce, o delimitador mal detectado que parte mal las columnas. |

---

## D2 — Validación de estructura (GATE) ⚠️ VETO

**Artefacto:** comportamiento de P2; `intake_rejection.json` si rechazó; Bronce si aprobó.

**Qué verificar:** el gate rechaza **si y solo si** falta ≥ 1 campo mínimo del esquema
correspondiente. Sin falsos positivos ni falsos negativos.

Campos mínimos — **Esquema 1:** `fecha_pedido`, `id_cliente`, `id_producto`, `cantidad_solicitada`.
**Esquema 2** (si activo y recibido): `fecha`, `id_producto`, `cantidad_producida`,
`stock_disponible`, `costo_unitario`, `stock_minimo`.

| Score | Criterio |
|-------|----------|
| **1.0** | Gate correcto: aceptó un archivo con todos los mínimos / rechazó (con `intake_rejection.json` y lista de faltantes, **sin** crear Bronce) uno al que le faltaba un mínimo. |
| **0.5** | El gate funcionó pero `intake_rejection.json` no listó todos los faltantes, o registró un ideal como si fuera mínimo (no bloqueó indebidamente). |
| **0.0** | Falso negativo (faltaba un mínimo y aun así se creó Bronce) o falso positivo (estaban todos y se rechazó). → **VETO AUTOMÁTICO.** |

---

## D3 — Validación de tipos y conteos

**Artefacto:** `intake_report.json` campos `schema1.errores_tipo`, `campos_ideales_faltantes`.

**Qué verificar:** errores de tipo contados con exactitud **sin detener** el flujo; campos
ideales faltantes registrados. C puede recontar sobre el Bronce para confirmar.

| Score | Criterio |
|-------|----------|
| **1.0** | Conteos de error por campo exactos (verificables recontando el Bronce); ninguna fila eliminada por tipo; ideales faltantes registrados. |
| **0.5** | Conteos aproximados (difieren en pocas unidades) o ideales faltantes no registrados, pero el flujo no se detuvo y no se eliminaron filas. |
| **0.0** | Filas eliminadas/alteradas por errores de tipo (no es trabajo del 015), o conteos groseramente equivocados, o el flujo se detuvo por un error de tipo. |

---

## D4 — Detección de duplicados

**Artefacto:** `intake_report.json` campo `duplicados` + Bronce (y manifest si incremental).

**Qué verificar:** clave compuesta `(fecha_pedido, id_cliente, id_producto)` aplicada;
comportamiento correcto por modo:
- **Batch:** duplicados internos **contados y NO eliminados** (las filas siguen en Bronce; el
  020 los contabiliza en Unicidad).
- **Incremental:** registros ya presentes en el Bronce acumulado (vía manifest) **excluidos**;
  solo los nuevos persistidos en el archivo de esta entrega.

| Score | Criterio |
|-------|----------|
| **1.0** | Clave compuesta correcta; batch cuenta y conserva; incremental excluye lo ya existente y persiste solo lo nuevo; conteos verificables. |
| **0.5** | Comportamiento correcto por modo pero el conteo `internos`/`vs_bronce_previo` impreciso o mal etiquetado. |
| **0.0** | Batch **eliminó** duplicados (alteró Bronce), o incremental re-persistió registros ya existentes, o clave compuesta mal aplicada. |

---

## D5 — Fidelidad e inmutabilidad de Bronce ⚠️ VETO

**Artefacto:** archivo(s) Bronce + `_manifest.json`. **C recalcula el hash y compara bytes
con el snapshot de entrada.**

**Qué verificar:**
- Bronce **bit-exacto** a la entrada (mismos bytes; no re-serializado desde un DataFrame).
- SHA-256 calculado, correcto y persistido en el manifest.
- Un archivo inmutable por entrega + manifest (incremental); **nada reescrito** (write-once).
- Un segundo intento con el mismo contenido **no reescribe** el archivo.

| Score | Criterio |
|-------|----------|
| **1.0** | Bronce byte-idéntico a la entrada; hash recalculado coincide con el manifest; un archivo por entrega; write-once respetado. |
| **0.5** | Bronce fiel y con hash, pero incremental implementado como **reescritura** de un único archivo acumulado en vez de archivo-por-entrega + manifest (rompe la auditoría temporal), o el hash no se persistió. |
| **0.0** | Bronce no coincide byte-a-byte con la entrada (parseo lo alteró), o no tiene SHA-256, o el hash recalculado no coincide. → **VETO AUTOMÁTICO.** |

---

## D6 — Completitud de reportes

**Artefactos:** `intake_report.json`, `_manifest.json`, `intake_log`.

**Qué verificar:** los tres completos y consistentes: conteos, rango, errores, duplicados,
warnings, `files` JSONB con hash por archivo. Los `sha256` deben coincidir entre manifest y log.

| Score | Criterio |
|-------|----------|
| **1.0** | Los tres artefactos completos y consistentes; `files` con hash por archivo; **el warning de rango (P5) registrado cuando aplica**. |
| **0.5** | Artefactos presentes pero con un gap menor: falta el warning de rango que sí ocurría, o `intake_log` sin alguna entrada de `files`, o inconsistencia menor manifest↔log. |
| **0.0** | Falta uno de los tres artefactos, o `intake_report` sin conteos, o hashes ausentes en `files`. |

---

## D7 — Evento emitido ⚠️ VETO

**Artefacto:** `600_persistence/events/intake_complete.json`.

**Qué verificar:** existe como **último paso** (después de Bronce + reportes verificados), con
payload completo.

### Campos obligatorios del evento

| Campo | Valor esperado |
|-------|---------------|
| `event` | `"intake_complete"` (literal) |
| `tenant_id` | no vacío, coincide con Bronce/manifest/reporte |
| `delivery_id` | `YYYYMMDD` de la entrega |
| `mode` | `batch` o `incremental` |
| `timestamp` | ISO 8601 |
| `bronze_path` / `manifest_path` / `intake_report_path` | paths existentes |
| `next_harnesses` | `["020_diagnosis", "025_refinery"]` |

| Score | Criterio |
|-------|----------|
| **1.0** | Evento existe con todos los campos, paths válidos, `next_harnesses` correcto, emitido tras Bronce verificado. |
| **0.5** | Evento existe pero falta un path o `next_harnesses` incompleto; o el `intake_log.event_emitted` no se actualizó a `true`. |
| **0.0** | Evento no existe, o se emitió **antes** de que el reporte/Bronce existieran, o `tenant_id` nulo. → **VETO AUTOMÁTICO.** |

---

## Fórmula de scoring global

```
score_global = (D1 + D2 + D3 + D4 + D5 + D6 + D7) / 7
```

### Determinación del veredicto

```
Si (D2 == 0.0) OR (D5 == 0.0) OR (D7 == 0.0):
    veredicto = REJECTED   ← veto — no importa el promedio
Si score_global >= 0.80:
    veredicto = APPROVED
Si score_global < 0.80:
    veredicto = REJECTED
```

> **Caso especial — rechazo de estructura (P2 rechazó):** si la entrada no pasó P2, NO hay
> Bronce ni evento que auditar; el flujo terminó con `intake_rejection.json`. Esto es **flujo
> normal de entrada**, no una ejecución de calidad fallida. C no aplica la rúbrica completa: lo
> documenta como rechazo de entrada (la decisión la cerró A en 12.2). Solo se audita con la
> rúbrica completa cuando se creó Bronce.

---

## Anclas globales few-shot (ejemplos completos)

### Score global ≈ 0.20 — Lectura corrupta y gate roto

**Perfil:** un CSV `cp1252` se leyó como utf-8 (`Categoría` → `Categorâ€¦`); el validador
aceptó el archivo aunque faltaba `cantidad_solicitada`; se escribió un "Bronce" ya alterado.

- D1 = 0.0 — encoding equivocado, acentos corruptos.
- D2 = 0.0 — faltaba un mínimo y aun así se creó Bronce. **VETO.**
- D3 = 0.0 — conteos sobre datos ya corruptos.
- D4 = 0.0 — dedupe sobre `id_cliente` corrupto.
- D5 = 0.0 — Bronce no byte-exacto, sin hash. **VETO.**
- D6 = 0.2 — reporte parcial.
- D7 = 0.0 — sin evento. **VETO.**

> Score: ≈ 0.03 → REJECTED (3 vetos).

---

### Score global ≈ 0.50 — Validación impecable, Bronce reescrito

**Perfil:** formato/estructura/tipos correctos, pero el `bronze_writer` en incremental
**concatenó** sobre el archivo previo (rompe write-once), no persistió el hash, y emitió el
evento antes de que el reporte existiera.

- D1 = 1.0 · D2 = 1.0 · D3 = 1.0 · D4 = 1.0
- D5 = 0.5 — fiel pero reescritura de archivo acumulado, sin hash persistido.
- D6 = 0.5 — reporte incompleto.
- D7 = 0.5 — evento existe pero se emitió fuera de orden.

> Score: ≈ 0.79 → REJECTED (sin veto, pero < 0.80; D5 cae a 0.5, no a 0.0).

---

### Score global ≈ 0.80 — Pipeline correcto, falta el warning de rango

**Perfil:** todo verificable; el historial real (3.4 años) difería del declarado (2 años) pero
el reporte no lo anotó como warning.

- D1 = 1.0 · D2 = 1.0 · D3 = 1.0 · D4 = 1.0 · D5 = 1.0
- D6 = 0.5 — falta el warning de rango (P5) que sí ocurría.
- D7 = 1.0 — evento como último paso, payload completo.

> Score: (1+1+1+1+1+0.5+1)/7 = **0.93** → APPROVED. (El gap de D6 es menor: no invalida el
> Bronce, pero el 020 pierde una señal.)

---

### Score global = 1.00 — Ejecución perfecta

**Perfil:** CSV `;` en cp1252; 45.230 filas; rango 2023-01-01 → 2026-05-31 (1.246 días); 12
errores en `cantidad_solicitada`; 34 duplicados internos registrados (batch, no eliminados);
Bronce `orders_batch_20260608.csv` con SHA-256 `a3f…`; manifest e intake_report completos;
warning de rango anotado; `intake_complete` emitido y con `next_harnesses: [020, 025]`.

- D1 = 1.0 — `;` + cp1252 detectados, acentos intactos.
- D2 = 1.0 — los 4 mínimos presentes, gate aprobó.
- D3 = 1.0 — 12 errores contados, ninguna fila eliminada.
- D4 = 1.0 — 34 duplicados internos contados, conservados en Bronce.
- D5 = 1.0 — Bronce byte-exacto, hash recalculado coincide con el manifest, write-once.
- D6 = 1.0 — los tres artefactos completos, `files` con hash, warning de rango anotado.
- D7 = 1.0 — evento como último paso, payload completo.

> Score: 1.00 → APPROVED (sin vetos).

---

## Clasificación de hallazgos

En `verdict.json` bajo `rejection_reasons` / `recommendations`:

**Major** (score 0.0 en la dimensión o veto activo): gate roto (D2), Bronce no fiel o sin hash
(D5), evento ausente o fuera de orden (D7), acentos corruptos (D1), filas eliminadas (D3/D4).

**Minor** (score 0.5): warning de rango omitido, `encoding` no registrado, conteo impreciso,
inconsistencia menor manifest↔log, `event_emitted` no actualizado.

---

## Nota sobre evolución de la rúbrica

Las dimensiones del 015 son estables (verificables criptográficamente). Si en el futuro se
añade un tercer esquema o nuevos campos mínimos (DEC-014), actualizar D2/D3 aquí y en
`intake-report-schema` de forma coordinada. Los pesos de cobro (complejidad de datos) **no**
forman parte de esta rúbrica — son del 020, no del 015.
