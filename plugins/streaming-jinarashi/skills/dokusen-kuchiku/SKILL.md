---
name: dokusen-kuchiku
description: >-
  This skill should be used when the user asks to
  "シーズンのアニメ配信情報を一括調査", "独占配信アニメを特定",
  "配信状況をまとめて調べて", "アニメの配信先を一括で調査",
  "独占駆逐して", "dokusen-kuchiku",
  or needs to orchestrate bulk streaming service research for a specific anime season.
allowed_tools: Bash, Read, Edit, Skill, Task, TaskCreate, TaskGet, TaskList, TaskUpdate, Write, TaskOutput
version: 1.1.0
---

# 独占駆逐 (dokusen-kuchiku)

特定シーズンの全アニメについて、配信サービス情報を一括で調査し、独占配信・複数配信の分析レポートを生成するオーケストレーションスキル。

## 入力パラメータ

| パラメータ | 必須 | 説明 | 例 |
|-----------|------|------|----|
| year | Yes | 調査対象の年 | 2026 |
| season | Yes | 調査対象のシーズン | WINTER, SPRING, SUMMER, FALL |

## 実行ワークフロー

以下のステップを順番に実行する。いずれかのステップで致命的エラーが発生した場合、以降のステップを中止してユーザーに報告する。

### Step 1: アニメ公式サイト一覧の取得

`anime-official-site-researcher` スキルを使用して、指定シーズンのアニメ公式サイトURL一覧を取得する。

**実行手順:**

1. `Skill` ツールで `streaming-jinarashi:anime-official-site-researcher` を呼び出す
2. スキルの指示に従い、`scripts/fetch_seasonal_anime.py` を `year` と `season` を引数として実行する
3. 出力されるJSON配列を解析し、各アニメの `title` と `officialSiteUrl` を取得する
4. `officialSiteUrl` が `null` または空のアニメは調査対象から除外し、除外したことを記録する

**期待される出力形式:**

```json
[
  {
    "title": { "romaji": "...", "native": "..." },
    "officialSiteUrl": "https://..."
  }
]
```

### Step 2: 配信サービス情報の並列収集

取得した各アニメについて、`Skill` ツールで `streaming-jinarashi:anime-streaming-researcher` を呼び出し、配信サービス情報を **最大10並列** で収集する。

各アニメのセッション名は英語（romaji）タイトルから自動生成されるため、セッションの競合は発生しない。

**重要: 並列実行の制御（スライディングウィンドウ方式）**

- 同時実行数の上限は **最大10** とする
- 1つのタスクが完了したら即座に次の未実行タスクを開始する
- 常に最大10個のタスクが並列実行されている状態を維持する
- 全タスクの完了後に Step 3 に進む

**実行手順:**

1. アニメリスト全体をキューとして扱う
2. まず最初の10件（またはリスト全体が10件未満の場合は全件）について、`Task` ツール（`run_in_background: true`）で `streaming-jinarashi:anime-streaming-researcher` スキルを呼び出す Agent を起動する
3. 以下のパラメータを引数として渡す:
   - アニメタイトル（日本語）: `{title.native}`
   - アニメタイトル（英語）: `{title.romaji}`
   - 公式サイトURL: `{officialSiteUrl}`
   - REPORT_OUTPUT_DIR: `<absolute_path_to>/reports/{year}/{season}`
4. `TaskOutput` で完了を監視し、いずれかのタスクが完了したら、キューに未実行のアニメが残っていれば即座に新しい `Task` を起動する
5. これを繰り返し、常に最大10並列を維持しながら全アニメの調査を完了させる

### Step 3: 結果の集約とレポート生成

全 Agent の実行完了後、各アニメの調査結果を集約してレポートを生成する。

**手順:**

1. `REPORT_OUTPUT_DIR` ディレクトリ配下の各アニメフォルダから `report_*.json` を読み取る
2. 全アニメの結果を以下のカテゴリに分類する:
   - **独占配信:** `streaming_service` 配列の要素数が 1
   - **複数サービス配信:** `streaming_service` 配列の要素数が 2 以上
   - **配信先なし:** `streaming_service` 配列が空、または `error` が存在する
3. `references/report-format.md` のテンプレートに従い、集約レポートを `<REPORT_OUTPUT_DIR>/summary_report.md` に出力する
4. レポートの内容をユーザーにサマリーとして表示する

## エラーハンドリング

| エラー状況 | 対応 |
|-----------|------|
| fetch_seasonal_anime.py 実行失敗 | エラー内容を表示し中止 |
| 一部 Agent の失敗 | 失敗分を「配信先なし」として記録し、レポートに含める |
| 全 Agent の失敗 | エラーを表示し、レポートにはエラーサマリーのみ出力 |

## 参考資料

### レポートフォーマット

集約レポートの詳細なテンプレートとフォーマットルールは `references/report-format.md` を参照する。
