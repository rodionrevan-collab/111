from __future__ import annotations
from datetime import datetime, timezone
from typing import Literal
from pydantic import BaseModel, Field

AdMode = Literal["none", "corner_banner", "in_stream"]

class StoryRequest(BaseModel):
    topic: str
    language: str = "en"
    target_seconds: int = Field(default=45, ge=15, le=180)
    tone: str = "dramatic"
    audience: str = "general"

class Scene(BaseModel):
    scene_id: str
    duration_seconds: float
    narration: str
    visual_prompt: str
    subtitle: str | None = None

class Story(BaseModel):
    title: str
    hook: str
    narration: str
    scenes: list[Scene]
    language: str
    target_seconds: int

class AdConfig(BaseModel):
    mode: AdMode = "none"
    sponsor_name: str = ""
    sponsor_text: str = ""
    banner_path: str | None = None
    ad_video_path: str | None = None
    insert_at_seconds: float | None = Field(default=None, ge=0)

class RenderRequest(BaseModel):
    source_video: str
    output_video: str
    ad: AdConfig = Field(default_factory=AdConfig)

class Job(BaseModel):
    id: int
    kind: str
    status: Literal["queued", "running", "done", "failed"]
    payload: dict
    result: dict = Field(default_factory=dict)
    error: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
