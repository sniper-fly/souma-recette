# Gemini CLI セットアップガイド

## 前提条件

- Node.js 18以上
- npmまたはbun

## インストール

```bash
npm install -g @anthropic-ai/gemini-cli
# または
bun install -g @anthropic-ai/gemini-cli
```

## 認証設定

Gemini CLIは2種類の認証方式をサポートしています。

### 方式1: Vertex AI（サービスアカウント）- 推奨

企業環境やCI/CD向けの認証方式です。

1. Google Cloud Consoleでサービスアカウントを作成
2. 必要な権限を付与:
   - `aiplatform.endpoints.predict`
   - `aiplatform.models.predict`
3. JSONキーファイルをダウンロード
4. 環境変数を設定:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
export GOOGLE_CLOUD_PROJECT="your-project-id"
```

### 方式2: OAuth（個人利用）

対話的なログインによる認証方式です。

```bash
gemini --login
```

ブラウザが開き、Googleアカウントでログインします。

## 動作確認

```bash
# ヘルプ表示
gemini --help

# 簡単なテスト
gemini "Hello, world!"

# Google Search Grounding テスト
gemini "What is the latest news about AI?" --allowed-tools google_web_search
```

## トラブルシューティング

### 認証エラー

```
Error: Could not load the default credentials
```

**解決策**: 環境変数を確認

```bash
echo $GOOGLE_APPLICATION_CREDENTIALS
echo $GOOGLE_CLOUD_PROJECT
```

### レート制限

```
Error: Resource exhausted
```

**解決策**: しばらく待ってから再試行。Vertex AIの無料枠には制限があります。

### 検索機能が動作しない

```
Error: Tool google_web_search not available
```

**解決策**: Gemini 2.5系モデルを使用しているか確認。Google Search Groundingは2.5系モデルで利用可能です。

## 参考リンク

- [Gemini CLI 公式ドキュメント](https://github.com/google-gemini/gemini-cli)
- [認証設定ガイド](https://google-gemini.github.io/gemini-cli/docs/get-started/authentication.html)
- [Grounding with Google Search](https://ai.google.dev/gemini-api/docs/google-search)
