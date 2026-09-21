from __future__ import annotations

from dataclasses import dataclass

from models import AdConfig, StoryRequest
from services.publisher import TikTokPublisher, YouTubePublisher
from services.story_video import StoryVideoBuilder
from services.youtube_trend import YouTubeTrendProvider


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
        use_trends: bool = False,
    ) -> AutoPilotResult:
        effective_request = story_request

        if use_trends and not story_request.topic.strip():
            provider = YouTubeTrendProvider()
            trends = await provider.most_popular(max_results=10)
            if not trends:
                raise RuntimeError("Trend radar returned no topics")
            effective_request = story_request.model_copy(
                update={"topic": trends[0].topic}
            )

        if not effective_request.topic.strip():
            raise ValueError("Topic is empty. Provide a topic or enable use_trends.")

        video = await self.video_builder.build(
            effective_request,
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
            video={**video, "topic": effective_request.topic},
            publications=publications,
        )
