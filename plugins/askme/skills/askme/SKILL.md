---
name: askme
description: This skill should be used when requirements have ambiguity or multiple interpretations, when there are multiple valid implementation approaches, when uncertainty exists that would be risky to assume through, or when the user asks about "clarification", "requirements validation", "approach confirmation". Enforces explicit confirmation over assumption.
---

# Askme スキル

## 核心原則

**仮定より確認**: 不確実な点は推測で進めず、AskUserQuestionツールで明示的に確認する。

## トリガー条件

以下のいずれかに該当する場合にこのスキルを適用:

1. **要件の曖昧さ**: 複数の解釈が可能な要件が存在する
2. **複数アプローチ**: 実装方法に複数の有効な選択肢がある
3. **リスクある不確実性**: 仮定で進めると手戻りや問題が発生するリスクがある

## 判断基準

### 確認すべきケース

| 状況 | 例 |
|------|-----|
| 複数解釈 | 「ユーザー一覧を表示」→ ページネーション要否、表示項目、ソート順 |
| 技術選択 | 「キャッシュを追加」→ Redis/Memcached/インメモリの選択 |
| 範囲不明確 | 「エラーハンドリング改善」→ 対象箇所、リトライ戦略、ログ出力 |
| 破壊的変更 | データベーススキーマ変更、API仕様変更 |

### 確認不要なケース

| 状況 | 理由 |
|------|------|
| 明示的指示 | ユーザーが具体的に指定済み |
| 標準的慣行 | コードベースやフレームワークの既存パターンに従う |
| 自明な選択 | 技術的に唯一の妥当な選択肢 |
| 軽微な決定 | 手戻りコストが極めて低い |

## AskUserQuestion ツールの活用

### 効果的な質問設計

例
```yaml
questions:
  - question: "キャッシュの実装方式はどちらを希望しますか？"
    header: "Cache"
    options:
      - label: "Redis（推奨）"
        description: "分散環境対応、永続化可能、スケーラブル"
      - label: "インメモリ"
        description: "シンプル、外部依存なし、単一プロセス向け"
    multiSelect: false
```

### 質問の原則

1. **具体性**: 漠然とした確認ではなく、具体的な選択肢を提示
2. **根拠提示**: 各選択肢のトレードオフを明記
3. **推奨明示**: 技術的に推奨がある場合は「（推奨）」と明示

### アンチパターン

- ❌ 確認のための確認（「これで進めていいですか？」）
- ❌ 自明な事項の確認（既存パターンに従う場合）
- ❌ 過度な選択肢（5つ以上の選択肢提示）
- ❌ 曖昧な質問（「どうしますか？」）

## 実践ワークフロー

### 1. 要件分析

タスクを受け取ったら、まず以下を評価:

- 明示されていない前提は何か
- 複数の解釈が可能な箇所はどこか
- 技術的選択肢は何があるか

### 2. 確認判断

トリガー条件に照らし、確認が必要か判断:

- 仮定で進めた場合のリスクは？
- 手戻りコストはどの程度か？
- 既存パターンで判断可能か？

### 3. 質問実行

確認が必要な場合、AskUserQuestionを使用:

- 選択肢を具体的に提示
- トレードオフを明記
- 推奨がある場合は明示

## 期待効果

- 手戻りの削減
- 認識齟齬の早期解消
- ユーザー意図の正確な反映
