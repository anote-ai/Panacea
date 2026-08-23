# Visão Geral do Aplicativo Web

O aplicativo web Anote AI é uma interface de chat estilo ChatGPT que se conecta ao backend do Anote.

## Recursos

- Modo claro e escuro (detecta automaticamente a preferência do sistema)
- Respostas em streaming via SSE
- Histórico de sessões de chat em uma barra lateral recolhível
- Seletor de modelo (Claude, GPT-4o, etc.)
- Upload de documentos e perguntas e respostas
- Design responsivo

## Executando Localmente

```bash
cd packages/web
npm install
npm run dev
```

O aplicativo é executado em `http://localhost:3000` e faz proxy das chamadas de API para `http://localhost:5000`.
