# Souma Recette

Claude Code / OpenCode など複数のコーディングエージェントで使えるスキル・エージェント・プロンプト・フックのパッケージ集です。[APM (Agent Package Manager)](https://microsoft.github.io/apm/) 形式で管理しています。

> *へこたれている暇なんか一秒もない。だって今オレ新しい技をモノにできるのが面白くて仕方ないんスよ！*
>
> — 幸平創真（『食戟のソーマ 弐ノ皿』第12話「魔術師再び」）

## セットアップ

APM CLI をインストール:

```bash
brew install microsoft/apm/apm
```

## 個別パッケージのインストール

各パッケージは `plugins/<name>/` に独立した APM パッケージとして格納されています。使いたいものだけを個別にインストールできます:

```bash
apm install github.com/sniper-fly/souma-recette -s plugins/terraform-review --target claude
```

ローカルにクローンしている場合はパスで直接指定できます:

```bash
apm install ./plugins/terraform-review --target claude
```

`--target` は `claude` の他、`opencode` / `copilot` / `cursor` / `gemini` など APM がサポートする任意のターゲットを指定できます(省略時は検出済みハーネスすべてに展開)。

複数パッケージを同時にインストールすると、`mirariko` のようにスキル名をパラメータとして他パッケージのスキルを横断利用するパッケージも機能します:

```bash
apm install ./plugins/mirariko ./plugins/terraform-review --target claude
```

## 含まれるパッケージ

| パッケージ | 内容 |
|---|---|
| `askme` | 不確実な要件や複数の実装アプローチがある場合に、仮定で進めず明示的にユーザーへ確認を行うスキル |
| `claude-settings-importer` | 個人(`~/.claude/`)またはプロジェクト固有(`.claude/`)のClaude Code設定をAPM形式のパッケージに変換するスキル |
| `gemini-search` | Gemini CLIのGoogle Search Grounding機能でWeb検索を実行 |
| `hasegawa` | ステージされていない変更を検出し、適切なコミット粒度の提案からgit commitまでを一貫してアシストするスキル |
| `mirariko` | スキルベースの実装計画書レビュー＆ブラッシュアップの反復ワークフロー |
| `prompt-optimization` | モデル非依存のプロンプト分析・最適化パターン（BP-001〜BP-008） |
| `python-seifuku` | uv + ruff + mypy + pytest構成のPythonプロジェクト初期セットアップとPostToolUse hooksによるコード品質チェック自動化 |
| `security-scanner` | リポジトリ全体のマルウェア・悪意コードパターン検出 |
| `session-archaeologist` | Claude Codeの過去の会話ログを発掘・分析し、開発の試行錯誤プロセスやインサイトを構造化して要約する |
| `skill-development` | Claude Codeプラグイン用スキル作成のベストプラクティス |
| `streaming-jinarashi` | AniList APIとPlaywright CLIを活用し、シーズンアニメの配信サービス情報を自動調査・独占配信を特定するツール |
| `tech-doc-research` | 要件定義書から必要技術を調査し、セットアップ手順・コード例・ベストプラクティスを含む技術調査ドキュメントを作成 |
| `terraform-review` | Terraformコードの本番デプロイ前レビュー |

## リポジトリ構成

このリポジトリはAPMの "Multi-plugin marketplace publisher" 構成を採用しています。ルートの `apm.yml` は `marketplace:` ブロックのみを持ち、各パッケージ本体は `plugins/<name>/` 配下に独立して存在します:

```
plugins/<name>/
  apm.yml               # パッケージ定義(name/version/description)
  .apm/
    skills/<name>/       # SKILL.md + references/, scripts/ など
    agents/*.agent.md
    prompts/*.prompt.md
    hooks/hooks.json
```

`.apm/` がAPMの正規レイアウトで、`apm install`/`apm compile` がここから各ターゲット(Claude Code, OpenCode, Copilot CLI など)向けの形式に変換します。

## `.claude-plugin/marketplace.json` について

ルートの `apm.yml` の `marketplace:` ブロックから `apm pack` で `.claude-plugin/marketplace.json` を生成しています(このファイルは手で編集せず、`apm pack` で再生成してください)。これはAnthropicのマーケットプレイススキーマと互換な副産物で、`apm marketplace add` / `apm search` / `apm install <pkg>@<marketplace>` によるカタログ検索を可能にするために生成しています。Claude Codeの `/plugin marketplace add` からもこのファイルを認識できますが、各パッケージの実体は `.apm/` 配下に正規化されているため native な `/plugin install` では正しく展開されません。**Claude Codeで利用する場合も上記の `apm install` を使ってください。**

## 新しいパッケージの追加方法

1. `plugins/<name>/` を作成し、`apm.yml`(name/version/description)を追加
2. `.apm/skills/`, `.apm/agents/`, `.apm/prompts/`, `.apm/hooks/` の該当するディレクトリにprimitiveを追加
3. ルート `apm.yml` の `marketplace.packages[]` にエントリを追加
4. `apm marketplace check` で解決確認、`apm pack` で `.claude-plugin/marketplace.json` を再生成

## 検証

```bash
apm marketplace check   # 全パッケージのsource/refが解決するか検証
apm pack                # marketplace.jsonを再生成
```

## ライセンス

MIT License
