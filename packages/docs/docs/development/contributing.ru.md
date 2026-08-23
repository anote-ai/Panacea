# Участие

## Настройка

```bash
git clone https://github.com/anote-ai/Panacea
cd Panacea

# Установите пакеты Node.js
npm install

# Настройка Python бэкенда
cd packages/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Отредактируйте .env с вашими ключами

# Запустите все
cd ../.. 
docker compose up
```

## Рабочий процесс разработки

1. Создайте ветку функции от `main`
2. Внесите изменения в соответствующую директорию `packages/`
3. Запустите тесты: `make test`
4. Запустите линтеры: `make lint`
5. Откройте запрос на слияние

## Тестирование

```bash
# Все тесты
make test

# Только бэкенд
make test-backend

# Только TypeScript
make test-ts
```

## Стандарты кода

### Python (бэкенд)
- **Ruff** для линтинга (`ruff check .`)
- **Mypy** для проверки типов (`mypy .`)
- **Pytest** для тестов (≥80% покрытия)
- Аннотируйте типы всех новых функций

### TypeScript (фронтенд/cli/sdk)
- **ESLint** для линтинга
- **Vitest** или **Jest** для тестов
- Строгий TypeScript (`"strict": true`)

## CI

GitHub Actions запускается при каждом пуше:
1. Бэкенд: ruff → mypy → pytest (80% порог покрытия)
2. TypeScript: сборка → тесты
3. VS Code: сборка расширения
4. Документация: сборка сайта MkDocs
