# Python SDK

Un client Python è disponibile tramite il pacchetto `anoteai` (parte del repository Anote-Product).

## Installazione

```bash
pip install anoteai
```

## Utilizzo

```python
from anoteai import Anote

client = Anote(api_key="sk-ai-...")

# I metodi pubblici esistenti si autenticano con Authorization: Bearer sk-ai-...
result = client.classify(document_id="doc_123", labels=["contract", "invoice"])
answer = client.answer(document_id="doc_123", question="Qual è l'importo del pagamento?")
```

Crea chiavi API da Impostazioni -> Chiavi API. La chiave in chiaro viene mostrata una sola volta; dopo di che viene visualizzato solo il prefisso della chiave.

Costi di credito:

| Operazione | Crediti |
| --- | ---: |
| Caricamento documento | 1 per file o URL |
| Messaggio chat / Q&A | 1 per richiesta |
| Completamento chat compatibile con OpenAI | 1 per richiesta |

Gestisci gli errori API per codice di stato:

| Stato | Significato |
| --- | --- |
| 401 | Chiave API mancante o non valida |
| 402 | Crediti insufficienti |
| 429 | Limite di frequenza per chiave superato |

Consulta il [repository Anote-Product](https://github.com/anote-ai/anote-product) per la documentazione completa del SDK.
