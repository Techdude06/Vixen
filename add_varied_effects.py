#!/usr/bin/env python3
"""
Add varied tempo-synced effects to The Greatest Show.tim
Uses effect types from Show Yourself.tim as reference
"""

import uuid

# Song tempo info
tempo_val = 156.6  # BPM
beat_interval = 60.0 / tempo_val
duration = 302.14

# Read stomps
stomps = []
with open('Greatestshow_Stomps.txt', 'r') as f:
    for line in f:
        parts = line.strip().split()
        if parts:
            stomps.append(float(parts[0]))

print(f"Using {len(stomps)} stomp times")

# Read TIM file
with open('The Greatest Show.tim', 'r', encoding='utf-8') as f:
    tim_content = f.read()

def seconds_to_duration(seconds):
    if seconds < 60:
        return f"PT{seconds}S"
    else:
        mins = int(seconds // 60)
        secs = seconds % 60
        return f"PT{mins}M{secs}S"

# Color presets (XYZ)
COLORS = [
    {'x': 41.24, 'y': 21.26, 'z': 1.93},    # red
    {'x': 18.05, 'y': 7.22, 'z': 95.05},    # blue  
    {'x': 35.76, 'y': 71.52, 'z': 11.92},   # green
    {'x': 77.0, 'y': 92.78, 'z': 13.85},    # yellow
    {'x': 13.80, 'y': 6.16, 'z': 43.59},    # purple
    {'x': 59.01, 'y': 56.80, 'z': 7.85},    # orange
    {'x': 95.05, 'y': 100.0, 'z': 108.88},  # white
    {'x': 53.81, 'y': 78.74, 'z': 106.97},  # cyan
]

# Effect Type IDs
EFFECT_TYPES = {
    'Pulse': 'cbd76d3b-c924-40ff-bad6-d1437b3dbdc0',
    'Wipe': '61746b54-a96c-4723-8bd6-39c7ea985f80',
    'Twinkle': '83bdd6f7-19c7-4598-b8e3-7ce28c44e7db',
    'Spiral': '3f629e8c-cd8d-467e-afab-1a3836b24342',
    'Butterfly': '09657ca9-2303-4870-b9f8-6b13b59f6e38',
}

# Target node
ALL_PIXELS_NODE_ID = 'c1ea9007-f2ab-4faa-8e63-798ad274695e'

# Find insertion points
data_models_end = tim_content.find('</_dataModels>')
effect_nodes_end = tim_content.find('</_effectNodeSurrogates>')

if data_models_end == -1 or effect_nodes_end == -1:
    print("ERROR: Could not find insertion points")
    raise SystemExit(1)

# Effect templates
def make_pulse(effect_id, color):
    return f'''    <d1p1:anyType xmlns:d2p1="http://schemas.datacontract.org/2004/07/VixenModules.Effect.Pulse" i:type="d2p1:PulseData">
      <ModuleInstanceId>{effect_id}</ModuleInstanceId>
      <ModuleTypeId>{EFFECT_TYPES['Pulse']}</ModuleTypeId>
      <TargetPositioning xmlns="http://schemas.datacontract.org/2004/07/VixenModules.Effect.Effect">Strings</TargetPositioning>
      <d2p1:ColorGradient xmlns:d3p1="http://schemas.datacontract.org/2004/07/VixenModules.App.ColorGradients">
        <d3p1:IsCurrentLibraryGradient>false</d3p1:IsCurrentLibraryGradient>
        <d3p1:_alphas><d3p1:AlphaPoint><d3p1:_focus>0.5</d3p1:_focus><d3p1:_position>0</d3p1:_position><d3p1:_alpha>1</d3p1:_alpha></d3p1:AlphaPoint><d3p1:AlphaPoint><d3p1:_focus>0.5</d3p1:_focus><d3p1:_position>1</d3p1:_position><d3p1:_alpha>1</d3p1:_alpha></d3p1:AlphaPoint></d3p1:_alphas>
        <d3p1:_colors><d3p1:ColorPoint><d3p1:_focus>0.5</d3p1:_focus><d3p1:_position>0</d3p1:_position><d3p1:_color xmlns:d6p1="http://schemas.datacontract.org/2004/07/Common.Controls.ColorManagement.ColorModels"><d6p1:_x>{color['x']}</d6p1:_x><d6p1:_y>{color['y']}</d6p1:_y><d6p1:_z>{color['z']}</d6p1:_z></d3p1:_color></d3p1:ColorPoint></d3p1:_colors>
        <d3p1:_gammacorrected>false</d3p1:_gammacorrected><d3p1:_libraryReferenceName></d3p1:_libraryReferenceName><d3p1:_title i:nil="true" />
      </d2p1:ColorGradient>
      <d2p1:LevelCurve xmlns:d3p1="http://schemas.datacontract.org/2004/07/VixenModules.App.Curves"><d3p1:IsCurrentLibraryCurve>false</d3p1:IsCurrentLibraryCurve><d3p1:Points xmlns:d4p1="http://schemas.datacontract.org/2004/07/ZedGraph"><d4p1:PointPair><schema i:type="a:int">11</schema><X i:type="a:double">0</X><Y i:type="a:double">100</Y><schema2 i:type="a:int">11</schema2><Z i:type="a:double">0</Z><Tag i:nil="true" /></d4p1:PointPair><d4p1:PointPair><schema i:type="a:int">11</schema><X i:type="a:double">100</X><Y i:type="a:double">0</Y><schema2 i:type="a:int">11</schema2><Z i:type="a:double">0</Z><Tag i:nil="true" /></d4p1:PointPair></d3p1:Points><d3p1:_libraryReferenceName i:nil="true" /></d2p1:LevelCurve>
    </d1p1:anyType>
'''

def make_wipe(effect_id, color, direction='Right'):
    return f'''    <d1p1:anyType xmlns:d2p1="http://schemas.datacontract.org/2004/07/VixenModules.Effect.Wipe" i:type="d2p1:WipeData">
      <ModuleInstanceId>{effect_id}</ModuleInstanceId>
      <ModuleTypeId>{EFFECT_TYPES['Wipe']}</ModuleTypeId>
      <TargetPositioning xmlns="http://schemas.datacontract.org/2004/07/VixenModules.Effect.Effect">Strings</TargetPositioning>
      <d2p1:ColorAcrossItemPerCount>true</d2p1:ColorAcrossItemPerCount>
      <d2p1:ColorGradient xmlns:d3p1="http://schemas.datacontract.org/2004/07/VixenModules.App.ColorGradients">
        <d3p1:IsCurrentLibraryGradient>false</d3p1:IsCurrentLibraryGradient>
        <d3p1:_alphas><d3p1:AlphaPoint><d3p1:_focus>0.5</d3p1:_focus><d3p1:_position>0</d3p1:_position><d3p1:_alpha>1</d3p1:_alpha></d3p1:AlphaPoint><d3p1:AlphaPoint><d3p1:_focus>0.5</d3p1:_focus><d3p1:_position>1</d3p1:_position><d3p1:_alpha>1</d3p1:_alpha></d3p1:AlphaPoint></d3p1:_alphas>
        <d3p1:_colors><d3p1:ColorPoint><d3p1:_focus>0.5</d3p1:_focus><d3p1:_position>0</d3p1:_position><d3p1:_color xmlns:d6p1="http://schemas.datacontract.org/2004/07/Common.Controls.ColorManagement.ColorModels"><d6p1:_x>{color['x']}</d6p1:_x><d6p1:_y>{color['y']}</d6p1:_y><d6p1:_z>{color['z']}</d6p1:_z></d3p1:_color></d3p1:ColorPoint></d3p1:_colors>
        <d3p1:_gammacorrected>false</d3p1:_gammacorrected><d3p1:_libraryReferenceName></d3p1:_libraryReferenceName><d3p1:_title i:nil="true" />
      </d2p1:ColorGradient>
      <d2p1:ColorHandling>GradientThroughWholeEffect</d2p1:ColorHandling>
      <d2p1:Curve xmlns:d3p1="http://schemas.datacontract.org/2004/07/VixenModules.App.Curves"><d3p1:IsCurrentLibraryCurve>false</d3p1:IsCurrentLibraryCurve><d3p1:Points xmlns:d4p1="http://schemas.datacontract.org/2004/07/ZedGraph"><d4p1:PointPair><schema i:type="a:int">11</schema><X i:type="a:double">0</X><Y i:type="a:double">0</Y><schema2 i:type="a:int">11</schema2><Z i:type="a:double">0</Z><Tag i:nil="true" /></d4p1:PointPair><d4p1:PointPair><schema i:type="a:int">11</schema><X i:type="a:double">100</X><Y i:type="a:double">100</Y><schema2 i:type="a:int">11</schema2><Z i:type="a:double">0</Z><Tag i:nil="true" /></d4p1:PointPair></d3p1:Points><d3p1:_libraryReferenceName i:nil="true" /></d2p1:Curve>
      <d2p1:Direction>{direction}</d2p1:Direction>
      <d2p1:MovementType>Position</d2p1:MovementType><d2p1:PassCount>1</d2p1:PassCount><d2p1:Pulses>1</d2p1:Pulses><d2p1:ReverseDirection>false</d2p1:ReverseDirection><d2p1:WipeByCount>false</d2p1:WipeByCount><d2p1:WipeMovement>Count</d2p1:WipeMovement><d2p1:WipeOn>true</d2p1:WipeOn><d2p1:WipeOff>false</d2p1:WipeOff>
    </d1p1:anyType>
'''

def make_twinkle(effect_id, color):
    return f'''    <d1p1:anyType xmlns:d2p1="http://schemas.datacontract.org/2004/07/VixenModules.Effect.Twinkle" i:type="d2p1:TwinkleData">
      <ModuleInstanceId>{effect_id}</ModuleInstanceId>
      <ModuleTypeId>{EFFECT_TYPES['Twinkle']}</ModuleTypeId>
      <TargetPositioning xmlns="http://schemas.datacontract.org/2004/07/VixenModules.Effect.Effect">Strings</TargetPositioning>
      <d2p1:AverageCoverage>50</d2p1:AverageCoverage><d2p1:AveragePulseTime>400</d2p1:AveragePulseTime>
      <d2p1:ColorGradient xmlns:d3p1="http://schemas.datacontract.org/2004/07/VixenModules.App.ColorGradients">
        <d3p1:IsCurrentLibraryGradient>false</d3p1:IsCurrentLibraryGradient>
        <d3p1:_alphas><d3p1:AlphaPoint><d3p1:_focus>0.5</d3p1:_focus><d3p1:_position>0</d3p1:_position><d3p1:_alpha>1</d3p1:_alpha></d3p1:AlphaPoint><d3p1:AlphaPoint><d3p1:_focus>0.5</d3p1:_focus><d3p1:_position>1</d3p1:_position><d3p1:_alpha>1</d3p1:_alpha></d3p1:AlphaPoint></d3p1:_alphas>
        <d3p1:_colors><d3p1:ColorPoint><d3p1:_focus>0.5</d3p1:_focus><d3p1:_position>0</d3p1:_position><d3p1:_color xmlns:d6p1="http://schemas.datacontract.org/2004/07/Common.Controls.ColorManagement.ColorModels"><d6p1:_x>{color['x']}</d6p1:_x><d6p1:_y>{color['y']}</d6p1:_y><d6p1:_z>{color['z']}</d6p1:_z></d3p1:_color></d3p1:ColorPoint></d3p1:_colors>
        <d3p1:_gammacorrected>false</d3p1:_gammacorrected><d3p1:_libraryReferenceName></d3p1:_libraryReferenceName><d3p1:_title i:nil="true" />
      </d2p1:ColorGradient>
      <d2p1:ColorHandling>GradientForEachPulse</d2p1:ColorHandling><d2p1:DepthOfEffect>0</d2p1:DepthOfEffect><d2p1:IndividualChannels>true</d2p1:IndividualChannels><d2p1:LevelVariation>50</d2p1:LevelVariation><d2p1:MaximumLevel>1</d2p1:MaximumLevel><d2p1:MinimumLevel>0</d2p1:MinimumLevel><d2p1:PulseTimeVariation>30</d2p1:PulseTimeVariation>
      <d2p1:StaticColor xmlns:d3p1="http://schemas.datacontract.org/2004/07/System.Drawing"><d3p1:knownColor>164</d3p1:knownColor><d3p1:name i:nil="true" /><d3p1:state>1</d3p1:state><d3p1:value>0</d3p1:value></d2p1:StaticColor>
    </d1p1:anyType>
'''

def make_spiral(effect_id, color1, color2):
    return f'''    <d1p1:anyType xmlns:d2p1="http://schemas.datacontract.org/2004/07/VixenModules.Effect.Spiral" i:type="d2p1:SpiralData">
      <ModuleInstanceId>{effect_id}</ModuleInstanceId>
      <ModuleTypeId>{EFFECT_TYPES['Spiral']}</ModuleTypeId>
      <TargetPositioning xmlns="http://schemas.datacontract.org/2004/07/VixenModules.Effect.Effect">Strings</TargetPositioning>
      <d2p1:Blend>true</d2p1:Blend>
      <d2p1:Colors xmlns:d3p1="http://schemas.datacontract.org/2004/07/VixenModules.App.ColorGradients">
        <d3p1:ColorGradient><d3p1:IsCurrentLibraryGradient>false</d3p1:IsCurrentLibraryGradient><d3p1:_alphas><d3p1:AlphaPoint><d3p1:_focus>0.5</d3p1:_focus><d3p1:_position>0</d3p1:_position><d3p1:_alpha>1</d3p1:_alpha></d3p1:AlphaPoint><d3p1:AlphaPoint><d3p1:_focus>0.5</d3p1:_focus><d3p1:_position>1</d3p1:_position><d3p1:_alpha>1</d3p1:_alpha></d3p1:AlphaPoint></d3p1:_alphas><d3p1:_colors><d3p1:ColorPoint><d3p1:_focus>0.5</d3p1:_focus><d3p1:_position>0</d3p1:_position><d3p1:_color xmlns:d7p1="http://schemas.datacontract.org/2004/07/Common.Controls.ColorManagement.ColorModels"><d7p1:_x>{color1['x']}</d7p1:_x><d7p1:_y>{color1['y']}</d7p1:_y><d7p1:_z>{color1['z']}</d7p1:_z></d3p1:_color></d3p1:ColorPoint></d3p1:_colors><d3p1:_gammacorrected>false</d3p1:_gammacorrected><d3p1:_libraryReferenceName></d3p1:_libraryReferenceName><d3p1:_title i:nil="true" /></d3p1:ColorGradient>
        <d3p1:ColorGradient><d3p1:IsCurrentLibraryGradient>false</d3p1:IsCurrentLibraryGradient><d3p1:_alphas><d3p1:AlphaPoint><d3p1:_focus>0.5</d3p1:_focus><d3p1:_position>0</d3p1:_position><d3p1:_alpha>1</d3p1:_alpha></d3p1:AlphaPoint><d3p1:AlphaPoint><d3p1:_focus>0.5</d3p1:_focus><d3p1:_position>1</d3p1:_position><d3p1:_alpha>1</d3p1:_alpha></d3p1:AlphaPoint></d3p1:_alphas><d3p1:_colors><d3p1:ColorPoint><d3p1:_focus>0.5</d3p1:_focus><d3p1:_position>0</d3p1:_position><d3p1:_color xmlns:d7p1="http://schemas.datacontract.org/2004/07/Common.Controls.ColorManagement.ColorModels"><d7p1:_x>{color2['x']}</d7p1:_x><d7p1:_y>{color2['y']}</d7p1:_y><d7p1:_z>{color2['z']}</d7p1:_z></d3p1:_color></d3p1:ColorPoint></d3p1:_colors><d3p1:_gammacorrected>false</d3p1:_gammacorrected><d3p1:_libraryReferenceName></d3p1:_libraryReferenceName><d3p1:_title i:nil="true" /></d3p1:ColorGradient>
      </d2p1:Colors>
      <d2p1:Direction>Forward</d2p1:Direction><d2p1:Grow>false</d2p1:Grow>
      <d2p1:LevelCurve xmlns:d3p1="http://schemas.datacontract.org/2004/07/VixenModules.App.Curves"><d3p1:IsCurrentLibraryCurve>false</d3p1:IsCurrentLibraryCurve><d3p1:Points xmlns:d4p1="http://schemas.datacontract.org/2004/07/ZedGraph"><d4p1:PointPair><schema i:type="a:int">11</schema><X i:type="a:double">0</X><Y i:type="a:double">100</Y><schema2 i:type="a:int">11</schema2><Z i:type="a:double">0</Z><Tag i:nil="true" /></d4p1:PointPair><d4p1:PointPair><schema i:type="a:int">11</schema><X i:type="a:double">100</X><Y i:type="a:double">100</Y><schema2 i:type="a:int">11</schema2><Z i:type="a:double">0</Z><Tag i:nil="true" /></d4p1:PointPair></d3p1:Points><d3p1:_libraryReferenceName i:nil="true" /></d2p1:LevelCurve>
      <d2p1:MovementCurve xmlns:d3p1="http://schemas.datacontract.org/2004/07/VixenModules.App.Curves"><d3p1:IsCurrentLibraryCurve>false</d3p1:IsCurrentLibraryCurve><d3p1:Points xmlns:d4p1="http://schemas.datacontract.org/2004/07/ZedGraph"><d4p1:PointPair><schema i:type="a:int">11</schema><X i:type="a:double">0</X><Y i:type="a:double">0</Y><schema2 i:type="a:int">11</schema2><Z i:type="a:double">0</Z><Tag i:nil="true" /></d4p1:PointPair><d4p1:PointPair><schema i:type="a:int">11</schema><X i:type="a:double">100</X><Y i:type="a:double">100</Y><schema2 i:type="a:int">11</schema2><Z i:type="a:double">0</Z><Tag i:nil="true" /></d4p1:PointPair></d3p1:Points><d3p1:_libraryReferenceName i:nil="true" /></d2p1:MovementCurve>
      <d2p1:MovementType>Speed</d2p1:MovementType><d2p1:Repeat>1</d2p1:Repeat><d2p1:Rotation>Forward</d2p1:Rotation><d2p1:Show3D>false</d2p1:Show3D>
      <d2p1:SpeedCurve xmlns:d3p1="http://schemas.datacontract.org/2004/07/VixenModules.App.Curves"><d3p1:IsCurrentLibraryCurve>false</d3p1:IsCurrentLibraryCurve><d3p1:Points xmlns:d4p1="http://schemas.datacontract.org/2004/07/ZedGraph"><d4p1:PointPair><schema i:type="a:int">11</schema><X i:type="a:double">0</X><Y i:type="a:double">50</Y><schema2 i:type="a:int">11</schema2><Z i:type="a:double">0</Z><Tag i:nil="true" /></d4p1:PointPair><d4p1:PointPair><schema i:type="a:int">11</schema><X i:type="a:double">100</X><Y i:type="a:double">50</Y><schema2 i:type="a:int">11</schema2><Z i:type="a:double">0</Z><Tag i:nil="true" /></d4p1:PointPair></d3p1:Points><d3p1:_libraryReferenceName i:nil="true" /></d2p1:SpeedCurve>
      <d2p1:Thickness>10</d2p1:Thickness>
    </d1p1:anyType>
'''

def make_butterfly(effect_id, color1, color2):
    return f'''    <d1p1:anyType xmlns:d2p1="http://schemas.datacontract.org/2004/07/VixenModules.Effect.Butterfly" i:type="d2p1:ButterflyData">
      <ModuleInstanceId>{effect_id}</ModuleInstanceId>
      <ModuleTypeId>{EFFECT_TYPES['Butterfly']}</ModuleTypeId>
      <TargetPositioning xmlns="http://schemas.datacontract.org/2004/07/VixenModules.Effect.Effect">Strings</TargetPositioning>
      <d2p1:BackgroundChunks>1</d2p1:BackgroundChunks><d2p1:BackgroundSkip>2</d2p1:BackgroundSkip><d2p1:ButterflyType>Type1</d2p1:ButterflyType><d2p1:ColorScheme>Gradient</d2p1:ColorScheme>
      <d2p1:Colors xmlns:d3p1="http://schemas.datacontract.org/2004/07/VixenModules.App.ColorGradients">
        <d3p1:GradientLevelPair>
          <d3p1:ColorGradient><d3p1:IsCurrentLibraryGradient>false</d3p1:IsCurrentLibraryGradient><d3p1:_alphas><d3p1:AlphaPoint><d3p1:_focus>0.5</d3p1:_focus><d3p1:_position>0</d3p1:_position><d3p1:_alpha>1</d3p1:_alpha></d3p1:AlphaPoint><d3p1:AlphaPoint><d3p1:_focus>0.5</d3p1:_focus><d3p1:_position>1</d3p1:_position><d3p1:_alpha>1</d3p1:_alpha></d3p1:AlphaPoint></d3p1:_alphas><d3p1:_colors><d3p1:ColorPoint><d3p1:_focus>0.5</d3p1:_focus><d3p1:_position>0</d3p1:_position><d3p1:_color xmlns:d8p1="http://schemas.datacontract.org/2004/07/Common.Controls.ColorManagement.ColorModels"><d8p1:_x>{color1['x']}</d8p1:_x><d8p1:_y>{color1['y']}</d8p1:_y><d8p1:_z>{color1['z']}</d8p1:_z></d3p1:_color></d3p1:ColorPoint><d3p1:ColorPoint><d3p1:_focus>0.5</d3p1:_focus><d3p1:_position>1</d3p1:_position><d3p1:_color xmlns:d8p1="http://schemas.datacontract.org/2004/07/Common.Controls.ColorManagement.ColorModels"><d8p1:_x>{color2['x']}</d8p1:_x><d8p1:_y>{color2['y']}</d8p1:_y><d8p1:_z>{color2['z']}</d8p1:_z></d3p1:_color></d3p1:ColorPoint></d3p1:_colors><d3p1:_gammacorrected>false</d3p1:_gammacorrected><d3p1:_libraryReferenceName></d3p1:_libraryReferenceName><d3p1:_title i:nil="true" /></d3p1:ColorGradient>
          <d3p1:Curve xmlns:d5p1="http://schemas.datacontract.org/2004/07/VixenModules.App.Curves"><d5p1:IsCurrentLibraryCurve>false</d5p1:IsCurrentLibraryCurve><d5p1:Points xmlns:d6p1="http://schemas.datacontract.org/2004/07/ZedGraph"><d6p1:PointPair><schema i:type="a:int">11</schema><X i:type="a:double">0</X><Y i:type="a:double">100</Y><schema2 i:type="a:int">11</schema2><Z i:type="a:double">0</Z><Tag i:nil="true" /></d6p1:PointPair><d6p1:PointPair><schema i:type="a:int">11</schema><X i:type="a:double">100</X><Y i:type="a:double">100</Y><schema2 i:type="a:int">11</schema2><Z i:type="a:double">0</Z><Tag i:nil="true" /></d6p1:PointPair></d5p1:Points><d5p1:_libraryReferenceName i:nil="true" /></d3p1:Curve>
        </d3p1:GradientLevelPair>
      </d2p1:Colors>
      <d2p1:Direction>Forward</d2p1:Direction><d2p1:Iterations>1</d2p1:Iterations><d2p1:Repeat>1</d2p1:Repeat>
      <d2p1:SpeedCurve xmlns:d3p1="http://schemas.datacontract.org/2004/07/VixenModules.App.Curves"><d3p1:IsCurrentLibraryCurve>false</d3p1:IsCurrentLibraryCurve><d3p1:Points xmlns:d4p1="http://schemas.datacontract.org/2004/07/ZedGraph"><d4p1:PointPair><schema i:type="a:int">11</schema><X i:type="a:double">0</X><Y i:type="a:double">25</Y><schema2 i:type="a:int">11</schema2><Z i:type="a:double">0</Z><Tag i:nil="true" /></d4p1:PointPair><d4p1:PointPair><schema i:type="a:int">11</schema><X i:type="a:double">100</X><Y i:type="a:double">25</Y><schema2 i:type="a:int">11</schema2><Z i:type="a:double">0</Z><Tag i:nil="true" /></d4p1:PointPair></d3p1:Points><d3p1:_libraryReferenceName i:nil="true" /></d2p1:SpeedCurve>
    </d1p1:anyType>
'''

# Generate effects with variety
new_effect_data = []
new_effect_nodes = []

# Define effect distribution pattern
# Weight: Pulse (common), Wipe (emphasis), Twinkle/Spiral/Butterfly (special)
# Valid WipeDirection values: Horizontal, Vertical, Burst, Circle, CurtainOpen, DiagonalUp, Dimaond
EFFECT_DISTRIBUTION = {
    'pattern': ['Pulse', 'Wipe', 'Twinkle', 'Spiral', 'Butterfly', 'Pulse', 'Wipe', 'Pulse'],
    'wipe_directions': ['Horizontal', 'Vertical', 'DiagonalUp', 'Burst']
}
effect_counts = {'Pulse': 0, 'Wipe': 0, 'Twinkle': 0, 'Spiral': 0, 'Butterfly': 0}

for i, beat_time in enumerate(stomps):
    if beat_time >= duration - 1:
        continue
    
    effect_id = str(uuid.uuid4())
    color_idx = i % len(COLORS)
    color = COLORS[color_idx]
    color2 = COLORS[(color_idx + 3) % len(COLORS)]
    
    # Vary effect duration
    if i % 8 == 0:
        effect_duration = beat_interval * 4
    elif i % 4 == 0:
        effect_duration = beat_interval * 2
    else:
        effect_duration = beat_interval * 1.5
    
    effect_type = EFFECT_DISTRIBUTION['pattern'][i % len(EFFECT_DISTRIBUTION['pattern'])]
    
    if effect_type == 'Pulse':
        effect_data = make_pulse(effect_id, color)
        type_id = EFFECT_TYPES['Pulse']
    elif effect_type == 'Wipe':
        direction = EFFECT_DISTRIBUTION['wipe_directions'][i % len(EFFECT_DISTRIBUTION['wipe_directions'])]
        effect_data = make_wipe(effect_id, color, direction)
        type_id = EFFECT_TYPES['Wipe']
    elif effect_type == 'Twinkle':
        effect_data = make_twinkle(effect_id, color)
        type_id = EFFECT_TYPES['Twinkle']
        effect_duration = beat_interval * 4
    elif effect_type == 'Spiral':
        effect_data = make_spiral(effect_id, color, color2)
        type_id = EFFECT_TYPES['Spiral']
        effect_duration = beat_interval * 4
    elif effect_type == 'Butterfly':
        effect_data = make_butterfly(effect_id, color, color2)
        type_id = EFFECT_TYPES['Butterfly']
        effect_duration = beat_interval * 4
    
    effect_counts[effect_type] += 1
    
    start_time = seconds_to_duration(beat_time)
    time_span = seconds_to_duration(effect_duration)
    
    effect_node = f'''    <EffectNodeSurrogate>
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
    
    new_effect_data.append(effect_data)
    new_effect_nodes.append(effect_node)

print(f"Generated effects:")
for etype, count in effect_counts.items():
    print(f"  {etype}: {count}")
print(f"  Total: {sum(effect_counts.values())}")

# Insert effects into the TIM content
# Note: We recalculate effect_nodes_end after modifying tim_content
# because the string positions shift after the first insertion
insert_data = '\n'.join(new_effect_data)
tim_content = tim_content[:data_models_end] + insert_data + '\n  ' + tim_content[data_models_end:]

# Recalculate position after content modification
effect_nodes_end = tim_content.find('</_effectNodeSurrogates>')
insert_nodes = '\n'.join(new_effect_nodes)
tim_content = tim_content[:effect_nodes_end] + insert_nodes + '\n  ' + tim_content[effect_nodes_end:]

# Save
with open('The Greatest Show.tim', 'w', encoding='utf-8') as f:
    f.write(tim_content)

print(f"\nSuccessfully added varied tempo-synced effects!")
