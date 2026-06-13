# Lessons Learned — 015 Intake
# Harness FARO — Sabbia Solutions & Software
# Escritores: Evaluator (C) al cierre · Governor (A) tras rechazos estratégicos u overrides
# Lector obligatorio: Orchestrator (B) en Modo PLAN y tras rechazos (§12.2 paso 2)

> Las lecciones son **transversales** — aplican a todos los tenants, a diferencia de las
> decisiones por tenant de `decisions_library.md`. Archivo **append-only**: nunca se borra ni
> edita una entrada; una lección superada se matiza con una entrada nueva. IDs secuenciales
> globales (`LEC-001`, `LEC-002`, …), sin reiniciar entre tenants ni ciclos.

### Cuándo agregar una entrada

**C agrega una entrada al cierre cuando:**
- Una dimensión de la rúbrica (`intake-rubric`) fue vetada o quedó < 0.5.
- El Worker requirió más de un reintento para completar el pipeline.
- Se detectó una inconsistencia no contemplada en los schemas (p. ej. SHA-256 que no recalcula,
  bit-exactitud rota, conteo de errores de tipo subestimado).

**A agrega una entrada cuando:**
- Se autorizó un override de write-once (rework D5) o un cambio que alteró el comportamiento del
  pipeline.
- El ciclo reveló un gap en las instrucciones del governor, del orchestrator o del processor.

**No** agregar entrada si el ciclo cerró sin rechazos, bloqueos ni sorpresas: escribir solo la
nota de cierre limpio (`"Ciclo sin rechazos ni bloqueos — ninguna lección registrada"`).

### Formato de cada entrada

```markdown
## Ciclo {N} — {tenant_id} — {fecha YYYY-MM-DD} — entrega {delivery_id}

### LEC-{NNN} — {Título breve de la lección}
**Fecha:** {YYYY-MM-DD}
**Fuente:** {C — evaluación de fidelidad | A — rechazo estratégico | A — override operador}
**Módulo/Agente afectado:** {módulo del pipeline, agente, o "flujo general"}
**Contexto:** {Qué ocurrió — descripción concisa del problema}
**Lección:** {La regla o comportamiento correcto a aplicar}
**Cómo aplicar:** {Instrucción accionable y concreta para B}
**Reintentos requeridos:** {N o "no aplica"}
```

---

_Este archivo se completa al cierre del primer ciclo de ejecución del harness._
