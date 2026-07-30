const { app, BrowserWindow, ipcMain, dialog } = require("electron");
const path = require("path");
const { spawn } = require("child_process");
const http = require("http");

if (app.isPackaged) {
  // Checks GitHub Releases (configured via the `github` publisher in
  // forge.config.js) for a newer version and applies it on next restart.
  require("update-electron-app")();
}

let mainWindow = null;
let backendProcess = null;
const BACKEND_PORT = 5099;
const BACKEND_URL = `http://127.0.0.1:${BACKEND_PORT}`;
const isDev = process.env.NODE_ENV === "development" || !app.isPackaged;

// Spawn bundled backend executable
function startBackend() {
  // The backend reads PORT (not FLASK_PORT) and binds HOST; keep it loopback-only
  // so the desktop backend is never reachable from the local network.
  const backendEnv = {
    ...process.env,
    PORT: String(BACKEND_PORT),
    HOST: "127.0.0.1",
  };
  let backendPath;
  if (isDev) {
    // In dev, start Python directly ("python" does not exist on modern macOS/Linux)
    const pythonBin = process.platform === "win32" ? "python" : "python3";
    backendPath = path.join(__dirname, "..", "backend", "app.py");
    backendProcess = spawn(pythonBin, [backendPath], {
      env: { ...backendEnv, APP_ENV: "local" },
      stdio: "pipe",
    });
  } else {
    // In production, use the bundled executable; APP_ENV=production keeps Flask
    // debug mode (and its interactive debugger + reloader fork) off.
    const exeName = process.platform === "win32" ? "anote-backend.exe" : "anote-backend";
    backendPath = path.join(process.resourcesPath, "backend-dist", exeName);
    backendProcess = spawn(backendPath, [], {
      env: { ...backendEnv, APP_ENV: "production" },
      stdio: "pipe",
    });
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
  if (require("electron-squirrel-startup")) app.quit();

  startBackend();
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
  if (backendProcess) {
    backendProcess.kill();
    backendProcess = null;
  }
});

// IPC handlers
ipcMain.handle("get-backend-url", () => BACKEND_URL);
ipcMain.handle("get-app-version", () => app.getVersion());
