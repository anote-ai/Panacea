# VS Code 擴充功能

Anote VS Code 擴充功能在您的編輯器中提供即時 AI 協助。

## 功能

- **聊天側邊欄** — 持久的 AI 聊天面板，包含會話歷史
- **CodeLens 操作** — 在每個函數上方解釋 / 修正 / 測試 / 重構
- **上下文注入** — 將選定的程式碼或檔案添加到聊天中
- **語義搜索** — 從命令面板搜索您的程式碼庫
- **內聯差異審查** — 按檔案接受或拒絕 AI 編輯
- **檔案附件** — 將圖片、PDF 和文本檔案附加到聊天中

## 安裝

在 VS Code 擴充功能市場中搜索 **"Anote"**。

或通過 CLI：

```bash
code --install-extension anote-ai.anote-ai-coding
```

## 快速設置

1. 打開 VS Code
2. 從命令面板運行 `Anote: Set Up` (`Ctrl+Shift+P`)
3. 選擇您的提供者（Anthropic 直接或通過 Anote 伺服器）
4. 輸入您的 API 權杖
5. 從活動欄打開聊天面板
