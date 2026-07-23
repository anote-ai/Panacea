# Anote AI Desktop

A private desktop AI assistant. All data stays on your machine.

## Development

```bash
# Install dependencies
npm install
cd frontend && npm install

# Start (dev mode - requires Python backend running separately)
cd packages/backend && python app.py --port 5099 &
npm run dev
```

## Testing

```bash
cd packages/desktop/frontend
npm test
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

### Code signing (release builds)

Unsigned builds work fine for local testing, but unsigned macOS apps are blocked by
Gatekeeper and unsigned Windows installers trigger SmartScreen warnings for other users.
Auto-update (`update-electron-app`, wired up in `main.js`) also requires a signed macOS
build to apply updates. Set these env vars before `npm run make` to produce signed
artifacts — `forge.config.js` picks them up automatically and falls back to unsigned
builds when they're unset:

| Variable | Purpose |
|---|---|
| `APPLE_SIGNING_IDENTITY` | macOS codesigning identity, e.g. `Developer ID Application: Your Name (TEAMID)` |
| `APPLE_ID` | Apple ID for notarization |
| `APPLE_ID_PASSWORD` | App-specific password for that Apple ID |
| `APPLE_TEAM_ID` | Apple Developer team ID |
| `WINDOWS_CERTIFICATE_FILE` | Path to a `.pfx` Authenticode certificate |
| `WINDOWS_CERTIFICATE_PASSWORD` | Password for that certificate |

## Provider API keys (BYOK)

Users can add their own Anthropic/OpenAI/Google API keys from the sidebar's
**API keys** button — they're encrypted server-side and used instead of the
shared server key configured in the backend's `.env`. Without either a
user-supplied key or a server-side `ANTHROPIC_API_KEY`/`OPENAI_API_KEY`, chat
requests will fail, since the packaged app has no bundled default key.
