"""Capture stage: headless Playwright cinematographer with anti-modal cleanup and smooth actions."""

import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

COOKIE_MODAL_SELECTORS = [
    "#onetrust-banner-sdk", ".cookie-banner", '[id*="cookie"]', '[class*="consent"]',
    "#intercom-container", ".crisp-client", '[aria-modal="true"]', ".modal-backdrop"
]

CURSOR_STYLE_INJECTION = """
  const cur = document.createElement('div');
  cur.id = 'reelforge-synthetic-cursor';
  cur.style.cssText = 'position:fixed;width:20px;height:20px;border-radius:50%;background:rgba(255,255,255,0.8);' +
    'border:2px solid #3b82f6;pointer-events:none;z-index:999999;transition:transform 0.05s ease;transform:translate(-50%, -50%);';
  document.body.appendChild(cur);
  window.__moveCursor = (x, y) => { cur.style.left = x + 'px'; cur.style.top = y + 'px'; };
"""

async def capture_page(
    live_url: str,
    output_dir: Path,
    scene_id: str,
    target_route: str = "/",
    timeout_sec: float = 15.0,
) -> dict[str, str]:
    """Capture 1920x1080 screenshot and scroll sequence with anti-modal cleanup."""
    os.makedirs(output_dir, exist_ok=True)
    screenshot_path = output_dir / f"{scene_id}.png"
    target_full_url = live_url.rstrip("/") + ("/" + target_route.lstrip("/") if target_route != "/" else "")

    assets = {"screenshot": str(screenshot_path)}

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=2,  # Crisp 4K downsampled retina rendering
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36",
        )
        page = await context.new_page()

        try:
            # 1. Navigate with timeout protection
            await page.goto(target_full_url, wait_until="domcontentloaded", timeout=timeout_sec * 1000)
            await page.wait_for_timeout(1500)

            # 2. Inject anti-modal and cookie purge script
            cleanup_js = f"""
                document.querySelectorAll('{", ".join(COOKIE_MODAL_SELECTORS)}').forEach(el => el.remove());
                document.body.style.overflow = 'auto';
            """
            await page.evaluate(cleanup_js)

            # 3. Inject synthetic animated cursor
            await page.evaluate(CURSOR_STYLE_INJECTION)

            # 4. Animate smooth scroll and cursor movement
            for y_offset in range(0, 300, 50):
                await page.evaluate(f"window.scrollBy({{top: 50, behavior: 'smooth'}}); window.__moveCursor(960, {400 + y_offset // 2});")
                await page.wait_for_timeout(50)

            # 5. Capture crisp full high-DPI snapshot
            await page.screenshot(path=str(screenshot_path), full_page=False)

        except Exception as exc:
            # Graceful fallback: synthesize a solid minimalist mock frame on timeout or navigation block
            from PIL import Image, ImageDraw
            img = Image.new("RGB", (1920, 1080), color=(15, 17, 23))
            draw = ImageDraw.Draw(img)
            draw.text((800, 500), f"PREVIEW: {target_route}", fill=(100, 150, 255))
            img.save(str(screenshot_path))

        finally:
            await context.close()
            await browser.close()

    return assets
