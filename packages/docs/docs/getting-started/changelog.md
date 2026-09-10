# Changelog

Ourogen doesn't publish a hand-maintained changelog file yet — the source of truth for what's shipped is:

- **[GitHub Releases](https://github.com/anote-ai/Panacea/releases)** — tagged releases for the CLI, VS Code extension, and other packages
- **[Commit history](https://github.com/anote-ai/Panacea/commits/main)** — every change, in order

## Generate one for your own project

The CLI can write a changelog from git history for *your* codebase:

```bash
anote changelog                    # since the last tag
anote changelog --since v1.2.0
anote changelog --dry-run          # print instead of writing CHANGELOG.md
```

This writes to your project's own `CHANGELOG.md`, not Ourogen's.
