# AI Story Factory

A self-hosted automation platform for creating original AI story videos, adding sponsor ads, and preparing/publishing vertical videos to YouTube Shorts and TikTok.

## What works in the current MVP

- AI story/script generation through an OpenAI-compatible LLM endpoint.
- Scene-by-scene prompts for vertical stories.
- AI video generation through the official video API adapter.
- Automatic narration through the speech API adapter.
- FFmpeg assembly into a vertical MP4.
- Two ad modes:
  - corner_banner: small sponsor banner in a corner.
  - in_stream: short sponsor video inserted into the story.
- Sponsor campaign storage and weighted campaign selection.
- One-click AutoPilot pipeline:
  topic/trend -> story -> AI scenes -> narration -> ad -> publishing.
- YouTube publisher adapter.
- TikTok Content Posting publisher adapter.
- YouTube Trend Radar using the public mostPopular endpoint.
- YouTube Analytics adapter.
- SQLite job queue.
- FastAPI dashboard.
- Docker support.
- CI syntax-check workflow.

## Current platform notes

YouTube and TikTok integrations use official APIs. OAuth/token setup is still a deployment step.

TikTok has platform-specific rules around promotional overlays and public Direct Post access. The local renderer supports both ad modes, but a TikTok-specific sponsored-content variant may need to be used depending on the current platform rules and approved app configuration.

AI-generated-content disclosure is carried through the publishing adapters where supported.

## Quick start

1. Install Python 3.12+ and FFmpeg, or use Docker.
2. Copy .env.example to .env.
3. Add the API keys you plan to use.
4. Run:

~~~text
pip install -r requirements.txt
uvicorn app:app --reload
~~~

Open http://127.0.0.1:8000.

## Main API endpoints

- POST /api/generate/story
- POST /api/generate/video-story
- POST /api/autopilot
- GET /api/trends/youtube
- POST /api/analytics/youtube
- POST /api/publish/youtube
- POST /api/publish/tiktok
- GET /api/campaigns
- POST /api/campaigns
- POST /api/render

## Repository structure

~~~text
app.py
config.py
models.py
services/
  story_engine.py
  ai_video_provider.py
  tts_provider.py
  story_video.py
  ad_engine.py
  ad_campaigns.py
  video_renderer.py
  autopilot.py
  youtube_trend.py
  youtube_analytics.py
  publisher.py
  queue.py
static/
  index.html
data/
.env.example
requirements.txt
Dockerfile
docker-compose.yml
THIRD_PARTY.md
PLATFORM_SETUP.md
~~~

## Third-party sources

The repository documents the open-source components we studied in THIRD_PARTY.md.

We do not embed the AGPL Postiz code into the core. OpenShorts' separately licensed cloud/ directory is also not copied into this project.

## Next development phase

- Secure OAuth flows and token refresh instead of manual access-token environment variables.
- Background workers and scheduled jobs.
- Burned-in subtitles and word timing.
- Platform-specific render variants.
- TikTok-safe sponsored-content workflow.
- More trend sources and trend freshness/velocity scoring.
- Feedback loop that uses analytics to choose future story topics/formats.
- Sponsor dashboard and campaign reporting.
- Content diversity/originality checks before publication.
