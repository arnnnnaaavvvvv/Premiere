"""Pydantic schemas for LLM product intelligence and beat-aligned scene planning."""

from typing import Literal
from pydantic import BaseModel, Field

class FeatureItem(BaseModel):
    """Core product capability distilled from codebase."""
    headline: str = Field(description="Max 4 punchy uppercase words")
    detail: str = Field(description="Clear explanation of the feature benefit")
    associated_route: str = Field(default="/", description="Relevant route or UI selector")

class MetricItem(BaseModel):
    """Quantitative performance indicator or differentiator."""
    value: str = Field(description="e.g. 10x, 99.9%, <5ms")
    label: str = Field(description="Context in uppercase e.g. FASTER BUILDS")

class ProductBrief(BaseModel):
    """Structured intelligence extracted from GitHub repo and live website."""
    product_name: str
    tagline: str = Field(description="Punchy uppercase tagline (max 6 words)")
    elevator_pitch: str
    primary_audience: str
    category: str = "Developer Tool"
    key_features: list[FeatureItem] = Field(min_length=3, max_length=5)
    metrics: list[MetricItem] = Field(default_factory=list)
    detected_routes: list[str] = Field(default_factory=lambda: ["/"])
    brand_color: str = "#3B82F6"

SceneType = Literal[
    "TitleReveal",
    "DeviceShowcase",
    "FeatureZoom",
    "StatCounter",
    "KineticText",
    "Outro",
]

TransitionType = Literal[
    "none",
    "push",
    "zoom-through",
    "mask-wipe",
    "blur-dissolve",
    "glitch-flash",
    "shared-element-morph",
]

class SceneItem(BaseModel):
    """Individual cinematic scene specification."""
    scene_id: str
    scene_type: SceneType
    headline: str = Field(description="Max 6 words, Apple-style uppercase punchy fragment")
    caption: str = Field(description="Inter micro-caption")
    duration_frames: int = Field(default=90, description="Duration in frames at 30fps (60-120 frames)")
    transition_in: TransitionType = "push"
    target_route: str = "/"
    props: dict = Field(default_factory=dict)

class ScenePlan(BaseModel):
    """Beat-aligned sequence of cinematic scenes for Remotion rendering."""
    job_id: str
    mood: str
    fps: int = 30
    total_duration_frames: int
    scenes: list[SceneItem]
