// Persists the auth token via the main process (encrypted at rest with
// Electron's safeStorage) when running inside Electron, falling back to
// localStorage when electronAPI isn't available (e.g. previewing the
// frontend alone in a browser during development).

export async function loadToken(): Promise<string | null> {
  if (window.electronAPI?.getToken) {
    try {
      return await window.electronAPI.getToken();
    } catch {
      return null;
    }
  }
  return localStorage.getItem("token");
}

export async function saveToken(token: string | null): Promise<void> {
  if (window.electronAPI?.setToken && window.electronAPI?.deleteToken) {
    try {
      if (token) await window.electronAPI.setToken(token);
      else await window.electronAPI.deleteToken();
      return;
    } catch {
      // fall through to localStorage
    }
  }
  if (token) localStorage.setItem("token", token);
  else localStorage.removeItem("token");
}
