# Manage Sessions

Every `anote chat` conversation is saved locally as a session — its messages, token usage, and working directory.

## List sessions

```bash
anote sessions list
anote sessions ls --limit 50
```

```
Saved sessions (3):
  a1b2c3d4  12 msgs  in=4,200 out=1,800  10m ago  /Users/you/project
  e5f6a7b8  4 msgs   in=900 out=400      2h ago   /Users/you/other-project
```

## Show a session

```bash
anote sessions show a1b2c3d4
anote sessions show a1b2c3d4 --limit 50   # more message history
```

Prints the conversation, token totals, and working directory for that session. You can pass a short prefix of the session ID rather than the full one.

## Delete a session

```bash
anote sessions delete a1b2c3d4
anote sessions rm a1b2c3d4
```

## Next steps

- [Common workflows](common-workflows.md)
- [How Panacea works](../core-concepts/how-it-works.md) — turns, compaction, and how session length affects context
