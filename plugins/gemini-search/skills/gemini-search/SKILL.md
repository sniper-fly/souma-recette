---
name: google_search
description: Gemini CLIのGoogle Search Grounding機能を使用してWeb検索を実行します。Claude CodeのWebSearchツールの代替として使用できます。
triggers:
  - search with gemini
  - gemini search
  - google search grounding
  - find latest information with gemini
---

# Gemini CLI Web Search スキル

## 概要

Gemini 2.5系モデルに組み込まれたGoogle Search Grounding機能を活用し、最新のWeb情報を検索・取得するスキルです。

## 使用方法

### コマンドでの実行

```bash
/gemini-search [検索クエリ]
```

### スクリプト直接実行

```bash
${CLAUDE_PLUGIN_ROOT}/skills/gemini-search/scripts/gemini-search.sh "検索クエリ"
```

## 検索実行フロー

1. ユーザーから検索クエリを受け取る
2. Gemini CLIを`--allowed-tools google_web_search`オプション付きで実行
3. JSON出力から`response`フィールドを抽出
4. 整形された検索結果を返す

## 特徴

- **安全性重視**: `--yolo`ではなく`--allowed-tools google_web_search`を使用し、検索ツールのみを自動承認
- **JSON出力**: `-o json`で構造化された出力を取得し、jqで整形
- **Vertex AI認証**: サービスアカウントJSONファイルによる認証（`GOOGLE_APPLICATION_CREDENTIALS`環境変数）

## 制限事項

- Gemini APIのレート制限が適用されます
- 検索結果はGeminiモデルが要約するため、原典URLが常に含まれるわけではありません
- 検索ツール以外の機能（コード実行等）は無効化されています

## 認証設定

初回セットアップについては [setup-guide.md](references/setup-guide.md) を参照してください。

## 関連リソース

- [Gemini CLI GitHub](https://github.com/google-gemini/gemini-cli)
- [Grounding with Google Search](https://ai.google.dev/gemini-api/docs/google-search)
