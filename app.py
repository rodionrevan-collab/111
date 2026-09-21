from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from config import settings
from models import AdConfig, RenderRequest, StoryRequest
from services.ad_campaigns import AdCampaignManager, Campaign
from services.ad_engine import create_corner_banner
from services.queue import JobQueue
from services.story_engine import generate_story
from services.story_video import StoryVideoBuilder
from services.video_renderer import VideoRenderer

app = FastAPI(title=settings.app_name, version="0.3.0")

static_dir = Path("static")
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

queue = JobQueue(settings.jobs_db)
renderer = VideoRenderer()
campaigns = AdCampaignManager(settings.data_dir / "campaigns.json")
story_video_builder = StoryVideoBuilder()


class CampaignList(BaseModel):
    campaigns: list[Campaign]


class CampaignSelectRequest(BaseModel):
    platform: str = "youtube"
    story_seconds: int = Field(default=45, ge=1, le=600)


class StoryVideoRequest(BaseModel):
    story: StoryRequest
    output_video: str = "data/renders/story.mp4"
    ad: AdConfig = Field(default_factory=AdConfig)


@app.get("/")
async def dashboard():
    return FileResponse(static_dir / "index.html")


@app.get("/api/health")
async def health():
    return {"ok": True, "app": settings.app_name, "version": "0.3.0"}


@app.get("/api/jobs")
async def jobs():
    return queue.list()


@app.post("/api/generate/story")
async def story(req: StoryRequest):
    result = await generate_story(req)
    return result.model_dump()


@app.post("/api/generate/video-story")
async def generate_video_story(req: StoryVideoRequest):
    try:
        result = await story_video_builder.build(
            req.story,
            req.output_video,
            req.ad,
        )
        return result
    except Exception as exc:
        raise HTTPException(500, str(exc)) from exc


@app.post("/api/ad/banner")
async def make_banner(ad: AdConfig):
    if ad.mode != "corner_banner":
        raise HTTPException(400, "mode must be corner_banner")
    path = settings.data_dir / "ads" / "generated_banner.png"
    create_corner_banner(ad, str(path))
    return {"path": str(path)}


@app.get("/api/campaigns")
async def list_campaigns():
    return {"campaigns": [c.__dict__ for c in campaigns.load()]}


@app.post("/api/campaigns")
async def save_campaigns(payload: CampaignList):
    campaigns.save(payload.campaigns)
    return {"saved": len(payload.campaigns)}


@app.post("/api/campaigns/select")
async def select_campaign(req: CampaignSelectRequest):
    campaign = campaigns.choose(req.platform, req.story_seconds)
    if not campaign:
        return {"campaign": None}
    return {
        "campaign": campaign.__dict__,
        "ad_config": campaigns.to_ad_config(campaign).model_dump(),
    }


@app.post("/api/render")
async def render(req: RenderRequest):
    source = Path(req.source_video)
    if not source.exists():
        raise HTTPException(404, f"Source video not found: {source}")

    output = Path(req.output_video)
    output.parent.mkdir(parents=True, exist_ok=True)

    ad = req.ad
    banner = ad.banner_path
    if ad.mode == "corner_banner" and not banner:
        banner = str(settings.data_dir / "ads" / "generated_banner.png")
        create_corner_banner(ad, banner)

    result_path = renderer.apply_ad(
        str(source),
        str(output),
        ad.mode,
        banner=banner,
        ad_clip=ad.ad_video_path,
        insert_at=ad.insert_at_seconds,
    )
    return {"output_video": result_path}


@app.post("/api/jobs/render")
async def queue_render(req: RenderRequest):
    job_id = queue.add("render", req.model_dump())
    return {"job_id": job_id, "status": "queued"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host=settings.host, port=settings.port, reload=True)
