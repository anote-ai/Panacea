# Configuração do CLI

O CLI do Anote pode ser configurado via `.anote.json` na raiz do seu projeto ou `~/.anote/config.json` globalmente.

## Arquivo de Configuração

```json
{
  "model": "claude-sonnet-4-6",
  "permissionMode": "default",
  "maxTurns": 20,
  "provider": "anthropic"
}
```

## Gerenciando Configuração

```bash
anote config list          # Mostrar todas as configurações
anote config get model     # Obter um valor
anote config set model claude-haiku-4-5-20251001  # Definir um valor
anote config unset model   # Remover um valor
```
