import { describe, it, expect, beforeEach } from "vitest";
import { loadToken, saveToken } from "./auth-storage";

describe("auth-storage (no electronAPI — plain browser fallback)", () => {
  beforeEach(() => {
    window.localStorage.clear();
    delete (window as any).electronAPI;
  });

  it("returns null when nothing is stored", async () => {
    expect(await loadToken()).toBeNull();
  });

  it("round-trips a token through localStorage", async () => {
    await saveToken("abc123");
    expect(await loadToken()).toBe("abc123");
    expect(window.localStorage.getItem("token")).toBe("abc123");
  });

  it("clears the token on saveToken(null)", async () => {
    await saveToken("abc123");
    await saveToken(null);
    expect(await loadToken()).toBeNull();
    expect(window.localStorage.getItem("token")).toBeNull();
  });
});

describe("auth-storage (electronAPI present — production path)", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it("delegates to electronAPI instead of localStorage", async () => {
    const store: { token: string | null } = { token: null };
    (window as any).electronAPI = {
      getBackendUrl: async () => "http://127.0.0.1:5099",
      getAppVersion: async () => "1.0.0",
      getToken: async () => store.token,
      setToken: async (t: string) => {
        store.token = t;
        return true;
      },
      deleteToken: async () => {
        store.token = null;
        return true;
      },
      platform: "darwin",
    };

    await saveToken("xyz");
    expect(store.token).toBe("xyz");
    expect(await loadToken()).toBe("xyz");
    // localStorage should be untouched — the token lives behind safeStorage instead.
    expect(window.localStorage.getItem("token")).toBeNull();

    await saveToken(null);
    expect(store.token).toBeNull();

    delete (window as any).electronAPI;
  });
});
