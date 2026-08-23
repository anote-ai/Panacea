# Bots de Mensagens Multi-Canal da Panacea

Esta receita explica as integrações no estilo chat-ops da Panacea: bots autônomos para Slack, SMS e WhatsApp que permitem que os usuários façam perguntas sobre programação a partir dos aplicativos de mensagens que já utilizam.

## O que você vai aprender

- O padrão de design compartilhado entre os três bots: receber → chamar um LLM → ajustar ao limite de caracteres do canal → responder
- Como o bot do Slack lida com threads e edita uma mensagem de "pensando..." no lugar
- Como os bots de SMS/WhatsApp respondem de forma síncrona usando o Twilio's TwiML
- Uma lacuna arquitetônica atual que vale a pena conhecer antes de estender esses bots

## Por que isso é importante

Nem todo usuário quer abrir uma interface web ou IDE para fazer uma pergunta — integrações no estilo chat-ops atendem as pessoas onde elas já estão. Cada bot é um pequeno serviço Flask implantável de forma independente, permitindo que uma equipe execute apenas os canais que precisa (por exemplo, apenas Slack) sem precisar configurar o restante da pilha da Panacea.

## Arquivos principais da Panacea

| Arquivo | Por que é importante |
|---|---|
| `Panacea/packages/bots/slack/app.py` | Aplicativo Slack Bolt; suporta Modo Socket ou webhook HTTP; espaço reservado "pensando..." atualizado no local |
| `Panacea/packages/bots/sms/app.py` | Manipulador de webhook SMS do Twilio (`MessagingResponse`/TwiML) |
| `Panacea/packages/bots/whatsapp/app.py` | Manipulador de webhook do sandbox WhatsApp do Twilio |
| `Panacea/packages/bots/{slack,sms,whatsapp}/.env.example` | Credenciais necessárias por canal |

## Como funciona

1. **Slack** (`slack/app.py`): escuta eventos `app_mention`. `extract_query()` remove a menção `<@BOT_ID>` do texto da mensagem. Ele imediatamente publica uma mensagem de espaço reservado `_Anote está pensando..._`, em seguida, executa a chamada LLM em uma thread em segundo plano e edita esse espaço reservado no local via `client.chat_update(...)` ou, se a postagem do espaço reservado falhar, envia uma nova resposta em thread.
2. **SMS** (`sms/app.py`): O Twilio POSTa cada texto recebido para `/sms` como dados de formulário (`Body`, `From`). O manipulador chama o LLM de forma síncrona e retorna um `MessagingResponse` (TwiML) com a resposta — o Twilio entrega isso como um texto de acompanhamento.
3. **WhatsApp** (`whatsapp/app.py`): mesmo padrão TwiML que o SMS, conectado ao webhook do sandbox WhatsApp do Twilio em vez de um número de telefone.
4. Todos os três chamam a **API da Anthropic diretamente** (`anthropic.Anthropic(...).messages.create(...)`) com um prompt de sistema compartilhado descrevendo o Anote como um assistente de programação — atualmente, eles não fazem proxy através do backend da Panacea, então não recebem RAG/aterramento de documentos, medição de crédito ou orquestração multi-agente das receitas 03/04/08.
5. As respostas são ajustadas ao limite de cada canal antes de serem enviadas: Slack 2900 caracteres, SMS/WhatsApp 1600 caracteres, cada uma com um aviso de truncamento anexado se cortada.

### Lacuna arquitetônica a ser conhecida

Como esses bots chamam a Anthropic diretamente em vez de rotearem através do backend da Panacea, um usuário de Slack/SMS/WhatsApp atualmente não pode fazer perguntas fundamentadas em documentos que eles carregaram para a Panacea, e seu uso não é medido através do sistema de crédito na receita 08. Se você deseja paridade de canal com a interface web, o próximo passo natural é trocar a chamada direta `anthropic_client.messages.create(...)` por uma solicitação ao próprio `/v1/chat/completions` da Panacea (gateway compatível com OpenAI da receita 07) para que esses bots herdem RAG, orquestração e faturamento gratuitamente.

## Execute localmente

Cada bot é independente — instale e execute apenas os que você precisa.

### Slack

```bash
cd Panacea/packages/bots/slack
pip install -r requirements.txt
cp .env.example .env   # preencha SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET, ANTHROPIC_API_KEY
python app.py
```

Defina `SLACK_APP_TOKEN` em `.env` para executar no Modo Socket (nenhuma URL pública necessária); caso contrário, ele serve HTTP na `PORT` (padrão 3000) e espera que o webhook da API de Eventos do Slack aponte para `POST /slack/events`.

### SMS

```bash
cd Panacea/packages/bots/sms
pip install -r requirements.txt
cp .env.example .env   # preencha ANTHROPIC_API_KEY
python app.py
```

Configure o webhook SMS do seu número do Twilio para `POST https://<seu-host>/sms` (porta padrão 3001).

### WhatsApp

```bash
cd Panacea/packages/bots/whatsapp
pip install -r requirements.txt
cp .env.example .env   # preencha ANTHROPIC_API_KEY
python app.py
```

Configure o webhook do sandbox WhatsApp do Twilio para apontar para `POST /whatsapp` neste serviço.

Cada bot também expõe `GET /health` para uma verificação rápida de vivacidade.

## Notas para o livro de receitas

Esta é uma boa receita para "estender a Panacea": os leitores podem ver a versão direta para a Anthropic funcionando em minutos, e depois seguir a nota sobre a lacuna arquitetônica acima para conectá-la através do backend da Panacea em vez disso para respostas fundamentadas e medidas.
