# 04. Data Models & API Contracts

## 1. Relational Data Model (PostgreSQL / Prisma)

The data model is designed for strict integrity, auditability, and idempotent pipeline retries.

```
 +--------------------+       1:N      +--------------------+       1:1      +--------------------+
 |      projects      | -------------> |        jobs        | -------------> |   product_briefs   |
 +--------------------+                +--------------------+                +--------------------+
           |                                     |                                     |
           |                                     | 1:N                                 | 1:1
           |                                     v                                     v
           |                           +--------------------+                +--------------------+
           |                           |       assets       |                |    scene_plans     |
           |                           +--------------------+                +--------------------+
           |                                     | 1:1
           |                                     v
           |                           +--------------------+
           +-------------------------> |      renders       |
                                       +--------------------+
```

### Prisma Schema (`packages/database/schema.prisma`)

```prisma
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

generator client {
  provider = "prisma-client-js"
}

enum JobStatus {
  PENDING
  VALIDATING
  ANALYZING_REPO
  SCRIPTING_SCENES
  CAPTURING_MEDIA
  PROCESSING_AUDIO
  COMPOSING_VIDEO
  RENDERING_MP4
  COMPLETED
  FAILED
  CANCELLED
}

enum MoodPreset {
  MINIMAL
  ENERGETIC
  FUTURISTIC
}

enum AssetType {
  SCREENSHOT
  FULL_PAGE_SCROLL
  ELEMENT_CLIP
  AUDIO_BACKGROUND
  AUDIO_NARRATION
  REPO_FAVICON
}

model Project {
  id          String   @id @default(uuid()) @db.Uuid
  liveUrl     String   @db.VarChar(1024)
  repoUrl     String   @db.VarChar(1024)
  name        String?  @db.VarChar(255)
  description String?  @db.Text
  createdAt   DateTime @default(now()) @map("created_at")
  updatedAt   DateTime @updatedAt @map("updated_at")
  jobs        Job[]

  @@index([liveUrl])
  @@index([repoUrl])
  @@map("projects")
}

model Job {
  id              String        @id @default(uuid()) @db.Uuid
  projectId       String        @db.Uuid @map("project_id")
  status          JobStatus     @default(PENDING)
  progressPercent Int           @default(0) @map("progress_percent")
  currentStage    String?       @map("current_stage") @db.VarChar(100)
  mood            MoodPreset    @default(ENERGETIC)
  includeVoiceover Boolean      @default(false) @map("include_voiceover")
  authCredentials Json?         @map("auth_credentials") // Never logged, transiently used
  idempotencyKey  String?       @unique @map("idempotency_key") @db.VarChar(128)
  errorCode       String?       @map("error_code") @db.VarChar(64)
  errorMessage    String?       @map("error_message") @db.Text
  retryCount      Int           @default(0) @map("retry_count")
  createdAt       DateTime      @default(now()) @map("created_at")
  updatedAt       DateTime      @updatedAt @map("updated_at")

  project         Project       @relation(fields: [projectId], references: [id], onDelete: Cascade)
  productBrief    ProductBrief?
  scenePlan       ScenePlan?
  assets          Asset[]
  render          Render?

  @@index([status])
  @@index([createdAt])
  @@map("jobs")
}

model ProductBrief {
  id           String   @id @default(uuid()) @db.Uuid
  jobId        String   @unique @db.Uuid @map("job_id")
  rawJson      Json     @map("raw_json") // Validated against product-brief.schema.json
  tokensUsed   Int?     @map("tokens_used")
  modelUsed    String?  @map("model_used") @db.VarChar(64)
  createdAt    DateTime @default(now()) @map("created_at")

  job          Job      @relation(fields: [jobId], references: [id], onDelete: Cascade)
  @@map("product_briefs")
}

model ScenePlan {
  id                  String   @id @default(uuid()) @db.Uuid
  jobId               String   @unique @db.Uuid @map("job_id")
  totalDurationFrames Int      @map("total_duration_frames")
  fps                 Int      @default(60)
  rawJson             Json     @map("raw_json") // Validated against scene-plan.schema.json
  createdAt           DateTime @default(now()) @map("created_at")

  job                 Job      @relation(fields: [jobId], references: [id], onDelete: Cascade)
  @@map("scene_plans")
}

model Asset {
  id             String    @id @default(uuid()) @db.Uuid
  jobId          String    @db.Uuid @map("job_id")
  assetType      AssetType @map("asset_type")
  storagePath    String    @map("storage_path") @db.VarChar(1024)
  mimeType       String    @map("mime_type") @db.VarChar(128)
  fileSizeBytes  BigInt    @map("file_size_bytes")
  metadataJson   Json?     @map("metadata_json") // Viewport, resolution, duration
  createdAt      DateTime  @default(now()) @map("created_at")

  job            Job       @relation(fields: [jobId], references: [id], onDelete: Cascade)
  @@index([jobId, assetType])
  @@map("assets")
}

model Render {
  id                   String   @id @default(uuid()) @db.Uuid
  jobId                String   @unique @db.Uuid @map("job_id")
  outputUrl            String   @map("output_url") @db.VarChar(1024)
  durationSeconds      Float    @map("duration_seconds")
  resolution           String   @default("1920x1080") @db.VarChar(32)
  fps                  Int      @default(60)
  fileSizeBytes        BigInt   @map("file_size_bytes")
  renderDurationMs     Int      @map("render_duration_ms")
  computeCostUsd       Decimal? @db.Decimal(6, 4) @map("compute_cost_usd")
  createdAt            DateTime @default(now()) @map("created_at")

  job                  Job      @relation(fields: [jobId], references: [id], onDelete: Cascade)
  @@map("renders")
}
```

---

## 2. API Contract & Specification

The API follows REST conventions, utilizing standard HTTP status codes and RFC 7807 (`application/problem+json`) error envelopes.

### Base URL: `/api/v1`

---

### Endpoint 1: Create Video Job
`POST /api/v1/jobs`

Initiates the autonomous pipeline. Validates URLs against SSRF policies before accepting.

#### Request Headers
```http
Content-Type: application/json
Idempotency-Key: 9f8a3c8e-5b23-4c91-a67b-120938495810 (Optional)
```

#### Request Payload
```json
{
  "liveUrl": "https://superagent.dev",
  "repoUrl": "https://github.com/superagent-ai/superagent",
  "mood": "energetic",
  "includeVoiceover": true,
  "aspectRatio": "16:9",
  "authCredentials": {
    "loginUrl": "https://superagent.dev/login",
    "username": "demo@superagent.dev",
    "password": "TemporaryDemoPassword123!"
  }
}
```

#### Response: `202 Accepted`
```json
{
  "jobId": "f78a2d12-4e31-4e78-958b-bc1903e1a082",
  "status": "PENDING",
  "currentStage": "VALIDATING",
  "progressPercent": 0,
  "createdAt": "2026-10-24T16:20:00Z",
  "eventsUrl": "/api/v1/jobs/f78a2d12-4e31-4e78-958b-bc1903e1a082/events",
  "statusUrl": "/api/v1/jobs/f78a2d12-4e31-4e78-958b-bc1903e1a082"
}
```

---

### Endpoint 2: Get Job Status (Polling Fallback)
`GET /api/v1/jobs/{jobId}`

#### Response: `200 OK`
```json
{
  "jobId": "f78a2d12-4e31-4e78-958b-bc1903e1a082",
  "status": "RENDERING_MP4",
  "currentStage": "Compositing 1080p60 frames (Frame 1140/1800)",
  "progressPercent": 68,
  "estimatedTimeRemainingSeconds": 24,
  "error": null,
  "completedAt": null
}
```

---

### Endpoint 3: Real-Time Event Stream (Server-Sent Events)
`GET /api/v1/jobs/{jobId}/events`

#### Response: `200 OK (text/event-stream)`
Streams low-latency status events directly to the frontend.

```http
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive

event: state_change
data: {"jobId":"f78a2d12...","status":"ANALYZING_REPO","progress":15,"message":"Cloning AST and analyzing README..."}

event: state_change
data: {"jobId":"f78a2d12...","status":"CAPTURING_MEDIA","progress":40,"message":"Recording 60fps hero interactions via Playwright..."}

event: log
data: {"level":"info","timestamp":"2026-10-24T16:21:04Z","text":"Purged OneTrust cookie modal from DOM"}

event: state_change
data: {"jobId":"f78a2d12...","status":"COMPLETED","progress":100,"message":"Render finished successfully"}

event: complete
data: {"jobId":"f78a2d12...","downloadUrl":"https://cdn.premiere.dev/renders/f78a2d12.../final.mp4","previewUrl":"/api/v1/jobs/f78a2d12.../preview"}
```

---

### Endpoint 4: Get Remotion Preview Payload
`GET /api/v1/jobs/{jobId}/preview`

Returns the exact `RemotionProps` object. The web frontend mounts `@remotion/player` with this payload to allow instantaneous client-side scrubbing without waiting for download.

#### Response: `200 OK`
```json
{
  "compositionId": "PremiereLaunchVideo",
  "fps": 60,
  "width": 1920,
  "height": 1080,
  "durationInFrames": 1800,
  "theme": {
    "primaryColor": "#3B82F6",
    "accentColor": "#60A5FA",
    "backgroundColor": "#050505",
    "surfaceColor": "#121212",
    "headlineFont": "Bebas Neue",
    "captionFont": "Inter"
  },
  "audio": {
    "musicUrl": "https://cdn.premiere.dev/audio/tracks/cyber-pulse.mp3",
    "volume": 0.8,
    "beatTimestampsSeconds": [0.0, 1.875, 3.75, 5.625, 7.5],
    "narrationUrl": "https://cdn.premiere.dev/assets/f78a2d12/voiceover.mp3"
  },
  "scenes": [...]
}
```

---

### Endpoint 5: Download Final Render
`GET /api/v1/jobs/{jobId}/download`

Returns a 302 redirect to a secure, pre-signed S3/Cloudflare R2 download URL with `Content-Disposition: attachment; filename="premiere-launch.mp4"`.

---

## 3. Standardized Error Envelope (RFC 7807)

```json
{
  "type": "https://premiere.dev/errors/SSRF_BLOCKED",
  "title": "Restricted Target Host",
  "status": 400,
  "detail": "The supplied live URL resolves to a private or loopback IP range (127.0.0.1) which is strictly forbidden.",
  "instance": "/api/v1/jobs",
  "errorCode": "ERR_SSRF_PROHIBITED",
  "timestamp": "2026-10-24T16:20:01Z"
}
```
