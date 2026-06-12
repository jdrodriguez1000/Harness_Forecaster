# Estado del Proyecto — FARO (Harness Forecaster)

## Última actualización
2026-06-12 (sesión 37 — **Test_006 COMPLETADA e2e: veredicto APPROVED 1.0, primer ciclo 010 completo con T-175 validado y gates/evaluador ejercitados.** La corrida (terminal de prueba `Test_006`) se reanudó desde la suspensión de CP-02 y llegó al **cierre limpio**: configurator DRAFT→CP-03 (operador aprobó 23:06:56)→COMMIT→CP-05→evaluator→CLOSE. `status: PHASE_COMPLETE`, `governor_mode: CLOSE`, **score 1.0, 7/7 dimensiones, sin vetos, sin hallazgos**. Esta terminal `Harness_Forecaster` operó como **soporte** (LEC-053): auditó los artefactos en disco y aplicó el fix de T-181. **Lo bueno validado en runtime:** **T-175 ✅** (`pending_email.json > destinatario_rol: "tecnico"` = Iván Cervantes, el extractor del ERP, NO Renata/principal — el desempate técnico>principal>usuario funcionó, cierra el mis-routing de Test_005); **gates CP-03/CP-04 + evaluador C ejercitados por primera vez** (operator_approvals/client_approval con timestamp; evaluador con contexto fresco emitió verdict+metrics); **suspensión/reanudación impecable** (3h50 entre 19:11 y 23:01, detectó workers parciales sin re-ejecutar); **T-173 ✅** (tenant_id consistente en los 14 artefactos); storage DEC-044 (6 subcarpetas); T-165 (Patricia Anaya como pagos, distinguida de Renata/principal); categoría **L**→USD350 plan Mensual correcto; encoding limpio. **Lo no tan bueno:** **T-181 AMPLIADO** — los timestamps vacíos no eran solo `[INTERVIEWER_COMPLETE]`; en el tramo de cierre también salieron sin hora `[CP-04]`, `[CONFIGURATOR_COMMIT_REQUIRED]` y `[AUDIT_PENDING]` (la regla enumerada de T-174 solo cubría `*_REQUIRED`); **+ regresión parcial del anti-duplicado (T-169)**: `[AUDIT_PENDING]` se escribió dos veces seguidas (una sin hora, otra con hora). **Fix T-181 aplicado al repo fuente esta sesión** (`discovery-governor.md`): regla de timestamp **universal** (toda línea `[ETIQUETA] <hora> — …`, sin lista de exentas) + **autochequeo** (la `-Value` debe contener literalmente `$(Get-Date -AsUTC` o no se escribe) + anti-duplicado extendido explícitamente a etiquetas improvisadas. **Otros hallazgos confirmados en runtime (sin tocar):** **T-179** (criterios_exito se comprimen a genéricos en session_data→client_profile, se pierde la tolerancia asimétrica), inconsistencia menor Batch+frecuencia "Semanal" en session_data, **T-178** (dimensión pedidos casi inerte), **T-172** (slug correcto otra vez pero sin confirmar si es fix de código o fortuito). Ver sección "Sesión 37" abajo.)

<sub>Entrada previa:</sub> 2026-06-12 (sesión 36 — **Prueba e2e Test_006 (Cosmética Señorío del Pacífico S.A. de C.V.) corrida y SUSPENDIDA limpiamente en CP-02 por el operador.** Esta terminal `Harness_Forecaster` operó SOLO como **soporte/supervisión** (LEC-053): aplicó el ajuste de permisos, simuló las respuestas de los 3 stakeholders y auditó los artefactos en disco — **NO ejecutó el harness; la corrida vive en la terminal de la carpeta `C:\Users\USUARIO\Documents\Triple S\Test_Forecaster\Test_006`.** **Validado en runtime:** **T-173 ✅** (tenant_id slug consistente también en `support/synthesis_report.json`, `open_questions.json`, `session_data.json` — cierra LEC-062 en corrida real); **T-172 ✅ aparente** (slug `cosmetica-senorio-del-pacifico-2229`: acentos transliterados ñ→n/í→i, truncado limpio a 30 chars en frontera de palabra — confirmar si fue fix o fortuito, T-172 figuraba `no iniciada`); capa de estado **DEC-050** (governor_mode EXECUTE, suspensión con context_note/resume_instruction, execution-state consistente, last_checkpoint CP-02); modelo conductor **DEC-051** (interviewer→synthesizer→analyst→CP-02 sin colgarse); calidad de captura/síntesis alta (snowball 3→7+2, 0 contradicciones, open_questions 0 bloqueantes, ITO 42.69→**L** verificado a mano, cold start **CS-ALTA**). **Pendiente/parcial:** **T-174 ⚠️ PARCIAL** (sin mojibake ✅ pero `[INTERVIEWER_COMPLETE]` AÚN con timestamp vacío → **T-181**); **T-175 ⏳ SIN VALIDAR** (suspendió antes del configurator DRAFT); el **evaluador C y los gates CP-03·CP-04 nunca se ejercitaron**. **Ajuste de permisos sesión 36 (DEC-054):** se añadió `"defaultMode": "bypassPermissions"` al template `client-project-settings.json` y al `settings.json` de Test_006 — cero prompts de herramienta dentro del proyecto, los gates Human-in-the-Loop intactos; ataca el síntoma, no la causa raíz (el harness emite `cd ... && powershell -Command "<heredoc>"` que dispara las heurísticas de "código arbitrario" → LEC-064). **Nuevos hallazgos → ajustes futuros:** **T-178** (ITO: dimensión pedidos casi inerte + ambigüedad pedidos vs líneas), **T-179** (tolerancia de error asimétrica se pierde al comprimir `criterios_exito` en session_data), **T-180** (timestamps internos de session_notes no anclados al reloj real de ejecución). Ver sección "Sesión 36" abajo.)

<sub>Entrada previa:</sub> 2026-06-12 (sesión 35 — **Los 3 fixes de código de sesión 34 (T-173, T-174, T-175) APLICADOS al repo fuente.** **T-173** (tenant_id en synthesizer): `discovery-synthesizer.md` ahora lee el tenant_id de `harness-state.json` en un nuevo Paso 3 (patrón del analyst, nunca deriva de stakeholder_map ni usa la razón social) y lo propaga idéntico a los 3 artefactos; notas de origen añadidas a los schemas `discovery-synthesis-schema` y `discovery-open-questions`; rúbrica `discovery-rubric` D4 ampliada con **tabla de consistencia global del tenant_id** que ahora incluye los artefactos de `support/` (divergencia en support → D4=0.5; divergencia en canónico db_records/evento → VETO 0.0). **T-174** (bitácora): `discovery-governor.md` — creación inicial de `claude-progress.txt` con `Set-Content -Encoding utf8` (sin BOM); regla de encoding sin excepción en todo `Add-Content`; regla de timestamp extendida explícitamente a las etiquetas de despacho improvisadas (`[SYNTHESIZER_REQUIRED]`, `[ANALYST_REQUIRED]`, etc.). **T-175** (mis-routing): `discovery-configurator.md` — nuevo campo `contacto_tecnico` en `estado_datos_erp`, Paso 6 con desempate **técnico > principal > usuario** para el destinatario de la guía, + `destinatario_rol` en `pending_email.json`. **Los 3 quedan pendientes de validación en runtime** (T-177 / Test_006). **PRÓXIMO PASO:** sincronizar el repo fuente a carpeta de prueba limpia y correr **Test_006** (empresa con razón social acentuada para re-ejercitar también T-172, cuyo fix es aparte). T-172 (slug acentuado/truncado) sigue pendiente como ajuste menor. Ver sección "Sesión 35" abajo.)

<sub>Entrada previa:</sub> 2026-06-12 (sesión 34 — **PRUEBA e2e Test_005_Flexempaque COMPLETA: veredicto APPROVED score 1.0, end-to-end sin colgarse.** Validó en runtime los fixes clave de sesión 33: **T-165** (responsable_pagos capturado como dato estructurado — Paola Domínguez bien distinguida del firmante Esteban y la patrocinadora Mariana, el objetivo principal de la prueba), **T-167/T-168** (tenant_id consistente en los 11 artefactos canónicos — la divergencia mayor de Test_004A NO se repitió), **T-162/T-163/DEC-050** (suspensión + reanudación limpias) y **T-164** (guardado incremental respaldado, con salvedad metodológica). Pero la corrida **destapó 4 hallazgos nuevos:** **T-173** (el `synthesis_report.json` y `open_questions.json` del synthesizer escriben el tenant_id como razón social, no slug — el synthesizer quedó fuera del alcance de BUG-1, y el evaluador no lo detectó → LEC-062), **T-174** (T-169 PARCIAL: el anti-duplicado funcionó, pero hubo timestamp vacío en `[SYNTHESIZER_REQUIRED]` y mojibake por codificación), **T-175** (la guía de datos se envió a Planeación/Lucía en vez del contacto técnico/Gerardo), y **T-176/DEC-053** (muchos prompts de permiso porque la allowlist cubría `Bash(...)` pero el harness corre PowerShell → LEC-063). **Ajuste aplicado esta sesión: T-176 / Opción A** — `templates/client-project-settings.json` ampliado con patrones `PowerShell(...)` para la plomería del harness; los gates del flujo (Sprint Contract, CP-03/04, escalamiento, handoff) NO se tocaron. **T-172** (slug acentuado/truncado) sigue pendiente como ajuste menor. **PRÓXIMO PASO:** aplicar T-173, T-174, T-175 al repo fuente y luego correr **Test_006** (T-177) en carpeta limpia. Ver sección "Sesión 34" abajo.)

<sub>Entrada previa:</sub> 2026-06-11 (sesión 33 — **BUG-1 (divergencia de `tenant_id`) CERRADO: T-167 + T-168 implementadas.** **T-167** restauró en `discovery-governor.md` la generación del tenant_id perdida por T-166a: nuevo **Paso C** en la Construcción del Sprint Contract (tras validar el brief) que deriva el tenant_id de la razón social con la convención DEC-047 (slug + sufijo `mmss`), lo persiste en `harness-state.json["tenant_id"]` ANTES de despachar workers, idempotente en reanudación; + línea `Tenant` en el template del contrato, `tenant_id: null` en el schema inicial E10-A.3, y nota del campo en `discovery-state-schema`. **T-168** corrigió `discovery-configurator.md`: el Paso 3 ahora **LEE** el tenant_id de `harness-state.json` (patrón idéntico al analyst, `BLOCKED` si vacío) en vez de generarlo con `$slug-$ts`; referencias `<generado>` actualizadas. Fuente única de verdad = governor en E10-A. **BUG-2 también CERRADO: T-169** corrigió el logging del governor a `claude-progress.txt` con dos reglas globales en la sección central de escritura — (1) sustitución obligatoria de `<timestamp>` por hora UTC real (`Get-Date -AsUTC`), prohibido el literal `[EXECUTE]  —` sin hora; (2) guard anti-duplicado que lee la última línea (`Get-Content -Tail 1`) y solo escribe si la etiqueta de evento no está ya presente, eliminando los duplicados por re-derivación stateless del bucle conductor; + puntero a la regla en el encabezado de despachos EXECUTE. **Falta validar en corrida real** (sincronizar agents/skills a carpeta de prueba limpia + correr e2e: confirmar un único `tenant_id` en todo el ciclo y bitácora sin duplicados/timestamps vacíos). **T-165 también CERRADO:** decisión del operador → el interviewer pregunta `responsable_pagos` de forma dirigida en el bloque de negocio. Aplicado en `preguntas_rol_negocio.md` (nueva pregunta obligatoria en Bloque 5: nombre + correo de quien recibe avisos de cobro/pago, distinguida de aprobador/firmante, con manejo MISSING) + reforzado en la nota de campos bloqueantes del `discovery-interviewer.md` Paso 6. No bloqueante restante: T-164 (verificar guardado incremental, requiere corrida). — sesión 32 previa: **Refactor conductor COMPLETO (T-166a–e) y VALIDADO end-to-end.** Implementadas T-166c (descripciones orchestrator/synthesizer), T-166d (flows + state-schema + **DEC-051**), y ejecutada **T-166e**: se reanudó Test_004A con el refactor sincronizado y el harness corrió **end-to-end sin colgarse** → synthesizer (CP-01, ~3 min vs 19 min de cuelgue previo) → analyst (CP-02) → configurator DRAFT (CP-03, gate) → COMMIT (CP-05) → evaluator → CLOSE. **Veredicto APPROVED 0.93, 1 iteración, PHASE_COMPLETE.** T-166/LEC-059 cerrado en corrida real. **PERO la corrida destapó 3 hallazgos nuevos:** **BUG-1 (major)** divergencia de `tenant_id` (`prolimex-mx` en governor/analysis vs `prolimex-s-a-de-c-v-4528` en deliverables/BD/storage/evento) — el rewrite T-166a perdió la generación de tenant_id en E10-A (→ **T-167**) y el configurator genera el suyo en vez de leerlo (→ **T-168**); **BUG-2 (menor)** bitácora con líneas duplicadas y timestamps vacíos por re-derivación stateless del conductor (→ **T-169**); **T-165** (responsable_pagos MISSING) confirmado. **Siguiente: T-167 + T-168** (BUG-1, bloquean el handoff limpio a 015). Ver LEC-060, LEC-061 y el informe de sesión 32 abajo.)

## Sesión 37 — Test_006 COMPLETADA e2e (APPROVED 1.0) + fix de T-181 (timestamps de bitácora)
2026-06-12 (sesión 37)

> **ARQUITECTURA DE DOS TERMINALES (LEC-053).** La corrida Test_006 se ejecutó en la terminal de prueba (`C:\Users\USUARIO\Documents\Triple S\Test_Forecaster\Test_006`). Esta terminal (`Harness_Forecaster`) operó SOLO como **soporte**: auditó los artefactos en disco tras el cierre y aplicó el fix de T-181 al repo fuente.

**Estado de Test_006:** **COMPLETADO** — `harness-state.json > status: PHASE_COMPLETE`, `governor_mode: CLOSE`. La corrida se reanudó desde la suspensión de sesión 36 (CP-02) y recorrió: configurator DRAFT → CP-03 (operador aprobó borradores 23:06:56) → CP-04 (operador aprobó COMMIT 23:08:36) → COMMIT → CP-05 → evaluador → CLOSE. **Veredicto APPROVED, score 1.0, 7/7 dimensiones en 1.0, sin vetos, sin hallazgos.**

### Lo bueno (validado en runtime hasta el cierre)
- **T-175 ✅ VALIDADO (era el gran pendiente de sesión 36).** `pending_email.json` dirige la guía de datos a `destinatario_rol: "tecnico"` → **Iván Cervantes** (extractor del ERP Aspel SAE), no a Renata (contacto principal). El desempate técnico>principal>usuario funcionó en runtime. Cierra el mis-routing de Test_005.
- **Gates CP-03/CP-04 + evaluador C ejercitados por primera vez.** Aprobaciones del operador registradas en `operator_approvals` y `client_approval` con timestamp. El evaluador corrió con contexto fresco y emitió `verdict.json` + `metrics_summary.json` (artifact_status todo EXISTS/true, revisiones: 1).
- **Suspensión/reanudación impecable (DEC-050).** Suspendió 19:11, reanudó 23:01 (3h50 después) detectando workers parciales (interviewer/synthesizer/analyst), CP-01/CP-02 registrados; continuó sin re-ejecutar nada. El contexto de reanudación incluso reportó ITO 42.69→L y CS-ALTA correctos.
- **T-173 ✅ — tenant_id consistente en los 14 artefactos** (`cosmetica-senorio-del-pacifico-2229`): harness-state, analysis, 4 db_records, deliverables, los 3 de `support/`, evento, verdict, metrics, storage. Cero divergencias.
- **Storage DEC-044 perfecto:** 6 subcarpetas bajo `tenants/{slug}/` (005_bronze/007_silver/009_gold, 1010_models, 1020_forecasts, 1030_exports).
- **T-165 ✅** Patricia Anaya capturada como `pagos` en contacts y `responsable_pagos` en client_profile/session_data, distinguida del contacto principal (Renata). Suscripción coherente con reglas de negocio: categoría **L**→USD350, plan Mensual sin descuento, `estado: onboarding_gratuito`, primer cobro 2026-07-12 (mes 2).
- **Encoding limpio** (parte de T-174 que sí sirvió): em-dashes y acentos correctos, sin mojibake.

### Lo no tan bueno (hallazgos)
- **T-181 confirmado y AMPLIADO → FIX APLICADO esta sesión.** Los timestamps vacíos no eran solo `[INTERVIEWER_COMPLETE]`: en el tramo post-CP03/CP04/cierre también salieron sin hora `[CP-04]`, `[CONFIGURATOR_COMMIT_REQUIRED]` y `[AUDIT_PENDING]`. La regla enumerada de T-174 solo cubría `*_REQUIRED`. **Además regresión parcial del anti-duplicado T-169:** `[AUDIT_PENDING]` se escribió dos veces seguidas (una con hora vacía, otra con hora real 23:14:30) porque la guarda no se aplicó a esa etiqueta improvisada. **Fix en `discovery-governor.md`:** (1) regla de timestamp **universal** (toda línea `[ETIQUETA] <hora> — …` sin lista de exentas, con ejemplos de las improvisadas); (2) **autochequeo** — la cadena `-Value` debe contener literalmente `$(Get-Date -AsUTC` o no se escribe (cierra el caso de copiar el `<timestamp>` literal); (3) anti-duplicado extendido explícitamente a etiquetas improvisadas con la nota del caso `[AUDIT_PENDING]`. **Pendiente validar en próxima corrida e2e.**
- **T-179 confirmado en runtime (sin tocar — ajuste futuro de schema).** `session_data.json` y `client_profile.json` comprimen los criterios a `["reducir quiebres","reducir sobre-inventario"]`; la tolerancia de error asimétrica (dónde el MAPE debe ser más bajo) no viaja a downstream.
- **Inconsistencia menor Batch vs frecuencia:** `session_data.json` dice `modo_ingesta: "Batch"` Y `frecuencia_incremental: "Semanal"` (contradictorio). El configurator lo resolvió bien (`client_config.json` con `frecuencia_incremental: null`), pero el dato origen quedó incoherente.
- **T-178 (ITO) sigue latente:** `pedidos_por_mes: 135` con `PEDIDOS_MAX=2000` casi no mueve la aguja; la categoría L la deciden SKUs (250) y clientes (60). No afectó el resultado.
- **T-172 sin confirmar en código:** el slug salió correcto otra vez (`...del-pacifico` truncado limpio a 30 chars), pero sigue sin verificarse si la transliteración está implementada en el Paso C del governor o el corte cayó por suerte al final de "pacifico".

### PRÓXIMO PASO — decidido por el operador: CONSTRUIR EL HARNESS 015 INTAKE
**El harness 010 queda CERRADO.** El siguiente paso es **T-060: crear `brief/015_intake.md`** (Plan de Construcción del 015 con las 7 secciones, patrón de `brief/010_discovery.md`). La persistencia Capa 1 se acopla al diseño del 015 (DEC-055, ver `documents/supabase_persistence_guide.md` D-A) — no se construye antes en aislamiento. Los fixes/ajustes pendientes del 010 quedan diferidos como NO bloqueantes:
- T-181 (timestamps de bitácora) — aplicado, validar en una corrida futura.
- T-172 (transliteración del slug) — confirmar en código cuando se priorice.
- T-178 (calibración ITO/T-030), T-179 (schema prioridad_precision), T-180 (timestamps internos del interviewer) — plegar idealmente al diseñar su harness consumidor (035/045) o en una pasada de limpieza.

**Cierre del día (sesión 37):** repositorio `Harness_Forecaster` enlazado a GitHub (`https://github.com/jdrodriguez1000/Harness_Forecaster.git`), `.gitignore` creado, todo subido.

---

## Sesión 36 — Prueba e2e Test_006 (suspendida en CP-02) + validación parcial de los fixes de sesión 35 + ajuste de permisos (bypassPermissions)
2026-06-12 (sesión 36)

> **ARQUITECTURA DE DOS TERMINALES (leer primero — LEC-053).** La prueba Test_006 se ejecuta en **otra terminal**, abierta en la carpeta `C:\Users\USUARIO\Documents\Triple S\Test_Forecaster\Test_006`. **Esta terminal (`Harness_Forecaster`) es SOLO soporte y supervisión: NO ejecuta el harness, NO conduce la entrevista.** Aquí se aplican fixes al repo fuente, se auditan los artefactos en disco de la carpeta de prueba y se diagnostican bugs. Las respuestas del interviewer se dan en la terminal de prueba, no aquí. Una sesión nueva en esta terminal debe asumir ese rol de soporte por defecto.

**Estado de Test_006:** **SUSPENDIDO por el operador en CP-02** (`harness-state.json > status: SUSPENDED`, `governor_mode: EXECUTE`, `last_checkpoint: CP-02`). Cadena recorrida: governor INICIO → Sprint Contract (APROBADO) → interviewer → synthesizer (CP-01) → analyst (CP-02) → **[suspendido antes de despachar configurator DRAFT, camino a CP-03]**. Reanudación documentada en el propio `harness-state.json > suspension.resume_instruction` (invocar governor `[MODO: EXECUTE]`; el conductor detecta `last_checkpoint=CP-02` y despacha el configurator DRAFT). Cliente: Cosmética Señorío del Pacífico S.A. de C.V. (Morelia, cosméticos B2B), tenant `cosmetica-senorio-del-pacifico-2229`, ITO 42.69 → **L**, cold start **CS-ALTA**.

### Lo bueno (validado en runtime hasta CP-02)
- **T-173 ✅ VALIDADO** — los 3 artefactos de `support/` (`synthesis_report.json`, `open_questions.json`, `session_data.json`) usan el slug `cosmetica-senorio-del-pacifico-2229`, no la razón social. Cierra en corrida real el agravante de LEC-062. El analyst y el harness-state también consistentes.
- **T-172 ✅ aparente** — el slug salió correcto: `Señorío`→`senorio` (ñ→n, í→i), `Pacífico`→`pacifico`, truncado limpio a 30 chars en frontera de palabra (sin guion colgante, sin perder media palabra). Contrasta con el defecto de Test_005 (`baj-o`). **Pero T-172 figuraba `no iniciada`** — confirmar si la transliteración se corrigió en código o fue fortuita en este nombre.
- **Capa de estado (DEC-050)** — `governor_mode: EXECUTE` vivo, `mode: INICIO` intacto (lo lee el orchestrator), `execution-state.json` consistente con `harness-state.json` (mismo `last_checkpoint`, paths de artefactos), `interviewer_completed_at` poblado, suspensión con `context_note` + `resume_instruction` precisas. Reanudable sin ambigüedad.
- **Modelo conductor (DEC-051)** — interviewer→synthesizer→analyst corrieron hasta CP-02 sin colgarse.
- **Calidad de captura y síntesis** — `session_notes.json` rico y fiel (cifras preservadas: ~380-400k MXN de Bellanova, ~60k de jabones caducados, fecha de entrega real ausente en Aspel, bus factor de Renata). Snowball 3→7 stakeholders + 2 administrativos, bien catalogados por origen/estado. Síntesis cruzó perspectivas (reconcilió cifras de Iván con Alejandra, `contradicciones: []` justificado), detectó riesgos reales (autorización de datos = bloqueante operativo, homologación Aspel↔Excel, normalización de sucursales, riesgo de adopción con Lorenzo). `open_questions`: 0 bloqueantes, 2 importantes, 3 registrables → `segunda_ronda: no_requerida` bien fundada. ITO verificado a mano (`0.40·50 + 0.35·60 + 0.25·6.75 = 42.69`, categoría L correcta). Objetivos del brief cumplidos: 3 roles administrativos distinguidos (Alejandra empuja / Humberto firma / Patricia paga), contacto principal (Renata) vs contacto de datos (Iván) separados, y se corrigió la hipótesis del brief (Renata NO es resistencia).

### Lo no tan bueno (hallazgos → ajustes futuros)
- **T-174 ⚠️ PARCIAL** — encoding limpio (sin mojibake; em-dash y acentos correctos), pero `claude-progress.txt` línea 10 quedó `[INTERVIEWER_COMPLETE]  — Entrevistas registradas...` **con timestamp vacío**. El fix de sesión 35 extendió la regla de timestamp a las etiquetas `*_REQUIRED`, pero `[INTERVIEWER_COMPLETE]` es otra etiqueta improvisada que escapó. → **T-181**.
- **T-175 ⏳ SIN VALIDAR** — la corrida suspendió antes del configurator DRAFT, así que el ruteo de la guía de datos al contacto técnico (Iván) no se ejercitó. Sigue pendiente de runtime.
- **Evaluador C y gates CP-03/CP-04 NUNCA se ejercitaron** — `605_eval/` vacío. La mitad "de control" del harness (auditoría independiente + aprobación humana de borradores) no se probó en esta corrida. No es defecto, es terreno no validado.
- **T-178 (ITO — calibración):** la dimensión **pedidos está casi inerte**: con `PEDIDOS_MAX=2000`, los 135 pedidos/mes normalizan a 6.75 y aportan solo **1.69 de los 42.69**. La categoría la deciden de facto SKUs y clientes. Además, **ambigüedad de definición**: ¿"volumen de pedidos" son pedidos (135) o líneas de pedido (~850)? El analyst tomó 135; con 850 el ITO sube a ~51.6 (sigue L aquí, robusto, pero en otro cliente podría cambiar categoría/precio). Alimenta T-030.
- **T-179 (pérdida de señal de tolerancia asimétrica):** el hallazgo más rico para el forecasting — que el error importa sobre todo en **productos estrella en pico** e **insumos de lead time largo** — se guardó bien en `session_notes`/`synthesis_report` pero `session_data.json` lo comprime a `criterios_exito: ["reducir quiebres","reducir sobre-inventario"]`. No hay campo estructurado para "dónde el MAPE debe ser más bajo". Limitación de schema (emparentada con LEC-044).
- **T-180 (timestamps internos no anclados):** el synthesizer corrió a las 19:04:57 (`interviewer_completed_at` 19:03:41), pero `session_notes.json` afirma que la entrevista de Renata fue a las 19:25–19:40 — *después*. Los timestamps que el interviewer escribe dentro del contenido son plausibles pero no están anclados al reloj real del pipeline. Inofensivo hoy, olor de higiene de datos.

### Ajuste de permisos sesión 36 — bypassPermissions por proyecto (DEC-054)
El operador suspendió por la cantidad de prompts de permiso, varios marcados como "script block que puede ejecutar código arbitrario". Diagnóstico: (1) el harness emite `cd "..." && powershell -NoProfile -Command "<heredoc multilínea con #>"` que **no matchea** la allowlist (`Bash(powershell.exe *)` no cubre un comando que empieza con `cd` y llama `powershell` sin `.exe`); (2) las heurísticas de seguridad ("script block…", "Command too long", "newline followed by #") son **barreras duras que ignoran la allowlist** — ningún `allow` las silencia. Decisión del operador: **a nivel de proyecto**, que cada `faro-setup` deje el permiso puesto. Se eligió **Opción A (bypass total por proyecto)** sobre atacar la causa raíz (que el harness use `Write`/`Edit` y la herramienta `PowerShell` nativa en vez de heredocs por Bash). **Aplicado:** `"defaultMode": "bypassPermissions"` añadido a `templates/client-project-settings.json` (todo proyecto FARO nuevo lo hereda) y al `.claude/settings.json` de Test_006 (para reanudar sin prompts). **No toca los gates Human-in-the-Loop** (capa distinta: aprobación de borradores, Sprint Contract, CP-03/04 siguen pidiendo decisión en la conversación). Riesgo aceptado: se pierde la red de seguridad de último recurso dentro de esa carpeta. DEC-054, LEC-064. La causa raíz (estilo de comandos del harness) queda como mejora de fondo pendiente.

### PRÓXIMO PASO
1. **Reanudar Test_006** (en la terminal de prueba) al menos hasta CP-03 para validar T-175 (guía al contacto técnico) y, por primera vez, los gates CP-03/CP-04 y el evaluador C.
2. Aplicar al repo fuente los ajustes T-181 (timestamp `[INTERVIEWER_COMPLETE]`) y, cuando se priorice, T-178/T-179/T-180.
3. Confirmar si T-172 está realmente corregido en código o el slug correcto de Test_006 fue fortuito.

---

## Sesión 35 — Aplicación al repo fuente de los 3 fixes de sesión 34 (T-173, T-174, T-175)
2026-06-12 (sesión 35)

**Contexto:** esta terminal (soporte) aplicó al repo fuente `Harness_Forecaster` los 3 fixes de código derivados de la corrida Test_005_Flexempaque. Ningún cambio toca los gates Human-in-the-Loop ni el bucle conductor.

### T-173 — tenant_id divergente en synthesizer (BUG)
- **`discovery-synthesizer.md`**: nuevo **Paso 3** "Leer tenant_id desde harness-state.json" (lee `600_persistence/harness-state.json`, retorna `BLOCKED` si vacío, **nunca** lo deriva de `stakeholder_map.json` ni usa la razón social — patrón idéntico al analyst Paso 2). Pasos "Determinar ciclo" y "Verificar sesiones" renumerados a 4 y 5. Corregida la derivación de `session_data.json` (antes "Completar tenant_id desde stakeholder_map" → ahora "con el valor leído en el Paso 3"). Reforzada la instrucción en "Escribir los tres artefactos" (mismo slug idéntico en synthesis_report, open_questions y session_data).
- **Schemas**: nota de origen del `tenant_id` añadida a `discovery-synthesis-schema/SKILL.md` (bloque > antes del schema) y a la tabla de campos de `discovery-open-questions/SKILL.md`.
- **Rúbrica** (`discovery-rubric/SKILL.md`, D4): nueva subsección **"Consistencia global del tenant_id"** con tabla de los 8 artefactos a cruzar contra `harness-state.json` (incluye los de `support/`). Anclas D4 actualizadas: los 4 BD completos + tenant_id consistente en TODOS (incluido support) → 1.0; divergencia solo en un artefacto de `support/` (p. ej. razón social) → 0.5; divergencia en artefacto canónico (db_records/evento) → VETO 0.0. Cierra el agravante "el evaluador no lo detectó" (LEC-062).

### T-174 — bitácora con timestamp vacío + mojibake (BUG, T-169 incompleto)
- **`discovery-governor.md`**: (1) la creación inicial de `claude-progress.txt` en E10-A pasa de prosa a comando explícito `Set-Content -Path ... -Encoding utf8` (UTF-8 sin BOM en PS7), con nota de no usar `utf8BOM`; (2) **regla de encoding sin excepción**: todo `Add-Content` lleva `-Encoding utf8`, incluidas líneas `*_REQUIRED` e improvisadas, y nunca leer el archivo con otra codificación (causa del mojibake `completÃ³`/`â€"`); (3) **regla de timestamp extendida** explícitamente a las etiquetas de despacho que el agente genere aunque no figuren como `Registrar [...]` en la tabla (`[SYNTHESIZER_REQUIRED]`, `[ANALYST_REQUIRED]`, `[CONFIGURATOR_REQUIRED]`, `[EVALUATOR_REQUIRED]`) — una etiqueta seguida de ` — ` sin hora es un defecto. La regla anti-duplicado de T-169 (que SÍ funcionó) intacta.
- **Causa raíz identificada**: `[SYNTHESIZER_REQUIRED]` no existe como etiqueta literal en el governor — el agente la improvisó al despachar el worker (la fila 2D no tiene instrucción `Registrar` propia, a diferencia de `INTERVIEWER_REQUIRED`), y al improvisarla omitió `Get-Date` y `-Encoding utf8`. El fix ataca exactamente ese caso.

### T-175 — guía de datos enviada al rol equivocado (mejora)
- **`discovery-configurator.md`**: (1) nuevo campo `contacto_tecnico` (nombre + correo) en la sección `estado_datos_erp` del schema de `onboarding_config.json`, con regla de población que identifica al stakeholder técnico extractor del ERP en `synthesis_report`/`stakeholder_map` (null si ninguno declara rol técnico); (2) Paso 6 reescrito con **regla de desempate técnico > principal > usuario** para seleccionar el destinatario de `data_intake_guide.md`; (3) `pending_email.json` ahora incluye `destinatario_rol` para trazabilidad.

### Ajuste de permisos (complemento de T-176 / DEC-053)
Al revisar el template `templates/client-project-settings.json` se detectó que el lado `Bash(...)` había quedado **incompleto y asimétrico** respecto al lado `PowerShell(...)`: faltaban `Get-Content`, `Set-Content`, `Out-File`, `Get-ChildItem`, `Copy-Item`, `Move-Item`, `Get-Date`, `python`, `py`. Como el harness también ejecuta comandos por la herramienta **Bash** (no solo PowerShell), esos faltantes seguirían disparando prompts "¿Permitir este comando?". El operador confirmó mantener **Opción A** (patrones específicos, no comodín) y **completar Bash para igualar PowerShell**. Añadidos los 9 patrones faltantes + `Bash(pwsh *)`. `settings.local.json` solo lleva `env`+`hooks` (sin permisos), así que el `allow` de `settings.json` es el efectivo. **Test_006 (carpeta nueva) hereda el template completo; Test_005 NO se actualiza** porque su `settings.json` ya existe y `faro-setup` no lo sobreescribe.

### Estado y próximo paso
- Los 3 fixes están en el **repo fuente**; **aún NO sincronizados** a ninguna carpeta de prueba.
- **Pendiente de validación en runtime (T-177 / Test_006):** correr e2e en carpeta limpia con empresa de razón social acentuada (re-ejercita T-172) confirmando: tenant_id consistente también en `support/`, bitácora sin timestamps vacíos en `*_REQUIRED` ni mojibake, guía dirigida al contacto técnico, y menos prompts de permiso (DEC-053).
- **T-172** (transliteración del slug + truncado en frontera de guion) sigue pendiente como ajuste menor aparte — no se tocó en esta sesión.

---

## Sesión 34 — Prueba e2e Test_005_Flexempaque (APPROVED 1.0) + 4 hallazgos nuevos + ajuste de permisos (Opción A)
2026-06-12 (sesión 34)

**Contexto:** corrida e2e de validación en carpeta limpia `Test_Forecaster\Test_005_Flexempaque` (Flexempaque del Bajío S.A. de C.V. — fabricante de empaques flexibles, Querétaro). Esta terminal `Harness_Forecaster` operó como **soporte/supervisión** (LEC-053): preparó el brief, simuló las respuestas de los stakeholders, revisó artefactos en disco y registró hallazgos; la entrevista se condujo en la terminal de prueba. 3 stakeholders entrevistados (Mariana Quintero — negocio+usuario, Gerardo Salinas — técnico, Lucía Bermúdez — usuario) + snowball (Joaquín Rentería — producción, Rebeca Solís — compras, Daniel Esquivel — partner SAP externo).

**Resultado de la corrida:** end-to-end **sin colgarse** → interviewer → (suspensión + reanudación limpia) → synthesizer (CP-01) → analyst (CP-02, ITO 32.60 → categoría **M**, cold start Estándar) → configurator DRAFT (CP-03, gate) → COMMIT (CP-05) → evaluator → CIERRE. **Veredicto APPROVED, score 1.0, 0 major, 3 minor, sin vetos.** Todos los artefactos presentes (deliverables, 4 db_records, evento, storage con 6 subcarpetas DEC-044, pending_email, verdict, metrics, knowledge base).

### Lo bueno (validado en runtime)
- **T-165 — responsable_pagos:** capturado como dato estructurado (`session_notes > notas_negocio > responsable_pagos`), Paola Domínguez con nombre+correo+confirmado, **bien distinguida** del firmante (Esteban) y la patrocinadora (Mariana). Objetivo principal de la prueba: ✅.
- **T-167/T-168 — tenant_id:** consistente en los **11 artefactos canónicos** (deliverables, db_records, evento, storage, harness-state, analysis_report, session_data, verdict, metrics). La divergencia mayor de Test_004A NO se repitió en la cadena crítica.
- **T-162/T-163/DEC-050 — capa de estado:** suspensión con `context_note`/`resume_instruction` precisas; reanudación detectó `interviewer_completed_at` poblado + `session_data.json` ausente → despachó synthesizer. `governor_mode` vivo, `mode` intacto.
- **T-164 — guardado incremental:** respaldado (de `[]` a 3 entradas con `bloques_guardados` granular). **Salvedad:** los timestamps internos son autoría del agente, no mtime real; no se capturó el estado "in fraganti" a mitad de un stakeholder. Mayormente verificado.
- **Snowball:** estados diferenciados correctos — Joaquín citado por 2 fuentes **no duplicado**, Daniel marcado `externo`, Esteban/Paola como `contactos_administrativos`. open_questions: 4 preguntas, 0 bloqueantes (sin segunda ronda).

### Lo no tan bueno (4 hallazgos nuevos → tareas)
- **T-173 (BUG, tenant_id en synthesizer):** `synthesis_report.json` y `open_questions.json` escriben `"tenant_id": "Flexempaque del Bajío S.A. de C.V."` (razón social) en vez del slug. El synthesizer nunca fue parchado (quedó fuera del alcance de BUG-1) y el **evaluador no lo detectó** (D2=1.0; la rúbrica no valida tenant_id en `support/`). → LEC-062. Fix: synthesizer lee tenant_id de harness-state + ampliar rúbrica.
- **T-174 (BUG, T-169 parcial):** anti-duplicado funcionó (sin duplicados pese a la reanudación), pero hubo **timestamp vacío** en `[SYNTHESIZER_REQUIRED]  — ` y **mojibake** en `[CP-01]`/`[CP-03 APROBADO]` (`completÃ³`, `â€"`) por codificación UTF-8/Latin-1 + BOM. Fix: extender la regla de timestamp a las líneas `*_REQUIRED` + `-Encoding utf8` consistente.
- **T-175 (mejora, mis-routing):** `pending_email.json` envió la guía de datos a Lucía (Planeación), pero quien extrae el histórico de SAP es Gerardo (técnico). Fix: el destinatario de la guía debe priorizar el rol técnico (desempate técnico > negocio > usuario).
- **T-176/DEC-053 (permisos):** demasiados prompts "¿Permitir este comando?" porque la allowlist heredada cubría `Bash(...)` pero el harness en Windows corre **PowerShell**. → LEC-063.

### Ajuste aplicado esta sesión (T-176 — Opción A)
El operador eligió **Opción A** (patrones específicos por comando, no comodín). Se amplió `templates/client-project-settings.json` con patrones `PowerShell(...)` para la plomería real del harness (`New-Item`, `Get-Content`, `Set-Content`, `Add-Content`, `Out-File`, `Test-Path`, `Get-ChildItem`, `Copy-Item`, `Move-Item`, `Remove-Item`, `Get-Date *`, `git *`, `python *`, `py *`). **Test_006 lo hereda** vía `faro-setup` (settings.json solo se crea si no existe). **Importante:** esto NO toca los gates Human-in-the-Loop (Sprint Contract, CP-03/04, escalamiento, handoff) — el operador aclaró que esos no se tocan; el problema eran los permisos de herramienta, no el flujo. DEC-053.

### Otros pendientes
- **T-172 (slug acentuado/truncado):** `flexempaque-del-baj-o-s-a-de-c-0949` — la `í` de "Bajío" se eliminó (`baj-o`) y se truncó perdiendo la `v` de "C.V.". No bloqueante (propaga consistente). Ajuste futuro de transliteración + truncado en frontera de guion.

### PRÓXIMO PASO (definido con el operador)
1. **Aplicar T-173, T-174, T-175 al repo fuente** (fixes de código en synthesizer, governor y configurator).
2. Correr **Test_006 (T-177)** en carpeta limpia para validar en runtime los tres fixes + el menor número de prompts (DEC-053). Empresa nueva con razón social acentuada para re-ejercitar el slug (T-172).
3. Arquitectura de dos terminales invariante (LEC-053): prueba en su carpeta, esta terminal de soporte.

---

## Sesión 33 — Cierre en código de BUG-1, BUG-2 y T-165; próximo paso = definir prueba e2e
2026-06-11 (sesión 33)

**Trabajo de esta terminal (soporte):** se implementaron los 3 fixes derivados de la corrida e2e de la sesión 32, todos en el repo fuente `Harness_Forecaster`:
- **T-167 + T-168 (BUG-1, tenant_id):** governor regenera el tenant_id en E10-A (nuevo Paso C, idempotente, DEC-047) y lo persiste antes de despachar workers; configurator ahora lo LEE de harness-state.json en vez de generarlo. Fuente única = governor.
- **T-169 (BUG-2, bitácora):** dos reglas globales de logging en el governor — sustitución obligatoria de timestamp UTC + guard anti-duplicado que verifica la última línea antes del append.
- **T-165 (responsable_pagos):** el interviewer ahora lo pregunta dirigido en el bloque de negocio (Bloque 5 de `preguntas_rol_negocio.md`), distinguido del aprobador/firmante. DEC-052.

**Decisiones nuevas:** DEC-052 (responsable_pagos dirigido). DEC-047 actualizada con la nota de restauración del tenant_id. LEC-060 y LEC-061 marcadas RESUELTO.

**Estado de los 3 hallazgos de la sesión 32:** BUG-1 ✅, BUG-2 ✅, T-165 ✅ — **todos cerrados en código, ninguno validado aún en runtime.** Falta T-164 (solo verificable observando una corrida).

**PRÓXIMO PASO (lo pidió el operador): DEFINIR una prueba end-to-end** que valide los 4 puntos pendientes en una corrida (tenant_id único, bitácora limpia, responsable_pagos capturado, guardado incremental). Detalle de objetivos y de la sincronización requerida en la sección "Estado actual → PRÓXIMO PASO" más abajo.

**Trabajo paralelo de la sesión 33 — Guía base de persistencia (Supabase):** a partir del análisis de `modelo.md` (schema de knowledge base heredado de OTRO harness), se creó `documents/supabase_persistence_guide.md` — documento guía con las definiciones principales para la persistencia futura de FARO. Hallazgo central del análisis: `modelo.md` solo cubre la capa de **conocimiento** (decisiones/lecciones), que es la **menos urgente**; FARO necesita 4 capas (operacional/runtime/medallón/knowledge) y la **operacional** (las 4 `db_records` que el configurator ya escribe con `_pendiente_supabase: true`) es la primera a construir, NO la de `modelo.md`. **Recomendación registrada en la guía: NO construir aún** — primero validar 010 e2e; la Capa 1 se construye antes/junto al diseño del harness 015. Ver la guía para capas, decisiones fundacionales (P-01…P-06), esquema operacional conceptual y decisiones abiertas (D-A…D-F). T-170.

---

## Sesión 32 — Refactor conductor cerrado + informe e2e Test_004A
2026-06-11 (sesión 32)

**Trabajo de esta terminal (soporte):** se cerraron T-166c y T-166d (ver "Estado actual"), se sincronizó el refactor a `Test_004A/.claude/` y, tras la corrida e2e del operador, se auditaron todos los artefactos. DEC-051 registrada. LEC-060 y LEC-061 añadidas. T-167/T-168/T-169 creadas.

**Informe de la corrida e2e (Test_004A — Prolimex S.A. de C.V., reanudación post límite de tokens 5h):**

*Lo bueno (el refactor funcionó):*
- El conductor despachó **toda la cadena no interactiva sin colgarse**: synthesizer (CP-01, ~3 min vs 19 min de cuelgue en sesión 30) → analyst (CP-02) → configurator DRAFT (CP-03, gate operador) → COMMIT (CP-05) → evaluator → CLOSE.
- **APPROVED 0.93, 1 iteración, `PHASE_COMPLETE`.** Cero `claude --print`, 48 señales `dispatch` en el governor.
- COMMIT completo: 4 registros BD, storage del tenant (6 subcarpetas), guía `.md`+`.pdf`, evento `onboarding_discovery_complete`, `pending_email.json` — rutas canónicas, sin vetos D4/D5/D7.
- DEC-050 confirmada (governor_mode transicionó EXECUTE→…→CLOSE; marcador interviewer respetado en la reanudación). Campos MISSING manejados con gracia (escalamiento no bloqueante, T-142).

*Lo no tan bueno (hallazgos nuevos):*
- **BUG-1 (major, real)** — divergencia de `tenant_id`: `prolimex-mx` (governor/analysis_report) vs `prolimex-s-a-de-c-v-4528` (deliverables/BD/storage/evento). Causa raíz confirmada en código: el governor ya no genera el tenant_id en E10-A (T-166a lo perdió) → analyst se bloqueó por ausencia y el governor lo generó reactivamente mal; y el configurator genera el suyo en vez de leerlo. El governor reconcilió en CLOSE (band-aid). Fix = **T-167** (governor) + **T-168** (configurator). Ver LEC-060.
- **BUG-2 (menor)** — `claude-progress.txt` con líneas duplicadas y timestamps vacíos. Se descartó el reinicio por tokens como causa (los timestamps muestran los duplicados DENTRO de la corrida continua post-reinicio, no en la frontera). Causa real = governor stateless que re-loguea en cada re-derivación del bucle conductor. Fix = **T-169**. Ver LEC-061.
- **T-165 confirmado** — `responsable_pagos` MISSING bajó D1 a 0.5 (no bloqueante).
- **Salvedad de T-166e** — el caso `EXECUTION_FAILED` (artefacto ausente) no se ejercitó porque ningún worker falló.

---

## Sesión 31 (T-166a)
2026-06-11 (sesión 31 — **T-166a implementada: governor refactorizado a despachador de un solo paso.** `discovery-governor.md` ya no encadena workers vía `claude --print` en background (causa del cuelgue T-166/LEC-059). Ahora cada modo de ejecución (EXECUTE, POST_CP03, POST_CP04, Protocolo de Rechazo) re-deriva su posición del disco y retorna **un solo** `GOVERNOR_RESULT`: cuando se necesita un worker o el orchestrator, emite `WORKER_REQUIRED`/`ORCHESTRATOR_REQUIRED` con un bloque `dispatch` (agent + prompt literal + then) para que el **conductor** (sesión principal) lo spawnee. EXECUTE = tabla de 13 filas (despachos 2A–2N); POST_CP04 = tabla de 5 filas (4A–4F, con pre-registro de campos MISSING como paso interno que NO spawnea); POST_CP03 rework en dos turnos; rechazo D2/D3→analyst, D4/D5/D7→configurator COMMIT, D1→interviewer. Eliminados los ~9 bloques CLI; `Agent` quitado de `tools` del frontmatter. Modos INIT/CLOSE/SUSPEND y formatos de estado intactos. Verificación estática OK. **Siguiente paso obligatorio: T-166b** (reescribir `commands/faro-discovery.md` como bucle conductor que consume estas señales). Hasta T-166b el harness NO corre end-to-end — es esperado. La prueba de reanudación de Test_004A es T-166e. Ver `progress/refactor_conductor_T166.md`.)

## Sesión 30
2026-06-11 (sesión 30 — **DEC-050 validada en corrida real.** Se reanudó Test_004A tras sincronizar a la carpeta de prueba los 3 archivos de la sesión 29 (orchestrator, governor, `discovery-state-schema`), que estaban desactualizados respecto al repo fuente. La reanudación confirmó **T-162** (`execution-state.json` recibió `interviewer_completed_at` + `interviewer_artifacts` vía el modo `INTERVIEWER_DONE`, sin avanzar `last_checkpoint`) y **T-163** (`harness-state.json` ganó `governor_mode: "EXECUTE"`, con `mode: "INICIO"` intacto a propósito). El harness avanzó al synthesizer y ahí apareció un **hallazgo nuevo**: el governor lo invocó como sub-instancia `claude --print` en background y quedó colgado ~19 min sin producir ningún artefacto (4 archivos de salida CLI en 0 bytes; cero `session_data.json`/`synthesis_report.json`/`open_questions.json`). Registrado como **T-166** + **LEC-059**. Prueba suspendida antes del synthesizer. Esta terminal operó como soporte. Quedan abiertos T-164, T-165 y T-166.)

## Sesión anterior
2026-06-11 (sesión 29 — Cerrados los dos hallazgos de capa de estado de Test_004A: **T-162** (marcador del tramo interactivo) y **T-163** (`governor_mode` vivo). Nuevo modo `[MODO: INTERVIEWER_DONE]` en el orchestrator que registra `interviewer_completed_at` sin avanzar `last_checkpoint`; nuevo campo `governor_mode` en `harness-state.json` sincronizado por el governor en cada transición. Aplicado en `discovery-orchestrator.md`, `discovery-governor.md`, `discovery-state-schema/SKILL.md` y `flows/010_discovery_flow.md`. DEC-050.)

## Estado actual — HARNESS 010 COMPLETO Y VALIDADO E2E; siguiente paso decidido: CONSTRUIR EL HARNESS 015 INTAKE

> **Para un agente en sesión nueva — leer esto primero.** El **harness 010 Discovery está terminado y validado end-to-end**: la corrida Test_006 (sesión 37) llegó al cierre con **veredicto APPROVED score 1.0, 7/7 dimensiones, sin vetos**. Todos los fixes funcionales acumulados (T-165, T-167/168, T-169, T-173, T-174, T-175, T-181) están en el repo fuente; el único recién aplicado (T-181, timestamps de bitácora) espera validación en la próxima corrida pero **NO es bloqueante**. Quedan 4 ajustes menores NO bloqueantes ya documentados (T-172, T-178, T-179, T-180) — refinamientos de calidad/schema, no deuda crítica.
>
> **DECISIÓN DEL OPERADOR (sesión 37): el siguiente paso es CONSTRUIR EL HARNESS 015 INTAKE** (tarea **T-060** = crear `brief/015_intake.md`, el Plan de Construcción con las 7 secciones, replicando el patrón de `brief/010_discovery.md`). El 015 consume el handoff del 010 (`onboarding_config.json` + evento `onboarding_discovery_complete`) e ingiere los datos del cliente para montar la capa **Bronce** (copia exacta intocable, arquitectura medallón). La documentación funcional ya existe en `harnesses/` (T-048) y el schema ampliado de `onboarding_config.json` que el 015 necesita ya está hecho (T-145).
>
> **Acoplamiento con la persistencia (DEC-055):** la guía `documents/supabase_persistence_guide.md` (D-A) vincula la **Capa 1 de persistencia** (esquema operacional Supabase) al diseño del 015 — se construye **junto/después** del 015, no antes en aislamiento. Mientras tanto el fallback JSON local (`_pendiente_supabase: true`) cubre el interín sin retrabajo (P-04). Dos decisiones abiertas frenan parte del detalle de persistencia: **T-031** (pasarela de pagos, D-B) y **T-030** (pesos del ITO, D-F, ligado a T-178).
>
> **Arquitectura de dos terminales (LEC-053) sigue vigente** para cualquier prueba e2e: la corrida vive en una carpeta de prueba dedicada; esta terminal `Harness_Forecaster` es soporte (aplica fixes al repo fuente, audita artefactos). El diseño/construcción del 015 (escribir el brief) SÍ se hace en esta terminal.

### Historial — el harness 010 fue terminado, validado y endurecido en 3 corridas e2e (sesiones 32–37)
- **Test_004A (sesión 32)** — validó el refactor al modelo conductor (T-166, DEC-051): el harness corre e2e sin colgarse. Destapó BUG-1 (tenant_id), BUG-2 (bitácora), T-165.
- **Test_005_Flexempaque (sesión 34)** — APPROVED 1.0. Validó T-165/T-167/T-168. Destapó T-173, T-174, T-175, T-176.
- **Test_006 (sesiones 36–37)** — APPROVED 1.0, ciclo completo con gates CP-03/CP-04 + evaluador C ejercitados. Validó T-173, T-174 (encoding), T-175. Destapó T-181 (timestamps, ya fixed) + confirmó T-178/T-179 (ajustes menores).

**El refactor al modelo conductor (T-166) está COMPLETO y PROBADO end-to-end** (sesión 32, revalidado en 34 y 37). Lo que sigue es **abrir el siguiente harness (015)**, no más correcciones del 010.

### Sesión 33 — qué se hizo (los 3 fixes derivados de la corrida e2e)

**BUG-1 — divergencia de `tenant_id` → CERRADO (T-167 + T-168):**
- **T-167** (`discovery-governor.md`): restaurada la generación del tenant_id perdida por el rewrite T-166a. Nuevo **Paso C** en "Construcción del Sprint Contract" (tras validar el brief en Paso B): deriva el tenant_id de la razón social con la convención DEC-047 (slug en minúsculas + sufijo `mmss` de 4 dígitos → `prolimex-s-a-de-c-v-4528`), lo persiste en `harness-state.json["tenant_id"]` **antes** de construir el contrato y despachar workers, e **idempotente** en reanudación (reutiliza si ya existe). Añadidos: línea `Tenant` al template del Sprint Contract, `tenant_id: null` al schema inicial de E10-A.3, y la persistencia al bloque de actualización de harness-state.
- **T-168** (`discovery-configurator.md`): el Paso 3 "Generar tenant_id" se reemplazó por "**Leer** tenant_id desde harness-state.json", replicando el patrón exacto del analyst (Paso 2): lee el campo, retorna `BLOCKED` si está vacío, **nunca genera**. Referencias `<generado>`/`<mismo generado>` en client_profile.json, onboarding_config.json y el CONFIGURATOR_RESULT actualizadas a "<leído de harness-state.json>".
- **Documentación:** nota del campo `tenant_id` añadida a `discovery-state-schema/SKILL.md` (fuente única = governor; analyst y configurator leen).
- **Resultado:** fuente única de verdad = governor en E10-A (DEC-047). El analyst ya leía bien; ahora el configurator también.

**BUG-2 — bitácora con líneas duplicadas y timestamps vacíos → CERRADO (T-169):**
- `discovery-governor.md`, sección central "Escritura en claude-progress.txt": dos reglas globales obligatorias que aplican a TODAS las escrituras del agente —
  1. **Regla de timestamp:** sustituir siempre `<timestamp>` por `$(Get-Date -AsUTC -Format 'yyyy-MM-ddTHH:mm:ssZ')` en el mismo `Add-Content`; prohibido el literal `<timestamp>` o el guion sin hora (`[EXECUTE]  —`).
  2. **Regla anti-duplicado (idempotencia):** leer la última línea con `Get-Content -Tail 1` y solo escribir si no contiene ya la misma etiqueta de evento (`if ($ultima -notmatch '\[CP-01\]')`). Ataca la causa raíz: el governor es stateless y el conductor lo re-spawnea en cada vuelta, re-derivando y re-logueando la misma transición.
- Puntero a estas reglas añadido en el encabezado de "Despachos y retornos de EXECUTE" (las filas checkpoint 2F/2I/2K se re-evalúan en cada vuelta). **Enfoque mantenible:** una regla central en vez de editar ~15 instrucciones de log dispersas.

**T-165 — `responsable_pagos` no capturado → CERRADO (decisión del operador: lo pregunta el interviewer):**
- `templates/010_discovery/preguntas_rol_negocio.md`: nueva pregunta **obligatoria** en el Bloque 5 (Plan de servicio) que pide **nombre + correo** de quien recibe los avisos de cobro/pago. Nota clave que la **distingue de "quién aprueba el presupuesto / firma el contrato"** (justo el error de Test_004A: se capturó al aprobador, no al responsable de pagos). Incluye sondas y manejo `MISSING`. Añadida a la tabla "Campos que este rol ayuda a completar" y a la checklist de cierre.
- `discovery-interviewer.md` Paso 6: la nota de campos bloqueantes ahora menciona `responsable_pagos` con apunte directo al Bloque 5.
- Las guías de preguntas se copian al proyecto vía `faro-init` (T-156), así que el fix llega a cada instalación nueva.

### Archivos tocados en sesión 33 (repo fuente `Harness_Forecaster`)
| Archivo | Cambio | Tarea |
|---|---|---|
| `.claude/agents/discovery-governor.md` | Paso C tenant_id en Sprint Contract + `tenant_id` en schema/template/persistencia; reglas globales de logging (timestamp + anti-duplicado) | T-167, T-169 |
| `.claude/agents/discovery-configurator.md` | Paso 3 lee tenant_id (no genera); referencias `<generado>` → leído | T-168 |
| `.claude/agents/discovery-interviewer.md` | Nota de campos bloqueantes Paso 6 menciona `responsable_pagos` | T-165 |
| `.claude/skills/discovery-state-schema/SKILL.md` | Nota documentando el campo `tenant_id` (fuente única = governor) | T-167 |
| `templates/010_discovery/preguntas_rol_negocio.md` | Pregunta dirigida de `responsable_pagos` en Bloque 5 + tabla + checklist | T-165 |

**Nota de sincronización:** estos cambios están en el repo fuente; **aún NO se sincronizaron a ninguna carpeta de prueba**. La corrida de validación requiere copiarlos primero (ver "PRÓXIMO PASO" abajo).

---

### Contexto del refactor conductor (sigue vigente)

**El refactor al modelo conductor (T-166) está COMPLETO y PROBADO end-to-end.** El harness 010 corre de principio a fin sin colgarse bajo el nuevo modelo.

### Qué es el modelo conductor (contexto para una sesión nueva)
Un subagente de Claude Code **no puede spawnear otros subagentes** (doc oficial). El governor y el orchestrator son subagentes → **ninguno spawnea**. El único que spawnea es el **conductor** = la sesión principal donde corre el comando `/faro-*`. Handshake: el conductor spawnea al governor en un modo → el governor re-deriva su posición del disco y retorna **un solo** `GOVERNOR_RESULT` (`WORKER_REQUIRED`/`ORCHESTRATOR_REQUIRED` con bloque `dispatch` = `{agent, prompt, then}`) → el conductor spawnea al agente vía herramienta `Agent`, verifica sus artefactos, y re-invoca al governor con `[MODO: then]`. El interviewer es la excepción (corre inline). Bucle definido en `templates/workflows/conductor_loop.md`. Decisión: **DEC-051**.

### Refactor T-166 — terminado (sesiones 31–32)
- ✅ **T-166a** — `discovery-governor.md` convertido a despachador de un paso (EXECUTE 13 filas, POST_CP04 5 filas, rechazo, sin bloques `claude --print`).
- ✅ **T-166b** — bucle conductor en `templates/workflows/conductor_loop.md`; `faro-discovery/restart/continue.md` reescritos como conductores.
- ✅ **T-166c** — descripciones corregidas en `discovery-orchestrator.md` y `discovery-synthesizer.md` ("el governor spawea" → "el conductor spawnea").
- ✅ **T-166d** — `flows/010_discovery_flow.md` (sección "El modelo conductor" + diagrama) y `discovery-state-schema/SKILL.md` actualizados; **DEC-051** registrada.
- ✅ **T-166e** — **VALIDACIÓN e2e en Test_004A**: synthesizer→CP-01→analyst→CP-02→configurator DRAFT→CP-03→COMMIT→CP-05→evaluator→CLOSE **sin colgarse**. **APPROVED 0.93, PHASE_COMPLETE.** Synthesizer en ~3 min (antes 19 min colgado). T-166/LEC-059 cerrado.
  - **SALVEDAD:** el caso de fallo "artefacto ausente → `EXECUTION_FAILED` (no espera infinita)" NO se ejercitó (ningún worker falló). Queda sin confirmar en runtime — provocar un fallo deliberado en una próxima prueba.

### PRÓXIMO PASO — DEFINIR la prueba end-to-end de validación

Todos los fixes de código (BUG-1, BUG-2, T-165) están aplicados en el repo fuente. **El próximo paso es DISEÑAR/DEFINIR una prueba e2e** que valide los 4 puntos pendientes en una sola corrida. El usuario pidió explícitamente que el próximo paso sea **definir esa prueba e2e**.

**Qué debe validar la prueba e2e (objetivos de aceptación):**
1. **tenant_id único (T-167+T-168)** — un solo `tenant_id` consistente en TODOS los artefactos: `harness-state.json`, `analysis_report.json`, `client_profile.json`, `onboarding_config.json`, registros BD (db_records), carpeta storage (`1000_storage_local/tenants/{id}/`) y evento `onboarding_discovery_complete`. Generado por el governor en E10-A con formato DEC-047. Cero divergencias.
2. **Bitácora limpia (T-169)** — `claude-progress.txt` SIN líneas duplicadas y SIN timestamps vacíos (`[EXECUTE]  —`). Cada evento de checkpoint aparece una sola vez con hora UTC real.
3. **responsable_pagos capturado (T-165)** — el interviewer hace la pregunta dirigida en el bloque de negocio; `responsable_pagos` (nombre + correo) queda como dato estructurado en session_notes → session_data → client_profile, NO como MISSING. (Distinto del aprobador/firmante.)
4. **Guardado incremental (T-164)** — inspeccionar `session_notes.json` A MITAD de una sesión de entrevista (no al final) para confirmar que el guardado por bloque persiste antes de completar todos los bloques del stakeholder.

**Salvedad heredada (opcional, no del usuario):** el caso de fallo "artefacto ausente → `EXECUTION_FAILED` sin espera infinita" sigue sin ejercitarse. Considerar provocar un fallo deliberado de un worker en esta o una prueba futura.

**Antes de correr la prueba — sincronizar el repo fuente a una carpeta de prueba LIMPIA** (sin tocar `010_discovery/support/`, `600_persistence/`, `settings*.json`):
- `.claude/agents/*` (governor, configurator, interviewer cambiaron en sesión 33)
- `.claude/skills/*` (state-schema cambió)
- `commands/*` → `.claude/commands/`
- `templates/workflows/conductor_loop.md` → `.claude/workflows/`
- `templates/010_discovery/preguntas_rol_negocio.md` → se copia vía `faro-init`; si la carpeta de prueba ya existe, copiarlo a `010_discovery/templates/` manualmente
- Recomendado: carpeta NUEVA y limpia (`faro-setup` → `/faro-init` → `/faro-discovery` desde cero), con un brief que incluya un responsable de pagos identificable para ejercitar T-165.

### Cómo se corre la prueba (dos terminales, LEC-053)
- **Terminal de prueba** = carpeta de prueba LIMPIA (p. ej. `C:\Users\USUARIO\Documents\Triple S\Test_Forecaster\Test_005\`). Ejecuta `faro-setup` → `/faro-init` → `/faro-discovery` y conduce la entrevista. (Test_004A quedó en `PHASE_COMPLETE` con el código viejo — NO sirve para revalidar; usar carpeta nueva.)
- **Esta terminal** (`Harness_Forecaster`) = soporte: aplica fixes al repo fuente, revisa artefactos en disco, NO conduce la entrevista.

**Base ya consolidada:** persistencia del interviewer resuelta (setup-first, DEC-049); capa de estado T-162/T-163 cerrada (DEC-050); modelo conductor T-166 cerrado y validado (DEC-051).

**Arquitectura de dos terminales (invariante para todas las pruebas):**

| Terminal | Proyecto | Rol |
|----------|----------|-----|
| Terminal de prueba | Carpeta `Test_004A/` (u otra) | Ejecuta el harness: `faro-setup` → `/faro-init` → `/faro-discovery` → interviewer interactivo |
| Terminal Harness_Forecaster (esta) | `Harness_Forecaster/` | Soporte: responde preguntas del operador, diagnostica bugs en tiempo real, aplica fixes al repo fuente |

**IMPORTANTE (LEC-053):** las respuestas de entrevista se dan en la terminal de PRUEBA, no en la de soporte. La terminal de soporte (esta) NO comparte sesión con la de prueba — sirve para diagnóstico, fixes y revisión de artefactos en disco, no para conducir la entrevista.

---

## Qué cambió en sesión 30

**Objetivo de la sesión:** validar en corrida real los fixes T-162/T-163 (DEC-050) reanudando Test_004A, con esta terminal `Harness_Forecaster` operando como soporte (diagnóstico, revisión de artefactos en disco, registro de hallazgos). No se condujo entrevista desde aquí (LEC-053).

**Sincronización previa necesaria (detectada como soporte):** Test_004A se instaló antes de la sesión 29, así que su `.claude/` estaba desactualizado respecto al repo fuente. Comprobación: `discovery-orchestrator.md` de la prueba tenía **0** referencias a `INTERVIEWER_DONE` (fuente: 2) y `discovery-governor.md` tenía 4 (fuente: 9). Sin sincronizar, la reanudación NO ejercitaría el fix. Se copiaron 3 archivos del repo fuente a `Test_004A/.claude/` **sin tocar artefactos ni estado**:
- `agents/discovery-orchestrator.md`
- `agents/discovery-governor.md`
- `skills/discovery-state-schema/SKILL.md`

**Validación (T-162 y T-163 — DEC-050 confirmada):** tras reanudar con `[MODO: EXECUTE] + interviewer_complete: true`:
- `execution-state.json` → `interviewer_completed_at: "2026-06-11T13:46:07Z"` + `interviewer_artifacts` con los paths de session_notes/stakeholder_map; `last_checkpoint` siguió en `null` (correcto — CP-01 es del synthesizer). ✅ T-162.
- `harness-state.json` → `status: ACTIVE`, `suspension: null`, **`governor_mode: "EXECUTE"`**; `mode` se mantuvo en `"INICIO"` (deliberado — lo lee el orchestrator en PLAN). ✅ T-163.
- `claude-progress.txt` registró `REANUDACION` (13:44) → `INTERVIEWER_COMPLETE` (13:46, "Marcador interviewer_completed_at persistido… Pasando al synthesizer").

**Hallazgo nuevo T-166 (LEC-059) — spawn de workers vía CLI anidado en background:** el governor avanzó al synthesizer invocándolo como sub-instancia de Claude en segundo plano (`<prompt> | claude --agent discovery-synthesizer --print --dangerously-skip-permissions 2>&1`) y se quedó haciendo polling del archivo de salida. Tras ~19 min: **cero artefactos** del synthesizer en todo el proyecto (sin `session_data.json`/`synthesis_report.json`/`open_questions.json`), **4 archivos de salida CLI en 0 bytes**, y un proceso `claude` colgado (~188s CPU). El agente synthesizer existía (12 KB) y los flags eran válidos — la falla es del **mecanismo de spawn**, no de sintaxis ni de datos. Causa raíz: `--print` solo emite al terminar; si la sub-instancia se cuelga, la salida queda vacía, los artefactos nunca se escriben y el governor espera indefinidamente. **Fix propuesto:** invocar a los workers (synthesizer/analyst/configurator) vía la herramienta `Agent` en la misma sesión, o — si se requiere aislamiento — no usar `--print` en background sin timeout + verificación de que los artefactos existen en disco antes de avanzar. Precaución de diagnóstico: una sub-instancia `claude` colgada puede ser indistinguible por PID de la propia terminal de prueba — no matar procesos a ciegas.

**Cierre de sesión:** prueba suspendida por el operador antes del synthesizer. Hallazgo registrado en `tasks.md` (T-166) y `lessons.md` (LEC-059). DEC-050 queda validada.

---

## Qué cambió en sesión 28

**El problema que persistía:** Pese a T-158 (sesión 27), las pruebas Test_003D y Test_003E mostraron que el `discovery-interviewer` seguía sin crear `stakeholder_map.json` ni `session_notes.json` de forma automática — solo los escribía si el operador se lo pedía explícitamente. El operador detectó el síntoma con precisión: el agente "pasaba directamente a las siguientes preguntas y no guardaba nada".

**Diagnóstico de raíz (dos causas combinadas):**
1. **Lenguaje condicional suave** — los pasos de inicio decían "**Intentar** leer `stakeholder_map.json`" y "Crear o cargar notas (**si aplica**)". Para un LLM, "intentar" y "si aplica" señalan que el paso es opcional; si el archivo no existe, el agente avanza sin escribir (LEC-055).
2. **El agente corría hacia la entrevista** — percibía su tarea como "entrevistar" y, con los stakeholders del brief ya en contexto, trataba la escritura de archivos como trámite redundante diferible (LEC-056).

**El operador hizo la pregunta clave:** "¿por qué dice *intentar* leer? debería ser *leer*". Eso enfocó el fix en la causa correcta.

**Fix aplicado (DEC-049) — rediseño setup-first de `discovery-interviewer.md`:**
- **T-159** — Sección "Al iniciar" reestructurada en un turno de setup explícito: Paso 1 leer brief → Paso 2 garantizar `stakeholder_map.json` (PRIMER ENTREGABLE) → Paso 3 garantizar `session_notes.json` (`[]` si nuevo) → Paso 4 confirmación visible al operador → Pasos 5-6 guías y modo. GATE DE ARRANQUE prohíbe preguntar antes de que ambos archivos existan en disco. El primer turno NO contiene preguntas.
- **T-160** — Eliminada la skill `discovery-session-schema` del frontmatter (pertenece al synthesizer). El conocimiento de campos bloqueantes se movió a una nota del Paso 6 (LEC-057).
- **T-161** — Guardado por bloque reformulado en lenguaje positivo ("STOP — no generar texto; escribir; confirmar; continuar"). Cierre snowball ahora escribe `stakeholder_map.json` con confirmación visible.

**Validación (T-004A) — prueba de humo con Prolimex S.A. de C.V. (Monterrey, NL):**
- 4 sesiones conducidas: Valentina Ríos (negocio+usuario), Rodrigo Castillo (técnico), Camila Fuentes (usuario), Patricio Lozano (usuario+técnico — descubierto por snowball).
- **Ambos archivos creados sin intervención del operador.** Confirmado que el agente de la prueba tenía el fix (GATE DE ARRANQUE presente).
- Calidad de captura muy alta: factores estacionales numéricos de Camila (×2.8–3.2 Buen Fin por cadena), hallazgo del "colchón de Patricio" como causa del sobre-inventario, dos eventos atípicos de producción marcados como outliers, lead time heterogéneo por SKU.
- Snowball expandió de 3 a 11 stakeholders con estados diferenciados (`completada`/`pendiente`/`opcional`/`externo`/`respaldo`).
- Suspendida limpiamente antes del synthesizer.

**Hallazgos nuevos en la capa de estado (del análisis post-prueba de los archivos en disco):**
- **T-162** — `execution-state.json` no registró que el interviewer completó (congelado en `last_checkpoint: null`, `last_updated` pre-entrevistas). El `orchestration_plan` no define checkpoint para el tramo interactivo. La única evidencia está en la nota de suspensión de `harness-state.json` (LEC-058).
- **T-163** — `harness-state.json > mode` quedó en `"INICIO"` aunque el harness ya estaba en EXECUTE.
- **T-164** — no se pudo verificar el guardado incremental por bloque (timestamps consistentes con un único write final). Inspeccionar a mitad de sesión en la próxima prueba.
- **T-165** — `responsable_pagos` (obligatorio del synthesizer) no se capturó como campo estructurado.

**Lección transversal:** lo que NO funcionó en sesiones previas fue endurecer el lenguaje prohibitivo (T-157 → LEC-054). Lo que SÍ funcionó fue reordenar el flujo en turnos y hacer del archivo el entregable visible del primer turno (LEC-056). El contraste entre ambas sesiones es la lección de diseño más importante para workers interactivos futuros.

---

## Qué cambió en sesión 27

**T-158 — Regresión de T-157 revertida en `discovery-interviewer.md`:**
- **Bug diagnosticado:** T-157 había agregado "PARAR COMPLETAMENTE — no escribir ningún texto adicional" al Paso 2 de la secuencia de guardado. Esta instrucción paralizaba al agente: interpretaba "no escribir texto" como "no producir ninguna salida", incluyendo llamadas al Write tool. El interviewer pasaba directamente al siguiente bloque sin guardar nada. Ni `session_notes.json` ni `stakeholder_map.json` se creaban.
- **Raíz del problema:** Lenguaje prohibitivo fuerte ("PARAR COMPLETAMENTE", "BLOQUEANTE", "inviolable") no refuerza secuencias en agentes — las inhibe. (LEC-054)
- **Fix:** Paso 2 revertido a "**PARAR** — no presentar el siguiente bloque todavía". Paso 6 simplificado a "Escribir el archivo completo con `Write`". Eliminada la línea "Esta secuencia es inviolable...". Estado idéntico al de Test_002B donde el guardado automático funcionaba.
- **Aplicado en:** `Harness_Forecaster/.claude/agents/discovery-interviewer.md` (repo fuente).

**Brief de Test_003C preparado:**
- Empresa: **Limptek Industrial S.A. de C.V.** (San Luis Potosí, SLP) — limpieza industrial para automotriz y alimentos.
- Diferente a T-003A (limpieza industrial B2B con Microsip) y T-003B (retail con SAP) en: ERP (CONTPAQi), mercado (automotriz+alimentos vs. industrial/retail), problema principal (estacionalidad por paros de planta vs. picos promocionales).
- Riesgo de adopción interesante: Marcos Pedraza (7 años en empresa, pronósticos Excel propios).

---

## Qué cambió en sesión 26

**Revisión del estado de Test_003A_Limpieza:**
- El harness llegó a `PENDING_CONTRACT` con Sprint Contract generado correctamente para Limpro Industrial S.A. de C.V.
- Se detectaron 3 bugs nuevos durante la revisión.

**T-155 — Governor E10-A.2 expandido a 10 carpetas:**
- El bloque `foreach` de E10-A.2 solo creaba 6 carpetas de primer nivel. Faltaban `010_discovery\deliverables`, `010_discovery\support`, `010_discovery\templates`, `010_discovery\schemas`.
- Fix: el `foreach` ahora crea las 10 carpetas completas. El governor es autosuficiente — no depende de que `faro-init` haya corrido previamente.
- Copiado a `Test_003A_Limpieza` y `Test_003B_Limpieza`.

**T-156 — faro-init copia preguntas_rol_*.md al proyecto:**
- El `discovery-interviewer` busca `preguntas_rol_negocio.md`, `preguntas_rol_tecnico.md`, `preguntas_rol_usuario.md` en `010_discovery/templates/` del proyecto, pero `faro-init` solo copiaba 2 archivos a esa carpeta.
- Sin las guías, el interviewer improvisa preguntas en lugar de seguir la estructura definida.
- Fix: `faro-init.md` ahora incluye los 3 archivos en el array `$incluir`.
- Los 3 archivos copiados a `Test_003A_Limpieza` y `Test_003B_Limpieza`.

**T-157 — Guardado por bloque del interviewer reforzado como BLOQUEANTE:**
- La instrucción de guardado ya existía pero el LLM podía saltársela. Se reforzó el lenguaje: "PARAR COMPLETAMENTE", "acción BLOQUEANTE", "Esta secuencia es inviolable".
- El agente no puede presentar el siguiente bloque hasta que el `Write` confirme éxito.
- Fix copiado a `Test_003A_Limpieza` y `Test_003B_Limpieza`.

**Brief de Test_003B preparado:**
- Empresa: **Prolimex S.A. de C.V.** (Monterrey, NL) — limpieza para hogar y comercial ligero.
- Diferente a Test_003A en: ERP (SAP vs. Microsip), escala (150 SKUs / 40 clientes vs. 95 / 70), historial (3 años vs. 5 años), mercado (retail vs. industrial), problema principal (picos promocionales vs. estacionalidad por auditorías).
- 3 stakeholders con perfil detallado. Riesgo interesante: Camila (Analista) tiene su propio modelo Excel de pronóstico — posible aliada o resistencia.

---

## Qué cambió en sesión 25

**T-150 completada — todos los fixes aplicados (15/15):**

Los últimos dos fixes (T-145 + T-139) se aplicaron a `discovery-configurator.md`:

- **T-145** — `onboarding_config.json` expandido a 6 secciones: `ingesta`, `pronostico`, `canales_entrega`, `alertas`, `estado_datos_erp`, `esquema2`. Cada sección tiene schema JSON documentado con fuentes y tipos.
- **T-139** — Reglas de población explícitas por sección en Modo DRAFT Paso 6: inferencia de canales por perfil de usuario, derivación de alertas desde `criterios_exito`, extracción de datos ERP desde notas del stakeholder técnico, lógica de `umbral_mape_objetivo_pct` según código cold start.
- `client_config.json` en Modo COMMIT (db_records) actualizado para reflejar los campos clave del nuevo schema (nivel_cold_start, sistema_erp, anios_historial_disponible, onboarding_config_path).

**Brief.md preparado para Limpro Industrial:**

- 3 stakeholders: Carlos Hernández (Negocio + Usuario), Patricia Méndez (Técnico), Jorge Avilés (Usuario)
- ERP: Microsip Enterprise desde 2020 (~5 años historial)
- ~95 SKUs activos (desengrasantes, desinfectantes, jabones, sanitizantes, limpiadores de piso)
- ~70 clientes B2B (plantas industriales, empacadoras, hoteles, rastros, distribuidores)
- Riesgo principal: duplicados en 2022 por migración de módulo en Microsip
- Estacionalidad ligada a calendarios de auditorías HACCP/NOM de clientes del sector alimentos

---

## Qué cambió en sesión 24

**T-148 descartada — razonamiento:**
Con DEC-048, `faro-setup` siempre copia `brief.md` al proyecto. El escenario "archivo no existe" ya no ocurre. El caso "brief incompleto" está cubierto por T-144. Se agregó un guard mínimo (brief no existe → INIT_FAILED + "ejecuta faro-setup primero") como parte de T-150 al editar el governor.

**T-150 — Fixes aplicados en sesión 24 (12 de 15):**

| # | Archivo | Fix | Estado |
|---|---|---|---|
| T-136 | `discovery-analyst.md` | Nuevo Paso 2: leer `tenant_id` desde `harness-state.json`. Bloquea si está vacío. Nunca genera el tenant_id. | ✅ |
| T-137 | `discovery-interviewer.md` | Cierre snowball: secuencia numerada obligatoria de 5 pasos para marcar `"completada"` en `session_notes.json`. REGLA CRÍTICA: aplica a todos los stakeholders incluyendo el último. | ✅ |
| T-143 | `discovery-synthesizer.md` | Verificado con lectura directa: los 3 paths de `session_data.json` ya usan `010_discovery/support/`. Sin cambios requeridos. | ✅ |
| T-144 + guard T-148 | `discovery-governor.md` | Construcción del Sprint Contract: Paso A verifica existencia de `brief.md` (INIT_FAILED + "ejecuta faro-setup"); Paso B valida campos obligatorios con tabla explícita y lista los vacíos antes de detener. | ✅ |
| T-142 | `discovery-governor.md` | POST_CP04 Paso 6 nuevo: lee `session_data.json`, detecta campos MISSING, pre-registra ESC en `harness-state.json` antes de lanzar auditoría. Paso 7 y 8 renumerados. | ✅ |
| DEC-006 | `discovery-governor.md` | `decisions_library.md` inicial: DEC-006 actualizada con rutas canónicas `600_persistence/pending_email.json` y `600_persistence/events/onboarding_discovery_complete.json`. Elimina referencias a `correo_pendiente.json` y `evento_pendiente.json`. | ✅ |
| T-138 | `discovery-configurator.md` | Paso 2 DRAFT: agrega `synthesis_report.json` como tercer artefacto de entrada. `criterios_exito` en `client_profile.json`: copiar TEXTUALMENTE desde `synthesis_report.campos_consolidados.criterios_exito.valor`. | ✅ |
| mkdir db_records | `discovery-configurator.md` | Paso 3 COMMIT: `New-Item -Force -Path "010_discovery/db_records"` explícito antes de escribir los 4 JSONs. | ✅ |
| storage configurator | `discovery-configurator.md` | Paso 4 y verificaciones COMMIT: `010_discovery/storage_local/` → `1000_storage_local/`. | ✅ |
| storage evaluator | `discovery-evaluator.md` | Tabla de artefactos y bloque PowerShell: `010_discovery/storage_local/` → `1000_storage_local/`. | ✅ |
| storage + correo rubric | `discovery-rubric/SKILL.md` | D5: path `1000_storage_local/`, subcarpetas DEC-044 (`1000_data/005_bronze/` etc.), `client_profile.json` → `deliverables/client_profile.json`. D6: `correo_pendiente.json` → `600_persistence/pending_email.json`. Ancla 1.0 actualizada. | ✅ |

**T-150 completada — 15/15 fixes aplicados:**

Últimos fixes aplicados en sesión 25 (T-145 + T-139):
- `discovery-configurator.md` Paso 6 DRAFT reemplazado: `onboarding_config.json` expandido a 6 secciones (`ingesta`, `pronostico`, `canales_entrega`, `alertas`, `estado_datos_erp`, `esquema2`) con schema JSON documentado y reglas de población explícitas por sección (inferencia de canales, derivación de alertas desde `criterios_exito`, extracción de datos ERP desde notas stakeholder técnico, `umbral_mape_objetivo_pct` según código cold start).
- `client_config.json` en Modo COMMIT (db_records) actualizado para incluir campos clave del nuevo schema: `nivel_cold_start`, `sistema_erp`, `anios_historial_disponible`, `onboarding_config_path`.

**Próxima acción — T-003B:**

La próxima prueba de humo es **Test_003B_Limpieza** con Prolimex S.A. de C.V. en una terminal de prueba separada. Esta terminal (`Harness_Forecaster`) actúa como soporte. Ver sección "Estado actual" al inicio del documento.

**Pasos para arrancar Test_003B:**
1. Abrir terminal de Claude Code en `Test_003B_Limpieza/`
2. Ejecutar `/faro-init` (ya instalado por faro-setup)
3. Ejecutar `/faro-discovery`
4. Cuando el governor retorne `INTERVIEWER_REQUIRED`, invocar `discovery-interviewer` y conducir las 3 sesiones (Valentina → Rodrigo → Camila)

---

## Qué cambió en sesión 23

**Rediseño completo de la infraestructura de instalación (DEC-048):**

- **T-149** — `.claude/agents/` y `.claude/skills/` del repo restaurados desde `Test_002B_Laboratorio`. 7 agentes y 7 skills copiados correctamente. Base para aplicar T-150.
- **T-151** — `faro-setup.ps1` reescrito desde cero como instalador por proyecto. Ejecutar con alias `faro-setup` desde terminal en la carpeta del proyecto. Instala: `.claude/agents/`, `.claude/skills/`, `.claude/commands/`, `.claude/workflows/`, `CLAUDE.md`, `settings.json`, `settings.local.json` (con `FARO_HOME` inyectado), `800_inputs/brief.md`. Sin junctions globales. Lógica de detección: agentes ajenos avisa y pide confirmación; harness activo avisa pero permite actualización; `settings.json` y `brief.md` no se sobreescriben si ya tienen contenido.
- **T-152** — `commands/faro-init.md` actualizado: crea todas las carpetas de runtime (`600_persistence/`, `605_eval/`, `610_knowledge/`, `615_changes/`, `700_contract/`) y estructura completa de `010_discovery/` (`deliverables/`, `support/`, `templates/`, `schemas/`). Copia desde `$env:FARO_HOME`: scripts `.py`, `session_template.md`, `data_intake_guide_template.md`, `data_intake_guide_esquema2_block.md`, schemas JSON. Los `preguntas_rol_*.md` NO se copian al proyecto.
- **T-153** — Alias `faro-setup` agregado al perfil de PowerShell 7 (`Documents/PowerShell/Microsoft.PowerShell_profile.ps1`). Permite invocar el script desde cualquier carpeta.
- **T-154** — Junction global `~/.claude/commands/` eliminada. Comandos ahora solo a nivel de proyecto.
- **Prueba exitosa** — `Test_Prueba_001` completó los tres pasos: `faro-setup` → `/faro-init` → `/faro-discovery`. Harness llegó a `PENDING_CONTRACT` correctamente con Sprint Contract generado.

**Flujo de instalación nuevo (DEC-048):**
```
1. cd <carpeta-proyecto-nuevo>
2. faro-setup                    ← terminal (alias PowerShell)
3. Completar 800_inputs\brief.md
4. Abrir/reiniciar Claude Code
5. /faro-init                    ← Claude Code
6. /faro-discovery               ← Claude Code
```

**Próxima acción inmediata — orden obligatorio:**

1. **T-148** — `discovery-governor.md` E10-A: si `800_inputs/brief.md` no existe → crear `800_inputs/`, copiar template desde `$env:FARO_HOME/templates/010_discovery/brief_template.md`, retornar `INIT_PAUSED`. Ya no usar `~/.faro/faro.config.json` — usar `$env:FARO_HOME`.
2. **T-150** — Re-aplicar los 14 fixes a los agentes restaurados en T-149.
3. **T-003** — Prueba de humo con Limpro Industrial S.A. de C.V.

---

## Resumen ejecutivo
El proyecto **completó dos pruebas de humo del harness 010 Discovery** (T-092 y T-129). El sistema se llama **FARO** (Forecasting Agentic Results & Operations — DEC-029).

- **Prueba T-092** con Distribuidora Nutrivalle S.A. de C.V. → **APPROVED score 0.93**
- **Prueba T-129 (Test_002B)** con Laboratorios Vita S.A. de C.V. → **APPROVED score 0.93** (2 iteraciones: rechazo 0.71 → aprobación 0.93)

El harness 010 funciona end-to-end. Se corrigieron los 10 bugs post-Test_002B y se descubrieron nuevos bugs de infraestructura. **SITUACIÓN CRÍTICA:** `.claude/agents/` y `.claude/skills/` del repo están vacíos — fueron borrados por un bug del `deploy-harness.ps1` (hot-swap en modo normal borraba archivos a través de junctions). La fuente de recuperación es `Test_002B_Laboratorio/.claude/` que tiene las versiones pre-sesión-20.

**Sesión 21 — Bugs corregidos en agentes/skills (se deben re-aplicar al restaurar desde Test_002B):**

| # | Archivo | Cambio | Tarea |
|---|---|---|---|
| 1 | `discovery-interviewer.md` | Secuencia numerada explícita (7 pasos) para cierre de sesión en `session_notes.json` + REGLA CRÍTICA para todos los stakeholders incluyendo el último | T-137 |
| 2 | `discovery-synthesizer.md` | Verificado: path `010_discovery/support/session_data.json` ya era correcto | T-143 |
| 3 | `discovery-governor.md` | Validación de 7 campos obligatorios del brief antes de construir Sprint Contract — lista vacíos y retorna INIT_FAILED | T-144 |
| 4 | `discovery-configurator.md` | Mkdir explícito `010_discovery/db_records/` antes de escribir los 4 archivos JSON | nuevo |
| 5 | `discovery-configurator.md`, `discovery-evaluator.md`, `discovery-rubric/SKILL.md` | Storage movido de `010_discovery/storage_local/` → `1000_storage_local/` en raíz del proyecto | nuevo |
| 6 | `discovery-rubric/SKILL.md` | Paths de `correo_pendiente.json` → `600_persistence/pending_email.json` en verificación D6 y anclas | nuevo |
| 7 | `discovery-governor.md` | DEC-006 en `decisions_library.md`: `correo_pendiente.json` → `600_persistence/pending_email.json`, `evento_pendiente.json` → `600_persistence/events/onboarding_discovery_complete.json` | nuevo |

⚠️ **ATENCIÓN:** Todos estos cambios fueron diseñados en sesión 21 pero los archivos en `.claude/agents/` y `.claude/skills/` siguen vacíos en disco. Al restaurar desde Test_002B (T-149), re-aplicar los 7 cambios de arriba MÁS los 7 de sesión 20 (T-136, T-138, T-139, T-140, T-141, T-142, T-145).

**Sesión 21 — Bugs de infraestructura descubiertos y diseño de solución:**

| Bug | Descripción | Estado |
|---|---|---|
| Deploy borra archivos a través de junction | En modo normal, el hot-swap del deploy borraba `discovery-*.md` del repo cuando el destino era una junction. Causa de la pérdida de archivos. | diseñado — pendiente fix |
| `faro-setup.ps1` no instala agents/skills globalmente | Solo instala commands. Agents y skills requieren deploy manual. | diseñado — pendiente fix |
| `/faro-init` requiere deploy previo | Governor no crea `800_inputs/` ni copia `brief_template.md` — depende del deploy. | diseñado — pendiente fix |

**Diseño aprobado por el operador — nuevo flujo objetivo:**
1. `faro-setup.ps1` (una vez por máquina) → junctionea `~/.claude/agents/`, `~/.claude/skills/` y `~/.claude/commands/` al repo
2. Crear carpeta del proyecto cliente
3. Abrir en Claude Code → `/faro-init` → governor crea estructura + deposita `brief.md` template + instruye al operador completarlo
4. Completar `800_inputs/brief.md` → `/faro-init` de nuevo → arranca el harness

**Sesión 20 — Corrección de bugs post-Test_002B:**

| Bug | Archivo | Descripción | Estado |
|---|---|---|---|
| T-142 | `discovery-governor.md` | Paso 6 nuevo en POST_CP04: pre-registrar ESC por campos MISSING antes de invocar evaluador | ✅ implementada |
| T-140 | `discovery-configurator.md` | Evento en `600_persistence/events/` — ya estaba correcto en código | ✅ verificada |
| T-141 | `discovery-configurator.md` | `pending_email.json` en `600_persistence/` — ya estaba correcto en código | ✅ verificada |
| T-136 | 3 archivos | tenant_id: governor lo genera al construir Sprint Contract y lo escribe en harness-state.json; analyst y configurator lo leen de harness-state.json (DEC-047) | ✅ implementada |
| T-138 | `discovery-configurator.md` | `criterios_exito` copia textual de `synthesis_report.campos_consolidados.criterios_exito.valor` | ✅ implementada |
| T-145 | `discovery-configurator.md` | Schema ampliado de `onboarding_config.json`: 6 secciones con estructura y fuentes definidas | ✅ implementada |
| T-139 | `discovery-configurator.md` | Lógica de población por sección del `onboarding_config.json` expandido | ✅ implementada |

**Próxima acción inmediata — PASO 1: Corregir infraestructura (antes de cualquier prueba):**

1. **T-146** — Corregir `deploy-harness.ps1`: en modo normal, antes del hot-swap verificar si `$destinoAgentes` / `$destinoSkills` son junctions — si lo son, eliminar solo el link (no el contenido)
2. **T-147** — Actualizar `faro-setup.ps1`: agregar junctions `~/.claude/agents/` → repo `.claude/agents/` y `~/.claude/skills/` → repo `.claude/skills/`
3. **T-148** — Actualizar `discovery-governor.md` E10-A: si `800_inputs/brief.md` no existe, crear la carpeta y copiar el template desde `faro_home` (leyendo `~/.faro/faro.config.json`), luego retornar instrucción al operador de completarlo
4. **T-149** — Restaurar `.claude/agents/` y `.claude/skills/` del repo desde `Test_002B_Laboratorio/.claude/`
5. **T-150** — Re-aplicar los 14 fixes a los archivos restaurados (7 de sesión 20 + 7 de sesión 21)
6. **T-003** — Ejecutar prueba de humo con Limpro Industrial S.A. de C.V. (brief en `brief.md` en raíz del repo) → objetivo: APPROVED en primera evaluación

**Qué cambió en sesión 20:**
- **T-142** — `discovery-governor.md` Modo POST_CP04: nuevo Paso 6 que lee `session_data.json`, detecta campos con valor `"MISSING"` y registra un ESC en `harness-state.json["escalations"]` por cada uno antes de invocar al evaluador. El antiguo Paso 6 (auditoría) quedó como Paso 7 y el antiguo Paso 7 (leer resultado) como Paso 8.
- **T-140 y T-141** — Verificadas: el configurator ya tenía las rutas correctas en el código (`600_persistence/events/` y `600_persistence/pending_email.json`). Solo estaban sin marcar en tasks.md.
- **T-136** — Fix en 3 archivos coordinados: (1) `discovery-governor.md` genera el `tenant_id` al construir el Sprint Contract (derivado de la razón social del brief) y lo persiste en `harness-state.json`; (2) `discovery-analyst.md` nuevo Paso 2 lee `harness-state.json` y extrae el campo — bloquea si está vacío; (3) `discovery-configurator.md` DRAFT Paso 3 lee `harness-state.json` en lugar de generar. DEC-047 registrada.
- **T-138** — `discovery-configurator.md` DRAFT Paso 2: agrega `synthesis_report.json` como tercer artefacto de entrada. Paso 5 (`client_profile.json`): instrucción explícita de copiar `criterios_exito` textualmente desde `synthesis_report.campos_consolidados.criterios_exito.valor` — sin resumir ni parafrasear.
- **T-145** — Schema ampliado de `onboarding_config.json` diseñado: 6 secciones (`ingesta`, `pronostico`, `canales_entrega`, `alertas`, `estado_datos_erp`, `esquema2`) con estructura y fuente de cada campo documentados.
- **T-139** — `discovery-configurator.md` DRAFT Paso 6 reemplazado: reglas de población explícitas por cada sección del `onboarding_config.json` expandido. Incluye inferencia de canales por perfil cuando no hay datos explícitos, derivación de alertas desde `criterios_exito`, extracción de datos ERP desde notas del stakeholder técnico en `synthesis_report`.
- **DEC-047** — El governor es el único generador del `tenant_id`. Registrado en `decisions.md`.

**Qué cambió en sesión 19:**
- **T-129** — Completada. Test_002B ejecutada en `Test_002B_Laboratorio`. APPROVED score 0.93.
- **Revisión post-prueba** — Análisis completo de todos los artefactos generados. Comportamiento documentado.
- **T-140 a T-145** — 6 nuevos bugs identificados en revisión post-Test_002B.
- **LEC-045 a LEC-047** — 3 nuevas lecciones: ruta canónica del evento, brecha entre "implementado" y comportamiento real, pre-registro de escalamientos.

**Qué cambió en sesión 18:**
- **T-135** — Parámetro `-Dev` implementado en `deploy-harness.ps1`: junctions para `.claude/agents/` y `.claude/skills/` en lugar de copias.
- **Commands eliminados del deploy** — Se detectó duplicación: `faro-setup.ps1` ya instala los commands globalmente vía junction. El `deploy-harness.ps1` ya no copia ni junctionea `.claude/commands/`. Responsabilidad exclusiva de `faro-setup.ps1`.
- **README.md creado** — Guía completa para nuevos operadores: setup por máquina, deploy, flujo completo, comandos, estructura de carpetas.
- **T-129 relanzada como Test_002B** — Prueba ejecutada en `Test_002B_Laboratorio`. Todos los workers completaron. Harness suspendido en CP-03 por límite de tokens de 5h.
- **T-136–T-139** — 4 bugs registrados para corregir después de completar T-129.

**Qué cambió en sesión 17:**
- **T-130** — Corregidas rutas de `session_notes.json`, `stakeholder_map.json`, `synthesis_report.json` y `open_questions.json` en 7 archivos: los agentes escribían en `010_discovery/` en lugar de `010_discovery/support/` (LEC-039). Afectados: `discovery-interviewer.md`, `discovery-synthesizer.md`, `discovery-governor.md`, `flows/010_discovery_flow.md`, `commands/faro-save.md`, `discovery-synthesis-schema/SKILL.md`, `discovery-open-questions/SKILL.md`.
- **T-131** — Agregado paso explícito en `discovery-interviewer.md` para marcar el stakeholder como `"en_curso"` en `stakeholder_map.json` al iniciar su sesión (antes solo lo marcaba `"completada"` al terminar).
- **T-132** — Corregido Sprint Contract del governor: ahora lee `800_inputs/brief.md` antes de construir el contrato, eliminados campos "Contrato firmado" y "Fecha de firma" que no existen en Discovery, "Categoría comercial" cambiada a "por determinar" (LEC-040).
- **T-133** — Cambiado comportamiento del interviewer: presenta todas las preguntas del bloque de una vez (DEC-045) y guarda `session_notes.json` inmediatamente al recibir las respuestas, en lugar del modelo conversacional pregunta-a-pregunta.
- **T-134** — Corregido `deploy-harness.ps1`: ahora copia `commands/*.md` a `.claude/commands/` del proyecto destino (LEC-041). Antes los commands solo existían globalmente vía junction de `faro-setup.ps1`.
- **DEC-045** — Interviewer en modo bloque completo de una vez.
- **DEC-046** — Decisión de agregar parámetro `-Dev` al deploy (junctions en lugar de copias para desarrollo).
- **LEC-039, LEC-040, LEC-041** — Tres nuevas lecciones de la prueba T-129.
- **T-135** — Implementado parámetro `-Dev` en `deploy-harness.ps1`: crea junctions para `.claude/agents/`, `.claude/skills/` y `.claude/commands/` apuntando al repo; maneja reemplazo correcto de junctions previas.

**Qué cambió en sesión 16:**
- **DEC-044** — Nueva convención de nombres para carpetas de datos/salidas del proyecto cliente: `bronze/` → `1000_data/005_bronze/`, `silver/` → `1000_data/007_silver/`, `gold/` → `1000_data/009_gold/`, `models/` → `1010_models/`, `forecasts/` → `1020_forecasts/`, `exports/` → `1030_exports/`.
- **T-127** — Ya estaba corregida desde sesión 15 (`tenant_id` correcto en `analysis_report.json`).
- **T-128** — `discovery-configurator.md` actualizado: carpetas del `storage_local` usan la nueva convención DEC-044.
- **T-126** — `discovery-orchestrator.md` corregido: la secuencia en modo PLAN ahora es `[interviewer → synthesizer → analyst → configurator]`. Descripción del CP-01 actualizada: lo registra el synthesizer, no el interviewer.
- **T-120 a T-124** — Reorganización de subcarpetas `deliverables/` y `support/` implementada en 6 archivos: `discovery-configurator.md`, `discovery-analyst.md`, `discovery-evaluator.md`, `discovery-governor.md`, `discovery-synthesizer.md` y `deploy-harness.ps1`. Rutas actualizadas:
  - `010_discovery/deliverables/` ← `client_profile.json`, `onboarding_config.json`, `data_intake_guide.md`
  - `010_discovery/support/` ← `session_data.json`, `analysis_report.json`
  - `600_persistence/pending_email.json` ← antes `010_discovery/correo_pendiente.json`
- **T-125** — Descartada como inválida: la suspensión durante T-092 fue manual por límite de tokens de 5h de Claude Code, no un bug del governor. LEC-037 corregida para reflejar el diagnóstico real.

**Qué cambió en sesión 15:**
- **T-092** — Prueba de humo completada con cliente ficticio Distribuidora Nutrivalle S.A. de C.V. (Guadalajara, México). Veredicto APPROVED, score 0.93/1.0. Tenant `distribuidora-nutrivalle-001` configurado como categoría L, plan trimestral, USD 322/mes.
- **DEC-042** — Reorganización de carpetas dentro de `010_discovery/`: `deliverables/` para artefactos finales (`client_profile.json`, `onboarding_config.json`, `data_intake_guide.md`) y `support/` para artefactos de trabajo interno (`session_notes.json`, `stakeholder_map.json`, `synthesis_report.json`, `open_questions.json`, `session_data.json`, `analysis_report.json`). `db_records/` y `storage_local/` se quedan donde están.
- **DEC-043** — `correo_pendiente.json` se renombra a `pending_email.json` (bug de convención: nombre en español) y se mueve a `600_persistence/`.
- **LEC-037** — Un campo bloqueante del synthesizer no debe suspender el harness — debe pedir segunda ronda acotada. La suspensión ocurrió por `plan_suscripcion` (resoluble con una pregunta), que es incorrecto.
- **LEC-038** — El orchestrator debe inicializarse con la cadena de workers actual incluyendo el synthesizer. El `execution-state.json` mostraba la cadena vieja `[interviewer → analyst → configurator]` sin el synthesizer.
- **T-120 a T-127** — Tareas creadas para implementar en sesión 16.

**Qué cambió en sesión 14:**
- **T-115** — `faro-setup.ps1`: el mecanismo de copia de comandos fue reemplazado por un junction `~/.claude/commands/` → `commands/` del repo. Cualquier nuevo comando FARO es visible automáticamente sin re-ejecutar el setup.
- **T-118** — `deploy-harness.ps1`: `brief_template.md` ahora se deploya como `brief.md` en `800_inputs/`. El mensaje de advertencia final también fue actualizado.
- **T-116** — `discovery-interviewer.md`: Paso 2 reforzado con extracción explícita del brief en contexto y regla crítica de no preguntar lo que ya está respondido.
- **T-117** — `discovery-interviewer.md`: guardado incremental convertido en punto de parada obligatorio de 8 pasos — el agente no puede avanzar al siguiente bloque hasta haber escrito el archivo.
- **T-113** — `discovery-governor.md`: Sprint Contract expandido con tabla descriptiva de los 5 checkpoints (quién registra, qué valida, qué artefacto).
- **T-114** — `discovery-governor.md`: Sprint Contract expandido con secciones **Entradas** y **Salidas** del harness.
- **T-119** — `discovery-governor.md` + `deploy-harness.ps1`: Sprint Contract persiste en `700_contract/sc_010_discovery.md`. El governor escribe el contrato primero como BORRADOR y lo marca APROBADO al confirmarlo el operador. harness-state.json almacena solo el path y el estado (DEC-041). La carpeta `700_contract/` se crea en E10-A y en el deploy.

**Qué cambió en sesión 12:**
- **T-111** — `discovery-interviewer.md` actualizado con guardado incremental: nueva sección "Guardado incremental por bloque", campos `estado`/`bloques_guardados`/`fecha_ultima_actualizacion` en cada entrada de `session_notes.json`, sección de cierre simplificada a solo marcar `completada` y agregar snowball.
- **T-112** — Comando `/faro-save` creado en `commands/faro-save.md`. Válvula de emergencia para guardar estado parcial a mitad de un bloque. Distingue tres estados: `parcial` (faro-save), `en_curso` (automático por bloque), `completada` (cierre de sesión).
- **T-110** — `flows/010_discovery_flow.md` completamente actualizado: tabla de actores con W2 synthesizer y W3/W4 renumerados; árbol de archivos con `800_inputs/`, `session_notes.json`, `stakeholder_map.json`, `synthesis_report.json`, `open_questions.json`; diagrama ASCII con N sesiones multi-stakeholder, segunda ronda condicional y CP-01 movido al synthesizer; sección EXECUTE renombrada a "cuatro workers"; tabla de checkpoints actualizada; escalaciones ampliadas a 4 casos; resumen visual actualizado.
- **Rename `inputs/` → `800_inputs/`** — Carpeta renombrada en: `deploy-harness.ps1`, `discovery-interviewer.md`, `flows/010_discovery_flow.md`, `brief_template.md`. DEC-037 actualizada. El prefijo numérico ubica la carpeta al final de la estructura y mantiene consistencia con la convención `6XX_*` del proyecto.
- **Skills renombradas a prefijo `discovery-*`** — `synthesis-report-schema` → `discovery-synthesis-schema` y `open-questions-schema` → `discovery-open-questions`. Causa: el deploy script usa filtro `"discovery-*"` — las skills sin ese prefijo nunca llegaban al proyecto cliente. DEC-039 registrada. Directorios renombrados, SKILL.md actualizados, referencias en `discovery-synthesizer.md` actualizadas.
- **`templates/client-project-CLAUDE.md` comprimido** — De 352 líneas a ~75. El árbol de decisión con 11 bloques de handoff idénticos fue reemplazado por un patrón genérico con tabla de referencia. Toda la lógica se mantiene, solo se eliminó la repetición.

**Qué cambió en sesión 11 (T-109):**
- `discovery-governor.md` Modo EXECUTE actualizado: cadena interviewer → synthesizer → analyst → configurator DRAFT.
- Paso 3 (interviewer): verificación cambia de `session_data.json` a `session_notes.json` + `stakeholder_map.json`. Ya no registra CP-01.
- Nuevo Paso 4 (synthesizer): invoca `discovery-synthesizer` vía CLI; si retorna `SEGUNDA_RONDA_REQUERIDA` devuelve `INTERVIEWER_REQUIRED` con `interviewer_mode: COMPLEMENTARIO` y lista de `campos_bloqueantes`; si `COMPLETE` registra CP-01.
- Pasos renumerados: analyst → Paso 5 (Worker 3), configurator DRAFT → Paso 6 (Worker 4).
- E10-B: nueva verificación previa `SYNTHESIZER_PENDING` para el estado "session_notes.json existe pero session_data.json no" (interviewer corrió, synthesizer no).
- Frontmatter del governor: `discovery-synthesizer` agregado al campo `agents:`.
- Tabla SUSPEND: CP-01 actualizado a "Synthesizer completo, analyst pendiente".
- Sprint Contract template: workers actualizados a 4 en orden correcto.
- LEC-030 registrada: checkpoints deben moverse con el worker final del tramo.

**Qué cambió en sesión 10:**
- `discovery-interviewer` rediseñado: conduce entrevistas por rol (negocio/técnico/usuario), maneja cola de stakeholders, snowball, produce `session_notes.json` + `stakeholder_map.json`. Modo COMPLEMENTARIO para segunda ronda.
- Nuevo agente `discovery-synthesizer`: cross-referencia entrevistas, detecta contradicciones, consolida campos, clasifica brechas (bloqueante/importante/registrable), produce `synthesis_report.json` + `open_questions.json` + `session_data.json` derivado.
- Nuevas skills `synthesis-report-schema` y `open-questions-schema` con schemas completos y ejemplos.
- `session_data_schema.json` y skill `discovery-session-schema` actualizados: escritor cambia de interviewer a synthesizer.
- `discovery-governor.md` corregido: nueva verificación previa en E10-B para el caso `ACTIVE + null checkpoint + escalations` → retorna `RESUME_AFTER_ESCALATION`.
- `deploy-harness.ps1` actualizado: crea `inputs/` y deposita `brief_template.md` al deployar harness 010.
- Tres plantillas de preguntas por rol creadas en `templates/010_discovery/`.
- `brief_template.md` creado en `templates/010_discovery/`.

### Estado de agentes (.claude/agents/)

| Archivo | Estado | Descripción |
|---------|--------|-------------|
| `discovery-orchestrator.md` | ✅ completo | Gestor de estado puro — modos PLAN/CHECKPOINT/WORKER_FAILED |
| `discovery-evaluator.md` | ✅ completo | Instancia C — carga skill `discovery-rubric`, evalúa 7 dimensiones |
| `discovery-interviewer.md` | ✅ completo | Multi-stakeholder, roles, snowball, guardado incremental por bloque, modo COMPLEMENTARIO |
| `discovery-synthesizer.md` | ✅ completo | Cross-referencia entrevistas, detecta contradicciones, produce `synthesis_report.json` + `open_questions.json` + `session_data.json` |
| `discovery-analyst.md` | ✅ completo | Calcula ITO normalizado (0–100), confirma M/L/XL, asigna nivel cold start |
| `discovery-configurator.md` | ✅ completo | Modos DRAFT y COMMIT — genera artefactos, registros BD, Storage, guía, evento |
| `discovery-governor.md` | ✅ completo | E10-B corregido; Modo EXECUTE con cadena interviewer → synthesizer → analyst → configurator |

### Estado de skills (.claude/skills/)

| Directorio | Estado | Descripción |
|-----------|--------|-------------|
| `discovery-state-schema/` | ✅ completo | Schemas de harness-state.json y execution-state.json |
| `discovery-session-schema/` | ✅ completo | Schema de session_data.json — escritor: synthesizer |
| `discovery-analysis-schema/` | ✅ completo | Schema de analysis_report.json con ITO, categoría y cold start |
| `discovery-rubric/` | ✅ completo | Rúbrica 7 dimensiones con anclas few-shot y reglas de veto |
| `discovery-knowledge-schema/` | ✅ completo | Schemas de decisions_library.md y lessons_learned.md |
| `discovery-synthesis-schema/` | ✅ completo | Schema de synthesis_report.json — renombrado de synthesis-report-schema (DEC-039) |
| `discovery-open-questions/` | ✅ completo | Schema de open_questions.json — renombrado de open-questions-schema (DEC-039) |

### Estado del harness 010 — construcción completa, todos los gaps cerrados

Los componentes principales están construidos. `deploy-harness.ps1 -Harness 010 -Destino <dir>` entrega:

| Componente | Path en destino |
|------------|----------------|
| 6 agentes discovery-* | `.claude/agents/` |
| 5 skills discovery-* | `.claude/skills/` |
| `session_template.md` | `010_discovery/` |
| `ito_calculator.py` | `010_discovery/` |
| `cold_start_evaluator.py` | `010_discovery/` |
| `data_intake_guide_template.md` | `010_discovery/templates/` |
| `data_intake_guide_esquema2_block.md` | `010_discovery/templates/` |
| `client-project-CLAUDE.md` | `CLAUDE.md` (raíz del proyecto cliente) |
| `client-project-settings.json` | `.claude/settings.json` |

**Gaps activos (bloquean cierre del harness):**

| # | Gap | Tarea | Estado |
|---|-----|-------|--------|
| 1 | Bug en governor: `$env:FARO_DEPLOY_SCRIPT` → `$env:HARNESS_DEPLOY_SCRIPT` | T-096 | ✅ cerrado |
| 2 | `client-project-CLAUDE.md` referenciaba `workflows/` inexistentes — creado `ciclo_010_discovery.md` | T-097 | ✅ cerrado |
| 3 | `templates/default_stacks.md` no existe — sección eliminada del deploy (redundante) | T-098 | ✅ descartada |
| 4 | `decisions_library.md` inicial sin mecanismo de creación — agregado E10-A.8 al governor | T-099 | ✅ cerrado |
| 5 | Schemas JSON deployables no existen como archivos (solo en skills) | T-100 | ✅ cerrado |
| 6 | Interviewer rediseñado, synthesizer creado, skills y schemas actualizados | T-101 a T-108 | ✅ cerrado |
| 7 | Brecha en tabla E10-B: caso ESCALATION_REQUIRED + null checkpoint no cubierto | T-106 | ✅ cerrado |
| 8 | Governor Modo EXECUTE no refleja la nueva cadena (interviewer → synthesizer → analyst) | T-109 | ✅ cerrado |
| 9 | `flows/010_discovery_flow.md` no refleja la nueva arquitectura multi-stakeholder | T-110 | ✅ cerrado |
| 10 | Skills `synthesis-report-schema` y `open-questions-schema` no llegaban al proyecto cliente por filtro del deploy | DEC-039 | ✅ cerrado |
| 11 | Gaps de prueba de humo: interviewer no leía brief, guardado incremental no ocurría, brief con nombre incorrecto, Sprint Contract incompleto, faro-save no disponible | T-113 a T-119 | ✅ cerrado |
| 12 | Prueba de humo con cliente ficticio — re-ejecución desde cero pendiente | T-092 | **pendiente** |

### Decisión de diseño importante — ITO normalizado

El `discovery-analyst` usa una escala normalizada 0–100 (no valores crudos). Los umbrales son M ≤ 33, L ≤ 66, XL > 66. El evaluador original tenía umbrales incorrectos (ITO ≤ 1500, etc.) — ya fueron corregidos en la sesión 3. Todos los agentes y skills ahora son consistentes en esta escala. Los pesos y referencias máximas son provisionales hasta T-030.

---

## Lo que está completamente definido

### Modelo de negocio (DEC-001)
- **Service as a Software** — Triple S opera todo, el cliente solo consume resultados
- El cliente no configura ni opera el software — dashboard de solo lectura

### Precios y planes (DEC-002, DEC-016)
- Tres categorías: **M** (USD 200), **L** (USD 350), **XL** (USD 500) por mes
- Clasificación por **Índice de Tamaño Operativo (ITO)**: productos activos + clientes atendidos + volumen de pedidos — pesos y umbrales pendientes de calibrar con datos piloto (T-030)
- Tres planes: **Mensual** (sin dto.), **Trimestral** (8% dto.), **Anual** (18% dto.) — descuentos fijos, sin reembolsos
- Cargo adicional por complejidad de datos: **+0%** (ISD ≥ 95%), **+20%** (ISD 70–94%), **+50%** (ISD 50–69%), **+80%** (ISD < 50%)

### Ciclo de pagos y suspensión (DEC-003)
- 30 días de servicio por pago
- Alertas: verde no fijo (días 2, 3) → verde fijo (día 5) → amarillo fijo (días 6, 7, 8) → suspensión (día 9+)
- Correo al responsable del cliente desde el día 2
- Atraso ≤ 2 días → conserva fecha original / Atraso ≥ 3 días → nueva fecha = pago + 30 días
- Pasarela de pagos: **Stripe** — proveedor por confirmar (T-031)
- Ciclo de vida del cliente: Prospecto → Onboarding → Activo → En mora → Suspendido → Reactivado/Cancelado

### Onboarding (DEC-004)
- **Mes 1 gratuito**: ingesta de datos, diagnóstico de salud, construcción de confianza
- Mes 2: primer pago
- Máximo mes 3: primer pronóstico entregado
- El mes 1 gratuito es el piloto — no hay piloto separado

### Datos — arquitectura medallón (DEC-005, DEC-012, DEC-014)
- Datos originales del cliente: **intocables**
- Tres capas: **Bronce** (copia exacta) → **Plata** (limpieza y normalización) → **Oro** (listo para modelos)
- Agentes de IA operan solo sobre capa Oro
- **Dos modos de ingesta:**
  - Modo Batch: archivo histórico completo, una sola vez
  - Modo Incremental: actualizaciones periódicas (diario/semanal), deduplicación automática, reentrenamiento semanal
- **Dos esquemas de datos:**
  - Esquema 1 (obligatorio): historial de pedidos — 4 campos mínimos, 17 campos ideales
  - Esquema 2 (opcional): producción e inventario de ABC — 6 campos para análisis de agotados y desperdicios

### Índice de Salud de Datos — ISD (DEC-015)
- **6 dimensiones ponderadas:** Completitud (25%), Consistencia (20%), Continuidad (20%), Unicidad (15%), Cobertura temporal (10%), Exactitud (10%)
- Resultado: 0–100%. Meta: ≥ 95%
- Presentación: mensual junto con el pronóstico + recálculo inmediato ante cada actualización de datos
- Maestro de datos: construido y mantenido por Triple S automáticamente (DEC-017)

### Estrategia cold start y historial (DEC-013)
- Mínimo recomendado: 2 años. Ideal: 3 años
- Historial variable por combinación cliente × producto — niveles de confianza ajustados
- Cascada cold start: (1) analogía por categoría → (2) analogía por cliente → (3) acumulación 3 meses

### Entrega de resultados (DEC-007)
- Dashboard de solo lectura (canal principal)
- Correo automático al publicar pronóstico
- Archivo exportable Excel/CSV desde el dashboard
- Sin API pública

### SLAs (DEC-009)
- Pronóstico: primeros 5 días hábiles del mes
- MAPE: ≤ 15% (ISD ≥ 95%) / ≤ 25% (ISD 70–94%) / sin garantía (ISD < 70%)
- Dashboard: 99% mensual
- Incidente crítico: respuesta 4h / resolución 24h hábiles
- Latencia dashboard: < 3s / procesamiento datos: < 24h / recálculo ISD: < 4h / correo: < 1h

### Retención de datos al cancelar (DEC-010)
- 6 meses de retención total
- Exportación (solo pronósticos): ventana 3 meses, entrega máximo 3 meses después
- Eliminación bloqueada si hay exportación pendiente de confirmación

### Alcance del pronóstico (DEC-018)
- Horizonte: variable por cliente (días, semanas, meses, múltiples meses)
- Niveles de producto: SKU + agregado por categoría/subcategoría (simultáneos)
- Niveles de cliente: por sede + cliente consolidado (simultáneos)
- Jerarquía geográfica: flexible y parcial — opera con los niveles disponibles

### Patrones de pedido (DEC-019)
- Estacionalidad: detectada en mes 1 de onboarding, puede o no existir
- Señales anticipadas de XYZn: generalmente no existen — modelo construido solo con historial
- Mínimos contractuales: algunos clientes los tienen, no siempre se cumplen
- Pedidos atípicos: detectados por desviación estadística, clasificados como legítimos o anomalías

### Stack tecnológico (DEC-020, DEC-021)
- **Fase 1:** Excel/CSV
- **Fase 2:** Streamlit
- **Fase 3:** Python + FastAPI + Supabase (Auth + PostgreSQL + Storage) + DuckDB + Prefect + Stripe + SendGrid + Docker + Railway
- Aislamiento multi-tenant: RLS en PostgreSQL + carpetas por tenant en Supabase Storage + DuckDB por cliente

### Unidad mínima de análisis (DEC-011)
- Combinación **cliente × producto** — no el cliente ni el producto por separado
- Cada par tiene su propia frecuencia de pedido y tiempo de entrega

---

## Decisiones registradas: DEC-001 a DEC-034

Ver `decisions.md` para detalle completo de cada decisión.

---

## Preguntas abiertas pendientes

### Bloque 2.8 — Integración y Operaciones (T-029) — una pregunta pendiente
- **[PENDIENTE]** ¿Se requiere aprobación humana (human-in-the-loop) antes de publicar un pronóstico? Opciones A (automático), B (manual siempre), C (híbrido por confianza). Opción C recomendada para Fase 3; Opción B para Fase 1.

### Pendientes adicionales
- T-030: Calibrar pesos (w1, w2, w3) y umbrales del ITO para clasificación M/L/XL
- T-031: Confirmar proveedor de pasarela de pagos (Stripe es la propuesta)

---

## Arquitectura de harnesses operacionales (DEC-024)

```
010 Discovery   → contexto del cliente, criterios de éxito (semi-humano)
015 Intake      → recepción y validación de datos, copia Bronze
020 Diagnosis   → ISD desde Bronze (paralelo con 025)
025 Refinery    → limpieza Bronze→Silver→Gold + maestros
030 Trainer     → feature engineering + entrenamiento de modelos
035 Predictor   → inferencia mensual + anomalías
040 Publisher   → dashboard + correo + exportable
045 Monitor     → MAPE real, deriva de modelos, salud del pipeline
050 Lifecycle   → ciclo de vida del cliente, pagos (event-driven)
055 Command     → operaciones internas Triple S, 6 KPIs (event-driven)
060 Simulator   → escenarios what-if predefinidos (on-demand)
```

Cadena de dependencias operacionales: `015 → { 020 ∥ 025 } → 030 → 035 → 040`

## Orden de construcción (DEC-026)

| Pos | Harness | Bloque | Hito |
|-----|---------|--------|------|
| 1 | 010 Discovery | A | Primer piloto ejecutable |
| 2 | 015 Intake | A | ↑ |
| 3 | 020 Diagnosis | A | ↑ |
| 4 | 050 Lifecycle | C | Listo para cobrar |
| 5 | 025 Refinery | B | Ciclo de valor completo |
| 6 | 030 Trainer | B | ↑ |
| 7 | 035 Predictor | B | ↑ |
| 8 | 040 Publisher | B | ↑ |
| 9 | 045 Monitor | D | Excelencia operativa |
| 10 | 055 Command | D | ↑ |
| 11 | 060 Simulator | E | Funcionalidad avanzada |

## Lo que está documentado en harnesses/

Todos los harnesses tienen documentación completa de entradas, procesos y salidas (T-046 a T-057):

| Harness | Archivo | Procesos documentados |
|---------|---------|----------------------|
| 010 Discovery | `010_discovery.md` | 7 procesos — sesión con cliente, ITO, cold start, configuración, guía de datos, registro, Storage |
| 015 Intake | `015_intake.md` | 8 procesos — recepción, validación, tipos, duplicados, rango, Bronze, reporte, evento |
| 020 Diagnosis | `020_diagnosis.md` | 12 procesos — 6 dimensiones ISD, cálculo global, problema principal, reporte JSON+PDF, BD, evento |
| 025 Refinery | `025_refinery.md` | 14 procesos — Silver (normalización, maestros, deduplicación) + Gold (series de tiempo, cold start, cruce Esquema 2) |
| 030 Trainer | `030_trainer.md` | 9 procesos — clasificación por estrategia, feature engineering, holdout, LightGBM, cold start cascade, serialización |
| 035 Predictor | `035_predictor.md` | 10 procesos — inferencia, 4 niveles jerárquicos, detección anomalías, clasificación, explicabilidad, artefactos |
| 040 Publisher | `040_publisher.md` | 8 procesos — 5 vistas por rol, ISD dashboard, correo SendGrid, exportable Excel+CSV, SLA |
| 050 Lifecycle | `050_lifecycle.md` | 11 procesos — onboarding, cálculo monto, factura Stripe, pago, alertas 9 niveles, suspensión, reactivación, cancelación, exportación, eliminación |
| 045 Monitor | `045_monitor.md` | 9 procesos — MAPE real, descomposición error, drift detection, salud pipeline, frescura datos, 6 KPIs, reporte, portal, alertas |
| 055 Command | `055_command.md` | 9 procesos — vista global, ficha cliente, ops gestión, ops pipeline, conflictos maestros, eventos registry, ops modelos, dashboard KPIs, command_log |
| 060 Simulator | `060_simulator.md` | 8 procesos — 5 escenarios estándar, ventanas modificadas, inferencia, agregación, delta vs. oficial, narrativa, artefactos, evento |

## Próximas acciones para el siguiente agente

### Sesión 22 — Correcciones de infraestructura implementadas

| # | Archivo | Cambio | Tarea |
|---|---|---|---|
| 1 | `deploy-harness.ps1` | En modo normal, antes de crear directorios de destino, verifica si `$destinoAgentes` / `$destinoSkills` son junctions — si lo son, elimina solo el link (`Remove-Item -Force` sin `-Recurse`) antes de crear el directorio real. Evita borrar archivos del repo a través de junctions. | T-146 ✅ |
| 2 | `faro-setup.ps1` | Agregados dos bloques al final: junctions `~/.claude/agents/` → `repo/.claude/agents/` y `~/.claude/skills/` → `repo/.claude/skills/`. Misma lógica de backup que ya existe para commands: backup de archivos no-FARO, elimina dir existente, crea junction. | T-147 ✅ |

### PASO 1 — INMEDIATO: Completar correcciones de infraestructura (T-148 → T-150) y prueba T-003

**Estado:** T-146 y T-147 completadas. Quedan T-148, T-149, T-150 antes de poder ejecutar la prueba.

**Orden obligatorio:**

1. **T-148** — `discovery-governor.md` Ritual E10-A: si `800_inputs/brief.md` no existe → leer `~/.faro/faro.config.json` para obtener `faro_home`, crear `800_inputs/`, copiar `$faro_home/templates/010_discovery/brief_template.md` → `800_inputs/brief.md`, retornar `INIT_PAUSED` con instrucción "Completa el brief y vuelve a ejecutar /faro-init". En lugar del actual `INIT_FAILED`.

2. **T-149** — Restaurar `.claude/agents/` y `.claude/skills/` del repo copiando desde `C:\Users\USUARIO\Documents\Triple S\Test_Forecaster\Test_002B_Laboratorio\.claude\`. Esas versiones son pre-sesión-20 — base para re-aplicar los 14 fixes.

3. **T-150** — Re-aplicar los 14 fixes a los archivos restaurados. Sesión 20 (7 fixes): T-136, T-138, T-139, T-140, T-141, T-142, T-145. Sesión 21 (7 fixes): T-137, T-143 (verificada), T-144, mkdir db_records en configurator, 1000_storage_local en configurator+evaluator+rubric, paths pending_email en rubric, DEC-006 en governor.

4. **T-003** — Prueba de humo con Limpro Industrial S.A. de C.V. (León, Guanajuato — productos de limpieza industrial). Brief preparado en `brief.md` en raíz del repo. Objetivo: APPROVED en primera evaluación sin rechazo. Solo ejecutar después de completar T-148 a T-150.

⚠️ **RECORDATORIO:** `.claude/agents/` y `.claude/skills/` del repo siguen vacíos. T-149 es bloqueante para T-150 y T-003.

---

### PASO 2 — HISTÓRICO: Corregir bugs T-136 a T-145 en el harness (todos implementados en sesiones 20-21, pendiente restauración)

**T-129 ya está completada (APPROVED 0.93).** Ahora hay que corregir los 10 bugs identificados en la revisión post-prueba. Orden recomendado por impacto:

**Alta prioridad — bugs que causan rechazo en primera evaluación:**

1. **T-142** — `discovery-governor.md` modo POST_CP04: antes de invocar al evaluador, leer `session_data.json`, identificar campos con valor `MISSING`, y registrar ESC-XXX en `harness-state.json` para cada uno si no existe. Causa: D1 score 0.0 → rechazo en primera evaluación.

2. **T-140** — `discovery-configurator.md` modo COMMIT: el evento debe escribirse en `600_persistence/events/onboarding_discovery_complete.json`. Crear la carpeta `events/` si no existe. Nunca en `010_discovery/deliverables/`. Causa: VETO D7 → rechazo en primera evaluación.

3. **T-136** — `discovery-analyst.md`: al inicio, leer `600_persistence/harness-state.json` y extraer el campo `tenant_id`. Usar ese valor en `analysis_report.json`. Nunca construir ni generar el tenant_id. Causa: inconsistencia GLOBAL → hallazgo major en evaluación.

4. **T-141** — `discovery-configurator.md` modo COMMIT: `pending_email.json` debe escribirse en `600_persistence/pending_email.json`, no en `010_discovery/deliverables/`. Nombre en inglés (DEC-043). T-121 fue marcada implementada pero el comportamiento no se verificó.

**Alta prioridad — calidad del producto entregado:**

5. **T-138** — `discovery-configurator.md` modo DRAFT y COMMIT: campo `criterios_exito` de `client_profile.json` debe copiarse textualmente desde `synthesis_report.json > campos_consolidados.criterios_exito`. No resumir ni parafrasear. Si el synthesizer captura "no repetir diciembre 2025, reducir inventario temporada baja 30%, cambio operativo junta lunes", eso debe aparecer íntegro.

6. **T-145** — Diseñar el schema ampliado de `onboarding_config.json` antes de implementar T-139. El archivo debe tener secciones por dimensión: (a) canales de entrega por perfil de usuario, (b) campos de datos disponibles y ausentes en ERP, (c) horizontes de pronóstico diferenciados, (d) alertas requeridas, (e) modo de ingesta con detalle técnico, (f) contexto de Esquema 2. Definir la estructura primero.

7. **T-139** — `discovery-configurator.md` modo DRAFT y COMMIT: `onboarding_config.json` debe usar el schema diseñado en T-145. El archivo es la entrada del harness 015 — debe tener toda la información técnica necesaria para arrancar la ingesta.

**Media prioridad — comportamientos auxiliares:**

8. **T-137** — `discovery-interviewer.md`: en el paso de cierre de sesión (snowball + confirmación final), marcar el stakeholder como `"completada"` en `session_notes.json[estado]` además de en `stakeholder_map.json`. El estado `"en_curso"` solo corresponde a sesiones activas, no completadas.

9. **T-143** — Verificar con `Grep` en `discovery-synthesizer.md` que la ruta de escritura de `session_data.json` es `010_discovery/support/session_data.json` (no `010_discovery/session_data.json`). En Test_002B el archivo apareció en la raíz — posible gap de T-130.

10. **T-144** — `discovery-governor.md` Modo INIT (E10-A): después de leer `800_inputs/brief.md`, verificar que los campos obligatorios no están vacíos. Si hay campos vacíos, listarlos explícitamente al operador y detener el proceso hasta que se completen. En Test_002B el primer evento fue `INIT_FAILED` porque el brief estaba incompleto, pero el Sprint Contract se generó igual con datos erróneos.

**Después de implementar T-136 a T-145:** ejecutar prueba T-003 en una nueva carpeta de prueba limpia para verificar que el harness corregido obtiene **APPROVED en primera evaluación**.

---

### Sesión 15 — Re-ejecutar prueba de humo T-092 desde cero *(completada)*

**Todos los gaps están corregidos.** La próxima acción es ejecutar la prueba de humo completa.

**Preparación de la carpeta de prueba:**

La carpeta `C:\Users\USUARIO\Documents\Triple S\Test_Forecaster\Test001_Alimentos` tiene estado residual de la prueba anterior (harness-state.json en `PENDING_CONTRACT`, decisions_library.md inicializado, agentes/skills de un deploy anterior). Para una prueba limpia hay dos opciones:

**Opción A (recomendada):** Eliminar todo el contenido de la carpeta y re-deployar desde cero:
```powershell
# Desde el directorio Harness_Forecaster:
Remove-Item "C:\Users\USUARIO\Documents\Triple S\Test_Forecaster\Test001_Alimentos\*" -Recurse -Force
.\deploy-harness.ps1 -Harness 010 -Destino "C:\Users\USUARIO\Documents\Triple S\Test_Forecaster\Test001_Alimentos"
```
Luego completar `800_inputs/brief.md` con los datos de Alimentos Prueba S.A. (los mismos de la prueba anterior).

**Opción B:** Usar la carpeta tal como está y ejecutar `/faro-restart` para retomar desde el punto suspendido.

**Secuencia de la prueba (Opción A — desde cero):**

1. Limpiar carpeta + re-deployar (ver arriba)
2. Completar `800_inputs/brief.md` con datos del cliente ficticio
3. Ejecutar `/faro-init` → governor genera Sprint Contract en `700_contract/sc_010_discovery.md`
4. Revisar el Sprint Contract. Verificar que tiene secciones **Entradas**, **Salidas** y tabla de **Checkpoints**
5. Aprobar el Sprint Contract → `/faro-discovery sprint_contract_approved: true`
6. Verificar que `700_contract/sc_010_discovery.md` cambia a `ESTADO: APROBADO`
7. El governor retorna `INTERVIEWER_REQUIRED` → el operador conduce la entrevista con el interviewer
8. **Verificar durante la entrevista:**
   - El interviewer lee el brief y NO pregunta datos ya provistos (T-116)
   - Al completar cada bloque, muestra `[FARO] Bloque X guardado` y `session_notes.json` existe (T-117)
9. Completar todas las sesiones del mapa de stakeholders → synthesizer → analyst → configurator DRAFT
10. Aprobar CP-03 → configurator COMMIT → evaluator → veredicto APPROVED

**Criterio de éxito de T-092:** Veredicto `APPROVED` del evaluador + todos los artefactos finales presentes + `session_notes.json` con entradas completas por bloque.

### Artefactos creados en sesión 9

| Artefacto | Path | Descripción |
|-----------|------|-------------|
| Schemas JSON deployables | `templates/010_discovery/schemas/session_data_schema.json` | Schema JSON Draft-07 completo del session_data — validaciones, enums, campos bloqueantes |
| Schemas JSON deployables | `templates/010_discovery/schemas/analysis_report_schema.json` | Schema JSON Draft-07 completo del analysis_report — ITO, categoría, cold start, escalamiento |
| Documento de flujo | `flows/010_discovery_flow.md` | Flujo completo del harness 010 con diagrama ASCII, detalle de cada etapa, checkpoints, gates y artefactos finales |
| Subdirectorios en deploy | `deploy-harness.ps1` | Actualizado para copiar subdirectorios de templates (ej: `schemas/`) al proyecto cliente |

### Artefactos creados en sesión 10

| Artefacto | Path | Descripción |
|-----------|------|-------------|
| Brief template | `templates/010_discovery/brief_template.md` | Plantilla que el operador completa antes de lanzar el harness. Se deployea a `inputs/`. |
| Guía rol negocio | `templates/010_discovery/preguntas_rol_negocio.md` | Guía de conversación para rol negocio — problema, ITO, criterios de éxito, plan, snowball. |
| Guía rol técnico | `templates/010_discovery/preguntas_rol_tecnico.md` | Guía de conversación para rol técnico — sistemas, historial, campos, jerarquías, Esquema 2. |
| Guía rol usuario | `templates/010_discovery/preguntas_rol_usuario.md` | Guía de conversación para rol usuario — decisiones, formato, horizonte, fricción actual. |
| Interviewer rediseñado | `.claude/agents/discovery-interviewer.md` | Multi-stakeholder, roles, snowball, modos DISCOVERY y COMPLEMENTARIO. Produce `session_notes.json` + `stakeholder_map.json`. |
| Nuevo agente synthesizer | `.claude/agents/discovery-synthesizer.md` | Cross-referencia entrevistas, consolida 17 campos, produce `synthesis_report.json` + `open_questions.json` + `session_data.json`. |
| Skill synthesis-report | `.claude/skills/synthesis-report-schema/SKILL.md` | Schema de `synthesis_report.json` con campos consolidados, contradicciones y decisión de segunda ronda. |
| Skill open-questions | `.claude/skills/open-questions-schema/SKILL.md` | Schema de `open_questions.json` con categorías bloqueante/importante/registrable y sistema de ciclos. |
| Schema actualizado | `templates/010_discovery/schemas/session_data_schema.json` | Escritor → synthesizer; C-06 agregado; fuentes documentadas. |
| Skill actualizada | `.claude/skills/discovery-session-schema/SKILL.md` | Escritor y descripción actualizados. |
| Governor corregido | `.claude/agents/discovery-governor.md` | Verificación previa E10-B: `ACTIVE + null + escalations` → `RESUME_AFTER_ESCALATION`. |
| Deploy actualizado | `deploy-harness.ps1` | Crea `inputs/` y deposita `brief_template.md` al deployar harness 010. |

### Contexto arquitectónico relevante para la siguiente sesión

- **Workflows como guías de navegación (DEC-033):** `templates/workflows/ciclo_010_discovery.md` existe y se deployea a `.claude/workflows/` en el proyecto cliente. Para harnesses futuros, crear el workflow correspondiente antes de cerrar el harness. El workflow cubre los 5 modos del governor con tabla GOVERNOR_RESULT → acción para el operador.
- **default_stacks.md eliminado (DEC-034):** No existe, no se crea. El stack vive en los agentes. La sección fue removida del `deploy-harness.ps1`.
- **E10-A.8 en el governor:** El ritual de inicio ahora crea `610_knowledge/decisions_library.md` con 7 decisiones de sistema si el archivo no existe. Las decisiones cubren: escala ITO, pesos provisionales, niveles cold start, cascada cold start, esquemas de datos, Fase 1 local, y regla de escalamiento por discrepancia de categoría.

### Briefing para T-081 — discovery-governor.md

El governor es la **Instancia A** del harness. Es el agente que el operador de Triple S
invoca directamente al arrancar el harness. Centraliza todas las decisiones de control.

**Modos de operación:**

| Modo | Disparador | Qué hace |
|------|-----------|----------|
| `INIT` | No existe `harness-state.json` | Ritual E10-A: crea carpetas, inicializa archivos de estado, presenta Sprint Contract al operador, espera aprobación |
| `EXECUTE` | Sprint Contract aprobado o continuación desde CP-01/CP-02 | Spawnea B (orchestrator), luego spawnea workers directamente: interviewer → analyst → configurator DRAFT |
| `POST_CP03` | B reporta DRAFT_COMPLETE | Presenta borradores al operador, espera aprobación (gate CP-03) |
| `POST_CP04` | Operador aprueba borradores | Registra aprobación en harness-state.json, retoma B para que configurator ejecute COMMIT |
| `CLOSE` | B reporta CP-05 completado | Spawnea C (evaluator), lee veredicto, si APPROVED cierra el harness; si REJECTED activa protocolo 12.4 |
| `SUSPEND` | Operador solicita pausa | Persiste estado de reanudación, escribe mensaje de cierre en claude-progress.txt |

**Reglas críticas para el governor:**
- Spawnea workers directamente vía CLI: `$result = "<prompt>" | claude --agent <nombre> --print --dangerously-skip-permissions`
- El interviewer NO puede spawnarse vía CLI (es interactivo) — retornar `INTERVIEWER_REQUIRED` al operador
- Solo escribe en `600_persistence/harness-state.json` y `600_persistence/claude-progress.txt`
- Nunca escribe en `execution-state.json` — eso es exclusivo del orchestrator
- Escala al operador si: campos ITO bloqueantes MISSING, discrepancia crítica M↔XL, historial < 3 meses, fallo irrecuperable en BD/Storage
- Al cierre: escribe en `610_knowledge/decisions_library.md` (DEC-XXX) las decisiones del ciclo

**Skills que debe cargar:**
- `discovery-state-schema` — para leer y escribir harness-state.json correctamente

**Archivos de referencia para escribir el governor:**
- `brief/010_discovery.md` secciones 6.12.1 a 6.12.5 — flujo completo detallado
- `Temporal/` — harnesses anteriores como referencia de patrón de governor
3. **T-081** — `discovery-governor.md` (el más complejo — dejar para el final)
4. **T-088 a T-091** — Templates y scripts Python de soporte
5. **T-092** — Prueba de humo con cliente ficticio

### Patrones obligatorios (DEC-030, DEC-031, LEC-012 a LEC-014)

- El governor spawna workers vía CLI: `$result = $prompt | claude --agent <nombre> --print --dangerously-skip-permissions`
- El orchestrator solo tiene modos PLAN / CHECKPOINT / WORKER_FAILED
- Cada skill es un **directorio** con `SKILL.md` dentro — no un archivo suelto
- `discovery-interviewer` es interactivo — el governor retorna `INTERVIEWER_REQUIRED`
- Consultar `Temporal/` como referencia de patrón antes de escribir cualquier agente nuevo

### Convenciones establecidas para todos los briefs (DEC-027, DEC-028)

**Nombres de archivo:** `{NNN}_{nombre}.md` — sin sufijo `_harness`
- ✓ `010_discovery.md`, `015_intake.md`, `020_diagnosis.md`

**Estructura de carpetas en ejecución:**
```
{NNN}_{nombre}/         ← artefactos de trabajo del harness
600_persistence/        ← harness-state.json (A) · execution-state.json (B) · claude-progress.txt
605_eval/               ← verdict.json · metrics_summary.json  (solo C)
610_knowledge/          ← lessons_learned.md · decisions_library.md
615_changes/            ← CR_XXXX_Descripcion.md  (solo si hay CRs)
```

**Checklist de alineación obligatorio** (LEC-011) — verificar en cada brief:
- [ ] E10-A incluye `git init` + enlace a GitHub remote
- [ ] Single Writer Rule explícita en 2.1
- [ ] Consulta de knowledge base en 12.2 es **obligatoria**, no condicional
- [ ] B notifica a A solo a través del filesystem (no canal directo)
- [ ] C nunca escribe en `600_persistence/harness-state.json`
- [ ] Rutas de `/610_knowledge/` correctas en todo el documento
- [ ] `metrics_summary.json` con estructura completa en Sección 4
- [ ] Protocolo CR en 12.4

### Pendientes de definición (no bloquean los briefs)
- T-029: ¿aprobación humana antes de publicar pronóstico? (opciones A/B/C — recomendación C)
- T-030: pesos w1, w2, w3 y umbrales del ITO para clasificación M/L/XL
- T-031: confirmar Stripe como pasarela de pagos

---

## Archivos clave
- `CLAUDE.md` — directrices generales, reglas de negocio resumidas
- `problem_statement.md` — definición completa del problema con todas las respuestas
- `progress/decisions.md` — decisiones tomadas (DEC-001 a DEC-029)
- `progress/tasks.md` — registro de tareas con estado (T-001 a T-075)
- `progress/lessons.md` — lecciones aprendidas
- `brief/` — Planes de Construcción por harness (blueprints agénticos) — en construcción
- `plan/` — Planes de Trabajo por harness (secuencias de construcción ejecutables)
- `commands/` — Comandos slash FARO (`faro-init`, `faro-discovery`, `faro-restart`, `faro-suspend`, `faro-continue`, `faro-override`)
- `faro-setup.ps1` — instala comandos FARO en la máquina local (ejecutar una vez por máquina)
- `install.ps1` — instalador remoto para máquinas nuevas
- `deploy-harness.ps1` — despliega un harness FARO a un directorio de proyecto cliente
- `harnesses/010_discovery.md` — entradas, procesos, salidas del harness Discovery
- `harnesses/015_intake.md` — entradas, procesos, salidas del harness Intake
- `harnesses/020_diagnosis.md` — entradas, procesos, salidas del harness Diagnosis
- `harnesses/025_refinery.md` — entradas, procesos, salidas del harness Refinery
- `harnesses/030_trainer.md` — entradas, procesos, salidas del harness Trainer
- `harnesses/035_predictor.md` — entradas, procesos, salidas del harness Predictor
- `harnesses/040_publisher.md` — entradas, procesos, salidas del harness Publisher
- `harnesses/050_lifecycle.md` — entradas, procesos, salidas del harness Lifecycle
- `harnesses/045_monitor.md` — entradas, procesos, salidas del harness Monitor
- `harnesses/055_command.md` — entradas, procesos, salidas del harness Command
- `harnesses/060_simulator.md` — entradas, procesos, salidas del harness Simulator
