# Comandi CLI

## `anote ask`

Fai qualsiasi domanda sul tuo codice.

```bash
anote ask "come funziona il middleware di autenticazione?"
anote ask --file src/auth.ts "spiega questo file"
anote ask --compare  # affianca più modelli
cat file.py | anote ask "trova bug"
```

## `anote fix`

Correggi i bug nella directory corrente.

```bash
anote fix
anote fix --loop                    # itera fino a quando i test non passano
anote fix --max-iterations 5        # limita le iterazioni
anote fix --file src/broken.ts      # correggi un file specifico
```

## `anote review`

Esamina il codice per bug, problemi di sicurezza e qualità.

```bash
anote review                        # esamina la directory corrente
anote review --file src/handler.ts  # esamina un file specifico
anote review --pr 42                # pubblica la revisione AI su GitHub PR
```

## `anote index`

Costruisci un indice di ricerca semantica TF-IDF del tuo codice.

```bash
anote index              # indicizza la directory corrente
anote index --watch      # monitora le modifiche e ri-indicizza
anote index /path/to/dir # indicizza una directory specifica
```

## `anote search`

Cerca nel tuo codice indicizzato in modo semantico.

```bash
anote search "validazione del token JWT"
anote search "connessione al database" --top 10
anote search "middleware di autenticazione" --json
```

## `anote doctor`

Controlla il tuo ambiente per problemi di configurazione.

```bash
anote doctor
```

Controlli: Node.js ≥ 18, `ANTHROPIC_API_KEY` impostato, `.anote.json` presente, `CLAW.md` presente, git installato.

## `anote changelog`

Genera un'entrata CHANGELOG.md dalla cronologia git.

```bash
anote changelog
anote changelog --since v1.2.0
anote changelog --dry-run
```

## `anote docs`

Genera documentazione per codice non documentato.

```bash
anote docs
anote docs src/api.ts
anote docs --style jsdoc
anote docs --dry-run
```

## `anote migrate`

Migrazione del codice assistita da AI.

```bash
anote migrate --from "React 17" --to "React 18"
anote migrate --from "axios" --to "fetch"
anote migrate --dry-run
```

## `anote security`

Audit di sicurezza del tuo codice (OWASP Top 10).

```bash
anote security
anote security --severity high
anote security --fix
```

## `anote perf`

Analisi delle prestazioni.

```bash
anote perf
anote perf --focus "database,bundle"
anote perf --fix
```
