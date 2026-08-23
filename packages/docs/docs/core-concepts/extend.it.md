# Estendi Panacea

Due modi per personalizzare il comportamento di Panacea nel tuo progetto: **CLAW.md** per istruzioni persistenti e **hooks** per eseguire i tuoi comandi attorno alle chiamate degli strumenti.

## CLAW.md — memoria del progetto

`CLAW.md` è un file markdown che Panacea legge per il contesto del progetto — la stessa idea di un README destinato all'agente invece che a un umano. `anote init` ne genera uno automaticamente, precompilato con il tuo stack rilevato e i comandi di verifica (test/lint/build):

```markdown
# CLAW.md

Questo file fornisce indicazioni ad Anote AI quando lavora con il codice in questo repository.

## Panoramica del progetto

<!-- Descrivi cosa fa questo progetto -->

## Stack

TypeScript · Next.js

## Verifica

Esegui questi comandi prima di considerare un cambiamento completato:

  npm test
  npm run lint

## Accordo di lavoro

- Leggi i file pertinenti prima di apportare modifiche
- Esegui i comandi di verifica dopo aver modificato la logica
- Mantieni le modifiche piccole e mirate
- Preferisci modificare file esistenti piuttosto che crearne di nuovi
```

Modificalo liberamente — aggiungi note architettoniche, convenzioni o cose che l'agente continua a sbagliare. Panacea lo legge all'inizio di ogni sessione in quella directory.

## Hooks — esegui i tuoi comandi attorno alle chiamate degli strumenti

Gli hooks eseguono un comando shell prima (`preToolUse`) o dopo (`postToolUse`) ogni chiamata agli strumenti, configurati in `.anote.json`:

```json
{
  "hooks": {
    "preToolUse": ["./scripts/check-tool-policy.sh"],
    "postToolUse": ["npx prettier --write ."]
  }
}
```

**Semantica del codice di uscita:**

| Codice di uscita | Effetto |
|---|---|
| `0` | Consenti — stdout viene catturato come messaggio informativo |
| `2` | Negare — stdout viene catturato come motivo, mostrato all'agente |
| qualsiasi altro valore | Avvisa ma consenti |

Usa `preToolUse` per bloccare comandi rischiosi o far rispettare la politica prima che vengano eseguiti; usa `postToolUse` per cose come l'auto-formattazione dopo ogni modifica.

## Prossimi passi

- [Esplora la directory .anote](anote-directory.md) — dove vivono CLAW.md e la configurazione
- [Modalità di autorizzazione](../use-panacea/permission-modes.md) — l'altro leva su ciò che l'agente può fare
