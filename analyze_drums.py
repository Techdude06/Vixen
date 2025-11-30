#!/usr/bin/env python3
"""
Advanced drum beat analysis for The Greatest Show MP3

This script uses librosa to:
1. Detect tempo (BPM)
2. Extract beat positions using onset detection
3. Identify drum/percussion hits
4. Create beat markers aligned with actual drum patterns
"""

import librosa
import numpy as np

# Load the MP3 file
mp3_file = "The Greatest Showman Cast - The Greatest Show (Official Audio) [ ezmp3.cc ].mp3"
print(f"Loading {mp3_file}...")

# Load audio with librosa
y, sr = librosa.load(mp3_file, sr=22050)
duration = librosa.get_duration(y=y, sr=sr)
print(f"Duration: {duration:.2f} seconds")
print(f"Sample rate: {sr} Hz")

# ===== TEMPO DETECTION =====
print("\n=== TEMPO ANALYSIS ===")

# Use multiple methods for tempo detection
tempo_plp, beats_plp = librosa.beat.beat_track(y=y, sr=sr, units='time')
print(f"Primary tempo (PLP): {float(tempo_plp):.1f} BPM")

# Also try tempogram-based detection
oenv = librosa.onset.onset_strength(y=y, sr=sr)
tempogram = librosa.feature.tempogram(onset_envelope=oenv, sr=sr)
tempo_tg = librosa.feature.tempo(onset_envelope=oenv, sr=sr, aggregate=None)
print(f"Tempogram tempo range: {tempo_tg.min():.1f} - {tempo_tg.max():.1f} BPM")

# ===== BEAT DETECTION =====
print("\n=== BEAT DETECTION ===")
print(f"Detected {len(beats_plp)} beats from beat_track")

# ===== ONSET/DRUM DETECTION =====
print("\n=== ONSET/DRUM DETECTION ===")

# Detect onsets (sudden changes in energy - typically drums/percussion)
onset_frames = librosa.onset.onset_detect(y=y, sr=sr, backtrack=True)
onset_times = librosa.frames_to_time(onset_frames, sr=sr)
print(f"Detected {len(onset_times)} onsets (drum hits/transients)")

# ===== PERCUSSIVE SEPARATION =====
print("\n=== PERCUSSIVE COMPONENT ANALYSIS ===")

# Separate harmonic and percussive components
y_harmonic, y_percussive = librosa.effects.hpss(y)

# Get beats from percussive component (more accurate for drums)
tempo_perc, beats_perc = librosa.beat.beat_track(y=y_percussive, sr=sr, units='time')
print(f"Percussive tempo: {float(tempo_perc):.1f} BPM")
print(f"Detected {len(beats_perc)} percussive beats")

# Get onsets from percussive component
onset_perc_frames = librosa.onset.onset_detect(y=y_percussive, sr=sr, backtrack=True)
onset_perc_times = librosa.frames_to_time(onset_perc_frames, sr=sr)
print(f"Detected {len(onset_perc_times)} percussive onsets")

# ===== COMBINE AND REFINE =====
print("\n=== COMBINED BEAT MARKERS ===")

# Combine beat positions from multiple sources
all_beats = set()

# Add beats from beat tracking
for b in beats_plp:
    all_beats.add(round(b, 3))

# Add beats from percussive analysis
for b in beats_perc:
    all_beats.add(round(b, 3))

# Filter to keep only strong, unique beats (remove duplicates within 0.1s)
sorted_beats = sorted(all_beats)
filtered_beats = []
last_beat = -1

for beat in sorted_beats:
    if beat - last_beat > 0.1:  # At least 0.1s apart
        filtered_beats.append(beat)
        last_beat = beat

print(f"Combined filtered beats: {len(filtered_beats)}")

# ===== STRONG BEAT DETECTION =====
print("\n=== STRONG BEAT (DOWNBEAT) DETECTION ===")

# Detect downbeats (strong beats, typically measure starts)
# Use the onset strength envelope
onset_env = librosa.onset.onset_strength(y=y, sr=sr)

# Find local maxima in onset strength
from scipy.signal import find_peaks
peaks, properties = find_peaks(onset_env, height=onset_env.mean(), distance=int(sr/512 * 0.2))
strong_beat_frames = peaks
strong_beat_times = librosa.frames_to_time(strong_beat_frames, sr=sr)
print(f"Detected {len(strong_beat_times)} strong beats (above average energy)")

# ===== CALCULATE FINAL TEMPO =====
if len(filtered_beats) > 1:
    intervals = np.diff(filtered_beats)
    median_interval = np.median(intervals)
    final_tempo = 60.0 / median_interval
    print(f"\nFinal estimated tempo: {final_tempo:.1f} BPM")
    print(f"Median beat interval: {median_interval:.3f}s")

# ===== SAVE BEAT MARKERS =====
print("\n=== SAVING BEAT MARKERS ===")

# Save all beat types for comparison
with open('beats_primary.txt', 'w') as f:
    for beat in beats_plp:
        f.write(f"{beat:.6f}\n")
print(f"Saved {len(beats_plp)} primary beats to beats_primary.txt")

with open('beats_percussive.txt', 'w') as f:
    for beat in beats_perc:
        f.write(f"{beat:.6f}\n")
print(f"Saved {len(beats_perc)} percussive beats to beats_percussive.txt")

with open('beats_combined.txt', 'w') as f:
    for beat in filtered_beats:
        f.write(f"{beat:.6f}\n")
print(f"Saved {len(filtered_beats)} combined beats to beats_combined.txt")

with open('onsets_percussive.txt', 'w') as f:
    for onset in onset_perc_times:
        f.write(f"{onset:.6f}\n")
print(f"Saved {len(onset_perc_times)} percussive onsets to onsets_percussive.txt")

# ===== COMPARE WITH EXISTING STOMPS =====
print("\n=== COMPARISON WITH EXISTING STOMPS ===")
stomps = []
with open('Greatestshow_Stomps.txt', 'r') as f:
    for line in f:
        parts = line.strip().split()
        if parts:
            stomps.append(float(parts[0]))

print(f"Existing stomps: {len(stomps)}")
print(f"New percussive beats: {len(beats_perc)}")
print(f"New combined beats: {len(filtered_beats)}")

# Check overlap
overlap_count = 0
for stomp in stomps:
    for beat in filtered_beats:
        if abs(stomp - beat) < 0.1:
            overlap_count += 1
            break

print(f"Overlap with existing stomps: {overlap_count}/{len(stomps)} ({100*overlap_count/len(stomps):.1f}%)")

# ===== PRINT FIRST 30 BEATS =====
print("\n=== FIRST 30 COMBINED BEATS ===")
for i, beat in enumerate(filtered_beats[:30]):
    print(f"  {i+1:3d}. {beat:.3f}s")

print("\n=== SUMMARY ===")
print(f"Tempo: {float(tempo_perc):.1f} BPM (from percussive analysis)")
print(f"Beat interval: {60.0/float(tempo_perc):.3f}s")
print(f"Total duration: {duration:.2f}s")
print(f"Expected beats at this tempo: {int(duration / (60.0/float(tempo_perc)))}")
print(f"Actual detected beats: {len(filtered_beats)}")
