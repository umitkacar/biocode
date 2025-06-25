#!/usr/bin/env python3
"""
Test BioCode Agent on Ear Segmentation AI project with Dashboard
"""
import sys
import os
import time
import threading
import webbrowser

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agent.biocode_agent import BioCodeAgent, AgentDNA
from dashboard.biocode_dashboard import run_dashboard

def test_ear_segmentation():
    """Test BioCode on Ear Segmentation AI project"""
    
    print("""
    🧬 BioCode Agent - Ear Segmentation AI Analysis
    ==============================================
    
    This will:
    1. Start the web dashboard
    2. Create specialized agents for the project
    3. Analyze code patterns and quality
    4. Display real-time monitoring
    """)
    
    # Target project
    project_path = "/home/umit/CLAUDE_PROJECT/Ear-segmentation-ai"
    
    if not os.path.exists(project_path):
        print(f"❌ Project not found: {project_path}")
        return
        
    print(f"\n📂 Target project: {project_path}")
    
    # Start dashboard in background
    print("\n🌐 Starting dashboard...")
    dashboard_thread = threading.Thread(
        target=run_dashboard,
        kwargs={'host': '127.0.0.1', 'port': 5000, 'debug': False}
    )
    dashboard_thread.daemon = True
    dashboard_thread.start()
    
    # Wait for dashboard
    time.sleep(3)
    
    # Open browser
    print("🌐 Opening dashboard in browser...")
    webbrowser.open('http://localhost:5000')
    
    print("\n🔬 Creating specialized agents...\n")
    
    agents = []
    
    # Agent 1: Code Quality Analyzer
    dna1 = AgentDNA(
        agent_id="quality_analyzer",
        scan_frequency=5.0,
        lifespan=300,  # 5 minutes
        error_tolerance=25,
        can_replicate=False,
        can_evolve=True,
        can_communicate=True,
        adaptation_speed=0.8
    )
    agent1 = BioCodeAgent(project_path, dna1, sandbox_mode=True)
    agents.append(("Quality Analyzer", agent1))
    print("✅ Quality Analyzer - Checks code quality metrics")
    
    # Agent 2: Test Coverage Inspector
    dna2 = AgentDNA(
        agent_id="test_inspector",
        scan_frequency=8.0,
        lifespan=300,
        can_replicate=False,
        can_evolve=True,
        aggressive_monitoring=True,
        mutation_rate=0.1
    )
    agent2 = BioCodeAgent(project_path, dna2, sandbox_mode=True)
    agents.append(("Test Inspector", agent2))
    print("✅ Test Inspector - Analyzes test coverage and patterns")
    
    # Agent 3: Architecture Explorer
    dna3 = AgentDNA(
        agent_id="architecture_explorer",
        scan_frequency=10.0,
        lifespan=300,
        can_replicate=True,  # Can create one child
        can_evolve=True,
        can_communicate=True,
        replication_threshold=0.8
    )
    agent3 = BioCodeAgent(project_path, dna3, sandbox_mode=True)
    agents.append(("Architecture Explorer", agent3))
    print("✅ Architecture Explorer - Maps project structure")
    
    # Agent 4: Performance Profiler
    dna4 = AgentDNA(
        agent_id="performance_profiler",
        scan_frequency=15.0,
        lifespan=300,
        can_replicate=False,
        can_evolve=True,
        error_tolerance=10  # Sensitive to performance issues
    )
    agent4 = BioCodeAgent(project_path, dna4, sandbox_mode=True)
    agents.append(("Performance Profiler", agent4))
    print("✅ Performance Profiler - Looks for optimization opportunities")
    
    # Start all agents
    print("\n🚀 Starting colony...")
    for name, agent in agents:
        agent.start()
        print(f"   {name} is alive!")
        time.sleep(0.5)
    
    print("\n" + "="*60)
    print("📊 Dashboard is running at: http://localhost:5000")
    print("="*60)
    
    print("\n💡 What to watch in the dashboard:")
    print("   • Colony Metrics: See agent count and files analyzed")
    print("   • Active Agents: Monitor health and energy levels")
    print("   • Colony Activity: Watch real-time graph")
    print("   • Use controls to launch more agents or kill existing ones")
    
    print("\n⏳ Analysis will run for 5 minutes...")
    print("   (Press Ctrl+C to stop early)")
    
    # Monitor for duration
    start_time = time.time()
    duration = 300  # 5 minutes
    
    try:
        while time.time() - start_time < duration:
            remaining = duration - (time.time() - start_time)
            
            # Show status every minute
            if int(remaining) % 60 == 0 and remaining < duration:
                elapsed = duration - int(remaining)
                print(f"\n\n📈 Status at {elapsed//60} minutes:")
                
                colony_status = BioCodeAgent.get_colony_status()
                print(f"   Active agents: {colony_status['active_agents']}")
                print(f"   Knowledge entries: {colony_status['total_knowledge_entries']}")
                
                # Count living agents
                alive_count = sum(1 for _, agent in agents if agent.alive)
                print(f"   Original agents alive: {alive_count}/{len(agents)}")
                
                # Show some learned patterns
                if colony_status['total_knowledge_entries'] > 10:
                    print("\n   📚 Sample knowledge entries:")
                    knowledge = list(BioCodeAgent._colony_knowledge)[-5:]
                    for entry in knowledge:
                        if isinstance(entry, dict) and 'type' in entry:
                            print(f"      - {entry.get('type', 'unknown')}: {entry.get('agent_id', 'unknown')}")
            
            # Update every second
            print(f"\r⏱️  Time remaining: {int(remaining)}s  ", end='', flush=True)
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted by user")
    
    # Analysis complete
    print("\n\n🔍 Analysis Summary:")
    
    # Collect results
    total_files = set()
    total_patterns = {}
    
    for name, agent in agents:
        if agent.memory:
            total_files.update(agent.memory.files_scanned)
            for pattern, count in agent.memory.learned_patterns.items():
                total_patterns[pattern] = total_patterns.get(pattern, 0) + count
    
    print(f"\n📊 Final Statistics:")
    print(f"   Total unique files analyzed: {len(total_files)}")
    print(f"   Unique patterns discovered: {len(total_patterns)}")
    
    if total_patterns:
        print(f"\n🔝 Top 10 Patterns:")
        sorted_patterns = sorted(total_patterns.items(), key=lambda x: x[1], reverse=True)
        for i, (pattern, count) in enumerate(sorted_patterns[:10], 1):
            print(f"   {i}. {pattern}: {count}")
    
    # Cleanup
    print("\n\n🧹 Cleaning up agents...")
    for name, agent in agents:
        if agent.alive:
            agent.apoptosis("analysis_complete")
            print(f"   {name} terminated gracefully")
    
    print("\n✅ Analysis completed!")
    print(f"\n📄 Reports saved in: ~/.biocode_agent/reports/")
    print("📊 Dashboard will remain active - view reports and analytics")
    print("\n   Press Ctrl+C to stop the dashboard")
    
    # Keep dashboard running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard stopped. Goodbye!")

if __name__ == "__main__":
    test_ear_segmentation()