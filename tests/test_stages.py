"""Tests for Analyze and Script pipeline stages."""

import pytest
from worker.analyze import build_deterministic_brief, parse_github_owner_repo
from worker.models import ProductBrief
from worker.script import enforce_apple_copy_rules, generate_scene_plan

def test_parse_github_owner_repo():
    """Verify owner/repo extraction from varied GitHub URL patterns."""
    owner, repo = parse_github_owner_repo("https://github.com/facebook/react")
    assert owner == "facebook"
    assert repo == "react"

    owner2, repo2 = parse_github_owner_repo("github.com/torvalds/linux.git")
    assert owner2 == "torvalds"
    assert repo2 == "linux"

def test_enforce_apple_copy_rules():
    """Ensure copy rules truncate words and enforce uppercase styling."""
    res = enforce_apple_copy_rules("this is a very long corporate headline that exceeds the word limit")
    words = res.split()
    assert len(words) <= 6
    assert res == res.upper()

def test_generate_scene_plan():
    """Verify scene plan composition generates 6 scenes with valid transitions."""
    brief = build_deterministic_brief(
        repo_url="https://github.com/acme/rocket",
        live_url="https://rocket.acme.dev",
        data={"package_json": {"description": "Blazing fast cloud engine"}, "routes": ["/", "/dashboard"]},
    )
    plan = generate_scene_plan("job-123", brief, mood="energetic", fps=30)
    assert len(plan.scenes) == 6
    assert plan.total_duration_frames > 400
    scene_types = [s.scene_type for s in plan.scenes]
    assert "TitleReveal" in scene_types
    assert "DeviceShowcase" in scene_types
    assert "StatCounter" in scene_types
    assert "Outro" in scene_types
