from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from config import settings


class VideoRenderer:
    def __init__(self, ffmpeg_bin: str | None = None):
        self.ffmpeg = ffmpeg_bin or settings.ffmpeg_bin

    def _run(self, args: list[str]) -> None:
        result = subprocess.run(args, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise RuntimeError(result.stderr[-4000:])

    def add_corner_banner(self, source: str, banner: str, output: str) -> str:
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        self._run([
            self.ffmpeg, "-y", "-i", source, "-i", banner,
            "-filter_complex", "[1:v]format=rgba[b];[0:v][b]overlay=W-w-24:H-h-24:format=auto",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-c:a", "aac",
            "-movflags", "+faststart", output,
        ])
        return output

    def insert_ad_clip(self, source: str, ad_clip: str, output: str, at_seconds: float) -> str:
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        work = Path(tempfile.mkdtemp(prefix="story_ad_"))
        try:
            part1, ad_part, part2 = work / "part1.mp4", work / "ad.mp4", work / "part2.mp4"
            concat = work / "concat.txt"
            self._run([
                self.ffmpeg, "-y", "-i", source, "-t", str(max(0.0, at_seconds)),
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", str(part1)
            ])
            self._run([
                self.ffmpeg, "-y", "-i", ad_clip,
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", str(ad_part)
            ])
            self._run([
                self.ffmpeg, "-y", "-ss", str(max(0.0, at_seconds)), "-i", source,
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", str(part2)
            ])
            concat.write_text(
                "file '" + part1.as_posix() + "'\n" +
                "file '" + ad_part.as_posix() + "'\n" +
                "file '" + part2.as_posix() + "'\n", encoding="utf-8"
            )
            self._run([
                self.ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(concat),
                "-c", "copy", "-movflags", "+faststart", output
            ])
            return output
        finally:
            shutil.rmtree(work, ignore_errors=True)

    def apply_ad(self, source: str, output: str, ad_mode: str, banner: str | None = None,
                 ad_clip: str | None = None, insert_at: float | None = None) -> str:
        if ad_mode == "corner_banner":
            if not banner:
                raise ValueError("banner is required for corner_banner mode")
            return self.add_corner_banner(source, banner, output)
        if ad_mode == "in_stream":
            if not ad_clip:
                raise ValueError("ad_video_path is required for in_stream mode")
            return self.insert_ad_clip(source, ad_clip, output, insert_at or 5.0)
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, output)
        return output
