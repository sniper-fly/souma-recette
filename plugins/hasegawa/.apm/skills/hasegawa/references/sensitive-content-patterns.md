# diff内容の機密情報パターン

diff の追加行（`+` で始まる行）に対して、以下のパターンで機密情報の混入をチェックする。

## Critical（コミット不可）

検出した場合、該当グループのコミットを停止し、ユーザーに警告する。

| パターン | 説明 | 例 |
|----------|------|----|
| `API_KEY\s*=\s*['"][^'"]+['"]` | APIキー代入 | `API_KEY = "abc123"` |
| `SECRET_KEY\s*=\s*['"][^'"]+['"]` | シークレットキー代入 | `SECRET_KEY = "xyz"` |
| `(api_key\|secret\|token\|password\|passwd)\s*[:=]\s*['"][^'"]{8,}['"]` | 認証情報の直書き | `password: "mypassword123"` |
| `-----BEGIN (RSA\|EC\|DSA\|OPENSSH)? ?PRIVATE KEY-----` | 秘密鍵ヘッダー | PEM形式の秘密鍵 |
| `ghp_[A-Za-z0-9_]{36,}` | GitHub Personal Access Token | `ghp_xxxx...` |
| `gho_[A-Za-z0-9_]{36,}` | GitHub OAuth Token | `gho_xxxx...` |
| `github_pat_[A-Za-z0-9_]{22,}` | GitHub Fine-grained PAT | `github_pat_xxxx...` |
| `sk-[A-Za-z0-9]{20,}` | OpenAI / Stripe Secret Key | `sk-xxxx...` |
| `sk-ant-[A-Za-z0-9-]{20,}` | Anthropic API Key | `sk-ant-xxxx...` |
| `xoxb-[0-9-]+` | Slack Bot Token | `xoxb-xxxx...` |
| `xoxp-[0-9-]+` | Slack User Token | `xoxp-xxxx...` |
| `xoxs-[0-9-]+` | Slack Session Token | `xoxs-xxxx...` |
| `AKIA[0-9A-Z]{16}` | AWS Access Key ID | `AKIAIOSFODNN7EXAMPLE` |
| `AIza[0-9A-Za-z_-]{35}` | Google API Key | `AIzaSyxxxx...` |

## Warning（確認必要）

テスト用の可能性があるため、ユーザーに確認を求める。

| パターン | 説明 |
|----------|------|
| `(auth_token\|access_token\|refresh_token)\s*[:=]\s*['"][^'"]+['"]` | 認証トークン代入（テスト用の可能性） |
| `[A-Za-z0-9+/]{40,}={0,2}` | 長いBase64文字列（40文字以上） |
| `(jdbc\|mysql\|postgres\|mongodb)://[^/\s]+:[^@\s]+@` | DB接続文字列にパスワード含む |

## 除外条件

以下の条件に該当する場合、パターンに一致してもスキップする:

1. **テストファイル内のダミー値**: ファイルパスが `test/`, `tests/`, `__tests__/`, `spec/`, `*_test.*`, `*.spec.*`, `*.test.*` に該当する場合
2. **コメント行**: `//`, `#`, `/*`, `*`, `--` で始まる行
3. **環境変数参照**: `process.env.`, `os.environ`, `ENV[`, `System.getenv`, `${` を含む行（値そのものではなく参照）
4. **exampleファイル**: `.example`, `.sample`, `.template` 拡張子を持つファイル
5. **明らかなプレースホルダー**: `your-api-key`, `xxx`, `dummy`, `placeholder`, `REPLACE_ME`, `TODO` を含む値

## チェック手順

```
1. git diff の出力から追加行（+ で始まる行）を抽出する
2. 除外条件に該当するファイル・行をフィルタリングする
3. 残った行に対して Critical → Warning の順でパターンマッチを実行する
4. 検出結果をレベル別にまとめて報告する:
   - Critical: 該当行の内容、ファイル名、パターン名
   - Warning: 該当行の内容、ファイル名、パターン名
```
