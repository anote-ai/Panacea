# Inizio Rapido

## 1. Inizializza

```bash
anote init
```

Questo ti guida nella configurazione della tua chiave API e del fornitore LLM preferito.

## 2. Fai una domanda

```bash
# Domanda generale
anote ask "come funziona l'autenticazione in questo codice?"

# Concentrati su un file
anote ask --file src/auth.ts "spiega questo"

# Pipe codice
cat src/handler.py | anote ask "cosa potrebbe andare storto qui?"
```

## 3. Risolvi i bug automaticamente

```bash
# Risolvi e itera fino a quando i test non passano (fino a 5 round)
anote fix --loop --max-iterations 5
```

## 4. Indicizza per ricerca semantica

```bash
# Indicizza il tuo codice (esegui una volta, poi mantieni aggiornato)
anote index

# Cerca semanticamente
anote search "validazione del token JWT"
anote search "pool di connessione al database"
```

## 5. Rivedi una PR

```bash
anote review --pr 42
```

## 6. Genera un changelog

```bash
anote changelog --since v1.2.0
```
