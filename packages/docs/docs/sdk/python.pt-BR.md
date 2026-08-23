# SDK Python

Um cliente Python está disponível através do pacote `anoteai` (parte do repositório Anote-Product).

## Instalação

```bash
pip install anoteai
```

## Uso

```python
from anoteai import Anote

client = Anote(api_key="sk-ai-...")

# Métodos públicos existentes autenticam com Authorization: Bearer sk-ai-...
result = client.classify(document_id="doc_123", labels=["contract", "invoice"])
answer = client.answer(document_id="doc_123", question="Qual é o valor do pagamento?")
```

Crie chaves de API em Configurações -> Chaves de API. A chave em texto simples é exibida uma vez; depois disso, apenas o prefixo da chave é mostrado.

Custos de crédito:

| Operação | Créditos |
| --- | ---: |
| Upload de documento | 1 por arquivo ou URL |
| Mensagem de chat / Q&A | 1 por solicitação |
| Conclusão de chat compatível com OpenAI | 1 por solicitação |

Trate erros de API pelo código de status:

| Status | Significado |
| --- | --- |
| 401 | Chave de API ausente ou inválida |
| 402 | Créditos insuficientes |
| 429 | Limite de taxa por chave excedido |

Veja o [repositório Anote-Product](https://github.com/anote-ai/anote-product) para a documentação completa do SDK.
