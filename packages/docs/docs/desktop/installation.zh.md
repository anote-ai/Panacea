# 桌面应用程序安装

## 下载

从 GitHub 发布页面下载适合您平台的最新版本。

| 平台 | 文件 |
|------|------|
| macOS | `Anote-AI-x.x.x.dmg` |
| Windows | `Anote-AI-Setup-x.x.x.exe` |
| Linux (deb) | `anote-ai_x.x.x_amd64.deb` |

## 从源代码构建

```bash
# 1. 打包 Python 后端
cd packages/backend
pip install pyinstaller
pyinstaller ../desktop/app.spec --distpath ../desktop/backend-dist

# 2. 构建并打包 Electron 应用程序
cd packages/desktop
npm install
npm run make
```

打包后的应用程序位于 `packages/desktop/out/`。
