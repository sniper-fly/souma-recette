---
name: claude-settings-importer
description: This skill should be used when the user asks to "個人のClaude設定をAPM化して", "~/.claude をAPMパッケージにして", "プロジェクトのClaude設定を集約して", "claude-settings-importer", or needs to convert personal (~/.claude/) or project-local (.claude/) Claude Code settings (skills, hooks, rules, env/permissions) into a portable APM package.
allowed_tools: Bash, Read, Write, Glob, AskUserQuestion
---

# claude-settings-importer

個人設定(`~/.claude/`)またはプロジェクト固有設定(`.claude/`)をAPM形式のパッケージに変換して書き出すスキルです。souma-recetteリポジトリの `plugins/` には追加しません(個人設定は別リポジトリで管理するのが自然なため、出力するだけに留めます)。

## 実行手順

### Step 1: 変換対象スコープの確認

ユーザーに次を確認してください(明示済みなら省略可):
- スコープ: `personal`(`~/.claude/`) か `project`(カレントプロジェクトの `.claude/`)
- 出力先ディレクトリ: 省略時は `generated/personal-claude-config/`(personal)または `generated/project-claude-config/`(project)
- 出力パッケージ名: 省略時は `personal-claude-settings` または `<プロジェクト名>-claude-settings`

個人設定・プロジェクト設定を両方変換したい場合は、必ず別パッケージとして出力してください(1つの `apm.yml` に混在させない)。

### Step 2: 変換スクリプトの実行

```bash
python3 scripts/export_settings.py \
  --claude-dir <スコープに応じた.claudeディレクトリ> \
  --output <出力先ディレクトリ> \
  --name <パッケージ名> \
  --description "<説明文>"
```

このスクリプトが以下を自動で行います:
- `skills/*` を symlink 解決して `.apm/skills/` へコピー
- `settings.json` の `hooks` を `.apm/hooks/hooks.json` として書き出し、参照するシェルスクリプトも `.apm/hooks/scripts/` に同梱
- `rules/*.md` を `.apm/instructions/*.instructions.md` に変換(`applyTo: "**"` を付与)
- 上記以外の `settings.json` キー(`env`/`permissions`/`statusLine`/`model` 等)を生成する `apm.yml` の `x-claude-settings` に格納
- `settings.json` 全体を `raw/settings.json` にバイト単位でバックアップ

詳細な対応表は [apm-primitive-mapping.md](references/apm-primitive-mapping.md) を参照してください。

### Step 3: 生成物のレビュー

以下を確認し、ユーザーに要約を報告してください:
1. `<出力先>/.apm/skills/` に想定したスキルがすべて存在するか(`ls`)
2. `<出力先>/.apm/hooks/hooks.json` があれば、参照スクリプトが `.apm/hooks/scripts/` に実在するか(パス欠落がないか)
3. `<出力先>/apm.yml` の `x-claude-settings` に、`hooks` 以外の設定(`env`, `permissions`, `statusLine`, `model` など)が漏れず入っているか
4. `<出力先>/raw/settings.json` が元の `settings.json` とバイト一致するか(`diff`)

### Step 4: 動作確認(任意)

生成したパッケージが実際にインストール可能か確認する場合:

```bash
apm marketplace check 2>&1 || true   # 単体パッケージなのでmarketplace対象外、apm.ymlのYAML構文確認目的
apm install <出力先の絶対パス> --target claude --dry-run
```

## 注意事項

- `commands/`(スラッシュコマンド)は変換対象外。必要であれば個別に `.apm/prompts/*.prompt.md` へ手動変換する
- `env`/`permissions`/`statusLine`/`model` はAPMの他ターゲット(OpenCode等)には展開されない。Claude Codeでのみ意味を持つ設定であることをユーザーに伝える
- このスキル自体はsouma-recetteの `plugins/` へ追加しない。出力はユーザー指定のディレクトリに留める
