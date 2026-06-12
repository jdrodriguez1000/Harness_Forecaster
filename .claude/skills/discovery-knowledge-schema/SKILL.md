---
name: discovery-knowledge-schema
description: Schemas y reglas de escritura de los dos archivos de knowledge base del
  harness 010 Discovery de FARO — decisions_library.md (escrito por A al cierre) y
  lessons_learned.md (escrito por C y A al cierre o tras rechazos). Define la estructura
  de cada entrada, quién escribe, quién lee y cuándo. B debe consultar ambos archivos
  obligatoriamente al inicio de cada ejecución (12.2 paso 2). Usar cuando A escribe
  decisions_library.md o cuando C o A escriben lessons_learned.md.
user-invocable: false
---

## Ubicación y Single Writer Rule

| Archivo | Path | Escritor(es) | Lectores |
|---------|------|-------------|----------|
| `decisions_library.md` | `610_knowledge/decisions_library.md` | **Solo A** (governor) — al cierre del harness (12.5 paso 3) | B (obligatorio al inicio), A (referencia en continuaciones) |
| `lessons_learned.md` | `610_knowledge/lessons_learned.md` | **C** (al cierre, 12.5 paso 2) y **A** (tras rechazos estratégicos, 12.4) | B (obligatorio al inicio y tras rechazos), A (referencia) |

**Regla de acceso para B:** La consulta de ambos archivos en 12.2 paso 2 es **obligatoria**,
no condicional. Si los archivos no existen (primer proyecto del sistema), B registra la
ausencia en `600_persistence/execution-state.json` bajo `knowledge_base_status` y continúa.
Nunca omite el intento de lectura.

---

## 1. decisions_library.md

### Propósito

Registra las decisiones tomadas durante la ejecución del harness que afectan cómo deben
ejecutarse los ciclos futuros para el mismo cliente. No captura decisiones de diseño del
sistema (esas van en `progress/decisions.md`) — captura decisiones operativas por cliente:
ajustes de categoría, resoluciones de discrepancias, configuraciones especiales aprobadas.

### Cuándo agregar una entrada

A agrega una entrada al cierre del harness (12.5 paso 3) cuando ocurrió alguno de:
- La categoría fue ajustada (ITO discrepaba con la comercial) y el operador resolvió
- Un campo MISSING fue resuelto con un valor especial o estimado acordado con el cliente
- El horizonte de pronóstico o la jerarquía fue configurada de forma no estándar
- Se aceptó un cliente con historial < 3 meses bajo condiciones especiales
- Cualquier override del operador que cambie el comportamiento esperado del harness

Si el ciclo transcurrió sin decisiones especiales, A escribe solo el encabezado del ciclo
y la nota `"Sin decisiones especiales en este ciclo"`.

### Estructura del archivo

El archivo es **append-only** — nunca se borra ni se edita una entrada anterior.
Cada ciclo de ejecución agrega su bloque al final.

```markdown
# Decisions Library — 010 Discovery
# Harness FARO — Sabbia Solutions & Software
# Escritor: Governor (Instancia A) · Lector obligatorio: Orchestrator (Instancia B)

---

## Ciclo {N} — {tenant_id} — {fecha YYYY-MM-DD}

### DEC-{NNN} — {Título breve de la decisión}
**Fecha:** {YYYY-MM-DD}
**Tenant:** {tenant_id}
**Categoría:** {comercial | técnica | operativa}
**Decisión:** {Qué se decidió, en una o dos oraciones}
**Razón:** {Por qué — el contexto que llevó a esta decisión}
**Impacto en futuras ejecuciones:** {Qué debe saber B la próxima vez que ejecute para este tenant}

---
```

### Reglas de escritura

1. **IDs secuenciales por harness** — el primer DEC del primer ciclo es DEC-001. El contador no reinicia entre clientes ni entre ciclos.
2. **Categorías válidas:** `comercial` (ajustes de precio, categoría o plan), `técnica` (fallbacks activados, umbrales alterados), `operativa` (campos MISSING resueltos, configuraciones especiales).
3. **"Impacto en futuras ejecuciones"** es el campo más importante — es lo que B lee para no repetir preguntas ya resueltas ni ejecutar pasos que ya fueron acordados de forma especial.
4. **Sin borrar ni editar** — si una decisión fue revertida, agregar una nueva entrada que la anule, no modificar la original.
5. **Si no hay decisiones especiales:** escribir el encabezado del ciclo con la nota `"Sin decisiones especiales en este ciclo"` para confirmar que A revisó.

### Ejemplo de entrada

```markdown
## Ciclo 1 — alimentos-abc-3207 — 2026-06-08

### DEC-001 — Categoría ajustada de M a L tras revisión comercial
**Fecha:** 2026-06-08
**Tenant:** alimentos-abc-3207
**Categoría:** comercial
**Decisión:** El ITO calculado (41.20) ubica al cliente en categoría L, pero fue vendido
como M. El gerente comercial de Triple S revisó y confirmó que el precio correcto es L
(USD 350/mes). Se actualizó client_profile.json con categoría=L.
**Razón:** El proceso comercial usó estimaciones de SKUs más bajas que las reales declaradas
en sesión (60 vs 210 SKUs activos). El ITO real es superior al umbral de M.
**Impacto en futuras ejecuciones:** Para este tenant, la categoría L es la definitiva.
No volver a calcular desde cero — leer este registro antes de presentar la categoría al
operador para evitar confusión con la categoría comercial original.

---
```

---

## 2. lessons_learned.md

### Propósito

Registra lecciones técnicas y operativas que mejoran la calidad de las ejecuciones
futuras del harness para cualquier cliente. A diferencia de `decisions_library.md`
(que es por tenant), las lecciones son **transversales** — aplican a todos los clientes.

### Cuándo agregar una entrada

**C agrega una entrada al cierre del harness (12.5 paso 2) cuando:**
- Una dimensión de la rúbrica fue rechazada (score < 0.5 o veto)
- Un Worker requirió más de 1 reintento para completar
- Se detectó una inconsistencia que no estaba contemplada en los schemas
- El flujo se bloqueó por un motivo no previsto

**A agrega una entrada cuando:**
- El operador rechazó los borradores en CP-03 (rechazo estratégico)
- Se activó un override o restricción que cambió el comportamiento del harness
- El ciclo reveló un gap en las instrucciones del governor o los workers

**No agregar entrada si** el ciclo transcurrió sin rechazos, bloqueos ni sorpresas. En ese
caso C y A escriben solo la nota de cierre limpio.

### Estructura del archivo

También **append-only**. Cada ciclo agrega su bloque al final.

```markdown
# Lessons Learned — 010 Discovery
# Harness FARO — Sabbia Solutions & Software
# Escritores: Evaluator (C) al cierre · Governor (A) tras rechazos estratégicos
# Lector obligatorio: Orchestrator (B) al inicio y tras rechazos

---

## Ciclo {N} — {tenant_id} — {fecha YYYY-MM-DD}

### LEC-{NNN} — {Título breve de la lección}
**Fecha:** {YYYY-MM-DD}
**Fuente:** {C — evaluación técnica | A — rechazo estratégico | A — override operador}
**Worker/Agente afectado:** {nombre del worker o "governor" o "flujo general"}
**Contexto:** {Qué ocurrió — descripción concisa del problema o situación}
**Lección:** {La regla, insight o comportamiento correcto que se debe aplicar}
**Cómo aplicar:** {Cuándo y dónde aplicar esta lección — instrucción accionable para B}
**Reintentos requeridos:** {N o "no aplica"}

---
```

### Reglas de escritura

1. **IDs secuenciales globales** — LEC-001, LEC-002... El contador no reinicia entre clientes ni ciclos. Si el archivo ya tiene LEC-014 (de ciclos anteriores), la siguiente es LEC-015.
2. **"Cómo aplicar" es accionable** — debe ser una instrucción concreta que B pueda seguir sin ambigüedad, no una observación general.
3. **Fuente siempre especificada** — quién escribe la entrada y por qué: C tras evaluación técnica, A tras rechazo estratégico o override.
4. **Cierre limpio** — si no hay lecciones en el ciclo, escribir el encabezado con `"Ciclo sin rechazos ni bloqueos — ninguna lección registrada"`.
5. **Sin borrar ni editar** — si una lección fue superada por una nueva, agregar una nueva entrada que la reemplace o matice, no modificar la original.

### Ejemplo de entrada técnica (escrita por C)

```markdown
## Ciclo 1 — alimentos-abc-3207 — 2026-06-08

### LEC-001 — correo_pendiente.json ausente provoca D6 = 0.5 aunque la guía existe
**Fecha:** 2026-06-08
**Fuente:** C — evaluación técnica
**Worker/Agente afectado:** discovery-configurator
**Contexto:** La guía data_intake_guide.md fue generada y estaba correctamente personalizada,
pero no existía correo_pendiente.json. El evaluador asignó D6 = 0.5 porque no había evidencia
de que la guía fue enviada ni registrada como pendiente.
**Lección:** El configurator debe crear correo_pendiente.json siempre que SendGrid no esté
disponible (Fase 1). La ausencia del archivo de registro es indistinguible de un fallo de
envío para el evaluador.
**Cómo aplicar:** Al ejecutar discovery-configurator en Modo COMMIT, verificar que
correo_pendiente.json fue creado antes de reportar COMMIT_COMPLETE. Si falta, crearlo
con _pendiente_envio: true antes de continuar.
**Reintentos requeridos:** 0 (detectado en evaluación, no durante ejecución)

---
```

### Ejemplo de entrada estratégica (escrita por A)

```markdown
### LEC-002 — Operador solicitó cambiar horizonte de "meses" a "semanas" en CP-03
**Fecha:** 2026-06-08
**Fuente:** A — rechazo estratégico
**Worker/Agente afectado:** discovery-configurator (borrador onboarding_config.json)
**Contexto:** El operador rechazó el borrador porque el horizonte de pronóstico "meses"
no coincidía con lo acordado verbalmente con el cliente durante la sesión. El cliente
mencionó "semanas" al final de la reunión pero el interviewer registró "meses".
**Lección:** El campo horizonte_pronostico es uno de los más propensos a ambigüedad en
sesión — el cliente puede mencionar varios horizontes y el interviewer puede registrar
el último mencionado en vez del más relevante. Confirmar explícitamente al final de la
sesión.
**Cómo aplicar:** Al ejecutar discovery-interviewer, incluir una pregunta de confirmación
explícita sobre el horizonte al final del Bloque 5, antes de cerrar la sesión: "Para
confirmar: ¿el horizonte principal de su pronóstico es [valor registrado]?"
**Reintentos requeridos:** 1 (re-ejecución de discovery-interviewer en modo complementario)

---
```

---

## Cómo B debe usar estos archivos (12.2 paso 2)

Al iniciar la ejecución técnica, B debe:

1. Intentar leer `610_knowledge/decisions_library.md`.
   - Si existe: identificar entradas con el `tenant_id` del cliente actual. Extraer el campo
     `"Impacto en futuras ejecuciones"` de cada entrada relevante. Aplicarlo antes de
     spawnear cualquier worker.
   - Si no existe: registrar en `execution-state.json`: `"knowledge_base_status": {"decisions_library": "NOT_FOUND", "lessons_learned": "..."}` y continuar.

2. Intentar leer `610_knowledge/lessons_learned.md`.
   - Si existe: leer todas las entradas. Las lecciones son transversales — todas aplican
     independientemente del tenant. Prestar atención especial a las entradas del worker
     que B está a punto de spawnear.
   - Si no existe: registrar en `execution-state.json` y continuar.

3. Tras un rechazo (12.4): releer `610_knowledge/lessons_learned.md` antes de re-spawnear
   el worker fallido. Es obligatorio — no relanzar un worker sin consultar las lecciones.

**Regla de aplicación:** B no debe incluir el contenido de los archivos de knowledge en
el prompt del worker — solo los lineamientos relevantes en forma de instrucciones concretas.
Los archivos pueden ser largos; pasarlos completos consumiría contexto innecesariamente.
