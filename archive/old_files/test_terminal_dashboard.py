#!/usr/bin/env python3
"""
Test BioCode Dashboard with Live Terminal - Ear Segmentation AI
"""
import sys
import os
import time
import threading
import webbrowser

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agent.biocode_agent import BioCodeAgent, AgentDNA
from dashboard.biocode_dashboard import run_dashboard

def test_with_terminal():
    """Test dashboard with live terminal output"""
    
    print("""
    🧬 BioCode Dashboard - Live Terminal Test
    ========================================
    
    Testing enhanced dashboard with real-time terminal
    """)
    
    # Start dashboard
    print("\n🌐 Starting dashboard with terminal...")
    dashboard_thread = threading.Thread(
        target=run_dashboard,
        kwargs={'host': '127.0.0.1', 'port': 5000, 'debug': False}
    )
    dashboard_thread.daemon = True
    dashboard_thread.start()
    
    time.sleep(3)
    
    # Open browser
    print("🌐 Opening dashboard at http://localhost:5000")
    webbrowser.open('http://localhost:5000')
    
    print("\n⏳ Waiting 5 seconds before starting agents...")
    time.sleep(5)
    
    # Target project
    project_path = "/home/umit/CLAUDE_PROJECT/Ear-segmentation-ai"
    
    print(f"\n📂 Target: {project_path}")
    print("🔬 Creating verbose agents...\n")
    
    # Create agents that will generate lots of terminal output
    agents = []
    
    # Agent 1: Verbose Scanner
    agent1 = BioCodeAgent(
        project_path,
        AgentDNA(
            agent_id="verbose_scanner",
            scan_frequency=3.0,  # Fast scanning for more logs
            lifespan=120,  # 2 minutes
            can_replicate=False,
            can_evolve=True,
            aggressive_monitoring=True  # More activity
        ),
        sandbox_mode=True
    )
    agents.append(agent1)
    print("✅ Verbose Scanner - Will generate lots of logs")
    
    # Agent 2: Pattern Detective
    agent2 = BioCodeAgent(
        project_path,
        AgentDNA(
            agent_id="pattern_detective",
            scan_frequency=5.0,
            lifespan=120,
            can_replicate=False,
            can_evolve=True,
            can_communicate=True
        ),
        sandbox_mode=True
    )
    agents.append(agent2)
    print("✅ Pattern Detective - Will report patterns found")
    
    # Start agents
    print("\n🚀 Starting agents...")
    for agent in agents:
        agent.start()
        time.sleep(1)
    
    print("\n" + "="*60)
    print("📊 Dashboard: http://localhost:5000")
    print("\n💡 Watch the Live Terminal section!")
    print("   • Green text = normal activity")
    print("   • Yellow text = warnings")
    print("   • Cyan text = success/patterns found")
    print("   • Red text = errors")
    print("   • Gray text = debug info")
    print("="*60)
    
    print("\n⏱️  Running for 2 minutes...")
    print("   (Terminal will show real-time agent activity)")
    
    # Monitor
    start_time = time.time()
    try:
        while time.time() - start_time < 120:
            remaining = 120 - (time.time() - start_time)
            
            # Status every 30 seconds
            if int(remaining) % 30 == 0 and remaining < 120:
                colony_status = BioCodeAgent.get_colony_status()
                terminal_logs = BioCodeAgent.get_terminal_logs(5)  # Last 5 logs
                
                print(f"\n\n📊 Status Update:")
                print(f"   Agents: {colony_status['active_agents']}")
                print(f"   Knowledge: {colony_status['total_knowledge_entries']}")
                print(f"\n   Recent terminal activity:")
                for log in terminal_logs:
                    print(f"   [{log['agent_id']}] {log['message']}")
            
            print(f"\r⏱️  {int(remaining)}s remaining", end='', flush=True)
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Stopped by user")
    
    # Cleanup
    print("\n\n🧹 Cleaning up...")
    for agent in agents:
        if agent.alive:
            agent.apoptosis("test_complete")
    
    print("\n✅ Test complete!")
    print("📊 Dashboard and terminal still running")
    print("   Check the Live Terminal for the complete activity log")
    print("\n   Press Ctrl+C to stop dashboard")
    
    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    test_with_terminal()