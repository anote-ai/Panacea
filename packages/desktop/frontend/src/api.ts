import axios from "axios";

function normalizeStreamError(message: string, model: string): string {
  if (!message) return "Sorry, something went wrong.";
  if (/not configured/i.test(message)) {
    return `The selected model (${model}) is not configured on this device yet. Add the matching provider key or switch to a configured model and try again.`;
  }
  return message;
}

// In Electron, resolve backend URL via preload
export async function getBackendBaseUrl(): Promise<string> {
  if (window.electronAPI) {
    return window.electronAPI.getBackendUrl();
  }
  return "http://localhost:5099";
}

let _client: ReturnType<typeof axios.create> | null = null;

async function client() {
  if (!_client) {
    const base = await getBackendBaseUrl();
    _client = axios.create({ baseURL: base });
  }
  const token = localStorage.getItem("token");
  if (token) _client.defaults.headers.common["Authorization"] = `Bearer ${token}`;
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

export async function streamChat(
  message: string,
  sessionId: string | null,
  model: string,
  onChunk: (text: string) => void,
  onSessionId: (id: string) => void,
  signal: AbortSignal
): Promise<void> {
  const base = await getBackendBaseUrl();
  const token = localStorage.getItem("token");
  const res = await fetch(`${base}/api/chat/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ message, session_id: sessionId, model }),
    signal,
  });
  if (!res.ok) {
    let errorMessage = "Stream failed";
    try {
      const payload = await res.json();
      errorMessage = payload.error || payload.message || errorMessage;
    } catch {}
    throw new Error(normalizeStreamError(errorMessage, model));
  }
  if (!res.body) throw new Error("Stream failed");
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
      let parsed: { type?: string; text?: string; session_id?: string; message?: string } | null = null;
      try {
        parsed = JSON.parse(data);
      } catch {
        continue;
      }
      if (parsed?.type === "text" && parsed.text) onChunk(parsed.text);
      if (parsed?.type === "session_id" && parsed.session_id) onSessionId(parsed.session_id);
      if (parsed?.type === "error") {
        throw new Error(normalizeStreamError(parsed.message || "Stream failed", model));
      }
    }
  }
}
