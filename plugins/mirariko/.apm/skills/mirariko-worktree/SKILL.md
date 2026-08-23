---
name: mirariko-worktree
description: "/mirariko コマンドが内部で使用するworktree管理ユーティリティ(create/squash/cleanup)。単体で呼び出す必要はありません。"
disable-model-invocation: true
---

# mirariko worktree ユーティリティ

`/mirariko` コマンドの実装手順から `scripts/worktree-mirariko.sh` を呼び出すために存在するスキルです。ユーザーが直接使うことはありません。

## 使用方法

```bash
scripts/worktree-mirariko.sh create   # worktreeを作成
scripts/worktree-mirariko.sh squash   # スカッシュマージ
scripts/worktree-mirariko.sh cleanup  # worktreeを削除
scripts/worktree-mirariko.sh status   # 状態を表示
```
