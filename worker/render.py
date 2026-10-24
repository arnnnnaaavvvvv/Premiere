"""Video render stage: compiles ScenePlan and captured assets into 1080p MP4."""

import json
import os
import subprocess
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from api.config import settings
from worker.models import ScenePlan

def render_scene_frame(
    scene,
    frame_idx: int,
    total_scene_frames: int,
    media_path: str | None,
    product_name: str,
    brand_color: tuple[int, int, int] = (59, 130, 246),
) -> np.ndarray:
    """Generate a single 1920x1080 frame adhering to Apple/Nike dark aesthetic."""
    img = Image.new("RGB", (1920, 1080), color=(5, 5, 5))
    draw = ImageDraw.Draw(img)

    # 1. Atmospheric Diffuse Ambient Radial Glow
    glow_overlay = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_overlay)
    glow_draw.ellipse([460, 100, 1460, 800], fill=(*brand_color, 30))
    img.paste(glow_overlay, (0, 0), glow_overlay)

    # 2. Render Scene Typography & Layout
    t = frame_idx / max(total_scene_frames, 1)
    scale = 0.95 + 0.05 * min(t * 3.0, 1.0)
    font_size = int(120 * scale)

    try:
        font = ImageFont.truetype("arialbd.ttf", font_size)
        sub_font = ImageFont.truetype("arial.ttf", 32)
    except Exception:
        font = ImageFont.load_default()
        sub_font = ImageFont.load_default()

    headline = scene.headline.upper()
    caption = scene.caption

    if scene.scene_type in ("TitleReveal", "StatCounter", "KineticText", "Outro"):
        draw.text((960, 480), headline, fill=(255, 255, 255), font=font, anchor="mm")
        draw.text((960, 580), caption, fill=(148, 163, 184), font=sub_font, anchor="mm")
    elif scene.scene_type == "DeviceShowcase":
        draw.text((960, 160), headline, fill=(255, 255, 255), font=font, anchor="mm")
        # Draw 3D Mockup Device Frame
        if media_path and os.path.exists(media_path):
            try:
                screen = Image.open(media_path).resize((1300, 720))
                img.paste(screen, (310, 260))
            except Exception:
                pass
        draw.rectangle([308, 258, 1612, 982], outline=(*brand_color, 120), width=3)
    elif scene.scene_type == "FeatureZoom":
        if media_path and os.path.exists(media_path):
            try:
                screen = Image.open(media_path).resize((1920, 1080))
                img.paste(screen, (0, 0))
            except Exception:
                pass
        draw.rectangle([100, 720, 800, 980], fill=(13, 15, 20), outline=(255, 255, 255), width=1)
        draw.text((450, 800), headline, fill=(255, 255, 255), font=font, anchor="mm")
        draw.text((450, 880), caption, fill=(148, 163, 184), font=sub_font, anchor="mm")

    # 3. Vignette Border
    frame_np = np.array(img)
    return cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)

async def render_video(
    job_id: str,
    plan: ScenePlan,
    asset_paths: dict[str, str],
    product_name: str,
    output_dir: Path,
) -> str:
    """Stitch beat-aligned scenes into final 1080p MP4."""
    os.makedirs(output_dir, exist_ok=True)
    mp4_path = output_dir / f"launch-{job_id}.mp4"

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(mp4_path), fourcc, 30.0, (1920, 1080))

    try:
        for scene in plan.scenes:
            media = asset_paths.get(scene.scene_id)
            for f in range(scene.duration_frames):
                frame_bgr = render_scene_frame(
                    scene=scene,
                    frame_idx=f,
                    total_scene_frames=scene.duration_frames,
                    media_path=media,
                    product_name=product_name,
                )
                out.write(frame_bgr)
    finally:
        out.release()

    return str(mp4_path)
