# Connect GitHub, Jira, Notion and MCP servers

**Settings → Developer tools.** Each connection is read-only until you approve a write, and disconnecting deletes everything synced from it.

| Tool | Connect with | It reads | It writes (only as approved actions) |
|---|---|---|---|
| **GitHub** | OAuth (if the server has a GitHub app), or a personal access token (`ghp_…` / `github_pat_…`) | PRs you authored and the files they touched, review comments you left, issues you're involved in, repository files for the AI engineer | Comment, open an issue, post a review, open a pull request |
| **Jira Cloud** | Your site (`acme.atlassian.net`), Atlassian email, and an [API token](https://id.atlassian.com/manage-profile/security/api-tokens) | Tickets you're assigned to or reported, with your comments | Create an issue, comment |
| **Notion** | OAuth, or an internal integration secret (`ntn_…`) shared with the pages it should see | Pages it can see (title and text) | Create a page |
| **MCP server** | A name, its Streamable HTTP URL, and an optional bearer token | The server's tool list | Call a tool |

For a fine-grained GitHub token, give it read access to the repositories, plus **Contents**, **Issues** and **Pull requests** write access if it should open PRs.

## Approvals and undo

Writes are actions (`github.comment`, `github.issue`, `github.review`, `github.pr`, `jira.issue`, `jira.comment`, `notion.page`, `mcp.call`). Each waits for approval by default; change it per type in **Settings → Autonomy**. **Undo** deletes a comment, closes an issue, closes a PR and deletes its branch, deletes a Jira issue or comment, or archives a Notion page.

## MCP servers

The coworker speaks the [Model Context Protocol](https://modelcontextprotocol.io) Streamable HTTP transport. Connecting runs `initialize` and `tools/list`. Calling a tool (`POST /mcp/<server>/call`) proposes an `mcp.call` action.

Servers must use `https://` and resolve to public addresses, so a pasted URL can't reach the backend's private network. `COWORKER_MCP_ALLOW_PRIVATE=1` allows `http://` and private addresses for local development only.

## Server configuration

| Variable | Purpose |
|---|---|
| `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, `GITHUB_REDIRECT_URI` | GitHub OAuth app (callback `BACKEND_URL/api/coworker/connections/github/callback`, scopes `repo read:user`). Without it, users paste a token. |
| `NOTION_CLIENT_ID`, `NOTION_CLIENT_SECRET`, `NOTION_REDIRECT_URI` | Notion public integration (callback `BACKEND_URL/api/coworker/connections/notion/callback`). Without it, users paste an integration secret. |
| `GITHUB_API_URL` | GitHub Enterprise Server API (default `https://api.github.com`) |
| `COWORKER_SANDBOX`, `COWORKER_SANDBOX_TIMEOUT` | Run tests for real repositories ([details](index.md#running-tests-on-real-repositories)) |
| `COWORKER_MCP_ALLOW_PRIVATE` | Local development only |

## API

`POST /connections/github/start`, `POST /connections/github/token`, `POST /connections/notion/start`, `POST /connections/notion/token`, `POST /connections/jira/token`, `POST /connections/mcp`, `GET /mcp/<server>/tools`, `POST /mcp/<server>/call`, `DELETE /connections/<provider>`.

Code: `coworker/connectors/github.py`, `jira.py`, `notion.py`, `mcp.py`, `devtools.py`.
