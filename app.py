from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from config import settings
from models import AdConfig, RenderRequest, StoryRequest
from services.ad_engine import create_corner_banner
from services.queue import JobQueue
from services.story_engine import generate_story
from services.video_renderer import VideoRenderer

app = FastAPI(title=settings.app_name, version="0.1.0")

static_dir = Path("static")
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

queue = JobQueue(settings.jobs_db)
renderer = VideoRenderer()


@app.get("/")
async def dashboard():
    return FileResponse(static_dir / "index.html")


@app.get("/api/health")
async def health():
    return {"ok": True, "app": settings.app_name, "version": "0.1.0"}


@app.get("/api/jobs")
async def jobs():
    return queue.list()


@app.post("/api/generate/story")
async def story(req: StoryRequest):
    result = await generate_story(req)
    return result.model_dump()


@app.post("/api/ad/banner")
async def make_banner(ad: AdConfig):
    if ad.mode != "corner_banner":
        raise HTTPException(400, "mode must be corner_banner")
    path = settings.data_dir / "ads" / "generated_banner.png"
    create_corner_banner(ad, str(path))
    return {"path": str(path)}


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
