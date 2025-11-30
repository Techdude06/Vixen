#!/usr/bin/env python3
"""
Add Pulse effects to The Greatest Show.tim

This script adds ONLY Pulse effects (the simplest effect type) at beat times,
using the exact XML structure from the existing working file.
"""

import uuid
import re

# Read stomps
stomps = []
with open('Greatestshow_Stomps.txt', 'r') as f:
    for line in f:
        parts = line.strip().split()
        if parts:
            stomps.append(float(parts[0]))

print(f"Loaded {len(stomps)} stomp times")

# Song duration
duration = 302.14
tempo_bpm = 156.6
beat_interval = 60.0 / tempo_bpm

# Read TIM file
with open('The Greatest Show.tim', 'r', encoding='utf-8') as f:
    tim_content = f.read()

def seconds_to_duration(seconds):
    """Convert seconds to ISO 8601 duration format."""
    if seconds < 60:
        return f"PT{seconds:.6f}S"
    else:
        mins = int(seconds // 60)
        secs = seconds % 60
        return f"PT{mins}M{secs:.6f}S"

# XYZ color values (same as existing effects in file)
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

# Pulse effect type ID (from existing file)
PULSE_TYPE_ID = 'cbd76d3b-c924-40ff-bad6-d1437b3dbdc0'

# Target node ID (All Pixels from the file)
ALL_PIXELS_NODE_ID = 'c1ea9007-f2ab-4faa-8e63-798ad274695e'

# Find insertion points
data_models_end = tim_content.find('</_dataModels>')
effect_nodes_end = tim_content.find('</_effectNodeSurrogates>')

if data_models_end == -1 or effect_nodes_end == -1:
    print("ERROR: Could not find insertion points")
    raise SystemExit(1)

def make_pulse_data(effect_id, color):
    """Generate Pulse effect data XML matching exact format from existing file."""
    return f'''    <d1p1:anyType xmlns:d2p1="http://schemas.datacontract.org/2004/07/VixenModules.Effect.Pulse" i:type="d2p1:PulseData">
      <ModuleInstanceId>{effect_id}</ModuleInstanceId>
      <ModuleTypeId>{PULSE_TYPE_ID}</ModuleTypeId>
      <TargetPositioning xmlns="http://schemas.datacontract.org/2004/07/VixenModules.Effect.Effect">Strings</TargetPositioning>
      <d2p1:ColorGradient xmlns:d3p1="http://schemas.datacontract.org/2004/07/VixenModules.App.ColorGradients">
        <d3p1:IsCurrentLibraryGradient>false</d3p1:IsCurrentLibraryGradient>
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
        <d3p1:_title i:nil="true" />
      </d2p1:ColorGradient>
      <d2p1:LevelCurve xmlns:d3p1="http://schemas.datacontract.org/2004/07/VixenModules.App.Curves">
        <d3p1:IsCurrentLibraryCurve>false</d3p1:IsCurrentLibraryCurve>
        <d3p1:Points xmlns:d4p1="http://schemas.datacontract.org/2004/07/ZedGraph">
          <d4p1:PointPair>
            <schema i:type="a:int">11</schema>
            <X i:type="a:double">0</X>
            <Y i:type="a:double">100</Y>
            <schema2 i:type="a:int">11</schema2>
            <Z i:type="a:double">0</Z>
            <Tag i:nil="true" />
          </d4p1:PointPair>
          <d4p1:PointPair>
            <schema i:type="a:int">11</schema>
            <X i:type="a:double">100</X>
            <Y i:type="a:double">0</Y>
            <schema2 i:type="a:int">11</schema2>
            <Z i:type="a:double">0</Z>
            <Tag i:nil="true" />
          </d4p1:PointPair>
        </d3p1:Points>
        <d3p1:_libraryReferenceName i:nil="true" />
      </d2p1:LevelCurve>
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

# Generate effects - only add every 4th beat (on measure) to avoid overloading
new_effect_data = []
new_effect_nodes = []
count = 0

for i, beat_time in enumerate(stomps):
    # Only add effects every 4 beats (on measures)
    if i % 4 != 0:
        continue
        
    if beat_time >= duration - 1:
        continue
    
    effect_id = str(uuid.uuid4())
    color = COLORS[count % len(COLORS)]
    
    # Effect duration - 2 beats
    effect_duration = beat_interval * 2
    
    start_time = seconds_to_duration(beat_time)
    time_span = seconds_to_duration(effect_duration)
    
    new_effect_data.append(make_pulse_data(effect_id, color))
    new_effect_nodes.append(make_effect_node(effect_id, start_time, time_span, PULSE_TYPE_ID))
    count += 1

print(f"Generated {count} Pulse effects")

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

print("Successfully added Pulse effects to The Greatest Show.tim!")
