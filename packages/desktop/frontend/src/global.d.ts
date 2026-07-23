interface Window {
  electronAPI?: {
    getBackendUrl: () => Promise<string>;
    getAppVersion: () => Promise<string>;
    getToken: () => Promise<string | null>;
    setToken: (token: string) => Promise<boolean>;
    deleteToken: () => Promise<boolean>;
    platform: string;
  };
}
