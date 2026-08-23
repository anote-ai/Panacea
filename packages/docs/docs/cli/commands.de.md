# CLI-Befehle

## `anote ask`

Stellen Sie eine beliebige Frage zu Ihrem Code.

```bash
anote ask "wie funktioniert die Authentifizierungs-Middleware?"
anote ask --file src/auth.ts "erkläre diese Datei"
anote ask --compare  # nebeneinander über mehrere Modelle
cat file.py | anote ask "finde Bugs"
```

## `anote fix`

Beheben Sie Bugs im aktuellen Verzeichnis.

```bash
anote fix
anote fix --loop                    # iterieren, bis die Tests bestehen
anote fix --max-iterations 5        # Iterationen begrenzen
anote fix --file src/broken.ts      # eine bestimmte Datei reparieren
```

## `anote review`

Überprüfen Sie den Code auf Bugs, Sicherheitsprobleme und Qualität.

```bash
anote review                        # aktuelles Verzeichnis überprüfen
anote review --file src/handler.ts  # eine bestimmte Datei überprüfen
anote review --pr 42                # AI-Überprüfung auf GitHub PR posten
```

## `anote index`

Erstellen Sie einen TF-IDF semantischen Suchindex Ihres Codebases.

```bash
anote index              # aktuelles Verzeichnis indizieren
anote index --watch      # auf Änderungen achten und neu indizieren
anote index /path/to/dir # ein bestimmtes Verzeichnis indizieren
```

## `anote search`

Durchsuchen Sie Ihr indiziertes Codebase semantisch.

```bash
anote search "JWT-Token-Validierung"
anote search "Datenbankverbindung" --top 10
anote search "auth middleware" --json
```

## `anote doctor`

Überprüfen Sie Ihre Umgebung auf Konfigurationsprobleme.

```bash
anote doctor
```

Überprüfungen: Node.js ≥ 18, `ANTHROPIC_API_KEY` gesetzt, `.anote.json` vorhanden, `CLAW.md` vorhanden, git installiert.

## `anote changelog`

Generieren Sie einen CHANGELOG.md-Eintrag aus der Git-Historie.

```bash
anote changelog
anote changelog --since v1.2.0
anote changelog --dry-run
```

## `anote docs`

Generieren Sie Dokumentation für nicht dokumentierten Code.

```bash
anote docs
anote docs src/api.ts
anote docs --style jsdoc
anote docs --dry-run
```

## `anote migrate`

AI-unterstützte Migration des Codebases.

```bash
anote migrate --from "React 17" --to "React 18"
anote migrate --from "axios" --to "fetch"
anote migrate --dry-run
```

## `anote security`

Sicherheitsaudit Ihres Codebases (OWASP Top 10).

```bash
anote security
anote security --severity high
anote security --fix
```

## `anote perf`

Leistungsanalyse.

```bash
anote perf
anote perf --focus "datenbank,bundle"
anote perf --fix
```
