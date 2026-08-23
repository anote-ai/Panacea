# Panacea Document Q&A + RAG

Esta receita explica como a Panacea constrói perguntas e respostas de documentos privados com geração aumentada por recuperação (RAG).

## O que você aprenderá

- Como a Panacea ingere documentos e os armazena como texto pesquisável
- Como o backend recupera partes relevantes para uma pergunta
- Como o sistema utiliza embeddings e fontes de documentos para fundamentar respostas
- Como o feedback de perguntas e respostas é capturado e melhora as respostas futuras

## Por que isso é importante

A Panacea foi projetada para permitir que equipes façam perguntas sobre documentos privados sem enviá-los para um serviço de chat de terceiros. O fluxo de trabalho é:

1. Fazer upload de documentos
2. Dividir e incorporar conteúdo
3. Recuperar partes relevantes para uma consulta do usuário
4. Responder usando um LLM com citações
5. Capturar feedback para melhorar a qualidade

## Principais arquivos da Panacea

| Arquivo | Por que é importante |
|---|---|
| `Panacea/backend/api_endpoints/documents/handler.py` | Rotas da API para upload e ingestão de documentos |
| `Panacea/backend/database/db.py` | Lógica SQL para armazenamento e recuperação de documentos |
| `Panacea/backend/database/qa_feedback.py` | Captura de feedback para perguntas e respostas de documentos |
| `Panacea/backend/agents/multi_agent_system.py` | Agentes de recuperação de documentos usados em fluxos de trabalho multi-agente |

## Como funciona

- Os documentos são enviados através do backend e armazenados em `documents.document_text`.
- O sistema divide documentos grandes e cria metadados de recuperação para busca rápida.
- Quando um usuário faz uma pergunta, a Panacea seleciona um ou mais agentes especializados para recuperar as melhores partes e, em seguida, gera uma resposta.
- O resultado inclui citações de fontes para que os usuários possam rastrear a resposta de volta ao documento original.
- Sinais de feedback são registrados em `qa_feedback` para permitir melhorias futuras na qualidade.

## Execute localmente

A partir da raiz do workspace (`anote/panacea`):

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

Isso inicia o backend, aplicativo web, MySQL, Redis e Tika.

Se você já estiver dentro da pasta da receita, use:

```bash
cd ../../../Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

Abra `http://localhost:3000` para usar a interface web da Panacea. Os uploads de documentos são tratados pela rota do backend `POST /ingest-pdf` com os campos de formulário obrigatórios `chat_id` e `files[]`.

Exemplo de comando de upload:

```bash
curl -X POST http://localhost:5000/ingest-pdf \
  -F chat_id=1 \
  -F "files[]=@./path/to/document.pdf"
```

### Passo a passo mínimo para upload

1. Inicie a Panacea a partir da raiz do repositório:

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

2. Em outro terminal, faça o upload de um único documento de texto ou PDF:

```bash
curl -X POST http://localhost:5000/ingest-pdf \
  -F chat_id=1 \
  -F "files[]=@./Cookbook/recipes/03-panacea-document-qa-rag/data/sample-doc.txt"
```

3. Confirme que o backend retorna uma resposta bem-sucedida `Documento Enviado`.

4. Use a interface web em `http://localhost:3000` e selecione a mesma sessão de chat para fazer perguntas sobre o documento enviado.

Se você quiser testar a API diretamente após o upload, encontre o ID da sessão de chat na interface ou no banco de dados e envie perguntas através do fluxo de chat do aplicativo. A Panacea irá recuperar partes relevantes e gerar uma resposta fundamentada.

## Notas para o livro de receitas

Esta receita é ideal para uma entrada de livro de receitas que explica como a Panacea suporta o trabalho de conhecimento privado. É mais conceitual do que um script de uma linha, porque o verdadeiro valor está em entender a arquitetura de ingestão e recuperação de documentos.
