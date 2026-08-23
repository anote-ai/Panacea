# Registro delle modifiche

Panacea non pubblica ancora un file di registro delle modifiche mantenuto a mano — la fonte di verità per ciò che è stato rilasciato è:

- **[Rilasci di GitHub](https://github.com/anote-ai/Panacea/releases)** — rilasci etichettati per il CLI, l'estensione di VS Code e altri pacchetti
- **[Storia dei commit](https://github.com/anote-ai/Panacea/commits/main)** — ogni modifica, in ordine

## Genera uno per il tuo progetto

Il CLI può scrivere un registro delle modifiche dalla cronologia git per *il tuo* codice sorgente:

```bash
anote changelog                    # dall'ultimo tag
anote changelog --since v1.2.0
anote changelog --dry-run          # stampa invece di scrivere CHANGELOG.md
```

Questo scrive nel `CHANGELOG.md` del tuo progetto, non in quello di Panacea.
