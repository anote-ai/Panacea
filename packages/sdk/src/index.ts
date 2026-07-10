/**
 * @anote-ai/sdk — TypeScript SDK for the Anote backend REST API.
 *
 * @example
 * ```ts
 * import { AnoteClient } from "@anote-ai/sdk";
 *
 * const client = new AnoteClient({ apiKey: "<jwt-access-token>" });
 *
 * const { response } = await client.chat("Explain this codebase");
 * console.log(response);
 *
 * for await (const chunk of client.chatStream("Explain this codebase")) {
 *   process.stdout.write(chunk);
 * }
 * ```
 */

// ── Types ─────────────────────────────────────────────────────────────────────

export interface AnoteClientOptions {
  /** Bearer token (JWT access token from /auth/login) sent as `Authorization: Bearer <token>`. */
  apiKey: string;
  /** Base URL of your Anote server. Defaults to `https://api.anote.ai`. */
  baseUrl?: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatOptions {
  /** Claude model to use. Defaults to the server's default model. */
  model?: string;
  /** Prior turns to include as conversation context. */
  history?: ChatMessage[];
}

export interface ChatResult {
  response: string;
  model: string;
}

export interface ChatStreamOptions {
  model?: string;
  /** Working directory for file operations on the server. Defaults to the server's cwd. */
  cwd?: string;
}

export interface SessionMessages {
  sessionId: string;
  messages: ChatMessage[];
}

export interface SearchResult {
  file: string;
  startLine: number;
  endLine: number;
  preview: string;
  score: number;
}

export interface SearchResponse {
  results: SearchResult[];
  query: string;
  cwd: string;
}

export interface HealthResult {
  status: string;
  service: string;
}

// ── Error class ─────────────────────────────────────────────────────────────────────

export class AnoteError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly body: unknown,
  ) {
    super(message);
    this.name = "AnoteError";
  }
}

// ── Client ────────────────────────────────────────────────────────────────────────────

export class AnoteClient {
  private readonly apiKey: string;
  private readonly baseUrl: string;

  constructor(options: AnoteClientOptions) {
    if (!options.apiKey) throw new Error("apiKey is required");
    this.apiKey = options.apiKey;
    this.baseUrl = (options.baseUrl ?? "https://api.anote.ai").replace(/\/$/, "");
  }

  // ── Core HTTP ───────────────────────────────────────────────────────────────────

  private async request<T>(
    method: string,
    path: string,
    body?: unknown,
    params?: Record<string, string | number | undefined>,
  ): Promise<T> {
    let url = `${this.baseUrl}${path}`;
    if (params) {
      const qs = new URLSearchParams(
        Object.entries(params)
          .filter(([, v]) => v !== undefined)
          .map(([k, v]) => [k, String(v)]),
      );
      if (qs.toString()) url += `?${qs}`;
    }

    const res = await fetch(url, {
      method,
      headers: {
        "Authorization": `Bearer ${this.apiKey}`,
        "Content-Type": "application/json",
        "User-Agent": "@anote-ai/sdk/1.0.0",
      },
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });

    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      const msg = (data as { error?: string }).error ?? `HTTP ${res.status}`;
      throw new AnoteError(msg, res.status, data);
    }

    return data as T;
  }

  // ── Chat ────────────────────────────────────────────────────────────────────────

  /** Send a message and receive a complete (non-streaming) AI response. */
  async chat(message: string, options: ChatOptions = {}): Promise<ChatResult> {
    return this.request<ChatResult>("POST", "/api/chat", {
      message,
      model: options.model,
      history: options.history,
    });
  }

  /**
   * Send a message and stream the response as it's generated, yielding text
   * chunks as they arrive over Server-Sent Events.
   */
  async *chatStream(message: string, options: ChatStreamOptions = {}): AsyncGenerator<string> {
    const res = await fetch(`${this.baseUrl}/api/chat/stream`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${this.apiKey}`,
        "Content-Type": "application/json",
        "User-Agent": "@anote-ai/sdk/1.0.0",
      },
      body: JSON.stringify({ message, model: options.model, cwd: options.cwd }),
    });

    if (!res.ok || !res.body) {
      const data = await res.json().catch(() => ({}));
      const msg = (data as { error?: string }).error ?? `HTTP ${res.status}`;
      throw new AnoteError(msg, res.status, data);
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      const events = buffer.split("\n\n");
      buffer = events.pop() ?? "";

      for (const event of events) {
        const dataLine = event.split("\n").find((line) => line.startsWith("data: "));
        const eventLine = event.split("\n").find((line) => line.startsWith("event: "));
        if (!dataLine) continue;

        const eventType = eventLine?.slice("event: ".length) ?? "text";
        const payload = JSON.parse(dataLine.slice("data: ".length));

        if (eventType === "text" && payload.text) yield payload.text as string;
        if (eventType === "error") throw new AnoteError(payload.message ?? "stream error", 0, payload);
      }
    }
  }

  // ── Sessions ─────────────────────────────────────────────────────────────────────────
  // Note: sessions are currently just server-side placeholders — creating one
  // doesn't yet link it to chat()/chatStream() calls.

  /** Create a new (empty) chat session. */
  async createSession(): Promise<{ sessionId: string }> {
    return this.request("POST", "/api/chat/sessions");
  }

  /** List all chat session IDs on the server. */
  async listSessions(): Promise<string[]> {
    const data = await this.request<{ sessions: string[] }>("GET", "/api/chat/sessions");
    return data.sessions;
  }

  /** Get the message history of a session. */
  async getSessionMessages(sessionId: string): Promise<SessionMessages> {
    return this.request("GET", `/api/chat/sessions/${encodeURIComponent(sessionId)}`);
  }

  /** Delete a session. Returns true on success. */
  async deleteSession(sessionId: string): Promise<boolean> {
    const data = await this.request<{ deleted: boolean }>(
      "DELETE",
      `/api/chat/sessions/${encodeURIComponent(sessionId)}`,
    );
    return data.deleted;
  }

  // ── Search ──────────────────────────────────────────────────────────────────────────

  /** TF-IDF search over the codebase index built by `anote index`. */
  async search(query: string, options: { cwd?: string; top?: number } = {}): Promise<SearchResponse> {
    return this.request("GET", "/api/search", undefined, {
      q: query,
      cwd: options.cwd,
      top: options.top,
    });
  }

  // ── Health ─────────────────────────────────────────────────────────────────────────────

  /** Check server liveness. Does not require authentication. */
  async health(): Promise<HealthResult> {
    const res = await fetch(`${this.baseUrl}/health`, {
      headers: { "User-Agent": "@anote-ai/sdk/1.0.0" },
    });
    return res.json();
  }
}

// Default export for convenience
export default AnoteClient;
