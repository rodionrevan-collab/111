# Third-party project plan

We are building one application, but we will reuse compatible open-source components rather than blindly copying whole applications.

## OpenShorts

Repository: https://github.com/mutonby/openshorts

The main repository code is MIT licensed. The repository explicitly excludes the cloud/ directory from the MIT license and uses a separate commercial license there.

Planned use:
- study/reuse compatible local video-processing ideas
- study queue/worker structure
- study captions and clip-processing components
- do not copy cloud/ code into this project

## ShortGPT

Repository: https://github.com/RayVentura/ShortGPT

License: MIT.

Planned use:
- study script-to-video orchestration
- study TTS/media provider separation
- reuse only the pieces that are actually useful to our architecture

## Postiz

Repository: https://github.com/gitroomhq/postiz-app

License: AGPL-3.0.

Decision: do not embed Postiz source into the core application. We can use it as an architectural reference and keep our own publisher implementation separate.

## Our rule

Each reused component must have:
1. a compatible license;
2. its copyright/license notices preserved where required;
3. a clear boundary in our code;
4. no dependency on private/restricted platform endpoints.
