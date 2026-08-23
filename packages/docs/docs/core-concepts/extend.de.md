# Panacea erweitern

Zwei Möglichkeiten, wie Sie das Verhalten von Panacea in Ihrem Projekt anpassen können: **CLAW.md** für persistente Anweisungen und **Hooks** zum Ausführen eigener Befehle rund um Toolaufrufe.

## CLAW.md — Projektgedächtnis

`CLAW.md` ist eine Markdown-Datei, die Panacea für den Projektkontext liest — die gleiche Idee wie eine README, die sich an den Agenten anstelle eines Menschen richtet. `anote init` generiert automatisch eine, die mit Ihrem erkannten Stack und den Verifizierungsbefehlen (Test/Lint/Bau) vorgefüllt ist:

```markdown
# CLAW.md

Diese Datei bietet Anleitungen für Anote AI, wenn sie mit Code in diesem Repository arbeitet.

## Projektübersicht

<!-- Beschreiben Sie, was dieses Projekt tut -->

## Stack

TypeScript · Next.js

## Verifizierung

Führen Sie diese aus, bevor Sie eine Änderung als abgeschlossen betrachten:

  npm test
  npm run lint

## Arbeitsvereinbarung

- Relevante Dateien lesen, bevor Änderungen vorgenommen werden
- Die Verifizierungsbefehle nach der Änderung der Logik ausführen
- Änderungen klein und fokussiert halten
- Bevorzugen Sie das Bearbeiten vorhandener Dateien gegenüber dem Erstellen neuer Dateien
```

Bearbeiten Sie es nach Belieben — fügen Sie Architekturhinweise, Konventionen oder Dinge hinzu, die der Agent immer wieder falsch macht. Panacea liest es zu Beginn jeder Sitzung in diesem Verzeichnis.

## Hooks — Führen Sie eigene Befehle rund um Toolaufrufe aus

Hooks führen einen Shell-Befehl vor (`preToolUse`) oder nach (`postToolUse`) jedem Toolaufruf aus, konfiguriert in `.anote.json`:

```json
{
  "hooks": {
    "preToolUse": ["./scripts/check-tool-policy.sh"],
    "postToolUse": ["npx prettier --write ."]
  }
}
```

**Semantik des Exit-Codes:**

| Exit-Code | Effekt |
|---|---|
| `0` | Erlauben — stdout wird als Informationsnachricht erfasst |
| `2` | Verweigern — stdout wird als Grund erfasst, der dem Agenten angezeigt wird |
| alles andere | Warnen, aber erlauben |

Verwenden Sie `preToolUse`, um riskante Befehle zu blockieren oder Richtlinien durchzusetzen, bevor sie ausgeführt werden; verwenden Sie `postToolUse` für Dinge wie automatisches Formatieren nach jeder Bearbeitung.

## Nächste Schritte

- [Erforschen Sie das .anote-Verzeichnis](anote-directory.md) — wo CLAW.md und die Konfiguration leben
- [Berechtigungsmodi](../use-panacea/permission-modes.md) — der andere Hebel, was der Agent tun kann
