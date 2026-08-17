# Ikhtisar

**Anote AI** adalah asisten coding AI terpadu dan platform chat pribadi. Ia membaca codebase Anda, mengedit file, menjalankan perintah, meninjau pull request, dan menjawab pertanyaan tentang dokumen Anda — tersedia di terminal, IDE, browser, aplikasi desktop, dan ponsel Anda.

## Memulai

Anote berjalan di beberapa permukaan: CLI, VS Code, web, desktop, dan mobile. Pilih salah satu di bawah ini untuk memulai. Sebagian besar permukaan berkomunikasi dengan backend Anote yang di-hosting atau instance self-hosted Anda sendiri (lihat [Konfigurasi](getting-started/configuration.md)).

=== "CLI"

    CLI dengan fitur lengkap untuk bekerja dengan Anote langsung di terminal Anda. Ajukan pertanyaan, perbaiki bug, tinjau pull request, dan cari codebase Anda tanpa meninggalkan shell.

    ```bash
    npm install -g @anote-ai/anote
    ```

    Membutuhkan Node.js 18 atau lebih baru. Lalu, di proyek mana pun:

    ```bash
    cd your-project
    anote init
    anote ask "explain this codebase"
    ```

    `anote init` memandu Anda mengatur API key dan penyedia LLM pilihan Anda.

    [Lanjutkan dengan Quick Start →](getting-started/quickstart.md)

=== "VS Code"

    Ekstensi VS Code menghadirkan sidebar chat, tinjauan diff inline, dan respons streaming langsung ke editor Anda.

    Cari **"Anote"** di marketplace ekstensi VS Code, atau instal melalui:

    ```bash
    code --install-extension anote-ai.anote-ai-coding
    ```

    [Ikhtisar Ekstensi VS Code →](vscode/overview.md)

=== "Aplikasi Web"

    Antarmuka chat berbasis browser bergaya ChatGPT dengan unggah dokumen dan tanya-jawab berbasis RAG. Self-host dengan Docker Compose:

    ```bash
    git clone https://github.com/anote-ai/Panacea
    cd Panacea
    cp packages/backend/.env.example packages/backend/.env
    # Edit .env dengan API key Anda
    docker compose up
    ```

    Frontend: `http://localhost:3000` · Backend: `http://localhost:5000`

    [Ikhtisar Aplikasi Web →](web/overview.md)

=== "Desktop"

    Aplikasi Electron yang privat dan dapat digunakan secara offline. Semua data tetap berada di mesin Anda, dan bekerja dengan model Ollama lokal saat Anda tidak ingin menggunakan penyedia yang di-hosting.

    Unduh rilis terbaru dari [GitHub Releases](https://github.com/anote-ai/Panacea/releases) — tersedia untuk **macOS** (DMG), **Windows** (installer), dan **Linux** (AppImage/DEB/RPM).

    [Ikhtisar Aplikasi Desktop →](desktop/overview.md)

=== "Mobile"

    Klien chat native iOS dan Android yang dibangun dengan Expo.

    ```bash
    cd packages/mobile
    npm install
    npx expo start
    ```

    Pindai kode QR dengan aplikasi Expo Go, atau jalankan di simulator.

    [Ikhtisar Aplikasi Mobile →](mobile/overview.md)

## Yang dapat Anda lakukan

??? abstract "Mengajukan pertanyaan tentang codebase Anda"

    ```bash
    anote ask "how does the authentication middleware work?"
    anote ask --file src/auth.ts "explain this file"
    anote ask --compare               # perbandingan berdampingan di beberapa model
    cat src/handler.py | anote ask "what could go wrong here?"
    ```

??? bug "Memperbaiki bug secara otomatis"

    `anote fix --loop` melakukan iterasi terhadap test suite Anda — hingga `--max-iterations` putaran — sampai berhasil, atau memperbaiki satu file dengan `--file`.

    ```bash
    anote fix --loop --max-iterations 5
    ```

??? example "Meninjau pull request"

    ```bash
    anote review --pr 42
    ```

    Tinjauan untuk bug, masalah keamanan, dan kualitas — secara lokal terhadap direktori/file, atau diposting langsung ke PR GitHub.

??? search "Mencari codebase Anda secara semantik"

    ```bash
    anote index              # membangun indeks TF-IDF (jalankan sekali, lalu tetap diperbarui)
    anote search "JWT token validation"
    ```

??? question "Chat dan tanya jawab seputar dokumen Anda"

    Unggah dokumen di [Aplikasi Web](web/overview.md) atau [Aplikasi Desktop](desktop/overview.md) dan ajukan pertanyaan tentangnya — berbasis RAG melalui `POST /api/documents/{id}/ask`.

??? tip "Mengaudit masalah keamanan dan performa"

    ```bash
    anote security --severity high --fix
    anote perf --focus "database,bundle" --fix
    ```

??? note "Menghasilkan changelog dan dokumentasi, atau menjalankan migrasi"

    ```bash
    anote changelog --since v1.2.0
    anote docs src/api.ts --style jsdoc
    anote migrate --from "React 17" --to "React 18"
    ```

??? info "Memeriksa konfigurasi Anda"

    ```bash
    anote doctor
    ```

    Memeriksa Node.js ≥ 18, `ANTHROPIC_API_KEY`, `.anote.json`, `CLAW.md`, dan git.

## Gunakan Anote di mana saja

| Saya ingin... | Pilihan terbaik |
|---|---|
| Bekerja dari terminal saya | [CLI](cli/overview.md) |
| Mendapatkan bantuan AI langsung di editor saya | [Ekstensi VS Code](vscode/overview.md) |
| Chat dengan dokumen di browser | [Aplikasi Web](web/overview.md) |
| Menjaga semuanya tetap privat dan offline | [Aplikasi Desktop](desktop/overview.md) — bekerja dengan model Ollama lokal |
| Chat dari ponsel saya | [Aplikasi Mobile](mobile/overview.md) |
| Memanggil Anote dari kode atau skrip saya sendiri | [TypeScript SDK](sdk/typescript.md) atau [Python SDK](sdk/python.md) |
| Berintegrasi langsung dengan REST API | [Backend API](api/overview.md) |
| Mengotomatiskan tinjauan PR atau pemeriksaan CI | [CLI: `anote review --pr`](cli/commands.md#anote-review) |

## Penyedia LLM yang didukung

- **Anthropic** — Claude (`claude-opus-4-8`, `claude-sonnet-4-6`, `claude-haiku-4-5`)
- **OpenAI** — GPT-4o, GPT-4o-mini
- **Google** — Gemini 2.0 Flash, Gemini 1.5 Pro
- **Ollama** — model lokal apa pun (Llama 3, Mistral, dll.)
- **xAI** — Grok

## Langkah selanjutnya

- [Quick Start](getting-started/quickstart.md) — init, ask, fix, index, review, dan changelog secara berurutan
- [Cara Kerja Panacea](core-concepts/how-it-works.md) — loop agentic, tools, dan streaming
- [Mode Izin](use-panacea/permission-modes.md) — kendalikan apa yang bisa dilakukan agent tanpa bertanya
- [Alur Kerja Umum](use-panacea/common-workflows.md) — pola langkah demi langkah untuk tugas sehari-hari
- [Konfigurasi](getting-started/configuration.md) — API key, pengaturan penyedia, dan `~/.anote/config.json`
- [Perintah CLI](cli/commands.md) — referensi perintah lengkap
- [Backend API](api/overview.md) — endpoint REST yang mendukung setiap permukaan
- [Arsitektur](development/architecture.md) — bagaimana monorepo dan backend saling terhubung
- [Berkontribusi](development/contributing.md) — mengatur repo untuk pengembangan lokal
