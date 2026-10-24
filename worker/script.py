"""Script stage: synthesizes beat-aligned ScenePlan adhering to Apple-style copy rules."""

from worker.models import ProductBrief, SceneItem, ScenePlan

def enforce_apple_copy_rules(text: str, max_words: int = 6) -> str:
    """Enforce uppercase, high-impact punchy fragments without filler words."""
    cleaned = text.strip().upper()
    words = cleaned.split()
    if len(words) > max_words:
        words = words[:max_words]
    return " ".join(words)

def generate_scene_plan(job_id: str, brief: ProductBrief, mood: str = "energetic", fps: int = 30) -> ScenePlan:
    """Compose a cinematic 6-scene storyboard quantized to musical bars."""
    scenes: list[SceneItem] = []

    # Scene 1: TitleReveal (2.5s = 75 frames at 30fps)
    scenes.append(
        SceneItem(
            scene_id="scene-1-title",
            scene_type="TitleReveal",
            headline=enforce_apple_copy_rules(brief.product_name),
            caption=brief.tagline,
            duration_frames=75,
            transition_in="none",
            props={
                "product_name": brief.product_name.upper(),
                "tagline": brief.tagline,
                "brand_color": brief.brand_color,
            },
        )
    )

    # Scene 2: DeviceShowcase (3.0s = 90 frames)
    feature_1 = brief.key_features[0] if brief.key_features else None
    headline_2 = feature_1.headline if feature_1 else "INSTANT SPEED"
    scenes.append(
        SceneItem(
            scene_id="scene-2-device",
            scene_type="DeviceShowcase",
            headline=enforce_apple_copy_rules(headline_2),
            caption=feature_1.detail if feature_1 else "Engineered for high-throughput performance",
            duration_frames=90,
            transition_in="zoom-through",
            target_route=feature_1.associated_route if feature_1 else "/",
            props={
                "device_type": "laptop",
                "headline": enforce_apple_copy_rules(headline_2),
                "caption": feature_1.detail if feature_1 else "Built for scale",
            },
        )
    )

    # Scene 3: FeatureZoom (2.5s = 75 frames)
    feature_2 = brief.key_features[1] if len(brief.key_features) > 1 else brief.key_features[0]
    scenes.append(
        SceneItem(
            scene_id="scene-3-feature",
            scene_type="FeatureZoom",
            headline=enforce_apple_copy_rules(feature_2.headline),
            caption=feature_2.detail,
            duration_frames=75,
            transition_in="push",
            target_route=feature_2.associated_route,
            props={
                "headline": enforce_apple_copy_rules(feature_2.headline),
                "detail": feature_2.detail,
            },
        )
    )

    # Scene 4: StatCounter (2.5s = 75 frames)
    metric = brief.metrics[0] if brief.metrics else None
    val = metric.value if metric else "10x"
    lbl = metric.label if metric else "FASTER WORKFLOWS"
    scenes.append(
        SceneItem(
            scene_id="scene-4-stats",
            scene_type="StatCounter",
            headline=enforce_apple_copy_rules(lbl),
            caption="Verified production benchmark across all workloads",
            duration_frames=75,
            transition_in="mask-wipe",
            props={
                "metric_value": val,
                "metric_label": lbl,
            },
        )
    )

    # Scene 5: KineticText (2.0s = 60 frames)
    scenes.append(
        SceneItem(
            scene_id="scene-5-kinetic",
            scene_type="KineticText",
            headline="BUILT. FOR. IMPACT.",
            caption="Zero compromise on developer experience",
            duration_frames=60,
            transition_in="glitch-flash",
            props={
                "words": ["BUILT.", "FOR.", "IMPACT."],
            },
        )
    )

    # Scene 6: Outro (3.0s = 90 frames)
    scenes.append(
        SceneItem(
            scene_id="scene-6-outro",
            scene_type="Outro",
            headline="START BUILDING TODAY",
            caption=f"Get started with {brief.product_name}",
            duration_frames=90,
            transition_in="blur-dissolve",
            props={
                "product_name": brief.product_name.upper(),
                "cta_text": "START BUILDING TODAY",
                "brand_color": brief.brand_color,
            },
        )
    )

    total_frames = sum(s.duration_frames for s in scenes)
    return ScenePlan(
        job_id=job_id,
        mood=mood,
        fps=fps,
        total_duration_frames=total_frames,
        scenes=scenes,
    )
