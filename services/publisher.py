from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import httpx

from config import settings


@dataclass
class PublishResult:
    platform: str
    status: str
    remote_id: str | None = None
    message: str = ""


class Publisher:
    platform = "unknown"

    async def publish(
        self,
        video_path: str,
        title: str,
        description: str = "",
        *,
        ai_generated: bool = True,
        paid_promotion: bool = False,
    ) -> PublishResult:
        raise NotImplementedError


class YouTubePublisher(Publisher):
    platform = "youtube"

    async def publish(
        self,
        video_path: str,
        title: str,
        description: str = "",
        *,
        ai_generated: bool = True,
        paid_promotion: bool = False,
    ) -> PublishResult:
        if not settings.youtube_access_token:
            return PublishResult(
                platform=self.platform,
                status="not_configured",
                message="Set YOUTUBE_ACCESS_TOKEN after completing YouTube OAuth.",
            )

        path = Path(video_path)
        if not path.exists():
            return PublishResult(
                platform=self.platform,
                status="failed",
                message=f"Video not found: {path}",
            )

        size = path.stat().st_size
        metadata = {
            "snippet": {
                "title": title[:100],
                "description": description,
                "categoryId": settings.youtube_category_id,
            },
            "status": {
                "privacyStatus": settings.youtube_privacy_status,
                "containsSyntheticMedia": bool(ai_generated),
            },
        }
        if paid_promotion:
            metadata["paidProductPlacementDetails"] = {
                "hasPaidProductPlacement": True,
            }

        parts = "snippet,status"
        if paid_promotion:
            parts += ",paidProductPlacementDetails"

        headers = {
            "Authorization": f"Bearer {settings.youtube_access_token}",
            "Content-Type": "application/json; charset=UTF-8",
            "X-Upload-Content-Type": "video/mp4",
            "X-Upload-Content-Length": str(size),
        }

        async with httpx.AsyncClient(timeout=180) as client:
            response = await client.post(
                "https://www.googleapis.com/upload/youtube/v3/videos",
                params={"uploadType": "resumable", "part": parts},
                headers=headers,
                json=metadata,
            )
            response.raise_for_status()
            upload_url = response.headers.get("location")
            if not upload_url:
                raise RuntimeError("YouTube did not return a resumable upload URL")

            video_bytes = path.read_bytes()
            upload_response = await client.put(
                upload_url,
                headers={
                    "Authorization": f"Bearer {settings.youtube_access_token}",
                    "Content-Type": "video/mp4",
                    "Content-Length": str(size),
                },
                content=video_bytes,
                timeout=600,
            )
            upload_response.raise_for_status()
            data = upload_response.json()

        return PublishResult(
            platform=self.platform,
            status="published",
            remote_id=data.get("id"),
            message="Uploaded with YouTube Data API.",
        )


class TikTokPublisher(Publisher):
    platform = "tiktok"

    async def publish(
        self,
        video_path: str,
        title: str,
        description: str = "",
        *,
        ai_generated: bool = True,
        paid_promotion: bool = False,
    ) -> PublishResult:
        if not settings.tiktok_access_token:
            return PublishResult(
                platform=self.platform,
                status="not_configured",
                message="Set TIKTOK_ACCESS_TOKEN after completing TikTok OAuth.",
            )

        path = Path(video_path)
        if not path.exists():
            return PublishResult(
                platform=self.platform,
                status="failed",
                message=f"Video not found: {path}",
            )

        file_size = path.stat().st_size
        chunk_size = max(1_000_000, settings.tiktok_chunk_size)
        total_chunks = math.ceil(file_size / chunk_size)

        headers = {
            "Authorization": f"Bearer {settings.tiktok_access_token}",
            "Content-Type": "application/json; charset=UTF-8",
        }

        async with httpx.AsyncClient(timeout=180) as client:
            creator_response = await client.post(
                "https://open.tiktokapis.com/v2/post/publish/creator_info/query/",
                headers=headers,
            )
            creator_response.raise_for_status()
            creator_data = creator_response.json().get("data", {})
            privacy_options = creator_data.get("privacy_level_options", [])

            privacy = settings.tiktok_privacy_level
            if privacy_options and privacy not in privacy_options:
                privacy = "SELF_ONLY" if "SELF_ONLY" in privacy_options else privacy_options[0]

            payload = {
                "post_info": {
                    "title": title[:2200],
                    "privacy_level": privacy,
                    "disable_duet": False,
                    "disable_comment": False,
                    "disable_stitch": False,
                    "brand_content_toggle": bool(paid_promotion),
                    "brand_organic_toggle": False,
                    "is_aigc": bool(ai_generated),
                },
                "source_info": {
                    "source": "FILE_UPLOAD",
                    "video_size": file_size,
                    "chunk_size": chunk_size,
                    "total_chunk_count": total_chunks,
                },
            }

            init_response = await client.post(
                "https://open.tiktokapis.com/v2/post/publish/video/init/",
                headers=headers,
                json=payload,
            )
            init_response.raise_for_status()
            init_data = init_response.json()
            error = init_data.get("error", {})
            if error.get("code") not in (None, "", "ok"):
                raise RuntimeError(error.get("message", "TikTok initialization failed"))

            data = init_data.get("data", {})
            publish_id = data.get("publish_id")
            upload_url = data.get("upload_url")
            if not publish_id or not upload_url:
                raise RuntimeError("TikTok did not return publish_id/upload_url")

            with path.open("rb") as video:
                for index in range(total_chunks):
                    start = index * chunk_size
                    chunk = video.read(chunk_size)
                    if not chunk:
                        break
                    end = start + len(chunk) - 1
                    upload_response = await client.put(
                        upload_url,
                        headers={
                            "Content-Type": "video/mp4",
                            "Content-Length": str(len(chunk)),
                            "Content-Range": f"bytes {start}-{end}/{file_size}",
                        },
                        content=chunk,
                        timeout=600,
                    )
                    upload_response.raise_for_status()

        return PublishResult(
            platform=self.platform,
            status="submitted",
            remote_id=publish_id,
            message="Submitted through TikTok Content Posting API.",
        )
