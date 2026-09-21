# AI Story Factory

Universal automation platform for generating original AI story videos and preparing/publishing them to YouTube Shorts and TikTok.

## MVP

- AI story/script engine with OpenAI-compatible LLM support
- Scene manifest generation
- FFmpeg video rendering
- Advertisement engine:
  - corner_banner: small sponsor banner in a video corner
  - in_stream: short sponsor clip inserted into the story
- SQLite job queue
- Provider interfaces for media generation and social publishing
- Simple dashboard
- Docker setup

## Quick start

1. Install Python 3.12+ and FFmpeg, or use Docker.
2. Copy .env.example to .env.
3. Run:

~~~text
pip install -r requirements.txt
uvicorn app:app --reload
~~~

Open http://127.0.0.1:8000

## AI

Set LLM_BASE_URL, LLM_API_KEY and LLM_MODEL for real story generation. The story engine uses an OpenAI-compatible Chat Completions endpoint so the provider can be swapped later.

## Advertising

The project has two first-class ad modes:

1. corner_banner — small sponsor banner over the video.
2. in_stream — short sponsor video inserted at a selected timestamp.

The ad engine is isolated from platform publishers so platform-specific rules can be applied before publication.

## Structure

~~~text
app.py
config.py
models.py
services/
  story_engine.py
  ad_engine.py
  video_renderer.py
  queue.py
  trend_engine.py
  media_provider.py
  publisher.py
static/
  index.html
data/
.env.example
requirements.txt
Dockerfile
docker-compose.yml
~~~

## Roadmap

- Trend collection from public signals and official APIs
- AI image/video generation providers
- TTS/voice providers
- Automatic scene generation and motion
- YouTube OAuth + upload/scheduling
- TikTok OAuth + Content Posting API
- Analytics feedback loop
- Content diversity/originality checks
- Sponsor campaign manager
- A/B variants
