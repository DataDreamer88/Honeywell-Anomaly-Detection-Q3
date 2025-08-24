// Application Data
const appData = {
  modules: [
    {"name": "Mixer", "status": "normal", "temperature": 276.5, "level": 0.85, "parameters": ["OpenDumpValve", "Level", "Temperature", "OpenOutlet", "Fill1On", "Fill2On", "Fill3On", "Fill4On", "Fill5On", "TurnMixerOn", "MixerIsOn", "InFlowMix", "OutFlowMix"]},
    {"name": "Pasteurizer", "status": "warning", "temperature": 276.8, "level": 0.0, "parameters": ["OpenDumpValve", "Level", "OpenOutlet", "HeaterOn", "Temperature", "CoolerOn", "InFlowMix", "OutFlowMix"]},
    {"name": "Homogenizer", "status": "normal", "temperature": 0.0, "level": 0.0, "parameters": ["ParticleSize", "HomogenizerOn", "Valve1/InFlowMix", "Valve2/OutFlowMix"]},
    {"name": "AgeingCooling", "status": "normal", "temperature": 276.7, "level": 0.0, "parameters": ["OpenDumpValve", "Level", "Temperature", "InFlowMix", "OpenOutlet", "AgeingCoolingOn", "OutFlowMix"]},
    {"name": "DynamicFreezer", "status": "anomaly", "temperature": 277.2, "level": 0.0, "parameters": ["OpenDumpValve", "Level", "OpenOutlet", "HeaterOn", "Temperature", "SolidFlavoringOn", "LiquidFlavoringOn", "FreezerOn", "DasherOn", "Overrun", "SendTestValues", "ParticleSize", "BarrelRotationSpeed", "PasteurizationUnits", "InFlowMix", "OutFlowMix"]},
    {"name": "Hardening", "status": "normal", "temperature": 251.1, "level": 0.0, "parameters": ["Packages", "OpenDumpValve", "Temperature", "HardeningOn", "FinishBatchOn", "InFlowMix"]}
  ],
  anomalyTypes: ["Normal", "Freeze", "Step", "Ramp"],
  recentAnomalies: [
    {"timestamp": "2025-08-24 18:45:32", "type": "Step", "module": "DynamicFreezer", "parameter": "Temperature", "severity": "High"},
    {"timestamp": "2025-08-24 18:42:15", "type": "Freeze", "module": "Pasteurizer", "parameter": "Level", "severity": "Medium"},
    {"timestamp": "2025-08-24 18:38:47", "type": "Ramp", "module": "Mixer", "parameter": "Level", "severity": "Low"}
  ],
  batchData: [
    {"batchId": "B001", "quality": 95.2, "anomalies": 0, "status": "Good"},
    {"batchId": "B002", "quality": 87.3, "anomalies": 2, "status": "Fair"},
    {"batchId": "B003", "quality": 92.8, "anomalies": 1, "status": "Good"}
  ]
};

// Global variables for charts
let temperatureChart, levelChart, anomalyChart, qualityChart, performanceChart;
let realTimeData = {
  temperature: [],
  level: [],
  timestamps: []
};

// Application initialization
document.addEventListener('DOMContentLoaded', function() {
  initializeApp();
});

function initializeApp() {
  setupNavigation();
  setupThemeToggle();
  renderModuleCards();
  renderAnomalies();
  renderBatchTable();
  setupCharts();
  setupModals();
  setupReports();
  startRealTimeSimulation();
}

// Navigation functionality - Fixed the navigation bug
function setupNavigation() {
  const navLinks = document.querySelectorAll('.nav__link');
  const pages = document.querySelectorAll('.page');

  navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const targetPage = e.currentTarget.dataset.page; // Fixed: use currentTarget instead of target
      
      // Ensure we have a valid target page
      if (!targetPage) return;
      
      // Update active nav link
      navLinks.forEach(l => l.classList.remove('nav__link--active'));
      e.currentTarget.classList.add('nav__link--active');
      
      // Show target page
      pages.forEach(page => page.classList.remove('page--active'));
      const targetPageElement = document.getElementById(targetPage);
      
      if (targetPageElement) {
        targetPageElement.classList.add('page--active');
        
        // Add fade-in animation
        targetPageElement.classList.add('fade-in');
        setTimeout(() => {
          targetPageElement.classList.remove('fade-in');
        }, 300);
        
        // Initialize charts if needed when navigating to analytics page
        if (targetPage === 'analytics') {
          setTimeout(() => {
            if (qualityChart) qualityChart.resize();
            if (performanceChart) performanceChart.resize();
          }, 100);
        }
        
        // Initialize anomaly chart when navigating to anomaly page
        if (targetPage === 'anomaly') {
          setTimeout(() => {
            if (anomalyChart) anomalyChart.resize();
          }, 100);
        }
      }
    });
  });
}

// Theme toggle functionality
function setupThemeToggle() {
  const themeToggle = document.getElementById('themeToggle');
  const currentTheme = localStorage.getItem('theme') || 'light';
  
  document.documentElement.setAttribute('data-color-scheme', currentTheme);
  updateThemeButton(currentTheme);

  themeToggle.addEventListener('click', () => {
    const currentTheme = document.documentElement.getAttribute('data-color-scheme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    document.documentElement.setAttribute('data-color-scheme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeButton(newTheme);
  });
}

function updateThemeButton(theme) {
  const themeToggle = document.getElementById('themeToggle');
  themeToggle.textContent = theme === 'light' ? '🌙 Dark Mode' : '☀️ Light Mode';
}

// Render module cards
function renderModuleCards() {
  const modulesGrid = document.getElementById('modulesGrid');
  
  const moduleCards = appData.modules.map(module => `
    <div class="module-card" data-module="${module.name}">
      <div class="module-card__header">
        <h3 class="module-card__title">${module.name}</h3>
        <span class="module-card__status module-card__status--${module.status}">
          ${module.status.charAt(0).toUpperCase() + module.status.slice(1)}
        </span>
      </div>
      <div class="module-card__metrics">
        <div class="metric">
          <span class="metric__label">Temperature</span>
          <span class="metric__value">${module.temperature.toFixed(1)}°K</span>
        </div>
        <div class="metric">
          <span class="metric__label">Level</span>
          <span class="metric__value">${(module.level * 100).toFixed(1)}%</span>
        </div>
      </div>
    </div>
  `).join('');
  
  modulesGrid.innerHTML = moduleCards;
  
  // Add click handlers
  document.querySelectorAll('.module-card').forEach(card => {
    card.addEventListener('click', (e) => {
      const moduleName = e.currentTarget.dataset.module;
      showModuleDetails(moduleName);
    });
  });
}

// Render recent anomalies
function renderAnomalies() {
  const alertsList = document.getElementById('alertsList');
  
  const alertItems = appData.recentAnomalies.map(anomaly => `
    <div class="alert-item alert-item--${anomaly.severity === 'High' ? 'error' : anomaly.severity === 'Medium' ? 'warning' : 'info'}">
      <div class="alert-content">
        <div class="alert-title">${anomaly.type} Anomaly Detected</div>
        <div class="alert-details">
          Module: ${anomaly.module} | Parameter: ${anomaly.parameter} | Severity: ${anomaly.severity}
        </div>
      </div>
      <div class="alert-timestamp">${anomaly.timestamp}</div>
    </div>
  `).join('');
  
  alertsList.innerHTML = alertItems;
  
  // Update active anomalies count
  document.getElementById('activeAnomalies').textContent = appData.recentAnomalies.filter(a => 
    new Date() - new Date(a.timestamp) < 3600000 // Last hour
  ).length;
}

// Render batch table
function renderBatchTable() {
  const tbody = document.getElementById('batchTableBody');
  
  const rows = appData.batchData.map(batch => `
    <tr>
      <td>${batch.batchId}</td>
      <td>${batch.quality.toFixed(1)}%</td>
      <td>${batch.anomalies}</td>
      <td>
        <span class="status ${batch.status === 'Good' ? 'status--success' : 'status--warning'}">
          ${batch.status}
        </span>
      </td>
    </tr>
  `).join('');
  
  tbody.innerHTML = rows;
}

// Setup charts
function setupCharts() {
  setupTemperatureChart();
  setupLevelChart();
  setupAnomalyChart();
  setupQualityChart();
  setupPerformanceChart();
}

function setupTemperatureChart() {
  const ctx = document.getElementById('temperatureChart').getContext('2d');
  
  temperatureChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: [],
      datasets: appData.modules.map((module, index) => ({
        label: module.name,
        data: [],
        borderColor: ['#1FB8CD', '#FFC185', '#B4413C', '#ECEBD5', '#5D878F', '#DB4545'][index],
        backgroundColor: ['#1FB8CD', '#FFC185', '#B4413C', '#ECEBD5', '#5D878F', '#DB4545'][index] + '20',
        tension: 0.4,
        fill: false
      }))
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: false,
          title: {
            display: true,
            text: 'Temperature (°K)'
          }
        },
        x: {
          title: {
            display: true,
            text: 'Time'
          }
        }
      },
      plugins: {
        legend: {
          position: 'top'
        }
      }
    }
  });
}

function setupLevelChart() {
  const ctx = document.getElementById('levelChart').getContext('2d');
  
  levelChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: [],
      datasets: appData.modules.map((module, index) => ({
        label: module.name,
        data: [],
        borderColor: ['#1FB8CD', '#FFC185', '#B4413C', '#ECEBD5', '#5D878F', '#DB4545'][index],
        backgroundColor: ['#1FB8CD', '#FFC185', '#B4413C', '#ECEBD5', '#5D878F', '#DB4545'][index] + '20',
        tension: 0.4,
        fill: false
      }))
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          max: 1,
          title: {
            display: true,
            text: 'Level (%)'
          }
        },
        x: {
          title: {
            display: true,
            text: 'Time'
          }
        }
      },
      plugins: {
        legend: {
          position: 'top'
        }
      }
    }
  });
}

function setupAnomalyChart() {
  const ctx = document.getElementById('anomalyChart').getContext('2d');
  
  const anomalyCounts = appData.anomalyTypes.map(type => 
    appData.recentAnomalies.filter(anomaly => anomaly.type === type).length
  );
  
  anomalyChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: appData.anomalyTypes,
      datasets: [{
        data: anomalyCounts,
        backgroundColor: ['#1FB8CD', '#FFC185', '#B4413C', '#ECEBD5']
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom'
        }
      }
    }
  });
}

function setupQualityChart() {
  const ctx = document.getElementById('qualityChart').getContext('2d');
  
  qualityChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: appData.batchData.map(batch => batch.batchId),
      datasets: [{
        label: 'Quality Score',
        data: appData.batchData.map(batch => batch.quality),
        backgroundColor: '#1FB8CD',
        borderRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          title: {
            display: true,
            text: 'Quality Score (%)'
          }
        }
      },
      plugins: {
        legend: {
          display: false
        }
      }
    }
  });
}

function setupPerformanceChart() {
  const ctx = document.getElementById('performanceChart').getContext('2d');
  
  const performanceData = appData.modules.map(module => {
    const basePerformance = 95;
    const statusModifier = module.status === 'normal' ? 0 : 
                          module.status === 'warning' ? -5 : -15;
    return Math.max(0, basePerformance + statusModifier + (Math.random() - 0.5) * 10);
  });
  
  performanceChart = new Chart(ctx, {
    type: 'radar',
    data: {
      labels: appData.modules.map(module => module.name),
      datasets: [{
        label: 'Performance Score',
        data: performanceData,
        backgroundColor: 'rgba(31, 184, 205, 0.2)',
        borderColor: '#1FB8CD',
        pointBackgroundColor: '#1FB8CD'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          beginAtZero: true,
          max: 100
        }
      },
      plugins: {
        legend: {
          display: false
        }
      }
    }
  });
}

// Modal functionality
function setupModals() {
  const modal = document.getElementById('moduleModal');
  const closeModal = document.getElementById('closeModal');
  
  closeModal.addEventListener('click', () => {
    modal.classList.add('hidden');
  });
  
  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      modal.classList.add('hidden');
    }
  });
  
  // Process flow module clicks
  document.querySelectorAll('.process-module').forEach(module => {
    module.addEventListener('click', (e) => {
      const moduleName = e.currentTarget.dataset.module;
      showModuleDetails(moduleName);
    });
  });
}

function showModuleDetails(moduleName) {
  const module = appData.modules.find(m => m.name === moduleName);
  const modal = document.getElementById('moduleModal');
  const modalTitle = document.getElementById('modalTitle');
  const modalBody = document.getElementById('modalBody');
  
  modalTitle.textContent = `${module.name} Details`;
  
  const statusClass = module.status === 'normal' ? 'success' : 
                     module.status === 'warning' ? 'warning' : 'error';
  
  modalBody.innerHTML = `
    <div class="module-details-content">
      <div class="status status--${statusClass}">${module.status.toUpperCase()}</div>
      
      <div class="metrics-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin: 20px 0;">
        <div class="metric">
          <span class="metric__label">Temperature</span>
          <span class="metric__value">${module.temperature.toFixed(2)}°K</span>
        </div>
        <div class="metric">
          <span class="metric__label">Level</span>
          <span class="metric__value">${(module.level * 100).toFixed(1)}%</span>
        </div>
      </div>
      
      <h4>Monitored Parameters:</h4>
      <div class="parameter-list">
        ${module.parameters.map(param => `<div class="parameter-item">${param}</div>`).join('')}
      </div>
    </div>
  `;
  
  modal.classList.remove('hidden');
}

// Reports functionality
function setupReports() {
  const generateBtn = document.getElementById('generateReport');
  const exportBtn = document.getElementById('exportData');
  
  generateBtn.addEventListener('click', generateReport);
  exportBtn.addEventListener('click', exportData);
  
  // Set default dates
  const today = new Date();
  const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
  
  document.getElementById('endDate').value = today.toISOString().split('T')[0];
  document.getElementById('startDate').value = weekAgo.toISOString().split('T')[0];
}

function generateReport() {
  const reportType = document.getElementById('reportType').value;
  const preview = document.getElementById('reportPreview');
  
  let reportContent = '';
  
  switch (reportType) {
    case 'anomaly':
      reportContent = generateAnomalyReport();
      break;
    case 'production':
      reportContent = generateProductionReport();
      break;
    case 'quality':
      reportContent = generateQualityReport();
      break;
  }
  
  preview.innerHTML = reportContent;
}

function generateAnomalyReport() {
  const anomalyCount = appData.recentAnomalies.length;
  const highSeverity = appData.recentAnomalies.filter(a => a.severity === 'High').length;
  
  return `
    <div class="report-content">
      <h4>Anomaly Report Summary</h4>
      <p><strong>Total Anomalies:</strong> ${anomalyCount}</p>
      <p><strong>High Severity:</strong> ${highSeverity}</p>
      <p><strong>Most Affected Module:</strong> ${getMostAffectedModule()}</p>
      
      <h5>Recent Anomalies:</h5>
      <ul>
        ${appData.recentAnomalies.map(a => `
          <li>${a.timestamp} - ${a.type} anomaly in ${a.module} (${a.severity})</li>
        `).join('')}
      </ul>
    </div>
  `;
}

function generateProductionReport() {
  const avgQuality = appData.batchData.reduce((sum, batch) => sum + batch.quality, 0) / appData.batchData.length;
  const totalAnomalies = appData.batchData.reduce((sum, batch) => sum + batch.anomalies, 0);
  
  return `
    <div class="report-content">
      <h4>Production Summary Report</h4>
      <p><strong>Average Quality:</strong> ${avgQuality.toFixed(2)}%</p>
      <p><strong>Total Batches:</strong> ${appData.batchData.length}</p>
      <p><strong>Total Anomalies:</strong> ${totalAnomalies}</p>
      <p><strong>System Efficiency:</strong> 94.2%</p>
      
      <h5>Batch Details:</h5>
      <ul>
        ${appData.batchData.map(b => `
          <li>${b.batchId} - Quality: ${b.quality}%, Anomalies: ${b.anomalies}, Status: ${b.status}</li>
        `).join('')}
      </ul>
    </div>
  `;
}

function generateQualityReport() {
  const goodBatches = appData.batchData.filter(b => b.status === 'Good').length;
  const qualityRate = (goodBatches / appData.batchData.length * 100).toFixed(1);
  
  return `
    <div class="report-content">
      <h4>Quality Analysis Report</h4>
      <p><strong>Quality Pass Rate:</strong> ${qualityRate}%</p>
      <p><strong>Good Batches:</strong> ${goodBatches}/${appData.batchData.length}</p>
      <p><strong>Average Quality Score:</strong> ${(appData.batchData.reduce((sum, batch) => sum + batch.quality, 0) / appData.batchData.length).toFixed(2)}%</p>
      
      <h5>Quality Distribution:</h5>
      <ul>
        <li>Excellent (>95%): ${appData.batchData.filter(b => b.quality > 95).length} batches</li>
        <li>Good (85-95%): ${appData.batchData.filter(b => b.quality >= 85 && b.quality <= 95).length} batches</li>
        <li>Fair (<85%): ${appData.batchData.filter(b => b.quality < 85).length} batches</li>
      </ul>
    </div>
  `;
}

function getMostAffectedModule() {
  const moduleCounts = {};
  appData.recentAnomalies.forEach(anomaly => {
    moduleCounts[anomaly.module] = (moduleCounts[anomaly.module] || 0) + 1;
  });
  
  return Object.keys(moduleCounts).reduce((a, b) => 
    moduleCounts[a] > moduleCounts[b] ? a : b
  ) || 'None';
}

function exportData() {
  const reportType = document.getElementById('reportType').value;
  const startDate = document.getElementById('startDate').value;
  const endDate = document.getElementById('endDate').value;
  
  // Create CSV data
  let csvData = '';
  let filename = '';
  
  switch (reportType) {
    case 'anomaly':
      csvData = 'Timestamp,Type,Module,Parameter,Severity\n';
      appData.recentAnomalies.forEach(anomaly => {
        csvData += `${anomaly.timestamp},${anomaly.type},${anomaly.module},${anomaly.parameter},${anomaly.severity}\n`;
      });
      filename = 'anomaly_report.csv';
      break;
      
    case 'production':
      csvData = 'BatchID,Quality,Anomalies,Status\n';
      appData.batchData.forEach(batch => {
        csvData += `${batch.batchId},${batch.quality},${batch.anomalies},${batch.status}\n`;
      });
      filename = 'production_report.csv';
      break;
      
    case 'quality':
      csvData = 'Module,Temperature,Level,Status\n';
      appData.modules.forEach(module => {
        csvData += `${module.name},${module.temperature},${module.level},${module.status}\n`;
      });
      filename = 'quality_report.csv';
      break;
  }
  
  // Download CSV
  const blob = new Blob([csvData], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  window.URL.revokeObjectURL(url);
}

// Real-time simulation
function startRealTimeSimulation() {
  setInterval(updateRealTimeData, 2000); // Update every 2 seconds
}

function updateRealTimeData() {
  const now = new Date();
  const timeLabel = now.toLocaleTimeString();
  
  // Generate simulated data
  appData.modules.forEach((module, index) => {
    // Simulate temperature fluctuations
    const baseTemp = module.temperature;
    const tempVariation = (Math.random() - 0.5) * 2;
    const newTemp = baseTemp + tempVariation;
    module.temperature = newTemp;
    
    // Simulate level changes
    const baseLevelVariation = (Math.random() - 0.5) * 0.1;
    module.level = Math.max(0, Math.min(1, module.level + baseLevelVariation));
    
    // Occasionally simulate status changes
    if (Math.random() < 0.05) { // 5% chance
      const statuses = ['normal', 'warning', 'anomaly'];
      const currentIndex = statuses.indexOf(module.status);
      if (currentIndex > 0 && Math.random() < 0.7) {
        module.status = statuses[currentIndex - 1]; // Tend towards normal
      }
    }
    
    // Update chart data
    if (temperatureChart && temperatureChart.data.datasets[index]) {
      temperatureChart.data.datasets[index].data.push(newTemp);
      if (temperatureChart.data.datasets[index].data.length > 20) {
        temperatureChart.data.datasets[index].data.shift();
      }
    }
    
    if (levelChart && levelChart.data.datasets[index]) {
      levelChart.data.datasets[index].data.push(module.level);
      if (levelChart.data.datasets[index].data.length > 20) {
        levelChart.data.datasets[index].data.shift();
      }
    }
  });
  
  // Update chart labels
  if (temperatureChart) {
    temperatureChart.data.labels.push(timeLabel);
    if (temperatureChart.data.labels.length > 20) {
      temperatureChart.data.labels.shift();
    }
    temperatureChart.update('none');
  }
  
  if (levelChart) {
    levelChart.data.labels.push(timeLabel);
    if (levelChart.data.labels.length > 20) {
      levelChart.data.labels.shift();
    }
    levelChart.update('none');
  }
  
  // Update module cards
  renderModuleCards();
  
  // Update system status
  updateSystemStatus();
}

function updateSystemStatus() {
  const statusIndicator = document.getElementById('systemStatus');
  const statusDot = statusIndicator.querySelector('.status-dot');
  
  const hasAnomalies = appData.modules.some(module => module.status === 'anomaly');
  const hasWarnings = appData.modules.some(module => module.status === 'warning');
  
  if (hasAnomalies) {
    statusDot.className = 'status-dot status-dot--error';
    statusIndicator.querySelector('span:last-child').textContent = 'Anomalies Detected';
  } else if (hasWarnings) {
    statusDot.className = 'status-dot status-dot--warning';
    statusIndicator.querySelector('span:last-child').textContent = 'System Warning';
  } else {
    statusDot.className = 'status-dot status-dot--success';
    statusIndicator.querySelector('span:last-child').textContent = 'System Normal';
  }
}