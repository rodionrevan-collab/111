from __future__ import annotations

import shutil
import subprocess
import uuid
from pathlib import Path

from config import settings
from models import AdConfig, StoryRequest
from services.ai_video_provider import SoraVideoProvider
from services.story_engine import generate_story
from services.video_renderer import VideoRenderer


class StoryVideoBuilder:
    def __init__(self):
        self.provider = SoraVideoProvider()
        self.renderer = VideoRenderer()

    @staticmethod
    def _clip_seconds(target: float) -> int:
        allowed = (4, 8, 12)
        return min(allowed, key=lambda value: abs(value - target))

    def _concat(self, clips: list[Path], output: Path) -> None:
        output.parent.mkdir(parents=True, exist_ok=True)
        concat_file = output.parent / f"{output.stem}_concat.txt"
        concat_file.write_text(
            "".join(f"file '{clip.as_posix()}'\n" for clip in clips),
            encoding="utf-8",
        )
        try:
            result = subprocess.run(
                [
                    settings.ffmpeg_bin,
                    "-y",
                    "-f",
                    "concat",
                    "-safe",
                    "0",
                    "-i",
                    str(concat_file),
                    "-c",
                    "copy",
                    "-movflags",
                    "+faststart",
                    str(output),
                ],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if result.returncode != 0:
                raise RuntimeError(result.stderr[-4000:])
        finally:
            concat_file.unlink(missing_ok=True)

    async def build(self, request: StoryRequest, output_path: str, ad: AdConfig | None = None) -> dict:
        story = await generate_story(request)
        run_dir = settings.data_dir / "generated" / uuid.uuid4().hex
        run_dir.mkdir(parents=True, exist_ok=True)

        clips: list[Path] = []
        try:
            for scene in story.scenes:
                seconds = self._clip_seconds(scene.duration_seconds)
                clip_path = run_dir / f"{scene.scene_id}.mp4"
                await self.provider.generate_clip(
                    prompt=scene.visual_prompt,
                    output_path=str(clip_path),
                    seconds=seconds,
                    size=settings.video_size,
                )
                clips.append(clip_path)

            base_path = run_dir / "master.mp4"
            self._concat(clips, base_path)

            final_path = Path(output_path)
            final_path.parent.mkdir(parents=True, exist_ok=True)

            if ad and ad.mode != "none":
                banner = ad.banner_path
                if ad.mode == "corner_banner" and not banner:
                    from services.ad_engine import create_corner_banner
                    banner = str(run_dir / "sponsor_banner.png")
                    create_corner_banner(ad, banner)
                self.renderer.apply_ad(
                    str(base_path),
                    str(final_path),
                    ad.mode,
                    banner=banner,
                    ad_clip=ad.ad_video_path,
                    insert_at=ad.insert_at_seconds,
                )
            else:
                shutil.copy2(base_path, final_path)

            return {
                "title": story.title,
                "hook": story.hook,
                "output_video": str(final_path),
                "scene_count": len(clips),
                "estimated_seconds": sum(self._clip_seconds(s.duration_seconds) for s in story.scenes),
                "ad_mode": ad.mode if ad else "none",
            }
        finally:
            shutil.rmtree(run_dir, ignore_errors=True)
