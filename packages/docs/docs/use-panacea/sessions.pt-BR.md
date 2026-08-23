# Gerenciar Sessões

Toda conversa `anote chat` é salva localmente como uma sessão — suas mensagens, uso de tokens e diretório de trabalho.

## Listar sessões

```bash
anote sessions list
anote sessions ls --limit 50
```

```
Sessões salvas (3):
  a1b2c3d4  12 msgs  in=4,200 out=1,800  há 10m  /Users/you/project
  e5f6a7b8  4 msgs   in=900 out=400      há 2h   /Users/you/other-project
```

## Mostrar uma sessão

```bash
anote sessions show a1b2c3d4
anote sessions show a1b2c3d4 --limit 50   # mais histórico de mensagens
```

Imprime a conversa, totais de tokens e diretório de trabalho para essa sessão. Você pode passar um prefixo curto do ID da sessão em vez do completo.

## Deletar uma sessão

```bash
anote sessions delete a1b2c3d4
anote sessions rm a1b2c3d4
```

## Próximos passos

- [Fluxos de trabalho comuns](common-workflows.md)
- [Como o Panacea funciona](../core-concepts/how-it-works.md) — turnos, compactação e como a duração da sessão afeta o contexto
