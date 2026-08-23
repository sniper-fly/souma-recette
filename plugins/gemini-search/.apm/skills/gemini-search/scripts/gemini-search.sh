#!/bin/bash
# Gemini CLI Google Search Grounding スクリプト
# 使用方法: gemini-search.sh "検索クエリ"

set -euo pipefail

# 引数チェック
if [ $# -eq 0 ]; then
    echo "Usage: gemini-search.sh \"検索クエリ\"" >&2
    exit 1
fi

QUERY="$*"

# Gemini CLIで検索を実行
# --allowed-tools: google_web_searchのみを自動承認（安全性重視）
# -o json: JSON形式で出力
result=$(gemini "$QUERY" --allowed-tools google_web_search -o json 2>/dev/null)

# jqがインストールされているか確認
if command -v jq &> /dev/null; then
    # JSON出力からresponseフィールドを抽出
    echo "$result" | jq -r '.response // empty'
else
    # jqがない場合は生のJSONを出力
    echo "$result"
fi
