# 07. Headless Browser Capture Engine (Playwright)

## 1. Overview & Capture Pipeline
The Headless Browser Capture Engine is an autonomous cinematographer running Playwright inside an isolated, hardened Linux container. Rather than capturing raw unguided scrolling, it executes scripted choreography: sweeping camera pans, organic synthetic cursor motions, and micro-element zooms, outputting high-framerate video and 4K-scaled snapshots.

---

## 2. Anti-Modal & Popup Scrubbing Strategy

Modern web applications present friction layers (GDPR cookie prompts, newsletter modals, chat widgets) that destroy promotional video aesthetics. The capture worker injects a stealth pre-navigation script that scrubs these elements before rendering begins:

```typescript
// injected into Page context before any site scripts execute
await page.addInitScript(() => {
  const BAD_SELECTORS = [
    '#onetrust-banner-sdk', '.cookie-banner', '[id*="cookie"]', '[class*="consent"]',
    '#intercom-container', '#drift-widget', '.crisp-client', '#hubspot-messages-iframe-container',
    '[aria-modal="true"]', '.modal-backdrop', '.newsletter-popup'
  ];

  // 1. Permanent CSS style injection
  const style = document.createElement('style');
  style.innerHTML = `
    ${BAD_SELECTORS.join(', ')} { display: none !important; opacity: 0 !important; visibility: hidden !important; pointer-events: none !important; }
    html, body { overflow: auto !important; position: static !important; }
  `;
  document.head.appendChild(style);

  // 2. Continuous MutationObserver to destroy dynamic late-injected nodes
  const observer = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      for (const node of mutation.addedNodes) {
        if (node instanceof HTMLElement) {
          for (const selector of BAD_SELECTORS) {
            if (node.matches(selector) || node.querySelector(selector)) {
              node.remove();
            }
          }
        }
      }
    }
  });

  observer.observe(document.documentElement, { childList: true, subtree: true });
});
```

---

## 3. Synthetic Bezier Cursor Choreography

Standard automated scripts exhibit robotic, instantaneous linear mouse movements. ReelForge computes cubic Bezier trajectories simulating human hand-eye motor deceleration (Fitts's Law):

```typescript
interface Point { x: number; y: number; }

function generateCubicBezierPath(start: Point, end: Point, numPoints = 60): Point[] {
  // Compute randomized control points perpendicular to trajectory
  const deltaX = end.x - start.x;
  const deltaY = end.y - start.y;
  const cp1 = { x: start.x + deltaX * 0.25 + (Math.random() - 0.5) * 50, y: start.y + deltaY * 0.1 };
  const cp2 = { x: start.x + deltaX * 0.75 + (Math.random() - 0.5) * 30, y: start.y + deltaY * 0.9 };

  const points: Point[] = [];
  for (let i = 0; i <= numPoints; i++) {
    const t = i / numPoints;
    // Ease-in-out time warp
    const easeT = t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
    const x = Math.pow(1 - easeT, 3) * start.x +
              3 * Math.pow(1 - easeT, 2) * easeT * cp1.x +
              3 * (1 - easeT) * Math.pow(easeT, 2) * cp2.x +
              Math.pow(easeT, 3) * end.x;
    const y = Math.pow(1 - easeT, 3) * start.y +
              3 * Math.pow(1 - easeT, 2) * easeT * cp1.y +
              3 * (1 - easeT) * Math.pow(easeT, 2) * cp2.y +
              Math.pow(easeT, 3) * end.y;
    points.push({ x: Math.round(x), y: Math.round(y) });
  }
  return points;
}
```

---

## 4. 60 FPS Capture Execution & Readiness Verification

To prevent capturing loading spinners, blank skeleton states, or partially painted fonts:

1. **Font Readiness**:
   ```typescript
   await page.evaluate(() => document.fonts.ready);
   ```
2. **Network Idle & Image Decoding**:
   ```typescript
   await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
   await page.evaluate(async () => {
     const images = Array.from(document.querySelectorAll('img'));
     await Promise.all(images.map(img => img.complete ? Promise.resolve() : img.decode().catch(() => {})));
   });
   ```
3. **High-DPI Recording**:
   Chromium is launched with a virtual viewport of $1920 \times 1080$ and `deviceScaleFactor: 2` (internal rendering at 4K $3840 \times 2160$ to guarantee anti-aliased, crisp text when downscaled inside device mockups).
4. **CDP Screencast Frame Pipeline**:
   The worker attaches to Chrome DevTools Protocol (`Page.startScreencast`, `format: 'jpeg'`, `quality: 95`, `everyNthFrame: 1`), piping lossless frame buffers into an FFmpeg stdin pipe encoding raw VP9/H.264 clips at constant 60fps.

---

## 5. Fallback Mechanisms (Bot Protection & Dynamic Failures)

When a target website is shielded by Cloudflare Turnstile, Akamai Bot Manager, or heavy client-side challenges:

```
[ Playwright Navigation Attempt ]
               |
               v
  [ HTTP Status 403 / 503 / Challenge Detected ]
               |
     +---------+---------+
     |                   |
[ Success ]         [ Blocked ]
                         |
                         v
           [ Tier 1: Stealth Spoofing ]
           - Re-launch with stealth headers
           - Spoofed Canvas/WebGL vendor fingerprints
                         |
                         v
                    [ Still Blocked? ]
                         |
                         v
           [ Tier 2: Static DOM Pan & Scan ]
           - Request public Wayback / Google Cache snapshot
           - Fallback to headless WebKit or rendering public OpenGraph hero image
           - Remotion animates synthetic CSS Ken-Burns camera sweep over static snapshot
```
