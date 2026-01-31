#!/bin/bash
# worktree-mirariko.sh - mirariko用worktree管理スクリプト
#
# 使用法:
#   worktree-mirariko.sh create  # worktreeを作成
#   worktree-mirariko.sh cleanup # worktreeを削除
#   worktree-mirariko.sh status  # 状態を表示

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(git rev-parse --show-toplevel)"
STATE_FILE="$PROJECT_ROOT/.mirariko-state.json"
WORKTREE_BASE="/tmp/mirariko-worktrees"

# 状態ファイルの読み込み
read_state() {
    if [[ -f "$STATE_FILE" ]]; then
        cat "$STATE_FILE"
    else
        echo "{}"
    fi
}

# 状態ファイルへの書き込み
write_state() {
    local worktree_path="$1"
    local original_branch="$2"
    local iteration="${3:-0}"

    cat > "$STATE_FILE" << EOF
{
    "worktree_path": "$worktree_path",
    "original_branch": "$original_branch",
    "iteration": $iteration,
    "created_at": "$(date -Iseconds)"
}
EOF
}

# 状態ファイルの削除
clear_state() {
    rm -f "$STATE_FILE"
}

# worktreeの作成 (Detached HEAD)
create_worktree() {
    local timestamp=$(date +%Y%m%d-%H%M%S)
    local worktree_path="$WORKTREE_BASE/mirariko-$timestamp"
    local current_branch

    # 現在のブランチ名を取得
    current_branch=$(git -C "$PROJECT_ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "HEAD")

    # worktreeディレクトリを作成
    mkdir -p "$WORKTREE_BASE"

    # Detached HEADでworktreeを作成
    git -C "$PROJECT_ROOT" worktree add --detach "$worktree_path" HEAD

    # 初期コミットを作成（空コミット）
    git -C "$worktree_path" commit --allow-empty -m "mirariko: 初期化"

    # 状態を保存
    write_state "$worktree_path" "$current_branch" 0

    echo "$worktree_path"
}

# worktreeの削除とクリーンアップ
cleanup_worktree() {
    local state=$(read_state)
    local worktree_path

    worktree_path=$(echo "$state" | grep -o '"worktree_path": "[^"]*"' | cut -d'"' -f4)

    if [[ -z "$worktree_path" ]]; then
        echo "状態ファイルが見つかりません" >&2
        return 1
    fi

    if [[ -d "$worktree_path" ]]; then
        # worktreeを削除
        git -C "$PROJECT_ROOT" worktree remove --force "$worktree_path" 2>/dev/null || true
        rm -rf "$worktree_path" 2>/dev/null || true
    fi

    # 状態ファイルを削除
    clear_state

    echo "クリーンアップ完了: $worktree_path"
}

# スカッシュマージの実行
squash_merge() {
    local state=$(read_state)
    local worktree_path
    local worktree_head

    worktree_path=$(echo "$state" | grep -o '"worktree_path": "[^"]*"' | cut -d'"' -f4)

    if [[ -z "$worktree_path" || ! -d "$worktree_path" ]]; then
        echo "worktreeが見つかりません" >&2
        return 1
    fi

    # worktreeのHEADを取得
    worktree_head=$(git -C "$worktree_path" rev-parse HEAD)

    # メインリポジトリでスカッシュマージ
    cd "$PROJECT_ROOT"
    git merge --squash "$worktree_head"

    echo "スカッシュマージ完了: $worktree_head"
}

# 状態の表示
show_status() {
    local state=$(read_state)

    if [[ "$state" == "{}" ]]; then
        echo "アクティブなmirarikоセッションはありません"
        return 0
    fi

    echo "=== mirariko セッション状態 ==="
    echo "$state" | python3 -m json.tool 2>/dev/null || echo "$state"
}

# イテレーション回数の更新
increment_iteration() {
    local state=$(read_state)
    local worktree_path original_branch current_iteration

    worktree_path=$(echo "$state" | grep -o '"worktree_path": "[^"]*"' | cut -d'"' -f4)
    original_branch=$(echo "$state" | grep -o '"original_branch": "[^"]*"' | cut -d'"' -f4)
    current_iteration=$(echo "$state" | grep -o '"iteration": [0-9]*' | grep -o '[0-9]*')

    local new_iteration=$((current_iteration + 1))
    write_state "$worktree_path" "$original_branch" "$new_iteration"

    echo "$new_iteration"
}

# メイン処理
case "${1:-help}" in
    create)
        create_worktree
        ;;
    cleanup)
        cleanup_worktree
        ;;
    squash)
        squash_merge
        ;;
    status)
        show_status
        ;;
    increment)
        increment_iteration
        ;;
    get-worktree)
        state=$(read_state)
        echo "$state" | grep -o '"worktree_path": "[^"]*"' | cut -d'"' -f4
        ;;
    help|*)
        echo "使用法: $0 {create|cleanup|squash|status|increment|get-worktree}"
        echo ""
        echo "コマンド:"
        echo "  create      - 新しいworktreeを作成"
        echo "  cleanup     - worktreeを削除してクリーンアップ"
        echo "  squash      - worktreeの変更をスカッシュマージ"
        echo "  status      - 現在の状態を表示"
        echo "  increment   - イテレーション回数をインクリメント"
        echo "  get-worktree - worktreeのパスを取得"
        ;;
esac
