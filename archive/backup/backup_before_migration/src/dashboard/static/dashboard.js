
// BioCode Dashboard Client
const socket = io();
let chartData = [];
let chart = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    console.log('BioCode Dashboard initializing...');
    
    // Setup WebSocket handlers
    socket.on('connect', function() {
        console.log('Connected to server');
        updateConnectionStatus(true);
    });
    
    socket.on('disconnect', function() {
        console.log('Disconnected from server');
        updateConnectionStatus(false);
    });
    
    socket.on('colony_update', function(data) {
        updateDashboard(data);
    });
    
    // Initialize chart
    initializeChart();
    
    // Load initial data
    loadDashboardData();
    
    // Setup auto-refresh
    setInterval(loadDashboardData, 5000);
});

function updateConnectionStatus(connected) {
    const indicator = document.getElementById('connection-status');
    if (indicator) {
        indicator.className = connected ? 'status-indicator status-alive' : 'status-indicator status-dead';
        indicator.title = connected ? 'Connected' : 'Disconnected';
    }
}

function loadDashboardData() {
    fetch('/api/dashboard')
        .then(response => response.json())
        .then(data => {
            updateMetrics(data.performance_metrics);
            updateRealtimeData(data.real_time_data);
        })
        .catch(error => console.error('Error loading dashboard data:', error));
    
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            updateAgentList(data.agents);
        })
        .catch(error => console.error('Error loading status:', error));
}

function updateMetrics(metrics) {
    for (const [key, value] of Object.entries(metrics)) {
        const element = document.getElementById(`metric-${key}`);
        if (element) {
            element.textContent = value;
        }
    }
}

function updateAgentList(agents) {
    const container = document.getElementById('agent-list');
    if (!container) return;
    
    container.innerHTML = '';
    
    agents.forEach(agent => {
        const item = document.createElement('div');
        item.className = 'agent-item';
        
        const healthPercent = agent.health || 0;
        const statusClass = healthPercent > 0 ? 'status-alive' : 'status-dead';
        
        item.innerHTML = `
            <div>
                <span class="status-indicator ${statusClass}"></span>
                <strong>${agent.id}</strong>
                <small> (Gen ${agent.generation})</small>
            </div>
            <div class="agent-health">
                <div class="health-bar">
                    <div class="health-fill" style="width: ${healthPercent}%"></div>
                </div>
                <span>${healthPercent.toFixed(0)}%</span>
            </div>
        `;
        
        container.appendChild(item);
    });
}

function updateRealtimeData(data) {
    if (!data || data.length === 0) return;
    
    // Update chart
    chartData = data.map(d => ({
        time: new Date(d.timestamp),
        agents: d.active_agents,
        knowledge: d.knowledge_entries
    }));
    
    if (chart) {
        updateChart();
    }
}

function initializeChart() {
    const canvas = document.getElementById('colony-chart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Simple line chart (you can use Chart.js for better charts)
    chart = {
        ctx: ctx,
        width: canvas.width,
        height: canvas.height
    };
    
    updateChart();
}

function updateChart() {
    if (!chart || chartData.length === 0) return;
    
    const ctx = chart.ctx;
    const width = chart.width;
    const height = chart.height;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Draw grid
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 1;
    
    for (let i = 0; i <= 10; i++) {
        const y = (height / 10) * i;
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
    }
    
    // Draw data
    if (chartData.length > 1) {
        const maxAgents = Math.max(...chartData.map(d => d.agents)) || 1;
        const xStep = width / (chartData.length - 1);
        
        // Draw agent count line
        ctx.strokeStyle = '#00ff41';
        ctx.lineWidth = 2;
        ctx.beginPath();
        
        chartData.forEach((data, index) => {
            const x = index * xStep;
            const y = height - (data.agents / maxAgents) * height;
            
            if (index === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        });
        
        ctx.stroke();
    }
}

// Control functions
function launchAgent() {
    const projectPath = prompt('Enter project path to analyze:');
    if (!projectPath) return;
    
    fetch('/api/launch_agent', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            project_path: projectPath,
            config: {
                scan_frequency: 5.0,
                lifespan: 300,
                can_replicate: false,
                can_evolve: true
            }
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(`Agent launched: ${data.agent_id}`);
        } else {
            alert(`Error: ${data.error}`);
        }
    })
    .catch(error => console.error('Error launching agent:', error));
}

function killAllAgents() {
    if (!confirm('Kill all agents?')) return;
    
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            data.agents.forEach(agent => {
                fetch(`/api/kill_agent/${agent.id}`, {method: 'POST'});
            });
        });
}

function viewReports() {
    window.location.href = '/reports';
}

function viewTerminal() {
    window.open('/terminal', '_blank');
}
