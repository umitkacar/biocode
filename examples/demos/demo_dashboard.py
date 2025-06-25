#!/usr/bin/env python3
"""
BioCode Dashboard Demo - Shows all features
"""
import sys
import os
import time
import threading

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agent.biocode_agent import BioCodeAgent, AgentDNA
from pathlib import Path

def create_demo_colony():
    """Create a demo colony with multiple specialized agents"""
    
    print("""
    🧬 BioCode Agent Colony Demo
    ============================
    
    This demo will:
    1. Launch the web dashboard
    2. Create 3 specialized agents
    3. Let them analyze the BioCode project itself
    4. Show real-time monitoring
    
    Press Ctrl+C to stop
    """)
    
    # Target project (analyze BioCode itself!)
    project_path = os.path.dirname(os.path.abspath(__file__))
    
    print(f"\n📂 Target project: {project_path}")
    print("\n🔬 Creating specialized agents...\n")
    
    agents = []
    
    # Agent 1: Fast Scanner
    dna1 = AgentDNA(
        agent_id="scanner_alpha",
        scan_frequency=3.0,  # Fast scanning
        lifespan=180,  # 3 minutes
        can_replicate=False,
        can_evolve=True,
        error_tolerance=20
    )
    agent1 = BioCodeAgent(project_path, dna1, sandbox_mode=True)
    agents.append(("Scanner Alpha", agent1))
    print("✅ Scanner Alpha - Fast file discovery")
    
    # Agent 2: Pattern Hunter
    dna2 = AgentDNA(
        agent_id="pattern_beta",
        scan_frequency=5.0,
        lifespan=180,
        can_replicate=False,
        can_evolve=True,
        aggressive_monitoring=True
    )
    agent2 = BioCodeAgent(project_path, dna2, sandbox_mode=True)
    agents.append(("Pattern Beta", agent2))
    print("✅ Pattern Beta - Deep pattern analysis")
    
    # Agent 3: Colony Coordinator
    dna3 = AgentDNA(
        agent_id="coordinator_gamma",
        scan_frequency=10.0,
        lifespan=180,
        can_replicate=True,  # Can create one child
        can_evolve=True,
        can_communicate=True,
        mutation_rate=0.2
    )
    agent3 = BioCodeAgent(project_path, dna3, sandbox_mode=True)
    agents.append(("Coordinator Gamma", agent3))
    print("✅ Coordinator Gamma - Colony intelligence")
    
    # Start all agents
    print("\n🚀 Starting colony...\n")
    for name, agent in agents:
        agent.start()
        print(f"   {name} is alive!")
        time.sleep(0.5)
    
    print("\n📊 Dashboard should be running at: http://localhost:5000")
    print("\n⏳ Demo will run for 3 minutes...")
    print("\n💡 Watch the dashboard to see:")
    print("   - Real-time agent health and energy")
    print("   - Pattern discovery progress")
    print("   - Colony knowledge sharing")
    print("   - Automatic report generation")
    
    # Monitor for demo duration
    start_time = time.time()
    duration = 180  # 3 minutes
    
    try:
        while time.time() - start_time < duration:
            remaining = duration - (time.time() - start_time)
            print(f"\r⏱️  Time remaining: {int(remaining)}s  ", end='', flush=True)
            time.sleep(1)
            
            # Show periodic status
            if int(remaining) % 30 == 0 and remaining < duration:
                print(f"\n\n📈 Colony Status at {duration - int(remaining)}s:")
                colony_status = BioCodeAgent.get_colony_status()
                print(f"   Active agents: {colony_status['active_agents']}")
                print(f"   Knowledge entries: {colony_status['total_knowledge_entries']}")
                print(f"   Living agents: {len([a for _, a in agents if a.alive])}\n")
                
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    
    # Cleanup
    print("\n\n🧹 Cleaning up...")
    for name, agent in agents:
        if agent.alive:
            agent.apoptosis("demo_complete")
            print(f"   {name} terminated gracefully")
    
    print("\n✅ Demo completed!")
    print("\n📄 Check reports in: ~/.biocode_agent/reports/")
    print("📊 Dashboard will remain active - press Ctrl+C to stop")

def main():
    # First, ensure dashboard is running
    print("Starting dashboard in background...")
    
    # Import and start dashboard in a thread
    from dashboard.biocode_dashboard import run_dashboard
    
    dashboard_thread = threading.Thread(
        target=run_dashboard,
        kwargs={'host': '127.0.0.1', 'port': 5000, 'debug': False}
    )
    dashboard_thread.daemon = True
    dashboard_thread.start()
    
    # Wait for dashboard to start
    time.sleep(3)
    
    # Open browser
    import webbrowser
    webbrowser.open('http://localhost:5000')
    
    # Run demo
    create_demo_colony()
    
    # Keep dashboard running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard stopped. Goodbye!")

if __name__ == '__main__':
    main()