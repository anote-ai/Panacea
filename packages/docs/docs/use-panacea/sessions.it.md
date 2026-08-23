# Gestire le sessioni

Ogni conversazione `anote chat` è salvata localmente come una sessione — i suoi messaggi, l'uso del token e la directory di lavoro.

## Elenca le sessioni

```bash
anote sessions list
anote sessions ls --limit 50
```

```
Sessioni salvate (3):
  a1b2c3d4  12 msgs  in=4,200 out=1,800  10m fa  /Users/you/project
  e5f6a7b8  4 msgs   in=900 out=400      2h fa   /Users/you/other-project
```

## Mostra una sessione

```bash
anote sessions show a1b2c3d4
anote sessions show a1b2c3d4 --limit 50   # più cronologia dei messaggi
```

Stampa la conversazione, i totali dei token e la directory di lavoro per quella sessione. Puoi passare un prefisso breve dell'ID della sessione invece di quello completo.

## Elimina una sessione

```bash
anote sessions delete a1b2c3d4
anote sessions rm a1b2c3d4
```

## Prossimi passi

- [Flussi di lavoro comuni](common-workflows.md)
- [Come funziona Panacea](../core-concepts/how-it-works.md) — turni, compattazione e come la lunghezza della sessione influisce sul contesto
