# 08. Audio Pipeline & Beat-Synchronized Engine

## 1. Curated Soundtrack Architecture & License Tracking

Premiere ships with an internal catalogue of high-production-value, royalty-free instrumental stems specifically produced for tech keynote trailers. Every track is pre-indexed with acoustic telemetry and licensing metadata:

```typescript
export interface AudioTrackMetadata {
  id: string;
  name: string;
  mood: "minimal" | "energetic" | "futuristic";
  bpm: number;
  durationSeconds: number;
  timeSignature: [4, 4];
  licenseType: "CC-BY-4.0" | "Royalty-Free-Commercial" | "Custom-Exclusive";
  attribution: string;
  fileUrl: string;
  waveformJsonUrl: string;
  downbeats: number[]; // Array of timestamps (seconds) marking bar beginnings
}
```

### Mood Archetypes
- **Minimal**: Ambient neo-classical synth, subtle sub-bass pulses, 100-110 BPM. Ideal for developer tools, clean APIs, and privacy-focused utilities.
- **Energetic**: High-velocity electro-industrial breaks, punchy kick drums, 126-132 BPM. Ideal for fast SaaS, fintech platforms, and consumer apps.
- **Futuristic**: Cyberpunk arpeggiated synths, heavy bass drops, 138-145 BPM. Ideal for AI agents, robotics, and cryptographic platforms.

---

## 2. Beat Detection & Onset Analysis (`librosa`)

The Audio Worker runs an automated Python pipeline using `librosa` to compute the musical grid:

```python
import librosa
import numpy as np

def analyze_audio_stem(audio_path: str):
    # Load audio stem at 22050 Hz mono
    y, sr = librosa.load(audio_path, sr=22050)

    # Compute onset envelope
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)

    # Estimate tempo (BPM) and beat frames
    tempo, beat_frames = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)

    # Detect downbeats (assuming 4/4 time signature: every 4th beat is a musical measure)
    downbeat_times = beat_times[::4].tolist()

    return {
        "bpm": float(tempo),
        "beat_timestamps": beat_times.tolist(),
        "downbeat_timestamps": downbeat_times
    }
```

---

## 3. Audio Ducking & Narration Sidechain Compression

When narration voiceover is toggled, background music must automatically attenuate smoothly beneath speech to preserve micro-intelligibility while keeping energy high during pauses.

```
Music Vol ^
    1.0   |---------+                               +---------
          |          \                             /
    0.2   |           +---------------------------+
          |           |                           |
          +-----------+---------------------------+------------> Time
                      [ Speech Begins ]           [ Speech Ends ]
                      |<-- 200ms -->|             |<-- 400ms -->|
                        (Attack)                    (Release)
```

### FFmpeg Sidechain Ducking Filter
The worker uses FFmpeg's `sidechaincompress` or `acompressor` filter to master the final audio track:

```bash
ffmpeg -i background_music.mp3 -i narration_voiceover.wav \
  -filter_complex "[0:a][1:a]sidechaincompress=threshold=0.08:ratio=6:attack=200:release=400[ducked_music]; \
  [ducked_music][1:a]amix=inputs=2:weights=1 1.2:normalize=0[mixed]; \
  [mixed]loudnorm=I=-14:LRA=7:tp=-1.5[out]" \
  -map "[out]" -c:a aac -b:a 192k final_mastered_audio.aac
```

### Loudness Normalization
All audio tracks are mastered to **-14 LUFS** ($\pm 1.0\text{ LUFS}$) in accordance with YouTube, Twitter, and web streaming loudness standards.
