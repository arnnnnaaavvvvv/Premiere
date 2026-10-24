"""Video render engine: compiles ScenePlan, Bebas Neue typography, safe margins, and audio muxing."""

import os
import shutil
import subprocess
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from worker.models import ScenePlan

FONTS_DIR = Path(__file__).resolve().parent / "assets" / "fonts"
BEBAS_FONT_PATH = FONTS_DIR / "BebasNeue-Regular.ttf"
INTER_FONT_PATH = FONTS_DIR / "Inter-Regular.ttf"

def get_font(font_path: Path, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load bundled TrueType font or fall back to system sans-serif."""
    if font_path.exists():
        try:
            return ImageFont.truetype(str(font_path), size)
        except Exception:
            pass
    try:
        return ImageFont.truetype("arialbd.ttf" if "Bebas" in font_path.name else "arial.ttf", size)
    except Exception:
        return ImageFont.load_default()

def draw_safe_text(draw: ImageDraw.ImageDraw, text: str, y: int, max_w: int, base_size: int, font_path: Path, fill=(255, 255, 255)):
    """Draw centered text with dynamic scaling to prevent horizontal overflow."""
    size = base_size
    font = get_font(font_path, size)
    bbox = draw.textbbox((0, 0), text, font=font)
    while (bbox[2] - bbox[0]) > max_w and size > 24:
        size -= 4
        font = get_font(font_path, size)
        bbox = draw.textbbox((0, 0), text, font=font)
    draw.text((960, y), text, fill=fill, font=font, anchor="mm")

def render_scene_frame(scene, frame_idx: int, total_frames: int, media_path: str | None, product_name: str, live_url: str = "premiere.dev", brand_color: tuple[int, int, int] = (59, 130, 246)) -> np.ndarray:
    """Render 1920x1080 frame with Bebas Neue typography, safe margins, and glow."""
    img = Image.new("RGB", (1920, 1080), color=(5, 5, 5))
    draw = ImageDraw.Draw(img)

    glow = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([460, 120, 1460, 780], fill=(*brand_color, 28))
    img.paste(glow, (0, 0), glow)

    max_safe_width = 1680
    headline = scene.headline.upper()

    if scene.scene_type in ("TitleReveal", "StatCounter", "KineticText"):
        draw_safe_text(draw, headline, 480, max_safe_width, 140, BEBAS_FONT_PATH)
        draw_safe_text(draw, scene.caption, 590, max_safe_width, 28, INTER_FONT_PATH, (148, 163, 184))
    elif scene.scene_type == "DeviceShowcase":
        draw_safe_text(draw, headline, 160, max_safe_width, 84, BEBAS_FONT_PATH)
        if media_path and os.path.exists(media_path):
            try:
                img.paste(Image.open(media_path).resize((1300, 720)), (310, 240))
            except Exception:
                pass
        draw.rectangle([308, 238, 1612, 962], outline=(*brand_color, 140), width=3)
    elif scene.scene_type == "FeatureZoom":
        if media_path and os.path.exists(media_path):
            try:
                img.paste(Image.open(media_path).resize((1920, 1080)), (0, 0))
            except Exception:
                pass
        draw.rectangle([120, 700, 840, 960], fill=(13, 15, 20), outline=(255, 255, 255, 80), width=1)
        draw_safe_text(draw, headline, 780, 680, 64, BEBAS_FONT_PATH)
        draw_safe_text(draw, scene.caption, 860, 680, 22, INTER_FONT_PATH, (148, 163, 184))
    elif scene.scene_type == "Outro":
        draw_safe_text(draw, headline, 420, max_safe_width, 130, BEBAS_FONT_PATH)
        draw.rectangle([740, 520, 1180, 600], fill=brand_color)
        draw_safe_text(draw, "GET STARTED NOW", 560, 400, 36, BEBAS_FONT_PATH)
        clean_url = live_url.replace("https://", "").replace("http://", "").rstrip("/")
        draw_safe_text(draw, clean_url.upper(), 660, max_safe_width, 26, INTER_FONT_PATH, (148, 163, 184))

    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

def find_ffmpeg_bin() -> str | None:
    """Detect available FFmpeg executable from system or Playwright cache."""
    if shutil.which("ffmpeg"):
        return "ffmpeg"
    playwright_dir = os.path.expanduser(r"~\AppData\Local\ms-playwright")
    if os.path.exists(playwright_dir):
        for root, _, files in os.walk(playwright_dir):
            for f in files:
                if f.lower().startswith("ffmpeg") and f.lower().endswith(".exe"):
                    return os.path.join(root, f)
    return None

async def render_video(job_id: str, plan: ScenePlan, asset_paths: dict[str, str], product_name: str, output_dir: Path, live_url: str = "premiere.dev") -> str:
    """Stitch beat-aligned scenes into 1080p MP4 and mux audio if available."""
    os.makedirs(output_dir, exist_ok=True)
    raw_path = output_dir / f"raw-{job_id}.mp4"
    final_path = output_dir / f"launch-{job_id}.mp4"

    out = cv2.VideoWriter(str(raw_path), cv2.VideoWriter_fourcc(*"mp4v"), 30.0, (1920, 1080))
    try:
        for scene in plan.scenes:
            media = asset_paths.get(scene.scene_id)
            for f in range(scene.duration_frames):
                out.write(render_scene_frame(scene, f, scene.duration_frames, media, product_name, live_url))
    finally:
        out.release()

    ffmpeg, audio_wav = find_ffmpeg_bin(), Path(__file__).resolve().parent / "audio" / "cyber-pulse.wav"
    if ffmpeg and audio_wav.exists():
        cmd = [ffmpeg, "-y", "-i", str(raw_path), "-i", str(audio_wav), "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(final_path)]
        try:
            res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
            if res.returncode == 0 and os.path.exists(final_path):
                try:
                    os.remove(raw_path)
                except Exception:
                    pass
                return str(final_path)
        except (subprocess.TimeoutExpired, Exception):
            pass

    return str(raw_path)
