# 01. System Scope & Non-Goals

## 1. Executive Summary
**ReelForge** is a specialized, zero-touch automated video generation engine. By accepting two primary inputs—a **live project URL** and a **public or authenticated GitHub repository URL**—it synthesizes software architecture, brand tokens, and UI layout into an ultra-premium, 60fps MNC-grade launch video (MP4) in under 3 minutes.

The design benchmark is the high-velocity, precision-engineered hardware and software launch films pioneered by Apple and Nike:
- Typography anchored by **Bebas Neue** (massive, tight uppercase display headings) with **Inter** micro-captions.
- Obsidian and deep-gradient lighting environments.
- 3D perspective floating device frames with dual-depth diffuse drop shadows.
- Micro-interaction zooms with synthetic Bezier cursor paths.
- Rhythmic, beat-synchronized frame pacing.

---

## 2. Scope Matrix: MVP vs. v2 vs. v3

| Dimension | Phase 1 (MVP) | Phase 2 (v2) | Phase 3 (v3) |
| :--- | :--- | :--- | :--- |
| **Output Formats** | 1080p (1920x1080), 60 FPS, 16:9 Landscape. H.264 / AAC MP4. | 9:16 Vertical (Reels/Shorts/TikTok), 1:1 Square (LinkedIn/Twitter). | Multi-asset bundle export (4K 16:9, 9:16 vertical, animated GIFs). |
| **Target Video Length** | 30s to 45s (tight 6 to 10 scenes, 2-4s each). | 30s to 60s customizable target duration. | Dynamic 15s teaser, 30s promo, or 90s deep dive. |
| **Input Sources** | Public live web URL + Public GitHub repository URL. | Public/Private GitHub repos (OAuth); Password/Basic-Auth web URLs. | Complex OAuth2/SAML flows, local Docker containers, preview deployments (Vercel/Netlify). |
| **Intelligence Engine** | Static AST + README + Package.json + DOM metadata parsing via Claude 3.5 Sonnet / GPT-4o. | Multi-page route crawler, user flow extraction from Cypress/Playwright test suites. | Autonomous agentic site traversal (simulating real user workflows like signup, checkout). |
| **Scene Catalog** | 6 Core Templates: `TitleReveal`, `DeviceShowcase`, `FeatureZoom`, `StatCounter`, `KineticText`, `Outro`. | +4 Templates: `CodeDiffExplosion`, `ArchitectureBento`, `TestimonialQuote`, `TerminalRun`. | Custom user-submitted React Remotion templates; community template registry. |
| **Browser Capture** | Headless Playwright: smooth scroll, synthetic cursor hover/click, banner purges, 2x DPR snapshots. | Synthetic video recording via CDP screencast, automated canvas & WebGL capture. | Multi-screen concurrent sync capture (e.g. mobile app + desktop dashboard side-by-side). |
| **Audio & Narration** | Curated 15-track royalty-free library (3 moods), Librosa beat detection & quantization. | Automated AI voiceover (ElevenLabs) with -14dB auto-ducking; user audio upload. | Multi-language AI voiceover (12+ locales) with lip-synced avatar or subtitle burn-in. |
| **Rendering Worker** | Dedicated Docker worker pool with headless Chromium + Remotion CLI. | Remotion Lambda distributed rendering across 100+ AWS Lambda chunks (<30s render). | Hybrid execution: edge preview rendering + serverless Lambda final export. |
| **User Editing** | Static generation with regenerate prompt parameter. | Web-based storyboard editor: edit text, swap track, change scene order. | Full browser Remotion timeline scrubbing with live element repositioning. |

---

## 3. Explicit Non-Goals

To maintain high development velocity, rock-solid reliability, and single-purpose engineering excellence, ReelForge explicitly excludes:

1. **Not a Freeform Canvas Video Editor (No Premiere/Canva/CapCut Clone)**  
   ReelForge will not provide a drag-and-drop timeline, manual keyframe curve editors, custom font uploads, or arbitrary layer positioning. All motion graphics are governed by programmatic React compositions with strict design tokens.

2. **Not a General Screen Recorder or Desktop Application Capture Tool**  
   ReelForge does not capture Electron desktop apps, mobile simulators on local host machines, or CLI terminal windows unless they are exposed through a web interface.

3. **Not an Automated QA / E2E Testing Suite**  
   While Playwright is used for automation, ReelForge does not run functional assertions, regression checks, or load testing. The browser session is strictly an aesthetic cinematography rig.

4. **Not a Permanent Video Hosting or Streaming CDN**  
   ReelForge generates and delivers downloadable MP4 files. Rendered videos are retained in S3/Cloudflare R2 storage for a configurable retention window (e.g., 7 days on free tiers, 30 days on paid tiers) with signed download links. Long-term video streaming or embed player hosting is not provided.

5. **Not a Code Remediation or Code Review Platform**  
   The repository analysis pipeline extracts brand identity, tech stack, and feature descriptions; it does not review, lint, or provide security assessments of the user's code.

---

## 4. Architectural Assumptions
- **Host Target Compatibility**: Target web applications must render in modern headless Chromium without requiring hardware security dongles or biometric 2FA.
- **Repository Access**: Public repositories are inspected via GitHub raw content and GraphQL APIs without cloning full commit histories. Private repositories in v2 require user-granted OAuth scopes.
- **Deterministic Output**: Given an identical `ScenePlanJSON` and asset bundle, the Remotion composition will output a bit-for-bit identical MP4 video.
