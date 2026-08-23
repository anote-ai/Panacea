# Häufige Arbeitsabläufe

Schritt-für-Schritt-Muster für alltägliche Aufgaben mit Panacea's CLI.

## Erkunde einen unbekannten Codebestand

```bash
anote explain                       # generiere eine CODEBASE.md Tour
anote explain src/auth.ts "wie funktioniert das?"
anote index && anote search "JWT-Validierung"
```

`explain` ohne Argumente schreibt eine `CODEBASE.md` Übersicht des gesamten Repos. Zeige auf eine Datei oder stelle eine spezifische Frage, um tiefer einzutauchen.

## Behebe einen Fehler

```bash
anote fix --error "TypeError: cannot read property 'id' of undefined"
anote fix src/handler.ts "der Webhook-Handler verwirft Ereignisse unter Last"
anote fix --loop --cmd "npm test"          # weiter iterieren, bis die Tests bestehen
```

## Schreiben und committen

```bash
anote generate "ein Rate Limiter Middleware für Express" -o src/middleware/rateLimit.ts
anote test src/middleware/rateLimit.ts --write
anote commit                                # AI-generierte Commit-Nachricht
```

## Überprüfen, bevor du pushst

```bash
anote diff --staged                         # überprüfe die gestagten Änderungen
anote review --pr 42                        # oder überprüfe einen offenen GitHub PR
anote security --severity high              # OWASP Top 10 Audit
```

## Öffne einen Pull-Request

```bash
anote pr --gh                               # generiere Beschreibung, öffne mit gh CLI
```

## Sicher refaktorisieren

```bash
anote refactor src/legacy.ts "extrahiere die Validierungslogik in eine eigene Funktion" --dry-run
anote refactor src/legacy.ts "extrahiere die Validierungslogik in eine eigene Funktion" --auto
```

Versuche immer zuerst `--dry-run` bei allem, was du noch nicht überprüft hast.

## Weiterarbeiten, während du etwas anderes tust

```bash
anote watch "src/**/*.ts"                   # bei jedem Speichern erneut analysieren
```

## Dokumentiere während du arbeitest

```bash
anote docs src/api.ts --style jsdoc
anote changelog --since v1.2.0
```

## Nächste Schritte

- [Prompt-Bibliothek](prompt-library.md) — Kopier- und Einfüge-Startpunkte
- [CLI-Befehle](../cli/commands.md) — vollständige Flaggenreferenz
