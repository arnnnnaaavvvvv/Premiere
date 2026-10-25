"""Zelios & Notion-style video render engine: modular UI blocks, multi-cursor choreography, 3D perspective, and H.264."""

import asyncio
import math
import os
import shutil
import subprocess
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw
from worker.models import ScenePlan
from worker.zelios_fx import (
    BEBAS_FONT_PATH, INTER_FONT_PATH, build_device_mockup, create_saas_dashboard,
    draw_animated_cursor, draw_glass_card, draw_notion_callout_block, draw_notion_code_block,
    draw_notion_cursor_tag, draw_notion_modular_card, draw_notion_studio_background,
    draw_notion_window_shell, draw_tech_grid, draw_volumetric_glow, ease_out_cubic, get_font,
    warp_3d_device,
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
    """Render cinematic Notion-style 1920x1080 explainer frame with modular blocks, multi-cursor choreography, and fluid transitions."""
    canvas = Image.new("RGBA", (1920, 1080), (10, 12, 17, 255))
    draw = ImageDraw.Draw(canvas)
    prog = frame_idx / max(1, total_frames - 1)
    t = ease_out_cubic(prog)

    # 1. Notion Studio Backdrop with subtle precision dot grid and ambient glow
    draw_notion_studio_background(draw, 1920, 1080)
    headline = scene.headline.upper()

    # Window bounds with subtle continuous camera ease
    ww = int(1420 + 20 * t)
    wh = int(790 + 10 * t)
    wx = (1920 - ww) // 2
    wy = (1080 - wh) // 2 + 10

    if scene.scene_type == "TitleReveal":
        # Notion Workspace Hook: One workspace for [product_name]
        draw_notion_window_shell(draw, wx, wy, ww, wh, product_name, "OVERVIEW", "OVERVIEW")

        # Inner canvas content - Tag pill
        draw.rounded_rectangle([wx + 260, wy + 74, wx + 620, wy + 106], radius=16, fill=(255, 255, 255, 10), outline=(255, 255, 255, 25))
        draw.text((wx + 276, wy + 90), "✦ ONE UNIFIED ENGINE FOR MODERN TEAMS", fill=(147, 197, 253), font=get_font(INTER_FONT_PATH, 12), anchor="lm")

        # Project Title (Bebas Neue)
        title_size = int(90 + 6 * t)
        draw.text((wx + 260, wy + 130), f"MEET {product_name.upper()}", fill=(255, 255, 255), font=get_font(BEBAS_FONT_PATH, title_size))

        # Notion Callout Block with extracted concept
        callout_y = wy + 230
        callout_w = ww - 300
        draw_notion_callout_block(
            draw, wx + 260, callout_y, callout_w, 88,
            "💡",
            headline,
            scene.caption,
            brand_color=(59, 130, 246),
        )

        # 3 Modular Overview Block preview pills below callout
        card_w = (callout_w - 32) // 3
        tags = [
            ("⚡ CORE ENGINE", "Sub-millisecond execution pipeline"),
            ("🔒 SECURITY ARCHITECTURE", "Hardened against unauthorized access"),
            ("🌐 PRODUCTION LIVE", f"Deployed at {live_url.replace('https://', '').replace('http://', '')[:16]}"),
        ]
        for idx, (t_title, t_sub) in enumerate(tags):
            cx = wx + 260 + idx * (card_w + 16)
            draw_notion_modular_card(draw, cx, wy + 340, card_w, 150, t_title, t_sub, "MODULE", is_active=(idx == 0))

        # Gliding lead cursor entering the workspace
        cur_x = int(wx + ww - 100 - (1.0 - t) * 320)
        cur_y = int(wy + wh - 100 - (1.0 - t) * 180)
        click_p = max(0.0, (prog - 0.6) / 0.4) if prog > 0.6 else 0.0
        draw_notion_cursor_tag(draw, cur_x, cur_y, "Alex • Lead", (59, 130, 246), click_p)

    elif scene.scene_type == "DeviceShowcase":
        # Notion Modular Block Showcase - Feature 1
        draw_notion_window_shell(draw, wx, wy, ww, wh, product_name, "FEATURES", "FEATURES")

        draw.text((wx + 260, wy + 76), headline, fill=(255, 255, 255), font=get_font(BEBAS_FONT_PATH, 54))
        draw.text((wx + 260, wy + 124), scene.caption[:90], fill=(148, 163, 184), font=get_font(INTER_FONT_PATH, 16))

        # Left side: Modular Code / Architecture block
        code_w = 460
        code_lines = [
            f"import {{ {product_name.replace(' ', '')} }} from '@core'",
            "",
            "// Working feature extracted from GitHub",
            f"const client = new {product_name.replace(' ', '')}()",
            "await client.initialize({",
            f"  feature: '{headline[:18]}',",
            "  telemetry: 'sub-millisecond'",
            "})",
        ]
        draw_notion_code_block(draw, wx + 260, wy + 160, code_w, 205, code_lines, "TypeScript")

        # Expandable Toggle Block
        draw.rounded_rectangle([wx + 260, wy + 380, wx + 260 + code_w, wy + 450], radius=10, fill=(20, 25, 36, 240), outline=(59, 130, 246, 120))
        draw.text((wx + 280, wy + 400), "▶  LIVE FEATURE SPECIFICATION", fill=(255, 255, 255), font=get_font(BEBAS_FONT_PATH, 20))
        draw.text((wx + 280, wy + 424), "Sub-millisecond execution with zero downtime", fill=(148, 163, 184), font=get_font(INTER_FONT_PATH, 13))

        # Right side: Live Browser screen or High-Fidelity UI Mockup
        right_x = wx + 260 + code_w + 30
        right_w = ww - 260 - code_w - 50
        right_h = 440

        screen = Image.open(media_path) if media_path and os.path.exists(media_path) else None
        if screen is None or np.array(screen).std() < 12.0:
            screen = create_saas_dashboard(product_name, headline)

        mockup = build_device_mockup(screen, product=product_name, headline=headline, w=right_w, h=right_h)
        canvas.paste(mockup, (right_x, wy + 160), mockup)
        draw = ImageDraw.Draw(canvas)

        # Cursor clicking toggle
        cur_x = int(wx + 260 + code_w - 40 * (1.0 - t))
        cur_y = int(wy + 415)
        click_p = max(0.0, (prog - 0.5) / 0.5) if prog > 0.5 else 0.0
        draw_notion_cursor_tag(draw, cur_x, cur_y, "Dev • Arnav", (16, 185, 129), click_p)

    elif scene.scene_type == "FeatureZoom":
        # Notion 3-Column Kanban Board / Database - Feature 2
        draw_notion_window_shell(draw, wx, wy, ww, wh, product_name, "WORKFLOW", "WORKFLOW")

        draw.text((wx + 260, wy + 76), headline, fill=(255, 255, 255), font=get_font(BEBAS_FONT_PATH, 54))
        draw.text((wx + 260, wy + 124), scene.caption[:90], fill=(148, 163, 184), font=get_font(INTER_FONT_PATH, 16))

        # 3 Kanban Columns (Notion style)
        board_x = wx + 260
        board_y = wy + 160
        total_bw = ww - 300
        col_w = (total_bw - 40) // 3
        col_h = 440

        cols = [
            ("1. INPUT & DISCOVERY", (100, 116, 139)),
            ("2. IN PIPELINE", (59, 130, 246)),
            ("3. PRODUCTION LIVE", (16, 185, 129)),
        ]

        for i, (col_name, col_accent) in enumerate(cols):
            cx = board_x + i * (col_w + 20)
            draw.rounded_rectangle([cx, board_y, cx + col_w, board_y + col_h], radius=12, fill=(15, 18, 26, 240), outline=(255, 255, 255, 20))
            draw.text((cx + 16, board_y + 16), col_name, fill=col_accent, font=get_font(BEBAS_FONT_PATH, 20))

            if i == 0:
                draw_notion_modular_card(draw, cx + 12, board_y + 55, col_w - 24, 110, "GITHUB REPOSITORY", "Main branch AST validated", "SYNCED")
                draw_notion_modular_card(draw, cx + 12, board_y + 180, col_w - 24, 110, "API ROUTE SPEC", "Routes & endpoints mapped", "READY")
            elif i == 1:
                # Active card that moves with prog
                offset_x = int((col_w + 20) * t) if prog > 0.3 else 0
                card_x = cx + 12 + offset_x
                draw_notion_modular_card(draw, card_x, board_y + 55, col_w - 24, 110, headline[:20], scene.caption[:45], "ACTIVE", is_active=True)
                draw_notion_modular_card(draw, cx + 12, board_y + 180, col_w - 24, 110, "REAL-TIME LOGS", "Sub-second event stream", "STREAM")
            else:
                draw_notion_modular_card(draw, cx + 12, board_y + 180, col_w - 24, 110, f"{product_name.upper()} ENGINE", "Production edge distribution", "LIVE")

        # Cursor dragging the card across columns
        cur_drag_x = int(board_x + col_w + 50 + (col_w + 20) * t)
        cur_drag_y = board_y + 100
        draw_notion_cursor_tag(draw, cur_drag_x, cur_drag_y, "Sarah • Product", (244, 114, 182), click_prog=0.5)

    elif scene.scene_type in ("StatCounter", "KineticText"):
        if scene.scene_type == "KineticText":
            # Multi-User Real-Time Collaboration Scene
            draw_notion_window_shell(draw, wx, wy, ww, wh, product_name, "DOCS & API", "DOCS & API")

            draw.text((wx + 260, wy + 76), "REAL-TIME TEAM COLLABORATION", fill=(147, 197, 253), font=get_font(INTER_FONT_PATH, 14))
            draw.text((wx + 260, wy + 110), headline, fill=(255, 255, 255), font=get_font(BEBAS_FONT_PATH, 64))

            doc_x = wx + 260
            doc_y = wy + 200
            doc_w = ww - 300
            doc_h = 380
            draw.rounded_rectangle([doc_x, doc_y, doc_x + doc_w, doc_y + doc_h], radius=14, fill=(16, 20, 28, 240), outline=(255, 255, 255, 24))

            draw.text((doc_x + 30, doc_y + 30), f"📄  {product_name.upper()} ARCHITECTURE & SPECIFICATION", fill=(255, 255, 255), font=get_font(BEBAS_FONT_PATH, 32))
            draw.line([(doc_x + 30, doc_y + 75), (doc_x + doc_w - 30, doc_y + 75)], fill=(255, 255, 255, 18), width=1)

            full_text = f"Built with {product_name} for uncompromising speed, modular building blocks, and team scale."
            chars_to_show = int(len(full_text) * min(1.0, prog * 1.3))
            typed = full_text[:chars_to_show]
            draw.text((doc_x + 30, doc_y + 105), typed, fill=(226, 232, 240), font=get_font(INTER_FONT_PATH, 18))

            # 3 Named Cursors actively collaborating in real time
            font_inter = get_font(INTER_FONT_PATH, 18)
            t_box = draw.textbbox((doc_x + 30, doc_y + 105), typed, font=font_inter)
            c1_x = min(doc_x + doc_w - 120, t_box[2] + 4)
            c1_y = doc_y + 105
            draw_notion_cursor_tag(draw, c1_x, c1_y, "Alex • Lead", (59, 130, 246), click_prog=0.3 if prog > 0.5 else 0.0)

            c2_x = doc_x + 200 + int(math.sin(t * 3.14) * 60)
            c2_y = doc_y + 240
            draw_notion_cursor_tag(draw, c2_x, c2_y, "Arnav • Core", (16, 185, 129), click_prog=0.0)

            c3_x = doc_x + doc_w - 220
            c3_y = doc_y + 220 + int(math.cos(t * 3.14) * 40)
            draw_notion_cursor_tag(draw, c3_x, c3_y, "AI • Engine", (168, 85, 247), click_prog=0.4 if prog > 0.6 else 0.0)

        else:
            # StatCounter Scene (Quantitative Metrics & Benchmarks)
            draw_notion_window_shell(draw, wx, wy, ww, wh, product_name, "OVERVIEW", "OVERVIEW")

            draw.text((wx + 260, wy + 76), headline, fill=(255, 255, 255), font=get_font(BEBAS_FONT_PATH, 54))
            draw.text((wx + 260, wy + 124), scene.caption[:90], fill=(148, 163, 184), font=get_font(INTER_FONT_PATH, 16))

            card_x = wx + 260
            card_y = wy + 170
            total_cw = ww - 300
            mc_w = (total_cw - 32) // 3
            mc_h = 240

            stats = [
                ("10X", "EXECUTION VELOCITY", "Sub-second turnaround across pipelines", (59, 130, 246)),
                ("99.9%", "SYSTEM RELIABILITY", "Zero-downtime distributed architecture", (16, 185, 129)),
                ("<5MS", "QUERY LATENCY", "High-throughput asynchronous event loop", (245, 158, 11)),
            ]

            for idx, (m_val, m_lbl, m_desc, m_col) in enumerate(stats):
                cx = card_x + idx * (mc_w + 16)
                draw.rounded_rectangle([cx, card_y, cx + mc_w, card_y + mc_h], radius=14, fill=(18, 22, 32, 240), outline=(255, 255, 255, 25))
                draw.text((cx + 24, card_y + 24), m_lbl, fill=m_col, font=get_font(INTER_FONT_PATH, 13))
                draw.text((cx + 24, card_y + 54), m_val, fill=(255, 255, 255), font=get_font(BEBAS_FONT_PATH, 76))
                draw.text((cx + 24, card_y + 140), m_desc, fill=(148, 163, 184), font=get_font(INTER_FONT_PATH, 13))

                bar_w = mc_w - 48
                draw.rounded_rectangle([cx + 24, card_y + 190, cx + 24 + bar_w, card_y + 200], radius=5, fill=(255, 255, 255, 15))
                fill_w = int(bar_w * t)
                if fill_w > 0:
                    draw.rounded_rectangle([cx + 24, card_y + 190, cx + 24 + fill_w, card_y + 200], radius=5, fill=m_col)

            draw_notion_cursor_tag(draw, card_x + mc_w - 40, card_y + 120, "Lead • Architect", (59, 130, 246), click_prog=0.0)

    elif scene.scene_type == "Outro":
        # Notion Outro: Full workspace framing + Actionable Call to Action
        draw_notion_window_shell(draw, wx, wy, ww, wh, product_name, "START BUILDING", "OVERVIEW")

        cta_cx = wx + 230 + (ww - 230) // 2

        draw.text((cta_cx, wy + 140), headline, fill=(255, 255, 255), font=get_font(BEBAS_FONT_PATH, 76), anchor="mm")
        draw.text((cta_cx, wy + 210), f"Experience the future of {product_name.lower()}", fill=(148, 163, 184), font=get_font(INTER_FONT_PATH, 20), anchor="mm")

        btn_w, btn_h = 360, 68
        btn_x, btn_y = cta_cx - btn_w // 2, wy + 270
        draw.rounded_rectangle([btn_x, btn_y, btn_x + btn_w, btn_y + btn_h], radius=12, fill=(59, 130, 246, 255))
        draw.text((cta_cx, btn_y + btn_h // 2), "GET STARTED NOW", fill=(255, 255, 255), font=get_font(BEBAS_FONT_PATH, 32), anchor="mm")

        clean_url = live_url.replace("https://", "").replace("http://", "").rstrip("/")
        pill_text = f"🌐  {clean_url.upper()}"
        pill_w = 400
        pill_x = cta_cx - pill_w // 2
        draw.rounded_rectangle([pill_x, wy + 370, pill_x + pill_w, wy + 414], radius=8, fill=(255, 255, 255, 10), outline=(255, 255, 255, 25))
        draw.text((cta_cx, wy + 392), pill_text, fill=(203, 213, 225), font=get_font(INTER_FONT_PATH, 14), anchor="mm")

        cur_x = int(cta_cx + 40 - (1.0 - t) * 120)
        cur_y = int(btn_y + btn_h // 2 + 10)
        click_p = max(0.0, (prog - 0.6) / 0.4) if prog > 0.6 else 0.0
        draw_notion_cursor_tag(draw, cur_x, cur_y, "Dev • Arnav", (16, 185, 129), click_prog=click_p)

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
                if f % 5 == 0:
                    await asyncio.sleep(0.001)
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
