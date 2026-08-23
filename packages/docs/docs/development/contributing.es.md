# Contribuyendo

## Configuración

```bash
git clone https://github.com/anote-ai/Panacea
cd Panacea

# Instalar paquetes de Node.js
npm install

# Configurar backend de Python
cd packages/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edita .env con tus claves

# Iniciar todo
cd ../.. 
docker compose up
```

## Flujo de Trabajo de Desarrollo

1. Crea una rama de función desde `main`
2. Realiza tus cambios en el directorio `packages/` correspondiente
3. Ejecuta pruebas: `make test`
4. Ejecuta linters: `make lint`
5. Abre una solicitud de extracción

## Pruebas

```bash
# Todas las pruebas
make test

# Solo backend
make test-backend

# Solo TypeScript
make test-ts
```

## Estándares de Código

### Python (backend)
- **Ruff** para linting (`ruff check .`)
- **Mypy** para verificación de tipos (`mypy .`)
- **Pytest** para pruebas (≥80% de cobertura)
- Anotar tipos en todas las nuevas funciones

### TypeScript (frontend/cli/sdk)
- **ESLint** para linting
- **Vitest** o **Jest** para pruebas
- TypeScript estricto (`"strict": true`)

## CI

GitHub Actions se ejecuta en cada push:
1. Backend: ruff → mypy → pytest (puerta de cobertura del 80%)
2. TypeScript: construir → pruebas
3. VS Code: construir extensión
4. Docs: construir sitio MkDocs
