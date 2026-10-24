# 06. Scene Template Catalog & Motion Design System

## 1. Non-Negotiable Design System Specification

| Attribute | Specification | Implementation Rationale |
| :--- | :--- | :--- |
| **Headline Typography** | **Bebas Neue** (Google Fonts), Uppercase | Delivers the bold, uncompromising, industrial punch of Apple keynote title cards and Nike promotional campaigns. Ultra-tight tracking (`letter-spacing: -0.02em`). |
| **Caption Typography** | **Inter** (Google Fonts), Regular/Medium, 400-500 weight | Maximum micro-legibility at 1080p and 4K resolutions for subtitles, technical tags, and URLs. |
| **Color Atmosphere** | Deep Obsidian Palette | `#050505` canvas base, `#0D0F14` card surface, with subtle atmospheric radial glows (`rgba(59, 130, 246, 0.12)`) centered at 50% 30% viewport. Zero harsh pure-white backgrounds. |
| **Motion Physics** | Spring-driven easing & smooth cubic-bezier | Spring settings: `stiffness: 140`, `damping: 18`, `mass: 1.0`. Cubic bezier for camera zooms: `cubic-bezier(0.16, 1.0, 0.3, 1.0)` (Apple ease-out). No linear transitions. |
| **Device Skeuomorphism** | Floating 3D Device Frames | MacBook Pro and iPhone 15 Pro frames rendered with subtle 3D perspective (`perspective: 1200px`, `rotateX(8deg)`, `rotateY(-10deg)`). Dual-depth diffuse drop shadows (`box-shadow: 0 30px 60px -12px rgba(0,0,0,0.85), 0 0 100px rgba(59,130,246,0.15)`). |
| **Pacing Discipline** | 2 to 4 seconds per scene | Maximum 1 cognitive concept per scene. Immediate visual interest, zero static frames. Cuts aligned to musical bars. |

---

## 2. Transition System & Permissibility Matrix

### Transition Definitions & Usage Criteria

1. **`push` (Directional Slide)**:
   - *Mechanic*: Outgoing scene slides left at $v(t)$, incoming scene slides in with subtle motion blur ($8\text{px}$).
   - *When Used*: Transitioning between parallel features or secondary screens.
2. **`zoom-through` (Camera Penetration)**:
   - *Mechanic*: Camera scales deeply into an element ($1.0 \to 4.0\times$) until pixels dissolve into the incoming viewport.
   - *When Used*: Transitioning from abstract `TitleReveal` directly into live UI `DeviceShowcase`.
3. **`mask-wipe` (Geometric High-Contrast Wipe)**:
   - *Mechanic*: 45-degree diagonal mask knife cuts across the frame in 12 frames on a strong musical beat.
   - *When Used*: Transitioning into high-impact `StatCounter` or key value inflection points.
4. **`blur-dissolve` (Gaussian Cross-Fade)**:
   - *Mechanic*: Simultaneous 20px Gaussian blur and opacity cross-fade across 14 frames.
   - *When Used*: Soft emotional transition from feature demo into brand `Outro`.
5. **`glitch-flash` (Chromatic Strobe Burst)**:
   - *Mechanic*: 2-frame RGB channel offset (red +8px, blue -8px) with a 1-frame 100% brightness peak.
   - *When Used*: Preceding rapid-fire `KineticText` sequences or high-tempo musical drops.
6. **`shared-element-morph` (Positional Interpolation)**:
   - *Mechanic*: Persistent element (e.g. device mockup or logo) smoothly rescales and translates position while background and nested contents morph.
   - *When Used*: Consecutive feature highlights within the same application layout.

### Permissibility & Transition Compatibility Matrix

| From Scene \ To Scene | TitleReveal | DeviceShowcase | FeatureZoom | StatCounter | KineticText | Outro |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **TitleReveal** | ❌ | `zoom-through` | `push` | `mask-wipe` | `glitch-flash` | ❌ |
| **DeviceShowcase** | ❌ | `shared-element-morph` | `zoom-through` | `mask-wipe` | `glitch-flash` | `blur-dissolve` |
| **FeatureZoom** | ❌ | `push` | `shared-element-morph` | `mask-wipe` | `glitch-flash` | `blur-dissolve` |
| **StatCounter** | ❌ | `push` | `zoom-through` | ❌ | `glitch-flash` | `blur-dissolve` |
| **KineticText** | ❌ | `zoom-through` | `push` | `mask-wipe` | `glitch-flash` | `blur-dissolve` |
| **Outro** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## 3. Scene Template Catalog & Props Specification

### 1. `TitleReveal`
- **Purpose**: Establishes brand dominance in first 2.5 seconds.
- **Duration**: 120 - 150 frames (2.0s - 2.5s at 60fps).
- **Visuals**: Massive Bebas Neue title scales from 90% to 100% with spring dampening; atmospheric radial glow pulses behind brand name; tagline fades in with letter-spacing expansion.
- **Props Schema**:
```typescript
interface TitleRevealProps {
  productName: string;         // e.g. "SUPERAGENT" (Bebas Neue, 120pt)
  tagline: string;             // e.g. "AUTONOMOUS AI WORKFLOWS" (Bebas Neue, 48pt)
  categoryBadge?: string;      // e.g. "NEXT-GEN DEVELOPER PLATFORM" (Inter, 16pt)
  brandColor: string;          // e.g. "#3B82F6"
}
```

---

### 2. `DeviceShowcase`
- **Purpose**: Presents the live application running inside a floating 3D browser or mobile frame.
- **Duration**: 180 - 240 frames (3.0s - 4.0s at 60fps).
- **Visuals**: MacBook Pro frame floats in 3D perspective (`rotateY(-8deg)`, `rotateX(6deg)`) with slow parallax drift; screencast video plays inside device screen; smooth Bezier cursor glides to a key CTA.
- **Props Schema**:
```typescript
interface DeviceShowcaseProps {
  headline: string;            // e.g. "INTELLIGENT BY DEFAULT"
  caption: string;             // e.g. "Unified workspace for autonomous workflows"
  deviceType: "laptop" | "mobile" | "dual";
  mediaUrl: string;            // Pre-signed S3 URL for 60fps screencast clip
  cursorTrajectory?: {
    startX: number; startY: number;
    endX: number; endY: number;
    clickAtFrame?: number;
  };
}
```

---

### 3. `FeatureZoom`
- **Purpose**: Highlights a micro-interaction or complex UI card (e.g., chart, table, AI chat dialog).
- **Duration**: 120 - 180 frames (2.0s - 3.0s at 60fps).
- **Visuals**: Darkened surrounding vignette overlays the full page while the target element is spotlighted, scaled 1.25x with a subtle glowing border, accompanied by an animated pointer callout.
- **Props Schema**:
```typescript
interface FeatureZoomProps {
  featureHeadline: string;     // e.g. "REAL-TIME TELEMETRY"
  featureDescription: string;  // e.g. "Sub-millisecond query inspection"
  screenshotUrl: string;       // High-DPI 2x screenshot of full page
  cropBoundingBox: {           // Coordinates of target element
    x: number; y: number;
    width: number; height: number;
  };
  highlightGlowColor: string;  // e.g. "#10B981"
}
```

---

### 4. `StatCounter`
- **Purpose**: Validates product performance with quantifiable social proof or benchmarks.
- **Duration**: 120 - 150 frames (2.0s - 2.5s at 60fps).
- **Visuals**: Giant Bebas Neue numerals roll up rapidly from 0 to final target value using spring physics; floating ambient geometric particles in background.
- **Props Schema**:
```typescript
interface StatCounterProps {
  metricValue: string;         // e.g. "10x" or "99.99%"
  metricLabel: string;         // e.g. "THROUGHPUT INCREASE"
  supportingDetail: string;    // e.g. "Benchmarked across 1M concurrent pipelines"
  accentGlow: string;
}
```

---

### 5. `KineticText`
- **Purpose**: High-energy, staccato typographic burst (Nike launch style) to elevate emotional tempo before the finale.
- **Duration**: 90 - 120 frames (1.5s - 2.0s at 60fps).
- **Visuals**: 3-4 power words flash in rapid succession (e.g. "BUILT." -> "FOR." -> "SCALE."), 18 frames each, beat-synced with subtle screen shake and strobe accents.
- **Props Schema**:
```typescript
interface KineticTextProps {
  words: string[];             // e.g. ["FASTER.", "STRONGER.", "UNSTOPPABLE."]
  highlightColor: string;
  flashSpeedFrames: number;    // e.g. 18 frames per word
}
```

---

### 6. `Outro`
- **Purpose**: Final call-to-action, branding stamp, and repository destination.
- **Duration**: 150 - 180 frames (2.5s - 3.0s at 60fps).
- **Visuals**: Centered brand logo resolves with metallic edge gleam; GitHub star counter badge and live domain URL pulsate gently; cinematic fade to pure black.
- **Props Schema**:
```typescript
interface OutroProps {
  productName: string;
  primaryCtaText: string;      // e.g. "START BUILDING TODAY"
  domainUrl: string;           // e.g. "reelforge.io"
  githubStarsBadge?: string;   // e.g. "★ 4.2k ON GITHUB"
  logoUrl?: string;
}
```
