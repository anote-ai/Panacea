# Обзор API для бэкенда

Бэкенд Anote — это унифицированный API на Flask, обслуживающий все клиентские интерфейсы.

Базовый URL: `http://localhost:5000` (локальный) или ваш развернутый URL бэкенда.

## Аутентификация

Все защищенные конечные точки требуют токен JWT:

```
Authorization: Bearer <token>
```

Получите токен через `POST /auth/login` или `POST /auth/register`.

## Ключевые конечные точки

### Чат агента (потоковая передача)

```
POST /api/chat/stream          # SSE потоковый чат
POST /api/chat                 # Непотоковый чат
GET  /api/chat/sessions        # Список сессий
POST /api/chat/sessions        # Создать сессию
```

### Документы

```
POST /api/documents/upload     # Загрузить документ
GET  /api/documents            # Список документов
GET  /api/documents/{id}       # Получить документ
DELETE /api/documents/{id}     # Удалить документ
POST /api/documents/{id}/ask   # Вопросы и ответы по документу
```

### Семантический поиск

```
GET  /api/search?q=...&cwd=... # Поиск по индексированному коду
```

### Аутентификация

```
POST /auth/register            # Регистрация
POST /auth/login               # Вход
POST /auth/refresh             # Обновить JWT
GET  /auth/google              # Google OAuth
```

### Пользователь и выставление счетов

```
GET  /api/user/profile         # Получить пользователя
POST /api/payments/checkout    # Оформление заказа через Stripe
POST /api/payments/portal      # Портал клиента
POST /api/payments/webhook     # Вебхук Stripe
```
