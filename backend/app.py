# backend/app.py - Flask Backend for Ice Cream Anomaly Detection System

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib
import logging
from datetime import datetime
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global variables
model = None
feature_columns = None
anomaly_mapping = {0: "Normal", 1: "Freeze", 2: "Step", 3: "Ramp"}

# Feature columns (54 total as per your model training)
FEATURE_COLUMNS = [
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

def load_model():
    """Load the trained XGBoost model"""
    global model
    try:
        model_path = 'models/anomaly_detector.pkl'
        if os.path.exists(model_path):
            model = joblib.load(model_path)
            logger.info("Model loaded successfully")
            return True
        else:
            logger.error(f"Model file not found: {model_path}")
            return False
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        return False

def identify_anomaly_parameter(input_data, anomaly_type):
    """
    Identify which parameter is most likely affected by the anomaly
    This is a simplified logic - you can enhance with more sophisticated analysis
    """
    if anomaly_type == "Normal":
        return "No Anomaly"
    
    # Group parameters by module
    modules = {
        'Mixer': [col for col in FEATURE_COLUMNS if col.startswith('Mixer/')],
        'Pasteurizer': [col for col in FEATURE_COLUMNS if col.startswith('Pasteurizer/')],
        'Homogenizer': [col for col in FEATURE_COLUMNS if col.startswith('Homogenizer/')],
        'AgeingCooling': [col for col in FEATURE_COLUMNS if col.startswith('AgeingCooling/')],
        'DynamicFreezer': [col for col in FEATURE_COLUMNS if col.startswith('DynamicFreezer/')],
        'Hardening': [col for col in FEATURE_COLUMNS if col.startswith('Hardening/')]
    }
    
    # Simple heuristic: check which parameters have unusual values
    # This is simplified - in real scenarios, you'd use feature importance or SHAP values
    suspected_params = []
    
    for module, params in modules.items():
        for param in params:
            if param in input_data.columns:
                value = input_data[param].iloc[0]
                # Check for suspicious patterns based on anomaly type
                if anomaly_type == "Freeze" and value == 0:
                    suspected_params.append(param)
                elif anomaly_type == "Step" and abs(value) > 300:  # Temperature step changes
                    suspected_params.append(param)
                elif anomaly_type == "Ramp" and value > 1:  # Gradually increasing values
                    suspected_params.append(param)
    
    # Return the most likely suspect or a default
    if suspected_params:
        return suspected_params[0]
    else:
        # Default fallback based on common failure points
        defaults = {
            "Freeze": "DynamicFreezer/Temperature",
            "Step": "Pasteurizer/Temperature", 
            "Ramp": "Mixer/Level"
        }
        return defaults.get(anomaly_type, "Unknown")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "model_loaded": model is not None,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/predict', methods=['POST'])
def predict_anomaly():
    """Main prediction endpoint"""
    try:
        # Get input data
        data = request.json
        
        if not data:
            return jsonify({"error": "No input data provided"}), 400
        
        # Convert to DataFrame
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame([data])
        
        # Ensure all required features are present
        missing_features = set(FEATURE_COLUMNS) - set(df.columns)
        if missing_features:
            # Fill missing features with 0 (or you could return an error)
            for feature in missing_features:
                df[feature] = 0
        
        # Select only the required features in the correct order
        input_features = df[FEATURE_COLUMNS]
        
        # Make prediction
        if model is None:
            return jsonify({"error": "Model not loaded"}), 500
        
        # Create DMatrix for XGBoost
        import xgboost as xgb
        dmatrix = xgb.DMatrix(input_features)
        
        # Get predictions
        prediction_probs = model.predict(dmatrix)
        predictions = np.argmax(prediction_probs, axis=1)
        
        results = []
        for i, pred in enumerate(predictions):
            anomaly_type = anomaly_mapping[pred]
            confidence = float(prediction_probs[i][pred])
            
            # Identify parameter for anomaly
            parameter_for_anomaly = identify_anomaly_parameter(input_features.iloc[[i]], anomaly_type)
            
            result = {
                "anomaly_type": anomaly_type,
                "anomaly_code": int(pred),
                "confidence": confidence,
                "parameter_for_anomaly": parameter_for_anomaly,
                "timestamp": datetime.now().isoformat(),
                "all_probabilities": {
                    anomaly_mapping[j]: float(prob) 
                    for j, prob in enumerate(prediction_probs[i])
                }
            }
            results.append(result)
        
        return jsonify({
            "predictions": results,
            "status": "success"
        })
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/batch_predict', methods=['POST'])
def batch_predict():
    """Batch prediction for multiple rows"""
    try:
        data = request.json
        
        if not data or 'batch_data' not in data:
            return jsonify({"error": "No batch data provided"}), 400
        
        batch_data = data['batch_data']
        df = pd.DataFrame(batch_data)
        
        # Process similar to single prediction
        missing_features = set(FEATURE_COLUMNS) - set(df.columns)
        for feature in missing_features:
            df[feature] = 0
        
        input_features = df[FEATURE_COLUMNS]
        
        import xgboost as xgb
        dmatrix = xgb.DMatrix(input_features)
        prediction_probs = model.predict(dmatrix)
        predictions = np.argmax(prediction_probs, axis=1)
        
        results = []
        for i, pred in enumerate(predictions):
            anomaly_type = anomaly_mapping[pred]
            confidence = float(prediction_probs[i][pred])
            parameter_for_anomaly = identify_anomaly_parameter(input_features.iloc[[i]], anomaly_type)
            
            result = {
                "row_id": i,
                "anomaly_type": anomaly_type,
                "anomaly_code": int(pred),
                "confidence": confidence,
                "parameter_for_anomaly": parameter_for_anomaly
            }
            results.append(result)
        
        return jsonify({
            "batch_predictions": results,
            "total_processed": len(results),
            "status": "success"
        })
        
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/simulate_data', methods=['GET'])
def simulate_data():
    """Generate simulated sensor data for testing"""
    try:
        # Generate realistic simulated data
        np.random.seed(42)
        
        simulated_data = {}
        
        # Mixer parameters
        simulated_data['Mixer/OpenDumpValve'] = 0
        simulated_data['Mixer/Level'] = np.random.uniform(0.1, 0.9)
        simulated_data['Mixer/Temperature'] = np.random.uniform(275, 278)
        simulated_data['Mixer/OpenOutlet'] = np.random.choice([0, 1])
        for i in range(1, 6):
            simulated_data[f'Mixer/Fill{i}On'] = np.random.choice([0, 1])
        simulated_data['Mixer/TurnMixerOn'] = 1
        simulated_data['Mixer/MixerIsOn'] = 1
        simulated_data['Mixer/InFlowMix'] = np.random.uniform(0, 10)
        simulated_data['Mixer/OutFlowMix'] = np.random.uniform(0, 10)
        
        # Continue for all modules...
        # (Add similar patterns for other modules)
        
        return jsonify({
            "simulated_data": simulated_data,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/model_info', methods=['GET'])
def model_info():
    """Get model information"""
    try:
        info = {
            "model_loaded": model is not None,
            "feature_count": len(FEATURE_COLUMNS),
            "anomaly_types": list(anomaly_mapping.values()),
            "feature_columns": FEATURE_COLUMNS
        }
        return jsonify(info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Load model on startup
    if load_model():
        logger.info("Starting Flask application...")
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        logger.error("Failed to load model. Exiting...")