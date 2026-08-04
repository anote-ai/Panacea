const { app, BrowserWindow, ipcMain, dialog, safeStorage } = require("electron");
const path = require("path");
const fs = require("fs");
const { spawn } = require("child_process");
const http = require("http");

if (app.isPackaged) {
  // Checks GitHub Releases (configured via the `github` publisher in
  // forge.config.js) for a newer version and applies it on next restart.
  require("update-electron-app")();
}

let mainWindow = null;
let backendProcess = null;
let isQuitting = false;
let backendRestartCount = 0;
const MAX_BACKEND_RESTARTS = 3;
const BACKEND_PORT = 5099;
const BACKEND_URL = `http://127.0.0.1:${BACKEND_PORT}`;
const isDev = process.env.NODE_ENV === "development" || !app.isPackaged;

function isBackendAlive() {
  return new Promise((resolve) => {
    http
      .get(`${BACKEND_URL}/health`, (res) => resolve(res.statusCode === 200))
      .on("error", () => resolve(false));
  });
}

// Spawn bundled backend executable
function startBackend() {
  let backendPath;
  const env = isDev
    ? { ...process.env, FLASK_PORT: String(BACKEND_PORT), APP_ENV: "local" }
    : { ...process.env, FLASK_PORT: String(BACKEND_PORT) };

  if (isDev) {
    // In dev, start Python directly
    backendPath = path.join(__dirname, "..", "backend", "app.py");
    backendProcess = spawn("python", [backendPath], { env, stdio: "pipe" });
  } else {
    // In production, use the bundled executable
    const exeName = process.platform === "win32" ? "anote-backend.exe" : "anote-backend";
    backendPath = path.join(process.resourcesPath, "backend-dist", exeName);
    backendProcess = spawn(backendPath, [], { env, stdio: "pipe" });
  }

  backendProcess.stdout?.on("data", (data) => {
    console.log("[backend]", data.toString());
  });
  backendProcess.stderr?.on("data", (data) => {
    console.error("[backend]", data.toString());
  });
  backendProcess.on("error", (err) => {
    console.error("Failed to start backend:", err);
  });
  backendProcess.on("exit", (code, signal) => {
    backendProcess = null;
    if (isQuitting) return;

    // The backend died mid-session (crash, killed, etc). Try to bring it
    // back a few times with backoff before giving up and telling the user.
    if (backendRestartCount >= MAX_BACKEND_RESTARTS) {
      dialog.showErrorBox(
        "Backend Error",
        "The Anote AI backend stopped unexpectedly and could not be restarted. Please restart the app."
      );
      return;
    }
    backendRestartCount += 1;
    const delay = 1000 * 2 ** (backendRestartCount - 1);
    console.error(
      `[backend] exited unexpectedly (code=${code}, signal=${signal}). ` +
        `Restarting in ${delay}ms (attempt ${backendRestartCount}/${MAX_BACKEND_RESTARTS})`
    );
    setTimeout(startBackend, delay);
  });
}

function stopBackend() {
  if (backendProcess) {
    backendProcess.kill();
    backendProcess = null;
  }
}

// Wait for backend to be ready
function waitForBackend(retries = 30) {
  return new Promise((resolve, reject) => {
    const check = (remaining) => {
      if (remaining <= 0) return reject(new Error("Backend failed to start"));
      http.get(`${BACKEND_URL}/health`, (res) => {
        if (res.statusCode === 200) resolve();
        else setTimeout(() => check(remaining - 1), 1000);
      }).on("error", () => setTimeout(() => check(remaining - 1), 1000));
    };
    check(retries);
  });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    titleBarStyle: process.platform === "darwin" ? "hiddenInset" : "default",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
    icon: path.join(__dirname, "assets", "icon.png"),
    show: false,
  });

  if (isDev) {
    mainWindow.loadURL("http://localhost:3001");
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, "frontend", "dist", "index.html"));
  }

  mainWindow.once("ready-to-show", () => mainWindow.show());
  mainWindow.on("closed", () => { mainWindow = null; });
}

app.whenReady().then(async () => {
  if (require("electron-squirrel-startup")) {
    app.quit();
    return;
  }

  // A previous instance's backend may still be alive (e.g. this process
  // crashed without cleaning up, or the app was relaunched quickly) —
  // reuse it instead of spawning a second one on the same port.
  if (!(await isBackendAlive())) {
    startBackend();
  } else {
    console.log("[backend] reusing already-running backend at", BACKEND_URL);
  }

  try {
    await waitForBackend();
  } catch (e) {
    console.error("Backend not ready:", e);
    dialog.showErrorBox("Backend Error", "Failed to start the Anote AI backend. Please try again.");
    app.quit();
    return;
  }

  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});

app.on("before-quit", () => {
  isQuitting = true;
  stopBackend();
});

app.on("will-quit", () => {
  isQuitting = true;
  stopBackend();
});

process.on("exit", stopBackend);

// IPC handlers
ipcMain.handle("get-backend-url", () => BACKEND_URL);
ipcMain.handle("get-app-version", () => app.getVersion());

// Auth token storage — encrypted at rest via Electron's safeStorage (backed
// by the OS keychain/DPAPI/libsecret) instead of the renderer's plaintext
// localStorage, since this app's whole premise is keeping data local & private.
const tokenFilePath = () => path.join(app.getPath("userData"), "auth.token");

ipcMain.handle("auth:get-token", () => {
  try {
    if (!safeStorage.isEncryptionAvailable()) return null;
    const encrypted = fs.readFileSync(tokenFilePath());
    return safeStorage.decryptString(encrypted);
  } catch {
    return null;
  }
});

ipcMain.handle("auth:set-token", (_event, token) => {
  try {
    if (!safeStorage.isEncryptionAvailable() || typeof token !== "string") return false;
    fs.writeFileSync(tokenFilePath(), safeStorage.encryptString(token), { mode: 0o600 });
    return true;
  } catch {
    return false;
  }
});

ipcMain.handle("auth:delete-token", () => {
  try {
    fs.unlinkSync(tokenFilePath());
  } catch {
    // already gone — fine
  }
  return true;
});
