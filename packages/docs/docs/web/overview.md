# Ourogen web app

Chat, write, and ask questions about your documents from your browser.

[Open Ourogen Chat](https://chat.ourogen.ai){ .md-button .md-button--primary }

## Start a conversation

1. Create an account or sign in with email or Google, when enabled on your server.
2. Choose **New Chat** and type a question. Use a suggested prompt if you need a starting point.
3. Press **Enter** to send. Use **Shift + Enter** to add a new line.
4. Use **Stop** to interrupt a response. Your conversations appear in the sidebar.

## Work with a document

Use the upload button beside the message box, or drag a file into the chat. Wait for processing to finish before asking a question. Try “Summarize the main findings in this document.”

Open **Library** to view uploaded files, organize them into folders, or return to an attached conversation. Check the source document when you need to verify an answer.

## Make the app comfortable

- Open your account menu for settings and model selection.
- Choose **System**, **Light**, or **Dark** appearance to match your workspace.
- Collapse the sidebar when you want more room for a conversation.

## Run locally

For the full app, follow [self-hosted installation](../getting-started/installation.md#web-app-self-hosted). To develop only the frontend with a backend already running:

```bash
npm install
npm run dev --workspace=packages/web
```

The app runs at `http://localhost:3000` and proxies API calls to `http://localhost:5000`. See [configuration](../getting-started/configuration.md) for backend settings.
