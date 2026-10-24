"""Zelios-style video render engine: 3D perspective UI, glassmorphism, cursor choreography, and H.264."""

import os
import shutil
import subprocess
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw
from worker.models import ScenePlan
from worker.zelios_fx import (
    BEBAS_FONT_PATH, INTER_FONT_PATH, build_device_mockup, draw_animated_cursor,
    draw_glass_card, draw_tech_grid, draw_volumetric_glow, ease_out_cubic, get_font, warp_3d_device,
)

def draw_safe_text(draw: ImageDraw.ImageDraw, text: str, y: int, max_w: int, base_size: int, font_path: Path, fill=(255, 255, 255)):
    """Draw centered text with dynamic scaling to fit within canvas margins."""
    clean = "".join(c for c in text if 32 <= ord(c) <= 126 or ord(c) >= 160)
    size = base_size
    font = get_font(font_path, size)
    bbox = draw.textbbox((0, 0), clean, font=font)
    while (bbox[2] - bbox[0]) > max_w and size > 20:
        size -= 4
        font = get_font(font_path, size)
        bbox = draw.textbbox((0, 0), clean, font=font)
    draw.text((960, y), clean, fill=fill, font=font, anchor="mm")

def render_scene_frame(scene, frame_idx: int, total_frames: int, media_path: str | None, product_name: str, live_url: str = "premiere.dev") -> np.ndarray:
    """Render cinematic Zelios-style 1920x1080 frame with 3D perspective and glassmorphism."""
    canvas = Image.new("RGBA", (1920, 1080), (7, 9, 14, 255))
    draw = ImageDraw.Draw(canvas)
    prog = frame_idx / max(1, total_frames - 1)
    t = ease_out_cubic(prog)

    draw_tech_grid(draw, 1920, 1080)
    draw_volumetric_glow(draw, (960, 520), 600, (59, 130, 246), 40)
    headline = scene.headline.upper()

    if scene.scene_type == "TitleReveal":
        draw.rounded_rectangle([800, 360, 1120, 396], radius=18, fill=(15, 20, 28, 200), outline=(255, 255, 255, 40))
        draw.text((960, 378), "NEXT-GEN PLATFORM", fill=(148, 163, 184), font=get_font(INTER_FONT_PATH, 16), anchor="mm")
        draw_safe_text(draw, headline, 490, 1600, int(130 + 10 * t), BEBAS_FONT_PATH)
        draw_safe_text(draw, scene.caption, 590, 1400, 26, INTER_FONT_PATH, (148, 163, 184))

    elif scene.scene_type == "DeviceShowcase":
        draw_safe_text(draw, headline, 130, 1600, 80, BEBAS_FONT_PATH)
        screen = Image.open(media_path) if media_path and os.path.exists(media_path) else Image.new("RGB", (1280, 720), (20, 24, 33))
        mockup = build_device_mockup(screen, product=product_name, headline=headline)
        drift = int(15 * (1.0 - t))
        dst_pts = np.float32([[380 - drift, 260], [1540 + drift, 190], [1460 + drift, 890], [330 - drift, 860]])
        warped = warp_3d_device(mockup, dst_pts)
        c_np = np.array(canvas)
        mask = warped[:, :, 3] > 0
        c_np[mask] = cv2.addWeighted(c_np[mask], 0.1, warped[mask], 0.9, 0)
        canvas = Image.fromarray(c_np)
        draw = ImageDraw.Draw(canvas)
        draw_glass_card(draw, 180, 240, 380, 72, "HIGH THROUGHPUT", "Sub-millisecond API response", (16, 185, 129))
        draw_glass_card(draw, 1360, 740, 380, 72, "ZERO CONFIG", "Automated cloud orchestration", (59, 130, 246))
        draw_animated_cursor(draw, (550, 750), (960, 520), prog)

    elif scene.scene_type == "FeatureZoom":
        screen = Image.open(media_path) if media_path and os.path.exists(media_path) else Image.new("RGB", (1280, 720), (20, 24, 33))
        if np.array(screen).std() < 12.0:
            from worker.zelios_fx import create_saas_dashboard
            screen = create_saas_dashboard(product_name, headline)
        zoom = 1.05 + 0.15 * t
        zw, zh = int(1920 * zoom), int(1080 * zoom)
        scaled = screen.resize((zw, zh), Image.Resampling.LANCZOS)
        ox, oy = (zw - 1920) // 2, (zh - 1080) // 2
        canvas.paste(scaled.crop((ox, oy, ox + 1920, oy + 1080)), (0, 0))
        dim = Image.new("RGBA", (1920, 1080), (7, 9, 14, 180))
        canvas.paste(dim, (0, 0), dim)
        draw = ImageDraw.Draw(canvas)
        draw_glass_card(draw, 140, 760, 720, 140, headline, scene.caption, (59, 130, 246))

    elif scene.scene_type in ("StatCounter", "KineticText"):
        draw_safe_text(draw, headline, 480, 1600, int(150 + 20 * t), BEBAS_FONT_PATH)
        draw_safe_text(draw, scene.caption, 590, 1400, 28, INTER_FONT_PATH, (148, 163, 184))

    elif scene.scene_type == "Outro":
        draw_safe_text(draw, headline, 400, 1600, 120, BEBAS_FONT_PATH)
        draw.rounded_rectangle([720, 500, 1200, 580], radius=16, fill=(59, 130, 246, 255))
        draw_safe_text(draw, "GET STARTED NOW", 540, 400, 36, BEBAS_FONT_PATH)
        clean_url = live_url.replace("https://", "").replace("http://", "").rstrip("/")
        draw_safe_text(draw, clean_url.upper(), 650, 1600, 26, INTER_FONT_PATH, (148, 163, 184))

    return cv2.cvtColor(np.array(canvas.convert("RGB")), cv2.COLOR_RGB2BGR)

def find_ffmpeg_bin() -> str | None:
    """Detect available FFmpeg executable from system, imageio_ffmpeg, or environment."""
    if shutil.which("ffmpeg"):
        return "ffmpeg"
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None

async def render_video(job_id: str, plan: ScenePlan, asset_paths: dict[str, str], product: str, out_dir: Path, live_url: str = "premiere.dev", audio_track_filename: str = "cyber-pulse.wav") -> str:
    """Stitch beat-aligned scenes into browser-compatible H.264 MP4 with faststart and AAC audio."""
    os.makedirs(out_dir, exist_ok=True)
    raw_path, final_path = out_dir / f"raw-{job_id}.mp4", out_dir / f"launch-{job_id}.mp4"
    out = cv2.VideoWriter(str(raw_path), cv2.VideoWriter_fourcc(*"mp4v"), 30.0, (1920, 1080))
    try:
        for scene in plan.scenes:
            media = asset_paths.get(scene.scene_id)
            for f in range(scene.duration_frames):
                out.write(render_scene_frame(scene, f, scene.duration_frames, media, product, live_url))
    finally:
        out.release()

    ffmpeg = find_ffmpeg_bin()
    audio_wav = Path(__file__).resolve().parent / "audio" / audio_track_filename
    if not audio_wav.exists():
        audio_wav = Path(__file__).resolve().parent / "audio" / "cyber-pulse.wav"

    if ffmpeg:
        cmd = [ffmpeg, "-y", "-i", str(raw_path)]
        if audio_wav.exists():
            cmd += ["-i", str(audio_wav), "-c:a", "aac", "-b:a", "192k", "-shortest"]
        cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(final_path)]
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
        if res.returncode == 0 and os.path.exists(final_path):
            try:
                os.remove(raw_path)
            except Exception:
                pass
            return str(final_path)

    return str(raw_path)
