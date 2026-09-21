from __future__ import annotations

import httpx

from config import settings
from services.trend_engine import TrendSignal


class YouTubeTrendProvider:
    def __init__(self):
        if not settings.youtube_api_key:
            raise RuntimeError("YOUTUBE_API_KEY is not configured")

    async def most_popular(self, max_results: int = 50) -> list[TrendSignal]:
        max_results = max(1, min(max_results, 50))
        params = {
            "part": "snippet,statistics",
            "chart": "mostPopular",
            "regionCode": settings.youtube_region_code,
            "maxResults": max_results,
            "key": settings.youtube_api_key,
        }

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                "https://www.googleapis.com/youtube/v3/videos",
                params=params,
            )
            response.raise_for_status()
            data = response.json()

        signals: list[TrendSignal] = []
        items = data.get("items", [])
        for index, item in enumerate(items):
            snippet = item.get("snippet", {})
            stats = item.get("statistics", {})
            views = int(stats.get("viewCount", 0) or 0)
            likes = int(stats.get("likeCount", 0) or 0)
            comments = int(stats.get("commentCount", 0) or 0)
            engagement = (likes + comments) / max(1, views)
            rank_score = 100.0 - min(index, 49) * 1.5
            score = rank_score + min(20.0, engagement * 1000.0)

            signals.append(
                TrendSignal(
                    topic=snippet.get("title", "unknown"),
                    score=round(score, 3),
                    reason=(
                        f"YouTube mostPopular rank={index + 1}; "
                        f"views={views}; likes={likes}; comments={comments}"
                    ),
                )
            )
        return signals
