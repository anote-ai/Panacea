# Berkontribusi

## Pengaturan

```bash
git clone https://github.com/anote-ai/Panacea
cd Panacea

# Instal paket Node.js
npm install

# Siapkan backend Python
cd packages/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env dengan kunci Anda

# Mulai semuanya
cd ../.. 
docker compose up
```

## Alur Kerja Pengembangan

1. Buat cabang fitur dari `main`
2. Lakukan perubahan Anda di direktori `packages/` yang relevan
3. Jalankan tes: `make test`
4. Jalankan linter: `make lint`
5. Buka permintaan tarik

## Pengujian

```bash
# Semua tes
make test

# Hanya backend
make test-backend

# Hanya TypeScript
make test-ts
```

## Standar Kode

### Python (backend)
- **Ruff** untuk linting (`ruff check .`)
- **Mypy** untuk pemeriksaan tipe (`mypy .`)
- **Pytest** untuk tes (≥80% cakupan)
- Beri anotasi tipe pada semua fungsi baru

### TypeScript (frontend/cli/sdk)
- **ESLint** untuk linting
- **Vitest** atau **Jest** untuk tes
- TypeScript ketat (`"strict": true`)

## CI

GitHub Actions berjalan pada setiap dorongan:
1. Backend: ruff → mypy → pytest (gerbang cakupan 80%)
2. TypeScript: bangun → tes
3. VS Code: bangun ekstensi
4. Dokumen: bangun situs MkDocs
