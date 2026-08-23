# Panacea マルチモーダルドキュメント取り込み

このレシピでは、Panacea がドキュメント Q&A + RAG（[レシピ 03](03-panacea-document-qa-rag.md)を参照）をプレーンテキストから画像、音声、動画、スプレッドシートに拡張する方法を説明します。これにより、すべてのコンテンツが同じチャンク化および埋め込みパイプラインを通じて検索可能になります。

## 学べること

- Panacea がアップロードを MIME タイプで分類し、専用の取り込みサービスにルーティングする方法
- 画像や動画フレームが視覚対応の LLM を使用してインデックス可能なテキストに変換される方法
- 音声（動画の音声トラックを含む）が Whisper を使用して文字起こしされる方法
- スプレッドシートが検索不可能なテキストダンプにフラット化されるのではなく、Markdown テーブルに変換される方法
- マルチモーダル取り込みを制御する機能フラグとサイズ制限

## なぜこれが重要か

Tika（デフォルトのドキュメントテキスト抽出ツール）は、テキストベースのフォーマットのみを有効に処理できます。追加の処理がない場合、アップロードされた画像、音声クリップ、動画、またはスプレッドシートは、取り込みに失敗するか、すべての構造を失います。Panacea は代わりに、アップロード時にメディアタイプを検出し、クリーンなテキストを生成するために特別に設計されたサービスを呼び出します。このテキストは `document_text` として保存され、他のドキュメントと同じ取得パスを通ります。したがって、スクリーンショット、通話録音、または営業用スプレッドシートは、PDF のようにチャットで回答可能になります。

## 主要な Panacea ファイル

| ファイル | 重要な理由 |
|---|---|
| `Panacea/backend/api_endpoints/documents/handler.py` | アップロード時に MIME タイプ/拡張子を検出し、適切な取り込みサービスにルーティングします |
| `Panacea/backend/services/vision_service.py` | `describe_image()` — GPT-4o または Claude ビジョンを使用して画像の詳細なテキスト説明を生成します |
| `Panacea/backend/services/audio_service.py` | `transcribe_audio()` — OpenAI Whisper を使用して音声を文字起こしします |
| `Panacea/backend/services/video_service.py` | `ffmpeg` を使用してフレームを抽出し、ビジョンサービスで各フレームを説明し、音声トラックを別々に文字起こしし、両方をインターリーブします |
| `Panacea/backend/services/tabular_service.py` | `ingest_tabular()` — CSV/TSV/XLSX/XLS/ODS をヘッダーと行を保持した Markdown テーブルに変換します |
| `Panacea/backend/agents/config.py` | `AgentConfig` 機能フラグ: `ENABLE_MULTIMODAL`, `MAX_IMAGE_BYTES`, `MAX_AUDIO_BYTES`, `MAX_VIDEO_BYTES`, `VIDEO_FRAME_INTERVAL_SECS`, `VIDEO_MAX_FRAMES` |

## 仕組み

1. ファイルは通常のドキュメント用の同じエンドポイントを通じてアップロードされます。`handler.py` は MIME タイプ/拡張子を嗅ぎ分け、画像、動画、音声、表形式、またはプレーンテキスト/ドキュメントとして分類します。
2. **画像** → `vision_service.describe_image()` は画像（base64 エンコード）を視覚対応モデルに送信し、目に見えるテキストを文字起こしし、チャート/図/ UI スクリーンショットを説明し、オブジェクトとレイアウトを記録するよう指示するプロンプトを使用します。これにより、説明だけでセマンティック検索が後で見つけるのに十分です。
3. **音声** → `audio_service.transcribe_audio()` は Whisper（`whisper-1`）を呼び出し、期間/言語メタデータ付きの文字起こしを返します。
4. **動画** → `video_service` は固定間隔（`VIDEO_FRAME_INTERVAL_SECS`、デフォルト 30 秒、`VIDEO_MAX_FRAMES` に制限）でフレームを `ffmpeg` を使用して抽出し、ビジョンサービスで各フレームを説明し、音声トラックを別々に文字起こしし、両方をタイムスタンプ付きのドキュメントにインターリーブします。
5. **表形式** → `tabular_service.ingest_tabular()` は各シートをネイティブに解析し（`csv`/`pandas`+`openpyxl`/`xlrd` を介して）、Markdown テーブルとしてレンダリングします。最初の 500 行を超える行についてはプレーン CSV にフォールバックし、検索インデックスから何も失われないようにします。
6. これらのサービスから出てくるテキストはすべて `document_text` として保存され、通常のドキュメントと同じようにチャンク化/埋め込まれるため、レシピ 03 からの標準 RAG Q&A フローを通じて取得可能です。

すべてのサービスは **決してエラーを発生させない** ように設計されています。失敗したビジョンコール、欠落した依存関係、またはサイズオーバーのファイルはプレースホルダ文字列（例: `"[画像がインライン分析に対して大きすぎます (23.4 MB)。制限: 20 MB.]"`）を返し、ドキュメントレコードは常に作成され、アップロード全体が失敗することはありません。

## ローカルで実行する

ワークスペースのルート（`anote/panacea`）から：

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

マルチモーダル取り込みはデフォルトでオンです（`ENABLE_MULTIMODAL=true`）。動作を調整するには、`backend/.env` でこれらを設定します：

```bash
ENABLE_MULTIMODAL=true        # マスター スイッチ
MAX_IMAGE_BYTES=20971520      # デフォルト 20 MB
MAX_AUDIO_BYTES=26214400      # デフォルト 25 MB
MAX_VIDEO_BYTES=524288000     # デフォルト 500 MB
VIDEO_FRAME_INTERVAL_SECS=30
VIDEO_MAX_FRAMES=20
```

動画の取り込みには、バックエンドコンテナの `PATH` に `ffmpeg` が存在する必要があります（提供された Docker イメージに既に含まれています）。Excel の取り込みには `openpyxl`（XLSX/ODS）と `xlrd`（レガシー XLS）が必要で、両方のビジョン/音声サービスには `OPENAI_API_KEY` および/または `ANTHROPIC_API_KEY` を設定する必要があります（`DEFAULT_AGENT_MODEL_TYPE` に応じて）。

### 試してみる

```bash
curl -X POST http://localhost:5000/ingest-pdf \
  -F chat_id=1 \
  -F "files[]=@./screenshot.png"

curl -X POST http://localhost:5000/ingest-pdf \
  -F chat_id=1 \
  -F "files[]=@./quarterly_sales.xlsx"
```

その後、`http://localhost:3000` のウェブ UI で同じチャットセッションを開き、アップロードした画像やスプレッドシートについて質問します。Panacea は生成された説明/Markdown テーブルから PDF のように回答します。

## クックブックのためのノート

このレシピはレシピ 03 と組み合わせると良いです。これは同じ RAG パイプラインですが、入力フォーマットの幅が広がります。「インデックス品質」は画像/動画のビジョンモデルの説明の良さに依存するため、`vision_service.py` の `_INDEXING_PROMPT` でのプロンプト調整は自然なカスタマイズポイントです。
