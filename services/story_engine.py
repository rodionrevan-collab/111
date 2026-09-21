from __future__ import annotations

import json
import re
from typing import Any

import httpx

from config import settings
from models import Scene, Story, StoryRequest


SYSTEM_PROMPT = """You are the story engine of an automated vertical-video studio.
Create original short-form stories for TikTok and YouTube Shorts.
Return ONLY valid JSON.
The story must be original, understandable without external context,
and structured into visually distinct scenes.
Do not copy known scripts, creators, or copyrighted stories.
"""


def _fallback_story(req: StoryRequest) -> Story:
    title = f"The {req.topic.title()} Mystery"
    hook = "Nobody expected what happened when this story began."
    scene_count = max(4, min(8, round(req.target_seconds / 8)))
    per_scene = req.target_seconds / scene_count
    scenes: list[Scene] = []

    for i in range(scene_count):
        n = i + 1
        text = (
            f"Scene {n}: something unexpected happens around {req.topic}. "
            "The main character notices a clue and decides not to ignore it."
        )
        scenes.append(
            Scene(
                scene_id=f"scene_{n}",
                duration_seconds=round(per_scene, 2),
                narration=text,
                visual_prompt=(
                    f"cinematic vertical scene, {req.topic}, mysterious atmosphere, "
                    f"high visual clarity, scene {n}, original characters, no text"
                ),
                subtitle=text,
            )
        )

    narration = " ".join(scene.narration for scene in scenes)
    return Story(
        title=title,
        hook=hook,
        narration=narration,
        scenes=scenes,
        language=req.language,
        target_seconds=req.target_seconds,
    )


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    fence = chr(96) * 3
    if text.startswith(fence):
        text = re.sub(r"^" + fence + r"(?:json)?\s*", "", text)
        text = re.sub(r"\s*" + fence + r"$", "", text)
    return json.loads(text)


async def generate_story(req: StoryRequest) -> Story:
    if not settings.llm_api_key:
        return _fallback_story(req)

    user_prompt = {
        "task": "Create a short original story for a vertical social video.",
        "topic": req.topic,
        "language": req.language,
        "target_seconds": req.target_seconds,
        "tone": req.tone,
        "audience": req.audience,
        "required_json": {
            "title": "string",
            "hook": "string",
            "narration": "string",
            "scenes": [
                {
                    "scene_id": "string",
                    "duration_seconds": "number",
                    "narration": "string",
                    "visual_prompt": "string",
                    "subtitle": "string",
                }
            ],
        },
    }

    url = f"{settings.llm_base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.llm_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.llm_model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(user_prompt, ensure_ascii=False)},
        ],
        "temperature": 0.9,
        "response_format": {"type": "json_object"},
    }

    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

    content = data["choices"][0]["message"]["content"]
    obj = _extract_json(content)
    return Story.model_validate(
        {
            **obj,
            "language": req.language,
            "target_seconds": req.target_seconds,
        }
    )
