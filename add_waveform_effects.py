#!/usr/bin/env python3
"""
Add effects that start and stop exactly on waveform-analyzed drum beats.

This script:
1. Uses enhanced waveform beat markers (beatnet_waveform_beats.txt)
2. Uses beat strength information to decide effect type
3. Analyzes existing effects to find gaps
4. Only adds effects where there are no existing effects
5. Effects START and END exactly on drum beats
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

# Read enhanced waveform beat markers with position and strength
beats = []
beat_data = {}  # time -> (position, strength)
with open('beatnet_waveform_beats.txt', 'r') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            parts = line.split(',')
            if len(parts) >= 3:
                time = float(parts[0])
                position = int(parts[1])
                strength = float(parts[2])
                beats.append(time)
                beat_data[time] = (position, strength)

print(f"Loaded {len(beats)} beats from waveform analysis")

# Read downbeats (measure starts)
downbeats = set()
with open('beatnet_waveform_downbeats.txt', 'r') as f:
    for line in f:
        line = line.strip()
        if line:
            downbeats.add(float(line))

print(f"Loaded {len(downbeats)} downbeats (measure starts)")

# Read strong beats
strong_beats = set()
with open('beatnet_strong_beats.txt', 'r') as f:
    for line in f:
        line = line.strip()
        if line:
            strong_beats.add(float(line))

print(f"Loaded {len(strong_beats)} strong beats")

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

def is_gap(time_point, existing_effects, threshold=0.3):
    """Check if a time point is in a gap (not covered by existing effects)"""
    for start, end in existing_effects:
        if start - threshold <= time_point <= end + threshold:
            return False
    return True

def find_end_beat(start_beat_idx, beats, existing_effects, beat_data, is_downbeat, is_strong, min_duration=0.5, max_duration=10.0):
    """Find the best ending beat for an effect starting at start_beat_idx.
    
    For downbeats/strong beats: allow longer durations (up to max_duration)
    For regular beats: shorter durations (pulse effects, up to 2 seconds)
    """
    start_time = beats[start_beat_idx]
    
    # Determine duration range based on beat type
    if is_downbeat:
        # Downbeats can have longer effects
        min_dur = 1.0
        max_dur = min(max_duration, 8.0)  # Up to 8 seconds
    elif is_strong:
        # Strong beats get medium duration
        min_dur = 0.7
        max_dur = min(max_duration, 4.0)  # Up to 4 seconds
    else:
        # Regular beats get pulse effects
        min_dur = min_duration
        max_dur = min(max_duration, 2.0)  # Up to 2 seconds
    
    # Look for beats within the duration range
    for i in range(start_beat_idx + 1, min(start_beat_idx + 20, len(beats))):
        end_time = beats[i]
        duration = end_time - start_time
        
        # Check if duration is within acceptable range
        if duration < min_dur:
            continue
        if duration > max_dur:
            break
            
        # Check if end point would overlap with existing effects
        overlap = False
        for ex_start, ex_end in existing_effects:
            if ex_start <= end_time <= ex_end:
                overlap = True
                break
        
        if not overlap:
            return i, end_time, duration
    
    return None, None, None

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
      <d2p1:IndividualChannels>false</d2p1:IndividualChannels>
      <d2p1:LevelCurve xmlns:d3p1="http://schemas.datacontract.org/2004/07/VixenModules.App.Curves">
        {make_curve([(0, 100), (100, 100)])}
      </d2p1:LevelCurve>
      <d2p1:LevelVariation>50</d2p1:LevelVariation>
      <d2p1:MaxCoverage>100</d2p1:MaxCoverage>
      <d2p1:MaxPulseTime>500</d2p1:MaxPulseTime>
      <d2p1:MinCoverage>25</d2p1:MinCoverage>
      <d2p1:MinPulseTime>200</d2p1:MinPulseTime>
    </d1p1:anyType>
'''

def make_butterfly_data(effect_id, color, butterfly_type=1):
    btype = f'Type{butterfly_type}'
    return f'''    <d1p1:anyType xmlns:d2p1="http://schemas.datacontract.org/2004/07/VixenModules.Effect.Butterfly" i:type="d2p1:ButterflyData">
      <ModuleInstanceId>{effect_id}</ModuleInstanceId>
      <ModuleTypeId>{BUTTERFLY_TYPE_ID}</ModuleTypeId>
      <TargetPositioning xmlns="http://schemas.datacontract.org/2004/07/VixenModules.Effect.Effect">Strings</TargetPositioning>
      <d2p1:BackgroundChunks>1</d2p1:BackgroundChunks>
      <d2p1:BackgroundSkip>2</d2p1:BackgroundSkip>
      <d2p1:ButterflyType>{btype}</d2p1:ButterflyType>
      <d2p1:ColorGradient xmlns:d3p1="http://schemas.datacontract.org/2004/07/VixenModules.App.ColorGradients">
        {make_color_gradient(color)}
      </d2p1:ColorGradient>
      <d2p1:ColorScheme>Gradient</d2p1:ColorScheme>
      <d2p1:Corner>BottomLeft</d2p1:Corner>
      <d2p1:Direction>Random</d2p1:Direction>
      <d2p1:Iterations>1</d2p1:Iterations>
      <d2p1:LevelCurve xmlns:d3p1="http://schemas.datacontract.org/2004/07/VixenModules.App.Curves">
        {make_curve([(0, 100), (100, 100)])}
      </d2p1:LevelCurve>
      <d2p1:Repeat>3</d2p1:Repeat>
      <d2p1:Speed>5</d2p1:Speed>
      <d2p1:SpeedCurve xmlns:d3p1="http://schemas.datacontract.org/2004/07/VixenModules.App.Curves">
        {make_curve([(0, 50), (100, 50)])}
      </d2p1:SpeedCurve>
    </d1p1:anyType>
'''

def make_spiral_data(effect_id, color):
    return f'''    <d1p1:anyType xmlns:d2p1="http://schemas.datacontract.org/2004/07/VixenModules.Effect.Spirals" i:type="d2p1:SpiralsData">
      <ModuleInstanceId>{effect_id}</ModuleInstanceId>
      <ModuleTypeId>{SPIRAL_TYPE_ID}</ModuleTypeId>
      <TargetPositioning xmlns="http://schemas.datacontract.org/2004/07/VixenModules.Effect.Effect">Strings</TargetPositioning>
      <d2p1:BandLength>0.5</d2p1:BandLength>
      <d2p1:Color xmlns:d3p1="http://schemas.datacontract.org/2004/07/Common.Controls.ColorManagement.ColorModels">
        <d3p1:_x>{color['x']}</d3p1:_x>
        <d3p1:_y>{color['y']}</d3p1:_y>
        <d3p1:_z>{color['z']}</d3p1:_z>
      </d2p1:Color>
      <d2p1:ColorType>Standard</d2p1:ColorType>
      <d2p1:Direction>Forward</d2p1:Direction>
      <d2p1:EndPosition>100</d2p1:EndPosition>
      <d2p1:LevelCurve xmlns:d3p1="http://schemas.datacontract.org/2004/07/VixenModules.App.Curves">
        {make_curve([(0, 100), (100, 100)])}
      </d2p1:LevelCurve>
      <d2p1:MovementType>Standard</d2p1:MovementType>
      <d2p1:Passes>5</d2p1:Passes>
      <d2p1:PulseLength>25</d2p1:PulseLength>
      <d2p1:PulsePercent>50</d2p1:PulsePercent>
      <d2p1:Reverse>false</d2p1:Reverse>
      <d2p1:Rotation>3D</d2p1:Rotation>
      <d2p1:SpiralCount>1</d2p1:SpiralCount>
      <d2p1:StartPosition>0</d2p1:StartPosition>
      <d2p1:Thickness>100</d2p1:Thickness>
      <d2p1:Grow>false</d2p1:Grow>
      <d2p1:Shrink>false</d2p1:Shrink>
    </d1p1:anyType>
'''

WIPE_DIRECTIONS = ['Horizontal', 'Vertical', 'DiagonalUp', 'Burst']

def make_wipe_data(effect_id, color, direction_idx=0):
    direction = WIPE_DIRECTIONS[direction_idx % len(WIPE_DIRECTIONS)]
    return f'''    <d1p1:anyType xmlns:d2p1="http://schemas.datacontract.org/2004/07/VixenModules.Effect.Wipe" i:type="d2p1:WipeData">
      <ModuleInstanceId>{effect_id}</ModuleInstanceId>
      <ModuleTypeId>{WIPE_TYPE_ID}</ModuleTypeId>
      <TargetPositioning xmlns="http://schemas.datacontract.org/2004/07/VixenModules.Effect.Effect">Strings</TargetPositioning>
      <d2p1:ColorGradient xmlns:d3p1="http://schemas.datacontract.org/2004/07/VixenModules.App.ColorGradients">
        {make_color_gradient(color)}
      </d2p1:ColorGradient>
      <d2p1:ColorHandling>ColorOverTime</d2p1:ColorHandling>
      <d2p1:Direction>{direction}</d2p1:Direction>
      <d2p1:PassCount>1</d2p1:PassCount>
      <d2p1:PulsePercent>33</d2p1:PulsePercent>
      <d2p1:PulseTime>1000</d2p1:PulseTime>
      <d2p1:ReverseCurve xmlns:d3p1="http://schemas.datacontract.org/2004/07/VixenModules.App.Curves">
        {make_curve([(0, 0), (100, 0)])}
      </d2p1:ReverseCurve>
      <d2p1:ReverseDirection>false</d2p1:ReverseDirection>
      <d2p1:WipeByCount>false</d2p1:WipeByCount>
      <d2p1:WipeMovement>Count</d2p1:WipeMovement>
      <d2p1:WipeOn>true</d2p1:WipeOn>
      <d2p1:WipeOff>true</d2p1:WipeOff>
    </d1p1:anyType>
'''

def make_effect_node(effect_id, target_node_id, start_time, duration):
    """Generate the effect node XML for a sequence element"""
    return f'''      <d1p1:EffectNode>
        <TargetNodes>
          <d1p1:guid>{target_node_id}</d1p1:guid>
        </TargetNodes>
        <StartTime>{start_time}</StartTime>
        <TimeSpan>{duration}</TimeSpan>
        <InstanceId>{effect_id}</InstanceId>
      </d1p1:EffectNode>
'''

# Find gaps and plan effects
print("\nFinding gaps in existing effects where beats occur...")

# Track which beats have been used
used_beats = set()
effects_to_add = []

# Process beats to find gaps
beat_idx = 0
while beat_idx < len(beats):
    beat_time = beats[beat_idx]
    
    # Check if this beat is in a gap
    if is_gap(beat_time, existing_effects):
        # Check beat properties
        is_downbeat = beat_time in downbeats
        is_strong = beat_time in strong_beats
        
        # Find an ending beat
        end_idx, end_time, duration = find_end_beat(
            beat_idx, beats, existing_effects, beat_data, 
            is_downbeat, is_strong
        )
        
        if end_time is not None:
            # Decide effect type based on beat type and duration
            if is_downbeat and duration >= 4.0:
                # Long downbeat effects: Spiral or Butterfly
                effect_type = random.choice(['spiral', 'butterfly'])
            elif is_downbeat or (is_strong and duration >= 2.0):
                # Medium downbeat/strong effects: Wipe, Twinkle
                effect_type = random.choice(['wipe', 'twinkle', 'butterfly'])
            elif is_strong:
                # Strong beat with shorter duration: Pulse or Twinkle
                effect_type = random.choice(['pulse', 'pulse', 'twinkle'])
            else:
                # Regular beat: Pulse
                effect_type = 'pulse'
            
            color = random.choice(COLORS)
            
            effects_to_add.append({
                'start_time': beat_time,
                'end_time': end_time,
                'duration': duration,
                'effect_type': effect_type,
                'color': color,
                'is_downbeat': is_downbeat,
                'is_strong': is_strong
            })
            
            # Skip to beat after end beat
            beat_idx = end_idx + 1
            continue
    
    beat_idx += 1

print(f"Planned {len(effects_to_add)} new effects")

# Count effect types
effect_counts = {}
for eff in effects_to_add:
    t = eff['effect_type']
    effect_counts[t] = effect_counts.get(t, 0) + 1
print("Effect type distribution:")
for t, c in sorted(effect_counts.items()):
    print(f"  {t}: {c}")

# Generate XML for new effects
effect_data_xml = ''
effect_nodes_xml = ''

for i, effect in enumerate(effects_to_add):
    effect_id = str(uuid.uuid4())
    start_time_iso = seconds_to_duration(effect['start_time'])
    duration_iso = seconds_to_duration(effect['duration'])
    color = effect['color']
    
    # Generate effect data based on type
    if effect['effect_type'] == 'pulse':
        effect_data_xml += make_pulse_data(effect_id, color)
    elif effect['effect_type'] == 'twinkle':
        effect_data_xml += make_twinkle_data(effect_id, color)
    elif effect['effect_type'] == 'butterfly':
        butterfly_type = random.randint(1, 5)
        effect_data_xml += make_butterfly_data(effect_id, color, butterfly_type)
    elif effect['effect_type'] == 'spiral':
        effect_data_xml += make_spiral_data(effect_id, color)
    elif effect['effect_type'] == 'wipe':
        direction_idx = random.randint(0, 3)
        effect_data_xml += make_wipe_data(effect_id, color, direction_idx)
    
    # Generate effect node
    effect_nodes_xml += make_effect_node(effect_id, ALL_PIXELS_NODE_ID, start_time_iso, duration_iso)

# Insert new effect data into content
# Find the position to insert effect data (before closing </EffectData>)
effect_data_end = content.find('</EffectData>')
if effect_data_end != -1:
    content = content[:effect_data_end] + effect_data_xml + content[effect_data_end:]
    print("Inserted effect data into EffectData section")

# Find the position to insert effect nodes (before closing </d1p1:ElementData>)
element_data_end = content.find('</d1p1:ElementData>')
if element_data_end != -1:
    content = content[:element_data_end] + effect_nodes_xml + content[element_data_end:]
    print("Inserted effect nodes into ElementData section")

# Write modified content
with open('The Greatest Show.tim', 'w') as f:
    f.write(content)

print(f"\nDone! Added {len(effects_to_add)} new effects to The Greatest Show.tim")
print("All effects start and end exactly on waveform-analyzed drum beats")
