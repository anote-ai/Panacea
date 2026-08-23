# Recursos do Aplicativo Web

## Interface de Chat

A visualização principal do chat reflete o design do ChatGPT: uma barra lateral esquerda colapsável com o histórico de sessões e um thread de mensagens centralizado com uma barra de entrada na parte inferior.

## Modo Claro / Escuro

Alternar com o botão no canto superior direito. A preferência é persistida em `localStorage`.

- **Claro**: fundos brancos/cinza-claro, texto preto
- **Escuro**: fundos `#212121`/`#2F2F2F`, texto branco

## Streaming

A entrada envia uma solicitação `POST /api/chat/stream` e lê a resposta SSE. Um botão de parar interrompe o streaming no meio.

## Sessões

Cada conversa é uma sessão armazenada no lado do servidor. As sessões são listadas na barra lateral e persistem entre as recargas de página.
