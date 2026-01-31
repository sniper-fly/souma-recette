---
description: リポジトリ全体のマルウェアスキャンを実行
argument-hint: "[--path <path>]"
allowed-tools: [Bash, Glob, Task, Read, Write]
---

# /security-check コマンド

リポジトリ内のファイルを対象にマルウェアスキャンを実行します。

## 引数

`$ARGUMENTS` には以下が渡される可能性があります：
- `--path <path>`: スキャン対象ディレクトリ（デフォルト: リポジトリルート）
- 引数なし: リポジトリ全体をスキャン

## 実行ワークフロー

以下のPhaseを順番に実行してください。

---

### Phase 1: ファイル列挙

1. Bashで全ファイルを列挙（バイナリ・不要ファイルを除外）:

```bash
# git管理下のテキストファイルを列挙
git ls-files | grep -v -E '\.(png|jpg|jpeg|gif|ico|svg|webp|woff|woff2|ttf|eot|pdf|zip|tar|gz|tgz|bz2|rar|7z|mp3|mp4|mov|avi|exe|dll|so|dylib|class|pyc|pyo|o|a|jar|war|lock)$' | grep -v -E '^(node_modules/|vendor/|\.git/)' > /tmp/security-check-files.txt

# ファイル数を確認
wc -l /tmp/security-check-files.txt
```

2. 結果を `/tmp/security-check-files.txt` に保存

---

### Phase 2: リポジトリ分析

1. Task(Explore)を呼び出してリポジトリ構造を分析:

```
Task(subagent_type=Explore):
  prompt: |
    リポジトリの構造を分析し、セキュリティスキャン用にファイルをグルーピングしてください。

    ## タスク
    1. ディレクトリ構造を把握
    2. package.json, requirements.txt等から技術スタックを特定
    3. /tmp/security-check-files.txt のファイルを機能単位でグルーピング

    ## グルーピングの基準
    - 同じ機能・モジュールに属するファイルをまとめる
    - 1グループあたり10-20ファイル程度を目安に
    - 設定ファイル群、テストファイル群は別グループに

    ## 出力形式
    以下のJSON形式で出力:
    ```json
    {
      "repository_info": {
        "name": "リポジトリ名",
        "tech_stack": ["技術1", "技術2"],
        "total_files": N
      },
      "groups": [
        {
          "name": "グループ名",
          "description": "このグループの役割",
          "files": ["path/to/file1", "path/to/file2"]
        }
      ]
    }
    ```
```

2. グルーピング結果をパースして保存

---

### Phase 3: 並列マルウェアチェック

Phase 2で得られた各グループに対して、`security-review` エージェントを**並列で**呼び出します。

**重要**: 複数のTaskを1つのメッセージで並列呼び出しすること。

```
# 複数のTaskを同時に呼び出し
Task(subagent_type=security-review):
  prompt: |
    FILE_GROUP_NAME: [グループ1の名前]
    FILE_LIST:
    - file1.ts
    - file2.ts
    ...
    CONTEXT: [グループ1の説明]

Task(subagent_type=security-review):
  prompt: |
    FILE_GROUP_NAME: [グループ2の名前]
    FILE_LIST:
    - file3.py
    - file4.py
    ...
    CONTEXT: [グループ2の説明]

# ... 他のグループも並列で呼び出し
```

各エージェントの結果を収集して保存。

---

### Phase 4: 整合性チェック

1. Phase 1のファイルリストを読み込み
2. 各SubAgentがスキャンしたファイルを集計
3. 差分を検出:

```
全ファイル: ${TOTAL}件
スキャン済み: ${SCANNED}件
漏れ: ${MISSING}件
```

4. **漏れがある場合**は追加で security-review を呼び出し:

```
Task(subagent_type=security-review):
  prompt: |
    FILE_GROUP_NAME: 追加スキャン
    FILE_LIST:
    - missing_file1.js
    - missing_file2.py
    CONTEXT: Phase 3で漏れたファイル群の追加スキャン
```

---

### Phase 5: 結果集約・レポート出力

すべてのスキャン結果を集約し、最終レポートを出力:

```markdown
# マルウェアスキャンレポート

## 実行サマリー
| 項目 | 値 |
|------|-----|
| 実行日時 | YYYY-MM-DD HH:MM |
| 対象 | [リポジトリパス] |
| ファイル数 | N |
| グループ数 | N |
| 整合性 | ✅ 全ファイルスキャン完了 / ⚠️ N件漏れあり |

## 検出結果サマリー

| 深刻度 | 件数 | ステータス |
|--------|------|----------|
| Critical | N | 🔴 |
| High | N | 🟠 |
| Medium | N | 🟡 |
| Low | N | 🟢 |

## 総合判定: [CLEAN / SUSPICIOUS / INFECTED]

---

## 詳細（深刻度順）

### Critical Issues

（あれば詳細を記載）

### High Issues

（あれば詳細を記載）

### Medium Issues

（あれば詳細を記載）

### Low Issues

（あれば詳細を記載）

---

## 推奨アクション

1. Critical/Highの問題は即時確認・対応
2. Mediumの問題はコンテキストを確認
3. Lowの問題は時間のあるときに改善

---

## スキャン対象グループ一覧

| グループ名 | ファイル数 | 結果 |
|-----------|----------|------|
| [グループ1] | N | CLEAN/SUSPICIOUS/INFECTED |
| [グループ2] | N | CLEAN/SUSPICIOUS/INFECTED |
...
```

---

## エラーハンドリング

- **ファイル読み込み失敗**: スキップして次へ進む。エラーをログに記録
- **Task失敗**: エラーを記録し、他のグループは続行
- **整合性チェックで漏れ**: 追加スキャンを実行
- **リポジトリが空**: エラーメッセージを表示して終了

---

## 使用例

```bash
# リポジトリ全体をスキャン
/security-check

# 特定ディレクトリのみスキャン
/security-check --path src/
```

---

## 注意事項

- 大規模リポジトリでは時間がかかる場合があります
- バイナリファイルは自動的にスキップされます
- node_modules等の依存関係ディレクトリはスキップされます
- 検出結果は参考情報です。最終判断は人間が行ってください
