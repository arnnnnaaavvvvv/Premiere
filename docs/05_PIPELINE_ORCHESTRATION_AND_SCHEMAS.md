# 05. Pipeline Orchestration & Transformation Stages

## 1. Pipeline Stage Flow & Contract Progression

```
+---------------------------------------------------------------------------------------------------+
|  STAGE 1: INGESTION & STATIC REPO ANALYSIS                                                        |
|  Inputs: liveUrl (string), repoUrl (string)                                                       |
|  Tasks:                                                                                           |
|    - Fetch GitHub README.md, package.json, and directory tree (routes/pages)                     |
|    - Playwright lightweight probe for DOM metadata: <title>, meta[description], OpenGraph tags    |
|  Outputs: Raw Context Token Buffer (< 8,000 tokens)                                              |
+---------------------------------------------------------------------------------------------------+
                                              |
                                              v
+---------------------------------------------------------------------------------------------------+
|  STAGE 2: PRODUCT BRIEF SYNTHESIS (LLM Analyzer)                                                  |
|  Inputs: Raw Context Buffer + Extraction System Prompt                                            |
|  Tasks:                                                                                           |
|    - Claude 3.5 Sonnet / GPT-4o with Pydantic JSON enforcement                                   |
|    - Distill product name, punchy tagline, elevator pitch, 3-5 core features, and metrics         |
|  Outputs: ProductBriefJSON (conforms to product-brief.schema.json)                                |
+---------------------------------------------------------------------------------------------------+
                                              |
                                              v
+---------------------------------------------------------------------------------------------------+
|  STAGE 3: CINEMATIC DIRECTOR & SCENE PLANNING (LLM Director)                                      |
|  Inputs: ProductBriefJSON + Mood Selection (Minimal / Energetic / Futuristic) + Audio BPM Grid    |
|  Tasks:                                                                                           |
|    - Formulate 6 to 10 cinematic scenes (2-4 seconds each)                                       |
|    - Match scene goals to template types (TitleReveal, DeviceShowcase, FeatureZoom, etc.)         |
|    - Assign permissible transition pairs (push, zoom-through, mask-wipe, etc.)                   |
|    - Quantize scene frame lengths to music beat intervals                                        |
|  Outputs: ScenePlanJSON (conforms to scene-plan.schema.json)                                      |
+---------------------------------------------------------------------------------------------------+
                                              |
                                              v
+---------------------------------------------------------------------------------------------------+
|  STAGE 4: CAPTURE MANIFEST COMPILATION                                                            |
|  Inputs: ScenePlanJSON + liveUrl + authCredentials                                                |
|  Tasks:                                                                                           |
|    - Map each visual scene requirement to a discrete Playwright browser action sequence          |
|    - Define viewport dimensions, CSS anti-modal selectors, scroll offsets, and cursor paths       |
|  Outputs: CaptureManifestJSON (conforms to capture-manifest.schema.json)                          |
+---------------------------------------------------------------------------------------------------+
                                              |
                                              v
+---------------------------------------------------------------------------------------------------+
|  STAGE 5: HEADLESS BROWSER CAPTURE & AUDIO MASTERING                                              |
|  Inputs: CaptureManifestJSON & Selected Audio Stem                                                |
|  Tasks:                                                                                           |
|    - Playwright captures 60fps raw clips (.webm) & 4K PNG snapshots                               |
|    - Librosa processes beat stamps; ElevenLabs generates narration (if enabled)                  |
|    - FFmpeg normalizes audio to -14 LUFS and applies sidechain ducking curve                      |
|  Outputs: Uploaded S3 Asset Bundle (Clips, Snapshots, Master Audio)                               |
+---------------------------------------------------------------------------------------------------+
                                              |
                                              v
+---------------------------------------------------------------------------------------------------+
|  STAGE 6: REMOTION PROPS RESOLUTION & RENDERING                                                   |
|  Inputs: ScenePlanJSON + S3 Asset Bundle URLs + Audio Beat Markers                                |
|  Tasks:                                                                                           |
|    - Resolve asset pointers into verified pre-signed CDN URLs                                     |
|    - Assemble final RemotionProps JSON payload                                                    |
|    - Dispatch Remotion headless Chromium render (or Remotion Lambda chunks)                       |
|    - Stitch and encode final 1080p60 H.264 / AAC MP4                                              |
|  Outputs: final_launch_1080p60.mp4 (stored on Cloudflare R2 / S3)                                 |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. Detailed Transformation Schemas & Logic

### Stage 1 -> 2: Token-Efficient Repository Extraction
To prevent context overflow and reduce latency, the Analyzer worker does not clone the full Git commit history. Instead, it issues targeted queries:
1. Fetch `README.md` (truncated to first 4,000 characters).
2. Fetch `package.json` (extracting `name`, `description`, `dependencies`).
3. Fetch GitHub Git Tree API: recursive scan of file paths matching:
   - `pages/**/*.{tsx,jsx,vue,svelte}` or `app/**/*.{tsx,jsx,vue,svelte}`
   - Filters out icons, tests, and styles.
   - Extracts top 5 route names (e.g. `/dashboard`, `/analytics`, `/integrations`).

### Stage 2: Product Brief Prompt Structure
```text
System: You are a Silicon Valley Creative Director specializing in Apple/Nike product launch films.
Input: Repository README, package.json, top routes, and homepage meta tags.
Task: Synthesize this technical project into high-impact launch film metadata.
Strict Rule: Adhere to Bebas Neue display constraints: Taglines and headlines must be short (2-5 words), UPPERCASE, punchy, and confident. Avoid corporate jargon.
Output: Return purely valid JSON adhering to ProductBrief schema.
```

### Stage 3: Beat-Quantization Algorithm
Scene durations must never feel arbitrary; cuts occur precisely on musical downbeats.
Given a selected soundtrack at $BPM = 128$:
- Time per beat: $T_{\text{beat}} = \frac{60}{128} = 0.46875\text{ seconds}$
- Frames per beat at 60 FPS: $F_{\text{beat}} = 0.46875 \times 60 = 28.125\text{ frames}$
- A 4-beat bar: $F_{\text{bar}} = 4 \times 28.125 = 112.5\text{ frames} \approx 1.875\text{s}$
- Permissible scene lengths:
  - 1 Bar (Fast / KineticText): ~112 frames (1.87s)
  - 1.5 Bars (Standard UI Zoom): ~169 frames (2.81s)
  - 2 Bars (Hero Device Showcase): ~225 frames (3.75s)
The Director LLM specifies nominal scene lengths in beats (e.g., 4 beats, 6 beats, 8 beats), and the Audio worker resolves exact frame boundaries to prevent rounding drift.
