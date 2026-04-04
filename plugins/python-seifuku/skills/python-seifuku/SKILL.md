---
name: python-seifuku
description: This skill should be used when the user asks to "Pythonプロジェクトをセットアップして", "python-seifuku", "コード品質チェックhookを設定して". Pythonの標準ガードレール(uv, ruff, mypy, pytest, PostToolUse hooks)を自動整備する。
allowed_tools: Bash, Read, Write, AskUserQuestion, Glob
disable-model-invocation: true
---

# python-seifuku - Python プロジェクト初期セットアップ

uv + ruff + mypy + pytest 構成の Python プロジェクトを初期セットアップし、Claude Code PostToolUse hooks によるコード品質チェック自動化を構成する。

## 前提条件

- uv がインストール済みであること。未インストールの場合: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- jq がインストール済みであること（hooks の JSON 出力に必要）

## ワークフロー

以下の5ステップを順番に実行する。

### Step 1: プロジェクト情報の収集

AskUserQuestion で以下の情報を収集する:

- **プロジェクト名**（ケバブケース推奨、例: `my-app`）
- **プロジェクトの説明**
- **Python バージョン**（デフォルト: `3.12`）
- **初期依存関係**（任意、例: `pydantic>=2.12.5`）

ユーザーのリクエストに既に含まれている情報は再度確認せずに使用する。

既存プロジェクトに対してセットアップを行う場合は、既存の `pyproject.toml` の有無を Glob で確認し、上書きするか追記するかを AskUserQuestion で確認する。

### Step 2: pyproject.toml 生成

1. `references/pyproject-template.md` を Read で読み込む
2. テンプレート内のプレースホルダーを Step 1 で取得した値で置換する:
   - `{PROJECT_NAME}` → プロジェクト名
   - `{DESCRIPTION}` → 説明
   - `{PYTHON_VERSION}` → Python バージョン（例: `3.12`）
   - `{PYTHON_VERSION_SHORT}` → ドットなしバージョン（例: `py312`）
   - `{DEPENDENCIES}` → 依存関係リスト（各行 `    "package>=x.y.z",` 形式）
   - `{MYPY_IGNORE_MODULES}` → mypy 除外モジュール（依存関係に応じて設定、不要なら `[[tool.mypy.overrides]]` セクションごと削除）
3. プロジェクトルートに `pyproject.toml` として Write で書き出す

### Step 3: check_code_quality.sh 配置

1. `scripts/check_code_quality.sh` を Read で読み込む
2. プロジェクトルートに `check_code_quality.sh` として Write で書き出す
3. 実行権限を付与する:

```bash
chmod +x check_code_quality.sh
```

### Step 4: Claude Code 設定

1. `references/claude-settings-template.md` を Read で読み込む
2. `.claude/settings.json` として Write で書き出す（`.claude/` ディレクトリが存在しない場合は `mkdir -p .claude` で作成）
3. `references/claude-md-template.md` を Read で読み込む
4. プロジェクトルートに `CLAUDE.md` として Write で書き出す

### Step 5: 依存関係インストールと検証

1. 開発依存関係をインストールする:

```bash
uv sync
```

2. コード品質チェックスクリプトの動作を確認する:

```bash
./check_code_quality.sh
```

セットアップが正常に完了したことをユーザーに報告する。

## リファレンス

- **`references/pyproject-template.md`** - pyproject.toml テンプレートとプレースホルダー説明
- **`references/claude-settings-template.md`** - .claude/settings.json テンプレート（PostToolUse hooks 設定）
- **`references/claude-md-template.md`** - CLAUDE.md テンプレート（hooks 前提の開発ルール）
- **`scripts/check_code_quality.sh`** - コード品質チェックスクリプト（ruff format, ruff check, mypy, pytest）
