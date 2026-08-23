# 変更履歴

Panacea はまだ手動で管理された変更履歴ファイルを公開していません — 出荷された内容の真実の源は次の通りです：

- **[GitHub リリース](https://github.com/anote-ai/Panacea/releases)** — CLI、VS Code 拡張機能、およびその他のパッケージのタグ付きリリース
- **[コミット履歴](https://github.com/anote-ai/Panacea/commits/main)** — すべての変更を順番に

## 自分のプロジェクトのために生成する

CLI は *あなたの* コードベースの git 履歴から変更履歴を作成できます：

```bash
anote changelog                    # 最後のタグから
anote changelog --since v1.2.0
anote changelog --dry-run          # CHANGELOG.md を書き込む代わりに印刷
```

これはあなたのプロジェクトの `CHANGELOG.md` に書き込まれ、Panacea のものではありません。
