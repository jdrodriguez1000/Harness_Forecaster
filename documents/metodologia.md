# Metodología Universal para la Construcción de Harnesses

Este documento define el estándar y el proceso para construir sistemas de harnesses que permitan ejecutar proyectos de forma autónoma y controlada, garantizando la calidad y la reducción de la varianza en los resultados.

---

## 1. Fundamentos y Propósito
El objetivo de un harness es reducir el espacio de decisiones probabilísticas de los LLMs, encuadrando su comportamiento mediante contratos, herramientas específicas y evaluación independiente.

### Principios de Ingeniería (P1-P8)
*   **P1: Separación de Roles**: Orquestador, Trabajador y Evaluador deben ser entidades distintas.
*   **P2: Artefactos de Handoff**: La comunicación entre fases se realiza exclusivamente mediante archivos persistentes.
*   **P3: Evaluador Externo Independiente**: Ningún agente evalúa su propio trabajo.
*   **P4: Context Resets**: Se prefiere el reinicio de contexto sobre la compactación para evitar la "ansiedad contextual".
*   **P5: Contratos Explícitos**: Definición de "terminado" antes de iniciar la ejecución.
*   **P6: Escalamiento Proporcional**: Ajuste del esfuerzo (workers, reasoning) según la complejidad.
*   **P7: Herramientas Críticas**: Las herramientas disponibles son tan importantes como el prompt.
*   **P8: Observabilidad**: Trazabilidad total de cada decisión en el filesystem.

### Estándares de Comportamiento (E1-E12)
*   **E1: Persistencia de estado**: El sistema debe poder reanudar el trabajo entre sesiones sin pérdida de contexto.
*   **E2: Context Anxiety**: Protocolo proactivo de reinicio de contexto al alcanzar umbrales de tokens.
*   **E3: Calibración del Evaluador**: Uso de rúbricas y ejemplos few-shot para evitar la lenidad del evaluador.
*   **E4: Mínima Complejidad**: Evolución continua del sistema, evitando sobre-ingeniería inicial.
*   **E5: Ejecución Durable**: Capacidad de reanudar la ejecución desde checkpoints canónicos tras un fallo.
*   **E6: Outputs al Filesystem**: Los agentes escriben resultados directamente al disco, no al orquestador.
*   **E7: Paralelización Explícita**: Ejecución simultánea de tareas independientes para reducir tiempos.
*   **E8: Extended Thinking**: Uso de razonamiento profundo (reasoning) para decisiones críticas y complejas.
*   **E9: Evaluación Temprana**: Validación con muestras pequeñas y representativas en etapas iniciales.
*   **E10: Inicio de Sesión Estructurado**: Ritual obligatorio de lectura de estado y orientación al arrancar.
*   **E11: Búsqueda de Amplio a Estrecho**: Entendimiento del dominio y el problema antes de entrar en detalles técnicos.
*   **E12: Arquitectura Orquestador-Trabajador**: El orquestador planifica y delega; los trabajadores ejecutan.

---

## 2. Arquitectura de Capas
El sistema no es un programa único, sino un "sistema de sistemas" dividido en dos capas para separar el **valor de negocio** de la **ejecución técnica**.

### ¿Por qué dos capas?
1.  **Eliminación de Sesgo**: El ejecutor (Capa 2) no debe ser el mismo que aprueba el alcance (Capa 1).
2.  **Gestión de Contexto**: La Capa 1 mantiene la visión global del proyecto, mientras que la Capa 2 opera con "Contexto Estricto" (E2) para evitar alucinaciones.
3.  **Seguridad**: La Capa 1 actúa como el "GateKeeper" humano-IA, asegurando que ninguna acción técnica ocurra sin alineación estratégica.

### Alineación con los Arneses del Sistema
Los 9 arneses definidos (`010` a `090`) representan las fases del ciclo de vida, orquestadas por la Capa de Gobernanza:

#### Capa 1: Gobernanza (Governance Harness)
*   **Misión**: "¿Estamos construyendo lo correcto?".
*   **Fases Estratégicas**:
    *   `010_discovery`: Captura de intención y objetivos de valor.
    *   `020_specification`: Definición del "Qué" (reglas y contratos de negocio).
    *   `040_planning`: Roadmap, hitos y contratos de iteración.
*   **Métricas**: Eficacia, satisfacción del cliente, valor de negocio (Tipo 2).

#### Capa 2: Ejecución (Execution Harness)
*   **Misión**: "¿Lo estamos construyendo bien?".
*   **Fases Tácticas/Técnicas**:
    *   `030_design`: Arquitectura técnica y desacoplamiento.
    *   `050_iteration`: Gestión de micro-ciclos y backlog táctico.
    *   `060_isolation`: Sandbox y aislamiento de contexto.
    *   `070_execution`: Ciclo TDD (Red-Green-Refactor).
    *   `080_verification`: Integración en el ecosistema y QA final.
    *   `090_deployment`: Entrega continua y monitoreo de salud.
*   **Métricas**: Calidad de código, cobertura de tests, éxito de despliegue (Tipo 1).

---

## 3. El Patrón Universal de Fase
En este sistema, una **Fase** es un bloque lógico de trabajo que representa un hito del proyecto (ej: cada uno de los 9 arneses definidos en `@Harnesses`). Ninguna fase puede considerarse terminada hasta que supere su gate de aprobación correspondiente.

Toda fase, sin excepción, debe implementar la colaboración de **tres instancias independientes** (sesiones de IA con contexto separado) para garantizar la calidad:

### Las Tres Instancias del Patrón
1.  **Instancia A: Gobernanza (Governor)**
    *   **Rol**: Director del Proyecto.
    *   **Responsabilidad**: Define el contrato de la fase, gestiona las señales de bloqueo y toma la decisión final de "Avanzar o Repetir" (GateKeeper). Es el único que escribe el estado global (`harness-state.json`).
2.  **Instancia B: Ejecución (Phase Orchestrator)**
    *   **Rol**: Capataz Técnico.
    *   **Responsabilidad**: Recibe el contrato, descompone el trabajo en micro-tareas y coordina a los **Workers** especializados para producir los artefactos. Escribe el estado técnico (`execution-state.json`).
    *   **Regla crítica (E12)**: Antes de activar cualquier Worker, la Instancia B debe persistir su plan de orquestación completo en la sección `orchestration_plan` de `execution-state.json`. Si el contexto crece durante la ejecución y el agente pierde el hilo, puede releer el plan desde el filesystem sin necesidad de reconstruirlo. Un Worker nunca debe ser activado sin que este plan esté guardado.
3.  **Instancia C: Evaluación (Phase Evaluator)**
    *   **Rol**: Auditor Independiente.
    *   **Responsabilidad**: Actúa con un cerebro fresco (sin contexto de la ejecución). Lee el contrato y los artefactos finales, aplica una rúbrica objetiva y emite un veredicto de aprobación o rechazo con feedback técnico.

### Jerarquía de Control y Llamadas entre Instancias
Las tres instancias no operan como pares; tienen una jerarquía de control estricta que debe respetarse para preservar P1 (Separación de Roles) y P3 (Evaluador Independiente).

```
A (Governor)
│
├──▶ spawea B (Phase Orchestrator)   ← delegación de ejecución
│         │
│         └──▶ spawea Workers (1..N, en paralelo si son independientes)
│                   │
│                   └──▶ escriben artefactos al filesystem
│
└──▶ spawea C (Phase Evaluator)      ← solo después de que B confirma finalización
          │
          └──▶ lee artefactos del filesystem → emite veredicto
```

**Reglas que no pueden violarse:**

*   **A llama a B para ejecutar, y a C para auditar — nunca al mismo tiempo.** El flujo es secuencial: primero B produce, luego C evalúa. A es el único que decide cuándo avanzar de una etapa a la siguiente.
*   **A NO llama a Workers directamente.** Hacerlo mezclaría el dominio estratégico de A con la ejecución táctica, contaminando su contexto y violando P1. B existe precisamente para ser el intermediario técnico que descompone y coordina.
*   **B llama a los Workers — es su responsabilidad exclusiva.** B conoce el contrato técnico y decide cuántos Workers activar, en qué orden y con qué especialización. Antes de activar cualquier Worker, persiste el `orchestration_plan` (ver regla crítica E12 arriba).
*   **C no llama a nadie.** C solo lee artefactos del filesystem. Si C contactara a B o a Workers para "aclarar" algo, perdería la independencia que garantiza P3. Toda la información que C necesita debe estar en los artefactos y en el Sprint Contract.
*   **Cada "llamada" es un agente con contexto fresco.** En la práctica con Claude Code, spawear una instancia significa lanzar un nuevo agente (`Agent` tool) con contexto limpio. Esto implementa P4 (Context Resets) y garantiza que ninguna instancia herede sesgos de las anteriores.

### Los 4 Elementos Internos de la Fase
Para que estas instancias operen, deben existir:
1.  **Sprint Contract**: El acuerdo de lo que significa "terminado", propuesto por A y ratificado por B y C.
2.  **Workers**: Agentes especializados activados por B para el trabajo de dominio.
3.  **Rúbrica de Evaluación**: Los criterios de puntuación (0.0–1.0) que usará la Instancia C. Para evitar lenidad sistémica, toda rúbrica debe incluir obligatoriamente tres elementos:
    *   **a) Dimensiones definidas**: Cada dimensión evaluada debe tener nombre, descripción y peso relativo. Las dimensiones estándar son: *Precisión Factual*, *Completitud*, *Calidad de Fuentes/Referencias* y *Eficiencia de Herramientas*. Un harness puede agregar dimensiones específicas de dominio.
    *   **b) Ejemplos few-shot calibrados**: Al menos 2 ejemplos con desglose de puntaje detallado por dimensión — uno de output aceptable (score global ≥ 0.7) y uno de output rechazado (score global < 0.5). Sin estos ejemplos, el evaluador opera sin referencia y tiende a la aprobación indiscriminada.
    *   **c) Anclas de calibración por nivel**: Definición explícita de qué constituye cada extremo de la escala para cada dimensión:
        *   **1.0** — Criterio cumplido sin observaciones.
        *   **0.5** — Criterio cumplido parcialmente; requiere corrección menor.
        *   **0.0** — Criterio ausente o incumplido; causa de rechazo directo.
4.  **Handoff Artifact**: El resultado tangible que C audita y A aprueba.

---

## 4. Estrategia de Persistencia y Trazabilidad
La "fuente de verdad" reside en el filesystem, no en la memoria de los agentes. Esta arquitectura garantiza que el sistema nunca pierda contexto, incluso entre sesiones o ante fallos.

### 4.1 Los Archivos de Estado (Single Writer Rule)
Para evitar condiciones de carrera, cada archivo tiene un único responsable de escritura:

*   **Harness State (`harness-state.json`)**: 
    *   **Responsable**: **Instancia A (Gobernanza)**.
    *   **Propósito**: Fuente de verdad estratégica, fases y aprobaciones.
*   **Execution State (`execution-state.json`)**:
    *   **Responsable**: **Instancia B (Ejecución)**.
    *   **Propósito**: Control de micro-tareas, uso de workers y estado técnico.
*   **Progress Log (`claude-progress.txt`)**:
    *   **Responsable**: **Orquestador activo** (la instancia que esté ejecutando la tarea en ese momento, ya sea A, B o C).
    *   **Propósito**: Bitácora narrativa de avance.

### 4.2 Regla de Referencias Ligeras (E6)
Cuando un Worker completa su tarea, **reporta al Orquestador (Instancia B) únicamente la referencia** al artefacto producido — el path del archivo o el ID del recurso — nunca el contenido completo.

*   **Por qué**: Pasar contenido completo entre agentes produce el efecto "teléfono descompuesto": cada traspaso degrada la fidelidad de la información, consume tokens innecesariamente y genera cuellos de botella en el orquestador.
*   **Cómo**: B actualiza `execution-state.json` con la referencia (path/ID) y continúa la coordinación. Cualquier instancia que necesite el contenido lo lee directamente del filesystem usando esa referencia.
*   **Aplica a toda la cadena**: Workers → B (solo paths), B → A (solo referencias de estado), C → A (solo path a `/eval/verdict.json`). Ningún agente embebe contenido de artefactos en sus mensajes de reporte.

### 4.3 Artefactos de Memoria y Métricas (Responsabilidades de Cierre) (Responsabilidades de Cierre)
*   **Métricas (`/eval/metrics_summary.json`)**:
    *   **Responsable**: **Instancia C (Evaluación)**. Se genera al finalizar la auditoría de cada fase.
*   **Base de Conocimiento (`/knowledge/decisions_library.md`, `lessons_learned.md`)**:
    *   **Responsable**: **Instancia A (Gobernanza)**. Al finalizar el proyecto, el Gobernador consolida las lecciones y decisiones validadas para integrarlas en la memoria a largo plazo.


### 4.4 Otros Artefactos de Persistencia
*   **Handoff Artifacts**: Documentos o datos específicos generados por una fase que sirven de entrada para la siguiente (ej: BRD, BDD, Código Verificado).
*   **Git History**: Registro inmutable de cambios con una convención de commits estricta para trazabilidad técnica.

---

## 5. Fase 0: Definición Estructural (Contrato del Arnés)
Antes de construir un harness, se debe definir su interfaz:

*   **Entradas (Inputs)**: ¿Qué material "en bruto" recibe?
*   **Propósito (Intent)**: ¿Qué problema específico resuelve?
*   **Procesos**: ¿Qué transformaciones ocurren dentro?
*   **Salidas (Outputs)**: ¿Qué artefactos tangibles produce?

### Estrategia de Exploración para la Definición (E11)
Cuando la definición del contrato requiere recopilar o analizar información de dominio — especialmente en los arneses `010_discovery` y `020_specification`, donde el insumo es la intención del cliente — se debe aplicar la estrategia de búsqueda **de amplio a estrecho**:

1.  **Exploración amplia**: Comenzar con preguntas o búsquedas cortas y abiertas para mapear el espacio de información disponible. El objetivo es detectar qué fuentes, áreas o ángulos existen, no profundizar en ninguno aún.
2.  **Identificación de densidad**: Determinar qué áreas contienen mayor concentración de información relevante para el problema.
3.  **Profundización selectiva**: Solo entonces dirigir preguntas o búsquedas específicas hacia las áreas de mayor densidad.
4.  **No comprometerse prematuramente**: No fijar el plan, la arquitectura ni el Sprint Contract a una sola fuente o enfoque antes de haber explorado la amplitud del espacio. Un compromiso prematuro ciega al agente ante información más relevante que aparece después.

Este patrón aplica tanto a búsquedas de información externa (documentos, APIs, bases de datos) como al análisis interno de requerimientos con el cliente o stakeholder. La Instancia B es responsable de aplicarlo durante la fase de recopilación de insumos; la Instancia A lo supervisa al revisar el Sprint Contract propuesto.

---

## 6. Fase 1: Diseño Agéntico
Definición de la infraestructura necesaria para ejecutar el arnés. En esta fase se deben cerrar los siguientes puntos antes de construir el primer componente:

*   **Roles de Subagentes**: Especialización de los Workers.
*   **Política de Herramientas**: Qué pueden y qué no pueden usar (P7).
*   **Política de Escalamiento**: Configuración de paralelismo y Reasoning Budget (P6, E8).
*   **Checkpoints Canónicos (E5)**: Definición de puntos de control obligatorios donde el sistema guarda estado. Si el proceso falla, se reanuda desde el último checkpoint, no desde cero.
*   **Política de Fallback de Herramientas (E5)**: Para cada herramienta crítica definida en la Política de Herramientas (P7), el harness debe especificar tres niveles de respuesta ante fallo, en este orden:
    1.  **Reintento**: Volver a intentar la operación hasta 2 veces antes de escalar. Los fallos transitorios (timeout, rate limit) se resuelven en este nivel.
    2.  **Fallback**: Si el reintento falla, activar la herramienta o método alternativo previamente definido para esa función (ej: si la búsqueda web falla, usar la base de conocimiento local).
    3.  **Escalamiento**: Si el fallback también falla, **detener la tarea**, registrar el bloqueo en `claude-progress.txt` con el detalle del fallo, y solicitar intervención humana. Nunca improvisar ni continuar con datos parciales o incompletos — un resultado degradado es peor que un bloqueo explícito.
*   **Trigger de Context Reset (E2)**: El Orquestador debe forzar un reinicio de contexto cuando se cumple **cualquiera** de las siguientes condiciones (la que ocurra primero):
    *   **Cuantitativo**: uso de tokens ≥ 70% de la ventana de contexto activa.
    *   **Conductual** (indicador más temprano y confiable): el agente muestra señales de "ansiedad contextual", que se manifiesta como alguno de estos comportamientos — cerrar tareas sin completarlas, omitir pasos del ciclo SDD+TDD, producir respuestas más cortas y superficiales de lo usual, o declarar trabajo como "terminado" sin evidencia de que los criterios de aceptación fueron verificados.
    El criterio conductual es superior al cuantitativo porque emerge antes de alcanzar el umbral de tokens y es una señal directa de degradación de calidad. Ante cualquier duda, priorizar el reset sobre la compactación.

---

## 7. Fase 2: Construcción Iterativa (SDD+TDD)
Este es el motor de ejecución técnica coordinado por la **Instancia B**. Se basa en el principio de que ninguna pieza de trabajo se produce sin una especificación previa y un mecanismo de validación.

### El Ciclo de Vida del Componente
1.  **SPEC (Specifier)**: Define el **Qué**. Transforma el contrato en una especificación técnica o de contenido detallada.
2.  **HUMAN REVIEW**: Punto de control donde el humano aprueba la intención y el alcance de la especificación antes de proceder.
3.  **RED (Tester)**: Define el **Criterio de Éxito**. Escribe las pruebas automáticas o el checklist de aserciones que el resultado debe cumplir.
4.  **GREEN (Executor)**: Define el **Cómo**. Produce el código o contenido mínimo necesario para satisfacer las pruebas/checklist.
5.  **REFACTOR (Optimizer)**: Mejora la estructura, el estilo y la mantenibilidad sin alterar el comportamiento verificado.
6.  **EVAL (Instancia C)**: Auditoría independiente que valida la coherencia entre Spec, Test y Output.

### Adaptación según el tipo de Artefacto
El ciclo SDD+TDD es un modelo mental universal aplicable a cualquier dominio:

| Paso         | Construcción de Código                           | Construcción de Documentos                                         |
| :----------- | :----------------------------------------------- | :----------------------------------------------------------------- |
| **SPEC**     | Define interfaces, tipos y lógica de algoritmos. | Define el índice, los temas clave y objetivos de información.      |
| **RED**      | Escribe un Test Unitario/Integración que falla.  | Crea un **Checklist de Aserciones** (ej: "Debe listar 3 riesgos"). |
| **GREEN**    | Escribe código hasta que el test pasa.           | Redacta el contenido hasta cubrir todos los puntos del checklist.  |
| **REFACTOR** | Limpia el código y aplica patrones de diseño.    | Mejora el estilo, la claridad y el uso del Lenguaje Ubicuo.        |

### Evaluación Temprana (E9)
No esperar a tener el harness completo para evaluar. La evaluación temprana es la intervención de mayor impacto en el ciclo de vida: los ajustes realizados aquí tienen un efecto de **30%–80% en la calidad final** a un costo mínimo comparado con corregir tarde.

**Cuándo activarla:** Al completar el **primer componente funcional** del ciclo SDD+TDD, antes de continuar con el segundo componente.

**Cómo ejecutarla:**
1.  La **Instancia B** selecciona una muestra de **~20 casos representativos** del dominio cubierto por el componente — no casos triviales ni extremos, sino los más frecuentes y críticos para el negocio.
2.  La **Instancia C** evalúa la muestra contra la rúbrica calibrada y produce un mini-veredicto con score por dimensión.
3.  B registra el resultado en `execution-state.json` bajo la sección `early_eval`.
4.  **Si el score es ≥ 0.7**: continuar al segundo componente sin cambios.
5.  **Si el score es < 0.7**: ajustar el Sprint Contract o la especificación del componente **antes** de seguir. Este ajuste no requiere completar la fase; es un punto de corrección temprana.

**Quién decide:** La Instancia B coordina la ejecución; la Instancia C produce el veredicto; la Instancia A decide si el ajuste al Sprint Contract requiere aprobación humana o puede resolverse internamente.

---

## 8. Gobernanza y Métricas
Control de calidad sistémico basado en indicadores cuantitativos y cualitativos. Toda ejecución de fase debe concluir con la generación de un artefacto de métricas.

### 8.1 Gates de Aprobación
*   **Automáticos**: Criterios técnicos medibles definidos en los contratos (ej: coverage, linting, pasar tests).
*   **Humanos**: Decisiones estratégicas, aprobación de hitos de valor y revisiones de impacto.

### 8.2 Estándar de Persistencia: `metrics_summary.json`
Para asegurar la observabilidad, la **Instancia C (Evaluador)** es responsable de generar un archivo `metrics_summary.json` en la carpeta `/eval` de la fase al finalizar su auditoría. Este archivo debe seguir esta estructura mínima:
*   **Pipeline Data**: Timestamps de completitud y cierre de cambios.
*   **Document/Artifact Status**: Versión final, número de revisiones, estado de aprobación y score detallado por rúbrica.
*   **Timeline Metrics**: Tiempos de ciclo entre hitos clave.
*   **Change Requests (CR)**: Registro de peticiones de cambio gestionadas durante la fase.

### 8.3 Métricas Tipo 1: Desempeño del Agente y Tarea (Micro-nivel)
Miden la eficacia de la ejecución de una tarea específica o el desempeño de un agente trabajador.
*   **Eficiencia**: Latencia de tarea y consumo de tokens vs. complejidad.
*   **Calidad**: Score de rúbrica, tasa de rechazo y apego a especificación.

### 8.4 Métricas Tipo 2: Salud y Eficiencia del Sistema (Macro-nivel)
Miden la salud del harness completo y el progreso hacia los objetivos del proyecto.
*   **Salud del Sistema**: Velocidad de Sprint, estabilidad de construcción y trazabilidad documental.
*   **Eficiencia Estratégica**: Valor de negocio/costo, tiempo total de ciclo de fase y efectividad del Gatekeeper.

---

## 9. Estándares de Ingeniería
*   **Convención de Commits**: `tipo(fase/sprint): descripción`.
*   **Estrategia de Ramas**: Ramas por sprint con merge a `main` tras gate aprobado.
*   **Selección de Modelos**: Asignación del modelo adecuado según la tarea (Opus para specs, Sonnet para ejecución).

---

## 10. Evolución del Harness (E4: Mínima Complejidad)
Los harnesses no son estáticos. Su diseño parte del mínimo viable y evoluciona conforme se validan o invalidan las suposiciones sobre las limitaciones del modelo.

### 10.1 Principio de Construcción Mínima
*   El harness se construye inicialmente con el menor número de componentes que satisfagan los contratos de la fase.
*   Cada componente codifica una suposición explícita sobre una limitación del modelo (ej: "sin este evaluador externo, el agente auto-aprueba su trabajo"). Esa suposición debe documentarse al crear el componente.
*   No se agrega un componente sin antes demostrar, mediante evidencia de una ejecución real, que su ausencia degrada la calidad del output.

### 10.2 Ciclo de Re-evaluación Periódica
Al cierre de cada proyecto, la **Instancia A (Gobernanza)** ejecuta el siguiente ciclo antes de consolidar las lecciones aprendidas:

1.  **Inventario**: Listar todos los componentes activos del harness y la suposición que cada uno cubre.
2.  **Prueba de Remoción**: Remover un componente a la vez (en un entorno de prueba) y medir el impacto en la calidad del output usando la rúbrica de la Instancia C.
3.  **Decisión**:
    *   Si la calidad cae: el componente se mantiene y su suposición se refuerza en `decisions_library.md`.
    *   Si la calidad no cae: el componente se elimina del harness y se registra como lección en `lessons_learned.md` (el modelo ya no requiere ese andamiaje).
4.  **Exploración de Nuevas Capacidades**: Verificar si capacidades nuevas del modelo (razonamiento extendido, herramientas adicionales) justifican agregar componentes que antes no existían.

### 10.3 Responsabilidades y Registro
*   **Responsable**: Instancia A, en coordinación con el análisis de cierre de proyecto (Sección 11.3).
*   **Artefacto de salida**: Una entrada en `decisions_library.md` por cada componente evaluado, con estado `MANTENIDO` o `ELIMINADO` y la evidencia que respalda la decisión.
*   **Frecuencia mínima**: Una re-evaluación por proyecto completado; no es opcional.

---

## 11. Memoria a Largo Plazo (Knowledge Base)
La memoria a largo plazo permite al sistema aprender de éxitos y errores pasados, evitando la repetición de fallos y facilitando la reutilización de soluciones arquitectónicas validadas. Reside en la carpeta `/knowledge`.

### 11.1 Estructura de la Memoria
*   **Decisions Library (`decisions_library.md`)**: Registro de decisiones de arquitectura (DA) tomadas en proyectos anteriores. Cada decisión indica su nivel de reutilización (Alta, Media, Baja), la justificación técnica y el contexto de cuándo NO reutilizarla.
*   **Lessons Learned (`lessons_learned.md`)**: Bitácora de errores operativos, hallazgos de evaluación (major/minor) y bloqueos técnicos. Cada lección incluye una "Regla para escritores futuros", una directriz obligatoria para evitar repetir el fallo.
*   **Índices (`_index.md`, etc.)**: Mapas de navegación para consultar rápidamente el histórico por tipo de proyecto, stack técnico o fecha.

### 11.2 Protocolo de Utilización (Consulta)
Es obligatorio que, antes de iniciar cualquier fase de diseño o planificación (especialmente en `020_specification` y `030_design`), la **Instancia B (Ejecución)** realice los siguientes pasos:
1.  **Consulta de Decisión**: Revisar la biblioteca de decisiones para identificar patrones de arquitectura base (DAs de alta reutilización) aplicables al problema actual.
2.  **Consulta de Lecciones**: Revisar `lessons_learned.md` filtrando por el documento o fase que se está por ejecutar.
3.  **Aplicación de Reglas**: Integrar las "Reglas para escritores futuros" identificadas como restricciones inmutables en el Sprint Contract de la fase.

### 11.3 Protocolo de Actualización (Persistencia)
Al cerrar un proyecto, el Orquestador es responsable de:
1.  **Extracción**: Consolidar las DAs aprobadas y las lecciones aprendidas durante la ejecución (incluyendo hallazgos del Evaluador/Instancia C).
2.  **Indexación**: Actualizar los archivos de índice con los metadatos del proyecto cerrado.
3.  **Integración**: Inyectar el conocimiento nuevo en los archivos de la `/knowledge` base para que esté disponible para el siguiente arnés.

## 12. Flujo del Arnés
El ciclo de vida de un arnés es una coreografía sincronizada entre las tres instancias, asegurando trazabilidad y mejora continua mediante persistencia y memoria.

### 12.1 Inicialización (Instancia A)

*   **Entrada**: Humano envía comando "Iniciemos" o "Continuemos". Instancia A es el agente que recibe este comando directamente en la sesión activa de Claude Code.

*   **Determinación del modo**: A verifica si `harness-state.json` existe en el directorio del proyecto:
    *   **No existe** → modo **Inicio** → ejecutar E10-A.
    *   **Existe y está íntegro** → modo **Continuación** → ejecutar E10-B.
    *   **Existe pero está corrupto** → ejecutar `git restore` o `git checkout` sobre el archivo dañado. Si el fallo persiste, detener el flujo y reportar el error en `claude-progress.txt` solicitando intervención humana.

*   **Ritual de arranque**:
    *   *Modo Inicio*: Ejecuta ritual **E10-A** en este orden exacto:
        1. Verificar directorio de trabajo y estado del ambiente (herramientas disponibles, dependencias instaladas).
        2. Crear la jerarquía de carpetas del proyecto.
        3. Inicializar `harness-state.json`, `execution-state.json` y `claude-progress.txt` con sus esquemas vacíos.
        4. Ejecutar `git init` y enlazar inmediatamente el repositorio a un remote en GitHub (`git remote add origin <url>`). Sin este enlace, la trazabilidad (P8) queda en riesgo ante fallos locales.
        5. Ejecutar una prueba básica de sanidad del ambiente (ej: verificar que las herramientas críticas responden).
        6. Registrar el arranque en `claude-progress.txt` con timestamp y estado inicial.
    *   *Modo Continuación*: Ejecuta ritual **E10-B** en este orden exacto:
        1. Verificar directorio de trabajo y estado del ambiente.
        2. Ejecutar `git log --oneline -10` para orientarse en el historial reciente.
        3. Leer `claude-progress.txt` para conocer el estado narrativo de la última sesión.
        4. Cargar `harness-state.json` y revisar el Sprint Contract vigente.
        5. Leer `execution-state.json` para identificar el último checkpoint alcanzado.
        6. Seleccionar la siguiente tarea prioritaria según el backlog registrado en `execution-state.json`.
        7. Ejecutar prueba básica de sanidad del ambiente antes de comenzar a trabajar.

*   **Reporte al humano (obligatorio antes de continuar)**: Al terminar el ritual, A presenta al humano un resumen estructurado con:
    1. **Estado encontrado**: modo detectado (Inicio o Continuación), integridad de archivos, resultado de la prueba de sanidad.
    2. **Sprint Contract propuesto**: en modo Inicio, A redacta el contrato de la fase a ejecutar; en modo Continuación, A muestra el contrato vigente y confirma si sigue siendo válido o requiere ajuste.
    3. **Próxima acción**: qué hará A a continuación una vez aprobado el contrato.
    A no spawea a B hasta recibir aprobación humana explícita del Sprint Contract.

*   **Gate de aprobación humana (P5)**: El humano revisa el Sprint Contract propuesto y responde:
    *   **Aprobado**: A escribe el Sprint Contract en `harness-state.json` y procede a spawear B.
    *   **Ajuste requerido**: A incorpora los cambios, actualiza el contrato y vuelve a presentarlo para aprobación. El ciclo se repite hasta obtener aprobación explícita.
    *   **Cancelación**: A registra la cancelación en `claude-progress.txt` y detiene el flujo.

*   **Delegación a B**: Una vez aprobado el Sprint Contract, A lo escribe en `harness-state.json` y **spawea la Instancia B** pasándole únicamente la referencia al archivo. A no inicia la ejecución técnica por sí mismo ni pasa el contenido del contrato de forma inline.

---

### 12.2 Ejecución Técnica (Instancia B + Workers)

*   **Entrada**: B recibe la referencia al Sprint Contract en `harness-state.json`. Lee el contrato; no recibe contenido inline de A.
*   **Memoria**: Consulta `knowledge/decisions_library.md` y `knowledge/lessons_learned.md` para ajustar el enfoque técnico según lecciones y decisiones previas.
*   **Plan de orquestación**: Antes de activar cualquier Worker, B persiste su plan completo en la sección `orchestration_plan` de `execution-state.json` (regla crítica E12).
*   **Orquestación de Workers**: B spawea los Workers especializados según la naturaleza de la tarea. Workers independientes se ejecutan en paralelo (E7). Cada Worker:
    1. Recibe su micro-tarea con objetivo, formato de salida y herramientas disponibles.
    2. Ejecuta el ciclo SDD+TDD correspondiente.
    3. Escribe su artefacto directamente al filesystem.
    4. Reporta a B **únicamente la referencia** al artefacto (path), nunca el contenido completo (E6).
*   **Estado**: B actualiza `execution-state.json` en cada checkpoint de avance, registrando qué Workers completaron y qué artefactos produjeron.
*   **Cierre de B**: Al finalizar todos los Workers, B actualiza `execution-state.json` con estado `EXECUTION_COMPLETE` y registra el resumen en `claude-progress.txt`. A es notificado a través del estado en el filesystem; no existe canal directo B → A.

---

### 12.3 Auditoría y Gate de Aprobación (Instancia C + Instancia A)

**Paso 1 — Gate intermedio (Instancia A):**
*   A lee `execution-state.json` y verifica que el estado sea `EXECUTION_COMPLETE`.
*   Si B no ha completado, A espera o investiga el bloqueo antes de continuar.
*   Una vez confirmada la completitud, A **spawea la Instancia C** pasándole las referencias al Sprint Contract y a los artefactos producidos (paths). A no pasa contenido inline.

**Paso 2 — Auditoría independiente (Instancia C):**
*   C lee los artefactos directamente del filesystem usando las referencias recibidas.
*   C evalúa contra la rúbrica calibrada (dimensiones, few-shot, anclas).
*   C escribe sus resultados en dos archivos propios — nunca en `harness-state.json`, que es responsabilidad exclusiva de A:
    *   `/eval/metrics_summary.json` — Métricas Tipo 1 y 2.
    *   `/eval/verdict.json` — Veredicto (`APPROVED` / `REJECTED`) con desglose de hallazgos.
*   C registra el cierre en `claude-progress.txt`.

**Paso 3 — Decisión final (Instancia A — GateKeeper):**
*   A lee `/eval/verdict.json`.
*   Toma la decisión **"Avanzar o Repetir"**:
    *   `APPROVED`: A actualiza `harness-state.json` con estado `PHASE_COMPLETE` y notifica al humano que la fase está cerrada.
    *   `REJECTED`: A activa el protocolo de rechazo (ver 12.4).
*   Solo A escribe en `harness-state.json`. C nunca modifica ese archivo.

---

### 12.4 Protocolo de Rechazo y Reintento
Cuando el veredicto de C es `REJECTED`, el flujo entra en estado de **Bloqueo de Fase**:

1.  **Rechazo Técnico (C → filesystem → A → B)**:
    *   **Motivo**: El artefacto no cumple con la rúbrica o los Criterios de Aceptación.
    *   **Flujo correcto**: C escribe el rechazo en `/eval/verdict.json` y `/eval/eval_{artefacto}.json`. A lee el veredicto, actualiza `harness-state.json` a `IN_REWORK` y **spawea B de nuevo** pasándole la referencia al archivo de rechazo. C nunca contacta a B directamente.
    *   **Acción de B**: Lee el informe de rechazo, consulta `lessons_learned.md` para evitar errores previos, y re-ejecuta el ciclo SDD+TDD únicamente para los componentes fallidos.

2.  **Rechazo Estratégico (Humano → A)**:
    *   **Motivo**: El artefacto (o la especificación) no cumple con el objetivo de negocio o requiere un cambio de alcance.
    *   **Acción**: A detiene el flujo, actualiza el `Sprint Contract` y documenta la solicitud de cambio en `harness-state.json` (o abre un nuevo CR). El proyecto no avanza hasta una nueva aprobación humana explícita.
    *   **Estado**: `harness-state.json` se marca como `HOLD`.

3.  **Registro de Aprendizaje**:
    *   Todo rechazo (major/minor) debe ser registrado por la Instancia C en `lessons_learned.md` al finalizar el proyecto, asegurando que el harness "recuerde" por qué falló esta vez.

### 12.4 Protocolo de Gestión de Cambios (CR)
Ante una solicitud de cambio (CR) sobre artefactos ya aprobados, el sistema activa el siguiente protocolo:

1.  **Registro y Notificación**:
    *   El humano o stakeholder envía el cambio.
    *   La **Instancia A (Gobernanza)** registra la solicitud en el `harness-state.json` bajo la sección `change_requests`, asignando un ID (ej: CR_001) y marcándolo como `OPEN`.

2.  **Registro Técnico (Instancia B)**:
    *   La **Instancia B (Ejecución)** crea un nuevo archivo de registro técnico en la carpeta `/changes` con el formato `CR_XXXX_Nombre.md` (ej: `CR_001_CampoVentas.md`).
    *   Este archivo detalla el alcance, los componentes afectados y el análisis de impacto técnico.

3.  **Evaluación de Impacto**:
    *   B evalúa qué fases, artefactos y pruebas existentes se ven afectados y estima el esfuerzo de re-ejecución.

4.  **Aprobación/Rechazo del CR**:
    *   La Instancia A presenta el impacto al humano. Tras la aprobación humana:
        *   El `harness-state.json` se actualiza: el CR cambia a `APPROVED`, se marcan los artefactos afectados como `DEPRECATED` o `PENDING_REWORK`.

5.  **Ejecución del Cambio**:
    *   El sistema reanuda la fase afectada desde el punto de cambio, utilizando el ciclo SDD+TDD para aplicar la actualización.

6.  **Cierre del CR**:
    *   Una vez que la Instancia C evalúa satisfactoriamente los cambios, la Instancia A marca el CR como `CLOSED` en el `harness-state.json` y archiva el registro de cambio y los reportes de evaluación en el histórico.




