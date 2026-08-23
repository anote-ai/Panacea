# Panacea API Gateway Compatível com OpenAI

Esta receita explica como direcionar qualquer ferramenta construída contra o SDK OpenAI para o Panacea — sem alterações de código — enquanto ainda obtém acesso a extensões RAG específicas do Panacea, como fontes de documentos fundamentadas.

## O que você vai aprender

- Como `AnoteOpenAI` espelha a interface do verdadeiro cliente `openai.OpenAI`
- Como fazer upload de documentos e obter respostas fundamentadas em documentos através de uma API moldada por chat-completions
- Como o streaming funciona sobre Eventos Enviados pelo Servidor (SSE), estilo OpenAI
- Onde as extensões específicas do Panacea (`anote_sources`, `anote_message_id`) aparecem na resposta

## Por que isso é importante

Uma quantidade enorme de ferramentas existentes — integrações do LangChain, scripts internos, frameworks de agentes de terceiros — é escrita contra a estrutura do SDK OpenAI (`client.chat.completions.create(...)`, `client.models.list()`). Em vez de pedir a cada integrador que aprenda um SDK Panacea sob medida, o Panacea fornece um cliente que se encaixa, que fala a mesma interface, para que as equipes possam adotar o backend privado e fundamentado em documentos do Panacea sem reescrever seu código de integração.

## Principais arquivos do Panacea

| Arquivo | Por que é importante |
|---|---|
| `Panacea/backend/sdk/anoteai/openai_compat.py` | Cliente `AnoteOpenAI`: `CompletionsClient`, `ModelsClient`, `DocumentsClient` e o parser de stream SSE |
| `Panacea/backend/sdk/anoteai/core.py` | A classe SDK subjacente `PrivateChatbot` que a camada de compatibilidade envolve |
| `Panacea/backend/sdk/anoteai/handlers/private_handlers.py` | Manipulação de requisições compartilhada com o SDK nativo |
| Rotas do servidor: `POST /v1/chat/completions`, `GET /v1/models`, `POST /v1/question-answer`, `POST /public/upload` | Os endpoints moldados como OpenAI (e um específico do Panacea) que o cliente chama |

## Como funciona

1. Instancie o cliente exatamente como o SDK OpenAI, mas apontando para seu backend Panacea:

   ```python
   from anoteai.openai_compat import AnoteOpenAI

   client = AnoteOpenAI(
       api_key="sua-chave-api-anote",       # ou defina ANOTE_API_KEY
       base_url="http://localhost:5000",    # ou https://api.anote.ai
   )
   ```

2. Para perguntas e respostas fundamentadas em documentos, faça upload dos arquivos primeiro — `client.documents.upload(...)` envia dados de formulário multipart para `/public/upload` e retorna um `chat_id`.
3. Faça uma pergunta da mesma forma que você chamaria o SDK OpenAI, passando o `chat_id` através de `extra_body` para que o servidor saiba quais documentos recuperar:

   ```python
   upload_resp = client.documents.upload("caminho/para/relatorio.pdf")
   chat_id = upload_resp["chat_id"]

   response = client.chat.completions.create(
       model="gpt-4o",
       messages=[{"role": "user", "content": "Resuma as principais descobertas."}],
       extra_body={"chat_id": chat_id},
   )
   print(response.choices[0].message.content)
   print("Fontes:", response.anote_sources)
   ```

4. A resposta é mapeada em dataclasses que espelham o verdadeiro SDK OpenAI (`ChatCompletion`, `Choice`, `Message`, `Usage`), além de duas extensões do Panacea: `anote_message_id` e `anote_sources` (os trechos/citações recuperados que sustentam a resposta).
5. Passe `stream=True` para obter um gerador de objetos `ChatCompletionChunk` analisados a partir de linhas SSE `text/event-stream` (`data: {...}` por token, terminado por `data: [DONE]`) — a mesma estrutura que o cliente de streaming da OpenAI produz.
6. `client.models.list()` chama `GET /v1/models` para descoberta de modelos, retornando objetos `Model`/`ModelList` exatamente como o SDK OpenAI.

## Execute localmente

A partir da raiz do workspace (`anote/panacea`):

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

Instale a única dependência do cliente e defina sua chave API:

```bash
pip install requests
export ANOTE_API_KEY=sua_chave_api_aqui   # macOS/Linux
set ANOTE_API_KEY=sua_chave_api_aqui      # Windows cmd
```

### Passo a passo mínimo

```python
from anoteai.openai_compat import AnoteOpenAI

client = AnoteOpenAI(base_url="http://localhost:5000")

# Chat simples, sem documentos:
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Qual é a capital da França?"}],
)
print(response.choices[0].message.content)

# Streaming:
for chunk in client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Conte até cinco."}],
    stream=True,
):
    for choice in chunk.choices:
        if choice.delta.content:
            print(choice.delta.content, end="", flush=True)
```

## Notas para o livro de receitas

Esta receita é um bom complemento para a receita 03 — é a mesma capacidade de perguntas e respostas/RAG de documentos, mas exposta através de uma interface que ferramentas existentes baseadas no SDK OpenAI podem consumir sem modificações. Vale ressaltar para os leitores que `DocumentsClient.upload()`/`question_answer()` são auxiliares específicos do Panacea sobrepostos ao núcleo compatível com OpenAI, não fazem parte da especificação OpenAI em si.
