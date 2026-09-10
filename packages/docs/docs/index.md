<p class="eyebrow">Ourogen documentation</p>

# One assistant. Start where you work.

<p class="lead">Chat, work with documents, and get help with your code. Choose a product below, then follow its guide to your first result.</p>

[Open Ourogen Chat](https://chat.ourogen.ai){ .md-button .md-button--primary }
[Set up locally](getting-started/installation.md){ .md-button }

## Choose your starting point

<div class="product-grid" markdown>

[**Web app**<span>Start a conversation or ask questions about a document in your browser.</span><span class="product-card__link">Start chatting →</span>](web/overview.md){ .product-card }

[**CLI**<span>Understand a codebase, review changes, and work from your terminal.</span><span class="product-card__link">Set up the CLI →</span>](cli/overview.md){ .product-card }

[**VS Code extension**<span>Ask about your code and review proposed edits alongside your files.</span><span class="product-card__link">Connect your editor →</span>](vscode/overview.md){ .product-card }

[**Desktop app**<span>Work with a local backend and configure Ollama for local model inference.</span><span class="product-card__link">Set up desktop →</span>](desktop/overview.md){ .product-card }

[**Mobile app**<span>Access chat from iOS or Android with the Expo app.</span><span class="product-card__link">Set up mobile →</span>](mobile/overview.md){ .product-card }

[**SDK &amp; API**<span>Add chat and document workflows to your own application.</span><span class="product-card__link">Build an integration →</span>](sdk/typescript.md){ .product-card }

</div>

## Your first conversation

1. Open [Ourogen Chat](https://chat.ourogen.ai) and create an account or sign in.
2. Send a question, or attach a file using the upload button in the message box.
3. Wait for the upload to finish, then ask a specific question about the document.
4. Find the conversation in your chat history and uploaded files in **Library**.

Try: “Summarize this document and list the decisions I need to make.”

## Prefer the terminal?

Install the CLI with Node.js 20.19 or later:

```bash
npm install -g @anote-ai/anote
cd your-project
anote init
anote ask "explain this codebase"
```

The command remains `anote`, and published packages use the `@anote-ai` namespace. Follow the [quick start](getting-started/quickstart.md) for configuration and common commands.

## Make it your own

- [Configuration](getting-started/configuration.md) — connect a provider or your own backend.
- [Local models](desktop/local-models.md) — configure Ollama for desktop use.
- [Common workflows](use-panacea/common-workflows.md) — follow practical examples.
- [Python SDK](sdk/python.md) — integrate from Python.
- [API reference](api/overview.md) — work directly with the backend.
- [Contributing](development/contributing.md) — build and improve the project.

Accounts, history, and documents are shared by clients connected to the same backend. A local desktop backend has its own data; it does not automatically sync with the hosted app.
