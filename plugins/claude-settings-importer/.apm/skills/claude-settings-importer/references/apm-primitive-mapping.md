# Claude Code設定 → APMプリミティブ対応表

| Claude Code側 | 変換後(APM) | 変換方法 |
|---|---|---|
| `skills/<name>/SKILL.md` | `.apm/skills/<name>/SKILL.md` | symlink解決してそのままコピー(無変換) |
| `settings.json` の `hooks` | `.apm/hooks/hooks.json` | キーをそのまま書き出し。参照するシェルスクリプト(`hooks/*.sh`)も `.apm/hooks/scripts/` に同梱 |
| `rules/*.md` | `.apm/instructions/*.instructions.md` | `description`/`applyTo: "**"` のfrontmatterを付与して変換 |
| `settings.json` の `env`/`permissions`/`statusLine`/`model` など、APMにプリミティブ対応がないキー全般 | 生成する `apm.yml` の `x-claude-settings` | 構造をそのまま保持(APMのmanifest schemaは `^x-[a-z][a-z0-9-]*$` にマッチする拡張フィールドを許可) |
| `settings.json` 全体 | `raw/settings.json` | バイト単位でバックアップ(x-claude-settingsへの変換漏れがあってもロスレスを保証する二重化) |

## 対応がないもの・注意点

- `env`/`permissions`/`statusLine`/`model` はAPMが解釈しないため、`x-claude-settings` に格納しても他ターゲット(OpenCode等)へは展開されない。Claude Codeへ戻す場合は `raw/settings.json` を使うか、`x-claude-settings` から手動で `.claude/settings.json` を再構築する
- `commands/` (スラッシュコマンド)は本スキルの変換対象外。個別のプラグイン化と同様に `.apm/prompts/*.prompt.md` へ手動変換すること
- 変換元に `hooks/*.sh` 以外の言語(Python等)のフックスクリプトがある場合、`export_settings.py` の `HOOK_SCRIPT_PATTERN` は `.sh` のみを検出する。他拡張子がある場合は個別にコピーする
