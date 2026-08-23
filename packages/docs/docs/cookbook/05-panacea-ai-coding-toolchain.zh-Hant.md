# Panacea AI 編碼工具鏈

本食譜解釋了 Panacea 的 AI 編碼體驗如何通過 CLI、SDK 和 VS Code 提供。

## 您將學到什麼

- Panacea 中不同的 AI 編碼入口點
- CLI、SDK 和 VS Code 擴展如何與共享後端相關
- 私有代碼輔助的關鍵產品功能
- 在代碼庫中查找實現細節的位置

## 為什麼這很重要

Panacea 被構建為一個統一的產品，具有多個介面：

- 一個 **CLI**，用於驅動 `anote chat`、代碼搜索和代碼庫審查
- 一個 **VS Code 擴展**，用於編輯器內的 AI 輔助
- 一個 **SDK**，用於將 Panacea 嵌入到其他應用程式中

這些介面共享一個後端和基於代理的推理層，使產品在桌面、網頁和代碼工作流程中保持一致。

## 主要的 Panacea 檔案

| 檔案 | 為什麼重要 |
|---|---|
| `Panacea/packages/cli` | 用於開發者工作流程的 TypeScript CLI 實現 |
| `Panacea/packages/vscode` | VS Code 擴展和聊天整合 |
| `Panacea/packages/sdk` | 用於程式化訪問的 TypeScript SDK |
| `Panacea/packages/backend` | 驅動所有 UI 和 CLI 互動的共享後端服務 |

## 它是如何運作的

- 編碼用戶操作從 CLI、SDK 或 VS Code 擴展開始。
- 請求被發送到 Panacea 的後端 API。
- 後端使用代理協調和模型提供者生成代碼感知的答案。
- 回應在相同的介面中返回，包含代碼建議、解釋或修正。

## 有用的產品功能

- **CLI**：`anote chat`、代碼庫搜索、代碼審查、代碼生成和基於嵌入的輔助。
- **VS Code**：內聯聊天、差異預覽、代碼操作和串流回應。
- **SDK**：Panacea API 的客戶端包裝器，支持自定義整合。

## 本地運行

從工作區根目錄 (`anote/panacea`)：

```bash
cd Panacea
cp packages/backend/.env.example packages/backend/.env
docker compose up --build
```

這將啟動共享的後端和前端服務。

在另一個終端中，運行 CLI 套件：

```bash
cd Panacea/packages/cli
npm install
npm run dev
```

然後您可以在本地使用 CLI 或使用 `npm run build` 進行構建。

對於 VS Code 開發，請在 VS Code 中打開 `Panacea/packages/vscode` 並使用調試器啟動擴展。

## 食譜的注意事項

本食譜對於需要高層次了解 Panacea 多介面 AI 編碼產品的團隊成員非常有用。它還可以指引讀者到可以修改或擴展的實現檔案。
