# Anote AI Desktop

A private desktop AI assistant. All data stays on your machine.

## Development

```bash
# Install dependencies
cd packages/desktop
npm install
cd frontend && npm install
cd ..

# Start Electron + Vite frontend.
# The Electron main process will launch packages/backend/app.py on port 5099.
npm run dev
```

If you want to debug the backend separately, start it like this instead:

```bash
cd packages/backend
PORT=5099 python app.py
```

## Building

```bash
# Bundle Python backend
cd packages/backend
pyinstaller ../desktop/app.spec --distpath ../desktop/backend-dist

# Build Electron app
cd packages/desktop
npm run make
```

Outputs in `out/` directory.
