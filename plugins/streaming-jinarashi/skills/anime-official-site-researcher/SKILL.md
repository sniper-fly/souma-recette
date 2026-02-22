---
name: anime-official-site-researcher
description: 「アニメの公式サイトを調べて」「シーズンのアニメ一覧を取得」「AniListからアニメ情報を取得」などのリクエストに対応するスキル
version: 1.1.0
---

# アニメ公式サイト検索スキル

AniList GraphQL APIを使用して、特定シーズンのアニメ情報と公式サイトURLを取得するスキルです。

## 目的

AniList APIから特定シーズンのアニメ情報を取得し、各アニメの公式サイトURLを収集します。

## ワークフロー

### ステップ1: スクリプトを実行してアニメリストを取得

`scripts/fetch_seasonal_anime.py` を実行して、指定シーズンの全アニメ情報を取得します。

**実行方法:**

```bash
python scripts/fetch_seasonal_anime.py <year> <season>
```

**引数:**

- `year`: 年（例: 2026）
- `season`: シーズン（WINTER, SPRING, SUMMER, FALL）

**実行例:**

```bash
python scripts/fetch_seasonal_anime.py 2026 WINTER
```

スクリプトが自動的にAniList APIへのクエリとページネーション処理を行い、結果をJSON形式で標準出力に出力します。

## 出力形式

スクリプトは以下の形式のJSON配列を出力します：

```json
[
  {
    "title": {
      "romaji": "Anime Title Romaji",
      "native": "アニメタイトル"
    },
    "officialSiteUrl": "https://example-anime.com/"
  }
]
```

## 参考リソース

### リファレンスファイル

- **`references/anilist-query.md`** - AniList API用のGraphQLクエリ完全版
- **`scripts/fetch_seasonal_anime.py`** - データ取得スクリプト