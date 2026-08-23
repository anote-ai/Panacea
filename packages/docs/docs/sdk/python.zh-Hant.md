# Python SDK

一個 Python 客戶端可以通過 `anoteai` 套件（屬於 Anote-Product 倉庫）獲得。

## 安裝

```bash
pip install anoteai
```

## 使用

```python
from anoteai import Anote

client = Anote(api_key="sk-ai-...")

# 現有的公共方法使用 Authorization: Bearer sk-ai-... 進行身份驗證
result = client.classify(document_id="doc_123", labels=["contract", "invoice"])
answer = client.answer(document_id="doc_123", question="付款金額是多少？")
```

從設定 -> API 金鑰創建 API 金鑰。明文金鑰僅顯示一次；之後僅顯示金鑰前綴。

信用成本：

| 操作 | 信用 |
| --- | ---: |
| 文件上傳 | 每個文件或 URL 1 |
| 聊天訊息 / 問答 | 每個請求 1 |
| OpenAI 兼容的聊天完成 | 每個請求 1 |

通過狀態碼處理 API 錯誤：

| 狀態 | 意義 |
| --- | --- |
| 401 | 缺少或無效的 API 金鑰 |
| 402 | 信用不足 |
| 429 | 每個金鑰的速率限制超過 |

請參閱 [Anote-Product 倉庫](https://github.com/anote-ai/anote-product) 獲取完整的 SDK 文檔。
