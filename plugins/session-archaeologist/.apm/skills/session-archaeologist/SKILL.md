---
name: session-archaeologist
description: >-
  This skill should be used when the user asks to
  "会話ログを分析して", "開発ヒストリーをまとめて", "過去のセッションを調べて",
  "試行錯誤の履歴を要約して", "開発の経緯を振り返って",
  "Zenn記事用に開発ログをまとめて", "会話ログからハイライトを抽出して",
  or needs to analyze Claude Code conversation history for a specific topic.
version: 1.0.0
allowed_tools: Bash, Read, Grep, Glob, Task
---

# セッション考古学 (Session Archaeologist)

Claude Codeの過去の会話ログ（JSONLセッションファイル）を発掘・分析し、特定トピックの開発における試行錯誤プロセス、ハイライト、インサイトを構造化して要約するスキル。

## 入力

- **トピック / キーワード**（必須）: 検索対象のトピックやキーワード。カンマ区切りで複数指定可能
- **プロジェクトパス**（オプション）: 対象プロジェクトのパス。省略時はカレントプロジェクトのパスを使用

## ワークフロー

### ステップ1: 関連セッションの検索

`scripts/extract_sessions.py` を使用して、指定キーワードにマッチするセッションを検索する。

```bash
python {SKILL_DIR}/scripts/extract_sessions.py \
  --project-path "{PROJECT_PATH}" \
  --keywords "{KEYWORDS}"
```

出力はJSON形式で、マッチしたセッションの一覧（session_id, ファイルサイズ, 更新日時, 最初のユーザーメッセージ）を返す。

**プロジェクトパスの決定:**

- ユーザーが指定した場合はそのパスを使用する
- 未指定の場合は、カレントワーキングディレクトリを使用する

### ステップ2: セッション内容の抽出

マッチしたセッションが少数（10件以下）の場合は `--extract` フラグで一括抽出する:

```bash
python {SKILL_DIR}/scripts/extract_sessions.py \
  --project-path "{PROJECT_PATH}" \
  --keywords "{KEYWORDS}" \
  --extract
```

マッチ数が多い場合は、ステップ1の結果から重要なセッション（ファイルサイズが大きいもの、first_promptがトピックに直接関連するもの）を選別し、個別に抽出する:

```bash
python {SKILL_DIR}/scripts/extract_sessions.py \
  --project-path "{PROJECT_PATH}" \
  --keywords "" \
  --session-id "{SESSION_UUID}"
```

**大量セッションの処理:** セッション数が多い場合は、Task ツール（subagent_type: general-purpose）を使って並列に分析する。各エージェントに5-10セッション分のメッセージ抽出結果を渡し、フェーズごとの要約を依頼する。

### ステップ3: 時系列の整理

抽出したメッセージを時系列順に整理し、以下を特定する:

1. **ユーザーの指示パターン** - 何を依頼し、どう方向修正したか
2. **エラーと解決** - 発生した問題とその解決策
3. **アーキテクチャの転換点** - 技術やアプローチが大きく変わった場面
4. **反復的改善のループ** - テスト→発見→修正のサイクル

### ステップ4: 構造化レポートの生成

`references/output-template.md` のテンプレートに従い、以下を含む分析レポートを生成する:

- タイムライン表
- フェーズ分析（技術スタック変更やアーキテクチャ転換でフェーズを分割）
- 試行錯誤のハイライト（エラー回復、設計壁打ち、ピボット等）
- 教訓とインサイトの一覧
- 関連するgitコミット履歴（`git log --oneline` から該当分を抽出）

### ステップ5: 関連gitコミットの取得

トピックに関連するgitコミットを取得して、レポートに付記する:

```bash
git log --oneline --all | grep -i "{keyword}"
```

## 分析の観点

レポートを生成する際、以下の観点を重視する:

- **技術記事の素材として有用なエピソード** を優先的に抽出する
- 単なるログの羅列ではなく、**なぜその判断をしたか**のストーリーを構成する
- エラーや失敗は隠さず、**そこから何を学んだか**を明示する
- **ユーザーとAIの対話による設計改善**の過程を特にハイライトする

## 出力形式

分析結果はMarkdown形式でユーザーに直接表示する（ファイル出力はユーザーが求めた場合のみ）。

## 参考リソース

### リファレンスファイル

- **`references/jsonl-format.md`** - Claude Codeセッションログの JSONL フォーマット仕様
- **`references/output-template.md`** - 分析レポートの出力テンプレートとハイライト抽出基準
