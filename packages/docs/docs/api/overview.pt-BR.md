# Visão Geral da API Backend

O backend do Anote é uma API unificada em Flask que atende todas as superfícies do cliente.

URL Base: `http://localhost:5000` (local) ou sua URL de backend implantada.

## Autenticação

Todos os endpoints protegidos requerem um token JWT:

```
Authorization: Bearer <token>
```

Obtenha um token via `POST /auth/login` ou `POST /auth/register`.

## Principais Endpoints

### Chat do Agente (Streaming)

```
POST /api/chat/stream          # Chat em streaming SSE
POST /api/chat                 # Chat não streaming
GET  /api/chat/sessions        # Listar sessões
POST /api/chat/sessions        # Criar sessão
```

### Documentos

```
POST /api/documents/upload     # Fazer upload de documento
GET  /api/documents            # Listar documentos
GET  /api/documents/{id}       # Obter documento
DELETE /api/documents/{id}     # Deletar documento
POST /api/documents/{id}/ask   # Perguntas e respostas sobre o documento
```

### Busca Semântica

```
GET  /api/search?q=...&cwd=... # Buscar no código indexado
```

### Autenticação

```
POST /auth/register            # Registrar
POST /auth/login               # Fazer login
POST /auth/refresh             # Atualizar JWT
GET  /auth/google              # OAuth do Google
```

### Usuário & Faturamento

```
GET  /api/user/profile         # Obter usuário
POST /api/payments/checkout    # Checkout do Stripe
POST /api/payments/portal      # Portal do cliente
POST /api/payments/webhook     # Webhook do Stripe
```
