# Ikhtisar

**Ourogen** adalah asisten pengkodean AI terpadu dan platform chatbot pribadi. Ini membaca basis kode Anda, mengedit file, menjalankan perintah, meninjau PR, dan menjawab pertanyaan tentang dokumen Anda — tersedia di terminal, IDE, browser, aplikasi desktop, dan ponsel Anda.

## Memulai

Anote berjalan di beberapa platform: CLI, VS Code, web, desktop, dan mobile. Pilih salah satu di bawah ini untuk memulai. Sebagian besar platform berkomunikasi dengan backend Anote yang dihosting atau instance yang dihosting sendiri (lihat [Konfigurasi](getting-started/configuration.md)).

=== "CLI"

    CLI dengan fitur lengkap untuk bekerja dengan Anote langsung di terminal Anda. Ajukan pertanyaan, perbaiki bug, tinjau PR, dan cari basis kode Anda tanpa meninggalkan shell.

    ```bash
    npm install -g @anote-ai/anote
    ```

    Memerlukan Node.js 18 atau lebih baru. Kemudian, di proyek mana pun:

    ```bash
    cd your-project
    anote init
    anote ask "jelaskan basis kode ini"
    ```

    `anote init` memandu Anda melalui pengaturan kunci API dan penyedia LLM yang diinginkan.

    [Lanjutkan dengan Quick Start →](getting-started/quickstart.md)

=== "VS Code"

    Ekstensi VS Code membawa sidebar obrolan, tinjauan perbedaan inline, dan respons streaming langsung ke editor Anda.

    Cari **"Anote"** di pasar Ekstensi VS Code, atau instal melalui:

    ```bash
    code --install-extension anote-ai.anote-ai-coding
    ```

    [Ikhtisar Ekstensi VS Code →](vscode/overview.md)

=== "Web App"

    Antarmuka obrolan browser gaya ChatGPT dengan unggahan dokumen dan Q&A berbasis RAG. Hosting sendiri dengan Docker Compose:

    ```bash
    git clone https://github.com/anote-ai/Panacea
    cd Panacea
    cp packages/backend/.env.example packages/backend/.env
    # Edit .env dengan kunci API Anda
    docker compose up
    ```

    Frontend: `http://localhost:3000` · Backend: `http://localhost:5000`

    [Ikhtisar Web App →](web/overview.md)

=== "Desktop"

    Aplikasi Electron pribadi yang dapat bekerja secara offline. Semua data tetap di mesin Anda, dan ini bekerja dengan model Ollama lokal ketika Anda tidak ingin menghubungi penyedia yang dihosting.

    Unduh rilis terbaru dari [GitHub Releases](https://github.com/anote-ai/Panacea/releases) — tersedia untuk **macOS** (DMG), **Windows** (installer), dan **Linux** (AppImage/DEB/RPM).

    [Ikhtisar Aplikasi Desktop →](desktop/overview.md)

=== "Mobile"

    Klien obrolan iOS dan Android asli yang dibangun dengan Expo.

    ```bash
    cd packages/mobile
    npm install
    npx expo start
    ```

    Pindai kode QR dengan aplikasi Expo Go, atau jalankan di simulator.

    [Ikhtisar Aplikasi Mobile →](mobile/overview.md)

## Apa yang bisa Anda lakukan

??? abstract "Ajukan pertanyaan tentang basis kode Anda"

    ```bash
    anote ask "bagaimana cara kerja middleware otentikasi?"
    anote ask --file src/auth.ts "jelaskan file ini"
    anote ask --compare               # berdampingan di beberapa model
    cat src/handler.py | anote ask "apa yang bisa salah di sini?"
    ```

??? bug "Perbaiki bug secara otomatis"

    `anote fix --loop` mengiterasi terhadap suite pengujian Anda — hingga `--max-iterations` putaran — sampai berhasil, atau memperbaiki satu file dengan `--file`.

    ```bash
    anote fix --loop --max-iterations 5
    ```

??? example "Tinjau permintaan tarik"

    ```bash
    anote review --pr 42
    ```

    Meninjau untuk bug, masalah keamanan, dan kualitas — secara lokal terhadap direktori/file, atau diposting langsung ke PR GitHub.

??? search "Cari basis kode Anda secara semantik"

    ```bash
    anote index              # bangun indeks TF-IDF (jalankan sekali, lalu tetap diperbarui)
    anote search "validasi token JWT"
    ```

??? question "Obrolan dan Q&A tentang dokumen Anda"

    Unggah dokumen di [Web App](web/overview.md) atau [Aplikasi Desktop](desktop/overview.md) dan ajukan pertanyaan terhadapnya — didukung RAG melalui `POST /api/documents/{id}/ask`.

??? tip "Audit untuk masalah keamanan dan kinerja"

    ```bash
    anote security --severity high --fix
    anote perf --focus "database,bundle" --fix
    ```

??? note "Hasilkan changelog dan dokumen, atau jalankan migrasi"

    ```bash
    anote changelog --since v1.2.0
    anote docs src/api.ts --style jsdoc
    anote migrate --from "React 17" --to "React 18"
    ```

??? info "Periksa pengaturan Anda"

    ```bash
    anote doctor
    ```

    Memeriksa Node.js ≥ 18, `ANTHROPIC_API_KEY`, `.anote.json`, `CLAW.md`, dan git.

## Gunakan Anote di mana saja

| Saya ingin... | Opsi terbaik |
|---|---|
| Bekerja dari terminal saya | [CLI](cli/overview.md) |
| Mendapatkan bantuan AI inline di editor saya | [Ekstensi VS Code](vscode/overview.md) |
| Berbicara dengan dokumen di browser | [Web App](web/overview.md) |
| Menjaga semuanya tetap pribadi dan offline | [Aplikasi Desktop](desktop/overview.md) — bekerja dengan model Ollama lokal |
| Berbicara dari ponsel saya | [Aplikasi Mobile](mobile/overview.md) |
| Memanggil Anote dari kode atau skrip saya sendiri | [TypeScript SDK](sdk/typescript.md) atau [Python SDK](sdk/python.md) |
| Mengintegrasikan langsung dengan REST API | [Backend API](api/overview.md) |
| Mengotomatiskan tinjauan PR atau pemeriksaan CI | [CLI: `anote review --pr`](cli/commands.md#anote-review) |

## Penyedia LLM yang Didukung

- **Anthropic** — Claude (`claude-opus-4-8`, `claude-sonnet-4-6`, `claude-haiku-4-5`)
- **OpenAI** — GPT-4o, GPT-4o-mini
- **Google** — Gemini 2.0 Flash, Gemini 1.5 Pro
- **Ollama** — model lokal apa pun (Llama 3, Mistral, dll.)
- **xAI** — Grok

## Langkah Selanjutnya

- [Quick Start](getting-started/quickstart.md) — inisialisasi, ajukan, perbaiki, indeks, tinjau, dan changelog secara berurutan
- [Cara Kerja Panacea](core-concepts/how-it-works.md) — loop agen, alat, dan streaming
- [Mode Izin](use-panacea/permission-modes.md) — kontrol apa yang dapat dilakukan agen tanpa bertanya
- [Alur Kerja Umum](use-panacea/common-workflows.md) — pola langkah demi langkah untuk tugas sehari-hari
- [Konfigurasi](getting-started/configuration.md) — kunci API, pengaturan penyedia, dan `~/.anote/config.json`
- [Perintah CLI](cli/commands.md) — referensi perintah lengkap
- [Backend API](api/overview.md) — endpoint REST yang mendukung setiap platform
- [Arsitektur](development/architecture.md) — bagaimana monorepo dan backend saling terhubung
- [Kontribusi](development/contributing.md) — siapkan repositori untuk pengembangan lokal
