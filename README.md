# Acess Website at : https://honeywell-anomaly-detection-q3.vercel.app/


# Anomalyze


## First - Initial Commit Commit

## Dataset Folder Added

## Added CSV

## Updated Labelling Script

## Updated labelling script to update runID and label anomaly





# AnomaLyze - Ice Cream Factory Anomaly Detection System

## Complete Setup and Deployment Guide

### Overview
This industrial-grade anomaly detection system monitors ice cream production processes and identifies deviations in real-time using XGBoost machine learning algorithms.

## Directory Structure

```
AnomaLyze/
├── backend/
│   ├── app.py                     # Flask backend (your backend-app.py)
│   ├── models/
│   │   ├── anomaly_detector.pkl   # Your trained XGBoost model
│   │   └── model_utils.py         # Utility functions
│   ├── data/
│   │   ├── exported_data.csv      # Your processed dataset (2M+ rows)
│   │   └── test_data.csv          # Test samples
│   ├── data_generator.py          # Simulation data generator (your data-generator.py)
│   └── requirements.txt           # Dependencies (your requirements.txt)
├── frontend/
│   ├── index.html                 # Main dashboard
│   ├── style.css                  # Complete styling
│   ├── app.js                     # Frontend JavaScript
│   └── dashboard_integration.js   # Backend integration (your dashboard-integration.js)
├── docs/
│   ├── README.md                  # This file
│   └── API_Documentation.md       # API docs
└── setup/
    ├── install.sh                 # Setup script
    └── docker-compose.yml         # Docker deployment
```

## Required Input Features (54 total)

Your XGBoost model expects exactly these 54 sensor parameters:

**Mixer Module (13 parameters):**
- Mixer/OpenDumpValve, Mixer/Level, Mixer/Temperature, Mixer/OpenOutlet
- Mixer/Fill1On through Mixer/Fill5On
- Mixer/TurnMixerOn, Mixer/MixerIsOn, Mixer/InFlowMix, Mixer/OutFlowMix

**Pasteurizer Module (8 parameters):**
- Pasteurizer/OpenDumpValve, Pasteurizer/Level, Pasteurizer/OpenOutlet
- Pasteurizer/HeaterOn, Pasteurizer/Temperature, Pasteurizer/CoolerOn
- Pasteurizer/InFlowMix, Pasteurizer/OutFlowMix

**Homogenizer Module (4 parameters):**
- Homogenizer/ParticleSize, Homogenizer/HomogenizerOn
- Homogenizer/Valve1/InFlowMix, Homogenizer/Valve2/OutFlowMix

**AgeingCooling Module (7 parameters):**
- AgeingCooling/OpenDumpValve, AgeingCooling/Level, AgeingCooling/Temperature
- AgeingCooling/InFlowMix, AgeingCooling/OpenOutlet, AgeingCooling/AgeingCoolingOn
- AgeingCooling/OutFlowMix

**DynamicFreezer Module (16 parameters):**
- DynamicFreezer/OpenDumpValve, DynamicFreezer/Level, DynamicFreezer/OpenOutlet
- DynamicFreezer/HeaterOn, DynamicFreezer/Temperature, DynamicFreezer/SolidFlavoringOn
- DynamicFreezer/LiquidFlavoringOn, DynamicFreezer/FreezerOn, DynamicFreezer/DasherOn
- DynamicFreezer/Overrun, DynamicFreezer/SendTestValues, DynamicFreezer/ParticleSize
- DynamicFreezer/BarrelRotationSpeed, DynamicFreezer/PasteurizationUnits
- DynamicFreezer/InFlowMix, DynamicFreezer/OutFlowMix

**Hardening Module (6 parameters):**
- Hardening/Packages, Hardening/OpenDumpValve, Hardening/Temperature
- Hardening/HardeningOn, Hardening/FinishBatchOn, Hardening/InFlowMix

## Model Output

The system returns:
- **Anomaly Type:** Normal (0), Freeze (1), Step (2), Ramp (3)
- **Parameter for Anomaly:** Which specific sensor is affected
- **Confidence Score:** Prediction confidence (0-1)
- **All Probabilities:** Probability distribution for all classes

## Setup Instructions

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend/

# Install Python dependencies
pip install -r requirements.txt

# Copy your trained model
cp /path/to/your/anomaly_detector.pkl models/

# Copy your dataset
cp /path/to/your/exported_data.csv data/

# Start the Flask backend
python app.py
```

The backend will start on `http://localhost:5000`

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend/

# Serve the dashboard (using Python's built-in server)
python -m http.server 8080

# Or use any web server like nginx, apache, or Node.js serve
```

Access the dashboard at `http://localhost:8080`

### 3. API Endpoints

**Health Check:**
```
GET /health
```

**Single Prediction:**
```
POST /predict
Content-Type: application/json

{
  "Mixer/Level": 0.85,
  "Mixer/Temperature": 276.5,
  // ... all 54 features
}
```

**Batch Prediction:**
```
POST /batch_predict
Content-Type: application/json

{
  "batch_data": [
    { /* sensor data row 1 */ },
    { /* sensor data row 2 */ },
    // ...
  ]
}
```

**Simulate Data:**
```
GET /simulate_data
```

### 4. Dashboard Features

#### **Main Dashboard Pages:**
1. **Overview** - Live process monitoring with module status
2. **Process Flow** - Step-by-step ice cream production visualization
3. **Anomaly Detection** - Real-time alerts and anomaly history
4. **Analytics** - Historical trends and performance metrics
5. **Reports** - Export functionality and batch analysis

#### **Key Features:**
- Real-time sensor monitoring with live charts
- Color-coded module status (Green=Normal, Yellow=Warning, Red=Anomaly)
- Interactive process flow diagram
- Anomaly notifications and logging
- Historical data analysis
- Export capabilities (CSV, PDF reports)
- Dark/Light theme toggle
- Responsive design for desktop/tablet

### 5. Deployment Options

#### **Option A: Traditional Deployment**
```bash
# Backend (Production)
gunicorn --bind 0.0.0.0:5000 app:app

# Frontend (Nginx)
# Configure nginx to serve static files from frontend/
```

#### **Option B: Docker Deployment**
```dockerfile
# Dockerfile for backend
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

### 6. Configuration

#### **Environment Variables:**
```bash
# Backend configuration
export FLASK_ENV=production
export MODEL_PATH=./models/anomaly_detector.pkl
export DATA_PATH=./data/exported_data.csv

# Frontend configuration (in dashboard_integration.js)
const API_BASE_URL = 'http://your-backend-url:5000';
```

### 7. Testing the System

```python
# Test with sample data
import requests
import json

# Sample input data (all 54 features required)
sample_data = {
    "Mixer/OpenDumpValve": 0,
    "Mixer/Level": 0.85,
    "Mixer/Temperature": 276.5,
    # ... include all 54 features
}

# Make prediction
response = requests.post(
    'http://localhost:5000/predict',
    headers={'Content-Type': 'application/json'},
    data=json.dumps(sample_data)
)

print(response.json())
```

### 8. Monitoring and Maintenance

- **Logs:** Check Flask application logs for errors
- **Performance:** Monitor CPU/Memory usage during prediction
- **Model Updates:** Replace `anomaly_detector.pkl` to update the model
- **Data:** Regularly update training data for model improvement

### 9. Troubleshooting

**Common Issues:**
- **Model Loading Error:** Ensure `anomaly_detector.pkl` is in the correct path
- **Missing Features:** API returns error if any of the 54 features are missing
- **CORS Issues:** Backend includes CORS headers for frontend integration
- **Dashboard Not Loading:** Check browser console for JavaScript errors

### 10. Production Considerations

- **Security:** Implement authentication and authorization
- **Scalability:** Use Redis for caching, PostgreSQL for data persistence
- **Monitoring:** Add Prometheus/Grafana for system monitoring
- **Backup:** Regular backup of models and historical data
- **Load Balancing:** Use nginx or cloud load balancer for high availability

## Support and Documentation

For detailed API documentation, troubleshooting, and advanced configuration, see:
- `/docs/API_Documentation.md`
- Backend logs at `/logs/`
- Frontend browser console for debugging

## Architecture Highlights

This system provides:
- **Real-time anomaly detection** with <1 second response time
- **Industrial-grade UI** suitable for factory floor deployment
- **Scalable architecture** supporting multiple concurrent users
- **Comprehensive monitoring** of all ice cream production stages
- **Actionable insights** with specific fix recommendations
- **Historical analysis** for process improvement

The dashboard successfully bridges the gap between complex ML models and practical industrial application, providing operators with intuitive tools for maintaining optimal ice cream production quality.
