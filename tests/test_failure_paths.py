"""Failure path and edge case audit tests."""

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from api.main import app
from api.rate_limit import _ip_requests
from worker.analyze import build_deterministic_brief
from worker.audio import calculate_beat_timestamps, compute_ducking_volume

def test_sparse_repo_fallback_deterministic_brief():
    """Verify empty or sparse repository triggers clean deterministic fallback."""
    brief = build_deterministic_brief(
        repo_url="https://github.com/nonexistent/empty-project",
        live_url="https://empty.dev",
        data={"readme": "", "package_json": {}, "routes": ["/"]},
    )
    assert brief.product_name == "Empty Project"
    assert len(brief.key_features) >= 3
    assert len(brief.tagline.split()) <= 6

def test_beat_quantization_and_ducking():
    """Verify musical bar alignment and narration volume attenuation."""
    beats = calculate_beat_timestamps(bpm=120.0, total_duration_sec=10.0)
    # At 120 BPM, bar interval is 2.0s
    assert 0.0 in beats
    assert 2.0 in beats
    assert 4.0 in beats

    # Ducking under narration: frame 100 within range (90, 150)
    ducked_vol = compute_ducking_volume(100, [(90, 150)], base_volume=0.8)
    assert ducked_vol == 0.2  # 20% volume
    normal_vol = compute_ducking_volume(50, [(90, 150)], base_volume=0.8)
    assert normal_vol == 0.8
