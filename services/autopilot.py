from __future__ import annotations

from dataclasses import dataclass

from models import AdConfig, StoryRequest
from services.publisher import TikTokPublisher, YouTubePublisher
from services.story_video import StoryVideoBuilder


@dataclass
class AutoPilotResult:
    video: dict
    publications: list[dict]


class AutoPilot:
    def __init__(self):
        self.video_builder = StoryVideoBuilder()
        self.publishers = {
            "youtube": YouTubePublisher(),
            "tiktok": TikTokPublisher(),
        }

    async def run(
        self,
        story_request: StoryRequest,
        output_video: str,
        platforms: list[str],
        ad: AdConfig,
    ) -> AutoPilotResult:
        video = await self.video_builder.build(
            story_request,
            output_video,
            ad,
        )

        publications: list[dict] = []
        paid = ad.mode != "none"

        for platform in platforms:
            publisher = self.publishers.get(platform.lower())
            if not publisher:
                publications.append({
                    "platform": platform,
                    "status": "unsupported",
                    "message": "No publisher adapter is configured for this platform.",
                })
                continue

            result = await publisher.publish(
                video_path=video["output_video"],
                title=video["title"],
                description=video["hook"],
                ai_generated=True,
                paid_promotion=paid,
            )
            publications.append(result.__dict__)

        return AutoPilotResult(
            video=video,
            publications=publications,
        )
