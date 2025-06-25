#!/usr/bin/env python3
"""
Controlled BioCode Analysis of Ear Segmentation AI with Dashboard
NO REPLICATION - Only analysis and monitoring
"""
import sys
import os
import time
import threading
import webbrowser

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agent.biocode_agent import BioCodeAgent, AgentDNA
from dashboard.biocode_dashboard import run_dashboard

def controlled_analysis():
    """Run controlled analysis without replication"""
    
    print("""
    🧬 BioCode Agent - Controlled Ear Segmentation Analysis
    =====================================================
    
    ⚠️  NO REPLICATION - Agents will NOT reproduce
    ✅ Safe analysis with web dashboard monitoring
    """)
    
    project_path = "/home/umit/CLAUDE_PROJECT/Ear-segmentation-ai"
    
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
    print("🌐 Opening dashboard at http://localhost:5000")
    webbrowser.open('http://localhost:5000')
    
    print(f"\n📂 Analyzing: {project_path}")
    print("\n🔬 Creating NON-REPLICATING agents...\n")
    
    # Create agents with NO REPLICATION
    agents = []
    
    # Agent 1: Pattern Analyzer
    agent1 = BioCodeAgent(
        project_path,
        AgentDNA(
            agent_id="pattern_analyzer",
            scan_frequency=5.0,
            lifespan=180,  # 3 minutes
            can_replicate=False,  # NO REPLICATION
            can_evolve=True,
            can_communicate=True
        ),
        sandbox_mode=True
    )
    agents.append(agent1)
    print("✅ Pattern Analyzer - Discovers code patterns")
    
    # Agent 2: Quality Inspector  
    agent2 = BioCodeAgent(
        project_path,
        AgentDNA(
            agent_id="quality_inspector",
            scan_frequency=7.0,
            lifespan=180,
            can_replicate=False,  # NO REPLICATION
            can_evolve=True,
            aggressive_monitoring=True
        ),
        sandbox_mode=True
    )
    agents.append(agent2)
    print("✅ Quality Inspector - Analyzes code quality")
    
    # Start agents
    print("\n🚀 Starting agents...")
    for agent in agents:
        agent.start()
        time.sleep(0.5)
    
    print("\n" + "="*60)
    print("📊 Dashboard: http://localhost:5000")
    print("⏱️  Analysis duration: 3 minutes")
    print("🚫 Replication: DISABLED")
    print("="*60)
    
    # Monitor for 3 minutes
    start_time = time.time()
    try:
        while time.time() - start_time < 180:
            remaining = 180 - (time.time() - start_time)
            
            # Status every 30 seconds
            if int(remaining) % 30 == 0 and remaining < 180:
                status = BioCodeAgent.get_colony_status()
                print(f"\n📊 Status: {status['active_agents']} agents, {status['total_knowledge_entries']} knowledge entries")
            
            print(f"\r⏱️  {int(remaining)}s remaining  ", end='', flush=True)
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Stopped by user")
    
    # Analyze results
    print("\n\n📊 Analysis Results:")
    
    total_files = set()
    patterns = {}
    
    for agent in agents:
        total_files.update(agent.memory.files_scanned)
        for p, c in agent.memory.learned_patterns.items():
            patterns[p] = patterns.get(p, 0) + c
    
    print(f"\n   Files analyzed: {len(total_files)}")
    print(f"   Patterns found: {len(patterns)}")
    
    if patterns:
        print("\n   Top patterns:")
        for pattern, count in sorted(patterns.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   - {pattern}: {count}")
    
    # Cleanup
    print("\n🧹 Cleaning up...")
    for agent in agents:
        if agent.alive:
            agent.apoptosis("analysis_complete")
    
    print("\n✅ Analysis complete!")
    print("📊 Dashboard still running - press Ctrl+C to stop")
    
    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    controlled_analysis()