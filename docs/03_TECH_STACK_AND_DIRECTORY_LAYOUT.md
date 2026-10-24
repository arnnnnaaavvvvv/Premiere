# 03. Tech Stack & Human-Readable Directory Layout

## 1. Technology Stack with One-Line Justifications

| Layer | Technology | Version | One-Line Justification |
| :--- | :--- | :--- | :--- |
| **Frontend Web** | Next.js (App Router, TypeScript) | 14.2+ | Server-side rendering for landing pages, API proxying, and official client support for `@remotion/player`. |
| **UI Design System** | Tailwind CSS + Radix UI Primitives | 3.4+ / 1.x | Rapid authoring of unstyled accessible components styled with custom dark-mode Apple-aesthetic tokens. |
| **API Backend** | FastAPI (Python, Uvicorn/Gunicorn) | 0.111+ | High-throughput asynchronous I/O, automatic OpenAPI docs generation, and native integration with Pydantic v2 schemas. |
| **Task Queue & PubSub** | Redis + Celery / ARQ | Redis 7.2+ | Battle-tested in-memory queue broker for priority task routing, delayed retries, and high-frequency SSE event broadcasting. |
| **Browser Cinematography** | Playwright (Python / Node.js) | 1.44+ | Industry-leading headless automation with native Chrome DevTools Protocol (CDP) support for 60fps frame/video capture. |
| **Video Synthesis & Motion** | Remotion (React 18, TypeScript) | 4.0+ | Frame-accurate, code-driven React animation engine that converts web DOM components directly into MP4 video frames. |
| **Relational Database** | PostgreSQL | 16.x | Robust ACID persistence for jobs, asset metadata, and scene plans with native JSONB indexing. |
| **Object Storage** | Cloudflare R2 / AWS S3 | S3 API | High-durability storage with zero egress fees (Cloudflare R2) for high-bandwidth raw WebM captures and final MP4 assets. |
| **LLM Reasoning & Scripting** | Claude 3.5 Sonnet / OpenAI GPT-4o | Current API | Unmatched instruction-following precision and strict structured JSON schema generation for repository extraction and directing. |
| **Audio Analysis & Quantization** | Librosa + FFmpeg | 0.10+ / 6.1+ | Accurate algorithmic onset detection, musical tempo tracking, and automated broadcast-compliant EBU R128 audio ducking. |
| **Container & Sandboxing** | Docker + gVisor / nsjail | Current | Complete network and process isolation for headless browser runs preventing untrusted code execution. |
| **Observability & Tracing** | OpenTelemetry + Prometheus + Sentry | Current | Distributed end-to-end tracing across async pipeline stages, error tracking, and queue latency metrics. |

---

## 2. Monorepo Directory Layout

The codebase follows a strict modular structure. Each file is single-purpose, capped at **~150 lines of code**, and avoids leaky or overly clever abstractions. A junior engineer can inspect any module and understand its contract in under 10 minutes.

```
reelforge/
├── apps/
│   ├── web/                              # Next.js 14 frontend application
│   │   ├── app/
│   │   │   ├── layout.tsx                # Root layout, Google Fonts (Bebas Neue, Inter) provider
│   │   │   ├── page.tsx                  # Marketing landing page & launch submission form
│   │   │   ├── jobs/
│   │   │   │   └── [id]/
│   │   │   │       ├── page.tsx          # Real-time job status, pipeline progress stepper
│   │   │   │       └── preview/
│   │   │   │           └── page.tsx      # In-browser Remotion player preview & MP4 download
│   │   │   └── api/
│   │   │       └── auth/                 # NextAuth session handlers for optional GitHub sign-in
│   │   ├── components/
│   │   │   ├── ui/                       # Atomic Radix UI base components (Button, Input, Slider)
│   │   │   ├── forms/
│   │   │   │   └── UrlSubmitForm.tsx     # Validated URL intake form with mood selector
│   │   │   ├── progress/
│   │   │   │   ├── PipelineStepper.tsx   # Visual status tracker (Analyzing -> Capturing -> Rendering)
│   │   │   │   └── TerminalLogFeed.tsx   # Live stream of pipeline logs for developer transparency
│   │   │   └── preview/
│   │   │       ├── VideoPlayer.tsx       # Remotion Player wrapper with playback controls
│   │   │       └── DownloadCard.tsx      # Video summary, resolution badges, and signed download trigger
│   │   ├── hooks/
│   │   │   ├── useJobStream.ts           # Server-Sent Events (SSE) hook with auto-reconnect
│   │   │   └── useFormValidation.ts      # Client-side regex URL validation and sanitization
│   │   └── lib/
│   │       ├── api-client.ts             # Typed Fetch wrapper for FastAPI backend endpoints
│   │       └── constants.ts              # UI theme tokens, default mood presets, and limits
│   │
│   ├── api/                              # FastAPI backend gateway
│   │   ├── main.py                       # FastAPI application initialization and CORS setup
│   │   ├── config.py                     # Environment variables, Redis/Postgres connection configs
│   │   ├── routes/
│   │   │   ├── jobs.py                   # POST /jobs, GET /jobs/{id}, job cancellation
│   │   │   ├── events.py                 # GET /jobs/{id}/events (SSE broadcast channel)
│   │   │   ├── preview.py                # GET /jobs/{id}/preview (returns Remotion props payload)
│   │   │   └── music.py                  # GET /music/tracks (catalog of mood-tagged tracks)
│   │   ├── middleware/
│   │   │   ├── rate_limit.py             # Redis sliding-window IP rate limiter
│   │   │   └── ssrf_guard.py             # Pre-flight DNS resolver blocking RFC 1918/loopback ranges
│   │   ├── services/
│   │   │   ├── job_service.py            # Job CRUD operations and state machine transitions
│   │   │   ├── queue_publisher.py        # Redis task enqueuer with priority channel selection
│   │   │   └── storage_service.py        # S3/R2 presigned URL generator for downloads
│   │   └── schemas/
│   │       ├── requests.py               # Pydantic models for incoming user payloads
│   │       ├── responses.py              # Pydantic models for API responses and errors
│   │       └── events.py                 # SSE event payload schemas
│   │
│   └── workers/                          # Distributed async pipeline workers
│       ├── analyzer/
│       │   ├── worker.py                 # Worker entrypoint consuming repo_analysis tasks
│       │   ├── repo_fetcher.py           # GitHub API client fetching README, package.json, routes
│       │   ├── dom_inspector.py          # Playwright lightweight scraper for page title, og:meta
│       │   ├── brief_generator.py        # LLM prompt constructing ProductBriefJSON
│       │   └── director.py               # LLM prompt planning scenes into ScenePlanJSON
│       │
│       ├── capture/
│       │   ├── worker.py                 # Worker entrypoint consuming browser_capture tasks
│       │   ├── browser_pool.py           # Playwright Chromium lifecycle manager with resource limits
│       │   ├── banner_cleaner.py         # DOM mutation scrubber for cookie modals and chat widgets
│       │   ├── cursor_simulator.py       # Human-like Bezier mouse movement and click animator
│       │   ├── actions_runner.py         # Sequencer for scrolling, clicking, and waiting
│       │   └── video_recorder.py         # CDP screencast recorder capturing 60fps WebM/PNG frames
│       │
│       ├── audio/
│       │   ├── worker.py                 # Worker entrypoint consuming audio_processing tasks
│       │   ├── beat_detector.py          # Librosa onset analyzer returning millisecond beat timestamps
│       │   ├── quantizer.py              # Snaps scene frame durations to nearest musical downbeats
│       │   ├── tts_synthesizer.py        # ElevenLabs / TTS client for scene narration voiceovers
│       │   └── sound_master.py           # FFmpeg audio ducking, gain normalization, and fade-in/out
│       │
│       └── render/
│           ├── worker.py                 # Worker entrypoint consuming video_render tasks
│           ├── remotion_bundler.py       # Pre-bundles Webpack/Vite Remotion assets
│           ├── local_renderer.py         # Self-hosted Chromium render executor for development
│           └── lambda_dispatcher.py      # AWS Lambda distributed renderer for 20-second production exports
│
├── packages/
│   ├── remotion/                         # Remotion video motion design system
│   │   ├── src/
│   │   │   ├── index.ts                  # Remotion root registering compositions
│   │   │   ├── Root.tsx                  # ReelForgeComposition definition with dynamic schema
│   │   │   ├── compositions/
│   │   │   │   └── LaunchVideo.tsx       # Main orchestrator sequencing scenes and transitions
│   │   │   ├── scenes/
│   │   │   │   ├── TitleReveal.tsx       # Bold typography punch-in with radiant backdrop
│   │   │   │   ├── DeviceShowcase.tsx    # 3D floating laptop/mobile with internal screencast
│   │   │   │   ├── FeatureZoom.tsx       # Macro callout highlighting specific UI component
│   │   │   │   ├── StatCounter.tsx       # Kinetic metric counter with glowing numbers
│   │   │   │   ├── KineticText.tsx       # Rapid Nike-style staccato typography cuts
│   │   │   │   └── Outro.tsx             # Brand badge, repo URL, and GitHub star CTA
│   │   │   ├── transitions/
│   │   │   │   ├── PushTransition.tsx    # Directional slide transition with motion blur
│   │   │   │   ├── ZoomThrough.tsx       # Seamless zoom-into-element transition
│   │   │   │   ├── MaskWipe.tsx          # High-contrast geometric diagonal wipe
│   │   │   │   ├── BlurDissolve.tsx      # Smooth Gaussian blur cross-fade
│   │   │   │   ├── GlitchFlash.tsx       # 2-frame chromatic aberration and strobe flash
│   │   │   │   └── SharedMorph.tsx       # Element scale/reposition interpolation
│   │   │   ├── components/
│   │   │   │   ├── LaptopFrame.tsx       # 3D MacBook Pro floating chassis with dual shadows
│   │   │   │   ├── MobileFrame.tsx       # 3D iPhone 15 Pro titanium chassis
│   │   │   │   ├── GlowBackdrop.tsx      # Atmospheric deep radial gradient background
│   │   │   │   └── AnimatedCursor.tsx    # Floating arrow cursor with click ripple
│   │   │   └── styles/
│   │   │       ├── fonts.ts              # Bebas Neue and Inter web font loader configurations
│   │   │       └── colors.ts             # Apple MNC dark-mode color palette definitions
│   │   ├── package.json
│   │   └── remotion.config.ts            # Remotion rendering configuration (codec, concurrency)
│   │
│   ├── database/                         # Relational database migrations and ORM
│   │   ├── schema.prisma                 # Prisma ORM schema (Jobs, Projects, Renders, Assets)
│   │   ├── migrations/                   # Sequential SQL migrations
│   │   └── client.ts                     # Initialized singleton database client
│   │
│   └── shared/                           # Shared TypeScript/Python definitions
│       ├── types/                        # TypeScript type definitions matching schemas
│       │   ├── product-brief.ts
│       │   ├── scene-plan.ts
│       │   ├── capture-manifest.ts
│       │   └── remotion-props.ts
│       └── constants/
│           ├── error-codes.ts            # Canonical error codes (SSRF_BLOCKED, SITE_UNREACHABLE)
│           └── moods.ts                  # Audio tracks metadata, BPMs, and styling rules
│
├── schemas/                              # Formal JSON Schema specifications (source of truth)
│   ├── product-brief.schema.json
│   ├── scene-plan.schema.json
│   ├── capture-manifest.schema.json
│   └── remotion-props.schema.json
│
├── docker/
│   ├── Dockerfile.web                    # Next.js standalone container
│   ├── Dockerfile.api                    # FastAPI container
│   ├── Dockerfile.worker-playwright      # Playwright + Chromium sandboxed container
│   └── Dockerfile.worker-remotion        # Remotion rendering container with GPU acceleration
│
├── docker-compose.yml                    # Local developer environment orchestration
├── package.json                          # Monorepo root workspace configuration
└── README.md                             # Architectural blueprint and setup guide
```
