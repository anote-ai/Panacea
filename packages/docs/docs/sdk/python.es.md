# SDK de Python

Un cliente de Python está disponible a través del paquete `anoteai` (parte del repositorio Anote-Product).

## Instalación

```bash
pip install anoteai
```

## Uso

```python
from anoteai import Anote

client = Anote(api_key="sk-ai-...")

# Los métodos públicos existentes se autentican con Authorization: Bearer sk-ai-...
result = client.classify(document_id="doc_123", labels=["contract", "invoice"])
answer = client.answer(document_id="doc_123", question="¿Cuál es el monto del pago?")
```

Crea claves API desde Configuración -> Claves API. La clave en texto plano se muestra una vez; después de eso, solo se muestra el prefijo de la clave.

Costos de crédito:

| Operación | Créditos |
| --- | ---: |
| Carga de documento | 1 por archivo o URL |
| Mensaje de chat / Q&A | 1 por solicitud |
| Finalización de chat compatible con OpenAI | 1 por solicitud |

Maneja errores de API por código de estado:

| Estado | Significado |
| --- | --- |
| 401 | Clave API faltante o inválida |
| 402 | Créditos insuficientes |
| 429 | Límite de tasa por clave excedido |

Consulta el [repositorio Anote-Product](https://github.com/anote-ai/anote-product) para la documentación completa del SDK.
