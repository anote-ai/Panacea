# Обзор

**Ourogen** — это унифицированный AI помощник по программированию и платформа для частных чат-ботов. Он читает вашу кодовую базу, редактирует файлы, выполняет команды, проверяет PR и отвечает на вопросы по вашим документам — доступен в вашем терминале, IDE, браузере, настольном приложении и на телефоне.

## Начало работы

Anote работает на нескольких платформах: CLI, VS Code, веб, настольный и мобильный. Выберите один из вариантов ниже, чтобы начать. Большинство платформ взаимодействуют с размещенным бэкендом Anote или вашей собственной саморазмещенной инстанцией (см. [Конфигурация](getting-started/configuration.md)).

=== "CLI"

    Полнофункциональный CLI для работы с Anote непосредственно в вашем терминале. Задавайте вопросы, исправляйте ошибки, проверяйте PR и ищите в вашей кодовой базе, не покидая оболочку.

    ```bash
    npm install -g @anote-ai/anote
    ```

    Требуется Node.js 18 или новее. Затем, в любом проекте:

    ```bash
    cd your-project
    anote init
    anote ask "объясните эту кодовую базу"
    ```

    `anote init` проведет вас через настройку вашего API ключа и предпочтительного поставщика LLM.

    [Продолжить с Быстрым стартом →](getting-started/quickstart.md)

=== "VS Code"

    Расширение для VS Code добавляет боковую панель чата, просмотр различий в коде и потоковые ответы непосредственно в ваш редактор.

    Найдите **"Anote"** в маркетплейсе расширений VS Code или установите через:

    ```bash
    code --install-extension anote-ai.anote-ai-coding
    ```

    [Обзор расширения VS Code →](vscode/overview.md)

=== "Веб-приложение"

    Интерфейс чата в браузере в стиле ChatGPT с загрузкой документов и поддержкой вопросов и ответов на основе RAG. Самостоятельно разместите его с помощью Docker Compose:

    ```bash
    git clone https://github.com/anote-ai/Panacea
    cd Panacea
    cp packages/backend/.env.example packages/backend/.env
    # Отредактируйте .env с вашими API ключами
    docker compose up
    ```

    Фронтенд: `http://localhost:3000` · Бэкенд: `http://localhost:5000`

    [Обзор веб-приложения →](web/overview.md)

=== "Настольное приложение"

    Частное приложение на Electron с возможностью работы в оффлайне. Все данные остаются на вашем компьютере, и оно работает с локальными моделями Ollama, когда вы не хотите обращаться к размещенному провайдеру.

    Скачайте последнюю версию с [GitHub Releases](https://github.com/anote-ai/Panacea/releases) — доступно для **macOS** (DMG), **Windows** (установщик) и **Linux** (AppImage/DEB/RPM).

    [Обзор настольного приложения →](desktop/overview.md)

=== "Мобильное приложение"

    Нативный клиент чата для iOS и Android, созданный с помощью Expo.

    ```bash
    cd packages/mobile
    npm install
    npx expo start
    ```

    Сканируйте QR-код с помощью приложения Expo Go или запустите в симуляторе.

    [Обзор мобильного приложения →](mobile/overview.md)

## Что вы можете сделать

??? abstract "Задавайте вопросы о вашей кодовой базе"

    ```bash
    anote ask "как работает промежуточное ПО аутентификации?"
    anote ask --file src/auth.ts "объясните этот файл"
    anote ask --compare               # сравнение между несколькими моделями
    cat src/handler.py | anote ask "что может пойти не так здесь?"
    ```

??? bug "Автоматически исправляйте ошибки"

    `anote fix --loop` выполняет итерации против вашего тестового набора — до `--max-iterations` раундов — пока не пройдет, или исправляет один файл с помощью `--file`.

    ```bash
    anote fix --loop --max-iterations 5
    ```

??? example "Проверяйте запросы на слияние"

    ```bash
    anote review --pr 42
    ```

    Проверяет на наличие ошибок, проблем с безопасностью и качества — локально против директории/файла или отправляет прямо в PR на GitHub.

??? search "Ищите в вашей кодовой базе семантически"

    ```bash
    anote index              # создайте индекс TF-IDF (запустите один раз, затем поддерживайте в актуальном состоянии)
    anote search "JWT token validation"
    ```

??? question "Чат и вопросы-ответы по вашим документам"

    Загружайте документы в [Веб-приложение](web/overview.md) или [Настольное приложение](desktop/overview.md) и задавайте им вопросы — поддержка RAG через `POST /api/documents/{id}/ask`.

??? tip "Аудит на наличие проблем с безопасностью и производительностью"

    ```bash
    anote security --severity high --fix
    anote perf --focus "database,bundle" --fix
    ```

??? note "Генерируйте журналы изменений и документацию или выполняйте миграции"

    ```bash
    anote changelog --since v1.2.0
    anote docs src/api.ts --style jsdoc
    anote migrate --from "React 17" --to "React 18"
    ```

??? info "Проверьте вашу настройку"

    ```bash
    anote doctor
    ```

    Проверяет Node.js ≥ 18, `ANTHROPIC_API_KEY`, `.anote.json`, `CLAW.md` и git.

## Используйте Anote везде

| Я хочу... | Лучший вариант |
|---|---|
| Работать из моего терминала | [CLI](cli/overview.md) |
| Получать встроенную помощь AI в моем редакторе | [Расширение VS Code](vscode/overview.md) |
| Общаться с документами в браузере | [Веб-приложение](web/overview.md) |
| Держать все приватно и оффлайн | [Настольное приложение](desktop/overview.md) — работает с локальными моделями Ollama |
| Общаться с телефона | [Мобильное приложение](mobile/overview.md) |
| Вызывать Anote из моего собственного кода или скриптов | [TypeScript SDK](sdk/typescript.md) или [Python SDK](sdk/python.md) |
| Интегрироваться напрямую с REST API | [Backend API](api/overview.md) |
| Автоматизировать проверку PR или CI | [CLI: `anote review --pr`](cli/commands.md#anote-review) |

## Поддерживаемые поставщики LLM

- **Anthropic** — Claude (`claude-opus-4-8`, `claude-sonnet-4-6`, `claude-haiku-4-5`)
- **OpenAI** — GPT-4o, GPT-4o-mini
- **Google** — Gemini 2.0 Flash, Gemini 1.5 Pro
- **Ollama** — любая локальная модель (Llama 3, Mistral и т.д.)
- **xAI** — Grok

## Следующие шаги

- [Быстрый старт](getting-started/quickstart.md) — инициализация, вопросы, исправления, индексация, обзор и журналы изменений по порядку
- [Как работает Panacea](core-concepts/how-it-works.md) — агентный цикл, инструменты и потоковая передача
- [Режимы разрешений](use-panacea/permission-modes.md) — контроль того, что агент может делать без запроса
- [Общие рабочие процессы](use-panacea/common-workflows.md) — пошаговые схемы для повседневных задач
- [Конфигурация](getting-started/configuration.md) — API ключи, настройка поставщика и `~/.anote/config.json`
- [Команды CLI](cli/commands.md) — полный справочник команд
- [Backend API](api/overview.md) — REST конечные точки, поддерживающие каждую платформу
- [Архитектура](development/architecture.md) — как монорепозиторий и бэкенд сочетаются
- [Участие](development/contributing.md) — настройка репозитория для локальной разработки
