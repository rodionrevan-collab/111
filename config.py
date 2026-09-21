from __future__ import annotations
import os
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "AI Story Factory")
    host: str = os.getenv("APP_HOST", "0.0.0.0")
    port: int = int(os.getenv("APP_PORT", "8000"))
    data_dir: Path = Path(os.getenv("DATA_DIR", "./data"))

    llm_base_url: str = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    llm_api_key: str = os.getenv("LLM_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4o-mini")

    video_base_url: str = os.getenv("VIDEO_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    video_api_key: str = os.getenv("VIDEO_API_KEY", "") or os.getenv("LLM_API_KEY", "")
    video_model: str = os.getenv("VIDEO_MODEL", "sora-2")
    video_size: str = os.getenv("VIDEO_SIZE", "720x1280")
    video_seconds: int = int(os.getenv("VIDEO_SECONDS", "8"))

    ffmpeg_bin: str = os.getenv("FFMPEG_BIN", "ffmpeg")

    youtube_api_key: str = os.getenv("YOUTUBE_API_KEY", "")
    youtube_region_code: str = os.getenv("YOUTUBE_REGION_CODE", "US")
    youtube_client_id: str = os.getenv("YOUTUBE_CLIENT_ID", "")
    youtube_client_secret: str = os.getenv("YOUTUBE_CLIENT_SECRET", "")
    youtube_redirect_uri: str = os.getenv("YOUTUBE_REDIRECT_URI", "http://127.0.0.1:8000/api/auth/youtube/callback")
    youtube_access_token: str = os.getenv("YOUTUBE_ACCESS_TOKEN", "")
    youtube_privacy_status: str = os.getenv("YOUTUBE_PRIVACY_STATUS", "private")
    youtube_category_id: str = os.getenv("YOUTUBE_CATEGORY_ID", "22")

    tiktok_client_key: str = os.getenv("TIKTOK_CLIENT_KEY", "")
    tiktok_client_secret: str = os.getenv("TIKTOK_CLIENT_SECRET", "")
    tiktok_redirect_uri: str = os.getenv("TIKTOK_REDIRECT_URI", "http://127.0.0.1:8000/api/auth/tiktok/callback")
    tiktok_access_token: str = os.getenv("TIKTOK_ACCESS_TOKEN", "")
    tiktok_privacy_level: str = os.getenv("TIKTOK_PRIVACY_LEVEL", "SELF_ONLY")
    tiktok_chunk_size: int = int(os.getenv("TIKTOK_CHUNK_SIZE", "10000000"))

    @property
    def jobs_db(self) -> Path:
        return self.data_dir / "jobs.db"

settings = Settings()
settings.data_dir.mkdir(parents=True, exist_ok=True)
