# コミットすべきでないファイルパターン

## Critical（即時除外）

以下のパターンに一致するファイルは絶対にコミットしてはならない。検出した場合は即座にユーザーに警告し、.gitignoreへの追加を提案する。

| パターン | 説明 |
|----------|------|
| `.env` | 環境変数ファイル（.env.local, .env.production等も含む） |
| `.env.*` | 環境変数のバリエーション |
| `*.pem` | SSL/TLS証明書 |
| `*.key` | 秘密鍵ファイル |
| `*.p12` | PKCS#12証明書 |
| `*.pfx` | PFX証明書 |
| `credentials.json` | 認証情報ファイル |
| `service-account*.json` | GCPサービスアカウントキー |
| `*_rsa` | SSH RSA秘密鍵 |
| `*_ed25519` | SSH Ed25519秘密鍵 |
| `*_ecdsa` | SSH ECDSA秘密鍵 |
| `id_rsa` | SSH秘密鍵 |
| `id_ed25519` | SSH秘密鍵 |
| `*.secret` | シークレットファイル |
| `.htpasswd` | Apache認証ファイル |
| `token.json` | トークンファイル |
| `secrets.yml` / `secrets.yaml` | シークレット定義ファイル |
| `*.keystore` | Javaキーストア |
| `*.jks` | Javaキーストア |

## Warning（除外推奨）

以下のパターンはコミットすべきでないことが多い。検出した場合はユーザーに確認する。

| パターン | 説明 |
|----------|------|
| `*.log` | ログファイル |
| `.DS_Store` | macOSメタデータ |
| `Thumbs.db` | Windowsサムネイルキャッシュ |
| `node_modules/` | npm依存パッケージ |
| `vendor/` | 依存パッケージ（言語による） |
| `dist/` | ビルド成果物 |
| `build/` | ビルド成果物 |
| `*.min.js` | Minifiedファイル |
| `*.min.css` | Minifiedファイル |
| `coverage/` | テストカバレッジレポート |
| `.nyc_output/` | nycカバレッジデータ |
| `*.sqlite` | SQLiteデータベース |
| `*.db` | データベースファイル |
| `*.dump` | データベースダンプ |
| `__pycache__/` | Pythonキャッシュ |
| `*.pyc` | Pythonコンパイル済みファイル |
| `.terraform/` | Terraformワーキングディレクトリ |
| `*.tfstate` | Terraform状態ファイル |
| `*.tfvars` | Terraform変数ファイル（機密情報含む場合） |

## 検出ロジック

1. `git status` の出力からステージ対象ファイルを取得
2. 既存の `.gitignore` を読み込み、既にカバーされているパターンを除外
3. 残ったファイルを上記パターンと照合
4. Criticalに該当するファイルは即時警告
5. Warningに該当するファイルは確認を求める
