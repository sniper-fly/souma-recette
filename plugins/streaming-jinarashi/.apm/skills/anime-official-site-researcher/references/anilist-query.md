# AniList GraphQL Query Reference

## Endpoint

```
POST https://graphql.anilist.co
Content-Type: application/json
```

## Query for Seasonal Anime (with Pagination)

```graphql
query ($season: MediaSeason, $seasonYear: Int, $page: Int) {
  Page(page: $page, perPage: 50) {
    pageInfo {
      total
      currentPage
      lastPage
      hasNextPage
      perPage
    }
    media(season: $season, seasonYear: $seasonYear, type: ANIME, format: TV) {
      id
      title {
        romaji
        native
        english
      }
      externalLinks {
        id
        url
        site
        type
      }
    }
  }
}
```

## Variables

```json
{
  "season": "SPRING",
  "seasonYear": 2026,
  "page": 1
}
```

## Pagination

全作品を取得するには、以下の手順でページネーションを行う:

1. `page: 1` でクエリを実行
2. レスポンスの `pageInfo.hasNextPage` を確認
3. `true` の場合、`page` をインクリメントして再度クエリ
4. `false` になるまで繰り返す

**pageInfo フィールド:**

| Field       | Description                    |
| ----------- | ------------------------------ |
| total       | 全作品数                       |
| currentPage | 現在のページ番号               |
| lastPage    | 最終ページ番号                 |
| hasNextPage | 次のページが存在するか (bool)  |
| perPage     | 1ページあたりの件数            |

## Season Values

| Season         | Value  |
| -------------- | ------ |
| Winter (1-3月) | WINTER |
| Spring (4-6月) | SPRING |
| Summer (7-9月) | SUMMER |
| Fall (10-12月) | FALL   |

## Response Structure

```json
{
  "data": {
    "Page": {
      "pageInfo": {
        "total": 49,
        "currentPage": 1,
        "lastPage": 1,
        "hasNextPage": false,
        "perPage": 50
      },
      "media": [
        {
          "id": 12345,
          "title": {
            "romaji": "Anime Title Romaji",
            "native": "アニメタイトル",
            "english": "Anime Title English"
          },
          "externalLinks": [
            {
              "id": 67890,
              "url": "https://example-anime.com/",
              "site": "Official Site",
              "type": "INFO"
            }
          ]
        }
      ]
    }
  }
}
```

## Extracting Official Site URL

To find the official website, filter `externalLinks` where:

- `site` contains "Official" or is the primary website
- `type` is "INFO" or similar

**Example filtering logic:**

```javascript
const officialSite = media.externalLinks.find(
  (link) =>
    link.site.toLowerCase().includes("official") || link.type === "INFO",
);
```

## cURL Example

```bash
# ページ1を取得
curl -s -X POST https://graphql.anilist.co \
  -H "Content-Type: application/json" \
  -d '{"query": "query ($season: MediaSeason, $seasonYear: Int, $page: Int) { Page(page: $page, perPage: 50) { pageInfo { total currentPage lastPage hasNextPage perPage } media(season: $season, seasonYear: $seasonYear, type: ANIME, format: TV) { id title { romaji native english } externalLinks { id url site type } } } }", "variables": {"season": "WINTER", "seasonYear": 2026, "page": 1}}' | jq '.'

# hasNextPage が true の場合、page を 2, 3, ... とインクリメントして繰り返す
```
