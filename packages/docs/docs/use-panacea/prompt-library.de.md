# Prompt-Bibliothek

Kopieren und Einfügen von Eingabeaufforderungen für `anote ask`, `anote chat` und `anote fix`, organisiert nach Aufgaben.

## Verständnis von Code

```bash
anote ask "was macht dieser Codebestand auf hoher Ebene?"
anote ask --file src/payments/webhook.ts "erkläre mir diese Datei Zeile für Zeile"
anote ask "wo ist der Ratenbegrenzer konfiguriert und was sind die Grenzen?"
anote ask "was würde kaputtgehen, wenn ich die Caching-Schicht hier entfernen würde?"
```

## Debugging

```bash
anote fix --error "$(cat error.log)"
anote ask "warum schlägt dieser Test sporadisch fehl, aber nicht konstant?"
anote fix src/db/pool.ts "Verbindungen werden nicht zurück zum Pool freigegeben"
```

## Code-Überprüfung

```bash
anote review --file src/auth/session.ts
anote review --pr 42
anote diff --staged -c "konzentriere dich auf Fehlerbehandlung und Randfälle"
```

## Refactoring

```bash
anote refactor src/utils.ts "teile dies in kleinere, einzweckige Funktionen auf" --dry-run
anote ask "gibt es einen einfacheren Weg, diese Logik auszudrücken?" --file src/parser.ts
anote migrate --from "moment" --to "date-fns"
```

## Tests schreiben

```bash
anote test src/utils/validate.ts --coverage --write
anote ask "welche Randfälle fehlen mir für diese Funktion?" --file src/utils/validate.ts
```

## Sicherheit und Leistung

```bash
anote security --severity high
anote perf --focus "datenbank,bündelgröße"
```

## Dokumentation

```bash
anote docs src/api/client.ts --style jsdoc
anote changelog --since v1.2.0
anote explain --stdout                       # schnelle Architekturübersicht
```

## Nächste Schritte

- [Häufige Arbeitsabläufe](common-workflows.md)
- [CLI-Befehle](../cli/commands.md)
