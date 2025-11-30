#!/usr/bin/env python3
"""
Add varied effects to The Greatest Show.tim

This script adds varied effect types (Pulse, Twinkle, Butterfly, Spiral, Wipe) 
throughout the song, ensuring no gap longer than 1 second without an effect.

Requirements:
- Pulse effects: up to 2 seconds
- Non-pulse effects: up to 10 seconds
- No time gap > 1 second without an effect
- Use varied colors
"""

import uuid
import random

# Read original stomps file for beat timing
stomps = []
with open('Greatestshow_Stomps.txt', 'r') as f:
    for line in f:
        parts = line.strip().split()
        if parts:
            stomps.append(float(parts[0]))

print(f"Loaded {len(stomps)} stomp times")

# Song info
DURATION = 302.14
TEMPO_BPM = 156.6
BEAT_INTERVAL = 60.0 / TEMPO_BPM

# Read original TIM file
with open('The Greatest Show.tim', 'r', encoding='utf-8') as f:
    tim_content = f.read()

def seconds_to_duration(seconds):
    """Convert seconds to ISO 8601 duration format."""
    if seconds < 60:
        return f"PT{seconds:.7f}S"
    else:
        mins = int(seconds // 60)
        secs = seconds % 60
        return f"PT{mins}M{secs:.7f}S"

# Colors in XYZ format (from Show Yourself.tim)
COLORS = [
    {'x': 41.24564394, 'y': 21.26729007, 'z': 1.93339082},    # red
    {'x': 18.05, 'y': 7.22, 'z': 95.05},                       # blue  
    {'x': 35.76, 'y': 71.52, 'z': 11.92},                      # green
    {'x': 77.0, 'y': 92.78, 'z': 13.85},                       # yellow
    {'x': 13.80, 'y': 6.16, 'z': 43.59},                       # purple
    {'x': 59.01, 'y': 56.80, 'z': 7.85},                       # orange
    {'x': 95.05, 'y': 100.0, 'z': 108.88},                     # white
    {'x': 42.35, 'y': 55.82, 'z': 103.15},                     # light blue
    {'x': 51.31, 'y': 73.74, 'z': 106.14},                     # cyan
    {'x': 28.18, 'y': 27.47, 'z': 98.43},                      # dark blue
]

# Effect Type IDs (from existing files)
PULSE_TYPE_ID = 'cbd76d3b-c924-40ff-bad6-d1437b3dbdc0'
TWINKLE_TYPE_ID = '83bdd6f7-19c7-4598-b8e3-7ce28c44e7db'
BUTTERFLY_TYPE_ID = 'e2ef89d5-c3b3-47e7-a776-f31b4193fc76'
SPIRAL_TYPE_ID = '3f629e8c-cd8d-467e-afab-1a3836b24342'
WIPE_TYPE_ID = '61746b54-a96c-4723-8bd6-39c7ea985f80'

# Target node ID (All Pixels from the original file)
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
    """Generate a curve XML snippet. Points is list of (x,y) tuples."""
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
    """Generate Pulse effect data XML."""
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
    """Generate Twinkle effect data XML."""
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
    """Generate Butterfly effect data XML."""
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
    """Generate Spiral effect data XML."""
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
    """Generate Wipe effect data XML."""
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
    """Generate effect node XML."""
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

# Find insertion points
data_models_end = tim_content.find('</_dataModels>')
effect_nodes_end = tim_content.find('</_effectNodeSurrogates>')

if data_models_end == -1 or effect_nodes_end == -1:
    print("ERROR: Could not find insertion points")
    raise SystemExit(1)

# Generate effects to fill the entire song
# Strategy: Use different effect types in rotation, ensuring continuous coverage
new_effect_data = []
new_effect_nodes = []

# Effect types with their IDs
effect_types = [
    ('pulse', PULSE_TYPE_ID, make_pulse_data),
    ('twinkle', TWINKLE_TYPE_ID, make_twinkle_data),
    ('butterfly', BUTTERFLY_TYPE_ID, lambda eid, c: make_butterfly_data(eid, c, random.choice(['Type1', 'Type2', 'Type3', 'Type4', 'Type5']))),
    ('spiral', SPIRAL_TYPE_ID, lambda eid, c: make_spiral_data(eid, random.sample(COLORS, 3))),
    ('wipe', WIPE_TYPE_ID, lambda eid, c: make_wipe_data(eid, c, random.choice(['Horizontal', 'Vertical', 'DiagonalUp', 'DiagonalDown', 'Burst']))),
]

# Start from 0 seconds and fill the entire song
current_time = 0.0
effect_count = 0
color_idx = 0

# Effect pattern: Pulse short, then longer effects, repeat
# Pattern: Pulse(2s), Twinkle(5s), Butterfly(7s), Spiral(8s), Wipe(6s), Pulse(1.5s), ...
effect_pattern = [
    ('pulse', 1.5),      # Pulse - short
    ('twinkle', 5.0),    # Twinkle - medium
    ('pulse', 1.2),      # Pulse - short
    ('butterfly', 6.0),  # Butterfly - long
    ('pulse', 2.0),      # Pulse - medium
    ('spiral', 8.0),     # Spiral - long
    ('pulse', 1.0),      # Pulse - short
    ('wipe', 5.0),       # Wipe - medium
    ('pulse', 1.8),      # Pulse - medium
    ('twinkle', 6.0),    # Twinkle - medium
    ('pulse', 1.5),      # Pulse - short
    ('butterfly', 7.0),  # Butterfly - long
    ('pulse', 1.3),      # Pulse - short
    ('wipe', 4.0),       # Wipe - medium
    ('pulse', 2.0),      # Pulse - medium
    ('spiral', 10.0),    # Spiral - long
]

pattern_idx = 0
while current_time < DURATION - 0.5:
    effect_name, base_duration = effect_pattern[pattern_idx % len(effect_pattern)]
    
    # Add some variation to duration (+/- 20%)
    duration = base_duration * (0.8 + random.random() * 0.4)
    
    # Cap durations according to requirements
    if effect_name == 'pulse':
        duration = min(duration, 2.0)
    else:
        duration = min(duration, 10.0)
    
    # Make sure we don't exceed song length
    if current_time + duration > DURATION:
        duration = DURATION - current_time
        if duration < 0.3:
            break
    
    effect_id = str(uuid.uuid4())
    color = COLORS[color_idx % len(COLORS)]
    color_idx += 1
    
    # Find the effect type
    type_id = None
    make_func = None
    for ename, tid, func in effect_types:
        if ename == effect_name:
            type_id = tid
            make_func = func
            break
    
    if type_id is None:
        print(f"WARNING: Unknown effect type {effect_name}")
        pattern_idx += 1
        continue
    
    # Create effect data
    new_effect_data.append(make_func(effect_id, color))
    
    # Create effect node
    start_time = seconds_to_duration(current_time)
    time_span = seconds_to_duration(duration)
    new_effect_nodes.append(make_effect_node(effect_id, start_time, time_span, type_id))
    
    effect_count += 1
    current_time += duration
    pattern_idx += 1

print(f"Generated {effect_count} new effects spanning {current_time:.1f} seconds")

# Insert effect data
insert_data = '\n'.join(new_effect_data)
tim_content = tim_content[:data_models_end] + insert_data + '\n  ' + tim_content[data_models_end:]

# Recalculate effect_nodes_end after insertion
effect_nodes_end = tim_content.find('</_effectNodeSurrogates>')
insert_nodes = '\n'.join(new_effect_nodes)
tim_content = tim_content[:effect_nodes_end] + insert_nodes + '\n  ' + tim_content[effect_nodes_end:]

# Save
with open('The Greatest Show.tim', 'w', encoding='utf-8') as f:
    f.write(tim_content)

print("Successfully added varied effects to The Greatest Show.tim!")

# Count effect types
pulse_count = sum(1 for d in new_effect_data if 'PulseData' in d)
twinkle_count = sum(1 for d in new_effect_data if 'TwinkleData' in d)
butterfly_count = sum(1 for d in new_effect_data if 'ButterflyData' in d)
spiral_count = sum(1 for d in new_effect_data if 'SpiralData' in d)
wipe_count = sum(1 for d in new_effect_data if 'WipeData' in d)

print(f"\nEffect breakdown:")
print(f"  Pulse: {pulse_count}")
print(f"  Twinkle: {twinkle_count}")
print(f"  Butterfly: {butterfly_count}")
print(f"  Spiral: {spiral_count}")
print(f"  Wipe: {wipe_count}")
