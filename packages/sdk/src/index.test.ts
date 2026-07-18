import { describe, it, expect, vi, afterEach } from "vitest";
import { AnoteClient } from "./index.js";

describe("AnoteClient", () => {
  it("constructs with a base URL", () => {
    const client = new AnoteClient({ apiKey: "test-key", baseUrl: "http://localhost:5000" });
    expect(client).toBeDefined();
  });

  it("constructs with default base URL", () => {
    const client = new AnoteClient({ apiKey: "test-key" });
    expect(client).toBeDefined();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("chat() posts to /api/chat with no version prefix", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ response: "hi", model: "claude-sonnet-4-6" }),
    });
    vi.stubGlobal("fetch", fetchMock);

    const client = new AnoteClient({ apiKey: "test-key", baseUrl: "http://localhost:5000" });
    const result = await client.chat("hello");

    expect(result).toEqual({ response: "hi", model: "claude-sonnet-4-6" });
    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe("http://localhost:5000/api/chat");
    expect(JSON.parse(init.body)).toEqual({ message: "hello", model: undefined, history: undefined });
  });

  it("listSessions() unwraps the { sessions } envelope", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ sessions: ["a", "b"] }),
    });
    vi.stubGlobal("fetch", fetchMock);

    const client = new AnoteClient({ apiKey: "test-key", baseUrl: "http://localhost:5000" });
    const sessions = await client.listSessions();

    expect(sessions).toEqual(["a", "b"]);
    expect(fetchMock.mock.calls[0][0]).toBe("http://localhost:5000/api/chat/sessions");
  });

  it("deleteSession() unwraps the { deleted } envelope", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ deleted: true }),
    });
    vi.stubGlobal("fetch", fetchMock);

    const client = new AnoteClient({ apiKey: "test-key", baseUrl: "http://localhost:5000" });
    const deleted = await client.deleteSession("abc");

    expect(deleted).toBe(true);
    expect(fetchMock.mock.calls[0][0]).toBe("http://localhost:5000/api/chat/sessions/abc");
  });

  it("health() hits /health with no /api prefix", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ status: "ok", service: "anote-backend" }),
    });
    vi.stubGlobal("fetch", fetchMock);

    const client = new AnoteClient({ apiKey: "test-key", baseUrl: "http://localhost:5000" });
    const health = await client.health();

    expect(health).toEqual({ status: "ok", service: "anote-backend" });
    expect(fetchMock.mock.calls[0][0]).toBe("http://localhost:5000/health");
  });
});
