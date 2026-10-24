"""Capture stage: hardened Playwright cinematographer with SSRF route filter and anti-modal cleanup."""

import asyncio
import os
from pathlib import Path
from playwright.async_api import Route, async_playwright
from api.security import validate_public_url

COOKIE_MODAL_SELECTORS = [
    "#onetrust-banner-sdk", ".cookie-banner", '[id*="cookie"]', '[class*="consent"]',
    "#intercom-container", ".crisp-client", '[aria-modal="true"]', ".modal-backdrop",
    ".newsletter-modal", '[id*="newsletter"]', "#drift-widget"
]

CURSOR_STYLE_INJECTION = """
  const cur = document.createElement('div');
  cur.id = 'premiere-synthetic-cursor';
  cur.style.cssText = 'position:fixed;width:20px;height:20px;border-radius:50%;background:rgba(255,255,255,0.85);' +
    'border:2px solid #3b82f6;pointer-events:none;z-index:999999;transition:transform 0.05s ease;transform:translate(-50%, -50%);' +
    'box-shadow: 0 0 20px rgba(59,130,246,0.6);';
  document.body.appendChild(cur);
  window.__moveCursor = (x, y) => { cur.style.left = x + 'px'; cur.style.top = y + 'px'; };
"""

async def intercept_ssrf_routes(route: Route):
    """Abort any request or redirect that attempts to target private subnets."""
    try:
        validate_public_url(route.request.url)
        await route.continue_()
    except Exception:
        await route.abort("accessdenied")

async def capture_page(
    live_url: str,
    output_dir: Path,
    scene_id: str,
    target_route: str = "/",
    timeout_sec: float = 15.0,
) -> dict[str, str]:
    """Capture 1920x1080 screenshot with SSRF route shielding and anti-modal cleanup."""
    os.makedirs(output_dir, exist_ok=True)
    screenshot_path = output_dir / f"{scene_id}.png"
    target_full_url = live_url.rstrip("/") + ("/" + target_route.lstrip("/") if target_route != "/" else "")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox", "--disable-dev-shm-usage"],
        )
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=2,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36",
        )
        page = await context.new_page()

        # Route-level SSRF interceptor preventing malicious redirects to internal IP
        await page.route("**/*", intercept_ssrf_routes)

        try:
            # 1. Navigate with timeout protection
            await page.goto(target_full_url, wait_until="domcontentloaded", timeout=timeout_sec * 1000)

            # 2. Wait for fonts & SPA hydration
            await page.evaluate("() => document.fonts ? document.fonts.ready : Promise.resolve()")
            await page.wait_for_timeout(1000)

            # 3. Clean cookie banners & overlays
            cleanup_js = f"""
                document.querySelectorAll('{", ".join(COOKIE_MODAL_SELECTORS)}').forEach(el => el.remove());
                document.body.style.overflow = 'auto';
            """
            await page.evaluate(cleanup_js)

            # 4. Inject animated cursor
            await page.evaluate(CURSOR_STYLE_INJECTION)

            # 5. Smooth scroll down and back for lazy-loaded assets
            for y in range(0, 300, 75):
                await page.evaluate(f"window.scrollBy({{top: 75, behavior: 'smooth'}}); window.__moveCursor(960, {400 + y // 2});")
                await page.wait_for_timeout(40)

            await page.screenshot(path=str(screenshot_path), full_page=False)

        except Exception:
            from PIL import Image, ImageDraw
            img = Image.new("RGB", (1920, 1080), color=(15, 17, 23))
            draw = ImageDraw.Draw(img)
            draw.text((960, 540), f"LIVE APPLICATION: {target_route}", fill=(100, 150, 255), anchor="mm")
            img.save(str(screenshot_path))

        finally:
            await context.close()
            await browser.close()

    return {"screenshot": str(screenshot_path)}
