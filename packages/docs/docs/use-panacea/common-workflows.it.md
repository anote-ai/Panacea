# Flussi di lavoro comuni

Modelli passo-passo per attività quotidiane con la CLI di Panacea.

## Esplora un codice sorgente sconosciuto

```bash
anote explain                       # genera un tour CODEBASE.md
anote explain src/auth.ts "come funziona?"
anote index && anote search "validazione JWT"
```

`explain` senza argomenti scrive una panoramica `CODEBASE.md` dell'intero repository. Puntalo su un file o fai una domanda specifica per approfondire.

## Risolvere un bug

```bash
anote fix --error "TypeError: cannot read property 'id' of undefined"
anote fix src/handler.ts "il gestore del webhook perde eventi sotto carico"
anote fix --loop --cmd "npm test"          # continua a iterare finché i test non passano
```

## Scrivere e fare commit

```bash
anote generate "un middleware di limitazione della velocità per Express" -o src/middleware/rateLimit.ts
anote test src/middleware/rateLimit.ts --write
anote commit                                # messaggio di commit generato dall'AI
```

## Rivedere prima di fare push

```bash
anote diff --staged                         # rivedi le modifiche in fase di staging
anote review --pr 42                        # oppure rivedi una PR aperta su GitHub
anote security --severity high              # audit OWASP Top 10
```

## Aprire una pull request

```bash
anote pr --gh                               # genera descrizione, apri con la CLI gh
```

## Rifattorizzare in sicurezza

```bash
anote refactor src/legacy.ts "estrae la logica di validazione in una propria funzione" --dry-run
anote refactor src/legacy.ts "estrae la logica di validazione in una propria funzione" --auto
```

Prova sempre `--dry-run` prima su qualsiasi cosa che non hai ancora revisionato.

## Continua a lavorare mentre fai qualcos'altro

```bash
anote watch "src/**/*.ts"                   # ri-analizza ad ogni salvataggio
```

## Documenta mentre procedi

```bash
anote docs src/api.ts --style jsdoc
anote changelog --since v1.2.0
```

## Prossimi passi

- [Libreria di prompt](prompt-library.md) — punti di partenza da copiare e incollare
- [Comandi CLI](../cli/commands.md) — riferimento completo ai flag
