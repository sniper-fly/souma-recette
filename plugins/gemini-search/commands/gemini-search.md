---
allowed_for: user
description: "Gemini CLIのGoogle Search Grounding機能でWeb検索を実行"
arguments:
  - name: query
    description: "検索クエリ（スペース区切りで複数単語可）"
    required: true
---

# Gemini Search

Gemini CLIのGoogle Search Grounding機能を使用してWeb検索を実行します。

## 検索クエリ

```
$ARGUMENTS
```

## 実行手順

1. 以下のコマンドを実行して検索結果を取得してください:

```bash
${CLAUDE_PLUGIN_ROOT}/skills/gemini-search/scripts/gemini-search.sh "$ARGUMENTS"
```

2. 検索結果をマークダウン形式で整形し、ユーザーに提示してください。

3. 検索結果に含まれる情報源（URL）があれば、Sources セクションとして最後に記載してください。

## 出力形式

検索結果を以下の形式で整理してください:

- 主要な情報を箇条書きで要約
- 詳細情報がある場合は適切にセクション分け
- URLがある場合は `Sources:` として最後にリスト
