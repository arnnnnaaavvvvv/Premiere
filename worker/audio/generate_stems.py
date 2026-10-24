"""Generate royalty-free audio stems with rhythmic beats for default pipeline audio."""

import os
import wave
import numpy as np

def generate_beat_track(output_wav: str, bpm: float = 128.0, duration_sec: float = 30.0):
    """Generate rhythmic electronic trailer audio stem at specified BPM."""
    sr = 44100
    total_samples = int(sr * duration_sec)
    t = np.linspace(0, duration_sec, total_samples, endpoint=False)
    audio = np.zeros(total_samples, dtype=np.float32)

    beat_interval = 60.0 / bpm
    beats = np.arange(0, duration_sec, beat_interval)

    # 1. Synthesize kick & sub-bass on each downbeat
    for b in beats:
        idx = int(b * sr)
        kick_len = int(0.18 * sr)
        if idx + kick_len < total_samples:
            kt = np.linspace(0, 0.18, kick_len, endpoint=False)
            freq = np.linspace(140, 45, kick_len)
            kick = np.sin(2 * np.pi * freq * kt) * np.exp(-kt * 22)
            audio[idx:idx + kick_len] += kick * 0.7

    # 2. Synthesize arpeggiated ambient synth pad
    pad = 0.15 * np.sin(2 * np.pi * 220.0 * t) + 0.10 * np.sin(2 * np.pi * 330.0 * t)
    audio += pad.astype(np.float32)

    # 3. Master and normalize to standard headroom
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = (audio / max_val) * 0.85

    # 4. Write 16-bit PCM WAV
    audio_int16 = (audio * 32767).astype(np.int16)
    os.makedirs(os.path.dirname(output_wav), exist_ok=True)
    with wave.open(output_wav, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(audio_int16.tobytes())

def generate_all_stems():
    """Synthesize audio files for all three mood tracks."""
    base = os.path.dirname(__file__)
    stems = [
        ("cyber-pulse.wav", 128.0),
        ("ambient-horizon.wav", 100.0),
        ("neon-overdrive.wav", 140.0),
    ]
    for filename, bpm in stems:
        path = os.path.join(base, filename)
        if not os.path.exists(path):
            generate_beat_track(path, bpm, 30.0)

if __name__ == "__main__":
    generate_all_stems()
    print("All audio stems generated successfully.")
