# Panaceaを拡張する

プロジェクトでのPanaceaの動作をカスタマイズする方法は2つあります：永続的な指示のための **CLAW.md** と、ツール呼び出しの前後で独自のコマンドを実行するための **フック** です。

## CLAW.md — プロジェクトメモリ

`CLAW.md` はPanaceaがプロジェクトのコンテキストのために読み取るMarkdownファイルです — 人間ではなくエージェント向けのREADMEのようなものです。`anote init` は検出したスタックと検証コマンド（test/lint/build）を事前に入力した状態で自動的に生成します：

```markdown
# CLAW.md

This file provides guidance to Anote AI when working with code in this repository.

## Project overview

<!-- Describe what this project does -->

## Stack

TypeScript · Next.js

## Verification

Run these before considering a change complete:

  npm test
  npm run lint

## Working agreement

- Read relevant files before making changes
- Run the verification commands after modifying logic
- Keep changes small and focused
- Prefer editing existing files over creating new ones
```

自由に編集してください — アーキテクチャのメモ、規約、エージェントが繰り返し間違えることなどを追加しましょう。Panaceaはそのディレクトリでの各セッション開始時にこれを読み取ります。

## フック — ツール呼び出しの前後で独自のコマンドを実行する

フックは、各ツール呼び出しの前（`preToolUse`）または後（`postToolUse`）にシェルコマンドを実行します。`.anote.json` で設定します：

```json
{
  "hooks": {
    "preToolUse": ["./scripts/check-tool-policy.sh"],
    "postToolUse": ["npx prettier --write ."]
  }
}
```

**終了コードのセマンティクス：**

| 終了コード | 効果 |
|---|---|
| `0` | 許可 — 標準出力は情報メッセージとしてキャプチャされます |
| `2` | 拒否 — 標準出力は理由としてキャプチャされ、エージェントに表示されます |
| それ以外 | 警告するが許可する |

`preToolUse` を使って、リスクのあるコマンドを実行前にブロックしたりポリシーを適用したりできます。`postToolUse` は、編集のたびに自動フォーマットするなどの用途に使えます。

## 次のステップ

- [.anoteディレクトリを探索する](anote-directory.md) — CLAW.mdと設定がどこにあるか
- [権限モード](../use-panacea/permission-modes.md) — エージェントが何をできるかを制御するもう一つのレバー
