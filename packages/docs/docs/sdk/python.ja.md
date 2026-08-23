# Python SDK

Pythonクライアントは`anoteai`パッケージ（Anote-Productリポジトリの一部）を介して利用可能です。

## インストール

```bash
pip install anoteai
```

## 使用法

```python
from anoteai import Anote

client = Anote(api_key="sk-ai-...")

# 既存の公開メソッドはAuthorization: Bearer sk-ai-...で認証します。
result = client.classify(document_id="doc_123", labels=["contract", "invoice"])
answer = client.answer(document_id="doc_123", question="支払い金額はいくらですか？")
```

APIキーは設定 -> APIキーから作成します。プレーンテキストのキーは一度だけ表示され、その後はキーのプレフィックスのみが表示されます。

クレジットコスト:

| 操作 | クレジット |
| --- | ---: |
| ドキュメントアップロード | 1ファイルまたはURLごと |
| チャットメッセージ / Q&A | リクエストごとに1 |
| OpenAI互換のチャット完了 | リクエストごとに1 |

ステータスコードによるAPIエラーの処理:

| ステータス | 意味 |
| --- | --- |
| 401 | APIキーが欠落または無効 |
| 402 | クレジット不足 |
| 429 | キーごとのレート制限を超過 |

完全なSDKドキュメントについては[Anote-Productリポジトリ](https://github.com/anote-ai/anote-product)を参照してください。
