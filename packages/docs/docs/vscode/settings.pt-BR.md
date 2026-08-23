# Configurações da Extensão do VS Code

Configure a extensão na interface de configurações do VS Code ou em `settings.json`.

| Configuração | Padrão | Descrição |
|--------------|--------|-----------|
| `anote.model` | `claude-sonnet-4-6` | Modelo padrão a ser usado |
| `anote.apiKey` | `""` | Chave da API da Anthropic (ou use a variável de ambiente) |
| `anote.permissionMode` | `default` | Modo de permissão da ferramenta: `default`, `auto`, `manual` |
| `anote.showToolUse` | `true` | Mostrar chamadas de ferramentas no painel de chat |

```json
{
  "anote.model": "claude-sonnet-4-6",
  "anote.permissionMode": "default"
}
```
