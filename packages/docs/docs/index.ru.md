# Обзор

**Anote AI** — это единый ИИ-ассистент для программирования и приватная платформа для чата. Он читает вашу кодовую базу, редактирует файлы, выполняет команды, проверяет pull request'ы и отвечает на вопросы по вашим документам — доступен в терминале, IDE, браузере, десктопном приложении и на телефоне.

## Начало работы

Anote работает на нескольких платформах: CLI, VS Code, веб, десктоп и мобильные устройства. Выберите одну из них ниже, чтобы начать. Большинство платформ обращаются к размещённому бэкенду Anote или к вашему собственному самостоятельно размещённому экземпляру (см. [Конфигурация](getting-started/configuration.md)).

=== "CLI"

    Полнофункциональный CLI для работы с Anote прямо в терминале. Задавайте вопросы, исправляйте ошибки, проверяйте pull request'ы и ищите по кодовой базе, не покидая оболочку.

    ```bash
    npm install -g @anote-ai/anote
    ```

    Требуется Node.js 18 или новее. Затем в любом проекте:

    ```bash
    cd your-project
    anote init
    anote ask "explain this codebase"
    ```

    `anote init` проведёт вас через настройку API-ключа и предпочитаемого LLM-провайдера.

    [Перейти к Быстрому старту →](getting-started/quickstart.md)

=== "VS Code"

    Расширение VS Code добавляет боковую панель чата, встроенный просмотр diff и потоковые ответы прямо в редактор.

    Найдите **«Anote»** в маркетплейсе расширений VS Code или установите через:

    ```bash
    code --install-extension anote-ai.anote-ai-coding
    ```

    [Обзор расширения VS Code →](vscode/overview.md)

=== "Веб-приложение"

    Браузерный чат-интерфейс в стиле ChatGPT с загрузкой документов и вопросами-ответами на основе RAG. Разверните самостоятельно с помощью Docker Compose:

    ```bash
    git clone https://github.com/anote-ai/Panacea
    cd Panacea
    cp packages/backend/.env.example packages/backend/.env
    # Отредактируйте .env, указав свои API-ключи
    docker compose up
    ```

    Фронтенд: `http://localhost:3000` · Бэкенд: `http://localhost:5000`

    [Обзор веб-приложения →](web/overview.md)

=== "Десктоп"

    Приватное, работающее офлайн приложение на Electron. Все данные остаются на вашем компьютере, а также оно работает с локальными моделями Ollama, если вы не хотите обращаться к размещённому провайдеру.

    Скачайте последнюю версию с [GitHub Releases](https://github.com/anote-ai/Panacea/releases) — доступно для **macOS** (DMG), **Windows** (установщик) и **Linux** (AppImage/DEB/RPM).

    [Обзор десктопного приложения →](desktop/overview.md)

=== "Мобильное"

    Нативный клиент чата для iOS и Android, созданный на Expo.

    ```bash
    cd packages/mobile
    npm install
    npx expo start
    ```

    Отсканируйте QR-код приложением Expo Go или запустите в симуляторе.

    [Обзор мобильного приложения →](mobile/overview.md)

## Что вы можете делать

??? abstract "Задавать вопросы о вашей кодовой базе"

    ```bash
    anote ask "how does the authentication middleware work?"
    anote ask --file src/auth.ts "explain this file"
    anote ask --compare               # сравнение нескольких моделей бок о бок
    cat src/handler.py | anote ask "what could go wrong here?"
    ```

??? bug "Автоматически исправлять ошибки"

    `anote fix --loop` итеративно прогоняет вашу тестовую сборку — до `--max-iterations` раундов — пока она не пройдёт, или исправляет один файл с помощью `--file`.

    ```bash
    anote fix --loop --max-iterations 5
    ```

??? example "Проверять pull request'ы"

    ```bash
    anote review --pr 42
    ```

    Проверки на ошибки, проблемы безопасности и качество — локально для директории/файла, либо публикуются прямо в GitHub PR.

??? search "Семантический поиск по кодовой базе"

    ```bash
    anote index              # построить TF-IDF индекс (один раз, затем поддерживается актуальным)
    anote search "JWT token validation"
    ```

??? question "Общаться и задавать вопросы по документам"

    Загружайте документы в [веб-приложении](web/overview.md) или [десктопном приложении](desktop/overview.md) и задавайте по ним вопросы — на основе RAG через `POST /api/documents/{id}/ask`.

??? tip "Проверять безопасность и производительность"

    ```bash
    anote security --severity high --fix
    anote perf --focus "database,bundle" --fix
    ```

??? note "Генерировать changelog и документацию, или выполнять миграции"

    ```bash
    anote changelog --since v1.2.0
    anote docs src/api.ts --style jsdoc
    anote migrate --from "React 17" --to "React 18"
    ```

??? info "Проверять настройку окружения"

    ```bash
    anote doctor
    ```

    Проверяет Node.js ≥ 18, `ANTHROPIC_API_KEY`, `.anote.json`, `CLAW.md` и git.

## Используйте Anote везде

| Я хочу... | Лучший вариант |
|---|---|
| Работать из терминала | [CLI](cli/overview.md) |
| Получать помощь ИИ прямо в редакторе | [Расширение VS Code](vscode/overview.md) |
| Общаться с документами в браузере | [Веб-приложение](web/overview.md) |
| Держать всё приватным и офлайн | [Десктопное приложение](desktop/overview.md) — работает с локальными моделями Ollama |
| Общаться с телефона | [Мобильное приложение](mobile/overview.md) |
| Вызывать Anote из своего кода или скриптов | [TypeScript SDK](sdk/typescript.md) или [Python SDK](sdk/python.md) |
| Интегрироваться напрямую с REST API | [Backend API](api/overview.md) |
| Автоматизировать проверку PR или CI-проверки | [CLI: `anote review --pr`](cli/commands.md#anote-review) |

## Поддерживаемые LLM-провайдеры

- **Anthropic** — Claude (`claude-opus-4-8`, `claude-sonnet-4-6`, `claude-haiku-4-5`)
- **OpenAI** — GPT-4o, GPT-4o-mini
- **Google** — Gemini 2.0 Flash, Gemini 1.5 Pro
- **Ollama** — любая локальная модель (Llama 3, Mistral и др.)
- **xAI** — Grok

## Дальнейшие шаги

- [Быстрый старт](getting-started/quickstart.md) — init, ask, fix, index, review и changelog по порядку
- [Как работает Panacea](core-concepts/how-it-works.md) — агентный цикл, инструменты и потоковая передача
- [Режимы разрешений](use-panacea/permission-modes.md) — контролируйте, что агент может делать без запроса
- [Типовые сценарии работы](use-panacea/common-workflows.md) — пошаговые схемы для повседневных задач
- [Конфигурация](getting-started/configuration.md) — API-ключи, настройка провайдера и `~/.anote/config.json`
- [Команды CLI](cli/commands.md) — полный справочник команд
- [Backend API](api/overview.md) — REST-эндпоинты, обслуживающие все платформы
- [Архитектура](development/architecture.md) — как связаны монорепозиторий и бэкенд
- [Участие в разработке](development/contributing.md) — настройка репозитория для локальной разработки
