# Comandos de CLI

## `anote ask`

Haz cualquier pregunta sobre tu código.

```bash
anote ask "¿cómo funciona el middleware de autenticación?"
anote ask --file src/auth.ts "explica este archivo"
anote ask --compare  # lado a lado a través de múltiples modelos
cat file.py | anote ask "encontrar errores"
```

## `anote fix`

Corrige errores en el directorio actual.

```bash
anote fix
anote fix --loop                    # iterar hasta que las pruebas pasen
anote fix --max-iterations 5        # limitar iteraciones
anote fix --file src/broken.ts      # corregir un archivo específico
```

## `anote review`

Revisa el código en busca de errores, problemas de seguridad y calidad.

```bash
anote review                        # revisar el directorio actual
anote review --file src/handler.ts  # revisar un archivo específico
anote review --pr 42                # publicar revisión de IA en PR de GitHub
```

## `anote index`

Construye un índice de búsqueda semántica TF-IDF de tu base de código.

```bash
anote index              # indexar el directorio actual
anote index --watch      # observar cambios y reindexar
anote index /path/to/dir # indexar un directorio específico
```

## `anote search`

Busca semánticamente en tu base de código indexada.

```bash
anote search "validación de token JWT"
anote search "conexión a la base de datos" --top 10
anote search "middleware de autenticación" --json
```

## `anote doctor`

Verifica tu entorno en busca de problemas de configuración.

```bash
anote doctor
```

Verificaciones: Node.js ≥ 18, `ANTHROPIC_API_KEY` configurado, `.anote.json` presente, `CLAW.md` presente, git instalado.

## `anote changelog`

Genera una entrada CHANGELOG.md a partir del historial de git.

```bash
anote changelog
anote changelog --since v1.2.0
anote changelog --dry-run
```

## `anote docs`

Genera documentación para código no documentado.

```bash
anote docs
anote docs src/api.ts
anote docs --style jsdoc
anote docs --dry-run
```

## `anote migrate`

Migración de base de código asistida por IA.

```bash
anote migrate --from "React 17" --to "React 18"
anote migrate --from "axios" --to "fetch"
anote migrate --dry-run
```

## `anote security`

Auditoría de seguridad de tu base de código (OWASP Top 10).

```bash
anote security
anote security --severity high
anote security --fix
```

## `anote perf`

Análisis de rendimiento.

```bash
anote perf
anote perf --focus "database,bundle"
anote perf --fix
```
