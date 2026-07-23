const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("electronAPI", {
  getBackendUrl: () => ipcRenderer.invoke("get-backend-url"),
  getAppVersion: () => ipcRenderer.invoke("get-app-version"),
  getToken: () => ipcRenderer.invoke("auth:get-token"),
  setToken: (token) => ipcRenderer.invoke("auth:set-token", token),
  deleteToken: () => ipcRenderer.invoke("auth:delete-token"),
  platform: process.platform,
});
