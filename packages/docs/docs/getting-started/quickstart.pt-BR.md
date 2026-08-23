# Início Rápido

## 1. Inicializar

```bash
anote init
```

Isso o guiará na configuração da sua chave de API e do provedor de LLM preferido.

## 2. Fazer uma pergunta

```bash
# Pergunta geral
anote ask "como funciona a autenticação neste código?"

# Focar em um arquivo
anote ask --file src/auth.ts "explique isso"

# Passar código
cat src/handler.py | anote ask "o que pode dar errado aqui?"
```

## 3. Corrigir bugs automaticamente

```bash
# Corrigir e iterar até os testes passarem (até 5 rodadas)
anote fix --loop --max-iterations 5
```

## 4. Indexar para busca semântica

```bash
# Indexar seu código (executar uma vez, depois manter atualizado)
anote index

# Buscar semanticamente
anote search "validação de token JWT"
anote search "pool de conexão com o banco de dados"
```

## 5. Revisar um PR

```bash
anote review --pr 42
```

## 6. Gerar um changelog

```bash
anote changelog --since v1.2.0
```
