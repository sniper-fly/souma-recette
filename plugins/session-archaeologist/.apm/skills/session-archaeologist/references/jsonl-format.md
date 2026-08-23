# Claude Code セッションログ JSONL フォーマット

## ファイルの場所

セッションログは `~/.claude/projects/` 配下に、プロジェクトの絶対パスのスラッシュをハイフンに置換した名前のディレクトリに保存される。

```
~/.claude/projects/
└── -home-user-work-my-project/
    ├── sessions-index.json          # セッション一覧インデックス（存在しない場合あり）
    ├── {session-uuid}.jsonl         # メインセッションログ
    ├── {session-uuid}/
    │   └── subagents/
    │       └── agent-{agent-id}.jsonl  # サブエージェントのログ
    └── ...
```

## sessions-index.json 構造

```json
{
  "version": 1,
  "entries": [
    {
      "sessionId": "uuid",
      "fullPath": "/absolute/path/to/session.jsonl",
      "fileMtime": 1769831561055,
      "firstPrompt": "ユーザーの最初のメッセージ",
      "summary": "セッションの要約",
      "messageCount": 15,
      "created": "2026-01-31T03:24:39.191Z",
      "modified": "2026-01-31T03:26:28.619Z",
      "gitBranch": "main",
      "projectPath": "/home/user/work/project",
      "isSidechain": false
    }
  ]
}
```

**注意:** sessions-index.json は全セッションを網羅していない場合がある。確実な検索にはJSONLファイルの直接走査が必要。

## JSONL メッセージ構造

各行は独立したJSONオブジェクト。主要な `type` フィールド:

### user メッセージ

```json
{
  "type": "user",
  "message": {
    "role": "user",
    "content": "テキスト文字列"
  }
}
```

または content が配列の場合:

```json
{
  "type": "user",
  "message": {
    "role": "user",
    "content": [
      {
        "type": "text",
        "text": "ユーザーのメッセージ本文"
      }
    ]
  }
}
```

**注意:** content が文字列の場合、`<local-command-caveat>` や `<command-name>` で始まるシステム系メッセージはフィルタリングすること。

### assistant メッセージ

```json
{
  "type": "assistant",
  "message": {
    "content": [
      {
        "type": "text",
        "text": "AIの応答テキスト"
      },
      {
        "type": "tool_use",
        "name": "Edit",
        "input": { ... }
      }
    ]
  }
}
```

content 配列には以下のブロックタイプが混在する:
- `text` - AIのテキスト応答（分析対象）
- `tool_use` - ツール呼び出し（name フィールドで何を実行したかがわかる）

### result メッセージ

```json
{
  "type": "result",
  "message": {
    "content": [
      {
        "type": "tool_result",
        "tool_use_id": "...",
        "content": "ツール実行結果（大量のテキストになりうる）"
      }
    ]
  }
}
```

**注意:** result メッセージは非常に大きくなる（ファイル内容、コマンド出力等）。分析時はスキップするか、先頭のみ参照すること。

## ファイルサイズの目安

| サイズ | セッション内容 |
|--------|---------------|
| < 10KB | 短い会話（2-3往復）または中断されたセッション |
| 10-100KB | 通常の作業セッション |
| 100KB-1MB | 複数のツール呼び出しを含む長いセッション |
| 1MB+ | サブエージェント起動を含む大規模セッション |

## 検索のヒント

- **トピック特定:** キーワードでJSONLファイル全体をgrep検索するのが最も確実
- **時系列:** ファイルの更新日時でソートすると開発の流れが追える
- **サブエージェント:** `{session-uuid}/subagents/` ディレクトリ内のログも関連情報を含む場合がある
- **大量セッション:** sessions-index.json の firstPrompt でフィルタリングし、候補を絞ってから個別に精査する
