# data_generator.py - Generate simulated ice cream factory sensor data

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

class IceCreamDataGenerator:
    """
    Generates realistic ice cream factory sensor data for testing
    the anomaly detection system
    """
    
    def __init__(self, seed=42):
        np.random.seed(seed)
        self.feature_columns = [
            'Mixer/OpenDumpValve', 'Mixer/Level', 'Mixer/Temperature', 'Mixer/OpenOutlet',
            'Mixer/Fill1On', 'Mixer/Fill2On', 'Mixer/Fill3On', 'Mixer/Fill4On', 'Mixer/Fill5On',
            'Mixer/TurnMixerOn', 'Mixer/MixerIsOn', 'Mixer/InFlowMix', 'Mixer/OutFlowMix',
            'Pasteurizer/OpenDumpValve', 'Pasteurizer/Level', 'Pasteurizer/OpenOutlet',
            'Pasteurizer/HeaterOn', 'Pasteurizer/Temperature', 'Pasteurizer/CoolerOn',
            'Pasteurizer/InFlowMix', 'Pasteurizer/OutFlowMix',
            'Homogenizer/ParticleSize', 'Homogenizer/HomogenizerOn',
            'Homogenizer/Valve1/InFlowMix', 'Homogenizer/Valve2/OutFlowMix',
            'AgeingCooling/OpenDumpValve', 'AgeingCooling/Level', 'AgeingCooling/Temperature',
            'AgeingCooling/InFlowMix', 'AgeingCooling/OpenOutlet', 'AgeingCooling/AgeingCoolingOn',
            'AgeingCooling/OutFlowMix',
            'DynamicFreezer/OpenDumpValve', 'DynamicFreezer/Level', 'DynamicFreezer/OpenOutlet',
            'DynamicFreezer/HeaterOn', 'DynamicFreezer/Temperature', 'DynamicFreezer/SolidFlavoringOn',
            'DynamicFreezer/LiquidFlavoringOn', 'DynamicFreezer/FreezerOn', 'DynamicFreezer/DasherOn',
            'DynamicFreezer/Overrun', 'DynamicFreezer/SendTestValues', 'DynamicFreezer/ParticleSize',
            'DynamicFreezer/BarrelRotationSpeed', 'DynamicFreezer/PasteurizationUnits',
            'DynamicFreezer/InFlowMix', 'DynamicFreezer/OutFlowMix',
            'Hardening/Packages', 'Hardening/OpenDumpValve', 'Hardening/Temperature',
            'Hardening/HardeningOn', 'Hardening/FinishBatchOn', 'Hardening/InFlowMix'
        ]
    
    def generate_normal_data(self, n_samples=100):
        """Generate normal operating condition data"""
        data = {}
        
        # Mixer parameters - normal operation
        data['Mixer/OpenDumpValve'] = np.zeros(n_samples)
        data['Mixer/Level'] = np.random.uniform(0.3, 0.9, n_samples)
        data['Mixer/Temperature'] = np.random.normal(276.5, 1.0, n_samples)
        data['Mixer/OpenOutlet'] = np.random.choice([0, 1], n_samples, p=[0.8, 0.2])
        
        for i in range(1, 6):
            data[f'Mixer/Fill{i}On'] = np.random.choice([0, 1], n_samples, p=[0.7, 0.3])
        
        data['Mixer/TurnMixerOn'] = np.ones(n_samples)
        data['Mixer/MixerIsOn'] = np.ones(n_samples)
        data['Mixer/InFlowMix'] = np.random.uniform(0, 5, n_samples)
        data['Mixer/OutFlowMix'] = np.random.uniform(0, 5, n_samples)
        
        # Pasteurizer parameters
        data['Pasteurizer/OpenDumpValve'] = np.zeros(n_samples)
        data['Pasteurizer/Level'] = np.random.uniform(0.2, 0.8, n_samples)
        data['Pasteurizer/OpenOutlet'] = np.random.choice([0, 1], n_samples, p=[0.9, 0.1])
        data['Pasteurizer/HeaterOn'] = np.ones(n_samples)
        data['Pasteurizer/Temperature'] = np.random.normal(276.8, 1.2, n_samples)
        data['Pasteurizer/CoolerOn'] = np.zeros(n_samples)
        data['Pasteurizer/InFlowMix'] = np.random.uniform(0, 3, n_samples)
        data['Pasteurizer/OutFlowMix'] = np.random.uniform(0, 3, n_samples)
        
        # Homogenizer parameters
        data['Homogenizer/ParticleSize'] = np.random.uniform(0.5, 2.0, n_samples)
        data['Homogenizer/HomogenizerOn'] = np.ones(n_samples)
        data['Homogenizer/Valve1/InFlowMix'] = np.random.uniform(0, 2, n_samples)
        data['Homogenizer/Valve2/OutFlowMix'] = np.random.uniform(0, 2, n_samples)
        
        # AgeingCooling parameters
        data['AgeingCooling/OpenDumpValve'] = np.zeros(n_samples)
        data['AgeingCooling/Level'] = np.random.uniform(0.1, 0.7, n_samples)
        data['AgeingCooling/Temperature'] = np.random.normal(276.7, 0.8, n_samples)
        data['AgeingCooling/InFlowMix'] = np.random.uniform(0, 2, n_samples)
        data['AgeingCooling/OpenOutlet'] = np.random.choice([0, 1], n_samples, p=[0.8, 0.2])
        data['AgeingCooling/AgeingCoolingOn'] = np.ones(n_samples)
        data['AgeingCooling/OutFlowMix'] = np.random.uniform(0, 2, n_samples)
        
        # DynamicFreezer parameters
        data['DynamicFreezer/OpenDumpValve'] = np.zeros(n_samples)
        data['DynamicFreezer/Level'] = np.random.uniform(0.2, 0.8, n_samples)
        data['DynamicFreezer/OpenOutlet'] = np.random.choice([0, 1], n_samples, p=[0.9, 0.1])
        data['DynamicFreezer/HeaterOn'] = np.zeros(n_samples)
        data['DynamicFreezer/Temperature'] = np.random.normal(277.2, 1.5, n_samples)
        data['DynamicFreezer/SolidFlavoringOn'] = np.random.choice([0, 1], n_samples, p=[0.6, 0.4])
        data['DynamicFreezer/LiquidFlavoringOn'] = np.random.choice([0, 1], n_samples, p=[0.7, 0.3])
        data['DynamicFreezer/FreezerOn'] = np.ones(n_samples)
        data['DynamicFreezer/DasherOn'] = np.ones(n_samples)
        data['DynamicFreezer/Overrun'] = np.random.uniform(0.8, 1.2, n_samples)
        data['DynamicFreezer/SendTestValues'] = np.zeros(n_samples)
        data['DynamicFreezer/ParticleSize'] = np.random.uniform(0.3, 1.0, n_samples)
        data['DynamicFreezer/BarrelRotationSpeed'] = np.random.uniform(50, 100, n_samples)
        data['DynamicFreezer/PasteurizationUnits'] = np.random.uniform(10, 30, n_samples)
        data['DynamicFreezer/InFlowMix'] = np.random.uniform(0, 4, n_samples)
        data['DynamicFreezer/OutFlowMix'] = np.random.uniform(0, 4, n_samples)
        
        # Hardening parameters
        data['Hardening/Packages'] = np.random.uniform(0, 10, n_samples)
        data['Hardening/OpenDumpValve'] = np.zeros(n_samples)
        data['Hardening/Temperature'] = np.random.normal(251.1, 2.0, n_samples)
        data['Hardening/HardeningOn'] = np.ones(n_samples)
        data['Hardening/FinishBatchOn'] = np.random.choice([0, 1], n_samples, p=[0.9, 0.1])
        data['Hardening/InFlowMix'] = np.random.uniform(0, 3, n_samples)
        
        return pd.DataFrame(data)
    
    def inject_freeze_anomaly(self, normal_data, anomaly_ratio=0.1):
        """Inject freeze anomalies into normal data"""
        data = normal_data.copy()
        n_samples = len(data)
        n_anomalies = int(n_samples * anomaly_ratio)
        
        # Select random rows for anomalies
        anomaly_indices = np.random.choice(n_samples, n_anomalies, replace=False)
        
        # Select random parameters to freeze
        freeze_params = ['Mixer/Level', 'Pasteurizer/Temperature', 'DynamicFreezer/Level', 
                        'AgeingCooling/Temperature', 'Hardening/Temperature']
        
        for idx in anomaly_indices:
            param = np.random.choice(freeze_params)
            # Freeze value at a constant
            freeze_value = data[param].iloc[max(0, idx-5)]
            data.loc[idx, param] = freeze_value
            
        return data, anomaly_indices
    
    def inject_step_anomaly(self, normal_data, anomaly_ratio=0.1):
        """Inject step change anomalies"""
        data = normal_data.copy()
        n_samples = len(data)
        n_anomalies = int(n_samples * anomaly_ratio)
        
        anomaly_indices = np.random.choice(n_samples, n_anomalies, replace=False)
        step_params = ['Pasteurizer/Temperature', 'DynamicFreezer/Temperature', 
                      'Mixer/Temperature', 'AgeingCooling/Temperature']
        
        for idx in anomaly_indices:
            param = np.random.choice(step_params)
            # Add a significant step change
            step_size = np.random.uniform(10, 30) * np.random.choice([-1, 1])
            data.loc[idx:, param] += step_size
            
        return data, anomaly_indices
    
    def inject_ramp_anomaly(self, normal_data, anomaly_ratio=0.1):
        """Inject gradual ramp anomalies"""
        data = normal_data.copy()
        n_samples = len(data)
        n_anomalies = int(n_samples * anomaly_ratio)
        
        anomaly_indices = np.random.choice(n_samples//2, n_anomalies, replace=False)
        ramp_params = ['Mixer/Level', 'DynamicFreezer/Level', 'Pasteurizer/Level']
        
        for start_idx in anomaly_indices:
            param = np.random.choice(ramp_params)
            ramp_length = min(20, n_samples - start_idx)
            ramp_slope = np.random.uniform(0.01, 0.05) * np.random.choice([-1, 1])
            
            for i in range(ramp_length):
                if start_idx + i < n_samples:
                    data.loc[start_idx + i, param] += ramp_slope * i
                    
        return data, anomaly_indices
    
    def generate_mixed_dataset(self, n_samples=1000):
        """Generate a mixed dataset with various anomaly types"""
        # Generate base normal data
        normal_data = self.generate_normal_data(n_samples)
        
        # Add different anomaly types
        data_with_freeze, freeze_indices = self.inject_freeze_anomaly(normal_data, 0.05)
        data_with_step, step_indices = self.inject_step_anomaly(data_with_freeze, 0.05)
        final_data, ramp_indices = self.inject_ramp_anomaly(data_with_step, 0.05)
        
        # Create labels
        labels = np.zeros(n_samples)  # 0 = Normal
        labels[freeze_indices] = 1    # 1 = Freeze
        labels[step_indices] = 2      # 2 = Step  
        labels[ramp_indices] = 3      # 3 = Ramp
        
        final_data['Anomaly'] = labels
        final_data['Timestamp'] = pd.date_range(start=datetime.now(), periods=n_samples, freq='30s')
        
        return final_data
    
    def generate_real_time_sample(self):
        """Generate a single real-time sample"""
        sample = self.generate_normal_data(1)
        
        # Sometimes inject an anomaly for demo purposes
        if np.random.random() < 0.1:  # 10% chance of anomaly
            anomaly_type = np.random.choice(['freeze', 'step', 'ramp'])
            
            if anomaly_type == 'freeze':
                param = np.random.choice(['Mixer/Level', 'Pasteurizer/Temperature'])
                sample[param] = 0
            elif anomaly_type == 'step':
                param = np.random.choice(['DynamicFreezer/Temperature', 'Pasteurizer/Temperature'])
                sample[param] += np.random.uniform(10, 20)
            elif anomaly_type == 'ramp':
                param = np.random.choice(['Mixer/Level', 'DynamicFreezer/Level'])
                sample[param] += np.random.uniform(0.5, 1.0)
        
        # Add timestamp
        sample['Timestamp'] = datetime.now().isoformat()
        
        return sample.to_dict(orient='records')[0]

# Usage example and testing
if __name__ == "__main__":
    generator = IceCreamDataGenerator()
    
    # Generate test dataset
    print("Generating mixed dataset...")
    mixed_data = generator.generate_mixed_dataset(1000)
    print(f"Generated {len(mixed_data)} samples")
    print(f"Anomaly distribution: \\n{mixed_data['Anomaly'].value_counts()}")
    
    # Save to CSV for testing
    mixed_data.to_csv('test_ice_cream_data.csv', index=False)
    print("Saved to test_ice_cream_data.csv")
    
    # Generate real-time sample
    print("\\nReal-time sample:")
    rt_sample = generator.generate_real_time_sample()
    print(json.dumps(rt_sample, indent=2, default=str))