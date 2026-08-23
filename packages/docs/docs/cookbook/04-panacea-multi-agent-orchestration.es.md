# Orquestación Multi-Agente de Panacea

Esta receta explica la arquitectura de orquestación de agentes de Panacea: cómo el orquestador asigna tareas, elige agentes y soporta flujos de trabajo secuenciales y jerárquicos.

## Lo que aprenderás

- El papel del orquestador como el cerebro del sistema
- Cómo Panacea enruta tareas a agentes especializados
- La diferencia entre flujos de trabajo secuenciales y jerárquicos
- Cómo las tripulaciones de agentes colaboran en un objetivo compartido
- Cómo funciona el registro de herramientas para que los agentes puedan usar nuevas capacidades

## Por qué esto es importante

En Panacea, el orquestador no es aleatorio. Elige el mejor agente basado en descripciones de capacidades, contexto de la tarea y estado del flujo de trabajo. Eso hace que el sistema sea predecible y extensible.

## Conceptos clave

- **Orquestador** — coordinador central que decide qué agente se ejecuta a continuación
- **Agente** — unidad autónoma con un propósito definido, como `DocumentRetrievalAgent`, `GeneralKnowledgeAgent` o `ChatHistoryAgent`
- **Tripulación** — un grupo de agentes trabajando juntos hacia un objetivo común
- **Flujos de trabajo** — el estilo de colaboración; puede ser:
  - **Secuencial**: un paso sigue a otro en orden
  - **Jerárquico**: una cadena de mando donde el orquestador delega subtareas a especialistas
- **Herramientas** — funciones que los agentes pueden llamar para realizar acciones como buscar, subir o ejecutar código

## Archivos clave de Panacea

| Archivo | Por qué es importante |
|---|---|
| `Panacea/backend/agents/multi_agent_system.py` | Lógica de orquestador y enrutamiento de flujos de trabajo |
| `Panacea/backend/agents/autonomous_agent.py` | Registro de herramientas y ciclo de vida del agente |
| `Panacea/backend/agents/routing.py` | Lógica auxiliar de enrutamiento de tareas |
| `Panacea/backend/agents/reactive_agent.py` | Inicializa el sistema multi-agente y lo conecta a flujos de chat |

## Cómo funciona

1. Un usuario envía una tarea o consulta.
2. El agente orquestador revisa la entrada y elige un siguiente agente basado en capacidades y requisitos de la tarea.
3. Los agentes especializados ejecutan su parte de la tubería y pueden devolver resultados intermedios.
4. El orquestador puede continuar secuencialmente o seguir delegando subtareas en un patrón jerárquico.
5. El resultado final se ensambla y se devuelve al usuario.

### Flujo de trabajo secuencial

Un flujo de trabajo secuencial es útil para tuberías fijas como:

- recuperar fragmentos de documentos → resumir → responder al usuario
- reunir contexto de código → analizar código → devolver sugerencias de revisión

Cada paso se ejecuta en orden, y el siguiente paso utiliza la salida del paso anterior.

### Flujo de trabajo jerárquico

Un flujo de trabajo jerárquico es útil para tareas complejas donde el orquestador gestiona especialistas:

- el orquestador asigna un agente para recopilar datos
- otro agente valida los datos
- un tercer agente genera la respuesta final

Esto es similar a una cadena de mando: el orquestador se mantiene en control y delega el trabajo a agentes especializados.

## Registro de herramientas

Panacea soporta el registro dinámico de herramientas. Si un agente necesita una nueva capacidad, puede llamar a `register_tool(...)` desde `backend/agents/autonomous_agent.py`.

Eso significa que el libro de cocina puede documentar no solo cómo usar herramientas existentes, sino cómo agregar nuevas herramientas al sistema.

## Ciclo de retroalimentación

La retroalimentación del usuario es esencial para mejorar la selección de agentes. Panacea registra comentarios de preguntas y respuestas de documentos y resultados de tareas para que el orquestador pueda aprender qué agentes y herramientas producen los mejores resultados.

## Notas para el libro de cocina

Esta receta es un fuerte candidato para una explicación manual. Debe incluir diagramas o ejemplos de flujo paso a paso que muestren por qué el orquestador toma decisiones en lugar de dejar la selección de agentes al azar.
