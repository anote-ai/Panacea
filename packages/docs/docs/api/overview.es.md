# Descripción general de la API del backend

El backend de Anote es una API unificada de Flask que sirve todas las superficies del cliente.

URL base: `http://localhost:5000` (local) o la URL de tu backend desplegado.

## Autenticación

Todos los endpoints protegidos requieren un token JWT:

```
Authorization: Bearer <token>
```

Obtén un token a través de `POST /auth/login` o `POST /auth/register`.

## Endpoints clave

### Chat de Agente (Streaming)

```
POST /api/chat/stream          # Chat por streaming SSE
POST /api/chat                 # Chat no streaming
GET  /api/chat/sessions        # Listar sesiones
POST /api/chat/sessions        # Crear sesión
```

### Documentos

```
POST /api/documents/upload     # Subir documento
GET  /api/documents            # Listar documentos
GET  /api/documents/{id}       # Obtener documento
DELETE /api/documents/{id}     # Eliminar documento
POST /api/documents/{id}/ask   # Preguntas y respuestas sobre el documento
```

### Búsqueda Semántica

```
GET  /api/search?q=...&cwd=... # Buscar en el código indexado
```

### Autenticación

```
POST /auth/register            # Registrarse
POST /auth/login               # Iniciar sesión
POST /auth/refresh             # Refrescar JWT
GET  /auth/google              # OAuth de Google
```

### Usuario y Facturación

```
GET  /api/user/profile         # Obtener usuario
POST /api/payments/checkout    # Pago con Stripe
POST /api/payments/portal      # Portal del cliente
POST /api/payments/webhook     # Webhook de Stripe
```
