#!/usr/bin/env python3
"""
BioCode Agent Colony Test - Advanced Pattern Learning & Coordination
"""
import sys
import os
import time
import json
import random
from pathlib import Path
from datetime import datetime
import threading

sys.path.append('/home/umit/CLAUDE_PROJECT/Code-Snippet')

from src.agent.biocode_agent import BioCodeAgent, AgentDNA
from src.evolution.horizontal_gene_transfer import GeneticElement, HGTNetwork

import logging
logger = logging.getLogger(__name__)

class EnhancedBioCodeAgent(BioCodeAgent):
    """Enhanced agent with pattern learning and colony coordination"""
    
    def __init__(self, project_path: str, dna: AgentDNA = None, role: str = "general"):
        super().__init__(project_path, dna, sandbox_mode=True)
        self.role = role  # specialist role in colony
        self.patterns_discovered = []
        self.code_quality_metrics = {}
        
    def _analyze_code_patterns(self):
        """Analyze code for patterns and quality metrics"""
        for file_path, snapshot in self._file_snapshots.items():
            if file_path.endswith('.py'):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Pattern detection
                    patterns = {
                        'test_files': 'test_' in os.path.basename(file_path),
                        'has_docstrings': '"""' in content or "'''" in content,
                        'uses_type_hints': '->' in content or ': ' in content,
                        'has_error_handling': 'try:' in content,
                        'uses_logging': 'logging' in content or 'logger' in content,
                        'is_async': 'async def' in content,
                        'uses_dataclasses': '@dataclass' in content,
                        'has_main_guard': 'if __name__ == "__main__"' in content,
                        'uses_pathlib': 'from pathlib import Path' in content,
                        'file_size_category': 'large' if snapshot['lines'] > 200 else 'medium' if snapshot['lines'] > 50 else 'small'
                    }
                    
                    # Update learned patterns
                    for pattern, found in patterns.items():
                        if found:
                            self.memory.learned_patterns[pattern] += 1
                            
                    # Code quality metrics
                    if self.role == "quality_inspector":
                        quality = {
                            'complexity': snapshot['functions'] / max(1, snapshot['lines']) * 100,
                            'class_to_function_ratio': snapshot['classes'] / max(1, snapshot['functions']),
                            'avg_function_size': snapshot['lines'] / max(1, snapshot['functions']),
                            'has_tests': 'test_' in file_path or '/tests/' in file_path
                        }
                        self.code_quality_metrics[file_path] = quality
                        
                except Exception as e:
                    logger.debug(f"Pattern analysis failed for {file_path}: {e}")
                    
    def share_specialized_knowledge(self):
        """Share role-specific discoveries with colony"""
        knowledge_packet = {
            'agent_id': self.dna.agent_id,
            'role': self.role,
            'timestamp': datetime.now().isoformat(),
            'discoveries': {
                'patterns': dict(self.memory.learned_patterns),
                'quality_metrics': self.code_quality_metrics if self.role == "quality_inspector" else {},
                'file_categories': self._categorize_files() if self.role == "architect" else {},
                'security_issues': self._find_security_issues() if self.role == "security_guard" else []
            }
        }
        
        # Broadcast to colony
        self._colony_knowledge.append(knowledge_packet)
        
        # Direct message to specialized peers
        for agent_id, agent in self._active_agents.items():
            if agent_id != self.dna.agent_id and isinstance(agent, EnhancedBioCodeAgent):
                if agent.role == self.role:  # Same role agents share more
                    agent.inbox.append({
                        'type': 'specialized_knowledge',
                        'from': self.dna.agent_id,
                        'role': self.role,
                        'priority': 'high',
                        'data': knowledge_packet
                    })
                    
    def _categorize_files(self):
        """Architect role: categorize project structure"""
        categories = {
            'core': [],
            'api': [],
            'tests': [],
            'utils': [],
            'config': [],
            'documentation': []
        }
        
        for file_path in self.memory.files_scanned:
            if '/core/' in file_path or 'core' in os.path.basename(file_path):
                categories['core'].append(file_path)
            elif '/api/' in file_path or 'api' in os.path.basename(file_path):
                categories['api'].append(file_path)
            elif '/test' in file_path or 'test_' in os.path.basename(file_path):
                categories['tests'].append(file_path)
            elif '/utils/' in file_path or 'utils' in os.path.basename(file_path):
                categories['utils'].append(file_path)
            elif 'config' in file_path or 'settings' in file_path:
                categories['config'].append(file_path)
                
        return categories
        
    def _find_security_issues(self):
        """Security guard role: look for potential security issues"""
        issues = []
        
        for file_path in self.memory.files_scanned:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Security patterns to check
                security_checks = {
                    'hardcoded_secrets': ['password =', 'api_key =', 'secret =', 'token ='],
                    'unsafe_eval': ['eval(', 'exec('],
                    'sql_injection_risk': ['f"SELECT', "f'SELECT", '% ('],
                    'path_traversal': ['../', '..\\'],
                    'debug_mode': ['DEBUG = True', 'debug=True'],
                }
                
                for issue_type, patterns in security_checks.items():
                    for pattern in patterns:
                        if pattern in content:
                            issues.append({
                                'file': file_path,
                                'issue': issue_type,
                                'pattern': pattern,
                                'severity': 'high' if issue_type in ['hardcoded_secrets', 'sql_injection_risk'] else 'medium'
                            })
                            
            except Exception as e:
                pass
                
        return issues
        
    def _evolution_loop(self):
        """Enhanced evolution with pattern learning"""
        while not self._stop_event.is_set() and self.alive:
            try:
                if self.dna.can_evolve:
                    # Original evolution
                    self._learn_from_errors()
                    self._adapt_behavior()
                    
                    # Enhanced pattern analysis
                    self._analyze_code_patterns()
                    
                    # Role-specific knowledge sharing
                    self.share_specialized_knowledge()
                    
                    # Colony learning
                    self._learn_from_colony()
                    
                time.sleep(15)  # Faster evolution cycle
                
            except Exception as e:
                logger.error(f"Evolution error: {e}")
                
    def _learn_from_colony(self):
        """Learn from other agents' discoveries"""
        colony_patterns = {}
        
        # Aggregate colony knowledge
        for knowledge in self._colony_knowledge:
            if knowledge.get('discoveries'):
                patterns = knowledge['discoveries'].get('patterns', {})
                for pattern, count in patterns.items():
                    colony_patterns[pattern] = colony_patterns.get(pattern, 0) + count
                    
        # Update own knowledge with colony wisdom
        for pattern, total_count in colony_patterns.items():
            if total_count > 5:  # Pattern confirmed by multiple agents
                self.memory.learned_patterns[f"colony_{pattern}"] = total_count


def create_specialized_colony(project_path: str, colony_size: int = 4):
    """Create a colony of specialized agents"""
    
    roles = ["architect", "quality_inspector", "security_guard", "performance_analyst"]
    agents = []
    
    print("🧬 Creating BioCode Agent Colony...")
    print(f"📍 Target: {project_path}")
    print(f"🔬 Colony size: {colony_size} agents")
    print("-" * 60)
    
    # Create specialized agents
    for i in range(colony_size):
        role = roles[i % len(roles)]
        
        # Customize DNA for role
        dna = AgentDNA(
            agent_id=f"{role}_{i}",
            generation=0,
            scan_frequency=3.0 + i,  # Stagger scanning
            error_tolerance=15,
            lifespan=600,  # 10 minutes
            can_replicate=True,
            can_evolve=True,
            can_communicate=True,
            aggressive_monitoring=role == "security_guard"
        )
        
        # Role-specific traits
        if role == "architect":
            dna.mutation_rate = 0.05  # Stable
        elif role == "quality_inspector":
            dna.adaptation_speed = 0.8  # Quick learner
        elif role == "security_guard":
            dna.scan_frequency = 2.0  # Frequent scans
        elif role == "performance_analyst":
            dna.error_tolerance = 5  # Sensitive to issues
            
        agent = EnhancedBioCodeAgent(project_path, dna, role)
        agents.append(agent)
        
        print(f"✅ Created {role} agent: {agent.dna.agent_id}")
        
    return agents


def run_colony_simulation(agents, duration=120):
    """Run colony simulation with coordination"""
    
    print("\n🚀 Starting colony simulation...")
    
    # Start all agents
    for agent in agents:
        agent.start()
        time.sleep(0.5)  # Stagger starts
        
    print(f"\n⏱️  Running for {duration} seconds...")
    start_time = time.time()
    
    # Create HGT network for knowledge transfer
    hgt_network = HGTNetwork()
    
    # Monitor colony
    while time.time() - start_time < duration:
        elapsed = int(time.time() - start_time)
        
        if elapsed % 20 == 0 and elapsed > 0:
            print(f"\n📊 Colony Status at {elapsed}s:")
            
            # Colony statistics
            total_files = set()
            total_patterns = {}
            total_errors = []
            
            for agent in agents:
                if agent.alive:
                    total_files.update(agent.memory.files_scanned)
                    
                    # Aggregate patterns
                    for pattern, count in agent.memory.learned_patterns.items():
                        total_patterns[pattern] = total_patterns.get(pattern, 0) + count
                        
                    total_errors.extend(agent.memory.errors_detected)
                    
                    print(f"   {agent.role} ({agent.dna.agent_id}):")
                    print(f"     Health: {agent.health:.1f}%, Energy: {agent.energy:.1f}%")
                    print(f"     Files: {len(agent.memory.files_scanned)}, Patterns: {len(agent.memory.learned_patterns)}")
                    
            print(f"\n   Colony Totals:")
            print(f"     Unique files scanned: {len(total_files)}")
            print(f"     Patterns discovered: {len(total_patterns)}")
            print(f"     Total errors: {len(total_errors)}")
            
            # Simulate knowledge transfer
            if elapsed % 40 == 0 and elapsed > 0:
                print("\n🧬 Simulating horizontal knowledge transfer...")
                
                # Create knowledge genes
                for pattern, count in total_patterns.items():
                    if count > 2:  # Significant pattern
                        gene = GeneticElement(
                            element_id=f"pattern_{pattern}",
                            element_type="trait",
                            source_species="biocode_agent",
                            code=json.dumps({pattern: count}),
                            metadata={"transferable": True},
                            fitness_impact=0.1
                        )
                        hgt_network.register_gene(gene)
                        
                # Transfer between agents
                events = hgt_network.simulate_hgt_event(agents)
                print(f"   Knowledge transfer events: {events}")
                
        # Check for agent reproduction
        if elapsed % 30 == 0 and elapsed > 0:
            for agent in agents[:]:  # Copy list to allow modification
                if agent.alive and agent.health > 80 and agent.energy > 70:
                    child = agent.mitosis()
                    if child:
                        agents.append(child)
                        print(f"\n🔬 Agent {agent.dna.agent_id} reproduced! Child: {child.dna.agent_id}")
                        
        time.sleep(1)
        
    return agents


def generate_colony_report(agents, project_path):
    """Generate comprehensive colony analysis report"""
    
    print("\n📝 Generating colony report...")
    
    # Aggregate all discoveries
    report = {
        'project': project_path,
        'analysis_date': datetime.now().isoformat(),
        'colony_size': len(agents),
        'alive_agents': sum(1 for a in agents if a.alive),
        'total_generations': max(a.dna.generation for a in agents),
        'collective_discoveries': {
            'total_files_scanned': len(set().union(*[a.memory.files_scanned for a in agents])),
            'patterns_discovered': {},
            'code_quality_insights': {},
            'security_findings': [],
            'architectural_analysis': {},
            'performance_insights': {}
        },
        'agent_reports': []
    }
    
    # Collect from each agent
    all_patterns = {}
    all_quality_metrics = {}
    all_security_issues = []
    
    for agent in agents:
        # Agent summary
        agent_report = {
            'id': agent.dna.agent_id,
            'role': agent.role,
            'generation': agent.dna.generation,
            'alive': agent.alive,
            'health': agent.health,
            'files_scanned': len(agent.memory.files_scanned),
            'patterns_found': len(agent.memory.learned_patterns),
            'offspring_count': len(agent.memory.replications)
        }
        report['agent_reports'].append(agent_report)
        
        # Aggregate patterns
        for pattern, count in agent.memory.learned_patterns.items():
            all_patterns[pattern] = all_patterns.get(pattern, 0) + count
            
        # Role-specific data
        if agent.role == "quality_inspector":
            all_quality_metrics.update(agent.code_quality_metrics)
        elif agent.role == "security_guard":
            security_issues = agent._find_security_issues()
            all_security_issues.extend(security_issues)
            
    # Analyze patterns
    report['collective_discoveries']['patterns_discovered'] = {
        'common_patterns': {k: v for k, v in sorted(all_patterns.items(), key=lambda x: x[1], reverse=True)[:10]},
        'test_coverage': all_patterns.get('test_files', 0),
        'documentation_quality': all_patterns.get('has_docstrings', 0),
        'modern_python_usage': {
            'type_hints': all_patterns.get('uses_type_hints', 0),
            'dataclasses': all_patterns.get('uses_dataclasses', 0),
            'pathlib': all_patterns.get('uses_pathlib', 0),
            'async': all_patterns.get('is_async', 0)
        }
    }
    
    # Quality insights
    if all_quality_metrics:
        avg_complexity = sum(m.get('complexity', 0) for m in all_quality_metrics.values()) / len(all_quality_metrics)
        avg_function_size = sum(m.get('avg_function_size', 0) for m in all_quality_metrics.values()) / len(all_quality_metrics)
        
        report['collective_discoveries']['code_quality_insights'] = {
            'average_complexity': round(avg_complexity, 2),
            'average_function_size': round(avg_function_size, 2),
            'files_with_tests': sum(1 for m in all_quality_metrics.values() if m.get('has_tests', False))
        }
        
    # Security findings
    report['collective_discoveries']['security_findings'] = all_security_issues
    
    # Colony knowledge
    colony_knowledge = BioCodeAgent._colony_knowledge
    report['colony_knowledge_entries'] = len(colony_knowledge)
    
    # Save report
    report_path = Path.home() / '.biocode_agent' / 'reports' / f'colony_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
        
    print(f"✅ Colony report saved to: {report_path}")
    
    return report, report_path


def main():
    """Run enhanced colony test"""
    
    project_path = "/home/umit/CLAUDE_PROJECT/Ear-segmentation-ai"
    
    print("🧬 BioCode Agent Colony Test - Advanced Analysis")
    print("=" * 60)
    
    # Create specialized colony
    agents = create_specialized_colony(project_path, colony_size=4)
    
    # Run colony simulation
    agents = run_colony_simulation(agents, duration=60)  # 1 minute
    
    # Generate report
    report, report_path = generate_colony_report(agents, project_path)
    
    # Display summary
    print("\n" + "=" * 60)
    print("📊 COLONY ANALYSIS SUMMARY")
    print("=" * 60)
    
    print(f"\n🧬 Colony Statistics:")
    print(f"   Initial agents: 4")
    print(f"   Final agents: {len(agents)}")
    print(f"   Alive agents: {report['alive_agents']}")
    print(f"   Max generation: {report['total_generations']}")
    
    print(f"\n📁 Code Analysis:")
    print(f"   Total files scanned: {report['collective_discoveries']['total_files_scanned']}")
    print(f"   Test files found: {report['collective_discoveries']['patterns_discovered']['test_coverage']}")
    print(f"   Files with docstrings: {report['collective_discoveries']['patterns_discovered']['documentation_quality']}")
    
    print(f"\n🔍 Top Patterns Discovered:")
    for pattern, count in list(report['collective_discoveries']['patterns_discovered']['common_patterns'].items())[:5]:
        print(f"   {pattern}: {count}")
        
    if report['collective_discoveries']['security_findings']:
        print(f"\n⚠️  Security Issues Found: {len(report['collective_discoveries']['security_findings'])}")
        for issue in report['collective_discoveries']['security_findings'][:3]:
            print(f"   - {issue['issue']} in {os.path.basename(issue['file'])}")
            
    print(f"\n🧠 Colony Intelligence:")
    print(f"   Knowledge entries shared: {report['colony_knowledge_entries']}")
    print(f"   Patterns learned collectively: {len(report['collective_discoveries']['patterns_discovered']['common_patterns'])}")
    
    # Cleanup
    print("\n💀 Triggering colony apoptosis...")
    for agent in agents:
        if agent.alive:
            agent.apoptosis("simulation_complete")
            
    print(f"\n✅ Colony test completed!")
    print(f"📄 Full report: {report_path}")
    
    # Display part of the report
    print("\n📋 Report Preview:")
    print(json.dumps(report['collective_discoveries'], indent=2)[:1000] + "...")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Colony test failed: {e}")
        import traceback
        traceback.print_exc()