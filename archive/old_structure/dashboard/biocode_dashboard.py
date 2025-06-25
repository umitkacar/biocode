#!/usr/bin/env python3
"""
BioCode Agent Colony Dashboard - Real-time monitoring and analytics
"""
import os
import sys
import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict, deque
import logging

# Flask imports
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.biocode_agent import BioCodeAgent, AgentDNA

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize Flask app
app = Flask(__name__, 
    template_folder='templates',
    static_folder='static'
)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', os.urandom(24).hex())

# Configure CORS
cors_origins = os.environ.get('BIOCODE_CORS_ORIGINS', 'http://localhost:5000').split(',')
CORS(app, origins=cors_origins)
socketio = SocketIO(app, cors_allowed_origins=cors_origins)

# Dashboard state
class DashboardState:
    def __init__(self):
        self.active_colonies = {}
        self.agent_history = deque(maxlen=1000)
        self.pattern_analytics = defaultdict(int)
        self.performance_metrics = {
            'total_agents_created': 0,
            'total_files_analyzed': 0,
            'total_patterns_discovered': 0,
            'total_errors_detected': 0,
            'avg_agent_lifespan': 0,
            'peak_colony_size': 0
        }
        self.real_time_data = deque(maxlen=100)
        self._update_thread = None
        self._running = False

    def start_monitoring(self):
        """Start real-time monitoring"""
        self._running = True
        self._update_thread = threading.Thread(target=self._monitor_loop)
        self._update_thread.daemon = True
        self._update_thread.start()

    def stop_monitoring(self):
        """Stop monitoring"""
        self._running = False
        if self._update_thread:
            self._update_thread.join()

    def _monitor_loop(self):
        """Main monitoring loop"""
        while self._running:
            try:
                # Get colony status
                colony_status = BioCodeAgent.get_colony_status()
                
                # Update metrics
                self._update_metrics(colony_status)
                
                # Prepare real-time data
                rt_data = {
                    'timestamp': datetime.now().isoformat(),
                    'active_agents': colony_status['active_agents'],
                    'knowledge_entries': colony_status['total_knowledge_entries'],
                    'agents': colony_status['agents']
                }
                
                self.real_time_data.append(rt_data)
                
                # Emit to connected clients
                socketio.emit('colony_update', rt_data)
                
                # Emit terminal logs
                terminal_logs = BioCodeAgent.get_terminal_logs(20)
                if terminal_logs:
                    socketio.emit('terminal_update', {'logs': terminal_logs})
                
                time.sleep(1)  # Update every second
                
            except Exception as e:
                logger.error(f"Monitor loop error: {e}")

    def _update_metrics(self, colony_status):
        """Update performance metrics"""
        current_size = colony_status['active_agents']
        
        # Update peak colony size
        if current_size > self.performance_metrics['peak_colony_size']:
            self.performance_metrics['peak_colony_size'] = current_size
            
        # Update total agents (approximate from knowledge entries)
        self.performance_metrics['total_agents_created'] = colony_status['total_knowledge_entries'] // 4

    def get_dashboard_data(self):
        """Get current dashboard data"""
        return {
            'performance_metrics': self.performance_metrics,
            'real_time_data': list(self.real_time_data),
            'pattern_analytics': dict(self.pattern_analytics),
            'active_colonies': self.active_colonies
        }

# Global dashboard state
dashboard = DashboardState()

# Routes
@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/status')
def api_status():
    """Get current colony status"""
    return jsonify(BioCodeAgent.get_colony_status())

@app.route('/api/dashboard')
def api_dashboard():
    """Get dashboard data"""
    return jsonify(dashboard.get_dashboard_data())

@app.route('/api/reports')
def api_reports():
    """List available reports"""
    reports_dir = Path.home() / '.biocode_agent' / 'reports'
    reports = []
    
    if reports_dir.exists():
        for report_file in reports_dir.glob('*.json'):
            try:
                with open(report_file, 'r') as f:
                    report_data = json.load(f)
                    reports.append({
                        'filename': report_file.name,
                        'agent_id': report_data.get('agent_id', 'unknown'),
                        'timestamp': report_file.stat().st_mtime,
                        'size': report_file.stat().st_size
                    })
            except Exception as e:
                logger.error(f"Error reading report {report_file}: {e}")
                
    # Sort by timestamp, newest first
    reports.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return jsonify(reports[:50])  # Return latest 50 reports

@app.route('/api/report/<filename>')
def api_report_detail(filename):
    """Get specific report content"""
    reports_dir = Path.home() / '.biocode_agent' / 'reports'
    report_path = reports_dir / filename
    
    if report_path.exists() and report_path.suffix == '.json':
        with open(report_path, 'r') as f:
            return jsonify(json.load(f))
    else:
        return jsonify({'error': 'Report not found'}), 404

@app.route('/api/launch_agent', methods=['POST'])
def api_launch_agent():
    """Launch a new agent"""
    data = request.json
    project_path = data.get('project_path')
    agent_config = data.get('config', {})
    
    if not project_path or not os.path.exists(project_path):
        return jsonify({'error': 'Invalid project path'}), 400
        
    try:
        # Create custom DNA
        dna = AgentDNA(
            agent_id=f"dashboard_{int(time.time())}",
            scan_frequency=agent_config.get('scan_frequency', 5.0),
            lifespan=agent_config.get('lifespan', 300),
            can_replicate=agent_config.get('can_replicate', False),
            can_evolve=agent_config.get('can_evolve', True),
            can_communicate=agent_config.get('can_communicate', True)
        )
        
        # Create and start agent
        agent = BioCodeAgent(project_path, dna, sandbox_mode=True)
        agent.start()
        
        return jsonify({
            'success': True,
            'agent_id': dna.agent_id,
            'message': f'Agent {dna.agent_id} launched successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/kill_agent/<agent_id>', methods=['POST'])
def api_kill_agent(agent_id):
    """Terminate specific agent"""
    if agent_id in BioCodeAgent._active_agents:
        agent = BioCodeAgent._active_agents[agent_id]
        agent.apoptosis("user_terminated")
        return jsonify({'success': True, 'message': f'Agent {agent_id} terminated'})
    else:
        return jsonify({'error': 'Agent not found'}), 404

@app.route('/api/terminal_logs')
def api_terminal_logs():
    """Get recent terminal logs"""
    logs = BioCodeAgent.get_terminal_logs(100)
    return jsonify(logs)

@app.route('/api/colony_knowledge')
def api_colony_knowledge():
    """Get colony knowledge entries"""
    knowledge = list(BioCodeAgent._colony_knowledge)
    
    # Analyze knowledge patterns
    patterns = defaultdict(int)
    for entry in knowledge:
        if isinstance(entry, dict):
            entry_type = entry.get('type', 'unknown')
            patterns[entry_type] += 1
            
    return jsonify({
        'total_entries': len(knowledge),
        'recent_entries': knowledge[-20:],  # Last 20 entries
        'entry_patterns': dict(patterns)
    })

@app.route('/reports')
def reports_page():
    """Reports viewer page"""
    return render_template('reports.html')

@app.route('/terminal')
def terminal_page():
    """Terminal viewer page"""
    return render_template('terminal.html')

@app.route('/visualization')
def visualization_page():
    """Agent visualization page"""
    return render_template('visualization.html')

# WebSocket events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info('Client connected')
    emit('connected', {'data': 'Connected to BioCode Dashboard'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info('Client disconnected')

@socketio.on('request_update')
def handle_update_request():
    """Handle manual update request"""
    colony_status = BioCodeAgent.get_colony_status()
    emit('colony_update', {
        'timestamp': datetime.now().isoformat(),
        'data': colony_status
    })

# Static file serving
@app.route('/static/<path:path>')
def send_static(path):
    """Serve static files"""
    return send_from_directory('static', path)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# CLI commands
def create_static_files():
    """Create static HTML/CSS/JS files for dashboard"""
    static_dir = Path(__file__).parent / 'static'
    templates_dir = Path(__file__).parent / 'templates'
    
    # Create directories
    static_dir.mkdir(exist_ok=True)
    templates_dir.mkdir(exist_ok=True)
    
    # Create CSS file
    css_content = """
/* BioCode Dashboard Styles */
:root {
    --primary-color: #00ff41;
    --secondary-color: #0080ff;
    --danger-color: #ff0040;
    --bg-color: #0a0a0a;
    --card-bg: #1a1a1a;
    --text-color: #e0e0e0;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Consolas', 'Monaco', monospace;
    background-color: var(--bg-color);
    color: var(--text-color);
    line-height: 1.6;
}

.container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 20px;
}

header {
    text-align: center;
    padding: 20px 0;
    border-bottom: 2px solid var(--primary-color);
    margin-bottom: 30px;
}

h1 {
    color: var(--primary-color);
    font-size: 2.5em;
    text-shadow: 0 0 10px var(--primary-color);
}

.subtitle {
    color: var(--secondary-color);
    margin-top: 10px;
}

.dashboard-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.card {
    background: var(--card-bg);
    border: 1px solid #333;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    transition: transform 0.2s;
}

.card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.5);
}

.card h2 {
    color: var(--primary-color);
    margin-bottom: 15px;
    font-size: 1.3em;
}

.metric {
    display: flex;
    justify-content: space-between;
    margin-bottom: 10px;
    padding: 5px 0;
    border-bottom: 1px solid #333;
}

.metric-value {
    color: var(--secondary-color);
    font-weight: bold;
}

.agent-list {
    max-height: 300px;
    overflow-y: auto;
}

.agent-item {
    background: #222;
    padding: 10px;
    margin-bottom: 10px;
    border-radius: 4px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.agent-health {
    display: flex;
    align-items: center;
    gap: 10px;
}

.health-bar {
    width: 100px;
    height: 10px;
    background: #333;
    border-radius: 5px;
    overflow: hidden;
}

.health-fill {
    height: 100%;
    background: var(--primary-color);
    transition: width 0.3s;
}

.controls {
    margin: 30px 0;
    text-align: center;
}

button {
    background: var(--primary-color);
    color: var(--bg-color);
    border: none;
    padding: 10px 20px;
    margin: 0 10px;
    border-radius: 4px;
    font-weight: bold;
    cursor: pointer;
    transition: all 0.3s;
}

button:hover {
    background: var(--secondary-color);
    transform: scale(1.05);
}

button:active {
    transform: scale(0.95);
}

.status-indicator {
    display: inline-block;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    margin-right: 5px;
}

.status-alive {
    background: var(--primary-color);
    box-shadow: 0 0 5px var(--primary-color);
}

.status-dead {
    background: var(--danger-color);
}

#real-time-graph {
    width: 100%;
    height: 300px;
    background: #0a0a0a;
    border: 1px solid #333;
    border-radius: 8px;
    margin-top: 20px;
}

.log-entry {
    padding: 5px;
    margin: 2px 0;
    background: #1a1a1a;
    border-left: 3px solid var(--secondary-color);
    font-size: 0.9em;
}

@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
}

.live-indicator {
    animation: pulse 2s infinite;
}
"""
    
    (static_dir / 'dashboard.css').write_text(css_content)
    
    # Create JavaScript file
    js_content = """
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
    window.open('/reports', '_blank');
}
"""
    
    (static_dir / 'dashboard.js').write_text(js_content)
    
    # Create HTML template
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BioCode Agent Colony Dashboard</title>
    <link rel="stylesheet" href="/static/dashboard.css">
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
</head>
<body>
    <div class="container">
        <header>
            <h1>🧬 BioCode Agent Colony Dashboard</h1>
            <p class="subtitle">Real-time monitoring and analytics for living code agents</p>
            <span id="connection-status" class="status-indicator status-dead" title="Disconnected"></span>
        </header>
        
        <div class="controls">
            <button onclick="launchAgent()">🚀 Launch Agent</button>
            <button onclick="killAllAgents()">💀 Kill All Agents</button>
            <button onclick="viewReports()">📊 View Reports</button>
            <button onclick="location.reload()">🔄 Refresh</button>
        </div>
        
        <div class="dashboard-grid">
            <div class="card">
                <h2>Colony Metrics</h2>
                <div class="metric">
                    <span>Active Agents:</span>
                    <span class="metric-value" id="metric-active_agents">0</span>
                </div>
                <div class="metric">
                    <span>Total Created:</span>
                    <span class="metric-value" id="metric-total_agents_created">0</span>
                </div>
                <div class="metric">
                    <span>Peak Colony Size:</span>
                    <span class="metric-value" id="metric-peak_colony_size">0</span>
                </div>
                <div class="metric">
                    <span>Files Analyzed:</span>
                    <span class="metric-value" id="metric-total_files_analyzed">0</span>
                </div>
                <div class="metric">
                    <span>Patterns Found:</span>
                    <span class="metric-value" id="metric-total_patterns_discovered">0</span>
                </div>
            </div>
            
            <div class="card">
                <h2>Active Agents</h2>
                <div id="agent-list" class="agent-list">
                    <p>No active agents</p>
                </div>
            </div>
            
            <div class="card">
                <h2>Colony Activity</h2>
                <canvas id="colony-chart" width="400" height="200"></canvas>
            </div>
        </div>
        
        <div class="card">
            <h2>Real-time Logs</h2>
            <div id="log-container" style="max-height: 200px; overflow-y: auto;">
                <div class="log-entry live-indicator">Dashboard initialized...</div>
            </div>
        </div>
    </div>
    
    <script src="/static/dashboard.js"></script>
</body>
</html>
"""
    
    (templates_dir / 'dashboard.html').write_text(html_content)
    
    logger.info("Static files created successfully")

# Main entry point
def run_dashboard(host='127.0.0.1', port=5000, debug=False):
    """Run the dashboard server"""
    print(f"""
    🧬 BioCode Agent Colony Dashboard
    ================================
    
    Starting dashboard server...
    URL: http://{host}:{port}
    
    Press Ctrl+C to stop
    """)
    
    # Create static files if they don't exist
    create_static_files()
    
    # Start monitoring
    dashboard.start_monitoring()
    
    try:
        # Run Flask app with SocketIO
        socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)
    finally:
        # Stop monitoring
        dashboard.stop_monitoring()

if __name__ == '__main__':
    run_dashboard(debug=True)