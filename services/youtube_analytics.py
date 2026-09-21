from __future__ import annotations

from datetime import date, timedelta

import httpx

from config import settings


class YouTubeAnalytics:
    base_url = "https://youtubeanalytics.googleapis.com/v2/reports"

    def __init__(self):
        if not settings.youtube_access_token:
            raise RuntimeError("YOUTUBE_ACCESS_TOKEN is not configured")

    async def query(
        self,
        metrics: str,
        *,
        start_date: str | None = None,
        end_date: str | None = None,
        dimensions: str | None = None,
        filters: str | None = None,
        include_revenue: bool = False,
    ) -> dict:
        end = date.today()
        start = end - timedelta(days=28)
        start_date = start_date or start.isoformat()
        end_date = end_date or end.isoformat()

        query_metrics = metrics
        if include_revenue and "estimatedRevenue" not in query_metrics:
            query_metrics += ",estimatedRevenue"

        headers = {
            "Authorization": f"Bearer {settings.youtube_access_token}",
        }
        params = {
            "ids": "channel==MINE",
            "startDate": start_date,
            "endDate": end_date,
            "metrics": query_metrics,
        }
        if dimensions:
            params["dimensions"] = dimensions
        if filters:
            params["filters"] = filters

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.get(
                self.base_url,
                headers=headers,
                params=params,
            )
            response.raise_for_status()
            return response.json()

    async def video_report(
        self,
        video_ids: list[str],
        *,
        start_date: str | None = None,
        end_date: str | None = None,
        include_revenue: bool = False,
    ) -> dict:
        if not video_ids:
            return {"rows": [], "columnHeaders": []}

        ids = ",".join(video_ids[:500])
        return await self.query(
            "views,likes,comments,estimatedMinutesWatched,averageViewDuration,"
            "averageViewPercentage,subscribersGained",
            start_date=start_date,
            end_date=end_date,
            dimensions="video",
            filters=f"video=={ids}",
            include_revenue=include_revenue,
        )
