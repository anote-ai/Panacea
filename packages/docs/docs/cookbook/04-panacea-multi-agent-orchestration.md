# Panacea Multi-Agent Orchestration

This recipe explains Panacea’s agent orchestration architecture: how the orchestrator assigns tasks, picks agents, and supports sequential and hierarchical workflows.

## What you'll learn

- The role of the orchestrator as the system brain
- How Panacea routes tasks to specialized agents
- The difference between sequential and hierarchical workflows
- How crews of agents collaborate on a shared goal
- How tool registration works so agents can use new capabilities

## Why this matters

In Panacea, the orchestrator is not random. It chooses the best agent based on capability descriptions, task context, and workflow state. That makes the system predictable and extensible.

## Key concepts

- **Orchestrator** — central coordinator that decides which agent runs next
- **Agent** — autonomous unit with a defined purpose, such as `DocumentRetrievalAgent`, `GeneralKnowledgeAgent`, or `ChatHistoryAgent`
- **Crew** — a group of agents working together toward a common objective
- **Workflows** — the collaboration style; can be:
  - **Sequential**: one step follows another in order
  - **Hierarchical**: a chain of command where the orchestrator delegates subtasks to specialists
- **Tools** — functions agents can call to perform actions like searching, uploading, or executing code

## Key Panacea files

| File | Why it matters |
|---|---|
| `Panacea/backend/agents/multi_agent_system.py` | Orchestrator and workflow routing logic |
| `Panacea/backend/agents/autonomous_agent.py` | Tool registration and agent lifecycle |
| `Panacea/backend/agents/routing.py` | Task-routing helper logic |
| `Panacea/backend/agents/reactive_agent.py` | Initializes the multi-agent system and connects it to chat flows |

## How it works

1. A user submits a task or query.
2. The orchestrator agent reviews the input and chooses a next agent based on capabilities and task requirements.
3. Specialized agents execute their part of the pipeline and may return intermediate results.
4. The orchestrator may either continue sequentially or keep delegating sub-tasks in a hierarchical pattern.
5. The final result is assembled and returned to the user.

### Sequential workflow

A sequential workflow is useful for fixed pipelines such as:

- retrieve document chunks → summarize → answer user
- gather code context → analyze code → return review suggestions

Each step runs in order, and the next step uses the previous step’s output.

### Hierarchical workflow

A hierarchical workflow is useful for complex tasks where the orchestrator manages specialists:

- orchestrator assigns one agent to gather data
- another agent validates the data
- a third agent generates the final response

This is similar to a chain of command: the orchestrator stays in control and delegates work to subject-matter agents.

## Tool registration

Panacea supports dynamic tool registration. If an agent needs a new capability, it can call `register_tool(...)` from `backend/agents/autonomous_agent.py`.

That means the cookbook can document not only how to use existing tools, but how to add new tools to the system.

## Feedback loop

User feedback is essential for improving agent selection. Panacea logs feedback from document Q&A and task results so the orchestrator can learn which agents and tools produce the best outcomes.

## Notes for the cookbook

This recipe is a strong candidate for a manual explanation. It should include diagrams or step-by-step flow examples that show why the orchestrator makes decisions instead of leaving agent selection to chance.
