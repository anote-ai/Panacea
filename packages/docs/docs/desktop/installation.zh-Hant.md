# 桌面應用程式安裝

## 下載

從 GitHub 發布頁面下載適用於您的平台的最新版本。

| 平台 | 檔案 |
|------|------|
| macOS | `Anote-AI-x.x.x.dmg` |
| Windows | `Anote-AI-Setup-x.x.x.exe` |
| Linux (deb) | `anote-ai_x.x.x_amd64.deb` |

## 從源碼構建

```bash
# 1. 打包 Python 後端
cd packages/backend
pip install pyinstaller
pyinstaller ../desktop/app.spec --distpath ../desktop/backend-dist

# 2. 構建並打包 Electron 應用程式
cd packages/desktop
npm install
npm run make
```

打包的應用程式位於 `packages/desktop/out/`。
