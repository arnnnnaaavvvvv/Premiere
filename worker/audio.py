"""Audio processing module: track selection, beat grid calculation, and narration ducking."""

import json
from pathlib import Path

AUDIO_DIR = Path(__file__).resolve().parent / "audio"
TRACKS_JSON = AUDIO_DIR / "tracks.json"

def get_track_catalog() -> list[dict]:
    """Load metadata list of royalty-free soundtracks."""
    if not TRACKS_JSON.exists():
        return []
    with open(TRACKS_JSON, "r", encoding="utf-8") as f:
        return json.load(f)

def select_track_for_mood(mood: str) -> dict:
    """Find track matching selected mood preset or fall back to energetic default."""
    tracks = get_track_catalog()
    for track in tracks:
        if track["mood"].lower() == mood.lower():
            return track
    return tracks[0] if tracks else {
        "id": "cyber-pulse", "name": "Cyber Pulse", "mood": "energetic",
        "bpm": 128, "beat_interval_sec": 0.46875, "filename": "cyber-pulse.wav"
    }

def calculate_beat_timestamps(bpm: float, total_duration_sec: float) -> list[float]:
    """Compute timestamps of downbeats (every 4 beats) across composition."""
    beat_interval = 60.0 / bpm
    bar_interval = beat_interval * 4.0  # 4/4 measure
    timestamps: list[float] = []
    current = 0.0
    while current <= total_duration_sec:
        timestamps.append(round(current, 3))
        current += bar_interval
    return timestamps

def compute_ducking_volume(current_frame: int, narration_ranges: list[tuple[int, int]], base_volume: float = 0.8) -> float:
    """Attenuate background music volume to 20% during active narration."""
    for start_f, end_f in narration_ranges:
        if start_f <= current_frame <= end_f:
            return round(base_volume * 0.25, 2)  # ~20%
    return base_volume
