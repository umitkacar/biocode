#!/usr/bin/env python3
"""
Demo: Multi-Colony Ecosystem
"""
import sys
import os
import time
import threading
import tempfile
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agent.biocode_agent import BioCodeAgent, AgentDNA
from ecosystem.multi_colony import get_ecosystem

print("""
🌍 BioCode Multi-Colony Ecosystem Demo
=====================================

This demo shows:
1. Multiple colonies in different projects
2. Agent migration between colonies
3. Gene transfer and knowledge sharing
4. Ecosystem health monitoring
""")

# Create test projects
projects = {}
for i in range(3):
    project_dir = tempfile.mkdtemp(prefix=f"colony_{i}_")
    projects[f"colony_{i}"] = project_dir
    
    # Add some code files
    for j in range(5):
        code = f'''
# Project {i} - Module {j}
import os

class Worker{i}_{j}:
    def __init__(self):
        self.id = "{i}_{j}"
        
    def process(self, data):
        return data * {i + 1}
        
def main():
    worker = Worker{i}_{j}()
    result = worker.process(10)
    print(f"Result: {{result}}")
    
if __name__ == "__main__":
    main()
'''
        (Path(project_dir) / f"module_{j}.py").write_text(code)
    
    print(f"📁 Created colony_{i} at {project_dir}")

# Get ecosystem coordinator
ecosystem = get_ecosystem("demo_ecosystem")
print("\n🌐 Ecosystem coordinator started")

# Create agents for each colony
agents = []

print("\n🧬 Creating agents...")
for i, (colony_name, project_path) in enumerate(projects.items()):
    # Create diverse agents
    for j in range(2):  # 2 agents per colony
        dna = AgentDNA(
            agent_id=f"{colony_name}_agent_{j}",
            generation=0,
            scan_frequency=3.0 + i,
            lifespan=600,
            can_replicate=True if j == 0 else False,
            can_evolve=True,
            can_communicate=True,
            mutation_rate=0.1 + (i * 0.05),
            adaptation_speed=0.5 + (j * 0.1)
        )
        
        agent = BioCodeAgent(project_path, dna=dna, sandbox_mode=False)
        agents.append(agent)
        
        print(f"✅ Created {dna.agent_id}")

# Establish alliances
ecosystem.establish_alliance("colony_0", "colony_1")
ecosystem.establish_alliance("colony_1", "colony_2")
print("\n🤝 Established colony alliances")

# Start all agents
print("\n🚀 Starting all agents...")
for agent in agents:
    agent.start()

# Monitor ecosystem
print("\n⏱️  Monitoring ecosystem for 2 minutes...")
print("=" * 60)

start_time = time.time()
last_report = 0

while time.time() - start_time < 120:  # 2 minutes
    current_time = time.time() - start_time
    
    # Report every 20 seconds
    if current_time - last_report > 20:
        print(f"\n📊 Ecosystem Status at {int(current_time)}s:")
        
        # Get ecosystem health
        health = ecosystem.analyze_ecosystem_health()
        
        print(f"   Status: {health['status']}")
        print(f"   Total colonies: {health['total_colonies']}")
        print(f"   Total population: {health['total_population']}")
        print(f"   Average health: {health['average_health']:.1f}%")
        print(f"   Max generation: {health['max_generation']}")
        print(f"   Genetic diversity: {health['genetic_diversity']:.2f}")
        print(f"   Recent migrations: {health['recent_migrations']}")
        print(f"   Gene transfers: {health['total_gene_transfers']}")
        
        if health['specializations']:
            print(f"   Specializations: {', '.join(health['specializations'])}")
            
        # Show migration flow
        if health['migration_flow']:
            print("\n   Migration Flow:")
            for source, targets in health['migration_flow'].items():
                for target, count in targets.items():
                    print(f"      {source} → {target}: {count} agents")
                    
        last_report = current_time
        
    time.sleep(5)

# Final ecosystem analysis
print("\n" + "=" * 60)
print("📊 Final Ecosystem Analysis:")
print("=" * 60)

final_health = ecosystem.analyze_ecosystem_health()
print(f"""
Status: {final_health['status']}
Total Colonies: {final_health['total_colonies']}
Total Population: {final_health['total_population']}
Average Health: {final_health['average_health']:.1f}%
Maximum Generation Reached: {final_health['max_generation']}
Genetic Diversity Score: {final_health['genetic_diversity']:.2f}
Total Migrations: {len(ecosystem.migration_history)}
Total Gene Transfers: {len(ecosystem.gene_transfers)}
""")

# Knowledge distribution
if final_health['knowledge_types']:
    print("\nKnowledge Distribution:")
    for k_type, count in final_health['knowledge_types'].items():
        print(f"   {k_type}: {count} entries")

# Stop all agents
print("\n🛑 Stopping all agents...")
for agent in agents:
    if agent.alive:
        agent.stop()

# Stop ecosystem
ecosystem.stop_coordinator()

print("\n✅ Demo complete!")
print("\n🧹 Cleanup commands:")
for colony, path in projects.items():
    print(f"   rm -rf {path}")

# Optional: Actually clean up
# import shutil
# for path in projects.values():
#     shutil.rmtree(path)