from __future__ import annotations

import asyncio
from pathlib import Path

import httpx

from config import settings


ALLOWED_SECONDS = {4, 8, 12}
ALLOWED_SIZES = {"720x1280", "1280x720", "1024x1792", "1792x1024"}


class SoraVideoProvider:
    """OpenAI video-generation adapter.

    The provider creates an asynchronous video job, polls its status, then
    downloads the completed MP4 into the local data directory.
    """

    def __init__(self):
        if not settings.video_api_key:
            raise RuntimeError("VIDEO_API_KEY or LLM_API_KEY must be configured")

    async def generate_clip(
        self,
        prompt: str,
        output_path: str,
        seconds: int | None = None,
        size: str | None = None,
    ) -> str:
        seconds = seconds or settings.video_seconds
        size = size or settings.video_size
        if seconds not in ALLOWED_SECONDS:
            raise ValueError(f"seconds must be one of {sorted(ALLOWED_SECONDS)}")
        if size not in ALLOWED_SIZES:
            raise ValueError(f"size must be one of {sorted(ALLOWED_SIZES)}")

        headers = {"Authorization": f"Bearer {settings.video_api_key}"}
        data = {
            "model": settings.video_model,
            "prompt": prompt,
            "seconds": str(seconds),
            "size": size,
        }

        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{settings.video_base_url}/videos",
                headers=headers,
                data=data,
            )
            response.raise_for_status()
            job = response.json()

            job_id = job["id"]
            while True:
                status_response = await client.get(
                    f"{settings.video_base_url}/videos/{job_id}",
                    headers=headers,
                )
                status_response.raise_for_status()
                status = status_response.json()
                state = status.get("status")

                if state == "completed":
                    break
                if state in {"failed", "cancelled"}:
                    error = status.get("error") or {}
                    raise RuntimeError(
                        f"Video job {job_id} ended with status={state}: "
                        f"{error.get('message', 'unknown error')}"
                    )

                await asyncio.sleep(5)

            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            content_response = await client.get(
                f"{settings.video_base_url}/videos/{job_id}/content",
                headers=headers,
            )
            content_response.raise_for_status()
            Path(output_path).write_bytes(content_response.content)

        return output_path
