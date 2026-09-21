from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path

from models import AdConfig


@dataclass
class Campaign:
    campaign_id: str
    sponsor_name: str
    mode: str
    weight: float = 1.0
    sponsor_text: str = ""
    asset_path: str | None = None
    platforms: list[str] | None = None
    min_story_seconds: int = 0

    def matches(self, platform: str, story_seconds: int) -> bool:
        if self.platforms and platform not in self.platforms:
            return False
        return story_seconds >= self.min_story_seconds


class AdCampaignManager:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, campaigns: list[Campaign]) -> None:
        self.path.write_text(
            json.dumps([c.__dict__ for c in campaigns], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def load(self) -> list[Campaign]:
        if not self.path.exists():
            return []
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        return [Campaign(**item) for item in raw]

    def choose(self, platform: str, story_seconds: int) -> Campaign | None:
        candidates = [
            c for c in self.load()
            if c.matches(platform, story_seconds)
        ]
        if not candidates:
            return None
        return random.choices(
            candidates,
            weights=[max(0.01, c.weight) for c in candidates],
            k=1,
        )[0]

    def to_ad_config(self, campaign: Campaign, insert_at: float | None = None) -> AdConfig:
        return AdConfig(
            mode=campaign.mode,
            sponsor_name=campaign.sponsor_name,
            sponsor_text=campaign.sponsor_text,
            banner_path=campaign.asset_path if campaign.mode == "corner_banner" else None,
            ad_video_path=campaign.asset_path if campaign.mode == "in_stream" else None,
            insert_at_seconds=insert_at,
        )
