#!/usr/bin/env python3
"""
Add effects that start and stop exactly on BeatNet-detected drum beats.

This script:
1. Uses BeatNet beat markers (beatnet_all_beats.txt)
2. Analyzes existing effects to find gaps
3. Only adds effects where there are no existing effects
4. Effects START and END exactly on drum beats
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

# Read BeatNet beat markers
beats = []
with open('beatnet_all_beats.txt', 'r') as f:
    for line in f:
        line = line.strip()
        if line:
            beats.append(float(line))

print(f"Loaded {len(beats)} beats from BeatNet analysis")

# Read BeatNet downbeats (measure starts)
downbeats = set()
with open('beatnet_downbeats.txt', 'r') as f:
    for line in f:
        line = line.strip()
        if line:
            downbeats.add(float(line))

print(f"Loaded {len(downbeats)} downbeats (measure starts)")

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

def find_end_beat(start_beat_idx, beats, existing_effects, min_duration=0.5, max_duration=10.0):
    """Find the best ending beat for an effect starting at start_beat_idx"""
    start_time = beats[start_beat_idx]
    
    # Look for beats within the duration range
    for i in range(start_beat_idx + 1, min(start_beat_idx + 20, len(beats))):
        end_time = beats[i]
        duration = end_time - start_time
        
        # Check if duration is within acceptable range
        if duration < min_duration:
            continue
        if duration > max_duration:
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

# Find beats that are in gaps (not covered by existing effects)
print("\nFinding beats in gaps...")

new_effect_data = []
new_effect_nodes = []
effects_added = 0
color_idx = 0
i = 0

while i < len(beats):
    beat_time = beats[i]
    
    # Check if this beat is in a gap
    if not is_gap(beat_time, existing_effects, threshold=0.3):
        i += 1
        continue
    
    # Find the ending beat for this effect
    # For pulses: short (up to 2 seconds)
    # For other effects: longer (up to 10 seconds)
    
    # Check if this is a downbeat (stronger beat for longer effects)
    is_downbeat = beat_time in downbeats
    
    if is_downbeat:
        # Longer effects on downbeats (measure starts)
        max_dur = 10.0
        min_dur = 2.0
        effect_choices = ['spiral', 'butterfly', 'twinkle', 'wipe']
    else:
        # Shorter effects on regular beats
        max_dur = 2.0
        min_dur = 0.5
        effect_choices = ['pulse']
    
    end_idx, end_time, duration = find_end_beat(i, beats, existing_effects, min_dur, max_dur)
    
    if end_idx is None:
        i += 1
        continue
    
    # Create the effect
    color = COLORS[color_idx % len(COLORS)]
    effect_id = str(uuid.uuid4())
    
    effect_type = random.choice(effect_choices)
    
    if effect_type == 'pulse':
        data = make_pulse_data(effect_id, color)
        type_id = PULSE_TYPE_ID
    elif effect_type == 'twinkle':
        data = make_twinkle_data(effect_id, color)
        type_id = TWINKLE_TYPE_ID
    elif effect_type == 'butterfly':
        btype = random.choice(['Type1', 'Type2', 'Type3', 'Type4', 'Type5'])
        data = make_butterfly_data(effect_id, color, btype)
        type_id = BUTTERFLY_TYPE_ID
    elif effect_type == 'spiral':
        data = make_spiral_data(effect_id, random.sample(COLORS, 3))
        type_id = SPIRAL_TYPE_ID
    elif effect_type == 'wipe':
        direction = random.choice(['Horizontal', 'Vertical', 'DiagonalUp', 'Burst'])
        data = make_wipe_data(effect_id, color, direction)
        type_id = WIPE_TYPE_ID
    
    new_effect_data.append(data)
    start_str = seconds_to_duration(beat_time)
    dur_str = seconds_to_duration(duration)
    new_effect_nodes.append(make_effect_node(effect_id, start_str, dur_str, type_id))
    
    effects_added += 1
    color_idx += 1
    
    # Skip to the end beat to avoid overlapping effects
    i = end_idx + 1
    
    # Update existing_effects to include this new effect
    existing_effects.append((beat_time, end_time))
    existing_effects.sort()

print(f"\nAdded {effects_added} new effects (all starting and ending on drum beats)")

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

print("\nSuccessfully added beat-aligned effects to The Greatest Show.tim!")

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
