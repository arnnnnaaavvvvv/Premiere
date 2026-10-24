"""Zelios-style motion graphics engine: 3D perspective transforms, glassmorphism, and cursors."""

import math
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONTS_DIR = Path(__file__).resolve().parent / "assets" / "fonts"
BEBAS_FONT_PATH = FONTS_DIR / "BebasNeue-Regular.ttf"
INTER_FONT_PATH = FONTS_DIR / "Inter-Regular.ttf"

def get_font(path: Path, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load bundled TrueType font with system fallback."""
    if path.exists():
        try:
            return ImageFont.truetype(str(path), size)
        except Exception:
            pass
    try:
        return ImageFont.truetype("arialbd.ttf" if "Bebas" in path.name else "arial.ttf", size)
    except Exception:
        return ImageFont.load_default()

def ease_out_cubic(t: float) -> float:
    """Smooth cubic deceleration curve for snappy tech UI animations."""
    t = max(0.0, min(1.0, t))
    return 1.0 - math.pow(1.0 - t, 3)

def draw_volumetric_glow(draw: ImageDraw.Draw, center: tuple[int, int], radius: int, color: tuple[int, int, int], alpha: int = 40):
    """Render atmospheric radial gradient glow with multi-layered falloff."""
    cx, cy = center
    for r, a in [(radius, int(alpha * 0.15)), (int(radius * 0.65), int(alpha * 0.4)), (int(radius * 0.35), alpha)]:
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*color, a))

def draw_tech_grid(draw: ImageDraw.Draw, w: int, h: int, horizon_y: int = 540, vanishing_x: int = 960):
    """Draw subtle perspective tech grid floor converging to vanishing point."""
    grid_color = (255, 255, 255, 12)
    for x in range(0, w + 200, 160):
        draw.line([(vanishing_x, horizon_y), (x - 100, h)], fill=grid_color, width=1)
    for y in [600, 680, 780, 900, 1040]:
        draw.line([(0, y), (w, y)], fill=grid_color, width=1)

def create_saas_dashboard(product: str, headline: str, brand_color=(59, 130, 246)) -> Image.Image:
    """Generate high-fidelity Zelios-style SaaS dashboard mockup with navigation, metrics, and charts."""
    img = Image.new("RGBA", (1280, 720), (13, 16, 23, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, 220, 720], fill=(18, 22, 31, 255))
    draw.rounded_rectangle([20, 24, 52, 56], radius=8, fill=brand_color)
    draw.text((64, 30), product[:12].upper(), fill=(255, 255, 255), font=get_font(BEBAS_FONT_PATH, 24))
    for i, item in enumerate(["OVERVIEW", "ANALYTICS", "SECURITY", "SETTINGS"]):
        y = 100 + i * 44
        col = (255, 255, 255) if i == 0 else (120, 135, 155)
        if i == 0:
            draw.rounded_rectangle([12, y - 6, 208, y + 26], radius=6, fill=(*brand_color, 45))
        draw.text((36, y), item, fill=col, font=get_font(INTER_FONT_PATH, 14))

    draw.rectangle([220, 0, 1280, 64], fill=(18, 22, 31, 255))
    draw.text((250, 20), headline[:36].upper(), fill=(255, 255, 255), font=get_font(BEBAS_FONT_PATH, 24))
    draw.rounded_rectangle([1120, 14, 1250, 48], radius=6, fill=brand_color)
    draw.text((1185, 24), "DEPLOY", fill=(255, 255, 255), font=get_font(BEBAS_FONT_PATH, 18), anchor="mm")

    for i, (m_val, m_lbl) in enumerate([("99.98%", "SYSTEM UPTIME"), ("12.4ms", "AVG LATENCY"), ("2.4M+", "SESSIONS")]):
        cx = 250 + i * 330
        draw.rounded_rectangle([cx, 88, cx + 310, 190], radius=10, fill=(22, 27, 38, 255), outline=(255, 255, 255, 20))
        draw.text((cx + 20, 108), m_lbl, fill=(120, 135, 155), font=get_font(INTER_FONT_PATH, 13))
        draw.text((cx + 20, 132), m_val, fill=(255, 255, 255), font=get_font(BEBAS_FONT_PATH, 42))

    draw.rounded_rectangle([250, 210, 1240, 690], radius=12, fill=(22, 27, 38, 255), outline=(255, 255, 255, 20))
    pts = [(280 + j * 90, 520 - int(math.sin(j * 0.7) * 120 + j * 12)) for j in range(11)]
    draw.line(pts, fill=brand_color, width=3)
    for p in pts:
        draw.ellipse([p[0] - 5, p[1] - 5, p[0] + 5, p[1] + 5], fill=(255, 255, 255))
    return img

def build_device_mockup(screen_img: Image.Image, product: str = "PREMIERE", headline: str = "PLATFORM", w: int = 1280, h: int = 760, brand_color=(59, 130, 246)) -> Image.Image:
    """Wrap page screenshot or synthesize SaaS dashboard inside sleek titanium browser mockup."""
    mockup = Image.new("RGBA", (w, h), (13, 15, 20, 255))
    draw = ImageDraw.Draw(mockup)
    draw.rounded_rectangle([0, 0, w - 1, h - 1], radius=16, fill=(13, 15, 20, 255), outline=(255, 255, 255, 38), width=2)
    draw.rounded_rectangle([0, 0, w - 1, 40], radius=16, fill=(22, 27, 34, 255))
    draw.rectangle([0, 24, w - 1, 40], fill=(22, 27, 34, 255))
    for i, col in enumerate([(239, 68, 68), (245, 158, 11), (16, 185, 129)]):
        draw.ellipse([16 + i * 18, 14, 26 + i * 18, 24], fill=col)
    draw.rounded_rectangle([180, 9, w - 180, 31], radius=6, fill=(33, 38, 45, 255), outline=(255, 255, 255, 18))

    # Detect blank or dark screens and fall back to rich synthesized dashboard
    screen_np = np.array(screen_img)
    if screen_np.std() < 12.0:
        screen_img = create_saas_dashboard(product, headline, brand_color)

    resized_screen = screen_img.convert("RGBA").resize((w - 4, h - 44), Image.Resampling.LANCZOS)
    mockup.paste(resized_screen, (2, 42))
    return mockup

def warp_3d_device(device_rgba: Image.Image, dst_pts: np.ndarray, canvas_w: int = 1920, canvas_h: int = 1080) -> np.ndarray:
    """Project device mockup into 3D isometric perspective using homography."""
    dev_np = np.array(device_rgba)
    h, w = dev_np.shape[:2]
    src_pts = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    M = cv2.getPerspectiveTransform(src_pts, dst_pts.astype(np.float32))
    return cv2.warpPerspective(dev_np, M, (canvas_w, canvas_h), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_CONSTANT)

def draw_glass_card(draw: ImageDraw.Draw, x: int, y: int, w: int, h: int, title: str, subtitle: str, color=(59, 130, 246)):
    """Render floating frosted glassmorphism card with glowing neon badge and sleek typography."""
    draw.rounded_rectangle([x, y, x + w, y + h], radius=14, fill=(15, 20, 28, 220), outline=(255, 255, 255, 45), width=1)
    draw.rounded_rectangle([x + 14, y + 14, x + 34, y + 34], radius=6, fill=(*color, 230))
    draw.text((x + 44, y + 12), title.upper(), fill=(255, 255, 255), font=get_font(BEBAS_FONT_PATH, 28))
    draw.text((x + 44, y + 38), subtitle, fill=(148, 163, 184), font=get_font(INTER_FONT_PATH, 16))

def draw_animated_cursor(draw: ImageDraw.Draw, start: tuple[int, int], end: tuple[int, int], progress: float):
    """Draw smooth gliding vector cursor with expanding click ripple shockwave."""
    t = ease_out_cubic(progress)
    cx, cy = int(start[0] + (end[0] - start[0]) * t), int(start[1] + (end[1] - start[1]) * t)
    if progress > 0.6:
        rip_prog = (progress - 0.6) / 0.4
        rip_r, rip_a = int(rip_prog * 45), int(220 * (1.0 - rip_prog))
        draw.ellipse([cx - rip_r, cy - rip_r, cx + rip_r, cy + rip_r], outline=(59, 130, 246, rip_a), width=2)
    pts = [(cx, cy), (cx + 16, cy + 12), (cx + 10, cy + 14), (cx + 15, cy + 24), (cx + 11, cy + 26), (cx + 6, cy + 15), (cx, cy + 19)]
    draw.polygon(pts, fill=(255, 255, 255, 255), outline=(0, 0, 0, 220))
