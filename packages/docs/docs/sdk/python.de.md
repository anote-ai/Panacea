# Python SDK

Ein Python-Client ist über das `anoteai`-Paket (Teil des Anote-Produkt-Repo) verfügbar.

## Installation

```bash
pip install anoteai
```

## Verwendung

```python
from anoteai import Anote

client = Anote(api_key="sk-ai-...")

# Vorhandene öffentliche Methoden authentifizieren mit Authorization: Bearer sk-ai-...
result = client.classify(document_id="doc_123", labels=["contract", "invoice"])
answer = client.answer(document_id="doc_123", question="Was ist der Zahlungsbetrag?")
```

Erstellen Sie API-Schlüssel unter Einstellungen -> API-Schlüssel. Der Klartextschlüssel wird einmal angezeigt; danach wird nur das Schlüsselpräfix angezeigt.

Kosten für Credits:

| Operation | Credits |
| --- | ---: |
| Dokumenten-Upload | 1 pro Datei oder URL |
| Chat-Nachricht / Q&A | 1 pro Anfrage |
| OpenAI-kompatible Chat-Vervollständigung | 1 pro Anfrage |

Behandeln Sie API-Fehler nach Statuscode:

| Status | Bedeutung |
| --- | --- |
| 401 | Fehlender oder ungültiger API-Schlüssel |
| 402 | Unzureichende Credits |
| 429 | Pro-Schlüssel-Datenlimit überschritten |

Siehe das [Anote-Produkt-Repository](https://github.com/anote-ai/anote-product) für die vollständige SDK-Dokumentation.
