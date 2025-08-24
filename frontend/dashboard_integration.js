// dashboard_integration.js - Integration layer between frontend and backend

class AnomalyDetectionAPI {
    constructor(baseURL = 'http://localhost:5000') {
        this.baseURL = baseURL;
    }

    async makeRequest(endpoint, options = {}) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers,
                },
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    // Health check
    async healthCheck() {
        return await this.makeRequest('/health');
    }

    // Single prediction
    async predictAnomaly(sensorData) {
        return await this.makeRequest('/predict', {
            method: 'POST',
            body: JSON.stringify(sensorData),
        });
    }

    // Batch prediction
    async batchPredict(batchData) {
        return await this.makeRequest('/batch_predict', {
            method: 'POST',
            body: JSON.stringify({ batch_data: batchData }),
        });
    }

    // Get simulated data
    async getSimulatedData() {
        return await this.makeRequest('/simulate_data');
    }

    // Get model information
    async getModelInfo() {
        return await this.makeRequest('/model_info');
    }
}

// Dashboard Manager - Main application controller
class DashboardManager {
    constructor() {
        this.api = new AnomalyDetectionAPI();
        this.isRunning = false;
        this.currentData = null;
        this.anomalyHistory = [];
        this.updateInterval = 5000; // 5 seconds
        this.charts = {};
        
        this.init();
    }

    async init() {
        console.log('Initializing dashboard...');
        
        try {
            // Check backend health
            const health = await this.api.healthCheck();
            console.log('Backend health:', health);
            
            // Get model info
            const modelInfo = await this.api.getModelInfo();
            console.log('Model info:', modelInfo);
            
            // Initialize UI components
            this.initializeUI();
            this.initializeCharts();
            
            // Start real-time monitoring
            this.startMonitoring();
            
        } catch (error) {
            console.error('Failed to initialize dashboard:', error);
            this.showError('Failed to connect to backend service');
        }
    }

    initializeUI() {
        // Initialize theme toggle
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', this.toggleTheme.bind(this));
        }

        // Initialize navigation
        const navLinks = document.querySelectorAll('.nav__link');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                const page = e.target.dataset.page;
                this.switchPage(page);
            });
        });

        // Initialize control buttons
        const startBtn = document.getElementById('startMonitoring');
        const stopBtn = document.getElementById('stopMonitoring');
        
        if (startBtn) startBtn.addEventListener('click', () => this.startMonitoring());
        if (stopBtn) stopBtn.addEventListener('click', () => this.stopMonitoring());
    }

    initializeCharts() {
        // Initialize temperature chart
        const tempCtx = document.getElementById('temperatureChart');
        if (tempCtx) {
            this.charts.temperature = new Chart(tempCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Mixer Temperature',
                        data: [],
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        tension: 0.1
                    }, {
                        label: 'Pasteurizer Temperature',
                        data: [],
                        borderColor: '#ef4444',
                        backgroundColor: 'rgba(239, 68, 68, 0.1)',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: false
                        }
                    }
                }
            });
        }

        // Initialize level chart
        const levelCtx = document.getElementById('levelChart');
        if (levelCtx) {
            this.charts.level = new Chart(levelCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Mixer Level',
                        data: [],
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 1
                        }
                    }
                }
            });
        }
    }

    async startMonitoring() {
        if (this.isRunning) return;
        
        this.isRunning = true;
        this.updateSystemStatus('active');
        
        // Start the monitoring loop
        this.monitoringLoop();
    }

    stopMonitoring() {
        this.isRunning = false;
        this.updateSystemStatus('stopped');
    }

    async monitoringLoop() {
        while (this.isRunning) {
            try {
                // Get simulated sensor data
                const response = await this.api.getSimulatedData();
                const sensorData = response.simulated_data;
                
                // Make prediction
                const prediction = await this.api.predictAnomaly(sensorData);
                
                // Update dashboard with new data
                this.updateDashboard(sensorData, prediction);
                
                // Wait for next update
                await new Promise(resolve => setTimeout(resolve, this.updateInterval));
                
            } catch (error) {
                console.error('Monitoring error:', error);
                // Continue monitoring despite errors
                await new Promise(resolve => setTimeout(resolve, this.updateInterval));
            }
        }
    }

    updateDashboard(sensorData, prediction) {
        // Update current data
        this.currentData = sensorData;
        
        // Update process modules status
        this.updateModulesStatus(sensorData, prediction);
        
        // Update charts
        this.updateCharts(sensorData);
        
        // Handle anomalies
        if (prediction.predictions && prediction.predictions.length > 0) {
            const pred = prediction.predictions[0];
            if (pred.anomaly_type !== 'Normal') {
                this.handleAnomaly(pred);
            }
        }
    }

    updateModulesStatus(sensorData, prediction) {
        const modules = ['Mixer', 'Pasteurizer', 'Homogenizer', 'AgeingCooling', 'DynamicFreezer', 'Hardening'];
        
        modules.forEach(module => {
            const moduleElement = document.querySelector(`[data-module="${module}"]`);
            if (moduleElement) {
                // Update temperature display
                const tempElement = moduleElement.querySelector('.module-temperature');
                if (tempElement && sensorData[`${module}/Temperature`] !== undefined) {
                    tempElement.textContent = `${sensorData[`${module}/Temperature`].toFixed(1)}°C`;
                }
                
                // Update level display
                const levelElement = moduleElement.querySelector('.module-level');
                if (levelElement && sensorData[`${module}/Level`] !== undefined) {
                    const levelPercent = (sensorData[`${module}/Level`] * 100).toFixed(0);
                    levelElement.textContent = `${levelPercent}%`;
                }
                
                // Update status based on anomaly
                let status = 'normal';
                if (prediction.predictions && prediction.predictions.length > 0) {
                    const pred = prediction.predictions[0];
                    if (pred.parameter_for_anomaly && pred.parameter_for_anomaly.startsWith(module) && pred.anomaly_type !== 'Normal') {
                        status = pred.anomaly_type.toLowerCase();
                    }
                }
                
                // Update visual status
                moduleElement.className = `module module--${status}`;
            }
        });
    }

    updateCharts(sensorData) {
        const now = new Date().toLocaleTimeString();
        
        // Update temperature chart
        if (this.charts.temperature) {
            const chart = this.charts.temperature;
            chart.data.labels.push(now);
            chart.data.datasets[0].data.push(sensorData['Mixer/Temperature']);
            chart.data.datasets[1].data.push(sensorData['Pasteurizer/Temperature']);
            
            // Keep only last 20 points
            if (chart.data.labels.length > 20) {
                chart.data.labels.shift();
                chart.data.datasets[0].data.shift();
                chart.data.datasets[1].data.shift();
            }
            
            chart.update('none');
        }
        
        // Update level chart
        if (this.charts.level) {
            const chart = this.charts.level;
            chart.data.labels.push(now);
            chart.data.datasets[0].data.push(sensorData['Mixer/Level']);
            
            if (chart.data.labels.length > 20) {
                chart.data.labels.shift();
                chart.data.datasets[0].data.shift();
            }
            
            chart.update('none');
        }
    }

    handleAnomaly(prediction) {
        // Add to anomaly history
        this.anomalyHistory.unshift({
            timestamp: new Date().toISOString(),
            ...prediction
        });
        
        // Keep only last 50 anomalies
        if (this.anomalyHistory.length > 50) {
            this.anomalyHistory = this.anomalyHistory.slice(0, 50);
        }
        
        // Show notification
        this.showAnomalyNotification(prediction);
        
        // Update anomaly log table
        this.updateAnomalyLog();
    }

    showAnomalyNotification(prediction) {
        const notification = document.createElement('div');
        notification.className = 'notification notification--error';
        notification.innerHTML = `
            <div class="notification__icon">⚠️</div>
            <div class="notification__content">
                <strong>Anomaly Detected:</strong> ${prediction.anomaly_type} in ${prediction.parameter_for_anomaly}
                <br><small>Confidence: ${(prediction.confidence * 100).toFixed(1)}%</small>
            </div>
            <button class="notification__close">&times;</button>
        `;
        
        // Add to page
        const container = document.querySelector('.notifications') || document.body;
        container.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
        
        // Close button functionality
        notification.querySelector('.notification__close').addEventListener('click', () => {
            notification.parentNode.removeChild(notification);
        });
    }

    updateAnomalyLog() {
        const logContainer = document.querySelector('.anomaly-log');
        if (!logContainer) return;
        
        const html = this.anomalyHistory.map(anomaly => `
            <div class="log-entry">
                <div class="log-entry__time">${new Date(anomaly.timestamp).toLocaleString()}</div>
                <div class="log-entry__type log-entry__type--${anomaly.anomaly_type.toLowerCase()}">${anomaly.anomaly_type}</div>
                <div class="log-entry__parameter">${anomaly.parameter_for_anomaly}</div>
                <div class="log-entry__confidence">${(anomaly.confidence * 100).toFixed(1)}%</div>
            </div>
        `).join('');
        
        logContainer.innerHTML = html;
    }

    updateSystemStatus(status) {
        const statusElement = document.getElementById('systemStatus');
        if (statusElement) {
            const statusDot = statusElement.querySelector('.status-dot');
            const statusText = statusElement.querySelector('span:last-child');
            
            switch (status) {
                case 'active':
                    statusDot.className = 'status-dot status-dot--success';
                    statusText.textContent = 'System Active';
                    break;
                case 'stopped':
                    statusDot.className = 'status-dot status-dot--error';
                    statusText.textContent = 'System Stopped';
                    break;
                case 'warning':
                    statusDot.className = 'status-dot status-dot--warning';
                    statusText.textContent = 'System Warning';
                    break;
            }
        }
    }

    switchPage(pageName) {
        // Update active navigation
        document.querySelectorAll('.nav__link').forEach(link => {
            link.classList.remove('nav__link--active');
        });
        document.querySelector(`[data-page="${pageName}"]`).classList.add('nav__link--active');
        
        // Show/hide page content
        document.querySelectorAll('.page').forEach(page => {
            page.classList.remove('page--active');
        });
        const targetPage = document.getElementById(`${pageName}Page`);
        if (targetPage) {
            targetPage.classList.add('page--active');
        }
    }

    toggleTheme() {
        document.documentElement.classList.toggle('theme-dark');
        const isDark = document.documentElement.classList.contains('theme-dark');
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.innerHTML = isDark ? '☀️ Light Mode' : '🌙 Dark Mode';
        }
    }

    showError(message) {
        console.error(message);
        // You can implement a proper error display here
        alert(message);
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboardManager = new DashboardManager();
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { AnomalyDetectionAPI, DashboardManager };
}