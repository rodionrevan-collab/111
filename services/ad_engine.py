from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from models import AdConfig

def create_corner_banner(ad: AdConfig, output_path: str, width: int = 520, height: int = 150) -> str:
    if not ad.sponsor_name:
        raise ValueError("sponsor_name is required for a corner banner")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((8, 8, width - 8, height - 8), radius=24, fill=(20, 20, 20, 225))
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 42)
        small = ImageFont.truetype("DejaVuSans.ttf", 28)
    except OSError:
        font = ImageFont.load_default()
        small = ImageFont.load_default()
    draw.text((28, 22), ad.sponsor_name[:24], fill=(255, 255, 255, 255), font=font)
    if ad.sponsor_text:
        draw.text((28, 82), ad.sponsor_text[:42], fill=(220, 220, 220, 255), font=small)
    image.save(output_path)
    return output_path
