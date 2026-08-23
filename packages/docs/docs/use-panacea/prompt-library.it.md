# Libreria di Prompt

Copia e incolla i prompt per `anote ask`, `anote chat` e `anote fix`, organizzati per compito.

## Comprendere il codice

```bash
anote ask "cosa fa questa base di codice, a un livello alto?"
anote ask --file src/payments/webhook.ts "guidami attraverso questo file riga per riga"
anote ask "dove è configurato il limitatore di velocità e quali sono i limiti?"
anote ask "cosa si romperebbe se rimuovessi il livello di caching qui?"
```

## Debugging

```bash
anote fix --error "$(cat error.log)"
anote ask "perché questo test fallisce in modo intermittente ma non in modo consistente?"
anote fix src/db/pool.ts "le connessioni non vengono restituite al pool"
```

## Revisione del codice

```bash
anote review --file src/auth/session.ts
anote review --pr 42
anote diff --staged -c "concentrati sulla gestione degli errori e sui casi limite"
```

## Refactoring

```bash
anote refactor src/utils.ts "dividi questo in funzioni più piccole e con uno scopo singolo" --dry-run
anote ask "c'è un modo più semplice per esprimere questa logica?" --file src/parser.ts
anote migrate --from "moment" --to "date-fns"
```

## Scrivere test

```bash
anote test src/utils/validate.ts --coverage --write
anote ask "quali casi limite mi mancano per questa funzione?" --file src/utils/validate.ts
```

## Sicurezza e prestazioni

```bash
anote security --severity high
anote perf --focus "database,bundle size"
```

## Documentazione

```bash
anote docs src/api/client.ts --style jsdoc
anote changelog --since v1.2.0
anote explain --stdout                       # riepilogo rapido dell'architettura
```

## Prossimi passi

- [Flussi di lavoro comuni](common-workflows.md)
- [Comandi CLI](../cli/commands.md)
