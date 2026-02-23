---
name: anime-streaming-researcher
description: 「配信サービスを調べて」「アニメの配信先を確認」「どこで見れるか調べて」「公式サイトから配信情報を調査」などのリクエストに対応するスキル
version: 2.0.0
allowed_tools: Bash, Read, Edit, Skill, Write
context: fork
agent: general-purpose
---

# アニメ配信サービス検索スキル

Playwright CLIを使用して、アニメの公式サイトから配信サービス情報を自動取得するスキルです。

## 入力

このスキルは以下の情報を入力として受け取ります：

- **アニメタイトル（日本語）** - 調査対象のアニメ名（日本語表記、例: `葬送のフリーレン`）
- **アニメタイトル（英語）** - 調査対象のアニメ名（romaji表記、例: `Sousou no Frieren`）
- **公式サイトURL** - アニメの公式サイトURL
- **REPORT_OUTPUT_DIR** - レポートの出力先親ディレクトリパス

## セッション名の決定

Playwright CLIのセッション名は、英語（romaji）タイトルから自動的に生成する。

**生成ルール:**

1. 英語タイトルからアルファベット・数字・スペース以外の特殊記号を除去する
2. スペースをハイフン `-` に置換する
3. 小文字に変換する

**例:**

| 英語タイトル | セッション名 |
|-------------|-------------|
| `Sousou no Frieren` | `sousou-no-frieren` |
| `Re:ZERO -Starting Life in Another World-` | `rezero-starting-life-in-another-world` |
| `Oshi no Ko 2nd Season` | `oshi-no-ko-2nd-season` |

## Playwright CLIの使い方

**重要:** ブラウザ操作には必ず `playwright-cli` スキルを使用すること。コマンドの詳細やオプションは `playwright-cli` スキルを参照する。

すべてのコマンドに `-s={SESSION_NAME}` を付与してセッションを分離する。必ず入力の英語タイトルから生成した SESSION_NAME を使い、他のセッションのブラウザを操作してはならない。

## ワークフロー

### ステップ1: 公式サイトから配信情報を探索

Playwright CLIを使用して公式アニメサイトをナビゲートし、配信情報を収集します。

**探索フロー:**

1. **ブラウザを開く** - `playwright-cli -s={SESSION_NAME} open {公式サイトURL}` でページを開く
2. **テキスト検索** - `playwright-cli -s={SESSION_NAME} snapshot` / `playwright-cli -s={SESSION_NAME} eval "code"` を使用してページコンテンツから配信サービスのキーワードを検索
3. **フォールバック: スクリーンショット分析** - テキスト検索で情報が得られない場合に限り、スクリーンショットを撮影して画像解析（撮影先は必ず `REPORT_OUTPUT_DIR` 配下）
4. **エビデンスハイライト** - 配信情報が特定できたら、`playwright-cli -s={SESSION_NAME} run-code "async page => { ... }"` を使用して該当テキスト要素の背景色をハイライト（例: `element.style.backgroundColor = 'yellow'`）し、どの情報を参考にしたか視覚的に明示する。**注意:** ハイライト処理は関数定義やforEachを含む複数行コードになるため、`eval` ではなく `run-code` を使用すること（`eval` はシリアライズエラーになる）
5. **エビデンス撮影** - ハイライト適用後、最終エビデンス用スクリーンショットを `REPORT_OUTPUT_DIR` 配下に撮影・保存

**探索段階のファイル生成ルール:**

- 探索段階では `snapshot` / `eval` のみを使用し、**ファイルを生成しない**
- スクリーンショットは**最終エビデンス用としてのみ**撮影し、必ず `REPORT_OUTPUT_DIR` 配下に保存する
- `REPORT_OUTPUT_DIR` 以外の場所（プロジェクトルート等）にファイルを生成してはならない

**探索設定:**

- 最大リトライ回数: 5回（異なるページ/セクションを探索）
- 対象サービス: 定額見放題サービスのみ（下記の重要な注意事項を参照）

### ステップ2: 出力の生成

**出力先ディレクトリ構造:**

すべての出力は `REPORT_OUTPUT_DIR` 配下にアニメタイトルごとのサブディレクトリを作成して保存します。

```
{REPORT_OUTPUT_DIR}/
└── {anime_title}/
    ├── report_{datetime}.json
    └── ss_{datetime}.png
```

**スクリーンショット保存:**

- パス: `{REPORT_OUTPUT_DIR}/{anime_title}/ss_{datetime}.{拡張子}`
- `{datetime}` は `YYYYMMDD_HHmmss` 形式（例: `20260222_143052`）
- 拡張子はスクリーンショットの形式に応じて `png`, `jpg` 等を使用

**JSONレポート保存:**

- パス: `{REPORT_OUTPUT_DIR}/{anime_title}/report_{datetime}.json`
- `{datetime}` はスクリーンショットと同一のタイムスタンプを使用

**成功時のフォーマット:**

```json
{
  "title": "アニメタイトル",
  "url": "公式サイトURL",
  "screenshot": "{REPORT_OUTPUT_DIR}/{anime_title}/ss_{datetime}.png",
  "streaming_service": ["Netflix", "Amazon Prime Video", "..."],
  "error": null
}
```

**エラー時のフォーマット（配信情報が見つからない場合）:**

```json
{
  "title": "アニメタイトル",
  "url": "公式サイトURL",
  "screenshot": "{REPORT_OUTPUT_DIR}/{anime_title}/ss_{datetime}.png",
  "streaming_service": [],
  "error": "配信先が見つかりませんでした"
}
```
## エビデンスハイライト手順

最終エビデンスのスクリーンショットを撮影する前に、配信情報として参照したテキスト要素を視覚的にハイライトする。

**原則:**

- ハイライト対象は**実際に `streaming_service` の根拠として参照したセクション・要素のみ**に限定する
- 同じサービス名がページ内の別セクション（個別課金、レンタル等）にも存在する場合があるため、ページ全体へのキーワードマッチは避ける
- 探索ステップで取得した `snapshot` のDOM構造を活用し、根拠となったセクションのコンテナ要素を特定した上で、そのコンテナ内の要素のみをハイライトする

**手順:**

1. 探索ステップで特定した「定額見放題」セクションのコンテナ要素をCSSセレクタ等で特定する
2. `playwright-cli -s={SESSION_NAME} run-code "async page => { await page.evaluate(() => { ... }); }"` を使用し、そのコンテナ内の要素に対してのみ背景色を設定（例: `element.style.backgroundColor = 'yellow'`）
3. **コントラストチェック** - ハイライト適用後、テキストの可読性を確認・補正する（下記「アクセシビリティ対応」参照）
4. ハイライト適用後にスクリーンショットを撮影

### アクセシビリティ対応（ハイライト時のコントラスト補正）

黄色背景のハイライトを適用する際、元のテキスト色が白や明るい色の場合に文字が読めなくなる問題を防ぐ。

**原則:**

- ハイライト背景色（黄色系）に対して、テキストが十分なコントラスト比を持つことを保証する
- 元のテキスト色を尊重しつつ、可読性が損なわれる場合のみ補正する

**実装手順:**

`playwright-cli -s={SESSION_NAME} run-code "async page => { ... }"` でハイライトを適用する際、以下のコントラストチェックを同時に実行する：

1. ハイライト対象の各要素について `window.getComputedStyle(element).color` で現在のテキスト色を取得する
2. テキスト色のRGB値から相対輝度を算出し、明るい色（白、薄いグレー等）かどうかを判定する
3. テキスト色が明るい場合（相対輝度が0.5以上を目安）、`element.style.color = '#333'` 等の暗い色に変更する
4. リンク要素（`<a>`タグ）のテキスト色も同様にチェック・補正する

**判定ロジック例（JavaScript）:**

```javascript
function ensureContrast(element) {
  const computed = window.getComputedStyle(element);
  const color = computed.color;
  // rgb(r, g, b) 形式をパース
  const match = color.match(/(\d+),\s*(\d+),\s*(\d+)/);
  if (match) {
    const [r, g, b] = [match[1], match[2], match[3]].map(Number);
    // 相対輝度の簡易計算
    const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
    if (luminance > 0.5) {
      element.style.color = '#333';
    }
  }
}
```

## 重要な注意事項

### streaming_service に含めないサービス

以下のタイプのサービスは `streaming_service` に含めないでください：

- **個別課金サービス**（1話ごとに料金が発生するもの）
- **都度課金サイト**（視聴ごとに支払いが必要なもの）
- **レンタル配信**（一定期間のみ視聴可能なレンタル形式のもの）
- **購入専用サービス**（買い切り型のみのサービス）

`streaming_service` には**定額見放題, 月額見放題サービス**のみを含めてください。

### 複数シーズンがあるアニメの取り扱い

複数のシーズンがあるアニメの場合、シーズンごとに配信サイトが異なることがあります。

**必ず以下を確認してください:**

1. 探しているアニメが何シーズン目なのかを確認
2. 公式サイトでそのシーズンの配信情報ページを特定
3. 該当シーズンの配信情報を確実に取得

例えば、「〇〇 2期」を調べる場合は、1期の配信情報ではなく、2期の配信情報ページを確認してください。

### ステップ3: ブラウザクリーンアップ

すべての作業（探索・スクリーンショット撮影・レポート出力）が完了した後、**必ず** `playwright-cli -s={SESSION_NAME} close` を呼び出してブラウザインスタンスを終了する。

**ルール:**

- レポート出力まで完了したことを確認してから `close` を実行する
- 正常終了・エラー終了を問わず、必ずクリーンアップを行う
- `close` を呼び忘れるとブラウザプロセスが残存しメモリを消費し続けるため、スキルの最終ステップとして必須とする

## 配信サービスキーワード一覧

公式サイトを検索する際、以下のキーワードを探してください：

- Netflix, Amazon Prime Video, Hulu, Disney+
- dアニメストア, U-NEXT, ABEMAプレミアム
- FOD, Lemino, DMM TV, アニメ放題
- バンダイチャンネル, TELASA, WOWOWオンデマンド

## 必要なツール

- **Playwright CLI** - ウェブサイト探索のブラウザ自動化（`playwright-cli` コマンド）
- **画像解析** - スクリーンショットベースの配信情報検出

## 参考リソース

### リファレンスファイル

- **`references/streaming-services.md`** - 配信サービス名とキーワードの包括的リスト
