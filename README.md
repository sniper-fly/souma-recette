# Souma Recette - Claude Code Plugin Marketplace

このリポジトリはClaude Codeのプラグインマーケットプレイスです。複数のプラグインを格納し、チームやコミュニティで共有できます。

> *プラグインはルセットであり、技である。あらゆるものを貪欲に吸収して自分の手札を増やし、新しいものを生み出す。*

## マーケットプレイスの追加方法

```bash
/plugin marketplace add sniper-fly/souma-recette
```

## 含まれるプラグイン

### askme
不確実な要件や複数の実装アプローチがある場合に、仮定で進めず明示的にユーザーへ確認を行うスキル

### gemini-search
Gemini CLIのGoogle Search Grounding機能でWeb検索を実行

### mirariko
スキルベースの実装計画書レビュー＆ブラッシュアップの反復ワークフロー

### prompt-optimization
モデル非依存のプロンプト分析・最適化パターン（BP-001〜BP-008）

### security-scanner
リポジトリ全体のマルウェア・悪意コードパターン検出

### skill-development
Claude Codeプラグイン用スキル作成のベストプラクティス

### tech-doc-research
要件定義書から必要技術を調査し、セットアップ手順・コード例・ベストプラクティスを含む技術調査ドキュメントを作成

### terraform-review
Terraformコードの本番デプロイ前レビュー

## プラグインのインストール

マーケットプレイスを追加後、個別のプラグインをインストール:

```bash
/plugin install askme@souma-recette
/plugin install gemini-search@souma-recette
/plugin install mirariko@souma-recette
/plugin install prompt-optimization@souma-recette
/plugin install security-scanner@souma-recette
/plugin install skill-development@souma-recette
/plugin install tech-doc-research@souma-recette
/plugin install terraform-review@souma-recette
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
