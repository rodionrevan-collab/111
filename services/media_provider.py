from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GeneratedMedia:
    kind: str
    path: str
    prompt: str
    duration_seconds: float


class MediaProvider:
    async def generate(self, prompt: str, duration_seconds: float) -> GeneratedMedia:
        raise NotImplementedError


class ExternalMediaProvider(MediaProvider):
    """Adapter point for image/video generation services."""

    async def generate(self, prompt: str, duration_seconds: float) -> GeneratedMedia:
        raise NotImplementedError(
            "No media provider is configured yet. Add a provider adapter under services."
        )
