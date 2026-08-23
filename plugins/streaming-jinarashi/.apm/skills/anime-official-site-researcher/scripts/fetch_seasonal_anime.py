#!/usr/bin/env python3
"""
AniList APIから特定シーズンのアニメ情報と公式サイトURLを取得するスクリプト

使用方法:
    python fetch_seasonal_anime.py <year> <season>

引数:
    year: 年（例: 2026）
    season: シーズン（WINTER, SPRING, SUMMER, FALL）

出力:
    JSON形式のアニメ情報リスト（標準出力）
"""

import argparse
import json
import sys
import urllib.request
import urllib.error

ANILIST_API_URL = "https://graphql.anilist.co"

GRAPHQL_QUERY = """
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
"""

VALID_SEASONS = {"WINTER", "SPRING", "SUMMER", "FALL"}


def fetch_page(season: str, year: int, page: int) -> dict:
    """AniList APIから指定ページのデータを取得"""
    payload = {
        "query": GRAPHQL_QUERY,
        "variables": {
            "season": season,
            "seasonYear": year,
            "page": page,
        },
    }

    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        ANILIST_API_URL,
        data=data,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (compatible; AnimeResearcher/1.0)",
            "Accept": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(request) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        raise RuntimeError(f"API error: {e.code} - {error_body}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error: {e.reason}") from e


def fetch_all_anime(season: str, year: int) -> list[dict]:
    """全ページのアニメデータを取得"""
    all_media = []
    page = 1

    while True:
        response = fetch_page(season, year, page)
        page_data = response.get("data", {}).get("Page", {})
        media = page_data.get("media", [])
        page_info = page_data.get("pageInfo", {})

        all_media.extend(media)

        if not page_info.get("hasNextPage", False):
            break

        page += 1

    return all_media


def extract_official_site_url(external_links: list[dict]) -> str | None:
    """
    externalLinksから公式サイトURLを抽出

    優先度:
    1. siteに"Official"が含まれるもの
    2. typeが"INFO"のもの
    3. どちらもなければNone
    """
    if not external_links:
        return None

    # 優先度1: siteに"Official"が含まれるもの
    for link in external_links:
        site = link.get("site", "")
        if "official" in site.lower():
            return link.get("url")

    # 優先度2: typeが"INFO"のもの
    for link in external_links:
        if link.get("type") == "INFO":
            return link.get("url")

    return None


def format_anime_data(media_list: list[dict]) -> list[dict]:
    """アニメデータを指定フォーマットに変換"""
    result = []

    for media in media_list:
        title = media.get("title", {})
        external_links = media.get("externalLinks", [])
        official_site_url = extract_official_site_url(external_links)

        result.append(
            {
                "title": {
                    "romaji": title.get("romaji"),
                    "native": title.get("native"),
                },
                "officialSiteUrl": official_site_url,
            }
        )

    return result


def main():
    parser = argparse.ArgumentParser(
        description="AniList APIから特定シーズンのアニメ情報を取得"
    )
    parser.add_argument("year", type=int, help="年（例: 2026）")
    parser.add_argument(
        "season",
        type=str,
        choices=list(VALID_SEASONS),
        help="シーズン（WINTER, SPRING, SUMMER, FALL）",
    )

    args = parser.parse_args()

    try:
        media_list = fetch_all_anime(args.season, args.year)
        formatted_data = format_anime_data(media_list)
        print(json.dumps(formatted_data, ensure_ascii=False, indent=2))
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
