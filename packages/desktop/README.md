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

## Code signing (releases)

Release builds (`.github/workflows/release.yml`) are unsigned today, which means macOS Gatekeeper and Windows SmartScreen show security warnings on install — see [#295](https://github.com/anote-ai/Panacea/issues/295). Signing is already wired into `forge.config.js` and the release workflow; it activates automatically once these repo secrets exist (**Settings → Secrets and variables → Actions**), no code changes needed:

| Secret | Platform | Description |
|---|---|---|
| `APPLE_CERTIFICATE_P12` | macOS | Base64-encoded Developer ID Application `.p12` certificate (`base64 -i cert.p12 \| pbcopy`) |
| `APPLE_CERTIFICATE_PASSWORD` | macOS | Password the `.p12` was exported with |
| `APPLE_ID` | macOS | Apple ID used for notarization |
| `APPLE_ID_PASSWORD` | macOS | App-specific password for that Apple ID (not the account password) |
| `APPLE_TEAM_ID` | macOS | Apple Developer Team ID |
| `CSC_LINK` | Windows | Base64-encoded Authenticode `.pfx` certificate |
| `CSC_KEY_PASSWORD` | Windows | Password the `.pfx` was exported with |

Requires an active Apple Developer Program membership (for the macOS cert) and a Windows code-signing certificate (standard or EV) — both are paid, and provisioning them is a release-owner task, not something resolvable in code.
