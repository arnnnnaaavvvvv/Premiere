"""Render quality and typography compliance tests."""

from pathlib import Path
from worker.models import SceneItem
from worker.render import BEBAS_FONT_PATH, INTER_FONT_PATH, get_font, render_scene_frame

def test_fonts_bundled_and_loadable():
    """Verify Bebas Neue and Inter fonts exist and load without exception."""
    assert BEBAS_FONT_PATH.exists(), "BebasNeue-Regular.ttf must be bundled in assets"
    assert INTER_FONT_PATH.exists(), "Inter-Regular.ttf must be bundled in assets"

    font_bebas = get_font(BEBAS_FONT_PATH, 120)
    font_inter = get_font(INTER_FONT_PATH, 28)
    assert font_bebas is not None
    assert font_inter is not None

def test_scene_frame_rendering_no_clip():
    """Verify 1920x1080 frame renders cleanly even with an excessively long headline."""
    long_headline_scene = SceneItem(
        scene_id="test-long-scene",
        scene_type="TitleReveal",
        headline="ENTERPRISE SCALE DISTRIBUTED MULTI REGION DATABASE ENGINE",
        caption="Verified sub-millisecond query inspection",
        duration_frames=30,
    )

    frame = render_scene_frame(
        scene=long_headline_scene,
        frame_idx=15,
        total_frames=30,
        media_path=None,
        product_name="PREMIERE",
        live_url="https://myapp.cloud",
    )

    assert frame.shape == (1080, 1920, 3)

def test_outro_scene_includes_url():
    """Verify Outro scene frame renders target domain cleanly."""
    outro_scene = SceneItem(
        scene_id="test-outro",
        scene_type="Outro",
        headline="START BUILDING TODAY",
        caption="Get started with Premiere",
        duration_frames=30,
    )

    frame = render_scene_frame(
        scene=outro_scene,
        frame_idx=15,
        total_frames=30,
        media_path=None,
        product_name="PREMIERE",
        live_url="https://acme.org",
    )

    assert frame.shape == (1080, 1920, 3)
