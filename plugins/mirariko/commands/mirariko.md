---
description: スキルベースの実装計画書レビュー＆ブラッシュアップワークフロー
argument-hint: "[スキル名] [計画書パス]"
allowed-tools: [Read, Write, Bash, AskUserQuestion, Task, TodoWrite]
---

# /mirariko コマンド

指定スキルを使って実装計画書をイテレーティブにレビュー・ブラッシュアップするワークフローコマンドです。

## 引数

`$ARGUMENTS` には以下が渡されます：
- 第1引数: スキル名（例: `terraform-review`）
- 第2引数: 計画書パス（例: `docs/implementation-plan.md`）

## 実行ワークフロー

### Phase 1: 初期化

1. 引数をパースして検証
2. worktreeを作成（Detached HEAD）
3. 状態ファイルを初期化

### Phase 2: レビュー＆ブラッシュアップループ

ユーザーが満足するまで以下を繰り返す：

1. **レビュー**: `plan-reviewer` エージェントでスキルベースのレビューを実行
2. **確認**: AskUserQuestionで次のアクションを確認
   - 「満足」→ Phase 3へ
   - 「修正が必要」→ ブラッシュアップへ
   - 「中止」→ クリーンアップして終了
3. **ブラッシュアップ**: `plan-brushup` エージェントで改善＋コミット

### Phase 3: 完了処理

1. スカッシュマージ
2. worktreeのクリーンアップ
3. 完了報告

---

## 実装手順

以下の手順で実装してください：

### Step 1: 引数の検証

```bash
# 引数を分割
SKILL_NAME=$(echo "$ARGUMENTS" | awk '{print $1}')
PLAN_PATH=$(echo "$ARGUMENTS" | awk '{print $2}')

# 引数が不足している場合はエラー
if [[ -z "$SKILL_NAME" || -z "$PLAN_PATH" ]]; then
    echo "エラー: スキル名と計画書パスを指定してください"
    echo "使用法: /mirariko [スキル名] [計画書パス]"
    exit 1
fi

# 計画書の存在確認
if [[ ! -f "$PLAN_PATH" ]]; then
    echo "エラー: 計画書が見つかりません: $PLAN_PATH"
    exit 1
fi
```

### Step 2: worktreeの作成

```bash
WORKTREE_PATH=$(${CLAUDE_PLUGIN_ROOT}/scripts/worktree-mirariko.sh create)
echo "worktreeを作成しました: $WORKTREE_PATH"

# 計画書をworktreeにコピー
cp "$PLAN_PATH" "$WORKTREE_PATH/$PLAN_PATH"
```

### Step 3: レビュー＆ブラッシュアップループ

```
LOOP:
  1. Task(plan-reviewer)を呼び出し:
     - SKILL_NAME: ${SKILL_NAME}
     - PLAN_PATH: ${WORKTREE_PATH}/${PLAN_PATH}

  2. レビュー結果を表示

  3. AskUserQuestionで確認:
     - 「満足しました」→ goto MERGE
     - 「修正が必要です」→ ユーザーからのフィードバックを受け取る
     - 「中止します」→ goto CLEANUP

  4. Task(plan-brushup)を呼び出し:
     - WORKTREE_PATH: ${WORKTREE_PATH}
     - PLAN_PATH: ${PLAN_PATH}
     - REVIEW_FEEDBACK: [レビュー結果 + ユーザーフィードバック]

  5. イテレーション回数をインクリメント

  6. goto LOOP
```

### Step 4: スカッシュマージ (MERGE)

```bash
# スカッシュマージ実行
${CLAUDE_PLUGIN_ROOT}/scripts/worktree-mirariko.sh squash

# 変更を確認してユーザーに報告
git diff --cached --stat
```

### Step 5: クリーンアップ (CLEANUP)

```bash
# worktreeを削除
${CLAUDE_PLUGIN_ROOT}/scripts/worktree-mirariko.sh cleanup

echo "mirarikоセッションを終了しました"
```

---

## 状態管理

`.mirariko-state.json` で以下を管理：
- `worktree_path`: 作業用worktreeのパス
- `original_branch`: 元のブランチ名
- `iteration`: イテレーション回数
- `created_at`: セッション開始時刻

## エラーハンドリング

- worktree作成失敗: エラーメッセージを表示して終了
- スキルが見つからない: エラーメッセージを表示して終了
- ユーザー中止: クリーンアップして正常終了

## 使用例

```
/mirariko terraform-review docs/infra-plan.md
/mirariko prompt-optimization plans/feature-spec.md
```
