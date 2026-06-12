## 4. Principios de Anthropic aplicados
- Principio 1: Separacion de roles (Specialization): Roles separados, no un agente todopoderoso
- Principio 2: Trabajo incremental con artefactos de handoff: Trabajo pequeno + contexto como artefactos
- Principio 3: Evaluador externo independiente (Separation of generation from evaluation): Quien genera no evalua; el evaluador es critico
- Principio 4: Context resets sobre compactacion continua: Reiniciar contexto limpio mejor que compactar historial
- Principio 5: Contratos explicitos antes de la ejecucion (Sprint contracts): Acordar "terminado" antes de empezar
- Principio 6: Escalamiento proporcional a la complejidad: Esfuerzo proporcional a la complejidad de la tarea
- Principio 7: Herramientas como extensiones criticas (Tool design is as important as prompt design): Herramientas y prompts son igual de criticos
- Principio 8: Observabilidad y depuracion como requisito (Traces over intuition): Trazabilidad completa para depurar
                                      |

## 5. Estandares de Comportamiento esperado del harness
Conceptos adicionales derivados de los articulos de Anthropic

### E.1. Persistencia de estado entre sesiones
Cada harness debe mantener estado entre sesiones mediante:
- Un archivo de progreso (progress file) que registre el historial de lo ejecutado
- Git como registro de estado: commits descriptivos al finalizar cada sesion, uso de `git log` para reorientarse al inicio de cada sesion. Ademas desde el principio debe estar enlazado a un repositorio en github.
- Sin este mecanismo, cada sesion comienza ciega y el agente desperdicia contexto reorientandose

### E.2. Context Anxiety — cuando y por que hacer reset
Los modelos exhiben "ansiedad contextual": cierran trabajo prematuramente cuando anticipan el limite de contexto.
- El reset (contexto limpio) es superior a la compactacion cuando este fenomeno aparece
- Criterio de activacion: si el agente empieza a cerrar tareas sin completarlas o a saltarse pasos, se debe hacer reset
- El reset agrega complejidad orquestal pero preserva la calidad del output

### E.3. Calibracion del evaluador con few-shot y rubrica 0.0–1.0
El Principio 3 (evaluador externo) requiere calibracion explicita para evitar lenidad sistematica:
- Proveer al evaluador pocos ejemplos con desglose de puntajes detallados
- Usar rubrica con scores 0.0–1.0 por dimension (precision factual, completitud, calidad de fuentes, eficiencia de herramientas)
- Una sola llamada LLM-as-Judge es mas consistente que multiples jueces
- Sin calibracion, los evaluadores son sistematicamente lenientes incluso con outputs de baja calidad

### E.4. Principio de Minima Complejidad + evolucion continua del harness
- Empezar con el harness mas simple posible; agregar componentes solo cuando se demuestre que son necesarios
- Cada componente codifica una suposicion sobre limitaciones del modelo que debe validarse periodicamente
- Proceso de re-evaluacion: remover un componente a la vez y medir impacto en calidad del output
- Los harnesses NO son estaticos: conforme los modelos mejoran, algunos componentes se vuelven obsoletos y emergen nuevas capacidades que justifican nuevos componentes

### E.5. Ejecucion durable: reanudar desde checkpoint, no reiniciar
- Los agentes son stateful y ejecutan periodos largos; los fallos son inevitables
- El harness debe implementar resumption desde el punto de fallo, no reinicio desde cero
- Los agentes deben poder adaptar su comportamiento cuando una herramienta falla (fallback, reintento, escalamiento)
- Esto aplica tanto al harness de gobernanza como al de construccion de productos

### E.6. Outputs al filesystem, no al orquestador
Para evitar el "telefono descompuesto" (degradacion de informacion al pasar por multiples agentes):
- Los subagentes escriben sus outputs directamente al filesystem o sistema externo
- El orquestador recibe solo referencias ligeras (paths, IDs), no el contenido completo
- Esto mejora fidelidad, reduce overhead de tokens y evita cuellos de botella

### E.7. Paralelizacion explicita como estrategia de rendimiento
- Ejecutar 3–5 subagentes en paralelo + 3+ herramientas en paralelo por subagente
- En el sistema de investigacion de Anthropic esto redujo el tiempo en 90% para queries complejas
- El uso de tokens explica el 80% de la varianza en rendimiento; la paralelizacion escala el uso de tokens eficientemente
- Aplicar en fases donde los documentos o features son independientes entre si

### E.8. Extended Thinking para tareas de reasoning complejo
- Para tareas de alta complejidad cognitiva usar extended thinking como scratchpad controlable
- Mejora seguimiento de instrucciones, razonamiento y eficiencia
- No aplicar de forma indiscriminada: reservar para los pasos donde la calidad del razonamiento es critica

### E.9. Evaluacion temprana con muestras pequenas
- No esperar a tener el harness completo para evaluar: empezar con ~20 queries/casos representativos
- Los cambios tempranos tienen efectos dramaticos (diferencias de 30% a 80% en calidad)
- Pocas pruebas revelan el impacto de cambios claramente; la evaluacion humana es complemento indispensable a la automatizada

### E.10. Secuencia de inicio de sesion estructurada
Cada harness debe definir una secuencia de arranque explicita para cada sesion:
- Verificar directorio y ambiente
- Leer git log y archivo de progreso
- Revisar contratos de sprint activos
- Ejecutar prueba basica de sanidad del ambiente
- Seleccionar la siguiente tarea prioritaria segun backlog

### E.11. Estrategia de busqueda "de amplio a estrecho"
Especialmente relevante para la construccion de gobernanza:
- Comenzar con queries cortas y amplias para evaluar disponibilidad de informacion
- Luego profundizar en las areas con mayor densidad de informacion relevante
- Evitar comprometer el plan a una fuente antes de explorar la amplitud del espacio

### E.12. Arquitectura Orquestador-Trabajador
- El agente orquestador analiza el objetivo, desarrolla la estrategia y crea subagentes especializados
- El orquestador guarda su plan en memoria ANTES de crear subagentes (para no perder el plan si el contexto crece)
- Los subagentes operan con ventanas de contexto propias y frescas
- Las descripciones de tareas para subagentes deben incluir: objetivo, formato de salida esperado, herramientas disponibles y limites claros
- Sin descripciones detalladas, los subagentes duplican trabajo o toman caminos equivocados
