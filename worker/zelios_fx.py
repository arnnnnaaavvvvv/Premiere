"""Zelios & Notion-style motion graphics engine: modular UI blocks, multi-cursor choreography, 3D perspective, and fluid transitions."""

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

def ease_in_out_cubic(t: float) -> float:
    """Smooth S-curve easing for camera pans and continuous transitions."""
    t = max(0.0, min(1.0, t))
    return 4 * t * t * t if t < 0.5 else 1 - math.pow(-2 * t + 2, 3) / 2

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

# ==============================================================================
# Notion Explainer Style Primitives & Visual Components
# ==============================================================================

def draw_notion_studio_background(draw: ImageDraw.Draw, w: int = 1920, h: int = 1080, brand_color=(59, 130, 246)):
    """Render Notion-style clean dark studio background with subtle precision dot grid and ambient lighting."""
    draw_volumetric_glow(draw, (960, 480), 750, brand_color, 28)
    draw_volumetric_glow(draw, (450, 850), 500, (16, 185, 129), 16)
    draw_volumetric_glow(draw, (1500, 250), 500, (139, 92, 246), 16)

    # Precision dot grid
    dot_color = (255, 255, 255, 14)
    for x in range(40, w, 44):
        for y in range(35, h, 44):
            draw.ellipse([x - 1, y - 1, x + 1, y + 1], fill=dot_color)

def draw_notion_window_shell(
    draw: ImageDraw.Draw,
    x: int,
    y: int,
    w: int,
    h: int,
    title: str,
    breadcrumb: str,
    active_tab: str = "OVERVIEW",
    brand_color=(59, 130, 246),
):
    """Draw Notion-style modular workspace window frame with sidebar and breadcrumbs."""
    # Main window canvas
    draw.rounded_rectangle([x, y, x + w, y + h], radius=18, fill=(13, 16, 22, 250), outline=(255, 255, 255, 25), width=1)

    # Top titlebar
    draw.rounded_rectangle([x, y, x + w, y + 46], radius=18, fill=(18, 22, 30, 255))
    draw.rectangle([x, y + 30, x + w, y + 46], fill=(18, 22, 30, 255))
    draw.line([(x, y + 46), (x + w, y + 46)], fill=(255, 255, 255, 18), width=1)

    # Traffic light dots
    for i, col in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        draw.ellipse([x + 20 + i * 18, y + 17, x + 30 + i * 18, y + 27], fill=col)

    # Notion breadcrumb bar
    crumb_text = f"WORKSPACE  /  {title[:16].upper()}  /  {breadcrumb.upper()}"
    draw.text((x + 95, y + 16), crumb_text, fill=(148, 163, 184), font=get_font(INTER_FONT_PATH, 13))

    # Right pills: Share & Sync
    draw.rounded_rectangle([x + w - 170, y + 12, x + w - 95, y + 34], radius=6, fill=(255, 255, 255, 10))
    draw.text((x + w - 132, y + 16), "✦ SHARE", fill=(203, 213, 225), font=get_font(INTER_FONT_PATH, 11), anchor="mm")
    draw.rounded_rectangle([x + w - 85, y + 12, x + w - 20, y + 34], radius=6, fill=(*brand_color, 40), outline=(*brand_color, 120))
    draw.text((x + w - 52, y + 16), "● LIVE", fill=(255, 255, 255), font=get_font(INTER_FONT_PATH, 11), anchor="mm")

    # Left sidebar (Notion style)
    sb_w = 230
    draw.rectangle([x, y + 47, x + sb_w, y + h - 1], fill=(15, 18, 25, 255))
    draw.line([(x + sb_w, y + 47), (x + sb_w, y + h - 1)], fill=(255, 255, 255, 14), width=1)

    # Workspace branding item in sidebar
    draw.rounded_rectangle([x + 16, y + 62, x + 44, y + 90], radius=6, fill=brand_color)
    draw.text((x + 30, y + 76), title[:1].upper(), fill=(255, 255, 255), font=get_font(BEBAS_FONT_PATH, 20), anchor="mm")
    draw.text((x + 54, y + 68), title[:14].upper(), fill=(255, 255, 255), font=get_font(BEBAS_FONT_PATH, 18))
    draw.text((x + 54, y + 84), "TEAM WORKSPACE", fill=(100, 116, 139), font=get_font(INTER_FONT_PATH, 10))

    # Navigation items
    nav_items = [("OVERVIEW", "🏠"), ("FEATURES", "✦"), ("WORKFLOW", "📋"), ("DOCS & API", "⚡"), ("SETTINGS", "⚙️")]
    for idx, (lbl, icon) in enumerate(nav_items):
        iy = y + 120 + idx * 40
        is_sel = (lbl == active_tab.upper())
        if is_sel:
            draw.rounded_rectangle([x + 12, iy - 4, x + sb_w - 12, iy + 26], radius=6, fill=(*brand_color, 45), outline=(*brand_color, 90))
            draw.text((x + 24, iy + 2), f"{icon}  {lbl}", fill=(255, 255, 255), font=get_font(INTER_FONT_PATH, 13))
        else:
            draw.text((x + 24, iy + 2), f"{icon}  {lbl}", fill=(140, 155, 175), font=get_font(INTER_FONT_PATH, 13))

def draw_notion_cursor_tag(
    draw: ImageDraw.Draw,
    x: int,
    y: int,
    name: str = "Dev • Arnav",
    color=(59, 130, 246),
    click_prog: float = 0.0,
):
    """Draw Notion's signature animated collaboration cursor with a vibrant user name badge."""
    # Expanding click ripple shockwave
    if 0.0 < click_prog < 1.0:
        rip_r = int(click_prog * 45)
        rip_a = int(240 * (1.0 - click_prog))
        draw.ellipse([x - rip_r, y - rip_r, x + rip_r, y + rip_r], outline=(*color, rip_a), width=2)

    # Sleek cursor arrow
    pts = [(x, y), (x + 15, y + 11), (x + 9, y + 13), (x + 14, y + 23), (x + 10, y + 25), (x + 5, y + 14), (x, y + 18)]
    draw.polygon(pts, fill=(255, 255, 255, 255), outline=(15, 23, 42, 230))

    # Name tag pill (Notion multi-user tag)
    tag_x, tag_y = x + 16, y + 16
    font = get_font(INTER_FONT_PATH, 12)
    bbox = draw.textbbox((tag_x, tag_y), name, font=font)
    pw, ph = bbox[2] - bbox[0] + 16, bbox[3] - bbox[1] + 8
    draw.rounded_rectangle([tag_x, tag_y, tag_x + pw, tag_y + ph], radius=6, fill=(*color, 240), outline=(255, 255, 255, 80))
    draw.text((tag_x + 8, tag_y + 4), name, fill=(255, 255, 255), font=font)

def draw_notion_callout_block(
    draw: ImageDraw.Draw,
    x: int,
    y: int,
    w: int,
    h: int,
    icon: str,
    title: str,
    subtitle: str,
    brand_color=(59, 130, 246),
):
    """Draw Notion signature callout box with icon and structured typography."""
    draw.rounded_rectangle([x, y, x + w, y + h], radius=12, fill=(20, 25, 35, 220), outline=(255, 255, 255, 25), width=1)
    draw.rounded_rectangle([x + 16, y + 16, x + 50, y + 50], radius=8, fill=(*brand_color, 45), outline=(*brand_color, 120))
    draw.text((x + 33, y + 33), icon, fill=(255, 255, 255), font=get_font(BEBAS_FONT_PATH, 22), anchor="mm")
    draw.text((x + 64, y + 16), title.upper()[:40], fill=(255, 255, 255), font=get_font(BEBAS_FONT_PATH, 24))
    draw.text((x + 64, y + 42), subtitle[:80], fill=(148, 163, 184), font=get_font(INTER_FONT_PATH, 15))

def draw_notion_modular_card(
    draw: ImageDraw.Draw,
    x: int,
    y: int,
    w: int,
    h: int,
    title: str,
    description: str,
    badge: str = "FEATURE",
    brand_color=(59, 130, 246),
    is_active: bool = False,
):
    """Draw a modular content block card (like a Notion page card or toggle block)."""
    fill_col = (25, 30, 42, 240) if is_active else (18, 22, 30, 220)
    border_col = (*brand_color, 140) if is_active else (255, 255, 255, 22)
    draw.rounded_rectangle([x, y, x + w, y + h], radius=12, fill=fill_col, outline=border_col, width=1)

    # Badge pill
    draw.rounded_rectangle([x + 16, y + 14, x + 96, y + 34], radius=6, fill=(*brand_color, 35), outline=(*brand_color, 100))
    draw.text((x + 56, y + 24), badge.upper(), fill=(147, 197, 253), font=get_font(INTER_FONT_PATH, 11), anchor="mm")

    # Content
    draw.text((x + 16, y + 44), title.upper()[:28], fill=(255, 255, 255), font=get_font(BEBAS_FONT_PATH, 24))
    # Multi-line word wrap for description
    words = description.split()
    lines, cur = [], []
    for w_word in words:
        cur.append(w_word)
        if len(" ".join(cur)) > 32:
            lines.append(" ".join(cur))
            cur = []
    if cur:
        lines.append(" ".join(cur))
    for idx, l in enumerate(lines[:3]):
        draw.text((x + 16, y + 74 + idx * 18), l, fill=(148, 163, 184), font=get_font(INTER_FONT_PATH, 13))

def draw_notion_code_block(draw: ImageDraw.Draw, x: int, y: int, w: int, h: int, code_lines: list[str], lang: str = "TypeScript"):
    """Draw a Notion-style syntax highlighted code block."""
    draw.rounded_rectangle([x, y, x + w, y + h], radius=10, fill=(11, 14, 20, 255), outline=(255, 255, 255, 18), width=1)
    draw.text((x + w - 90, y + 10), lang.upper(), fill=(100, 116, 139), font=get_font(INTER_FONT_PATH, 11))
    for idx, line in enumerate(code_lines[:7]):
        ly = y + 16 + idx * 22
        draw.text((x + 16, ly), f"{idx + 1:2d}", fill=(71, 85, 105), font=get_font(INTER_FONT_PATH, 12))
        color = (147, 197, 253) if "import" in line or "export" in line else ((244, 114, 182) if "const" in line or "await" in line else (226, 232, 240))
        draw.text((x + 46, ly), line, fill=color, font=get_font(INTER_FONT_PATH, 12))

# ==============================================================================
# Legacy Zelios Compatibility Primitives
# ==============================================================================

def create_saas_dashboard(product: str, headline: str, brand_color=(59, 130, 246)) -> Image.Image:
    """Generate high-fidelity SaaS dashboard mockup with navigation, metrics, and charts."""
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
    draw.text((x + 44, y + 12), title.upper()[:30], fill=(255, 255, 255), font=get_font(BEBAS_FONT_PATH, 28))
    draw.text((x + 44, y + 38), subtitle[:50], fill=(148, 163, 184), font=get_font(INTER_FONT_PATH, 16))

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
