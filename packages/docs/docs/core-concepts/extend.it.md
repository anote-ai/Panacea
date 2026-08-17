# Estendere Panacea

Due modi per personalizzare il comportamento di Panacea nel tuo progetto: **CLAW.md** per istruzioni persistenti, e gli **hook** per eseguire i tuoi comandi attorno alle chiamate degli strumenti.

## CLAW.md — memoria del progetto

`CLAW.md` è un file markdown che Panacea legge per il contesto del progetto — la stessa idea di un README, ma rivolto all'agente invece che a un umano. `anote init` ne genera uno automaticamente, precompilato con lo stack rilevato e i comandi di verifica (test/lint/build):

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

Modificalo liberamente — aggiungi note di architettura, convenzioni, o cose su cui l'agente continua a sbagliare. Panacea lo legge all'inizio di ogni sessione in quella directory.

## Hook — eseguire i tuoi comandi attorno alle chiamate degli strumenti

Gli hook eseguono un comando shell prima (`preToolUse`) o dopo (`postToolUse`) ogni chiamata di strumento, configurati in `.anote.json`:

```json
{
  "hooks": {
    "preToolUse": ["./scripts/check-tool-policy.sh"],
    "postToolUse": ["npx prettier --write ."]
  }
}
```

**Semantica dei codici di uscita:**

| Codice di uscita | Effetto |
|---|---|
| `0` | Consenti — stdout viene acquisito come messaggio informativo |
| `2` | Nega — stdout viene acquisito come motivo, mostrato all'agente |
| qualsiasi altro | Avvisa ma consenti |

Usa `preToolUse` per bloccare comandi rischiosi o applicare policy prima che vengano eseguiti; usa `postToolUse` per cose come la formattazione automatica dopo ogni modifica.

## Prossimi passi

- [Esplorare la directory .anote](anote-directory.md) — dove risiedono CLAW.md e la configurazione
- [Modalità di permesso](../use-panacea/permission-modes.md) — l'altra leva su cosa può fare l'agente
