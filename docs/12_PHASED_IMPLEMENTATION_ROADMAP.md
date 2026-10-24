# 12. Phased Implementation Roadmap & Acceptance Criteria

## 1. Phased Delivery Overview

```
+------------------------------------+------------------------------------+------------------------------------+
|  PHASE 1: Core Pipeline & MVP      |  PHASE 2: Hardening & Narration    |  PHASE 3: Studio Polish & Scale    |
|  (Weeks 1 - 4)                     |  (Weeks 5 - 8)                     |  (Weeks 9 - 14)                    |
+------------------------------------+------------------------------------+------------------------------------+
| - End-to-end autonomous pipeline   | - ElevenLabs narration & ducking   | - Interactive storyboard editor    |
| - 6 Core Remotion scenes           | - 9:16 vertical & 1:1 square video | - Remotion Lambda auto-dispatch    |
| - Playwright popup cleanup         | - Authenticated site login session | - Multi-lingual audio & subtitles  |
| - Librosa beat quantization        | - GitHub OAuth for private repos   | - Webhook CI/CD triggers           |
| - 1080p60 H.264 MP4 export         | - Redis priority queue partition   | - Team workspaces & analytics      |
+------------------------------------+------------------------------------+------------------------------------+
```

---

## 2. Detailed Phase Breakdown & Acceptance Criteria

### Phase 1: Core Engine & End-to-End MVP (Weeks 1 – 4)
- **Objective**: Establish the core ingestion, analysis, capture, composition, and rendering pipeline for public URLs.
- **Sprint Milestones**:
  - *Sprint 1.1*: FastAPI backend scaffold, PostgreSQL Prisma schema, Redis ARQ worker wiring, SSRF pre-flight DNS validator.
  - *Sprint 1.2*: Analyzer worker parsing GitHub README/package.json; Claude 3.5 Sonnet generating valid `ProductBriefJSON` and `ScenePlanJSON`.
  - *Sprint 1.3*: Headless Playwright capture worker with anti-modal script, synthetic Bezier cursor movement, and 60fps CDP screencast recording.
  - *Sprint 1.4*: Remotion design system implementation with Bebas Neue / Inter typography, 6 core scene templates, and local Chromium rendering.
- **Measurable Acceptance Criteria**:
  1. A user can submit any public live URL and GitHub repo URL and receive a 1080p60 MP4 launch video in under 3 minutes.
  2. All 6 core scene templates render without visual artifacts or clipping.
  3. Video cuts align to within $\pm 1$ frame of musical downbeats.
  4. Playwright successfully suppresses cookie banners on 90%+ of tested public landing pages.
  5. 100% of internal private IP submissions (e.g. `127.0.0.1`, `169.254.169.254`) are rejected with `ERR_SSRF_PROHIBITED`.

---

### Phase 2: Production Hardening, Narration & Formats (Weeks 5 – 8)
- **Objective**: Expand visual formats, introduce AI voiceover with audio ducking, and support auth-gated web applications.
- **Sprint Milestones**:
  - *Sprint 2.1*: ElevenLabs TTS integration with automatic script generation and FFmpeg sidechain audio ducking (-14 LUFS compliance).
  - *Sprint 2.2*: Multi-aspect ratio support (16:9 Landscape, 9:16 Vertical for mobile reels, 1:1 Square for social feeds).
  - *Sprint 2.3*: Playwright automated login flow executing transient credential injection into form fields.
  - *Sprint 2.4*: GitHub OAuth integration allowing users to point to private repositories with scoped read tokens.
- **Measurable Acceptance Criteria**:
  1. Narration voiceover plays with clear speech intelligibility and seamless background music ducking (-14dB attenuation during speech).
  2. Videos render cleanly in 9:16 vertical orientation with responsive mobile device framing.
  3. Auth-gated dashboard pages are successfully captured and rendered without credential leakage.
  4. End-to-end pipeline p95 latency drops below 2.5 minutes.

---

### Phase 3: Interactive Studio, Lambda Rendering & Scale (Weeks 9 – 14)
- **Objective**: Provide user-directed editing capabilities, sub-30-second rendering via Remotion Lambda, and enterprise CI/CD triggers.
- **Sprint Milestones**:
  - *Sprint 3.1*: Web-based storyboard editor: edit headline copy, swap scene order, change music tracks, and preview live via `@remotion/player`.
  - *Sprint 3.2*: Migration of production rendering to `@remotion/lambda` (rendering 1800 frames across 100+ Lambdas in parallel).
  - *Sprint 3.3*: GitHub Action / Webhook trigger ("generate launch video on new GitHub Release tag").
  - *Sprint 3.4*: Multi-language narration synthesis and burned-in subtitle support across 10+ languages.
- **Measurable Acceptance Criteria**:
  1. Remotion Lambda completes 60-second 1080p60 video rendering in under 30 seconds.
  2. Storyboard editor updates preview in `@remotion/player` instantaneously (<200ms).
  3. GitHub Action generates downloadable video artifact directly within GitHub Actions workflow runs.
