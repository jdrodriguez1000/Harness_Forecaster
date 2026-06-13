# Lecciones Aprendidas — Harness Forecaster

Leer a demanda antes de implementar para evitar repetir problemas.
Cada lección incluye el contexto en que surgió y cómo aplicarla.

---

## Índice (catálogo)

> Escanea esta tabla y abre solo la entrada que necesites (busca `## LEC-NNN`). **Alcance:** `Fundacional` = lección transversal (metodología, prompts, infra, patrones reutilizables en todos los harnesses); `H-010` = específica de la mecánica del harness 010. Las entradas no están en orden numérico estricto en el cuerpo — usa el buscador.

| ID | Título | Alcance |
|---|---|---|
| LEC-001 | El modelo de negocio define la arquitectura, no al revés | Fundacional |
| LEC-002 | Los SLAs de precisión deben vincularse a la calidad de los datos | Fundacional |
| LEC-003 | La unidad de análisis es cliente × producto | Fundacional |
| LEC-004 | Las reglas de pago son reglas del sistema, no procesos externos | Fundacional |
| LEC-005 | Los datos originales del cliente son intocables | Fundacional |
| LEC-006 | La eliminación de datos no puede ejecutarse con exportaciones pendientes | Fundacional |
| LEC-007 | Supabase como plataforma central simplifica la operación inicial | Fundacional |
| LEC-008 | El horizonte de pronóstico es propio de cada cliente | Fundacional |
| LEC-009 | Los pedidos atípicos: clasificar antes de modelar | Fundacional |
| LEC-010 | Los replace_all en paths pueden generar rutas dobles | Fundacional (técnica) |
| LEC-011 | Los briefs deben revisarse contra principios.md y metodologia.md | Fundacional (clave para 015) |
| LEC-012 | El orchestrator (B) es un gestor de estado puro, no coordina workers | Fundacional (patrón) |
| LEC-013 | Las skills son carpetas con SKILL.md, no archivos sueltos | Fundacional |
| LEC-014 | Un worker interactivo no puede spawnarse vía CLI (corre inline) | Fundacional (patrón) |
| LEC-015 | Los workers que tocan sistemas externos necesitan fallback local | Fundacional |
| LEC-016 | El ITO usa normalización para que las 3 dimensiones tengan peso real | H-010 (liga T-178) |
| LEC-017 | El evaluador debe ser delgado y delegar el scoring a una skill | Fundacional (patrón) |
| LEC-018 | Los knowledge base son append-only y requieren IDs globales | Fundacional |
| LEC-019 | Los skills son la fuente autoritativa sobre los archivos plan/ | Fundacional |
| LEC-020 | El deploy requiere dos carpetas fuente por harness: scripts/ y templates/ | Fundacional (infra) |
| LEC-021 | Los templates de proyecto cliente deben adaptarse, no copiarse | Fundacional |
| LEC-022 | El governor debe usar la misma env var que el deploy script | Fundacional (infra) |
| LEC-023 | Los workflows referenciados en CLAUDE.md deben existir en el deploy | Fundacional |
| LEC-024 | Archivos de stack en proyectos cliente crean deuda sin valor | Fundacional |
| LEC-025 | Brecha de reanudación E10-B: caso ESCALATION post-interviewer | H-010 |
| LEC-026 | Discovery no es un formulario — es una conversación | H-010 |
| LEC-027 | Un stakeholder puede cubrir múltiples roles | H-010 |
| LEC-028 | La síntesis puede derivar artefactos de compatibilidad downstream | H-010 |
| LEC-029 | Las verificaciones de reanudación deben ser explícitas y ordenadas | Fundacional (patrón) |
| LEC-030 | Al insertar un worker, el checkpoint del tramo se mueve al worker final | Fundacional (patrón) |
| LEC-031 | Los workers interactivos largos necesitan guardado incremental | Fundacional (patrón) |
| LEC-032 | El comando de emergencia complementa, no reemplaza, el guardado auto | H-010 |
| LEC-033 | Las skills del deploy deben llevar el prefijo del harness | Fundacional (infra) |
| LEC-034 | El CLAUDE.md cliente debe usar patrones genéricos, no bloques por harness | Fundacional |
| LEC-035 | El Sprint Contract debe ser autocontenido (entradas/salidas/checkpoints) | Fundacional (patrón) |
| LEC-036 | La prueba de humo revela gaps de comportamiento no vistos en código | Fundacional (metodología) |
| LEC-037 | La suspensión en T-092 fue manual por tokens, no un bug | H-010 |
| LEC-038 | El orchestrator debe inicializarse con la cadena de workers actual | H-010 |
| LEC-039 | Las rutas de archivo en los agentes solo se validan en ejecución real | Fundacional (metodología) |
| LEC-040 | El Sprint Contract no debe pedir datos inexistentes en la etapa | Fundacional |
| LEC-041 | Los commands deben deployarse al proyecto cliente, no solo global | Fundacional (infra) |
| LEC-042 | El analyst no genera su tenant_id — lo lee de harness-state.json | Fundacional (liga DEC-047) |
| LEC-043 | El interviewer debe cerrar el estado del último stakeholder | H-010 |
| LEC-044 | El configurator preserva la riqueza semántica, no la resume | Fundacional (liga T-179) |
| LEC-045 | El configurator debe conocer la ruta canónica del evento | H-010 |
| LEC-046 | Una tarea "implementada" no garantiza el comportamiento en runtime | Fundacional (metodología) |
| LEC-047 | El governor pre-registra escalamientos antes de invocar al evaluador | H-010 |
| LEC-048 | Agents y skills globales contaminan sesiones no-FARO | Fundacional (infra) |
| LEC-049 | La instalación a nivel de proyecto es el modelo correcto | Fundacional |
| LEC-050 | `FARO_HOME` en settings.local.json permite a los comandos hallar el repo | Fundacional (infra) |
| LEC-051 | El governor debe crear todas las carpetas del runtime | Fundacional (patrón) |
| LEC-052 | Las guías de preguntas del interviewer deben vivir en el proyecto | H-010 |
| LEC-053 | Las respuestas del operador van en la terminal donde corre el agente | Fundacional (metodología de prueba) |
| LEC-054 | "PARAR COMPLETAMENTE — no escribir texto" paraliza al agente | Fundacional (prompts) |
| LEC-055 | El lenguaje condicional suave vuelve opcional un paso obligatorio | Fundacional (prompts) |
| LEC-056 | Separar el turno de setup del de entrevista fuerza la creación de archivos | Fundacional (prompts) |
| LEC-057 | Un agente no debe cargar una skill que describe el artefacto de otro | Fundacional |
| LEC-058 | execution-state.json no registra la completitud del interviewer | H-010 |
| LEC-059 | El governor no debe lanzar workers como `claude --print` en background | Fundacional (conductor) |
| LEC-060 | Validar e2e destapa regresiones que el flujo anterior enmascaraba | Fundacional (metodología) |
| LEC-061 | Un governor sin estado registra eventos duplicados al re-derivar | Fundacional (patrón) |
| LEC-062 | Al corregir un campo transversal, auditar TODOS sus escritores | Fundacional (metodología) |
| LEC-063 | En Windows la allowlist debe cubrir PowerShell, no solo Bash | Fundacional (infra) |
| LEC-064 | La allowlist no silencia las heurísticas de seguridad; bypass por proyecto | Fundacional (infra) |
| LEC-065 | Un APPROVED no audita la calibración ni la riqueza semántica | Fundacional (metodología) |
| LEC-066 | Los timestamps redactados por el agente no son reloj de ejecución | Fundacional (liga T-180) |

---

## LEC-001 — El modelo de negocio define la arquitectura, no al revés
**Contexto:** Al inicio se asumió un modelo SaaS con multi-tenancy autoservicio. El usuario corrigió: el modelo es Service as a Software donde Triple S opera todo.
**Lección:** Antes de proponer cualquier componente técnico, confirmar el modelo de negocio. En este proyecto el cliente no opera el sistema — solo consume resultados. Esto elimina portales de configuración, APIs públicas y autoservicio del cliente.
**Cómo aplicar:** Si una propuesta técnica requiere que el cliente configure algo, pausar y preguntar si eso es coherente con el modelo de servicio.

---

## LEC-002 — Los SLAs de precisión deben estar vinculados a la calidad de los datos
**Contexto:** Al definir SLAs se intentó fijar un MAPE único. Pero la precisión del pronóstico depende directamente de la calidad de los datos del cliente.
**Lección:** No comprometer precisión sin condicionarla al índice de salud de datos. Un cliente con datos en mal estado no puede recibir la misma garantía de precisión que uno con datos en excelente estado.
**Cómo aplicar:** Siempre que se mencione precisión del pronóstico, verificar que esté referenciada al umbral de salud de datos correspondiente (ver DEC-009).

---

## LEC-003 — La unidad de análisis es cliente × producto, no cliente ni producto por separado
**Contexto:** Al pensar en frecuencias de pedido se asumió inicialmente que había un ciclo por cliente. El usuario aclaró que un mismo cliente puede tener frecuencias distintas por producto.
**Lección:** Nunca asumir ciclos estándar. La granularidad mínima de análisis y pronóstico es la combinación cliente × producto. Diseñar modelos de datos y agentes con esta granularidad desde el inicio.
**Cómo aplicar:** Al diseñar tablas, esquemas o agentes, verificar que la clave primaria de análisis incluya siempre el par (cliente, producto).

---

## LEC-004 — Las reglas de negocio de pago son reglas del sistema, no procesos externos
**Contexto:** Las reglas de mora, suspensión y renovación de fecha de pago se definieron con detalle operativo. Es tentador tratarlas como procesos administrativos externos.
**Lección:** Estas reglas deben vivir dentro del harness. El sistema debe calcular automáticamente fechas de vencimiento, emitir alertas y bloquear acceso sin intervención manual de Triple S.
**Cómo aplicar:** Al implementar el módulo de suscripciones, codificar cada regla (colores de mensaje, días de gracia, cálculo de nueva fecha) como lógica del sistema, no como tareas manuales.

---

## LEC-005 — Los datos originales del cliente son intocables
**Contexto:** Al describir la arquitectura medallón surgió la tentación de "limpiar" los datos directamente.
**Lección:** La capa Bronce es una copia exacta e inmutable. Toda transformación ocurre en capas posteriores (Plata, Oro) sobre esa copia. Nunca modificar Bronce.
**Cómo aplicar:** El pipeline de ingesta debe tener dos pasos distintos: (1) copia exacta a Bronce, (2) transformación de Bronce a Plata. Ningún proceso debe escribir sobre Bronce una vez creado.

---

## LEC-007 — Supabase como plataforma central simplifica la operación inicial
**Contexto:** Al definir el stack tecnológico se evaluó AWS S3 para almacenamiento. El usuario prefirió no usar AWS inicialmente.
**Lección:** Supabase consolida autenticación, PostgreSQL y Storage (S3-compatible) en un solo proveedor. Para un equipo pequeño como Triple S esto reduce drásticamente la complejidad operativa. La migración a AWS S3 es posible sin cambios de código cuando la escala lo requiera.
**Cómo aplicar:** Siempre que se necesite agregar un nuevo servicio de infraestructura, verificar primero si Supabase ya lo ofrece antes de agregar un proveedor externo.

---

## LEC-008 — El horizonte de pronóstico es propio de cada cliente
**Contexto:** Al definir el alcance del pronóstico se intentó establecer un horizonte global (mensual). El usuario aclaró que cada empresa ABC puede tener su propio horizonte: días, semanas, meses o múltiples meses.
**Lección:** No asumir ningún parámetro global de pronóstico. El horizonte, la frecuencia de pedido y el tiempo de entrega son todos configurables por cliente. El sistema debe ser parametrizable desde el onboarding.
**Cómo aplicar:** Al diseñar el motor de pronóstico, todos los parámetros temporales deben leerse de la configuración del cliente, nunca de constantes globales.

---

## LEC-009 — Los pedidos atípicos pueden ser legítimos o errores — siempre clasificar antes de modelar
**Contexto:** Al definir el tratamiento de pedidos extraordinarios, surgió el ejemplo de aumentos de fin de año por primas navideñas.
**Lección:** Un pedido atípico no es necesariamente un error de datos. El sistema debe clasificarlo antes de decidir si lo incluye en el modelo: si coincide con un evento conocido es un evento estacional legítimo que enriquece el modelo; si no tiene explicación, es una anomalía que debe confirmarse con el cliente.
**Cómo aplicar:** El agente de detección de anomalías siempre debe tener un paso de clasificación antes de escalar o descartar un pedido atípico.

---

## LEC-010 — Los replace_all en paths pueden generar rutas dobles si el string objetivo ya contiene parte de la ruta destino
**Contexto:** Al renombrar `/knowledge/` → `/610_knowledge/` usando replace_all, una edición previa había convertido `lessons_learned.md` en `` `/knowledge/lessons_learned.md` `` (con backticks dentro de la ruta). El replace_all produjo `` `/knowledge/`/knowledge/lessons_learned.md`` `` — una ruta malformada.
**Lección:** Antes de hacer replace_all en rutas, verificar con grep que no existen instancias ya parcialmente transformadas en el archivo. Si las hay, hacer las sustituciones en orden: primero limpiar las malformadas, luego hacer el replace_all global.
**Cómo aplicar:** Siempre hacer un grep de verificación después de cada replace_all masivo de rutas. Nunca asumir que el resultado es correcto sin inspeccionar.

---

## LEC-011 — Los briefs de harness deben revisarse contra principios.md y metodologia.md antes de darse por completos
**Contexto:** El brief del 010 Discovery se escribió con buen contenido de dominio pero con gaps de alineación: faltaba el `git init` en E10-A, la consulta de knowledge base era condicional en vez de obligatoria, C podía implícitamente escribir en `harness-state.json`, y las rutas de `/knowledge/` eran incorrectas.
**Lección:** Todo brief nuevo debe pasar por una revisión explícita contra `documents/principios.md` y `documents/metodologia.md` antes de marcarse como `implementada`. Los gaps más comunes son: (1) Ritual E10-A sin `git init`, (2) Single Writer Rule no explícita, (3) rutas de `/knowledge/` incorrectas, (4) consulta de knowledge base tratada como opcional.
**Cómo aplicar:** Usar el checklist de gaps identificados en la sesión 2026-06-08 como referencia para revisar cada nuevo brief.

---

## LEC-012 — El orchestrator (B) NO coordina workers — es un gestor de estado puro
**Contexto:** El primer borrador de `discovery-orchestrator.md` tenía lógica de coordinación (spawnear workers, tomar decisiones de gate). Al revisar la carpeta Temporal con harnesses anteriores, se descubrió que el orchestrator solo gestiona estado.
**Lección:** El governor (A) es quien spawna todos los workers directamente vía CLI (`claude --agent <nombre> --print --dangerously-skip-permissions`). El orchestrator recibe el resultado del governor y actualiza `execution-state.json`. Solo tiene tres modos: PLAN, CHECKPOINT y WORKER_FAILED.
**Cómo aplicar:** Si el orchestrator de cualquier harness tiene lógica de "si pasa X entonces spawna Y", mover esa lógica al governor. El orchestrator solo lee estado, escribe estado y retorna resultados estructurados.

---

## LEC-013 — Las skills son carpetas con SKILL.md, no archivos .md sueltos
**Contexto:** Al crear las primeras skills se asumió que eran archivos `.md` en `.claude/skills/`. El script `deploy-harness.ps1` busca directorios con prefijo `discovery-*` en `.claude/skills/`.
**Lección:** Cada skill es un **directorio** con un archivo `SKILL.md` dentro. El directorio tiene el nombre de la skill (ej: `discovery-state-schema/`). Las skills son documentos de referencia — schemas, formatos, reglas de escritura — no procedimientos.
**Cómo aplicar:** Al crear una skill nueva, siempre crear el directorio primero (`New-Item -ItemType Directory`) y luego escribir `SKILL.md` dentro. Verificar que el deploy script la detecte correctamente.

---

## LEC-014 — discovery-interviewer es interactivo y no puede spawnarse vía CLI
**Contexto:** Al diseñar el governor, se asumió que todos los workers se invocan vía CLI. El interviewer necesita hacer preguntas al operador y recibir respuestas en tiempo real.
**Lección:** Los workers interactivos (como discovery-interviewer) no pueden spawnarse vía `claude --agent ... --print` porque ese modo no permite interacción. El governor retorna `INTERVIEWER_REQUIRED` y el workflow (CLAUDE.md del proyecto cliente) lo ejecuta directamente en la sesión principal de Claude Code.
**Cómo aplicar:** Al diseñar workers, clasificarlos explícitamente como interactivos o no-interactivos antes de escribir el governor. Los interactivos requieren un modo de delegación especial en el governor.

---

## LEC-017 — El evaluador debe ser un agente delgado que delega la lógica de scoring a una skill
**Contexto:** El primer borrador de `discovery-evaluator.md` tenía toda la rúbrica embebida (criterios, anclas, campos a verificar, fórmulas). Además contenía umbrales ITO incorrectos (≤ 1500, ≤ 4000) que no correspondían con la escala normalizada del analyst.
**Lección:** El evaluador debe cargar una skill de rúbrica (`discovery-rubric`) y aplicarla — no repetir los criterios inline. Esto garantiza que si los umbrales o criterios cambian, solo se actualiza la skill y el evaluador sigue siendo válido sin modificaciones. El agente solo orquesta la lectura de artefactos, el cálculo del score y la escritura del veredicto.
**Cómo aplicar:** Al escribir evaluadores de harnesses futuros, seguir el mismo patrón: agente delgado + skill de rúbrica separada. Los únicos criterios en el agente son los procedimentales (cómo leer, cómo calcular, qué escribir), nunca los sustantivos (qué significa cada score).

---

## LEC-018 — Los archivos de knowledge base (decisions_library, lessons_learned) son append-only y requieren IDs globales
**Contexto:** Al diseñar `discovery-knowledge-schema`, surgió la pregunta de si los IDs de decisiones y lecciones debían reiniciarse por cliente o por ciclo.
**Lección:** Los IDs son globales y secuenciales a lo largo de toda la vida del sistema (DEC-001, DEC-002... y LEC-001, LEC-002... sin reiniciar). Esto permite referenciar decisiones y lecciones específicas desde cualquier harness o sesión sin ambigüedad. Los archivos nunca se editan — si una decisión o lección es reemplazada, se agrega una nueva entrada que la anula.
**Cómo aplicar:** Al escribir el governor de cualquier harness, leer el último ID de cada archivo de knowledge antes de agregar una entrada nueva para continuar la secuencia correctamente.

---

## LEC-015 — Los workers que tocan sistemas externos necesitan fallback local explícito desde el inicio
**Contexto:** Al escribir `discovery-configurator.md`, este worker debe crear registros en Supabase, enviar correos con SendGrid y emitir eventos con Prefect. En Fase 1 ninguno de esos sistemas existe.
**Lección:** Todo worker que dependa de infraestructura externa (BD, Storage, correo, eventos) debe tener un fallback local completo y documentado desde la primera versión del agente. El fallback no es un parche — es el modo de operación real de Fase 1. Estructura recomendada: detectar si el sistema externo está disponible (variable de entorno o config), y si no, escribir localmente con `_pendiente_supabase: true` o similar.
**Cómo aplicar:** Al escribir cualquier worker de harness posterior que toque Supabase, SendGrid, Prefect u otro sistema externo, incluir siempre la sección "Detectar fase de operación" con fallback local para Fase 1.

---

## LEC-016 — El ITO usa normalización para que las tres dimensiones tengan peso real
**Contexto:** La fórmula ITO podría aplicarse como suma ponderada directa sobre valores crudos (SKUs, clientes, pedidos). Pero las escalas son muy distintas: un cliente puede tener 100 SKUs y 5.000 pedidos, lo que haría que pedidos dominara completamente el resultado.
**Lección:** Normalizar cada componente a escala 0–100 antes de ponderar. Usar referencias máximas provisionales (SKUs: 500, clientes: 100, pedidos: 2.000) hasta que T-030 calibre los valores reales con datos del primer piloto. Marcar siempre el ITO como `provisional: true` hasta esa calibración.
**Cómo aplicar:** El `discovery-analyst.md` ya implementa esta normalización. Si se ajustan las referencias máximas en T-030, actualizar los valores en el agente y en `discovery-analysis-schema/SKILL.md`.

---

## LEC-019 — Los skills son la fuente autoritativa sobre los archivos plan/ cuando hay conflicto
**Contexto:** Al implementar `ito_calculator.py`, el `plan/010_discovery.md` tenía pesos W1=0.4, W2=0.4, W3=0.2 con umbrales crudos (1500, 4000). El skill `discovery-analysis-schema` tenía pesos W1=0.40, W2=0.35, W3=0.25 con normalización 0–100 y umbrales M≤33, L≤66, XL>66. Los archivos `plan/` se escribieron antes que los skills y quedaron desactualizados.
**Lección:** Los skills son la especificación de referencia actualizada. Los archivos `plan/` son planes de trabajo que pueden quedar desactualizados cuando se refina la especificación. Ante cualquier conflicto entre ambos, siempre usar el skill como fuente de verdad.
**Cómo aplicar:** Antes de implementar cualquier script o lógica de cálculo, leer el skill correspondiente. Si hay discrepancia con el plan, implementar según el skill y dejar nota en el plan indicando que fue actualizado por el skill.

---

## LEC-020 — El deploy-harness.ps1 requiere dos carpetas fuente por harness: scripts/ y templates/
**Contexto:** Al actualizar el deploy para el harness 010, se necesitaba un patrón genérico para copiar scripts Python y plantillas Markdown al directorio del cliente.
**Lección:** Cada harness tiene dos carpetas fuente en el repositorio: `scripts/{NNN}_{nombre}/` (scripts de soporte, Python u otros) y `templates/{NNN}_{nombre}/` (plantillas que el configurator personaliza por cliente). El deploy copia los scripts directamente a `{destino}/{NNN}_{nombre}/` y las plantillas (excepto `session_template.md`) a `{destino}/{NNN}_{nombre}/templates/`. La `session_template.md` va a la raíz de la carpeta del harness porque la usa el interviewer directamente.
**Cómo aplicar:** Al crear artefactos de soporte para harnesses futuros, colocarlos en `scripts/{NNN}_{nombre}/` o `templates/{NNN}_{nombre}/` según corresponda. El deploy los levanta automáticamente sin modificar el script.

---

## LEC-021 — Los templates de proyecto cliente deben adaptarse en cada proyecto, no copiarse directamente
**Contexto:** Al agregar `client-project-CLAUDE.md` y `client-project-settings.json` desde un proyecto anterior (FORGE), la estructura de harnesses era diferente: FORGE tenía 5 harnesses (010, 020, 030, 040, 050) y FARO tiene 11 (010–060). Los nombres de governors, rutas de persistencia (`persistence/` vs `600_persistence/`) y comandos (`/forge-restart` vs `/faro-restart`) también diferían.
**Lección:** Al incorporar templates de proyectos anteriores, siempre hacer una revisión explícita contra la estructura actual del proyecto destino antes de aceptarlos. Los cambios más frecuentes entre proyectos son: secuencia de harnesses, nombres de governors, ruta de persistencia y comandos de gestión.
**Cómo aplicar:** Antes de mover cualquier archivo desde `Temporal/` al repositorio, leer el deploy script para entender qué rutas y nombres espera, y comparar con las del proyecto anterior de origen.

---

## LEC-022 — El governor debe usar la misma variable de entorno que el deploy script
**Contexto:** El `discovery-governor.md` usa `$env:FARO_DEPLOY_SCRIPT` en su sección de handoff al 015, pero `deploy-harness.ps1` inyecta la variable como `$env:HARNESS_DEPLOY_SCRIPT` en `settings.local.json` y `settings.json`. El deploy del siguiente harness fallará silenciosamente porque la variable no existe.
**Lección:** La variable de entorno que invoca el deploy script debe ser consistente en todos los agentes que la usen. El nombre canónico lo define `deploy-harness.ps1` — los agentes deben leerlo desde ahí, no inventarlo.
**Cómo aplicar:** Al escribir la sección de handoff de cualquier governor, verificar en `deploy-harness.ps1` cuál es el nombre exacto de la variable de entorno antes de escribirla en el agente.

---

## LEC-023 — Los archivos de workflow referenciados en CLAUDE.md deben existir en el deploy
**Contexto:** El template `client-project-CLAUDE.md` referenciaba `.claude/workflows/ciclo_0XX.md` que el deploy no copiaba. Se evaluaron dos opciones: eliminar las referencias o crear los archivos.
**Lección:** La opción correcta es crear los archivos como guías de navegación livianas (~80 líneas) — no eliminar las referencias. Un CLAUDE.md sin las referencias pierde la capacidad de delegar el "cómo" de cada ciclo sin mantener lógica inline. Los workflow files son ligeros: solo tabla de modos del governor y acciones por GOVERNOR_RESULT status. Ver DEC-033.
**Cómo aplicar:** Al cerrar cada harness, crear `templates/workflows/ciclo_0XX_nombre.md` antes de marcar el harness como listo. Verificar que el deploy script lo incluye (ya está configurado para copiar todo `templates/workflows/*.md`).

---

## LEC-024 — Archivos de referencia de stack en proyectos cliente crean deuda sin valor
**Contexto:** Se planificó crear `templates/default_stacks.md` para que los agentes del proyecto cliente consultaran el stack tecnológico. Al analizar quién lo leería y para qué, se concluyó que nadie lo usaría: los agentes especializados tienen el stack embebido y Claude Code no debe tomar decisiones de arquitectura en el proyecto cliente.
**Lección:** No crear archivos de "referencia global" en proyectos cliente a menos que haya un agente o un paso específico que los lea. Un archivo que nadie consume es deuda de mantenimiento pura. El criterio de evaluación es: ¿qué agente concreto lee este archivo, en qué paso, para tomar qué decisión?
**Cómo aplicar:** Antes de agregar cualquier archivo de referencia al deploy, identificar el agente consumidor y el paso específico. Si no hay respuesta concreta, no crear el archivo.

---

## LEC-025 — Brecha en la tabla de reanudación E10-B: caso ESCALATION post-interviewer no está cubierto
**Contexto:** Al analizar cómo el operador entrega información nueva al harness después de resolver una escalación, se detectó que la tabla de reanudación E10-B del governor tiene un caso no mapeado. Cuando la escalación es por campos ITO bloqueantes con MISSING, el estado queda: `harness-state.json status=ACTIVE`, `execution-state.json last_checkpoint=null` (CP-01 nunca se registró porque la escalación ocurre antes), y `escalations[]` no vacío. La tabla E10-B interpreta `last_checkpoint=null` como arranque fresco y reconstrye el Sprint Contract, ignorando que hay una sesión parcial con MISSING en `session_data.json`.
**Lección:** La tabla de reanudación debe cubrir explícitamente el estado post-escalación: `status=ACTIVE AND last_checkpoint=null AND escalations[]!=vacío AND session_data.json existe` → retornar `RESUME_AFTER_ESCALATION` y re-ejecutar el interviewer en modo complementario (solo campos faltantes). Sin este caso, el harness repite trabajo innecesario y el `session_data.json` parcial queda huérfano.
**Cómo aplicar:** Al corregir el governor (T-106), agregar esta verificación ANTES de la tabla de reanudación estándar. Aplicar el mismo patrón en governors de harnesses futuros que tengan escalaciones antes del primer checkpoint.

---

## LEC-026 — Discovery no es un formulario — es una conversación para construir comprensión
**Contexto:** El `discovery-interviewer` original fue diseñado como un capturador de campos: preguntaba campo por campo, los mapeaba a `session_data.json` y avanzaba. Al analizar las preguntas reales que hacía, era indistinguible de llenar un formulario en voz alta. No profundizaba en respuestas, no detectaba contexto cualitativo, no identificaba señales de riesgo no formuladas, y no preguntaba "¿por qué?".
**Lección:** Una sesión de discovery tiene valor solo si produce comprensión del problema real, no solo datos estructurados. El entrevistador debe: (1) abrir con preguntas contextuales antes de preguntar datos, (2) hacer seguimiento cuando una respuesta es vaga o contradictoria, (3) capturar el "estado emocional" del stakeholder (urgencia, frustración, expectativas), (4) identificar quién más tiene perspectiva relevante. Los campos del schema son consecuencia de la conversación, no el objetivo.
**Cómo aplicar:** Al rediseñar el interviewer (T-101), construir primero el marco de preguntas abiertas por rol antes de pensar en el schema de salida. El schema de salida es la última cosa que se diseña, no la primera.

---

## LEC-027 — Un stakeholder puede cubrir múltiples roles; las preguntas deben adaptarse sin repetir
**Contexto:** Al diseñar el modelo multi-stakeholder del interviewer, surgió el caso de que en empresas medianas una sola persona frecuentemente cubre negocio + técnico + usuario. Si el interviewer hace todas las preguntas de todos los roles a la misma persona, la sesión se vuelve repetitiva y agotadora.
**Lección:** El interviewer debe detectar qué roles tiene asignados el stakeholder (del brief o por declaración propia durante la entrevista) y generar solo las preguntas relevantes para esos roles, sin duplicar. Si un stakeholder tiene rol negocio + técnico, la sesión cubre ambos bloques en una sola conversación. Si tiene solo usuario, la sesión es más corta y enfocada.
**Cómo aplicar:** Al implementar T-101, el interviewer debe construir el plan de preguntas por sesión cruzando roles del stakeholder × preguntas del banco de roles, eliminando duplicados. No hay una secuencia fija — la conversación se adapta.

---

## LEC-028 — El agente de síntesis puede derivar artefactos de compatibilidad para no romper interfaces downstream
**Contexto:** Al rediseñar el interviewer para producir `session_notes.json` (notas brutas) en vez de `session_data.json` (campos estructurados), el analyst quedaba huérfano — su entrada de datos cambió de escritor. Había dos opciones: actualizar el analyst para leer `synthesis_report.json`, o hacer que el synthesizer derive `session_data.json` con los campos consolidados.
**Lección:** Cuando un rediseño cambia el escritor de un artefacto pero no su estructura, el agente nuevo puede derivar el artefacto antiguo como paso final para mantener las interfaces downstream sin cambios. Esto aísla el cambio arquitectónico al synthesizer y evita una cascada de actualizaciones en el analyst, configurator y evaluator.
**Cómo aplicar:** Antes de cambiar el escritor de un artefacto compartido, evaluar si el agente nuevo puede derivar el artefacto viejo como último paso. Si la estructura no cambia, esta es la opción de menor fricción.

---

## LEC-029 — Las verificaciones previas en tablas de reanudación deben ser explícitas y ordenadas
**Contexto:** La tabla E10-B del governor tenía el caso `last_checkpoint=null` mapeado a "construir Sprint Contract desde cero". Pero ese mismo estado puede significar "hubo escalación post-interviewer" — dos situaciones radicalmente distintas con el mismo fingerprint superficial.
**Lección:** Las tablas de reanudación deben tener verificaciones previas explícitas que evalúen combinaciones de campos antes de llegar a la tabla. El orden importa: verificar primero los estados excepcionales (`SUSPENDED`, `AUDIT_PENDING`, `ESCALATION post-interviewer`) antes de la lógica general. Sin este orden, los casos excepcionales caen en la rama equivocada.
**Cómo aplicar:** Al diseñar o revisar tablas de reanudación en governors futuros, listar todos los estados posibles incluyendo los estados de escalación, y agregar una verificación previa por cada uno antes de la tabla principal.

---

## LEC-031 — Los workers interactivos con sesiones largas necesitan guardado incremental, no solo al finalizar
**Contexto:** El `discovery-interviewer` original guardaba `session_notes.json` al terminar la sesión completa de un stakeholder. Una sesión con tres roles puede tener 30–50 intercambios y durar 30–40 minutos. Si Claude Code se cierra, el navegador se cuelga o el operador comete un error, toda esa sesión se pierde sin posibilidad de recuperación parcial.
**Lección:** Cualquier worker interactivo con sesiones de más de 10 intercambios debe guardar estado de forma incremental. El criterio práctico es: ¿puede el operador perder más de 5 minutos de trabajo si algo falla? Si sí, se necesita guardado incremental. Los bloques temáticos naturales (negocio / técnico / usuario) son el punto de guardado ideal — el operador puede repetir el bloque interrumpido sin repetir lo anterior.
**Cómo aplicar:** Al diseñar workers interactivos en harnesses futuros, identificar los puntos de guardado natural antes de escribir el agente. El patrón es: completar bloque → guardar → continuar. Nunca acumular todo al final si la sesión supera ~10 minutos.

---

## LEC-032 — El comando de emergencia complementa pero no reemplaza el guardado automático
**Contexto:** Se evaluó si el comando `/faro-save` era suficiente por sí solo para proteger la información de las entrevistas. La conclusión fue que no: depende de que el operador recuerde ejecutarlo, especialmente en momentos de alta concentración con el cliente.
**Lección:** Los mecanismos de seguridad que requieren acción humana son un complemento, no la base. La base debe ser automática y no depender de que alguien recuerde hacer algo. `/faro-save` es útil para interrupciones dentro de un bloque, pero el guardado automático por bloque es la garantía principal.
**Cómo aplicar:** Al diseñar cualquier mecanismo de persistencia en workers interactivos, implementar primero el guardado automático y agregar el comando manual como capa adicional, nunca al revés.

---

## LEC-030 — Al insertar un worker en medio de un pipeline, el checkpoint de ese tramo debe moverse al nuevo worker final, no quedarse en el original
**Contexto:** Al insertar `discovery-synthesizer` entre el interviewer y el analyst, el checkpoint CP-01 estaba registrado después del interviewer (el worker original). Pero la salida real del tramo — `session_data.json` consolidado — la produce el synthesizer. Si CP-01 quedaba después del interviewer, al reanudar desde ese punto el harness arrancaría con el analyst pero sin `session_data.json`.
**Lección:** Un checkpoint debe representar un estado completo y estable del pipeline, no la finalización de un sub-paso. Cuando se inserta un nuevo worker al final de un tramo, el checkpoint de ese tramo debe moverse al nuevo worker final. El criterio es: ¿con solo los artefactos producidos hasta este checkpoint, puede el siguiente worker correr sin información adicional? Si no, el checkpoint está en el lugar equivocado.
**Cómo aplicar:** Al insertar workers en pipelines existentes en harnesses futuros, revisar la tabla de checkpoints y verificar que cada CP sigue representando un estado completo. Si un tramo que antes tenía un solo worker ahora tiene dos, el CP se registra al completar el segundo, no el primero.

---

## LEC-033 — Las skills del deploy deben tener el prefijo del harness o el filtro las excluye
**Contexto:** Las skills `synthesis-report-schema` y `open-questions-schema` existían en `.claude/skills/` pero nunca llegaban al proyecto cliente. El `deploy-harness.ps1` copia skills usando el filtro `"discovery-*"`. Al no tener ese prefijo, eran invisibles para el deploy aunque el agente las declarara en su frontmatter.
**Lección:** Toda skill que deba deployarse a proyectos cliente debe tener el prefijo del harness al que pertenece (`discovery-*`, `intake-*`, etc.). El filtro del deploy es la única forma en que el script sabe qué skills corresponden a qué harness. Un nombre sin prefijo es un archivo huérfano que nunca viaja.
**Cómo aplicar:** Al crear una skill nueva, el primer criterio de nombre es el prefijo del harness. Verificar con `Get-ChildItem .claude/skills -Directory -Filter "{prefijo}-*"` que el script la detecta antes de marcarla como lista.

---

## LEC-034 — El CLAUDE.md del proyecto cliente debe usar patrones genéricos, no bloques repetitivos por harness
**Contexto:** El `templates/client-project-CLAUDE.md` tenía 352 líneas — 300 de ellas eran 11 bloques de handoff con lógica idéntica, solo cambiando números y nombres. Cada bloque era: verificar PENDING_HANDOFF → preguntar → deploy → verificar → actualizar estado. Repetido 11 veces consumía contexto innecesario en cada sesión del proyecto cliente.
**Lección:** Cuando un patrón de comportamiento se repite N veces con solo variables cambiando, expresarlo una sola vez con tabla de referencia. El resultado es funcionalmente equivalente y ocupa 5–10× menos contexto. El CLAUDE.md del cliente es leído en cada sesión — cada línea extra tiene un costo recurrente.
**Cómo aplicar:** Al escribir CLAUDE.md para proyectos cliente de harnesses futuros, identificar los patrones repetitivos antes de escribir y expresarlos como patrón genérico + tabla de variables. No escribir un bloque por harness si la lógica es idéntica.

---

## LEC-035 — El Sprint Contract debe ser autocontenido: entradas, salidas y descripción de checkpoints
**Contexto:** Durante la prueba de humo T-092 el operador observó que el Sprint Contract generado por el governor solo listaba los checkpoints como `CP-01, CP-02, CP-03, CP-04, CP-05` sin describir qué valida cada uno, quién lo registra ni qué artefacto produce. Tampoco mostraba las entradas requeridas ni las salidas que produce el harness.
**Lección:** El Sprint Contract es el contrato de trabajo visible para el operador. Debe ser autocontenido: cualquier persona que lo lea sin conocer el harness debe entender qué entra, qué sale y en qué puntos puede intervenir. Un contrato que solo nombra los checkpoints obliga al operador a conocer el sistema internamente para interpretar qué está aprobando.
**Cómo aplicar:** Al construir el template del Sprint Contract en cualquier governor futuro, incluir tres secciones explícitas: (1) **Entradas** — archivos y datos requeridos para que el harness arranque; (2) **Salidas** — artefactos y registros que produce el harness al completarse; (3) **Checkpoints** — tabla con columnas CP, descripción de qué valida, quién lo registra y qué artefacto lo respalda.

---

## LEC-036 — La prueba de humo reveló tres gaps de comportamiento real no detectados en revisión de código
**Contexto:** Durante la prueba de humo T-092 con Alimentos Prueba S.A. se observaron tres fallos que no eran visibles leyendo el código del agente: (1) el interviewer no leyó `800_inputs/brief.md` y preguntó datos ya provistos; (2) después del Bloque 1, `session_notes.json` no fue creado pese a que T-111 decía implementado el guardado incremental; (3) el comando `/faro-save` no estaba disponible en la terminal porque `faro-setup.ps1` no fue re-ejecutado tras crear T-112.
**Lección:** "Implementado" en tasks.md significa que el código fue escrito — no que el comportamiento fue verificado. Una instrucción en el agente puede estar redactada correctamente y aún así no ejecutarse si el modelo la interpreta con baja prioridad o la trata como condicional cuando no lo es. Solo la ejecución real revela esto. Los tres puntos también muestran que el mecanismo de instalación de comandos por copia manual tiene fricción suficiente para causar omisiones.
**Cómo aplicar:** Después de implementar cualquier comportamiento crítico en un agente (guardado, lectura de archivo, escritura de artefacto), verificar en una ejecución real que el archivo existe con el contenido esperado — no asumir que la instrucción fue suficiente. Para comandos nuevos, el mecanismo de symlink (T-115) elimina la fricción de instalación.

---

## LEC-039 — Las rutas de archivo en los agentes no se validan en el deploy — solo la ejecución real las revela
**Contexto:** Durante la prueba de humo T-129 se detectó que `session_notes.json`, `stakeholder_map.json`, `synthesis_report.json` y `open_questions.json` se estaban escribiendo en `010_discovery/` en lugar de `010_discovery/support/`. El deploy script creaba correctamente la subcarpeta `support/` (T-124), pero las instrucciones de los agentes seguían apuntando a la ruta antigua. La inconsistencia no era visible leyendo el código — solo se detectó al revisar el filesystem durante la ejecución real.
**Lección:** Cuando se reorganiza la estructura de carpetas de un harness (como hizo DEC-042), no es suficiente actualizar el deploy script y un agente. Hay que buscar sistemáticamente todas las referencias a los paths afectados en todos los archivos del harness — agentes, skills, flows, commands — con grep antes de declarar la tarea implementada.
**Cómo aplicar:** Después de cualquier cambio de rutas de artefactos, ejecutar `Grep` con el path antiguo en todo el repositorio antes de cerrar la tarea. Si hay matches: corregir. Si no hay matches: el cambio está completo.

---

## LEC-040 — El Sprint Contract no debe pedir datos que no existen en la etapa del harness
**Contexto:** Durante T-129, el governor preguntó al operador: "¿Cuál es la categoría comercial (M/L/XL)?", "¿Fecha de firma del contrato?" y "¿Referencia al contrato firmado?" — ninguno de esos datos existe en la etapa de Discovery. La categoría es un OUTPUT del discovery-analyst, no una entrada. El contrato se firma después del Discovery.
**Lección:** El template del Sprint Contract debe distinguir claramente entre entradas que ya existen al iniciar el harness y salidas que produce. Nunca incluir como "entrada requerida" un campo que es output del mismo harness o que pertenece a una etapa posterior del negocio.
**Cómo aplicar:** Al diseñar el Sprint Contract de cualquier governor futuro, revisar cada campo de "Entradas requeridas" y preguntarse: ¿este dato existe ANTES de que el harness arranque? Si la respuesta es "lo produce este harness" o "lo define una etapa posterior", moverlo a "Salidas" o eliminarlo.

---

## LEC-041 — Los commands no se deployaban al proyecto cliente — solo existían globalmente
**Contexto:** El `/faro-save` no estaba disponible en la terminal de `Test_002_Laboratorio` aunque existía en `Harness_Forecaster/commands/`. El `faro-setup.ps1` crea un junction global `~/.claude/commands/` → repo, por lo que los commands son visibles globalmente. Pero el `deploy-harness.ps1` nunca copiaba la carpeta `commands/` al proyecto cliente, así que en proyectos sin el junction global (nuevas máquinas, instalaciones parciales) los commands simplemente no existían.
**Lección:** El mecanismo de junction global de `faro-setup.ps1` es una conveniencia para la máquina del operador de Triple S, no una garantía de disponibilidad. Para que un command esté disponible de forma confiable en cualquier proyecto cliente, debe deployarse explícitamente en `.claude/commands/` del proyecto.
**Cómo aplicar:** El deploy siempre copia `commands/*.md` a `.claude/commands/` del destino. Si se agrega un nuevo command al repositorio, estará disponible en todos los proyectos desde el siguiente deploy sin cambios adicionales.

---

## LEC-037 — La suspensión durante la prueba de humo T-092 fue manual por límite de tokens, no un bug del governor
**Contexto:** Durante la prueba de humo T-092, el synthesizer detectó `plan_suscripcion` como campo bloqueante y retornó `SEGUNDA_RONDA_REQUERIDA`. El governor respondió correctamente con `INTERVIEWER_REQUIRED` modo COMPLEMENTARIO. El operador suspendió el harness manualmente porque se agotó el límite de tokens de 5 horas de Claude Code — no por un fallo del sistema. El diagnóstico original en T-125 era incorrecto.
**Lección:** Antes de registrar un comportamiento como bug, confirmar si la causa fue el sistema o una acción manual del operador. El límite de tokens de 5 horas de Claude Code es una restricción operativa real que puede interrumpir harnesses largos. No confundir suspensiones manuales con fallos del governor.
**Cómo aplicar:** Si el harness se suspende inesperadamente durante una prueba, verificar primero el `claude-progress.txt` y el contexto del operador antes de diagnosticar un bug. Para harnesses que puedan exceder 5 horas, planificar puntos de pausa naturales en los checkpoints.

---

## LEC-038 — El orchestrator debe inicializarse con la cadena de workers actual, incluido el synthesizer
**Contexto:** Durante la prueba de humo T-092, el `execution-state.json` mostraba la secuencia `[interviewer → analyst → configurator]` — el `discovery-synthesizer` no aparecía. El orchestrator fue inicializado con el plan anterior al rediseño de sesión 10. Aunque el harness completó correctamente (el governor ejecutó la cadena real), el estado registrado era inconsistente con la ejecución real.
**Lección:** Cuando se modifica la cadena de workers de un harness, actualizar explícitamente el modo PLAN del orchestrator para que la secuencia persista correctamente. El `execution-state.json` es el registro de auditoría — si no refleja la cadena real, los checkpoints quedan mal posicionados y el harness no puede reanudar correctamente desde un CP intermedio.
**Cómo aplicar:** Al modificar la cadena de workers en cualquier governor (T-126), actualizar simultáneamente el modo PLAN del orchestrator correspondiente. Verificar en la prueba siguiente que `execution-state.json` muestra la secuencia completa.

---

## LEC-042 — El analyst no debe generar su propio tenant_id — debe leerlo del harness-state.json
**Contexto:** Durante T-129 (Test_002B), `analysis_report.json` contenía `tenant_id: "laboratorios-vita-001"` mientras que `harness-state.json` y `client_profile.json` usaban `"laboratorios-vita-s-a-de-c-v-2502"`. El analyst generó el ID de forma autónoma en lugar de leerlo del estado del harness. Este mismo bug ocurrió en T-092 (Nutrivalle) y fue corregido en T-127, pero la corrección no llegó al analyst — solo al configurator.
**Lección:** El `tenant_id` es el identificador canónico del cliente en todo el sistema. Solo se genera una vez — en el governor durante E10-A — y desde ese momento todos los agentes lo leen de `harness-state.json`. Ningún agente downstream debe inferirlo, derivarlo ni generarlo de nuevo. Si un agente necesita el tenant_id, siempre debe leer el campo `harness-state.json > tenant_id`.
**Cómo aplicar:** Al escribir o revisar cualquier worker que produzca un artefacto JSON, verificar que `tenant_id` se obtiene de `harness-state.json`, no se construye internamente. Aplicar el mismo principio a cualquier campo de identidad global (phase, harness, etc.).

---

## LEC-043 — El interviewer debe cerrar el estado del último stakeholder en session_notes.json, no solo en stakeholder_map.json
**Contexto:** Durante T-129 (Test_002B), Marco Villarreal (último stakeholder entrevistado) quedó con `"estado": "en_curso"` en `session_notes.json` aunque su sesión estaba completa. El `stakeholder_map.json` lo marcaba correctamente como `"completada"`. El interviewer actualizaba el mapa pero no la entrada de notas del stakeholder al terminar la sesión de cierre (snowball).
**Lección:** Hay dos archivos que registran el estado de cada stakeholder: `session_notes.json` (notas detalladas) y `stakeholder_map.json` (mapa de cobertura). Ambos deben actualizarse de forma consistente. El paso de cierre del interviewer — que incluye la pregunta de snowball y el guardado final — debe marcar `"completada"` en ambos archivos, no solo en el mapa.
**Cómo aplicar:** Al revisar o corregir el interviewer (T-137), verificar que el paso de cierre de sesión incluye explícitamente la actualización de `estado` en la entrada de `session_notes.json` además del `stakeholder_map.json`.

---

## LEC-044 — El configurator debe preservar la riqueza semántica de los artefactos, no resumirla
**Contexto:** Durante T-129 (Test_002B), dos artefactos del configurator perdieron información valiosa: (1) `client_profile.json > criterios_exito` redujo criterios ricos y medibles de Roberto ("no repetir diciembre", "inventario verano -30%", "cambio operativo junta lunes") a etiquetas genéricas `["reducir sobre-inventario", "reducir quiebres"]`; (2) `onboarding_config.json` quedó casi idéntico a `session_data.json` — faltaban canales por usuario, campos SAP disponibles, alertas requeridas, horizontes diferenciados por perfil.
**Lección:** El configurator no es un transcriptor de campos — es quien consolida el contexto del cliente en artefactos operativos. Los criterios de éxito deben ser medibles y rastreables en el tiempo; si se pierde la especificidad, el cliente no puede verificar si el servicio cumplió lo prometido. El `onboarding_config.json` es la entrada del harness 015 — si llega escaso, los harnesses downstream trabajan con información incompleta.
**Cómo aplicar:** Al corregir el configurator (T-138 y T-139): (1) `criterios_exito` debe copiarse textualmente del `synthesis_report.json`, no parafrasarse; (2) `onboarding_config.json` debe tener una sección explícita por dimensión: canales, campos de datos, horizontes por perfil, alertas requeridas, modo de ingesta con detalle. Definir el schema completo en T-139 antes de implementar.

---

## LEC-045 — El configurator debe conocer la ruta canónica del evento — no puede inferirla
**Contexto:** Durante Test_002B, el configurator depositó el evento `onboarding_discovery_complete` en `010_discovery/deliverables/evento_pendiente.json`. El evaluador esperaba `600_persistence/events/onboarding_discovery_complete.json`. La discrepancia activó el VETO D7 y rechazó la primera auditoría (score 0.71). El governor tuvo que crear la carpeta y copiar el archivo manualmente para pasar la segunda evaluación.
**Lección:** La ruta canónica de los eventos del harness es infraestructura del sistema — no es deducible por el configurator a partir del contexto. Debe estar explícita en el prompt del configurator: "Evento debe escribirse en `600_persistence/events/onboarding_discovery_complete.json`". Sin instrucción explícita, el configurator elige una ruta plausible pero incorrecta.
**Cómo aplicar:** Al corregir el configurator (T-140), incluir la ruta canónica del evento de forma explícita y absoluta en las instrucciones del modo COMMIT. Al diseñar configurators de harnesses futuros, incluir la ruta del evento como constante en el prompt, nunca como algo que el agente debe deducir.

---

## LEC-046 — Una tarea "implementada" en tasks.md no garantiza que el comportamiento se ejecuta en tiempo real
**Contexto:** T-121 fue marcada como implementada: "Actualizar `discovery-configurator.md`: escribir `correo_pendiente.json` → renombrar a `pending_email.json` y moverlo a `600_persistence/`". En Test_002B, el configurator escribió el archivo como `010_discovery/deliverables/correo_pendiente.json` — exactamente el comportamiento incorrecto que T-121 debía corregir. Mismo patrón que LEC-036 (el interviewer no leía el brief pese a estar "implementado").
**Lección:** "Implementado" significa que el código fue escrito — no que el agente exhibe el comportamiento en ejecución real. Los LLM pueden ignorar instrucciones de baja prominencia, especialmente en prompts largos. Para comportamientos críticos de escritura de archivos (rutas, nombres, formatos), el único criterio de "implementado" es verificar que el archivo existe en el path correcto con el nombre correcto después de una ejecución real.
**Cómo aplicar:** Al corregir T-141, además de actualizar el prompt, verificar en la siguiente prueba que `600_persistence/pending_email.json` existe y `010_discovery/deliverables/correo_pendiente.json` no existe. Si el archivo aparece en el lugar incorrecto, la corrección no funcionó — aumentar la prominencia de la instrucción (moverla al inicio del paso, agregarla como CRÍTICO, etc.).

---

## LEC-047 — El governor debe pre-registrar escalamientos formales antes de invocar al evaluador
**Contexto:** En Test_002B, `responsable_pagos` estaba documentado como MISSING en `session_data.json` y en `synthesis_report.json`. El governor generó el COMMIT sin registrar un escalamiento formal (ESC-XXX) en `harness-state.json`. El evaluador aplicó la rúbrica D1: encontró el campo MISSING sin escalamiento → score 0.0. La corrección requirió una segunda auditoría (+1 iteración completa).
**Lección:** La rúbrica del evaluador requiere DOS condiciones para aprobar campos MISSING: (1) el campo está documentado como MISSING en los artefactos, y (2) hay un escalamiento formal registrado en `harness-state.json`. El governor debe verificar ambas condiciones antes de invocar al evaluador — no después. El escalamiento formal es el mecanismo que comunica "este campo falta, estamos gestionándolo" — sin él, el evaluador tiene que rechazar.
**Cómo aplicar:** Al corregir el governor (T-142), agregar un paso explícito en el modo POST_CP04 (antes de invocar al evaluador): leer `session_data.json`, identificar todos los campos con valor `MISSING`, y para cada uno verificar si existe un ESC en `harness-state.json`. Si no existe, crearlo con estado `ABIERTO` antes de continuar. Aplicar el mismo patrón en governors de harnesses futuros.

---

## LEC-049 — La instalación a nivel de proyecto es el modelo correcto para FARO (sesión 23)
**Contexto:** En sesiones anteriores se intentó instalar agents, skills y commands a nivel de usuario (`~/.claude/`) mediante junctions. Esto causó que agentes FARO aparecieran en todas las sesiones de Claude Code, consumiendo contexto innecesario. En sesión 23 se rediseñó completamente la arquitectura de instalación.
**Lección:** Todo lo que pertenece a un harness específico debe instalarse a nivel de proyecto. `faro-setup.ps1` es el instalador de proyecto — crea `.claude/agents/`, `.claude/skills/`, `.claude/commands/`, `.claude/workflows/`, `CLAUDE.md`, `settings.json`, `settings.local.json` e inyecta `FARO_HOME` como variable de entorno. `/faro-init` luego prepara las carpetas operativas del harness. Este modelo es limpio, explícito y sin contaminación entre proyectos.
**Cómo aplicar:** Nunca instalar agents o skills FARO a nivel de usuario. Al crear un proyecto cliente nuevo: `faro-setup` desde terminal → `/faro-init` → `/faro-discovery`. Ver DEC-048.

---

## LEC-050 — `FARO_HOME` en settings.local.json es el mecanismo para que los comandos encuentren el repo (sesión 23)
**Contexto:** Al eliminar `~/.faro/faro.config.json` y el modelo de junctions globales, surgió el problema de cómo los comandos slash (`/faro-init`) saben dónde está el repo FARO para copiar archivos. La solución fue inyectar `FARO_HOME` como variable de entorno en `settings.local.json` durante la ejecución de `faro-setup.ps1`.
**Lección:** `settings.local.json` soporta una sección `env` que Claude Code expone como variables de entorno en la sesión. Es el canal correcto para inyectar rutas y configuraciones específicas de la máquina sin necesitar archivos de configuración adicionales ni machine-level setup. `settings.local.json` siempre se regenera al ejecutar `faro-setup.ps1` — garantiza que `FARO_HOME` refleja la ubicación real del repo en esa máquina.
**Cómo aplicar:** Si en harnesses futuros un comando necesita acceder al repo, leer `$env:FARO_HOME` — no hardcodear rutas ni leer archivos de configuración adicionales.

---

## LEC-048 — Agents y skills a nivel global contaminan sesiones no-FARO
**Contexto:** Al implementar T-147, `faro-setup.ps1` crea junctions `~/.claude/agents/` y `~/.claude/skills/` apuntando al repo. Esto hace los agentes FARO disponibles en cualquier sesión de Claude Code del operador, incluyendo proyectos que no tienen nada que ver con FARO.
**Lección:** El nivel de usuario (`~/.claude/agents/`) es adecuado para agentes verdaderamente globales (utilidades genéricas). Los agentes de un harness específico son contexto innecesario fuera de ese harness — consumen tokens y pueden generar confusión. El nivel de proyecto (`.claude/agents/` dentro del proyecto cliente) es el nivel correcto para agentes de dominio. El bug que motivaba poner agents a nivel global (T-147) ya fue resuelto por T-146 — el deploy normal ya no borra archivos a través de junctions.
**Cómo aplicar:** Antes de decidir dónde viven los agents en producción, evaluar: ¿son útiles fuera del harness? Si no, nivel de proyecto vía `deploy-harness.ps1 -Dev`. Solo subir a nivel de usuario si son herramientas transversales. Ver DEC-048 para el estado actual de la decisión.

---

## LEC-051 — El governor debe crear todas las carpetas del runtime, no depender de faro-init (sesión 26)
**Contexto:** Durante la revisión de Test_003A, se detectó que E10-A.2 solo creaba 6 carpetas de primer nivel. Las subcarpetas `010_discovery/deliverables/` y `010_discovery/support/` no se creaban porque estaban en `faro-init`. Si el operador saltaba `faro-init` o el Paso 1 no corría completo, el interviewer y el configurator fallaban al intentar escribir en esas rutas.
**Lección:** El governor no puede asumir que `faro-init` se ejecutó previamente y correctamente. E10-A es el ritual de inicio — debe crear todo lo que el harness necesita para funcionar, incluyendo subcarpetas de trabajo. La redundancia entre `faro-init` y E10-A.2 es intencional y deseable (idempotente con `-Force`).
**Cómo aplicar:** Cada vez que se agregue una nueva carpeta requerida por algún worker, agregarla tanto en `faro-init.md` (Paso 1) como en E10-A.2 del governor.

---

## LEC-052 — Las guías de preguntas del interviewer deben vivir en el proyecto, no solo en el repo (sesión 26)
**Contexto:** `faro-init` solo copiaba 2 archivos a `010_discovery/templates/`. Los `preguntas_rol_*.md` existían en el repo (`Harness_Forecaster/templates/010_discovery/`) pero no se copiaban al proyecto. El interviewer los buscaba en el proyecto y al no encontrarlos improvisaba preguntas desde su conocimiento general, perdiendo la estructura definida por los roles FARO.
**Lección:** Todo archivo que un agente lee con `Read` en tiempo de ejecución debe estar en el proyecto, no solo en el repo fuente. El repo es la fuente de verdad para editar; el proyecto es el entorno de ejecución. Un agente no puede leer archivos de `FARO_HOME` directamente a menos que el código lo instruya explícitamente.
**Cómo aplicar:** Al agregar un nuevo archivo de referencia que un agente debe leer durante la ejecución, agregarlo también al bloque de copia de `faro-init.md`. Si el archivo es sensible al cliente (no debe compartirse entre proyectos), ponerlo solo en `faro-init`. Si es compartido entre todos los proyectos, puede ir en la lista de templates a copiar.

---

## LEC-053 — Las respuestas del operador deben darse en la terminal donde corre el agente (sesión 26)
**Contexto:** Durante el apoyo a la prueba, el operador respondió preguntas de entrevista en la terminal de soporte (`Harness_Forecaster`) en lugar de en la terminal de prueba (`Test_003B_Limpieza`). Las respuestas no llegaron al `discovery-interviewer` ni se guardaron en `session_notes.json`.
**Lección:** La terminal de soporte y la terminal de prueba son sesiones de Claude Code independientes. Lo que se escribe en una no es visible para la otra. El operador debe responder las preguntas del interviewer en la misma terminal donde está corriendo el harness. La terminal de soporte sirve para diagnóstico, fixes y contexto, pero no para conducir la entrevista.
**Cómo aplicar:** Al iniciar una prueba, dejar claro al operador que la terminal de soporte es para preguntas técnicas sobre el harness, no para responder las preguntas del interviewer. Si el operador no entiende qué pregunta hacer en cada terminal, explicar la diferencia antes de arrancar.

---

## LEC-054 — "PARAR COMPLETAMENTE — no escribir ningún texto adicional" paraliza al agente (sesión 27)
**Contexto:** T-157 reforzó la instrucción de guardado del `discovery-interviewer` con el texto "PARAR COMPLETAMENTE — no escribir ningún texto adicional, no presentar el siguiente bloque". El objetivo era impedir que el agente avanzara sin guardar. El efecto real fue el opuesto: el agente interpretó "no escribir ningún texto adicional" como "no producir ninguna salida", lo que bloqueó también las llamadas a herramientas (`Write`). El interviewer pasaba directamente al siguiente bloque sin guardar nada — ni `session_notes.json` ni `stakeholder_map.json`.
**Lección:** "No escribir texto" y "no llamar herramientas" son la misma instrucción para un agente. Si se quiere impedir que el agente responda con texto antes de ejecutar una acción, la instrucción correcta es describir qué debe hacer primero — no prohibir la salida de texto. Lenguaje prohibitivo muy fuerte ("PARAR COMPLETAMENTE", "BLOQUEANTE", "inviolable") no refuerza el comportamiento deseado; puede inhibir toda acción.
**Cómo aplicar:** Para forzar una secuencia específica en un agente, describir la secuencia positivamente: "Tu primera acción es X, luego Y, luego Z." Evitar instrucciones del tipo "no hagas nada hasta que...". La versión que funcionaba en Test_002B usaba "PARAR — no presentar el siguiente bloque todavía" sin prohibir texto ni tool calls — esa formulación es la correcta.

---

## LEC-055 — El lenguaje condicional suave ("intentar leer", "si aplica") vuelve opcional un paso obligatorio (sesión 28)
**Contexto:** En Test_003D y Test_003E el `discovery-interviewer` conducía las entrevistas pero NO creaba `stakeholder_map.json` ni `session_notes.json` salvo que el operador se lo pidiera explícitamente. La causa estaba en la redacción de los pasos de inicio del agente: el Paso 3 decía "**Intentar** leer `stakeholder_map.json`. Si no existe → construir el mapa" y el Paso 5 decía "Crear o cargar notas de sesión (**si aplica**)". Para un LLM, "intentar leer" y "si aplica" comunican que el paso es opcional — si el archivo no existe, el agente lo interpreta como "no hay nada que hacer aquí" y avanza sin escribir. El mismo patrón suave aparecía en los pasos de guardado por bloque.
**Lección:** Los agentes LLM tratan el lenguaje condicional suave ("intentar", "si aplica", "si existe", "opcionalmente") como permiso para saltarse el paso. Un paso que DEBE producir un archivo en disco debe redactarse en imperativo con una consecuencia clara: "Leer X. Si no existe, crearlo y escribirlo en disco **antes de continuar al siguiente paso**. Este paso es obligatorio — no avanzar sin que el archivo exista." La diferencia entre "intentar leer" y "garantizar que exista" cambia el comportamiento real.
**Cómo aplicar:** Al redactar pasos que producen artefactos en cualquier agente, usar verbos imperativos ("garantizar que exista", "escribir", "crear") y agregar un gate explícito ("no avanzar hasta que el archivo exista en disco"). Nunca usar "intentar", "si aplica" ni "opcionalmente" para un paso cuyo output es obligatorio.

---

## LEC-056 — Separar el turno de setup del turno de entrevista fuerza la creación de archivos (sesión 28)
**Contexto:** Reforzar el lenguaje de guardado no bastaba: la causa raíz era que el agente percibía su tarea como "entrevistar" y trataba la escritura de archivos como burocracia secundaria que podía diferir. Corría hacia la primera pregunta y, como ya tenía los stakeholders del brief en su contexto de trabajo, "razonaba" que escribir el mapa era redundante. La solución de fondo fue reestructurar la sección "Al iniciar" en un **turno de setup explícito**: el primer turno del agente produce `stakeholder_map.json` + `session_notes.json` + una confirmación visible al operador, y NO contiene ninguna pregunta de entrevista. La entrevista arranca recién en el turno siguiente, tras un GATE DE ARRANQUE que prohíbe preguntar si ambos archivos no existen en disco.
**Lección:** Cuando un agente se salta un paso de persistencia, el problema rara vez es la fuerza del lenguaje — es que el agente corre hacia lo que percibe como su tarea principal. La corrección efectiva es separar las fases en turnos distintos y hacer que el artefacto sea la única salida del primer turno, no un efecto secundario silencioso. Así el agente "quiere" producir el archivo porque es su entregable visible, no un trámite.
**Cómo aplicar:** En workers interactivos que deben inicializar archivos antes de operar, estructurar un turno de setup dedicado: primera salida = los archivos + confirmación, sin nada de la tarea principal. Agregar un gate que bloquee la tarea principal hasta que los archivos existan. Validado en Test_004A: ambos archivos se crearon sin intervención del operador. Contrasta con LEC-054 (reforzar lenguaje prohibitivo no funciona) — lo que funciona es reordenar el flujo, no endurecer prohibiciones.

---

## LEC-057 — Un agente no debe cargar una skill que describe el artefacto de otro agente (sesión 28)
**Contexto:** El `discovery-interviewer` tenía en su frontmatter `skills: [discovery-session-schema]`. Pero esa skill define el schema de `session_data.json`, cuyo **escritor único es el synthesizer** (la propia skill lo dice: "Escritor único: discovery-synthesizer"). El interviewer la usaba solo como referencia de qué campos son bloqueantes, pero su primer paso de inicio era cargar una skill sobre un archivo que él no produce — lo que orientaba su atención hacia campos ajenos en vez de hacia sus propios artefactos (`session_notes.json`, `stakeholder_map.json`).
**Lección:** Las skills cargadas por un agente deben corresponder a los artefactos que ese agente produce o consume directamente. Cargar la skill del artefacto de otro agente desenfoca al modelo y crea acoplamiento innecesario. El conocimiento que el interviewer sí necesitaba (qué campos son bloqueantes) ya vive en sus propias secciones de cierre y en las guías de preguntas por rol — no requería la skill del synthesizer.
**Cómo aplicar:** Al definir el frontmatter `skills:` de cualquier agente, verificar que cada skill describe un artefacto que ese agente lee o escribe. Si la skill es de un artefacto downstream que produce otro agente, quitarla y mover el conocimiento mínimo necesario (ej. lista de campos bloqueantes) a las instrucciones propias del agente.

---

## LEC-058 — execution-state.json no registra la completitud del interviewer — el tramo interactivo queda sin checkpoint (sesión 28)
**Contexto:** En Test_004A el `discovery-interviewer` completó 4 sesiones y persistió `session_notes.json` + `stakeholder_map.json` correctamente, pero `execution-state.json` quedó congelado en su estado pre-entrevistas (`last_checkpoint: null`, `status: IN_PROGRESS`, `last_updated` anterior al arranque del interviewer). La única evidencia de que las entrevistas ocurrieron estaba en la nota de suspensión de `harness-state.json`. Causa: el `orchestration_plan` no define ningún checkpoint para el interviewer (CP-01 es del synthesizer), así que el tramo interactivo puede completar sin dejar rastro en el registro de ejecución. Además, el campo `mode` de `harness-state.json` quedó en `"INICIO"` aunque el harness ya estaba en EXECUTE (la suspensión lo registró como `governor_mode: "EXECUTE"`).
**Lección:** El registro de estado (`execution-state.json`) debe reflejar el progreso real del pipeline, incluyendo los tramos interactivos. Si un worker puede completar sin que ningún checkpoint lo registre, el estado de ejecución miente sobre dónde está el harness y una reanudación desde `execution-state.json` no sabría que las entrevistas ya se hicieron. El interviewer hizo su trabajo; quien no cerró el ciclo de estado fue la capa de coordinación (governor/orchestrator). Los campos de estado de alto nivel (como `mode`) deben actualizarse en cada transición, no solo al inicio.
**Cómo aplicar:** Registrar un checkpoint o marca de progreso al completar el interviewer (aunque no sea un CP formal del pipeline) para que `execution-state.json` refleje que el tramo interactivo terminó. Mantener `harness-state.json > mode` sincronizado con el modo real del governor en cada transición. Verificar en cada prueba que `execution-state.json` no quede congelado tras un worker interactivo.

---

## LEC-059 — El governor no debe lanzar workers como subproceso `claude --print` anidado en background (sesión 29)
**Contexto:** Validados los fixes T-162/T-163 en la reanudación de Test_004A, el governor avanzó al `discovery-synthesizer`. Para invocarlo abrió una **sub-instancia de Claude en segundo plano** vía Bash: `<prompt> | claude --agent discovery-synthesizer --print --dangerously-skip-permissions 2>&1`, y luego se quedó haciendo polling del archivo de salida. Resultado tras ~19 minutos: **cero artefactos** (no se creó `session_data.json`, `synthesis_report.json` ni `open_questions.json` en ninguna parte del proyecto), los **4 archivos de salida CLI en 0 bytes**, y un proceso `claude` colgado consumiendo CPU (~188s) sin completar. El agente synthesizer existía (12 KB) y los flags eran válidos — la falla no era de sintaxis ni de datos, sino del **mecanismo de spawn**. Causa raíz: el modo `--print` solo emite la salida al terminar por completo; si la sub-instancia se cuelga a mitad de camino, el archivo de salida queda vacío, los artefactos nunca se escriben y el governor espera indefinidamente un resultado que no llega. El patrón "spawnear sub-Claude en background + polling de archivo" no es confiable para encadenar workers.
**Lección:** Encadenar workers abriendo una sub-instancia de Claude en background y esperando su archivo de salida es frágil: sin streaming (`--print` no muestra avances), sin garantía de que el proceso complete, y sin forma de que el governor distinga "trabajando" de "colgado". El governor tiene la herramienta `Agent` disponible — la vía robusta es invocar al worker **como subagente dentro de la misma sesión** (Agent/Task tool), que corre con contexto propio y persiste sus archivos de forma confiable, devolviendo el control al governor al terminar. Cuidado adicional al diagnosticar: una de las sub-instancias `claude` colgadas puede ser indistinguible por PID de la propia sesión de la terminal de prueba — no matar procesos a ciegas.
**Cómo aplicar:** Cambiar en `discovery-governor.md` la invocación de workers (synthesizer, analyst, configurator) de subproceso `claude --print` en background a invocación vía la herramienta `Agent` en la misma sesión. Si por diseño se requiere aislamiento de proceso, no usar `--print` en background sin un timeout y una verificación explícita de que los artefactos esperados existen en disco antes de avanzar; tratar "archivo de salida vacío" + "artefactos ausentes" como fallo del worker, no como "aún trabajando". Ver T-166.

**⚠️ CORRECCIÓN (sesión 31) — el "Cómo aplicar" de arriba era parcialmente erróneo:** invocar al worker vía la herramienta `Agent` **desde dentro del governor** NO funciona. El governor es un subagente, y la doc oficial de Claude Code confirma que **un subagente no puede spawnear otros subagentes**. La solución correcta (implementada en T-166a/b) es el **modelo conductor**: el governor pasa a despachador de un solo paso que retorna `WORKER_REQUIRED`/`ORCHESTRATOR_REQUIRED` con un bloque `dispatch`, y la **sesión principal (el conductor)** es la única que spawnea — vía la herramienta `Agent` — siguiendo el bucle de `templates/workflows/conductor_loop.md`. El interviewer ya seguía este patrón (corre inline). Ver `progress/refactor_conductor_T166.md`, T-166a/b, y **DEC-051** (registrada en T-166d, sesión 32). **VALIDADO end-to-end en sesión 32** (Test_004A reanudado): el conductor despachó synthesizer→analyst→configurator→evaluator sin colgarse; el synthesizer completó en ~3 min (antes: 19 min colgado). Ver LEC-060.

---

## LEC-060 — El modelo conductor funciona, pero validar e2e destapa regresiones que el flujo anterior enmascaraba (sesión 32)
**Contexto:** Se reanudó Test_004A con el refactor conductor (T-166a–d sincronizados a la carpeta de prueba). El harness corrió **end-to-end por primera vez con el nuevo modelo**: synthesizer (CP-01) → analyst (CP-02) → configurator DRAFT (CP-03, gate operador) → COMMIT (CP-05) → evaluator → CLOSE. Veredicto **APPROVED 0.93, 1 sola iteración**. El objetivo central de T-166 quedó probado en corrida real: **cero cuelgues, cero invocaciones `claude --print`**, despacho limpio vía la herramienta `Agent` desde el conductor. PERO la auditoría detectó un **hallazgo major real**: dos `tenant_id` en circulación — `prolimex-mx` (en `harness-state.json` y `analysis_report.json`) vs `prolimex-s-a-de-c-v-4528` (en `client_profile.json`, BD, storage y evento). Causa raíz confirmada en código: (1) el governor **ya no genera el `tenant_id` en E10-A** (DEC-047/T-136 lo exigen; el rewrite T-166a perdió ese paso) — por eso el analyst se bloqueó por tenant_id ausente y el governor lo generó reactivamente como `prolimex-mx` (formato ad-hoc, ni siquiera la convención DEC-047); (2) el configurator **genera su propio tenant_id** en el Paso 3 ("Generar tenant_id") en vez de leerlo de `harness-state.json` — violación vieja de DEC-047 que T-136 supuestamente corrigió pero que nunca llegó a ese archivo (o se perdió en la restauración T-149).
**Lección:** Pasar una prueba con APPROVED no significa que el sistema esté correcto — significa que la rúbrica no vetó. Un bug de consistencia (dos tenant_id) puede convivir con un score 0.93 si ninguna dimensión tiene veto sobre él. Más importante: **un refactor grande (T-166a reescribió el governor entero) puede perder pasos silenciosamente** (la generación de tenant_id en E10-A) sin que ninguna verificación estática lo note, porque el paso perdido solo se manifiesta en runtime. Y los bugs "marcados como implementados" (T-136 en el configurator) pueden no estar realmente en el archivo — mismo patrón que LEC-046. Validar e2e es lo único que destapa estas dos clases de fallo.
**Cómo aplicar:** (1) Tras cualquier rewrite mayor de un agente, hacer un diff de responsabilidades contra las decisiones vigentes (aquí: ¿el governor sigue generando tenant_id en E10-A según DEC-047?) — no confiar solo en que "compila" o pasa verificación estática. (2) La fuente única de `tenant_id` es el governor en E10-A (DEC-047); cualquier worker que lo "genere" es un bug — buscar `Generar tenant_id` en todos los agentes. (3) Restaurar T-167 (governor genera en E10-A) y T-168 (configurator lee, no genera). Ver T-167, T-168, BUG-1 del informe de sesión 32.
**RESUELTO (sesión 33):** T-167 y T-168 implementadas. El governor regenera y persiste el tenant_id en un nuevo Paso C de E10-A (idempotente), y el configurator ahora lo lee de harness-state.json en vez de generarlo. **Pendiente: validar en corrida e2e** que un único tenant_id fluye por todos los artefactos (es uno de los objetivos de la prueba e2e que se va a definir).

---

## LEC-061 — Un governor sin estado (modelo conductor) registra eventos duplicados al re-derivar su posición en cada re-entrada (sesión 32)
**Contexto:** En la corrida e2e de Test_004A, `claude-progress.txt` quedó con **líneas duplicadas y timestamps vacíos**: `[EXECUTE] … despachando configurator DRAFT` 2× (una sin timestamp), `[CP-03] … DRAFT completó` 2× (una sin timestamp). Se sospechó del reinicio por límite de tokens de 5h, pero los timestamps lo descartan: el reinicio (`[CONTINUACIÓN] 19:35:01`, vía `faro-restart`/`faro-continue`) ocurrió en el hueco 14:01→19:35, y los duplicados aparecieron después, a las 19:43–19:47, dentro de una corrida continua. Causa real: en el modelo conductor el governor es **sin estado** — el conductor lo re-spawnea en `[MODO: EXECUTE]` en cada vuelta del bucle, y el governor re-deriva su posición leyendo el disco y **escribe la línea de progreso cada vez, sin comprobar si ya la escribió**. Las re-entradas a la misma posición lógica duplican el evento. Además hay una ruta de código que emite la línea con el placeholder `<timestamp>` sin sustituir por la hora real.
**Lección:** Hacer el governor stateless (re-derivar del disco en cada invocación) ganó robustez de reanudación pero perdió la "memoria" de qué ya se logueó. Un log append-only + re-entradas idempotentes en la lógica = eventos duplicados en la bitácora. No es un bug del reinicio ni del operador; es un efecto colateral del diseño conductor.
**Cómo aplicar:** En `discovery-governor.md`, escribir el evento de progreso solo en la **transición real** (p. ej. cuando el checkpoint pasa de ausente a presente en el disco), no incondicionalmente en cada re-derivación. Alternativamente, antes de hacer append, verificar si la última línea de `claude-progress.txt` ya es ese mismo evento. Y corregir la ruta que emite `[EXECUTE]  —` sin timestamp para que siempre sustituya la hora UTC real. Ver T-169.
**RESUELTO (sesión 33):** T-169 implementada con la opción "verificar la última línea antes del append": se añadieron dos reglas globales a la sección "Escritura en claude-progress.txt" del governor — (1) sustitución obligatoria de `<timestamp>` por `$(Get-Date -AsUTC -Format ...)`, y (2) guard anti-duplicado que lee la última línea con `Get-Content -Tail 1` y solo escribe si la etiqueta del evento no está ya presente. Se eligió una regla central (no editar las ~15 instrucciones de log dispersas) por mantenibilidad.
**VALIDADO PARCIALMENTE (sesión 34, Test_005_Flexempaque):** el guard anti-duplicado **SÍ funcionó** — la bitácora salió sin líneas duplicadas pese a una reanudación intermedia. PERO la corrida destapó dos defectos residuales: (a) **timestamp vacío** en `[SYNTHESIZER_REQUIRED]  — ` — la regla de timestamp no alcanzó las líneas de despacho `*_REQUIRED`; (b) **mojibake** en `[CP-01]` y `[CP-03 APROBADO]` (`completÃ³`, `â€"`) por mezcla de codificación UTF-8/Latin-1 y BOM. → derivado a **T-174**.

---

## LEC-062 — Al corregir un campo transversal hay que auditar TODOS sus escritores, no solo el que falló (sesión 34)
**Contexto:** BUG-1 (divergencia de `tenant_id`) se atacó en sesión 33 con T-167 (governor genera y persiste el tenant_id en E10-A) y T-168 (configurator lo lee en vez de generarlo); el analyst ya lo leía bien. En la corrida e2e de Test_005_Flexempaque el tenant_id salió **consistente en los 11 artefactos canónicos** (deliverables, db_records, evento, storage, harness-state, analysis_report, session_data, verdict, metrics) — pero **2 artefactos del synthesizer** (`synthesis_report.json` y `open_questions.json`) escribieron `"tenant_id": "Flexempaque del Bajío S.A. de C.V."` (la **razón social**) en vez del slug. El `discovery-synthesizer` nunca fue parchado: quedó fuera del alcance de BUG-1 porque en Test_004A la divergencia se manifestó en analyst/configurator, no en él. **Agravante:** el `discovery-evaluator` dio D2=1.0 sin detectarlo, porque la rúbrica no valida consistencia de tenant_id en los archivos de `support/`.
**Lección:** Cuando un campo es **transversal** (lo escriben varios agentes), corregir solo los escritores que fallaron en la prueba anterior deja escritores "durmientes" con el mismo bug latente. La cobertura del fix debe ser por **inventario de escritores del campo**, no por síntoma observado. Y el evaluador solo caza lo que su rúbrica mira: si la rúbrica no inspecciona los artefactos intermedios, un APPROVED 1.0 puede convivir con una divergencia real.
**Cómo aplicar:** Al corregir un campo compartido, listar TODOS los agentes que lo escriben y aplicar el mismo patrón ("leer de la fuente única, nunca generar") a cada uno. Para tenant_id: governor (genera) → analyst, configurator **y synthesizer** (leen). Ampliar la rúbrica (D2/D4) para validar que TODOS los artefactos, incluidos los de `support/`, usan el tenant_id del harness-state. Ver T-173.

---

## LEC-063 — En Windows la allowlist de permisos debe cubrir la herramienta PowerShell, no solo Bash (sesión 34)
**Contexto:** En Test_005_Flexempaque el operador recibió muchos prompts de permiso "¿Permitir este comando?" durante la corrida, que percibió (con razón) como interrupciones que no son puntos de control. El análisis del `settings.json` mostró que la allowlist heredada tenía casi todas sus entradas en `Bash(...)` (`Bash(New-Item *)`, `Bash(Add-Content *)`, etc.), pero el harness en Windows ejecuta esos comandos vía la herramienta **PowerShell**, de la que casi no había entradas allowlisteadas. Cada `New-Item`/`Get-Content -Tail`/`Add-Content`/`Test-Path`/`git` corrido como PowerShell caía fuera de la lista y pedía permiso.
**Lección:** La allowlist de Claude Code es **por herramienta**: `Bash(patrón)` y `PowerShell(patrón)` son namespaces distintos. Permitir un comando en Bash no lo permite en PowerShell. En un proyecto Windows donde los agentes corren PowerShell, la allowlist debe expresarse en `PowerShell(...)` o los prompts se disparan en cascada — y se confunden con fricción del flujo cuando en realidad es configuración de permisos. Esto es independiente del diseño Human-in-the-Loop: los gates reales (Sprint Contract, CP-03/04, escalamiento, handoff) son otra cosa y no se tocan.
**Cómo aplicar:** Mantener el template de permisos (`templates/client-project-settings.json`) con patrones `PowerShell(...)` que cubran la plomería real del harness. Al portar a otra plataforma, revisar qué herramienta ejecuta realmente los comandos. Decisión registrada: DEC-053 (Opción A, patrones específicos). Ver T-176.

---

## LEC-064 — La allowlist no silencia las heurísticas de seguridad de comandos; en Windows el bypass por proyecto es la vía pragmática (sesión 36)
**Contexto:** En Test_006 el operador suspendió por la cantidad de prompts de permiso, varios marcados con avisos de seguridad ("Command contains script block that may execute arbitrary code", "Command too long for parsing", "Newline followed by # … can hide arguments"). El template ya tenía allowlist `Bash(...)`/`PowerShell(...)` (DEC-053), pero los prompts seguían. Dos causas: (1) **mismatch de forma** — el harness emite `cd "..." && powershell -NoProfile -Command "<heredoc multilínea>"`; la regla `Bash(powershell.exe *)` no matchea un comando que empieza con `cd` y llama `powershell` (sin `.exe`); el matcher es por prefijo del comando completo. (2) **las heurísticas de seguridad son barreras duras que ignoran la allowlist** — un comando marcado como "script block / código arbitrario / args ocultos por `#`" pide confirmación aunque exista una regla `allow` que lo cubra. Ningún `allow` las apaga.
**Lección:** En Claude Code, `permissions.allow` y las heurísticas de seguridad de comandos son capas distintas: la allowlist evita el prompt "rutinario", pero los flags de peligrosidad lo fuerzan igual. Para llegar a **cero prompts** dentro de una carpeta controlada (un proyecto FARO que el harness opera de punta a punta) la palanca correcta es `permissions.defaultMode: "bypassPermissions"` a nivel de proyecto, NO seguir ampliando patrones de allowlist. Esto es independiente de los gates Human-in-the-Loop (Sprint Contract, CP-03/04, escalamiento, handoff), que viven en la lógica de los agentes y no se ven afectados por el modo de permisos. El costo del bypass es perder la red de seguridad de último recurso dentro de esa carpeta — aceptable cuando el harness controla todo lo que se ejecuta ahí.
**Cómo aplicar:** Para proyectos cliente FARO usar `bypassPermissions` en el `settings.json` que instala `faro-setup` (DEC-054). La **causa raíz** sigue siendo el estilo de comandos del harness (heredocs de PowerShell incrustados en Bash con `#` y multilínea): la mejora de fondo es que los agentes usen las herramientas dedicadas `Write`/`Edit` para archivos y la herramienta `PowerShell` nativa para comandos, evitando `cd ... && powershell -Command "<heredoc>"`. Mientras eso no se haga, no confiar en la allowlist para esos comandos — solo el bypass los cubre. Ver DEC-053, DEC-054, LEC-063.

---

## LEC-065 — Una prueba con APPROVED no audita la calibración ni la riqueza semántica de los artefactos (sesión 36)
**Contexto:** En Test_006 (suspendida en CP-02, antes del evaluador) la auditoría manual de soporte destapó dos defectos que ninguna corrida previa con veredicto APPROVED había señalado, porque la rúbrica del evaluador no los mira: (1) **ITO mal calibrado** — la dimensión *pedidos* es casi inerte (`PEDIDOS_MAX=2000` hace que 135 pedidos/mes aporten 1.69 de 42.69; la categoría la deciden de facto SKUs y clientes), más una **ambigüedad de definición** (pedidos vs líneas de pedido, ~135 vs ~850, que cambia el ITO de 42.69 a ~51.6); (2) **pérdida de señal asimétrica** — la tolerancia de error por segmento (mínimo en productos estrella en pico e insumos de lead time largo) se captura en `session_notes`/`synthesis_report` pero se comprime al derivar `session_data.json` a dos etiquetas genéricas, perdiendo el dato más accionable para 035/045.
**Lección:** El veredicto del evaluador valida lo que su rúbrica inspecciona (presencia de campos, consistencia de tenant_id, rutas, escalamientos), no la *corrección sustantiva* de los números (¿el ITO discrimina de verdad?) ni la *preservación de matices* (¿llegó al config la asimetría del error?). Un APPROVED puede convivir con un índice mal calibrado y con riqueza semántica perdida. La revisión humana de soporte sigue siendo necesaria para esa clase de defecto, y los hallazgos deben registrarse como ajustes aunque la prueba "pase".
**Cómo aplicar:** (1) Calibrar `PEDIDOS_MAX`/`SKUS_MAX`/`CLIENTES_MAX` con datos piloto (T-030) y fijar la unidad de "pedidos" en el schema y en la pregunta del interviewer (T-178). (2) Añadir un campo estructurado de prioridad de precisión / segmentos críticos que preserve la tolerancia asimétrica desde `session_data` hasta `onboarding_config` (T-179). (3) Considerar ampliar la rúbrica para que verifique que `criterios_exito` y la prioridad de precisión no se reduzcan a etiquetas genéricas (extensión de LEC-044 aguas arriba).

---

## LEC-066 — Los timestamps que un agente redacta dentro del contenido no son confiables como reloj de ejecución (sesión 36)
**Contexto:** En Test_006, `session_notes.json` registra la entrevista de Renata con `fecha_sesion`/`fecha_ultima_actualizacion` 19:25–19:40, pero el `discovery-synthesizer` ya había corrido a las 19:04:57 (con `interviewer_completed_at = 19:03:41` en `execution-state.json`). Es decir, el contenido afirma que una entrevista ocurrió *después* de que la síntesis que la consume ya se había producido. Los sellos de tiempo dentro de `session_notes.json` son narrados por el agente, no tomados del reloj real en el momento del Write.
**Lección:** Hay dos clases de timestamp en el harness: los **operativos** (escritos por la capa de estado con `Get-Date -AsUTC` real: `claude-progress.txt`, `execution-state.json`, `harness-state.json`) y los **de contenido** (que un worker redacta dentro de un artefacto de dominio). Los segundos son ilustrativos y pueden contradecir el orden real del pipeline. No usarlos para ordenar, conciliar ni auditar por tiempo — la fuente de verdad temporal es la capa operativa.
**Cómo aplicar:** Si un campo de timestamp dentro de un artefacto debe ser fiable, hacer que el agente lo selle con `Get-Date -AsUTC` real en el momento del Write (no un valor inventado). Si solo es ilustrativo, documentarlo como tal en el schema. Verificación de soporte: nunca asumir que `fecha_*` dentro de `session_notes.json`/`synthesis_report.json` refleja el reloj real de ejecución. Ver T-180.

---

## LEC-006 — La eliminación de datos no puede ejecutarse con exportaciones pendientes
**Contexto:** Al definir la política de retención de datos al cancelar surgió el caso borde de solicitudes de exportación recibidas en el último mes permitido.
**Lección:** El proceso de eliminación definitiva debe verificar si hay exportaciones pendientes de confirmación antes de ejecutarse. Si las hay, el proceso se bloquea hasta recibir confirmación de entrega.
**Cómo aplicar:** Implementar el job de eliminación con una verificación previa del estado de exportaciones del cliente. Solo eliminar si el estado es "sin exportaciones pendientes" o "exportación confirmada entregada".
