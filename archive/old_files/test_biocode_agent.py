#!/usr/bin/env python3
"""
BioCode Agent Test - Ear Segmentation AI Project Analysis
"""
import sys
import os
import time
import json
from pathlib import Path

# Add BioCode to path dynamically
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from src.agent.biocode_agent import BioCodeAgent, AgentDNA

def test_biocode_agent(target_project=None):
    """Test BioCode Agent on a project"""
    
    # Use environment variable or default path
    if target_project is None:
        target_project = os.environ.get('BIOCODE_TEST_PROJECT', 
                                      str(current_dir.parent / 'Ear-segmentation-ai'))
    
    print("🧬 BioCode Agent Test Starting...")
    print(f"📂 Target Project: {target_project}")
    print("-" * 60)
    
    # Create custom DNA for this test
    test_dna = AgentDNA(
        agent_id="ear_seg_analyzer",
        scan_frequency=2.0,  # Fast scanning for demo
        error_tolerance=20,  # Higher tolerance
        lifespan=300,  # 5 minutes lifetime
        aggressive_monitoring=True,  # Detailed monitoring
        can_replicate=False,  # No replication for this test
        can_evolve=True,
        can_communicate=True
    )
    
    # Create agent
    print("\n🔬 Creating BioCode Agent...")
    agent = BioCodeAgent(
        project_path=target_project,
        dna=test_dna,
        sandbox_mode=True  # Safe mode
    )
    
    print(f"✅ Agent {agent.dna.agent_id} created")
    print(f"📍 Sandbox location: {agent.project_path}")
    
    # Start agent
    print("\n🚀 Starting agent lifecycle...")
    agent.start()
    
    # Monitor for a while
    monitoring_duration = 30  # 30 seconds of monitoring
    print(f"\n⏱️  Monitoring for {monitoring_duration} seconds...")
    
    start_time = time.time()
    while time.time() - start_time < monitoring_duration:
        # Check agent health
        if int(time.time() - start_time) % 10 == 0:
            print(f"\n📊 Status at {int(time.time() - start_time)}s:")
            print(f"   Health: {agent.health:.1f}%")
            print(f"   Energy: {agent.energy:.1f}%")
            print(f"   Files scanned: {len(agent.memory.files_scanned)}")
            print(f"   Errors detected: {len(agent.memory.errors_detected)}")
            
        time.sleep(1)
        
        # Check if agent died
        if not agent.alive:
            print("\n⚠️  Agent died prematurely!")
            break
    
    # Get colony status
    print("\n🌐 Colony Status:")
    colony_status = BioCodeAgent.get_colony_status()
    print(json.dumps(colony_status, indent=2))
    
    # Force agent to create final report before death
    print("\n📝 Generating final report...")
    
    # Manually trigger report creation
    report_data = {
        'agent_id': agent.dna.agent_id,
        'project_analyzed': target_project,
        'analysis_duration': time.time() - agent.birth_time,
        'files_discovered': list(agent.memory.files_scanned),
        'total_files_scanned': len(agent.memory.files_scanned),
        'errors_found': agent.memory.errors_detected,
        'performance_metrics': agent.memory.performance_metrics,
        'learned_patterns': dict(agent.memory.learned_patterns),
        'file_statistics': {},
        'project_insights': {}
    }
    
    # Analyze file types
    file_types = {}
    for file_path in agent.memory.files_scanned:
        ext = Path(file_path).suffix
        file_types[ext] = file_types.get(ext, 0) + 1
    report_data['file_statistics']['file_types'] = file_types
    
    # Calculate project complexity
    total_functions = 0
    total_classes = 0
    total_lines = 0
    
    for file_path, snapshot in agent._file_snapshots.items():
        total_functions += snapshot.get('functions', 0)
        total_classes += snapshot.get('classes', 0)
        total_lines += snapshot.get('lines', 0)
    
    report_data['project_insights'] = {
        'total_functions': total_functions,
        'total_classes': total_classes,
        'total_lines': total_lines,
        'average_file_size': total_lines / len(agent._file_snapshots) if agent._file_snapshots else 0
    }
    
    # Save custom report
    report_path = Path.home() / '.biocode_agent' / 'reports' / f'ear_segmentation_analysis_{agent.dna.agent_id}.json'
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w') as f:
        json.dump(report_data, f, indent=2, default=str)
    
    print(f"✅ Report saved to: {report_path}")
    
    # Print summary
    print("\n📋 Analysis Summary:")
    print(f"   Total files scanned: {len(agent.memory.files_scanned)}")
    print(f"   Python files: {file_types.get('.py', 0)}")
    print(f"   Total functions: {total_functions}")
    print(f"   Total classes: {total_classes}")
    print(f"   Total lines of code: {total_lines}")
    print(f"   Errors detected: {len(agent.memory.errors_detected)}")
    
    if agent.memory.learned_patterns:
        print("\n🧠 Learned Patterns:")
        for pattern, count in agent.memory.learned_patterns.items():
            print(f"   {pattern}: {count}")
    
    # Trigger apoptosis
    print("\n💀 Initiating programmed cell death...")
    agent.apoptosis("test_complete")
    
    print("\n✅ Test completed successfully!")
    print(f"📄 Full report available at: {report_path}")
    
    # Display report content
    print("\n📊 Full Report Content:")
    print("-" * 60)
    with open(report_path, 'r') as f:
        print(f.read())
    
    return report_path

if __name__ == "__main__":
    try:
        # Get project path from command line or environment
        project_path = sys.argv[1] if len(sys.argv) > 1 else None
        report_path = test_biocode_agent(project_path)
        print(f"\n🎉 BioCode Agent test completed! Check report at: {report_path}")
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()