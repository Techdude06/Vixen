#!/usr/bin/env python3
"""
BeatNet-based beat detection for The Greatest Show MP3.

Uses BeatNet (https://github.com/mjhydri/BeatNet) for real-time beat tracking
which is more accurate for drum beat detection.
"""

# Monkey-patch numpy for compatibility with older code
import numpy as np
np.float = np.float64
np.int = np.int64

from BeatNet.BeatNet import BeatNet

# Initialize BeatNet estimator 
# Using online mode with PF (Particle Filter) inference model
print("Initializing BeatNet...")
estimator = BeatNet(1, mode='online', inference_model='PF', plot=[], thread=False)

# Process the audio file
audio_path = 'The Greatest Showman Cast - The Greatest Show (Official Audio) [ ezmp3.cc ].mp3'
print(f"Analyzing: {audio_path}")
print("This may take a minute...")

# Get beat positions and downbeats
# Output format: array of [beat_time, beat_type] where beat_type indicates downbeat (1.0) or other beats
output = estimator.process(audio_path)

print(f"\nBeatNet detected {len(output)} beats")

# Separate beats and downbeats
all_beats = []
downbeats = []

for beat_info in output:
    beat_time = beat_info[0]
    beat_type = beat_info[1]  # 1.0 for downbeat, other values for other beats in measure
    all_beats.append(beat_time)
    if beat_type == 1.0:
        downbeats.append(beat_time)

print(f"  - All beats: {len(all_beats)}")
print(f"  - Downbeats (measure starts): {len(downbeats)}")

# Calculate tempo from beat intervals
if len(all_beats) > 1:
    intervals = [all_beats[i+1] - all_beats[i] for i in range(min(100, len(all_beats)-1))]
    avg_interval = sum(intervals) / len(intervals)
    tempo_bpm = 60.0 / avg_interval
    print(f"  - Detected tempo: {tempo_bpm:.1f} BPM")
    print(f"  - Beat interval: {avg_interval:.3f}s")

# Save beat times
with open('beatnet_all_beats.txt', 'w') as f:
    for beat_time in all_beats:
        f.write(f"{beat_time:.6f}\n")

with open('beatnet_downbeats.txt', 'w') as f:
    for beat_time in downbeats:
        f.write(f"{beat_time:.6f}\n")

print(f"\nSaved {len(all_beats)} beats to beatnet_all_beats.txt")
print(f"Saved {len(downbeats)} downbeats to beatnet_downbeats.txt")

# Print first 20 beats for verification
print("\nFirst 20 beats:")
for i, beat in enumerate(all_beats[:20]):
    beat_type = "DOWNBEAT" if beat in downbeats else "beat"
    print(f"  {i+1}. {beat:.3f}s - {beat_type}")
