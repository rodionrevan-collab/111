from __future__ import annotations

from pathlib import Path

import httpx

from config import settings


class TTSProvider:
    def __init__(self):
        if not settings.audio_api_key:
            raise RuntimeError("AUDIO_API_KEY or LLM_API_KEY is not configured")

    async def synthesize(
        self,
        text: str,
        output_path: str,
        *,
        voice: str | None = None,
        speed: float | None = None,
    ) -> str:
        if not text.strip():
            raise ValueError("TTS input text is empty")
        if len(text) > 4096:
            raise ValueError("TTS input exceeds the API 4096-character limit")

        payload = {
            "model": settings.tts_model,
            "voice": voice or settings.tts_voice,
            "input": text,
            "response_format": "mp3",
            "speed": speed if speed is not None else settings.tts_speed,
        }
        headers = {
            "Authorization": f"Bearer {settings.audio_api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=180) as client:
            response = await client.post(
                f"{settings.audio_base_url}/audio/speech",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_bytes(response.content)
        return output_path
