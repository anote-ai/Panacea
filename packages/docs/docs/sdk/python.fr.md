# SDK Python

Un client Python est disponible via le package `anoteai` (partie du dépôt Anote-Product).

## Installation

```bash
pip install anoteai
```

## Utilisation

```python
from anoteai import Anote

client = Anote(api_key="sk-ai-...")

# Les méthodes publiques existantes s'authentifient avec Authorization: Bearer sk-ai-...
result = client.classify(document_id="doc_123", labels=["contrat", "facture"])
answer = client.answer(document_id="doc_123", question="Quel est le montant du paiement ?")
```

Créez des clés API depuis Paramètres -> Clés API. La clé en texte clair est affichée une fois ; après cela, seul le préfixe de la clé est affiché.

Coûts en crédits :

| Opération | Crédits |
| --- | ---: |
| Téléchargement de document | 1 par fichier ou URL |
| Message de chat / Q&R | 1 par demande |
| Complétion de chat compatible OpenAI | 1 par demande |

Gérez les erreurs API par code d'état :

| Statut | Signification |
| --- | --- |
| 401 | Clé API manquante ou invalide |
| 402 | Crédits insuffisants |
| 429 | Limite de taux par clé dépassée |

Consultez le [dépôt Anote-Product](https://github.com/anote-ai/anote-product) pour la documentation complète du SDK.
