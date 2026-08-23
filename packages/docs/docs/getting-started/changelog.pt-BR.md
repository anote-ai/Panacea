# Registro de Mudanças

A Panacea ainda não publica um arquivo de registro de mudanças mantido manualmente — a fonte de verdade sobre o que foi lançado é:

- **[Lançamentos do GitHub](https://github.com/anote-ai/Panacea/releases)** — lançamentos marcados para o CLI, extensão do VS Code e outros pacotes
- **[Histórico de commits](https://github.com/anote-ai/Panacea/commits/main)** — cada alteração, em ordem

## Gere um para seu próprio projeto

O CLI pode escrever um registro de mudanças a partir do histórico do git para *seu* código-fonte:

```bash
anote changelog                    # desde a última tag
anote changelog --since v1.2.0
anote changelog --dry-run          # imprime em vez de escrever CHANGELOG.md
```

Isso escreve no `CHANGELOG.md` do seu projeto, não no da Panacea.
