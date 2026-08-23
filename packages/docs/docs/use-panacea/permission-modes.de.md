# Berechtigungsmodi

Panacea hat drei Berechtigungsmodi, die steuern, ob der Agent vor dem Schreiben von Dateien oder dem Ausführen von Befehlen fragt.

| Modus | Verhalten |
|---|---|
| `default` | Bestätigt vor dem Bearbeiten von Dateien oder dem Ausführen von nicht schreibgeschützten Befehlen |
| `acceptEdits` | Akzeptiert Dateiänderungen automatisch, ohne zu fragen |
| `bypassPermissions` | Führt alles ohne Bestätigung aus — vorsichtig verwenden |

Setzen Sie es global oder projektspezifisch:

```bash
anote config set permissionMode acceptEdits
```

oder in `.anote.json`:

```json
{ "permissionMode": "acceptEdits" }
```

## Befehlsüberschreibungen

Die meisten Befehle erfordern keine Änderungen an der globalen Konfiguration — sie verwenden ihre eigenen Flags für dasselbe Konzept:

| Flag | Verfügbar bei | Effekt |
|---|---|---|
| `--auto` | `fix`, `refactor` | Akzeptiert Änderungen nur für diesen Durchlauf automatisch |
| `--dry-run` | `fix`, `docs`, `migrate`, `security`, `perf`, `refactor`, `generate`, `changelog`, `commit`, `review` | Zeigt, was passieren würde, ohne etwas zu schreiben |
| `--no-edit` | `ask` | Nur lesen — der Agent kann Dateien nicht ändern, selbst wenn er möchte |
| `--yes` | `init` | Interaktive Eingabeaufforderungen überspringen, Standardwerte akzeptieren |

`anote fix --loop` impliziert automatisch `acceptEdits`, da es erforderlich ist, über Iterationen hinweg zu bearbeiten, ohne jedes Mal zu fragen.

## Hooks als Richtlinienebene

Für alles, was spezifischer ist als "fragen vs. nicht fragen" — wie das Blockieren von `Bash`-Aufrufen, die einen bestimmten Pfad berühren — verwenden Sie stattdessen einen `preToolUse`-Hook. Siehe [Panacea erweitern](../core-concepts/extend.md).

## Nächste Schritte

- [Wie Panacea funktioniert](../core-concepts/how-it-works.md) — die Agentenschleife, die diese Modi steuert
- [Erforschen Sie das .anote-Verzeichnis](../core-concepts/anote-directory.md) — wo `permissionMode` in der Konfiguration lebt
