"""
BioCode Evolution Lab - Realtime Dashboard Demo
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
import websockets
from aiohttp import web
import aiohttp_cors

from src.evolution_lab.colony import EvolutionLabColony


class RealtimeDashboard:
    """Realtime dashboard for Evolution Lab monitoring"""
    
    def __init__(self, colony: EvolutionLabColony):
        self.colony = colony
        self.connected_clients = set()
        self.analysis_running = False
        self.update_interval = 5.0  # seconds
        
    async def websocket_handler(self, websocket):
        """Handle WebSocket connections"""
        self.connected_clients.add(websocket)
        print(f"🔌 Client connected. Total clients: {len(self.connected_clients)}")
        
        try:
            # Send initial data
            if self.colony.get_latest_snapshot():
                await self.send_update(websocket)
                
            # Keep connection alive
            await websocket.wait_closed()
        finally:
            self.connected_clients.remove(websocket)
            print(f"🔌 Client disconnected. Total clients: {len(self.connected_clients)}")
            
    async def send_update(self, websocket=None):
        """Send analysis update to clients"""
        snapshot = self.colony.get_latest_snapshot()
        if not snapshot:
            return
            
        # Prepare comprehensive data
        data = {
            'timestamp': datetime.now().isoformat(),
            'project_path': snapshot.project_path,
            'health_score': snapshot.health_score,
            'metrics': snapshot.metrics,
            'issues': snapshot.issues,
            'suggestions': snapshot.suggestions[:10],  # Top 10 suggestions
            'colony_health': self.colony.get_colony_health(),
            'summary': self._generate_summary(snapshot),
        }
        
        message = json.dumps(data)
        
        if websocket:
            await websocket.send(message)
        else:
            # Broadcast to all connected clients
            if self.connected_clients:
                await asyncio.gather(
                    *[client.send(message) for client in self.connected_clients],
                    return_exceptions=True
                )
                
    def _generate_summary(self, snapshot):
        """Generate summary statistics from snapshot"""
        summary = {
            'total_issues': len(snapshot.issues),
            'critical_issues': len([i for i in snapshot.issues if i.get('severity') == 'critical']),
            'high_issues': len([i for i in snapshot.issues if i.get('severity') == 'high']),
            'medium_issues': len([i for i in snapshot.issues if i.get('severity') == 'medium']),
            'low_issues': len([i for i in snapshot.issues if i.get('severity') == 'low']),
        }
        
        # Extract key metrics from each analyzer
        if 'CodeAnalyzer' in snapshot.metrics:
            code = snapshot.metrics['CodeAnalyzer']
            summary['code_stats'] = {
                'total_files': code.get('total_files', 0),
                'total_lines': code.get('total_lines', 0),
                'primary_language': code.get('primary_language', 'Unknown'),
                'complexity_score': code.get('complexity_score', 0),
            }
            
        if 'SecurityAnalyzer' in snapshot.metrics:
            security = snapshot.metrics['SecurityAnalyzer']
            summary['security_stats'] = {
                'security_score': security.get('security_score', 0),
                'vulnerabilities': sum(len(v) for v in security.get('vulnerabilities', {}).values()),
                'authentication': bool(security.get('authentication', {}).get('methods')),
                'encryption': security.get('encryption', {}).get('tls_ssl', False),
            }
            
        if 'PerformanceAnalyzer' in snapshot.metrics:
            perf = snapshot.metrics['PerformanceAnalyzer']
            summary['performance_stats'] = {
                'performance_score': perf.get('performance_score', 0),
                'nested_loops': len(perf.get('algorithmic_complexity', {}).get('nested_loops', [])),
                'async_functions': perf.get('async_patterns', {}).get('async_functions', 0),
                'caching_enabled': perf.get('caching', {}).get('cache_decorators', 0) > 0,
            }
            
        if 'TestCoverageAnalyzer' in snapshot.metrics:
            test = snapshot.metrics['TestCoverageAnalyzer']
            summary['test_stats'] = {
                'test_score': test.get('test_score', 0),
                'coverage': test.get('coverage_report', {}).get('total_coverage', 0),
                'total_tests': test.get('test_statistics', {}).get('total_test_functions', 0),
                'ci_configured': test.get('ci_integration', {}).get('ci_configured', False),
            }
            
        if 'InnovationAnalyzer' in snapshot.metrics:
            innovation = snapshot.metrics['InnovationAnalyzer']
            summary['innovation_stats'] = {
                'innovation_score': innovation.get('innovation_score', 0),
                'design_patterns': innovation.get('design_patterns', {}).get('unique_patterns_count', 0),
                'modern_features': innovation.get('modern_features', {}).get('adoption_rate', 0),
                'tech_diversity': innovation.get('tech_stack_maturity', {}).get('stack_diversity', 0),
            }
            
        if 'AIModelAnalyzer' in snapshot.metrics:
            ai = snapshot.metrics['AIModelAnalyzer']
            summary['ai_stats'] = {
                'model_files': ai.get('model_files', {}).get('count', 0),
                'frameworks': list(k for k, v in ai.get('frameworks', {}).items() if v),
                'training_scripts': ai.get('training', {}).get('scripts_found', 0),
                'datasets': ai.get('data', {}).get('datasets_found', 0),
            }
            
        return summary
        
    async def continuous_analysis(self, project_path: str):
        """Run continuous analysis and send updates"""
        self.analysis_running = True
        
        while self.analysis_running:
            try:
                print(f"🔄 Running analysis cycle...")
                start_time = time.time()
                
                # Run analysis
                await self.colony.analyze_project(project_path)
                
                # Send update to all clients
                await self.send_update()
                
                analysis_time = time.time() - start_time
                print(f"✅ Analysis complete in {analysis_time:.2f}s")
                
                # Wait before next cycle
                await asyncio.sleep(max(0, self.update_interval - analysis_time))
                
            except Exception as e:
                print(f"❌ Error in analysis: {e}")
                await asyncio.sleep(5)
                
    async def serve_dashboard(self, request):
        """Serve the HTML dashboard"""
        html_content = '''<!DOCTYPE html>
<html>
<head>
    <title>BioCode Evolution Lab - Realtime Dashboard</title>
    <meta charset="utf-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0a;
            color: #e0e0e0;
            line-height: 1.6;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border-radius: 10px;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #00ff88, #00bbff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .status {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            margin: 5px;
        }
        .status.connected { background: #00ff88; color: #000; }
        .status.disconnected { background: #ff4444; color: #fff; }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: #1a1a2e;
            border-radius: 10px;
            padding: 20px;
            border: 1px solid #2a2a3e;
            transition: transform 0.2s;
        }
        .card:hover {
            transform: translateY(-2px);
            border-color: #00ff88;
        }
        .card h3 {
            color: #00ff88;
            margin-bottom: 15px;
            font-size: 1.2em;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #2a2a3e;
        }
        .metric:last-child { border-bottom: none; }
        .metric-value {
            font-weight: bold;
            color: #00bbff;
        }
        .score {
            font-size: 2em;
            font-weight: bold;
            text-align: center;
            padding: 20px;
            border-radius: 50%;
            width: 100px;
            height: 100px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto;
        }
        .score.high { background: linear-gradient(135deg, #00ff88, #00cc66); color: #000; }
        .score.medium { background: linear-gradient(135deg, #ffaa00, #ff8800); color: #000; }
        .score.low { background: linear-gradient(135deg, #ff4444, #cc0000); color: #fff; }
        .issues {
            margin-top: 20px;
        }
        .issue {
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
            font-size: 0.9em;
        }
        .issue.critical { background: #cc0000; }
        .issue.high { background: #ff4444; }
        .issue.medium { background: #ff8800; }
        .issue.low { background: #666; }
        .suggestions {
            background: #16213e;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
        }
        .suggestion {
            padding: 8px;
            margin: 5px 0;
            background: #1a1a2e;
            border-radius: 5px;
            border-left: 3px solid #00ff88;
        }
        .timestamp {
            text-align: center;
            color: #666;
            margin: 20px 0;
        }
        .loading {
            text-align: center;
            padding: 50px;
            font-size: 1.2em;
        }
        .analyzer-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .analyzer-card {
            background: #16213e;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        .analyzer-score {
            font-size: 1.5em;
            font-weight: bold;
            margin: 10px 0;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        .analyzing {
            animation: pulse 2s infinite;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧬 BioCode Evolution Lab</h1>
            <p>Realtime Project Intelligence Dashboard</p>
            <span id="status" class="status disconnected">Disconnected</span>
            <span id="project" class="status">No Project</span>
        </div>
        
        <div id="loading" class="loading analyzing">
            🔬 Connecting to Evolution Lab...
        </div>
        
        <div id="dashboard" style="display: none;">
            <div class="grid">
                <div class="card">
                    <h3>🏥 Overall Health</h3>
                    <div id="health-score" class="score">-</div>
                    <div id="colony-status"></div>
                </div>
                
                <div class="card">
                    <h3>📊 Issues Summary</h3>
                    <div id="issues-summary"></div>
                </div>
                
                <div class="card">
                    <h3>🔍 Code Analysis</h3>
                    <div id="code-stats"></div>
                </div>
            </div>
            
            <div class="analyzer-grid" id="analyzer-scores"></div>
            
            <div class="grid">
                <div class="card">
                    <h3>🛡️ Security Analysis</h3>
                    <div id="security-stats"></div>
                </div>
                
                <div class="card">
                    <h3>⚡ Performance Analysis</h3>
                    <div id="performance-stats"></div>
                </div>
                
                <div class="card">
                    <h3>🧪 Test Coverage</h3>
                    <div id="test-stats"></div>
                </div>
                
                <div class="card">
                    <h3>💡 Innovation Score</h3>
                    <div id="innovation-stats"></div>
                </div>
                
                <div class="card">
                    <h3>🤖 AI/ML Components</h3>
                    <div id="ai-stats"></div>
                </div>
            </div>
            
            <div class="issues">
                <h3>🚨 Critical Issues</h3>
                <div id="critical-issues"></div>
            </div>
            
            <div class="suggestions">
                <h3>💡 Top Suggestions</h3>
                <div id="suggestions"></div>
            </div>
            
            <div class="timestamp" id="timestamp"></div>
        </div>
    </div>
    
    <script>
        let ws = null;
        let reconnectInterval = null;
        
        function connect() {
            ws = new WebSocket('ws://localhost:8765');
            
            ws.onopen = () => {
                console.log('Connected to Evolution Lab');
                document.getElementById('status').className = 'status connected';
                document.getElementById('status').textContent = 'Connected';
                clearInterval(reconnectInterval);
            };
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                updateDashboard(data);
            };
            
            ws.onclose = () => {
                console.log('Disconnected from Evolution Lab');
                document.getElementById('status').className = 'status disconnected';
                document.getElementById('status').textContent = 'Disconnected';
                
                // Reconnect after 3 seconds
                if (!reconnectInterval) {
                    reconnectInterval = setInterval(() => {
                        console.log('Attempting to reconnect...');
                        connect();
                    }, 3000);
                }
            };
            
            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
        }
        
        function updateDashboard(data) {
            document.getElementById('loading').style.display = 'none';
            document.getElementById('dashboard').style.display = 'block';
            
            // Update project path
            document.getElementById('project').textContent = data.project_path.split('/').pop();
            
            // Update health score
            const healthScore = Math.round(data.health_score);
            const healthEl = document.getElementById('health-score');
            healthEl.textContent = healthScore + '%';
            healthEl.className = 'score ' + (healthScore >= 70 ? 'high' : healthScore >= 40 ? 'medium' : 'low');
            
            // Update colony status
            const colony = data.colony_health;
            document.getElementById('colony-status').innerHTML = `
                <div class="metric"><span>Status</span><span class="metric-value">${colony.status}</span></div>
                <div class="metric"><span>Active Cells</span><span class="metric-value">${colony.total_cells}</span></div>
                <div class="metric"><span>Healthy Cells</span><span class="metric-value">${colony.healthy_cells}</span></div>
                <div class="metric"><span>Avg Energy</span><span class="metric-value">${Math.round(colony.average_energy)}%</span></div>
            `;
            
            // Update issues summary
            const summary = data.summary;
            document.getElementById('issues-summary').innerHTML = `
                <div class="metric"><span>Critical</span><span class="metric-value">${summary.critical_issues}</span></div>
                <div class="metric"><span>High</span><span class="metric-value">${summary.high_issues}</span></div>
                <div class="metric"><span>Medium</span><span class="metric-value">${summary.medium_issues}</span></div>
                <div class="metric"><span>Low</span><span class="metric-value">${summary.low_issues}</span></div>
                <div class="metric"><span>Total</span><span class="metric-value">${summary.total_issues}</span></div>
            `;
            
            // Update analyzer scores
            const scores = [
                { name: '🛡️ Security', score: summary.security_stats?.security_score || 0 },
                { name: '⚡ Performance', score: summary.performance_stats?.performance_score || 0 },
                { name: '🧪 Test Coverage', score: summary.test_stats?.test_score || 0 },
                { name: '💡 Innovation', score: summary.innovation_stats?.innovation_score || 0 },
            ];
            
            document.getElementById('analyzer-scores').innerHTML = scores.map(s => `
                <div class="analyzer-card">
                    <div>${s.name}</div>
                    <div class="analyzer-score" style="color: ${s.score >= 70 ? '#00ff88' : s.score >= 40 ? '#ffaa00' : '#ff4444'}">
                        ${Math.round(s.score)}%
                    </div>
                </div>
            `).join('');
            
            // Update code stats
            if (summary.code_stats) {
                document.getElementById('code-stats').innerHTML = `
                    <div class="metric"><span>Language</span><span class="metric-value">${summary.code_stats.primary_language}</span></div>
                    <div class="metric"><span>Files</span><span class="metric-value">${summary.code_stats.total_files}</span></div>
                    <div class="metric"><span>Lines</span><span class="metric-value">${summary.code_stats.total_lines.toLocaleString()}</span></div>
                    <div class="metric"><span>Complexity</span><span class="metric-value">${summary.code_stats.complexity_score.toFixed(1)}</span></div>
                `;
            }
            
            // Update security stats
            if (summary.security_stats) {
                document.getElementById('security-stats').innerHTML = `
                    <div class="metric"><span>Score</span><span class="metric-value">${Math.round(summary.security_stats.security_score)}%</span></div>
                    <div class="metric"><span>Vulnerabilities</span><span class="metric-value">${summary.security_stats.vulnerabilities}</span></div>
                    <div class="metric"><span>Authentication</span><span class="metric-value">${summary.security_stats.authentication ? '✓' : '✗'}</span></div>
                    <div class="metric"><span>Encryption</span><span class="metric-value">${summary.security_stats.encryption ? '✓' : '✗'}</span></div>
                `;
            }
            
            // Update performance stats
            if (summary.performance_stats) {
                document.getElementById('performance-stats').innerHTML = `
                    <div class="metric"><span>Score</span><span class="metric-value">${Math.round(summary.performance_stats.performance_score)}%</span></div>
                    <div class="metric"><span>Nested Loops</span><span class="metric-value">${summary.performance_stats.nested_loops}</span></div>
                    <div class="metric"><span>Async Functions</span><span class="metric-value">${summary.performance_stats.async_functions}</span></div>
                    <div class="metric"><span>Caching</span><span class="metric-value">${summary.performance_stats.caching_enabled ? '✓' : '✗'}</span></div>
                `;
            }
            
            // Update test stats
            if (summary.test_stats) {
                document.getElementById('test-stats').innerHTML = `
                    <div class="metric"><span>Score</span><span class="metric-value">${Math.round(summary.test_stats.test_score)}%</span></div>
                    <div class="metric"><span>Coverage</span><span class="metric-value">${Math.round(summary.test_stats.coverage)}%</span></div>
                    <div class="metric"><span>Total Tests</span><span class="metric-value">${summary.test_stats.total_tests}</span></div>
                    <div class="metric"><span>CI/CD</span><span class="metric-value">${summary.test_stats.ci_configured ? '✓' : '✗'}</span></div>
                `;
            }
            
            // Update innovation stats
            if (summary.innovation_stats) {
                document.getElementById('innovation-stats').innerHTML = `
                    <div class="metric"><span>Score</span><span class="metric-value">${Math.round(summary.innovation_stats.innovation_score)}%</span></div>
                    <div class="metric"><span>Design Patterns</span><span class="metric-value">${summary.innovation_stats.design_patterns}</span></div>
                    <div class="metric"><span>Modern Features</span><span class="metric-value">${Math.round(summary.innovation_stats.modern_features)}%</span></div>
                    <div class="metric"><span>Tech Diversity</span><span class="metric-value">${summary.innovation_stats.tech_diversity}</span></div>
                `;
            }
            
            // Update AI stats
            if (summary.ai_stats) {
                document.getElementById('ai-stats').innerHTML = `
                    <div class="metric"><span>Model Files</span><span class="metric-value">${summary.ai_stats.model_files}</span></div>
                    <div class="metric"><span>Frameworks</span><span class="metric-value">${summary.ai_stats.frameworks.join(', ') || 'None'}</span></div>
                    <div class="metric"><span>Training Scripts</span><span class="metric-value">${summary.ai_stats.training_scripts}</span></div>
                    <div class="metric"><span>Datasets</span><span class="metric-value">${summary.ai_stats.datasets}</span></div>
                `;
            }
            
            // Update critical issues
            const criticalIssues = data.issues.filter(i => i.severity === 'critical').slice(0, 5);
            document.getElementById('critical-issues').innerHTML = criticalIssues.length ? 
                criticalIssues.map(i => `<div class="issue critical">${i.message}</div>`).join('') :
                '<div class="issue medium">No critical issues found! 🎉</div>';
            
            // Update suggestions
            document.getElementById('suggestions').innerHTML = data.suggestions.slice(0, 10)
                .map(s => `<div class="suggestion">💡 ${s}</div>`).join('');
            
            // Update timestamp
            document.getElementById('timestamp').textContent = 
                'Last updated: ' + new Date(data.timestamp).toLocaleString();
        }
        
        // Connect on load
        connect();
    </script>
</body>
</html>'''
        
        return web.Response(text=html_content, content_type='text/html')
        
    def stop(self):
        """Stop the dashboard"""
        self.analysis_running = False


async def main():
    """Run the realtime dashboard demo"""
    print("🧬 BioCode Evolution Lab - Realtime Dashboard Demo")
    print("=" * 50)
    
    # Create colony
    colony = EvolutionLabColony()
    dashboard = RealtimeDashboard(colony)
    
    # Project to analyze
    project_path = "/home/umit/CLAUDE_PROJECT/Ear-segmentation-ai"
    
    print(f"📁 Target Project: {project_path}")
    print(f"🔬 Spawning {len(colony.analyzer_cells)} analyzer cells...")
    print("-" * 50)
    
    # Start WebSocket server
    ws_server = await websockets.serve(
        dashboard.websocket_handler,
        "localhost",
        8765
    )
    print("🌐 WebSocket server started on ws://localhost:8765")
    
    # Start HTTP server for dashboard
    app = web.Application()
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })
    
    # Add routes
    resource = app.router.add_resource("/")
    route = resource.add_route("GET", dashboard.serve_dashboard)
    cors.add(route)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()
    
    print("🌐 Dashboard available at http://localhost:8080")
    print("-" * 50)
    print("🚀 Starting continuous analysis...")
    print("   Updates every 5 seconds")
    print("   Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        # Start continuous analysis
        await dashboard.continuous_analysis(project_path)
    except KeyboardInterrupt:
        print("\n⏹️  Stopping dashboard...")
    finally:
        dashboard.stop()
        ws_server.close()
        await ws_server.wait_closed()
        await runner.cleanup()
        print("✅ Dashboard stopped")


if __name__ == "__main__":
    asyncio.run(main())