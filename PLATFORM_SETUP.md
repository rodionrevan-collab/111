# Platform integration notes

## YouTube Shorts

Use the official YouTube Data API and OAuth 2.0 for channel publishing.

The video upload operation is videos.insert. Google currently notes that uploads from unverified API projects created after July 28, 2020 are restricted to private viewing until the project completes the required audit.

Official docs:
- https://developers.google.com/youtube/v3/docs/videos/insert
- https://developers.google.com/youtube/v3/guides/uploading_a_video

## TikTok

Use the official TikTok Content Posting API.

Direct Post requires:
- a registered TikTok developer app;
- the Content Posting API product;
- approval for the video.publish scope;
- user authorization.

TikTok currently states that unaudited clients are restricted to private visibility until the client passes the audit.

Official docs:
- https://developers.tiktok.com/docs/en/content-posting-api-get-started
- https://developers.tiktok.com/docs/en/content-posting-api-reference-direct-post

TikTok also states that apps should avoid superimposing unwanted promotional branding, links or promotional text on content shared through the Content Posting API. Therefore the ad engine is platform-aware and must not assume that a baked-in sponsor banner is valid for every TikTok publishing path.

## AI-generated content

The publishing layer will carry an AI-generated-content disclosure decision when required by a platform.

## Design decision

Publishing is a separate service from rendering. This lets us render one master video and create platform-specific variants before upload.
