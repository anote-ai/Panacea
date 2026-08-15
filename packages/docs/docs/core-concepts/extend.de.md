# Panacea erweitern

Zwei Möglichkeiten, das Verhalten von Panacea in Ihrem Projekt anzupassen: **CLAW.md** für dauerhafte Anweisungen und **Hooks** zum Ausführen eigener Befehle rund um Tool-Aufrufe.

## CLAW.md — Projektgedächtnis

`CLAW.md` ist eine Markdown-Datei, die Panacea für den Projektkontext liest — dieselbe Idee wie eine README, nur für den Agenten statt für Menschen. `anote init` generiert automatisch eine, vorausgefüllt mit Ihrem erkannten Stack und Verifizierungsbefehlen (test/lint/build):

```markdown
# CLAW.md

This file provides guidance to Anote AI when working with code in this repository.

## Project overview

<!-- Describe what this project does -->

## Stack

TypeScript · Next.js

## Verification

Run these before considering a change complete:

  npm test
  npm run lint

## Working agreement

- Read relevant files before making changes
- Run the verification commands after modifying logic
- Keep changes small and focused
- Prefer editing existing files over creating new ones
```

Bearbeiten Sie sie frei — fügen Sie Architekturnotizen, Konventionen oder Dinge hinzu, bei denen der Agent immer wieder Fehler macht. Panacea liest sie zu Beginn jeder Sitzung in diesem Verzeichnis.

## Hooks — eigene Befehle rund um Tool-Aufrufe ausführen

Hooks führen einen Shell-Befehl vor (`preToolUse`) oder nach (`postToolUse`) jedem Tool-Aufruf aus, konfiguriert in `.anote.json`:

```json
{
  "hooks": {
    "preToolUse": ["./scripts/check-tool-policy.sh"],
    "postToolUse": ["npx prettier --write ."]
  }
}
```

**Exit-Code-Semantik:**

| Exit-Code | Wirkung |
|---|---|
| `0` | Erlauben — stdout wird als informative Nachricht erfasst |
| `2` | Verweigern — stdout wird als Begründung erfasst und dem Agenten angezeigt |
| alles andere | Warnen, aber erlauben |

Verwenden Sie `preToolUse`, um riskante Befehle zu blockieren oder Richtlinien vor der Ausführung durchzusetzen; verwenden Sie `postToolUse` für Dinge wie automatische Formatierung nach jeder Änderung.

## Nächste Schritte

- [Das .anote-Verzeichnis erkunden](anote-directory.md) — wo CLAW.md und die Konfiguration liegen
- [Berechtigungsmodi](../use-panacea/permission-modes.md) — der andere Hebel für das, was der Agent tun darf
