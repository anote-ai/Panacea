# Comandos CLI

## `anote ask`

Faça qualquer pergunta sobre seu código.

```bash
anote ask "como funciona o middleware de autenticação?"
anote ask --file src/auth.ts "explique este arquivo"
anote ask --compare  # lado a lado em vários modelos
cat file.py | anote ask "encontrar bugs"
```

## `anote fix`

Corrija bugs no diretório atual.

```bash
anote fix
anote fix --loop                    # iterar até que os testes passem
anote fix --max-iterations 5        # limitar iterações
anote fix --file src/broken.ts      # corrigir um arquivo específico
```

## `anote review`

Revise o código em busca de bugs, problemas de segurança e qualidade.

```bash
anote review                        # revisar diretório atual
anote review --file src/handler.ts  # revisar um arquivo específico
anote review --pr 42                # postar revisão de IA no PR do GitHub
```

## `anote index`

Construa um índice de busca semântica TF-IDF do seu código.

```bash
anote index              # indexar diretório atual
anote index --watch      # monitorar mudanças e reindexar
anote index /path/to/dir # indexar um diretório específico
```

## `anote search`

Pesquise seu código indexado semanticamente.

```bash
anote search "validação de token JWT"
anote search "conexão com o banco de dados" --top 10
anote search "middleware de autenticação" --json
```

## `anote doctor`

Verifique seu ambiente em busca de problemas de configuração.

```bash
anote doctor
```

Verificações: Node.js ≥ 18, `ANTHROPIC_API_KEY` definido, `.anote.json` presente, `CLAW.md` presente, git instalado.

## `anote changelog`

Gere uma entrada CHANGELOG.md a partir do histórico do git.

```bash
anote changelog
anote changelog --since v1.2.0
anote changelog --dry-run
```

## `anote docs`

Gere documentação para código não documentado.

```bash
anote docs
anote docs src/api.ts
anote docs --style jsdoc
anote docs --dry-run
```

## `anote migrate`

Migração de código assistida por IA.

```bash
anote migrate --from "React 17" --to "React 18"
anote migrate --from "axios" --to "fetch"
anote migrate --dry-run
```

## `anote security`

Auditoria de segurança do seu código (OWASP Top 10).

```bash
anote security
anote security --severity high
anote security --fix
```

## `anote perf`

Análise de desempenho.

```bash
anote perf
anote perf --focus "database,bundle"
anote perf --fix
```
