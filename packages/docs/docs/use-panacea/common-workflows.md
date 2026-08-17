# Common Workflows

Step-by-step patterns for everyday tasks with Panacea's CLI.

## Explore an unfamiliar codebase

```bash
anote explain                       # generate a CODEBASE.md tour
anote explain src/auth.ts "how does this work?"
anote index && anote search "JWT validation"
```

`explain` with no arguments writes a `CODEBASE.md` overview of the whole repo. Point it at a file or ask a specific question to go deeper.

## Fix a bug

```bash
anote fix --error "TypeError: cannot read property 'id' of undefined"
anote fix src/handler.ts "the webhook handler drops events under load"
anote fix --loop --cmd "npm test"          # keep iterating until tests pass
```

## Write and commit

```bash
anote generate "a rate limiter middleware for Express" -o src/middleware/rateLimit.ts
anote test src/middleware/rateLimit.ts --write
anote commit                                # AI-generated commit message
```

## Review before you push

```bash
anote diff --staged                         # review staged changes
anote review --pr 42                        # or review an open GitHub PR
anote security --severity high              # OWASP Top 10 audit
```

## Open a pull request

```bash
anote pr --gh                               # generate description, open with gh CLI
```

## Refactor safely

```bash
anote refactor src/legacy.ts "extract the validation logic into its own function" --dry-run
anote refactor src/legacy.ts "extract the validation logic into its own function" --auto
```

Always try `--dry-run` first on anything you haven't reviewed yet.

## Keep working while you do something else

```bash
anote watch "src/**/*.ts"                   # re-analyze on every save
```

## Document as you go

```bash
anote docs src/api.ts --style jsdoc
anote changelog --since v1.2.0
```

## Next steps

- [Prompt library](prompt-library.md) — copy-paste starting points
- [CLI Commands](../cli/commands.md) — full flag reference
