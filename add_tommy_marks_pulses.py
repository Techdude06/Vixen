#!/usr/bin/env python3
"""
Add Pulse effects to TIM file using Tommy's Marks for timing.
Alternates between all colors found in the original TIM file.
"""

import re
import uuid

# Read Tommy's Marks (beat timestamps)
def read_tommy_marks(filename):
    """Read beat timestamps from Tommy's Marks.txt"""
    marks = []
    with open(filename, 'r') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 1:
                try:
                    time_sec = float(parts[0])
                    marks.append(time_sec)
                except ValueError:
                    continue
    return marks

# Extract unique colors from TIM file
def extract_colors(tim_content):
    """Extract unique XYZ colors from the TIM file"""
    color_pattern = r'<d3p1:_color[^>]*>\s*<d6p1:_x>([^<]+)</d6p1:_x>\s*<d6p1:_y>([^<]+)</d6p1:_y>\s*<d6p1:_z>([^<]+)</d6p1:_z>\s*</d3p1:_color>'
    colors = re.findall(color_pattern, tim_content)
    
    # Get unique colors (rounded)
    unique_colors = []
    seen = set()
    for x, y, z in colors:
        rounded = (round(float(x), 1), round(float(y), 1), round(float(z), 1))
        if rounded not in seen:
            seen.add(rounded)
            unique_colors.append((float(x), float(y), float(z)))
    
    return unique_colors

# Convert seconds to ISO 8601 duration format
def seconds_to_duration(seconds):
    """Convert seconds to PT format (e.g., PT1.5S)"""
    return f"PT{seconds}S"

# Generate Pulse effect data XML
def generate_pulse_data(instance_id, color_xyz):
    """Generate PulseData XML block for effect data"""
    x, y, z = color_xyz
    return f'''    <d1p1:anyType xmlns:d2p1="http://schemas.datacontract.org/2004/07/VixenModules.Effect.Pulse" i:type="d2p1:PulseData">
      <ModuleInstanceId>{instance_id}</ModuleInstanceId>
      <ModuleTypeId>cbd76d3b-c924-40ff-bad6-d1437b3dbdc0</ModuleTypeId>
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
              <d6p1:_x>{x}</d6p1:_x>
              <d6p1:_y>{y}</d6p1:_y>
              <d6p1:_z>{z}</d6p1:_z>
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
        <d3p1:_libraryReferenceName></d3p1:_libraryReferenceName>
      </d2p1:LevelCurve>
    </d1p1:anyType>'''

# Generate EffectNodeSurrogate XML
def generate_effect_node(instance_id, start_time, duration):
    """Generate EffectNodeSurrogate XML block"""
    return f'''    <EffectNodeSurrogate>
      <InstanceId>{instance_id}</InstanceId>
      <StartTime>{seconds_to_duration(start_time)}</StartTime>
      <TargetNodes>
        <ChannelNodeReferenceSurrogate>
          <Name>All Pixels</Name>
          <NodeId>c1ea9007-f2ab-4faa-8e63-798ad274695e</NodeId>
        </ChannelNodeReferenceSurrogate>
      </TargetNodes>
      <TimeSpan>{seconds_to_duration(duration)}</TimeSpan>
      <TypeId>cbd76d3b-c924-40ff-bad6-d1437b3dbdc0</TypeId>
    </EffectNodeSurrogate>'''

def main():
    # Read Tommy's Marks
    marks = read_tommy_marks("Tommy's Marks.txt")
    print(f"Read {len(marks)} beat marks from Tommy's Marks.txt")
    
    # Read original TIM file
    with open("The Greatest Show.tim", "r", encoding="utf-8") as f:
        tim_content = f.read()
    
    # Extract colors
    colors = extract_colors(tim_content)
    print(f"Found {len(colors)} unique colors in TIM file:")
    for i, (x, y, z) in enumerate(colors):
        print(f"  {i+1}. XYZ({x:.2f}, {y:.2f}, {z:.2f})")
    
    # Generate effects for each mark
    pulse_data_blocks = []
    effect_node_blocks = []
    
    for i, start_time in enumerate(marks):
        # Alternate colors
        color = colors[i % len(colors)]
        
        # Calculate duration to next beat (or default to 0.5s for last beat)
        if i < len(marks) - 1:
            duration = min(marks[i + 1] - start_time, 2.0)  # Cap at 2 seconds
        else:
            duration = 0.5  # Default for last beat
        
        # Ensure minimum duration
        duration = max(duration, 0.1)
        
        # Generate unique instance ID
        instance_id = str(uuid.uuid4())
        
        # Generate XML blocks
        pulse_data_blocks.append(generate_pulse_data(instance_id, color))
        effect_node_blocks.append(generate_effect_node(instance_id, start_time, duration))
    
    print(f"\nGenerated {len(pulse_data_blocks)} Pulse effects")
    
    # Insert effects into TIM file
    # Find insertion points
    data_models_end = tim_content.rfind("</d1p1:anyType>\n  </_dataModels>")
    if data_models_end == -1:
        print("ERROR: Could not find _dataModels end marker")
        return
    
    effect_nodes_end = tim_content.rfind("</EffectNodeSurrogate>\n  </_effectNodeSurrogates>")
    if effect_nodes_end == -1:
        print("ERROR: Could not find _effectNodeSurrogates end marker")
        return
    
    # Insert pulse data blocks before _dataModels closing tag
    insert_pos1 = data_models_end + len("</d1p1:anyType>")
    pulse_data_insert = "\n" + "\n".join(pulse_data_blocks)
    
    new_content = tim_content[:insert_pos1] + pulse_data_insert + tim_content[insert_pos1:]
    
    # Recalculate position after first insertion
    effect_nodes_end = new_content.rfind("</EffectNodeSurrogate>\n  </_effectNodeSurrogates>")
    insert_pos2 = effect_nodes_end + len("</EffectNodeSurrogate>")
    effect_node_insert = "\n" + "\n".join(effect_node_blocks)
    
    new_content = new_content[:insert_pos2] + effect_node_insert + new_content[insert_pos2:]
    
    # Write updated TIM file
    with open("The Greatest Show.tim", "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print(f"\nUpdated The Greatest Show.tim with {len(marks)} Pulse effects at Tommy's Marks")
    print(f"Colors alternate through {len(colors)} different colors")

if __name__ == "__main__":
    main()
