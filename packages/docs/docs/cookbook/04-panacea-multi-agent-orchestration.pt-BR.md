# Orquestração Multi-Agente do Panacea

Esta receita explica a arquitetura de orquestração de agentes do Panacea: como o orquestrador atribui tarefas, escolhe agentes e suporta fluxos de trabalho sequenciais e hierárquicos.

## O que você aprenderá

- O papel do orquestrador como o cérebro do sistema
- Como o Panacea roteia tarefas para agentes especializados
- A diferença entre fluxos de trabalho sequenciais e hierárquicos
- Como equipes de agentes colaboram em um objetivo compartilhado
- Como funciona o registro de ferramentas para que os agentes possam usar novas capacidades

## Por que isso é importante

No Panacea, o orquestrador não é aleatório. Ele escolhe o melhor agente com base nas descrições de capacidade, no contexto da tarefa e no estado do fluxo de trabalho. Isso torna o sistema previsível e extensível.

## Conceitos-chave

- **Orquestrador** — coordenador central que decide qual agente será executado em seguida
- **Agente** — unidade autônoma com um propósito definido, como `DocumentRetrievalAgent`, `GeneralKnowledgeAgent` ou `ChatHistoryAgent`
- **Equipe** — um grupo de agentes trabalhando juntos em direção a um objetivo comum
- **Fluxos de trabalho** — o estilo de colaboração; pode ser:
  - **Sequencial**: um passo segue o outro em ordem
  - **Hierárquico**: uma cadeia de comando onde o orquestrador delega subtarefas a especialistas
- **Ferramentas** — funções que os agentes podem chamar para realizar ações como buscar, fazer upload ou executar código

## Arquivos-chave do Panacea

| Arquivo | Por que é importante |
|---|---|
| `Panacea/backend/agents/multi_agent_system.py` | Lógica de orquestrador e roteamento de fluxo de trabalho |
| `Panacea/backend/agents/autonomous_agent.py` | Registro de ferramentas e ciclo de vida do agente |
| `Panacea/backend/agents/routing.py` | Lógica auxiliar de roteamento de tarefas |
| `Panacea/backend/agents/reactive_agent.py` | Inicializa o sistema multi-agente e o conecta aos fluxos de chat |

## Como funciona

1. Um usuário envia uma tarefa ou consulta.
2. O agente orquestrador revisa a entrada e escolhe um próximo agente com base nas capacidades e nos requisitos da tarefa.
3. Agentes especializados executam sua parte do pipeline e podem retornar resultados intermediários.
4. O orquestrador pode continuar sequencialmente ou continuar delegando subtarefas em um padrão hierárquico.
5. O resultado final é montado e retornado ao usuário.

### Fluxo de trabalho sequencial

Um fluxo de trabalho sequencial é útil para pipelines fixos, como:

- recuperar partes de documentos → resumir → responder ao usuário
- reunir contexto de código → analisar código → retornar sugestões de revisão

Cada passo é executado em ordem, e o próximo passo utiliza a saída do passo anterior.

### Fluxo de trabalho hierárquico

Um fluxo de trabalho hierárquico é útil para tarefas complexas onde o orquestrador gerencia especialistas:

- o orquestrador atribui um agente para reunir dados
- outro agente valida os dados
- um terceiro agente gera a resposta final

Isso é semelhante a uma cadeia de comando: o orquestrador mantém o controle e delega o trabalho a agentes especialistas.

## Registro de ferramentas

O Panacea suporta registro dinâmico de ferramentas. Se um agente precisar de uma nova capacidade, ele pode chamar `register_tool(...)` de `backend/agents/autonomous_agent.py`.

Isso significa que o livro de receitas pode documentar não apenas como usar ferramentas existentes, mas como adicionar novas ferramentas ao sistema.

## Ciclo de feedback

O feedback do usuário é essencial para melhorar a seleção de agentes. O Panacea registra feedback de perguntas e respostas de documentos e resultados de tarefas para que o orquestrador possa aprender quais agentes e ferramentas produzem os melhores resultados.

## Notas para o livro de receitas

Esta receita é uma forte candidata a uma explicação manual. Deve incluir diagramas ou exemplos de fluxo passo a passo que mostrem por que o orquestrador toma decisões em vez de deixar a seleção de agentes ao acaso.
