# Python SDK

可以通过 `anoteai` 包（Anote-Product 仓库的一部分）获得 Python 客户端。

## 安装

```bash
pip install anoteai
```

## 使用

```python
from anoteai import Anote

client = Anote(api_key="sk-ai-...")

# 现有的公共方法使用 Authorization: Bearer sk-ai-... 进行身份验证
result = client.classify(document_id="doc_123", labels=["contract", "invoice"])
answer = client.answer(document_id="doc_123", question="What is the payment amount?")
```

从设置 -> API 密钥中创建 API 密钥。明文密钥仅显示一次；之后只显示密钥前缀。

信用费用：

| 操作 | 信用 |
| --- | ---: |
| 文档上传 | 每个文件或 URL 1 |
| 聊天消息 / 问答 | 每个请求 1 |
| OpenAI 兼容的聊天完成 | 每个请求 1 |

通过状态码处理 API 错误：

| 状态 | 意义 |
| --- | --- |
| 401 | 缺少或无效的 API 密钥 |
| 402 | 信用不足 |
| 429 | 每个密钥的速率限制超出 |

请参阅 [Anote-Product 仓库](https://github.com/anote-ai/anote-product) 以获取完整的 SDK 文档。
