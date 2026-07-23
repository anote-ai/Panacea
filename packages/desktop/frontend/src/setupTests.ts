import "@testing-library/jest-dom/vitest";

// Node 22+ ships its own global `localStorage`/`sessionStorage` (backed by a
// file, unconfigured here) which shadows jsdom's implementation and can't be
// read back out once assigned — so instead of relying on jsdom's storage,
// swap in a minimal in-memory Storage. This is portable across Node versions
// (CI pins Node 20, which has no built-in localStorage at all; local dev may
// be on a newer Node that does).
class MemoryStorage implements Storage {
  private store = new Map<string, string>();
  getItem(key: string) {
    return this.store.has(key) ? this.store.get(key)! : null;
  }
  setItem(key: string, value: string) {
    this.store.set(key, String(value));
  }
  removeItem(key: string) {
    this.store.delete(key);
  }
  clear() {
    this.store.clear();
  }
  key(index: number) {
    return Array.from(this.store.keys())[index] ?? null;
  }
  get length() {
    return this.store.size;
  }
}

for (const key of ["localStorage", "sessionStorage"] as const) {
  Object.defineProperty(globalThis, key, { configurable: true, value: new MemoryStorage() });
}

// jsdom doesn't implement matchMedia; App.tsx reads it synchronously on
// first render to pick the initial theme.
if (!window.matchMedia) {
  window.matchMedia = ((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  })) as unknown as typeof window.matchMedia;
}
