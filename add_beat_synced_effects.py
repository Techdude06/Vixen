#!/usr/bin/env python3
"""
Add beat-synced effects to The Greatest Show.tim

This script:
1. Uses drum beat markers from librosa analysis (beats_percussive.txt)
2. Analyzes existing effects to find gaps
3. Only adds effects where there are no existing effects
4. Focuses on tempo matching - effects change on drum beats
5. Tempo: 161.5 BPM (from percussive analysis)
"""

import re
import uuid
import random

def parse_duration(dur_str):
    """Convert ISO 8601 duration to seconds"""
    match = re.match(r'PT(?:(\d+)M)?(\d+(?:\.\d+)?)S', dur_str)
    if match:
        mins = int(match.group(1)) if match.group(1) else 0
        secs = float(match.group(2))
        return mins * 60 + secs
    return 0

def seconds_to_duration(seconds):
    """Convert seconds to ISO 8601 duration format."""
    if seconds < 60:
        return f"PT{seconds:.7f}S"
    else:
        mins = int(seconds // 60)
        secs = seconds % 60
        return f"PT{mins}M{secs:.7f}S"

# Read drum beat markers from librosa analysis (more accurate than stomps)
drum_beats = []
try:
    with open('beats_percussive.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                drum_beats.append(float(line))
    print(f"Loaded {len(drum_beats)} drum beat markers from librosa analysis")
except FileNotFoundError:
    # Fallback to stomps if drum analysis not available
    with open('Greatestshow_Stomps.txt', 'r') as f:
        for line in f:
            parts = line.strip().split()
            if parts:
                drum_beats.append(float(parts[0]))
    print(f"Loaded {len(drum_beats)} beat markers from stomps (fallback)")

# Calculate tempo from beat intervals
if len(drum_beats) > 1:
    intervals = [drum_beats[i+1] - drum_beats[i] for i in range(min(100, len(drum_beats)-1))]
    avg_interval = sum(intervals) / len(intervals)
    tempo_bpm = 60.0 / avg_interval
    print(f"Tempo: {tempo_bpm:.1f} BPM (beat interval: {avg_interval:.3f}s)")

# Read original TIM file
with open('The Greatest Show.tim', 'r') as f:
    content = f.read()

# Extract existing effects with their time ranges
pattern = r'<StartTime>([^<]+)</StartTime>.*?<TimeSpan>([^<]+)</TimeSpan>'
matches = re.findall(pattern, content, re.DOTALL)

existing_effects = []
for start, duration in matches:
    start_sec = parse_duration(start)
    dur_sec = parse_duration(duration)
    end_sec = start_sec + dur_sec
    existing_effects.append((start_sec, end_sec))

existing_effects.sort()
print(f"Found {len(existing_effects)} existing effects")

def is_gap(time_point, existing_effects, threshold=0.5):
    """Check if a time point is in a gap (not covered by existing effects)"""
    for start, end in existing_effects:
        if start - threshold <= time_point <= end + threshold:
            return False
    return True

def find_gap_duration(time_point, existing_effects, max_duration=10.0):
    """Find how long we can make an effect starting at time_point without overlapping"""
    end_time = time_point + max_duration
    for start, end in existing_effects:
        if start > time_point and start < end_time:
            end_time = start - 0.1  # Leave small gap
    return min(end_time - time_point, max_duration)

# Colors in XYZ format
COLORS = [
    {'x': 41.24564394, 'y': 21.26729007, 'z': 1.93339082},    # red
    {'x': 18.05, 'y': 7.22, 'z': 95.05},                       # blue  
    {'x': 35.76, 'y': 71.52, 'z': 11.92},                      # green
    {'x': 77.0, 'y': 92.78, 'z': 13.85},                       # yellow
    {'x': 13.80, 'y': 6.16, 'z': 43.59},                       # purple
    {'x': 59.01, 'y': 56.80, 'z': 7.85},                       # orange
    {'x': 95.05, 'y': 100.0, 'z': 108.88},                     # white
    {'x': 42.35, 'y': 55.82, 'z': 103.15},                     # light blue
]

# Effect Type IDs
PULSE_TYPE_ID = 'cbd76d3b-c924-40ff-bad6-d1437b3dbdc0'
TWINKLE_TYPE_ID = '83bdd6f7-19c7-4598-b8e3-7ce28c44e7db'
BUTTERFLY_TYPE_ID = 'e2ef89d5-c3b3-47e7-a776-f31b4193fc76'
SPIRAL_TYPE_ID = '3f629e8c-cd8d-467e-afab-1a3836b24342'
WIPE_TYPE_ID = '61746b54-a96c-4723-8bd6-39c7ea985f80'

ALL_PIXELS_NODE_ID = 'c1ea9007-f2ab-4faa-8e63-798ad274695e'

def make_color_gradient(color):
    """Generate a color gradient XML snippet."""
    return f'''<d3p1:IsCurrentLibraryGradient>false</d3p1:IsCurrentLibraryGradient>
        <d3p1:_alphas>
          <d3p1:AlphaPoint>
            <d3p1:_focus>0.5</d3p1:_focus>
            <d3p1:_position>0</d3p1:_position>
            <d3p1:_alpha>1</d3p1:_alpha>
          </d3p1:AlphaPoint>
          <d3p1:AlphaPoint>
            <d3p1:_focus>0.5</d3p1:_focus>
            <d3p1:_position>1</d3p1:_position>
            <d3p1:_alpha>1</d3p1:_alpha>
          </d3p1:AlphaPoint>
        </d3p1:_alphas>
        <d3p1:_colors>
          <d3p1:ColorPoint>
            <d3p1:_focus>0.5</d3p1:_focus>
            <d3p1:_position>0</d3p1:_position>
            <d3p1:_color xmlns:d6p1="http://schemas.datacontract.org/2004/07/Common.Controls.ColorManagement.ColorModels">
              <d6p1:_x>{color['x']}</d6p1:_x>
              <d6p1:_y>{color['y']}</d6p1:_y>
              <d6p1:_z>{color['z']}</d6p1:_z>
            </d3p1:_color>
          </d3p1:ColorPoint>
        </d3p1:_colors>
        <d3p1:_gammacorrected>false</d3p1:_gammacorrected>
        <d3p1:_libraryReferenceName></d3p1:_libraryReferenceName>
        <d3p1:_title i:nil="true" />'''

def make_curve(points):
    """Generate a curve XML snippet."""
    point_xml = ''
    for x, y in points:
        point_xml += f'''          <d4p1:PointPair>
            <schema i:type="a:int">11</schema>
            <X i:type="a:double">{x}</X>
            <Y i:type="a:double">{y}</Y>
            <schema2 i:type="a:int">11</schema2>
            <Z i:type="a:double">0</Z>
            <Tag i:nil="true" />
          </d4p1:PointPair>
'''
    return f'''<d3p1:IsCurrentLibraryCurve>false</d3p1:IsCurrentLibraryCurve>
        <d3p1:Points xmlns:d4p1="http://schemas.datacontract.org/2004/07/ZedGraph">
{point_xml}        </d3p1:Points>
        <d3p1:_libraryReferenceName></d3p1:_libraryReferenceName>'''

def make_pulse_data(effect_id, color):
    return f'''    <d1p1:anyType xmlns:d2p1="http://schemas.datacontract.org/2004/07/VixenModules.Effect.Pulse" i:type="d2p1:PulseData">
      <ModuleInstanceId>{effect_id}</ModuleInstanceId>
      <ModuleTypeId>{PULSE_TYPE_ID}</ModuleTypeId>
      <TargetPositioning xmlns="http://schemas.datacontract.org/2004/07/VixenModules.Effect.Effect">Strings</TargetPositioning>
      <d2p1:ColorGradient xmlns:d3p1="http://schemas.datacontract.org/2004/07/VixenModules.App.ColorGradients">
        {make_color_gradient(color)}
      </d2p1:ColorGradient>
      <d2p1:LevelCurve xmlns:d3p1="http://schemas.datacontract.org/2004/07/VixenModules.App.Curves">
        {make_curve([(0, 100), (100, 0)])}
      </d2p1:LevelCurve>
    </d1p1:anyType>
'''

def make_twinkle_data(effect_id, color):
    return f'''    <d1p1:anyType xmlns:d2p1="http://schemas.datacontract.org/2004/07/VixenModules.Effect.Twinkle" i:type="d2p1:TwinkleData">
      <ModuleInstanceId>{effect_id}</ModuleInstanceId>
      <ModuleTypeId>{TWINKLE_TYPE_ID}</ModuleTypeId>
      <TargetPositioning xmlns="http://schemas.datacontract.org/2004/07/VixenModules.Effect.Effect">Strings</TargetPositioning>
      <d2p1:AverageCoverage>50</d2p1:AverageCoverage>
      <d2p1:AveragePulseTime>400</d2p1:AveragePulseTime>
      <d2p1:ColorGradient xmlns:d3p1="http://schemas.datacontract.org/2004/07/VixenModules.App.ColorGradients">
        {make_color_gradient(color)}
      </d2p1:ColorGradient>
      <d2p1:ColorHandling>GradientForEachPulse</d2p1:ColorHandling>
      <d2p1:DepthOfEffect>0</d2p1:DepthOfEffect>
      <d2p1:IndividualChannels>true</d2p1:IndividualChannels>
      <d2p1:LevelVariation>50</d2p1:LevelVariation>
      <d2p1:MaximumLevel>1</d2p1:MaximumLevel>
      <d2p1:MinimumLevel>0</d2p1:MinimumLevel>
      <d2p1:PulseTimeVariation>30</d2p1:PulseTimeVariation>
      <d2p1:StaticColor xmlns:d3p1="http://schemas.datacontract.org/2004/07/System.Drawing">
        <d3p1:knownColor>164</d3p1:knownColor>
        <d3p1:name i:nil="true" />
        <d3p1:state>1</d3p1:state>
        <d3p1:value>0</d3p1:value>
      </d2p1:StaticColor>
    </d1p1:anyType>
'''

def make_butterfly_data(effect_id, color, butterfly_type='Type1'):
    return f'''    <d1p1:anyType xmlns:d2p1="http://schemas.datacontract.org/2004/07/VixenModules.Effect.Butterfly" i:type="d2p1:ButterflyData">
      <ModuleInstanceId>{effect_id}</ModuleInstanceId>
      <ModuleTypeId>{BUTTERFLY_TYPE_ID}</ModuleTypeId>
      <TargetPositioning xmlns="http://schemas.datacontract.org/2004/07/VixenModules.Effect.Effect">Strings</TargetPositioning>
      <d2p1:BackgroundChunks>1</d2p1:BackgroundChunks>
      <d2p1:BackgroundSkips>2</d2p1:BackgroundSkips>
      <d2p1:ButterflyType>{butterfly_type}</d2p1:ButterflyType>
      <d2p1:ColorScheme>Gradient</d2p1:ColorScheme>
      <d2p1:Direction>Forward</d2p1:Direction>
      <d2p1:Gradient xmlns:d3p1="http://schemas.datacontract.org/2004/07/VixenModules.App.ColorGradients">
        {make_color_gradient(color)}
      </d2p1:Gradient>
      <d2p1:Iterations>5</d2p1:Iterations>
      <d2p1:LevelCurve xmlns:d3p1="http://schemas.datacontract.org/2004/07/VixenModules.App.Curves">
        {make_curve([(0, 100), (100, 100)])}
      </d2p1:LevelCurve>
      <d2p1:MovementType>Iterations</d2p1:MovementType>
      <d2p1:Orientation>Vertical</d2p1:Orientation>
      <d2p1:Repeat>1</d2p1:Repeat>
      <d2p1:SpeedCurve xmlns:d3p1="http://schemas.datacontract.org/2004/07/VixenModules.App.Curves">
        {make_curve([(0, 60), (100, 60)])}
      </d2p1:SpeedCurve>
    </d1p1:anyType>
'''

def make_spiral_data(effect_id, colors):
    color_gradients = ''
    for color in colors:
        color_gradients += f'''        <d3p1:ColorGradient>
          {make_color_gradient(color)}
        </d3p1:ColorGradient>
'''
    return f'''    <d1p1:anyType xmlns:d2p1="http://schemas.datacontract.org/2004/07/VixenModules.Effect.Spiral" i:type="d2p1:SpiralData">
      <ModuleInstanceId>{effect_id}</ModuleInstanceId>
      <ModuleTypeId>{SPIRAL_TYPE_ID}</ModuleTypeId>
      <TargetPositioning xmlns="http://schemas.datacontract.org/2004/07/VixenModules.Effect.Effect">Strings</TargetPositioning>
      <d2p1:Blend>true</d2p1:Blend>
      <d2p1:Colors xmlns:d3p1="http://schemas.datacontract.org/2004/07/VixenModules.App.ColorGradients">
{color_gradients}      </d2p1:Colors>
      <d2p1:Direction>Forward</d2p1:Direction>
      <d2p1:Grow>false</d2p1:Grow>
      <d2p1:LevelCurve xmlns:d3p1="http://schemas.datacontract.org/2004/07/VixenModules.App.Curves">
        {make_curve([(0, 100), (100, 100)])}
      </d2p1:LevelCurve>
      <d2p1:MovementType>Iterations</d2p1:MovementType>
      <d2p1:Orientation>Vertical</d2p1:Orientation>
      <d2p1:Repeat>1</d2p1:Repeat>
      <d2p1:RotationCurve xmlns:d3p1="http://schemas.datacontract.org/2004/07/VixenModules.App.Curves">
        {make_curve([(0, 57), (100, 57)])}
      </d2p1:RotationCurve>
      <d2p1:Show3D>false</d2p1:Show3D>
      <d2p1:Shrink>false</d2p1:Shrink>
      <d2p1:Speed>1</d2p1:Speed>
      <d2p1:SpeedCurve xmlns:d3p1="http://schemas.datacontract.org/2004/07/VixenModules.App.Curves">
        {make_curve([(0, 70), (100, 70)])}
      </d2p1:SpeedCurve>
      <d2p1:ThicknessCurve xmlns:d3p1="http://schemas.datacontract.org/2004/07/VixenModules.App.Curves">
        {make_curve([(0, 60), (100, 60)])}
      </d2p1:ThicknessCurve>
    </d1p1:anyType>
'''

def make_wipe_data(effect_id, color, direction='Horizontal'):
    return f'''    <d1p1:anyType xmlns:d2p1="http://schemas.datacontract.org/2004/07/VixenModules.Effect.Wipe" i:type="d2p1:WipeData">
      <ModuleInstanceId>{effect_id}</ModuleInstanceId>
      <ModuleTypeId>{WIPE_TYPE_ID}</ModuleTypeId>
      <TargetPositioning xmlns="http://schemas.datacontract.org/2004/07/VixenModules.Effect.Effect">Strings</TargetPositioning>
      <d2p1:ColorAcrossItemPerCount>true</d2p1:ColorAcrossItemPerCount>
      <d2p1:ColorGradient xmlns:d3p1="http://schemas.datacontract.org/2004/07/VixenModules.App.ColorGradients">
        {make_color_gradient(color)}
      </d2p1:ColorGradient>
      <d2p1:ColorHandling>GradientThroughWholeEffect</d2p1:ColorHandling>
      <d2p1:Curve xmlns:d3p1="http://schemas.datacontract.org/2004/07/VixenModules.App.Curves">
        {make_curve([(0, 0), (50, 100), (100, 0)])}
      </d2p1:Curve>
      <d2p1:Direction>{direction}</d2p1:Direction>
      <d2p1:MovementCurve xmlns:d3p1="http://schemas.datacontract.org/2004/07/VixenModules.App.Curves">
        {make_curve([(0, 0), (100, 100)])}
      </d2p1:MovementCurve>
      <d2p1:PassCount>1</d2p1:PassCount>
      <d2p1:PulsePercent>33</d2p1:PulsePercent>
      <d2p1:PulseTime>1000</d2p1:PulseTime>
      <d2p1:ReverseColorDirection>true</d2p1:ReverseColorDirection>
      <d2p1:ReverseDirection>false</d2p1:ReverseDirection>
      <d2p1:WipeMovement>Count</d2p1:WipeMovement>
      <d2p1:WipeOff>false</d2p1:WipeOff>
      <d2p1:WipeOn>true</d2p1:WipeOn>
      <d2p1:XOffset>0</d2p1:XOffset>
      <d2p1:YOffset>0</d2p1:YOffset>
    </d1p1:anyType>
'''

def make_effect_node(effect_id, start_time, time_span, type_id):
    return f'''    <EffectNodeSurrogate>
      <InstanceId>{effect_id}</InstanceId>
      <StartTime>{start_time}</StartTime>
      <TargetNodes>
        <ChannelNodeReferenceSurrogate>
          <Name>All Pixels</Name>
          <NodeId>{ALL_PIXELS_NODE_ID}</NodeId>
        </ChannelNodeReferenceSurrogate>
      </TargetNodes>
      <TimeSpan>{time_span}</TimeSpan>
      <TypeId>{type_id}</TypeId>
    </EffectNodeSurrogate>
'''

# Find drum beats that are in gaps (no existing effects)
beats_in_gaps = []
for beat_time in drum_beats:
    if is_gap(beat_time, existing_effects, threshold=0.3):
        beats_in_gaps.append(beat_time)

print(f"\nFound {len(beats_in_gaps)} drum beats in gaps (out of {len(drum_beats)} total)")

# Group consecutive beats to form effect placements
# Strategy: For longer gaps, use longer effects; for short gaps, use pulses
new_effect_data = []
new_effect_nodes = []
effects_added = 0
color_idx = 0

# Effect patterns based on section (different parts of song)
# Using the beat markers to determine where we are in the song structure
i = 0
while i < len(beats_in_gaps):
    beat_time = beats_in_gaps[i]
    
    # Find how many consecutive beats are in this gap
    gap_duration = find_gap_duration(beat_time, existing_effects, max_duration=10.0)
    
    # Count beats within this gap
    beats_in_this_gap = 1
    j = i + 1
    while j < len(beats_in_gaps) and beats_in_gaps[j] < beat_time + gap_duration:
        beats_in_this_gap += 1
        j += 1
    
    color = COLORS[color_idx % len(COLORS)]
    effect_id = str(uuid.uuid4())
    
    # Choose effect type based on gap size and position
    # Longer gaps get more complex effects
    if gap_duration >= 5.0:
        # Long gaps: use Spiral, Butterfly, or Twinkle
        effect_choice = random.choice(['spiral', 'butterfly', 'twinkle'])
        duration = min(gap_duration, 8.0)  # Cap at 8 seconds
        
        if effect_choice == 'spiral':
            data = make_spiral_data(effect_id, random.sample(COLORS, 3))
            type_id = SPIRAL_TYPE_ID
        elif effect_choice == 'butterfly':
            btype = random.choice(['Type1', 'Type2', 'Type3', 'Type4', 'Type5'])
            data = make_butterfly_data(effect_id, color, btype)
            type_id = BUTTERFLY_TYPE_ID
        else:
            data = make_twinkle_data(effect_id, color)
            type_id = TWINKLE_TYPE_ID
            
    elif gap_duration >= 2.5:
        # Medium gaps: use Wipe or shorter Twinkle
        effect_choice = random.choice(['wipe', 'twinkle', 'butterfly'])
        duration = min(gap_duration, 5.0)
        
        if effect_choice == 'wipe':
            direction = random.choice(['Horizontal', 'Vertical', 'DiagonalUp', 'Burst'])
            data = make_wipe_data(effect_id, color, direction)
            type_id = WIPE_TYPE_ID
        elif effect_choice == 'butterfly':
            data = make_butterfly_data(effect_id, color)
            type_id = BUTTERFLY_TYPE_ID
        else:
            data = make_twinkle_data(effect_id, color)
            type_id = TWINKLE_TYPE_ID
            
    else:
        # Short gaps: use Pulse (synced to the beat)
        duration = min(gap_duration, 2.0)  # Pulse max 2 seconds
        data = make_pulse_data(effect_id, color)
        type_id = PULSE_TYPE_ID
    
    new_effect_data.append(data)
    start_str = seconds_to_duration(beat_time)
    dur_str = seconds_to_duration(duration)
    new_effect_nodes.append(make_effect_node(effect_id, start_str, dur_str, type_id))
    
    effects_added += 1
    color_idx += 1
    
    # Skip beats that are covered by this effect
    while i < len(beats_in_gaps) and beats_in_gaps[i] < beat_time + duration:
        i += 1

print(f"Added {effects_added} new effects at beat positions")

# Find insertion points
data_models_end = content.find('</_dataModels>')
effect_nodes_end = content.find('</_effectNodeSurrogates>')

if data_models_end == -1 or effect_nodes_end == -1:
    print("ERROR: Could not find insertion points")
    raise SystemExit(1)

# Insert effect data
insert_data = '\n'.join(new_effect_data)
content = content[:data_models_end] + insert_data + '\n  ' + content[data_models_end:]

# Recalculate position after insertion
effect_nodes_end = content.find('</_effectNodeSurrogates>')
insert_nodes = '\n'.join(new_effect_nodes)
content = content[:effect_nodes_end] + insert_nodes + '\n  ' + content[effect_nodes_end:]

# Save
with open('The Greatest Show.tim', 'w', encoding='utf-8') as f:
    f.write(content)

print("\nSuccessfully added beat-synced effects to The Greatest Show.tim!")

# Count effect types
pulse_count = sum(1 for d in new_effect_data if 'PulseData' in d)
twinkle_count = sum(1 for d in new_effect_data if 'TwinkleData' in d)
butterfly_count = sum(1 for d in new_effect_data if 'ButterflyData' in d)
spiral_count = sum(1 for d in new_effect_data if 'SpiralData' in d)
wipe_count = sum(1 for d in new_effect_data if 'WipeData' in d)

print(f"\nNew effect breakdown:")
print(f"  Pulse: {pulse_count}")
print(f"  Twinkle: {twinkle_count}")
print(f"  Butterfly: {butterfly_count}")
print(f"  Spiral: {spiral_count}")
print(f"  Wipe: {wipe_count}")
