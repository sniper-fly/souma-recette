# Souma Recipe - Claude Code Plugin Marketplace

このリポジトリはClaude Codeのプラグインマーケットプレイスです。複数のプラグインを格納し、チームやコミュニティで共有できます。

## マーケットプレイスの追加方法

```bash
/plugin marketplace add sniper-fly/souma-recipe
```

## 含まれるプラグイン

### example-commands
カスタムスラッシュコマンドのサンプルプラグイン

- `/hello` - シンプルな挨拶コマンド
- `/summarize` - ファイルの要約コマンド

### example-agent
カスタムエージェントのサンプルプラグイン

- `code-reviewer` - コードレビュー用エージェント

## プラグインのインストール

マーケットプレイスを追加後、個別のプラグインをインストール:

```bash
/plugin install example-commands@souma-recipe
/plugin install example-agent@souma-recipe
```

## 新しいプラグインの追加方法

1. `plugins/` ディレクトリに新しいプラグインフォルダを作成
2. `.claude-plugin/plugin.json` を作成（必須）
3. `commands/`, `agents/`, `skills/`, `hooks/` などのコンポーネントを追加
4. `.claude-plugin/marketplace.json` にプラグイン情報を追加

### ディレクトリ構成例

```
plugins/
└── my-new-plugin/
    ├── .claude-plugin/
    │   └── plugin.json      # 必須
    ├── commands/            # スラッシュコマンド
    │   └── my-command.md
    ├── agents/              # エージェント
    │   └── my-agent.md
    ├── skills/              # スキル
    │   └── my-skill/
    │       └── SKILL.md
    ├── hooks/               # フック
    │   └── hooks.json
    └── .mcp.json            # MCPサーバー設定
```

## plugin.json の例

```json
{
  "name": "my-plugin",
  "description": "プラグインの説明",
  "version": "1.0.0",
  "author": {
    "name": "Author Name",
    "email": "author@example.com"
  },
  "license": "MIT",
  "keywords": ["keyword1", "keyword2"],
  "commands": "./commands/",
  "agents": "./agents/"
}
```

## 検証

公開前にプラグインを検証:

```bash
claude plugin validate .
```

## ライセンス

MIT License
