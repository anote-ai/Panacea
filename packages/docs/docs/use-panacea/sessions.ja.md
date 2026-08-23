# セッションの管理

すべての `anote chat` 会話は、セッションとしてローカルに保存されます — そのメッセージ、トークン使用量、および作業ディレクトリ。

## セッションの一覧

```bash
anote sessions list
anote sessions ls --limit 50
```

```
保存されたセッション (3):
  a1b2c3d4  12 メッセージ  in=4,200 out=1,800  10分前  /Users/you/project
  e5f6a7b8  4 メッセージ   in=900 out=400      2時間前   /Users/you/other-project
```

## セッションの表示

```bash
anote sessions show a1b2c3d4
anote sessions show a1b2c3d4 --limit 50   # より多くのメッセージ履歴
```

そのセッションの会話、トークン合計、および作業ディレクトリを表示します。セッションIDの短いプレフィックスを渡すこともできます。

## セッションの削除

```bash
anote sessions delete a1b2c3d4
anote sessions rm a1b2c3d4
```

## 次のステップ

- [一般的なワークフロー](common-workflows.md)
- [Panaceaの仕組み](../core-concepts/how-it-works.md) — ターン、圧縮、およびセッションの長さがコンテキストに与える影響
