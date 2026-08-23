# Panacea AI Coding Toolchain

Esta receita explica como a experiência de codificação com IA da Panacea é entregue através do CLI, SDK e VS Code.

## O que você vai aprender

- Os diferentes pontos de entrada de codificação com IA na Panacea
- Como o CLI, SDK e a extensão do VS Code se relacionam com o backend compartilhado
- Principais capacidades do produto para assistência de código privada
- Onde procurar no repositório por detalhes de implementação

## Por que isso é importante

A Panacea é construída como um produto unificado com múltiplas interfaces:

- um **CLI** que alimenta `anote chat`, busca de código e revisão de repositórios
- uma **extensão do VS Code** para assistência de IA dentro do editor
- um **SDK** para incorporar a Panacea em outras aplicações

Essas interfaces compartilham um backend e uma camada de raciocínio orientada por agentes, o que torna o produto consistente em fluxos de trabalho de desktop, web e código.

## Principais arquivos da Panacea

| Arquivo | Por que é importante |
|---|---|
| `Panacea/packages/cli` | Implementação do CLI em TypeScript para fluxos de trabalho de desenvolvedores |
| `Panacea/packages/vscode` | Extensão do VS Code e integração de chat |
| `Panacea/packages/sdk` | SDK em TypeScript para acesso programático |
| `Panacea/packages/backend` | Serviço de backend compartilhado que alimenta todas as interações de UI e CLI |

## Como funciona

- Uma ação de codificação do usuário começa no CLI, SDK ou extensão do VS Code.
- A solicitação é enviada para a API de backend da Panacea.
- O backend utiliza orquestração de agentes e provedores de modelo para produzir respostas cientes de código.
- A resposta é retornada na mesma interface, com sugestões de código, explicações ou correções.

## Recursos úteis do produto

- **CLI**: `anote chat`, busca de repositórios, revisão de código, geração de código e assistência alimentada por embeddings.
- **VS Code**: chat inline, pré-visualizações de diffs, ações de código e respostas em streaming.
- **SDK**: um wrapper cliente para a API da Panacea, permitindo integrações personalizadas.

## Execute localmente

A partir da raiz do workspace (`anote/panacea`):

```bash
cd Panacea
cp packages/backend/.env.example packages/backend/.env
docker compose up --build
```

Isso inicia os serviços de backend e frontend compartilhados.

Em outro terminal, execute o pacote CLI:

```bash
cd Panacea/packages/cli
npm install
npm run dev
```

Então você pode usar o CLI localmente ou construí-lo com `npm run build`.

Para desenvolvimento no VS Code, abra `Panacea/packages/vscode` no VS Code e inicie a extensão com o depurador.

## Notas para o livro de receitas

Esta receita é útil para colegas de equipe que precisam de um guia de alto nível sobre o produto de codificação com IA de múltiplas interfaces da Panacea. Ela também pode direcionar os leitores para arquivos de implementação que podem modificar ou estender.
