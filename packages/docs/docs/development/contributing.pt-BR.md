# Contribuindo

## Configuração

```bash
git clone https://github.com/anote-ai/Panacea
cd Panacea

# Instalar pacotes do Node.js
npm install

# Configurar backend em Python
cd packages/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edite .env com suas chaves

# Iniciar tudo
cd ../.. 
docker compose up
```

## Fluxo de Trabalho de Desenvolvimento

1. Crie uma branch de recurso a partir de `main`
2. Faça suas alterações no diretório relevante `packages/`
3. Execute os testes: `make test`
4. Execute os linters: `make lint`
5. Abra um pull request

## Testes

```bash
# Todos os testes
make test

# Somente backend
make test-backend

# Somente TypeScript
make test-ts
```

## Padrões de Código

### Python (backend)
- **Ruff** para linting (`ruff check .`)
- **Mypy** para verificação de tipos (`mypy .`)
- **Pytest** para testes (≥80% de cobertura)
- Anote todos os novos tipos de funções

### TypeScript (frontend/cli/sdk)
- **ESLint** para linting
- **Vitest** ou **Jest** para testes
- TypeScript estrito (`"strict": true`)

## CI

O GitHub Actions é executado em cada push:
1. Backend: ruff → mypy → pytest (gate de 80% de cobertura)
2. TypeScript: build → testes
3. VS Code: build da extensão
4. Docs: build do site MkDocs
