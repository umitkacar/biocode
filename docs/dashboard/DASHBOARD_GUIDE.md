# BioCode Agent Colony Dashboard Guide

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch Dashboard
```bash
python launch_dashboard.py
```

This will:
- Start the web server on http://localhost:5000
- Open your browser automatically
- Create necessary static files

### 3. Launch with Demo Agent
```bash
python launch_dashboard.py --demo
```

## 🎯 Features

### Real-time Monitoring
- **Active Agent Tracking**: See all living agents, their health, energy, and generation
- **Colony Metrics**: Total agents created, peak colony size, files analyzed
- **Live Activity Graph**: Visual representation of colony activity over time
- **Real-time Logs**: Stream of agent activities and events

### Agent Management
- **Launch New Agents**: Start agents for specific projects with custom configurations
- **Kill Agents**: Terminate individual or all agents
- **View Reports**: Access detailed JSON reports from completed agents

### Colony Intelligence
- **Pattern Analytics**: See discovered code patterns across the colony
- **Knowledge Sharing**: Monitor how agents share information
- **Performance Metrics**: Track agent efficiency and resource usage

## 🛠️ Advanced Usage

### Custom Host/Port
```bash
python launch_dashboard.py --host 0.0.0.0 --port 8080
```

### Debug Mode
```bash
python launch_dashboard.py --debug
```

### Headless Mode (No Browser)
```bash
python launch_dashboard.py --no-browser
```

## 📊 Dashboard Sections

### 1. Colony Metrics Card
Displays:
- Active Agents (currently alive)
- Total Agents Created (historical)
- Peak Colony Size (maximum concurrent)
- Files Analyzed (across all agents)
- Patterns Discovered (unique patterns)

### 2. Active Agents List
Shows each agent with:
- Agent ID and generation
- Health bar (0-100%)
- Alive/dead status indicator

### 3. Colony Activity Chart
Real-time visualization of:
- Agent population over time
- Knowledge entries growth
- Activity patterns

### 4. Control Panel
- **Launch Agent**: Configure and start new agent
- **Kill All Agents**: Emergency stop for all agents
- **View Reports**: Open reports directory
- **Refresh**: Manual dashboard update

## 🔧 API Endpoints

### REST API
- `GET /api/status` - Current colony status
- `GET /api/dashboard` - Dashboard metrics
- `GET /api/reports` - List available reports
- `GET /api/report/<filename>` - Get specific report
- `POST /api/launch_agent` - Launch new agent
- `POST /api/kill_agent/<id>` - Terminate agent
- `GET /api/colony_knowledge` - Colony knowledge base

### WebSocket Events
- `connect` - Client connected
- `disconnect` - Client disconnected
- `colony_update` - Real-time colony data
- `request_update` - Manual update request

## 🎨 Customization

### Modify Styles
Edit `/src/dashboard/static/dashboard.css`:
- Change color scheme in `:root` variables
- Adjust layout in `.dashboard-grid`
- Customize card appearance

### Extend Functionality
Edit `/src/dashboard/biocode_dashboard.py`:
- Add new API endpoints
- Create custom metrics
- Implement new visualizations

## 🐛 Troubleshooting

### Port Already in Use
```bash
python launch_dashboard.py --port 5001
```

### Permission Denied
```bash
sudo python launch_dashboard.py  # Not recommended
# Better: use a port > 1024
```

### Missing Dependencies
```bash
pip install flask flask-socketio flask-cors
```

### Agent Not Starting
- Check project path exists
- Verify sandbox permissions
- Check system resources

## 🚨 Security Notes

1. **Default Binding**: Dashboard binds to localhost only by default
2. **Sandbox Mode**: All agents run in sandbox mode
3. **No Code Execution**: Dashboard cannot modify project files
4. **Rate Limiting**: Consider adding for production use

## 📈 Performance Tips

1. **Limit Active Agents**: Too many agents can slow the system
2. **Use Shorter Lifespans**: For testing, use 60-300 second lifespans
3. **Disable Replication**: Set `can_replicate=false` for controlled testing
4. **Monitor Resources**: Watch CPU/memory usage in Colony Metrics

## 🔮 Future Enhancements

- [ ] Historical data persistence
- [ ] Advanced visualizations (D3.js)
- [ ] Agent communication graph
- [ ] Pattern analysis dashboard
- [ ] Export functionality
- [ ] Multi-project support
- [ ] Authentication system

## 📝 Example Workflow

1. Start dashboard: `python launch_dashboard.py`
2. Launch agent for your project via UI
3. Watch real-time monitoring as agent analyzes code
4. View discovered patterns and metrics
5. Download report when agent completes
6. Analyze colony knowledge growth

Enjoy monitoring your living code colony! 🧬✨