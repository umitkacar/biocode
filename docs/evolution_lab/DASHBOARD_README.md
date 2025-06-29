# BioCode Evolution Lab - Realtime Dashboard

## Overview

The Evolution Lab Dashboard provides real-time monitoring and analysis of external projects using the BioCode swarm intelligence framework. It streams live metrics from multiple analyzer cells working in parallel.

## Features

### 🔬 Seven Powerful Analyzers

1. **CodeAnalyzer** - Analyzes code structure, complexity, languages, and frameworks
2. **AIModelAnalyzer** - Detects AI/ML models, frameworks, training scripts, and datasets
3. **SecurityAnalyzer** - Finds vulnerabilities, checks authentication, encryption, and security practices
4. **PerformanceAnalyzer** - Identifies bottlenecks, N+1 queries, memory issues, async problems
5. **TestCoverageAnalyzer** - Analyzes test quality, coverage, CI/CD integration
6. **InnovationAnalyzer** - Detects design patterns, modern features, architectural decisions
7. **DependencyGraphAnalyzer** - Maps module/class/function dependencies, detects circular deps, god classes

### 📊 Real-time Metrics

- **Health Score**: Overall project health (0-100%)
- **Colony Status**: Health of analyzer cells
- **Issue Tracking**: Critical, High, Medium, Low severity issues
- **Live Updates**: Metrics refresh every 5 seconds
- **Suggestions**: Actionable improvement recommendations

### 🎨 Dashboard UI

- Modern dark theme with gradient accents
- Responsive grid layout
- Color-coded severity indicators
- Real-time WebSocket updates
- Animated loading states

## Installation

```bash
# Install dashboard dependencies
pip install websockets aiohttp aiohttp-cors networkx

# Or install all BioCode dashboard features
pip install -e '.[dashboard]'
```

## Running the Dashboard

### Method 1: Direct Script
```bash
python run_dashboard.py
```

### Method 2: Through Demo
```bash
python demos/evolution_lab_demo.py
# Then choose option 2 for realtime dashboard
```

### Method 3: Import and Run
```python
import asyncio
from src.evolution_lab.dashboard_demo import main

asyncio.run(main())
```

## Dashboard Components

### WebSocket Server (ws://localhost:8765)
- Handles real-time client connections
- Broadcasts analysis updates to all connected clients
- Maintains client state and reconnection

### Web Server (http://localhost:8080)
- Serves the dashboard HTML/CSS/JavaScript
- Single-page application with no external dependencies
- Auto-reconnecting WebSocket client

### Analysis Engine
- Spawns 6 analyzer cells for comprehensive analysis
- Runs continuous analysis cycles
- Aggregates results from all analyzers
- Calculates health scores and summaries

## Data Flow

```
Project Directory
    ↓
Evolution Lab Colony
    ↓
[6 Analyzer Cells Running in Parallel]
    ↓
Result Aggregation
    ↓
WebSocket Broadcast
    ↓
Dashboard UI Updates
```

## Metrics Displayed

### Overall Metrics
- Project health score (0-100%)
- Total issues by severity
- Colony health status
- Active analyzer cells

### Per-Analyzer Scores
- Security Score
- Performance Score
- Test Coverage Score
- Innovation Score

### Detailed Analysis
- Code statistics (files, lines, language, complexity)
- Security vulnerabilities and authentication status
- Performance bottlenecks and optimization status
- Test coverage percentage and CI/CD status
- Innovation metrics (design patterns, modern features)
- AI/ML components (models, frameworks, datasets)

### Critical Issues
- Real-time display of top 5 critical issues
- Color-coded by severity

### Suggestions
- Top 10 actionable improvement recommendations
- Aggregated from all analyzers

## Example Output

```
🧬 BioCode Evolution Lab - Realtime Dashboard Demo
==================================================
📁 Target Project: /home/umit/CLAUDE_PROJECT/Ear-segmentation-ai
🔬 Spawning 6 analyzer cells...
--------------------------------------------------
🌐 WebSocket server started on ws://localhost:8765
🌐 Dashboard available at http://localhost:8080
--------------------------------------------------
🚀 Starting continuous analysis...
   Updates every 5 seconds
   Press Ctrl+C to stop
--------------------------------------------------
🔄 Running analysis cycle...
✅ Analysis complete in 2.34s
```

## Architecture

The dashboard uses a biological-inspired architecture:

- **Colony**: Manages the overall analysis system
- **Analyzer Cells**: Individual analysis units with health and energy
- **ECS System**: Entity-Component-System for cell management
- **Mixins**: Observable and Networkable behaviors
- **Aspects**: Logging and Performance monitoring

## Customization

### Change Target Project
Edit the `project_path` in `dashboard_demo.py`:
```python
project_path = "/path/to/your/project"
```

### Adjust Update Interval
Change `self.update_interval` in `RealtimeDashboard`:
```python
self.update_interval = 10.0  # seconds
```

### Add New Analyzers
1. Create new analyzer in `src/evolution_lab/analyzers/`
2. Import in `colony.py`
3. Add to `spawn_analyzer_cells()` method

## Troubleshooting

### WebSocket Connection Failed
- Check if port 8765 is available
- Ensure WebSocket server is running
- Check browser console for errors

### Dashboard Not Loading
- Verify port 8080 is available
- Check if aiohttp server started successfully
- Try different browser

### Analysis Errors
- Ensure target project path exists
- Check analyzer cell health in colony status
- Review console output for specific errors

## Future Enhancements

- [ ] Historical data persistence
- [ ] Multiple project comparison
- [ ] Export analysis reports
- [ ] Customizable analyzer configurations
- [ ] Authentication for dashboard access
- [ ] Docker containerization
- [ ] Prometheus metrics export