#!/usr/bin/env python3
"""
Waveform analysis for The Greatest Show MP3 without librosa.

Uses pydub and numpy for audio processing and custom beat detection
based on energy/amplitude analysis of the waveform.
"""

import numpy as np
from pydub import AudioSegment
import struct

audio_path = 'The Greatest Showman Cast - The Greatest Show (Official Audio) [ ezmp3.cc ].mp3'
print(f"Loading audio: {audio_path}")

# Load audio with pydub
audio = AudioSegment.from_mp3(audio_path)
duration = len(audio) / 1000.0  # Convert ms to seconds
sample_rate = audio.frame_rate
channels = audio.channels

print(f"Duration: {duration:.1f} seconds")
print(f"Sample rate: {sample_rate} Hz")
print(f"Channels: {channels}")

# Convert to mono if stereo
if channels > 1:
    audio = audio.set_channels(1)

# Get raw audio data as numpy array
raw_data = audio.raw_data
samples = np.array(struct.unpack(f'{len(raw_data)//2}h', raw_data), dtype=np.float64)
samples = samples / 32768.0  # Normalize to -1 to 1

print(f"Total samples: {len(samples)}")

# === Beat Detection Algorithm ===
print("\n=== Beat Detection via Energy Analysis ===")

# Parameters for beat detection - optimized for faster tempos
hop_size = int(sample_rate * 0.01)  # 10ms hop
window_size = int(sample_rate * 0.02)  # 20ms window (shorter for faster detection)

# Calculate short-term energy
print("Calculating energy envelope...")
energy = []
for i in range(0, len(samples) - window_size, hop_size):
    window = samples[i:i + window_size]
    e = np.sum(window ** 2) / window_size
    energy.append(e)

energy = np.array(energy)
time_axis = np.arange(len(energy)) * hop_size / sample_rate

print(f"Energy frames: {len(energy)}")

# Smooth the energy with a moving average
print("Smoothing energy curve...")
smooth_window = 5  # Smaller window for faster response
smoothed = np.convolve(energy, np.ones(smooth_window)/smooth_window, mode='same')

# Calculate local average for adaptive threshold
local_avg_window = 50  # Smaller window for faster tempo detection
local_avg = np.convolve(smoothed, np.ones(local_avg_window)/local_avg_window, mode='same')

# Detect beats as peaks above local average
print("Detecting beats from energy peaks...")
threshold_factor = 1.2  # Peak must be 20% above local average
min_beat_interval = int(0.15 * sample_rate / hop_size)  # Minimum 150ms between beats (for up to 200 BPM)

beats = []
last_beat_idx = -min_beat_interval

for i in range(1, len(smoothed) - 1):
    # Check if this is a local peak
    if smoothed[i] > smoothed[i-1] and smoothed[i] > smoothed[i+1]:
        # Check if above threshold
        if smoothed[i] > local_avg[i] * threshold_factor:
            # Check minimum interval
            if i - last_beat_idx >= min_beat_interval:
                beat_time = time_axis[i]
                beat_strength = smoothed[i] / (local_avg[i] + 0.0001)
                beats.append((beat_time, beat_strength))
                last_beat_idx = i

print(f"Initial beats detected: {len(beats)}")

# === Tempo Estimation ===
print("\n=== Tempo Estimation ===")

if len(beats) > 10:
    # Calculate intervals between consecutive beats
    intervals = []
    for i in range(len(beats) - 1):
        interval = beats[i+1][0] - beats[i][0]
        if 0.2 < interval < 0.8:  # Filter for 75-300 BPM range
            intervals.append(interval)
    
    if intervals:
        # Use histogram approach to find most common interval
        # This helps identify the true tempo even with some irregular beats
        interval_counts = {}
        bucket_size = 0.02  # 20ms buckets
        for interval in intervals:
            bucket = round(interval / bucket_size) * bucket_size
            interval_counts[bucket] = interval_counts.get(bucket, 0) + 1
        
        # Find the most common interval bucket
        most_common = max(interval_counts, key=interval_counts.get)
        
        # Get all intervals near this bucket
        near_intervals = [i for i in intervals if abs(i - most_common) < 0.05]
        
        if near_intervals:
            median_interval = sum(near_intervals) / len(near_intervals)
        else:
            median_interval = most_common
            
        tempo_bpm = 60.0 / median_interval
        print(f"Most common interval: {most_common:.3f}s (count: {interval_counts[most_common]})")
        print(f"Average near-interval: {median_interval:.3f}s")
        print(f"Estimated tempo: {tempo_bpm:.1f} BPM")
        
        # For this song, we know it's a fast-tempo show tune
        # If detected tempo is low, it might be half-time
        if tempo_bpm < 120:
            tempo_bpm *= 2
            median_interval /= 2
            print(f"Adjusted tempo (half-time correction): {tempo_bpm:.1f} BPM")
        
        # Round tempo to nearest common value
        common_tempos = [120, 130, 140, 150, 155, 160, 165, 170, 175, 180]
        rounded_tempo = min(common_tempos, key=lambda x: abs(x - tempo_bpm))
        print(f"Rounded tempo: {rounded_tempo} BPM")
        
        beat_interval = 60.0 / rounded_tempo
    else:
        beat_interval = 0.37  # Default ~162 BPM
        tempo_bpm = 60.0 / beat_interval
        rounded_tempo = 160
else:
    beat_interval = 0.37
    tempo_bpm = 60.0 / beat_interval
    rounded_tempo = 160

# === Generate Regular Beat Grid ===
print("\n=== Generating Beat Grid ===")

# Find the first strong beat (look for a beat near the start with high energy)
first_beat = 0.5  # Default
for t, s in beats[:20]:
    if s > 1.3 and t > 0.3:  # Strong beat at least 300ms in
        first_beat = t
        break

print(f"First beat at: {first_beat:.3f}s")

# Generate regular beat grid aligned to detected tempo
beat_times = []
current_time = first_beat
while current_time < duration:
    beat_times.append(current_time)
    current_time += beat_interval

print(f"Generated {len(beat_times)} beats on regular grid at {rounded_tempo} BPM")

# === Identify Downbeats ===
beats_per_measure = 4
downbeats = []
for i, beat_time in enumerate(beat_times):
    if i % beats_per_measure == 0:
        downbeats.append(beat_time)

print(f"Identified {len(downbeats)} downbeats")

# === Find Strong Beats ===
# Match grid beats to detected energy peaks
print("\n=== Identifying Strong Beats ===")
strong_beats = []
beat_strengths = []

for beat_time in beat_times:
    # Find nearest detected peak
    min_dist = float('inf')
    strength = 0.0
    for peak_time, peak_strength in beats:
        dist = abs(peak_time - beat_time)
        if dist < min_dist and dist < beat_interval * 0.3:  # Within 30% of beat interval
            min_dist = dist
            strength = peak_strength
    
    beat_strengths.append(strength)
    if strength > 1.3:  # Strong beat threshold
        strong_beats.append(beat_time)

print(f"Identified {len(strong_beats)} strong beats")

# === Save Results ===
print("\n=== Saving Results ===")

# Normalize strengths
max_strength = max(beat_strengths) if beat_strengths and max(beat_strengths) > 0 else 1.0
beat_strengths = [s / max_strength for s in beat_strengths]

with open('beatnet_waveform_beats.txt', 'w') as f:
    f.write("# Waveform analysis results (pydub + energy detection)\n")
    f.write(f"# Tempo: {rounded_tempo} BPM\n")
    f.write(f"# Beat interval: {beat_interval:.3f}s\n")
    f.write(f"# Total beats: {len(beat_times)}\n")
    f.write(f"# Downbeats: {len(downbeats)}\n")
    f.write("# Format: time_seconds,beat_position_in_measure,strength\n")
    for i, beat_time in enumerate(beat_times):
        beat_pos = (i % beats_per_measure) + 1
        strength = beat_strengths[i] if i < len(beat_strengths) else 0
        f.write(f"{beat_time:.6f},{beat_pos},{strength:.3f}\n")

with open('beatnet_waveform_downbeats.txt', 'w') as f:
    for beat_time in downbeats:
        f.write(f"{beat_time:.6f}\n")

with open('beatnet_strong_beats.txt', 'w') as f:
    for beat_time in strong_beats:
        f.write(f"{beat_time:.6f}\n")

print(f"Saved {len(beat_times)} beats to beatnet_waveform_beats.txt")
print(f"Saved {len(downbeats)} downbeats to beatnet_waveform_downbeats.txt")
print(f"Saved {len(strong_beats)} strong beats to beatnet_strong_beats.txt")

# Print first 40 beats
print("\nFirst 40 beats:")
for i, beat_time in enumerate(beat_times[:40]):
    beat_pos = (i % beats_per_measure) + 1
    strength = beat_strengths[i] if i < len(beat_strengths) else 0
    is_strong = beat_time in strong_beats
    strength_indicator = "**STRONG**" if is_strong else ""
    marker = ">>> DOWNBEAT" if beat_pos == 1 else f"    beat {beat_pos}"
    print(f"  {i+1:3d}. {beat_time:7.3f}s - {marker} (str: {strength:.2f}) {strength_indicator}")
