"""
Evolution Lab Colony - Living Code Analysis System
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
import asyncio
import json
from typing import Any, Optional
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field

# BioCode ECS imports
from biocode.ecs import World, Entity, System
from biocode.ecs.components import (
    HealthComponent, EnergyComponent, CommunicationComponent
)
from biocode.factories import CellFactory
from biocode.mixins import ObservableMixin, NetworkableMixin
from biocode.aspects import LoggingAspect, PerformanceAspect, AspectWeaver

# Evolution Lab analyzers
from .analyzers import (
    CodeAnalyzer, AIModelAnalyzer,
    SecurityAnalyzer, PerformanceAnalyzer,
    TestCoverageAnalyzer, InnovationAnalyzer,
    DependencyGraphAnalyzer
    # HealthAnalyzer, DocumentationAnalyzer
)


@dataclass
class ProjectSnapshot:
    """Snapshot of project analysis at a point in time"""
    timestamp: datetime = field(default_factory=datetime.now)
    project_path: str = ""
    health_score: float = 0.0
    metrics: dict[str, Any] = field(default_factory=dict)
    issues: list[dict[str, Any]] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'project_path': self.project_path,
            'health_score': self.health_score,
            'metrics': self.metrics,
            'issues': self.issues,
            'suggestions': self.suggestions,
        }


class AnalyzerCell(Entity, ObservableMixin, NetworkableMixin):
    """A cell that runs a specific analyzer"""
    
    def __init__(self, analyzer_class, project_path: str, cell_id: Optional[str] = None):
        Entity.__init__(self, cell_id)
        ObservableMixin.__init__(self)
        NetworkableMixin.__init__(self)
        
        self.analyzer = analyzer_class(project_path)
        self.add_component(HealthComponent(current=100.0))
        self.add_component(EnergyComponent(current=100.0))
        self.add_component(CommunicationComponent())
        self.add_tag("analyzer_cell")
        self.add_tag(analyzer_class.__name__.lower())
        
    async def analyze(self) -> dict[str, Any]:
        """Run the analyzer and return results"""
        try:
            # Consume energy for analysis
            energy = self.get_component(EnergyComponent)
            energy.current -= 10.0
            
            # Run analysis
            result = await asyncio.to_thread(self.analyzer.analyze)
            
            # Update health based on issues found
            health = self.get_component(HealthComponent)
            issue_count = len(result.issues)
            health.current = max(0, health.current - issue_count * 2)
            
            # Notify observers
            # self.notify_observers('analysis_complete', result=result)
            
            # Return the full AnalysisResult object, not just to_dict()
            return result
            
        except Exception as e:
            # Damage health on error
            health = self.get_component(HealthComponent)
            health.current = max(0, health.current - 20)
            
            # self.notify_observers('analysis_error', error=str(e))
            return {'error': str(e)}


class ColonyAnalysisSystem(System):
    """System that coordinates analyzer cells"""
    
    def __init__(self, priority: int = 1):
        super().__init__(priority)
        self.analysis_results = {}
        self.project_snapshots = []
        
    def required_components(self):
        return [HealthComponent, EnergyComponent]
        
    def process(self, delta_time: float):
        """Process all analyzer cells"""
        for entity in self.get_entities():
            if 'analyzer_cell' in entity.tags:
                # Regenerate energy over time
                energy = entity.get_component(EnergyComponent)
                energy.current = min(100.0, energy.current + delta_time * 5)
                
                # Heal slowly over time
                health = entity.get_component(HealthComponent)
                health.current = min(100.0, health.current + delta_time * 2)
                
    async def run_analysis(self, cells: list[AnalyzerCell]) -> ProjectSnapshot:
        """Run analysis using all cells and aggregate results"""
        tasks = []
        for cell in cells:
            tasks.append(cell.analyze())
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate results
        snapshot = ProjectSnapshot()
        all_metrics = {}
        all_issues = []
        all_suggestions = []
        
        for i, result in enumerate(results):
            if isinstance(result, dict) and 'error' in result:
                # Skip error results
                continue
            elif hasattr(result, 'metrics'):  # It's an AnalysisResult object
                analyzer_name = cells[i].analyzer.__class__.__name__
                all_metrics[analyzer_name] = result.metrics
                all_issues.extend(result.issues)
                all_suggestions.extend(result.suggestions)
                
        # Calculate health score
        total_cells = len(cells)
        healthy_cells = sum(1 for cell in cells if cell.get_component(HealthComponent).current > 50)
        health_score = (healthy_cells / total_cells) * 100 if total_cells > 0 else 0
        
        snapshot.metrics = all_metrics
        snapshot.issues = all_issues
        snapshot.suggestions = list(set(all_suggestions))  # Remove duplicates
        snapshot.health_score = health_score
        
        self.project_snapshots.append(snapshot)
        return snapshot


class EvolutionLabColony:
    """Main colony that manages the analysis of external projects"""
    
    def __init__(self):
        self.world = World()
        self.cell_factory = CellFactory(self.world)
        self.colony_system = ColonyAnalysisSystem()
        self.world.add_system(self.colony_system)
        
        # Apply aspects for monitoring
        self.weaver = AspectWeaver()
        self.weaver.add_aspect(LoggingAspect())
        self.weaver.add_aspect(PerformanceAspect(alert_threshold_ms=1000))
        
        self.analyzer_cells = []
        self.is_running = False
        
    def spawn_analyzer_cells(self, project_path: str):
        """Spawn analyzer cells for a project"""
        analyzers = [
            CodeAnalyzer,
            AIModelAnalyzer,
            SecurityAnalyzer,
            PerformanceAnalyzer,
            TestCoverageAnalyzer,
            InnovationAnalyzer,
            DependencyGraphAnalyzer,
            # Add more analyzers as implemented
            # DependencyAnalyzer,
            # HealthAnalyzer,
            # DocumentationAnalyzer
        ]
        
        for analyzer_class in analyzers:
            cell = AnalyzerCell(analyzer_class, project_path)
            self.world.add_entity(cell)
            self.analyzer_cells.append(cell)
            
            # Apply aspects to cell
            self.weaver.weave(cell)
            
    async def analyze_project(self, project_path: str) -> ProjectSnapshot:
        """Analyze a project and return snapshot"""
        # Clear previous cells
        for cell in self.analyzer_cells:
            self.world.remove_entity(cell.id)
        self.analyzer_cells.clear()
        
        # Spawn new cells
        self.spawn_analyzer_cells(project_path)
        
        # Run analysis
        snapshot = await self.colony_system.run_analysis(self.analyzer_cells)
        snapshot.project_path = project_path
        
        return snapshot
        
    async def start_monitoring(self, project_path: str, interval: float = 60.0):
        """Start continuous monitoring of a project"""
        self.is_running = True
        
        while self.is_running:
            try:
                snapshot = await self.analyze_project(project_path)
                print(f"Analysis complete - Health: {snapshot.health_score:.1f}%")
                
                # Update world
                self.world.update(interval)
                
                # Wait before next analysis
                await asyncio.sleep(interval)
                
            except Exception as e:
                print(f"Error during monitoring: {e}")
                await asyncio.sleep(10)  # Wait before retry
                
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.is_running = False
        
    def get_latest_snapshot(self) -> Optional[ProjectSnapshot]:
        """Get the most recent analysis snapshot"""
        if self.colony_system.project_snapshots:
            return self.colony_system.project_snapshots[-1]
        return None
        
    def get_metrics_history(self) -> list[dict[str, Any]]:
        """Get history of all snapshots"""
        return [snapshot.to_dict() for snapshot in self.colony_system.project_snapshots]
        
    def export_analysis(self, output_path: str):
        """Export analysis results to file"""
        latest = self.get_latest_snapshot()
        if latest:
            with open(output_path, 'w') as f:
                json.dump(latest.to_dict(), f, indent=2)
                
    def get_colony_health(self) -> dict[str, Any]:
        """Get overall colony health status"""
        total_cells = len(self.analyzer_cells)
        if total_cells == 0:
            return {'status': 'empty', 'cells': 0}
            
        healthy = sum(1 for cell in self.analyzer_cells 
                     if cell.get_component(HealthComponent).current > 70)
        damaged = sum(1 for cell in self.analyzer_cells 
                     if 30 < cell.get_component(HealthComponent).current <= 70)
        critical = sum(1 for cell in self.analyzer_cells 
                      if cell.get_component(HealthComponent).current <= 30)
                      
        avg_energy = sum(cell.get_component(EnergyComponent).current 
                        for cell in self.analyzer_cells) / total_cells
                        
        return {
            'status': 'healthy' if healthy > total_cells * 0.7 else 'degraded',
            'total_cells': total_cells,
            'healthy_cells': healthy,
            'damaged_cells': damaged,
            'critical_cells': critical,
            'average_energy': avg_energy,
            'analyzers_active': [cell.analyzer.__class__.__name__ for cell in self.analyzer_cells],
        }


# Example usage function
async def analyze_ear_segmentation_project():
    """Example: Analyze the Ear-segmentation-ai project"""
    colony = EvolutionLabColony()
    
    # Path to the ear segmentation project
    project_path = "/home/umit/CLAUDE_PROJECT/Ear-segmentation-ai"
    
    print("🧬 Spawning Evolution Lab Colony...")
    print(f"🔬 Target: {project_path}")
    print("-" * 50)
    
    # Run single analysis
    snapshot = await colony.analyze_project(project_path)
    
    print(f"\n📊 Analysis Complete!")
    print(f"Health Score: {snapshot.health_score:.1f}%")
    print(f"Issues Found: {len(snapshot.issues)}")
    print(f"Suggestions: {len(snapshot.suggestions)}")
    
    # Print some metrics
    if 'CodeAnalyzer' in snapshot.metrics:
        code_metrics = snapshot.metrics['CodeAnalyzer']
        print(f"\n📝 Code Metrics:")
        print(f"  - Primary Language: {code_metrics.get('primary_language', 'unknown')}")
        print(f"  - Total Files: {code_metrics.get('total_files', 0)}")
        print(f"  - Total Lines: {code_metrics.get('total_lines', 0)}")
        
    if 'AIModelAnalyzer' in snapshot.metrics:
        ai_metrics = snapshot.metrics['AIModelAnalyzer']
        print(f"\n🤖 AI/ML Metrics:")
        print(f"  - Model Files: {ai_metrics['model_files']['count']}")
        print(f"  - Frameworks: {', '.join(k for k, v in ai_metrics['frameworks'].items() if v)}")
        
    # Export results
    colony.export_analysis("ear_segmentation_analysis.json")
    print(f"\n💾 Analysis exported to ear_segmentation_analysis.json")
    
    # Get colony health
    health = colony.get_colony_health()
    print(f"\n🏥 Colony Health: {health['status']}")
    print(f"   Active Analyzers: {', '.join(health['analyzers_active'])}")