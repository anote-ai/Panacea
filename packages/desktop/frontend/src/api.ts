import axios from "axios";

// In Electron, resolve backend URL via preload
async function getBase(): Promise<string> {
  if (window.electronAPI) {
    return window.electronAPI.getBackendUrl();
  }
  return "http://localhost:5099";
}

type UnauthorizedHandler = () => void;
let onUnauthorized: UnauthorizedHandler | null = null;

// App.tsx registers a handler here so a 401 (expired/invalid token) can log
// the user out, regardless of whether it surfaced via axios or raw fetch.
export function setUnauthorizedHandler(handler: UnauthorizedHandler | null) {
  onUnauthorized = handler;
}

// Kept in sync with App.tsx's token state so every request (axios or fetch)
// uses the current token without re-reading storage on each call.
let cachedToken: string | null = null;

export function setCachedToken(token: string | null) {
  cachedToken = token;
}

let _client: ReturnType<typeof axios.create> | null = null;

async function client() {
  if (!_client) {
    const base = await getBase();
    _client = axios.create({ baseURL: base });
    _client.interceptors.response.use(
      (res) => res,
      (err) => {
        if (err?.response?.status === 401) onUnauthorized?.();
        return Promise.reject(err);
      }
    );
  }
  if (cachedToken) _client.defaults.headers.common["Authorization"] = `Bearer ${cachedToken}`;
  else delete _client.defaults.headers.common["Authorization"];
  return _client;
}

export async function login(email: string, password: string) {
  const c = await client();
  const res = await c.post("/auth/login", { email, password });
  return res.data.token as string;
}

export async function register(email: string, password: string, name: string) {
  const c = await client();
  const res = await c.post("/auth/register", { email, password, name });
  return res.data.token as string;
}

export async function getSessions() {
  const c = await client();
  const res = await c.get("/api/chat/sessions");
  return res.data.sessions ?? [];
}

export async function getSession(id: string) {
  const c = await client();
  const res = await c.get(`/api/chat/sessions/${id}`);
  return res.data.messages ?? [];
}

export async function deleteSession(id: string) {
  const c = await client();
  await c.delete(`/api/chat/sessions/${id}`);
}

export async function getProviderKeys(): Promise<Record<string, string>> {
  const c = await client();
  const res = await c.get("/api/user/provider-keys");
  return res.data.keys ?? {};
}

export async function setProviderKey(provider: string, key: string): Promise<string> {
  const c = await client();
  const res = await c.put("/api/user/provider-keys", { provider, key });
  return res.data.masked as string;
}

export async function deleteProviderKey(provider: string): Promise<void> {
  const c = await client();
  await c.delete(`/api/user/provider-keys/${provider}`);
}

export async function streamChat(
  message: string,
  sessionId: string | null,
  model: string,
  onChunk: (text: string) => void,
  onSessionId: (id: string) => void,
  signal: AbortSignal
): Promise<void> {
  const base = await getBase();
  const res = await fetch(`${base}/api/chat/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(cachedToken ? { Authorization: `Bearer ${cachedToken}` } : {}),
    },
    body: JSON.stringify({ message, session_id: sessionId, model }),
    signal,
  });
  if (res.status === 401) {
    onUnauthorized?.();
    throw new Error("Unauthorized");
  }
  if (!res.ok || !res.body) throw new Error("Stream failed");
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";
    for (const line of lines) {
      if (!line.startsWith("data: ")) continue;
      const data = line.slice(6).trim();
      if (data === "[DONE]") return;
      try {
        const parsed = JSON.parse(data);
        if (parsed.type === "text" && parsed.text) onChunk(parsed.text);
        if (parsed.type === "session_id") onSessionId(parsed.session_id);
      } catch {}
    }
  }
}
