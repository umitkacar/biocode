#!/usr/bin/env python3
"""
Demo: BioCode Terminal with Ear Segmentation Analysis
"""
import sys
import os
import time
import threading
import webbrowser

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agent.biocode_agent import BioCodeAgent, AgentDNA
from dashboard.biocode_dashboard import run_dashboard

print("""
🧬 BioCode Terminal Demo - Ear Segmentation AI
=============================================

This demo shows:
1. Real-time terminal output from agents
2. Pattern discovery logs
3. File scanning progress
""")

# Start dashboard
print("\n🌐 Starting dashboard...")
dashboard_thread = threading.Thread(
    target=run_dashboard,
    kwargs={'host': '127.0.0.1', 'port': 5000, 'debug': False}
)
dashboard_thread.daemon = True
dashboard_thread.start()

time.sleep(3)

# Open browser
print("🌐 Opening dashboard...")
webbrowser.open('http://localhost:5000')

print("\n📂 Target: Ear Segmentation AI")
print("🔬 Creating analysis agents...\n")

# Create agents
project_path = "/home/umit/CLAUDE_PROJECT/Ear-segmentation-ai"

agent1 = BioCodeAgent(
    project_path,
    AgentDNA(
        agent_id="scanner_alpha",
        scan_frequency=4.0,
        lifespan=180,
        can_replicate=False,
        can_evolve=True
    ),
    sandbox_mode=True
)

agent2 = BioCodeAgent(
    project_path,
    AgentDNA(
        agent_id="analyzer_beta",
        scan_frequency=6.0,
        lifespan=180,
        can_replicate=False,
        can_evolve=True,
        aggressive_monitoring=True
    ),
    sandbox_mode=True
)

print("✅ Scanner Alpha - Fast file discovery")
print("✅ Analyzer Beta - Deep analysis")

print("\n🚀 Starting agents...")
agent1.start()
agent2.start()

print("\n" + "="*60)
print("📊 Dashboard: http://localhost:5000")
print("🖥️  Terminal: Click 'Terminal' button in dashboard")
print("="*60)

print("\n💡 The terminal will show:")
print("   • File scanning progress")
print("   • Pattern discoveries")
print("   • Agent lifecycle events")
print("   • Real-time activity")

print("\n⏱️  Running for 3 minutes...")
print("   Press Ctrl+C to stop\n")

try:
    time.sleep(180)  # 3 minutes
except KeyboardInterrupt:
    print("\n\n⚠️  Stopped by user")

# Cleanup
print("\n🧹 Cleaning up...")
if agent1.alive:
    agent1.apoptosis("demo_complete")
if agent2.alive:
    agent2.apoptosis("demo_complete")

print("\n✅ Demo complete!")
print("📊 Dashboard still running at http://localhost:5000")
print("🖥️  Check the Terminal for complete activity log")
print("\nPress Ctrl+C to stop dashboard")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n👋 Goodbye!")