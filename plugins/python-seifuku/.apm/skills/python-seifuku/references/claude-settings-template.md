# .claude/settings.json テンプレート

以下の内容をそのまま `.claude/settings.json` として配置する。

```json
{
  "plansDirectory": ".claude/plans",
  "permissions": {
    "allow": [
      "READ(./**)"
    ]
  },
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit|Update|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "./check_code_quality.sh --hooks"
          }
        ]
      }
    ]
  }
}
```

## 設定内容

- **plansDirectory**: Claude Codeの計画ファイル保存先
- **permissions.allow**: READツールでプロジェクト内全ファイルの読み取りを許可
- **hooks.PostToolUse**: Write/Edit/Update/MultiEdit後に `check_code_quality.sh --hooks` を自動実行し、品質違反があればblockする
