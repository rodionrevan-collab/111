from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PublishResult:
    platform: str
    status: str
    remote_id: str | None = None
    message: str = ""


class Publisher:
    platform = "unknown"

    async def publish(self, video_path: str, title: str, description: str = "") -> PublishResult:
        raise NotImplementedError


class YouTubePublisher(Publisher):
    platform = "youtube"

    async def publish(self, video_path: str, title: str, description: str = "") -> PublishResult:
        return PublishResult(
            platform=self.platform,
            status="not_configured",
            message="YouTube OAuth/upload adapter is reserved for the publishing phase.",
        )


class TikTokPublisher(Publisher):
    platform = "tiktok"

    async def publish(self, video_path: str, title: str, description: str = "") -> PublishResult:
        return PublishResult(
            platform=self.platform,
            status="not_configured",
            message="TikTok OAuth/Content Posting adapter is reserved for the publishing phase.",
        )
