# Define the feature columns that your XGBoost model expects
# Based on your training code, these are the columns after excluding the specified ones

feature_columns = [
    # Mixer Module (13 parameters)
    'Mixer/OpenDumpValve', 'Mixer/Level', 'Mixer/Temperature', 'Mixer/OpenOutlet',
    'Mixer/Fill1On', 'Mixer/Fill2On', 'Mixer/Fill3On', 'Mixer/Fill4On', 'Mixer/Fill5On',
    'Mixer/TurnMixerOn', 'Mixer/MixerIsOn', 'Mixer/InFlowMix', 'Mixer/OutFlowMix',
    
    # Pasteurizer Module (8 parameters)
    'Pasteurizer/OpenDumpValve', 'Pasteurizer/Level', 'Pasteurizer/OpenOutlet',
    'Pasteurizer/HeaterOn', 'Pasteurizer/Temperature', 'Pasteurizer/CoolerOn',
    'Pasteurizer/InFlowMix', 'Pasteurizer/OutFlowMix',
    
    # Homogenizer Module (4 parameters)
    'Homogenizer/ParticleSize', 'Homogenizer/HomogenizerOn',
    'Homogenizer/Valve1/InFlowMix', 'Homogenizer/Valve2/OutFlowMix',
    
    # AgeingCooling Module (7 parameters)
    'AgeingCooling/OpenDumpValve', 'AgeingCooling/Level', 'AgeingCooling/Temperature',
    'AgeingCooling/InFlowMix', 'AgeingCooling/OpenOutlet', 'AgeingCooling/AgeingCoolingOn',
    'AgeingCooling/OutFlowMix',
    
    # DynamicFreezer Module (16 parameters)
    'DynamicFreezer/OpenDumpValve', 'DynamicFreezer/Level', 'DynamicFreezer/OpenOutlet',
    'DynamicFreezer/HeaterOn', 'DynamicFreezer/Temperature', 'DynamicFreezer/SolidFlavoringOn',
    'DynamicFreezer/LiquidFlavoringOn', 'DynamicFreezer/FreezerOn', 'DynamicFreezer/DasherOn',
    'DynamicFreezer/Overrun', 'DynamicFreezer/SendTestValues', 'DynamicFreezer/ParticleSize',
    'DynamicFreezer/BarrelRotationSpeed', 'DynamicFreezer/PasteurizationUnits',
    'DynamicFreezer/InFlowMix', 'DynamicFreezer/OutFlowMix',
    
    # Hardening Module (6 parameters)
    'Hardening/Packages', 'Hardening/OpenDumpValve', 'Hardening/Temperature',
    'Hardening/HardeningOn', 'Hardening/FinishBatchOn', 'Hardening/InFlowMix'
]

print(f"Total input features required: {len(feature_columns)}")
print("\nFeature columns:")
for i, col in enumerate(feature_columns, 1):
    print(f"{i:2d}. {col}")

# Output mappings
anomaly_mapping = {0: "Normal", 1: "Freeze", 2: "Step", 3: "Ramp"}
print(f"\nOutput mappings:")
print("Anomaly Types:", anomaly_mapping)