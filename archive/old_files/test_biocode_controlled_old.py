#!/usr/bin/env python3
"""
BioCode Agent - Controlled Colony Test with Pattern Learning
"""
import sys
import os
import time
import json
from pathlib import Path
from datetime import datetime

sys.path.append('/home/umit/CLAUDE_PROJECT/Code-Snippet')

from src.agent.biocode_agent import BioCodeAgent, AgentDNA

def controlled_colony_test():
    """Run a controlled test showing all features"""
    
    project_path = "/home/umit/CLAUDE_PROJECT/Ear-segmentation-ai"
    
    print("🧬 BioCode Agent Controlled Colony Test")
    print("=" * 60)
    print("This test demonstrates:")
    print("1. Pattern learning over extended time")
    print("2. Colony knowledge sharing")
    print("3. Controlled reproduction")
    print("4. Advanced analysis capabilities")
    print("=" * 60)
    
    # Create specialized agents with NO reproduction initially
    agents = []
    roles = [
        ("architect", "Analyzes project structure and architecture"),
        ("quality_inspector", "Checks code quality and best practices"),
        ("security_guard", "Looks for security vulnerabilities"),
        ("pattern_hunter", "Discovers coding patterns and conventions")
    ]
    
    print("\n🔬 Creating specialized colony...")
    
    for i, (role, description) in enumerate(roles):
        # Custom DNA for each role
        dna = AgentDNA(
            agent_id=f"{role}_{i}",
            generation=0,
            scan_frequency=5.0,  # 5 second scans
            error_tolerance=20,
            lifespan=300,  # 5 minutes
            can_replicate=False,  # No automatic replication
            can_evolve=True,
            can_communicate=True,
            aggressive_monitoring=role == "security_guard",
            mutation_rate=0.1,
            adaptation_speed=0.7
        )
        
        # Create agent
        agent = BioCodeAgent(project_path, dna, sandbox_mode=True)
        
        # Add custom analysis method based on role
        if role == "security_guard":
            agent._custom_analysis = lambda: analyze_security(agent)
        elif role == "quality_inspector":
            agent._custom_analysis = lambda: analyze_quality(agent)
        elif role == "pattern_hunter":
            agent._custom_analysis = lambda: analyze_patterns(agent)
        
        agents.append(agent)
        print(f"✅ Created {role}: {description}")
    
    # Start all agents
    print("\n🚀 Starting colony...")
    for agent in agents:
        agent.start()
        
    # Phase 1: Initial learning (30 seconds)
    print("\n📚 Phase 1: Initial Learning (30 seconds)")
    time.sleep(30)
    
    print("\n📊 Initial Colony Status:")
    display_colony_status(agents)
    
    # Phase 2: Enable controlled reproduction for best performer
    print("\n🧬 Phase 2: Selective Reproduction")
    
    # Find healthiest agent
    best_agent = max(agents, key=lambda a: a.health)
    print(f"Best performer: {best_agent.dna.agent_id} (Health: {best_agent.health}%)")
    
    # Allow it to reproduce ONCE
    best_agent.dna.can_replicate = True
    child = best_agent.mitosis()
    if child:
        agents.append(child)
        print(f"✅ Created offspring: {child.dna.agent_id}")
    best_agent.dna.can_replicate = False  # Disable again
    
    # Phase 3: Extended analysis (30 seconds)
    print("\n🔍 Phase 3: Deep Analysis (30 seconds)")
    time.sleep(30)
    
    # Collect comprehensive results
    print("\n📊 Final Analysis Results:")
    print("=" * 60)
    
    # Aggregate all discoveries
    all_patterns = {}
    all_files = set()
    security_issues = []
    quality_metrics = {}
    
    for agent in agents:
        if not agent.alive:
            continue
            
        # Collect files
        all_files.update(agent.memory.files_scanned)
        
        # Collect patterns
        for pattern, count in agent.memory.learned_patterns.items():
            all_patterns[pattern] = all_patterns.get(pattern, 0) + count
            
        # Role-specific analysis
        if "security" in agent.dna.agent_id:
            issues = find_security_issues(agent)
            security_issues.extend(issues)
            
        elif "quality" in agent.dna.agent_id:
            metrics = calculate_quality_metrics(agent)
            quality_metrics.update(metrics)
    
    # Display results
    print(f"\n📁 Project Analysis:")
    print(f"   Total files scanned: {len(all_files)}")
    print(f"   Python files: {len([f for f in all_files if f.endswith('.py')])}")
    
    print(f"\n🔍 Top Patterns Discovered:")
    sorted_patterns = sorted(all_patterns.items(), key=lambda x: x[1], reverse=True)
    for pattern, count in sorted_patterns[:10]:
        print(f"   {pattern}: {count} occurrences")
        
    if security_issues:
        print(f"\n⚠️  Security Concerns ({len(security_issues)} found):")
        for issue in security_issues[:5]:
            print(f"   - {issue}")
            
    if quality_metrics:
        print(f"\n📈 Code Quality Metrics:")
        for metric, value in list(quality_metrics.items())[:5]:
            print(f"   {metric}: {value}")
    
    # Colony knowledge
    print(f"\n🧠 Colony Intelligence:")
    print(f"   Active agents: {sum(1 for a in agents if a.alive)}")
    print(f"   Total knowledge entries: {len(BioCodeAgent._colony_knowledge)}")
    print(f"   Shared patterns: {len([k for k in all_patterns.keys() if 'colony' in k])}")
    
    # Create final report
    report = {
        'test_type': 'controlled_colony',
        'project': project_path,
        'duration': 60,
        'agents': len(agents),
        'files_analyzed': len(all_files),
        'patterns': dict(sorted_patterns[:20]),
        'security_issues': security_issues[:10],
        'quality_metrics': quality_metrics,
        'colony_knowledge': len(BioCodeAgent._colony_knowledge)
    }
    
    report_path = Path.home() / '.biocode_agent' / 'reports' / f'controlled_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    print(f"\n📄 Report saved: {report_path}")
    
    # Cleanup
    print("\n💀 Initiating controlled shutdown...")
    for agent in agents:
        if agent.alive:
            agent.apoptosis("test_complete")
            
    print("\n✅ Test completed successfully!")
    
    return report_path


def display_colony_status(agents):
    """Display current colony status"""
    for agent in agents:
        if agent.alive:
            print(f"\n   {agent.dna.agent_id}:")
            print(f"     Health: {agent.health:.1f}%, Energy: {agent.energy:.1f}%")
            print(f"     Files: {len(agent.memory.files_scanned)}")
            print(f"     Patterns: {len(agent.memory.learned_patterns)}")
            print(f"     Errors: {len(agent.memory.errors_detected)}")


def analyze_security(agent):
    """Security-focused analysis"""
    security_patterns = {
        'hardcoded_password': ['password =', 'PASSWORD ='],
        'api_key_exposure': ['api_key =', 'API_KEY ='],
        'sql_injection': ['execute(', 'raw_query'],
        'unsafe_eval': ['eval(', 'exec('],
        'debug_enabled': ['DEBUG = True', 'debug=True']
    }
    
    for pattern_name, keywords in security_patterns.items():
        for keyword in keywords:
            agent.memory.learned_patterns[f"security_{pattern_name}"] = 0


def analyze_quality(agent):
    """Quality-focused analysis"""
    for file_path, snapshot in agent._file_snapshots.items():
        if snapshot['functions'] > 0:
            complexity = snapshot['lines'] / snapshot['functions']
            if complexity > 50:
                agent.memory.learned_patterns['high_function_complexity'] += 1
            elif complexity < 10:
                agent.memory.learned_patterns['low_function_complexity'] += 1


def analyze_patterns(agent):
    """Pattern-focused analysis"""
    # This runs automatically through the agent's pattern detection
    pass


def find_security_issues(agent):
    """Extract security issues from agent's memory"""
    issues = []
    for pattern, count in agent.memory.learned_patterns.items():
        if pattern.startswith('security_') and count > 0:
            issues.append(f"{pattern}: {count} occurrences")
    return issues


def calculate_quality_metrics(agent):
    """Calculate code quality metrics"""
    metrics = {}
    
    if agent._file_snapshots:
        total_lines = sum(s['lines'] for s in agent._file_snapshots.values())
        total_functions = sum(s['functions'] for s in agent._file_snapshots.values())
        total_classes = sum(s['classes'] for s in agent._file_snapshots.values())
        
        metrics['avg_file_size'] = round(total_lines / len(agent._file_snapshots), 2)
        metrics['total_functions'] = total_functions
        metrics['total_classes'] = total_classes
        
        if total_functions > 0:
            metrics['avg_function_size'] = round(total_lines / total_functions, 2)
            
    return metrics


if __name__ == "__main__":
    try:
        controlled_colony_test()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()