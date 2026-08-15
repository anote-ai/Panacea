# Prompt Library

Copy-paste prompts for `anote ask`, `anote chat`, and `anote fix`, organized by task.

## Understanding code

```bash
anote ask "what does this codebase do, at a high level?"
anote ask --file src/payments/webhook.ts "walk me through this file line by line"
anote ask "where is the rate limiter configured, and what are the limits?"
anote ask "what would break if I removed the caching layer here?"
```

## Debugging

```bash
anote fix --error "$(cat error.log)"
anote ask "why does this test fail intermittently but not consistently?"
anote fix src/db/pool.ts "connections aren't being released back to the pool"
```

## Code review

```bash
anote review --file src/auth/session.ts
anote review --pr 42
anote diff --staged -c "focus on error handling and edge cases"
```

## Refactoring

```bash
anote refactor src/utils.ts "split this into smaller, single-purpose functions" --dry-run
anote ask "is there a simpler way to express this logic?" --file src/parser.ts
anote migrate --from "moment" --to "date-fns"
```

## Writing tests

```bash
anote test src/utils/validate.ts --coverage --write
anote ask "what edge cases am I missing for this function?" --file src/utils/validate.ts
```

## Security and performance

```bash
anote security --severity high
anote perf --focus "database,bundle size"
```

## Documentation

```bash
anote docs src/api/client.ts --style jsdoc
anote changelog --since v1.2.0
anote explain --stdout                       # quick architecture summary
```

## Next steps

- [Common workflows](common-workflows.md)
- [CLI Commands](../cli/commands.md)
