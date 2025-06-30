#!/usr/bin/env python3
"""
🧬 BioCode Unified Demo - All Features in One Place
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.

This demo showcases ALL BioCode features:
- Evolution Lab with 9 analyzers
- Pareto Health Optimization
- SwarmSearchCV for ML
- Code Smell Detection & Auto-fix
- Dependency Graphs
- Code Embeddings & Similarity
- ECS Architecture
- Living Colony Dashboard
"""
import asyncio
import sys
import tempfile
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track, Progress
from rich.prompt import Prompt, Confirm
from rich.layout import Layout
from rich.live import Live
from rich import print as rprint
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import all BioCode features
from src.evolution_lab.colony import EvolutionLabColony
from src.evolution_lab.analyzers.code_smell_analyzer import CodeSmellAnalyzer
from src.evolution_lab.analyzers.dependency_graph_analyzer import DependencyGraphAnalyzer
from src.evolution_lab.analyzers.code_embedding_analyzer import CodeEmbeddingAnalyzer
from src.evolution_lab.optimizers.pareto_health import ParetoHealthOptimizer
from src.evolution_lab.optimizers.swarm_search import SwarmSearchCV
from src.evolution_lab.fixers.smell_fixer import SmellFixer
from src.biocode.ecs import World
from src.biocode.ecs.systems import LifeSystem, EnergySystem
from src.biocode.factories import CellFactory

# For ML demo
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC


class UnifiedBioCodeDemo:
    """Unified demo showcasing all BioCode features"""
    
    def __init__(self):
        self.console = Console()
        self.project_path = None
        self.results = {}
        
    def show_welcome(self):
        """Display welcome screen"""
        welcome_text = """
[bold cyan]🧬 BioCode - Unified Demo[/bold cyan]
        
[yellow]This demo will showcase:[/yellow]
• Evolution Lab Colony with 9 analyzers
• Multi-objective optimization (Pareto)
• Swarm intelligence for ML (PSO)
• Code smell detection & auto-fix
• Dependency graph visualization
• Semantic code search
• ECS living architecture
• Real-time dashboard

[dim]Press Ctrl+C anytime to exit[/dim]
        """
        self.console.print(Panel(welcome_text, title="Welcome", border_style="cyan"))
        
    def select_demo_mode(self):
        """Let user select demo mode"""
        self.console.print("\n[bold]Select Demo Mode:[/bold]")
        self.console.print("1. 🚀 Quick Demo (5 min) - Key features only")
        self.console.print("2. 📊 Full Demo (15 min) - All features")
        self.console.print("3. 🎯 Custom Demo - Choose features")
        self.console.print("4. 🌐 Live Dashboard - Web interface")
        
        choice = Prompt.ask("Enter your choice", choices=["1", "2", "3", "4"], default="1")
        return choice
        
    async def run_evolution_lab_analysis(self, quick=False):
        """Run Evolution Lab analysis"""
        self.console.print("\n[bold cyan]🔬 Evolution Lab Analysis[/bold cyan]")
        
        with Progress() as progress:
            task = progress.add_task("[cyan]Initializing colony...", total=100)
            
            # Create colony
            colony = EvolutionLabColony()
            progress.update(task, advance=20)
            
            # Analyze project
            progress.update(task, description="[cyan]Analyzing project...")
            snapshot = await colony.analyze_project(self.project_path)
            progress.update(task, advance=60)
            
            # Store results
            self.results['colony_snapshot'] = snapshot
            self.results['metrics'] = snapshot.metrics
            progress.update(task, advance=20)
            
        # Display results
        self._display_colony_results(snapshot, quick)
        
    def _display_colony_results(self, snapshot, quick=False):
        """Display colony analysis results"""
        # Summary table
        summary = Table(title="Colony Health Summary")
        summary.add_column("Metric", style="cyan")
        summary.add_column("Score", style="yellow")
        
        summary.add_row("Overall Health", f"{snapshot.health_score}%")
        summary.add_row("Active Analyzers", str(len(snapshot.metrics)))
        summary.add_row("Total Issues", str(sum(len(m.get('issues', [])) for m in snapshot.metrics.values())))
        
        self.console.print(summary)
        
        if not quick:
            # Detailed analyzer results
            self.console.print("\n[bold]Analyzer Results:[/bold]")
            for name, metrics in snapshot.metrics.items():
                if 'score' in metrics or 'health_score' in metrics:
                    score = metrics.get('score', metrics.get('health_score', 'N/A'))
                    self.console.print(f"  • {name}: {score}")
                    
    def run_pareto_optimization(self):
        """Run Pareto health optimization"""
        self.console.print("\n[bold cyan]🎯 Pareto Health Optimization[/bold cyan]")
        
        if 'metrics' not in self.results:
            self.console.print("[yellow]Skipping - no metrics available[/yellow]")
            return
            
        optimizer = ParetoHealthOptimizer()
        
        with self.console.status("[cyan]Running multi-objective optimization..."):
            solutions = optimizer.optimize(
                self.results['metrics'],
                n_gen=20,  # Quick demo
                pop_size=30,
                algorithm="nsga3"
            )
            
        # Display Pareto front
        self.console.print(f"[green]✓[/green] Found {len(solutions)} Pareto-optimal solutions")
        
        # Get balanced solution
        balanced = optimizer.select_balanced_solution()
        if balanced:
            weights_table = Table(title="Optimal Analyzer Weights")
            weights_table.add_column("Analyzer", style="cyan")
            weights_table.add_column("Weight", style="yellow")
            
            for analyzer, weight in balanced.weights.items():
                weights_table.add_row(analyzer, f"{weight:.3f}")
                
            self.console.print(weights_table)
            
        # Save visualization
        optimizer.plot_convergence(save_path="output/visualizations/pareto_demo.png")
        self.console.print("[dim]Pareto front saved to output/visualizations/pareto_demo.png[/dim]")
        
    def run_swarm_search_demo(self):
        """Run SwarmSearchCV demo"""
        self.console.print("\n[bold cyan]🦜 Swarm Search Hyperparameter Optimization[/bold cyan]")
        
        # Generate sample data
        X, y = make_classification(n_samples=200, n_features=10, n_classes=2, random_state=42)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        
        # Define search space
        param_distributions = {
            'C': (0.1, 10.0, 'log'),
            'gamma': (0.001, 1.0, 'log'),
            'kernel': ['rbf', 'linear']
        }
        
        # Create and run SwarmSearchCV
        swarm = SwarmSearchCV(
            SVC(),
            param_distributions,
            n_particles=10,
            n_iterations=10,
            cv=3,
            verbose=0,
            random_state=42
        )
        
        with self.console.status("[cyan]Optimizing SVM hyperparameters with PSO..."):
            swarm.fit(X_train, y_train)
            
        # Display results
        results_table = Table(title="PSO Optimization Results")
        results_table.add_column("Metric", style="cyan")
        results_table.add_column("Value", style="yellow")
        
        results_table.add_row("Best CV Score", f"{swarm.best_score_:.4f}")
        results_table.add_row("Test Score", f"{swarm.score(X_test, y_test):.4f}")
        
        self.console.print(results_table)
        
        # Best parameters
        self.console.print("\n[bold]Best Parameters:[/bold]")
        for param, value in swarm.best_params_.items():
            self.console.print(f"  • {param}: {value}")
            
    def run_code_smell_detection(self):
        """Run code smell detection and auto-fix"""
        self.console.print("\n[bold cyan]🦨 Code Smell Detection & Auto-Fix[/bold cyan]")
        
        analyzer = CodeSmellAnalyzer(self.project_path)
        results = analyzer.analyze()
        
        # Display smell summary
        smell_table = Table(title="Code Smell Summary")
        smell_table.add_column("Type", style="cyan")
        smell_table.add_column("Count", style="yellow")
        
        for smell_type, count in results['smell_distribution'].items():
            if count > 0:
                smell_table.add_row(smell_type.replace('_', ' ').title(), str(count))
                
        self.console.print(smell_table)
        self.console.print(f"\n[bold]Health Score:[/bold] {results['health_score']}%")
        self.console.print(f"[bold]Auto-fixable:[/bold] {results['auto_fixable_count']} issues")
        
        # Auto-fix demo
        if results['auto_fixable_count'] > 0 and Confirm.ask("Run auto-fix demo?", default=False):
            fixer = SmellFixer()
            fixable = [s for s in results['smells'] if s['auto_fixable']][:3]  # Fix up to 3
            
            with self.console.status("[cyan]Applying auto-fixes..."):
                fix_results = fixer.apply_fixes(fixable, dry_run=True)
                
            self.console.print(f"[green]✓[/green] Generated fixes for {len(fix_results)} files")
            
    def run_dependency_graph(self):
        """Run dependency graph analysis"""
        self.console.print("\n[bold cyan]🕸️ Dependency Graph Analysis[/bold cyan]")
        
        analyzer = DependencyGraphAnalyzer(self.project_path)
        results = analyzer.analyze()
        
        # Display graph metrics
        metrics_table = Table(title="Dependency Metrics")
        metrics_table.add_column("Metric", style="cyan")
        metrics_table.add_column("Value", style="yellow")
        
        metrics_table.add_row("Total Modules", str(results.get('total_modules', 0)))
        metrics_table.add_row("Total Dependencies", str(results.get('total_dependencies', 0)))
        metrics_table.add_row("Circular Dependencies", str(len(results.get('circular_dependencies', []))))
        
        self.console.print(metrics_table)
        
        # God classes
        if results.get('god_classes'):
            self.console.print("\n[bold]God Classes Detected:[/bold]")
            for cls in results['god_classes'][:3]:
                self.console.print(f"  • {cls['name']} ({cls['method_count']} methods)")
                
    def run_code_embedding_demo(self):
        """Run code embedding and similarity demo"""
        self.console.print("\n[bold cyan]🧬 Code Embedding & Similarity Search[/bold cyan]")
        
        analyzer = CodeEmbeddingAnalyzer(self.project_path)
        
        with self.console.status("[cyan]Generating code embeddings..."):
            results = analyzer.analyze()
            
        # Display clone statistics
        if results.get('clones'):
            clone_table = Table(title="Clone Detection Results")
            clone_table.add_column("Type", style="cyan")
            clone_table.add_column("Count", style="yellow")
            
            clone_types = {}
            for clone in results['clones']:
                clone_type = clone.get('type', 'Unknown')
                clone_types[clone_type] = clone_types.get(clone_type, 0) + 1
                
            for clone_type, count in clone_types.items():
                clone_table.add_row(clone_type, str(count))
                
            self.console.print(clone_table)
            
        self.console.print(f"[bold]Duplication Ratio:[/bold] {results.get('duplication_ratio', 0):.1%}")
        
    def run_ecs_demo(self):
        """Run ECS architecture demo"""
        self.console.print("\n[bold cyan]🧪 ECS Living Architecture Demo[/bold cyan]")
        
        # Create world
        world = World()
        world.add_system(LifeSystem())
        world.add_system(EnergySystem())
        
        # Create cells
        factory = CellFactory(world)
        cells = []
        
        with self.console.status("[cyan]Creating living cells..."):
            for i in range(5):
                cell = factory.create_stem_cell(position=(i*10, 0, 0))
                cells.append(cell)
                time.sleep(0.2)
                
        self.console.print(f"[green]✓[/green] Created {len(cells)} living cells")
        
        # Simulate
        self.console.print("\n[bold]Simulating cellular life:[/bold]")
        with Progress() as progress:
            task = progress.add_task("[cyan]Life simulation...", total=10)
            
            for tick in range(10):
                world.update(delta_time=0.1)
                progress.update(task, advance=1)
                
                # Show cell states
                if tick % 3 == 0:
                    alive_count = sum(1 for c in cells if c.has_component('HealthComponent'))
                    energy_avg = np.mean([c.get_component('EnergyComponent').current 
                                        for c in cells if c.has_component('EnergyComponent')])
                    progress.console.print(f"  Tick {tick}: {alive_count} alive, avg energy: {energy_avg:.1f}")
                    
    def show_summary(self):
        """Show final summary"""
        summary_text = f"""
[bold green]✨ BioCode Analysis Complete![/bold green]

[bold]Project:[/bold] {self.project_path}
[bold]Features Demonstrated:[/bold]
  ✓ Evolution Lab with {len(self.results.get('metrics', {}))} analyzers
  ✓ Pareto multi-objective optimization
  ✓ Swarm intelligence for ML
  ✓ Code smell detection & auto-fix
  ✓ Dependency graph analysis
  ✓ Code embedding & similarity
  ✓ ECS living architecture

[dim]All features are now integrated into a single, powerful framework![/dim]
        """
        self.console.print(Panel(summary_text, title="Summary", border_style="green"))
        
    async def run_quick_demo(self):
        """Run quick demo (5 min)"""
        # Use sample project or current directory
        self.project_path = str(Path(__file__).parent.parent / "src" / "evolution_lab")
        
        # Run key features
        await self.run_evolution_lab_analysis(quick=True)
        self.run_code_smell_detection()
        self.run_swarm_search_demo()
        self.show_summary()
        
    async def run_full_demo(self):
        """Run full demo (15 min)"""
        # Let user choose project
        default_path = str(Path(__file__).parent.parent / "src")
        self.project_path = Prompt.ask("Enter project path to analyze", default=default_path)
        
        # Run all features
        await self.run_evolution_lab_analysis(quick=False)
        self.run_pareto_optimization()
        self.run_swarm_search_demo()
        self.run_code_smell_detection()
        self.run_dependency_graph()
        self.run_code_embedding_demo()
        self.run_ecs_demo()
        self.show_summary()
        
    async def run_custom_demo(self):
        """Run custom demo with selected features"""
        # Get project path
        default_path = str(Path(__file__).parent.parent / "src")
        self.project_path = Prompt.ask("Enter project path to analyze", default=default_path)
        
        # Feature selection
        features = {
            "1": ("Evolution Lab Analysis", self.run_evolution_lab_analysis),
            "2": ("Pareto Optimization", self.run_pareto_optimization),
            "3": ("Swarm Search ML", self.run_swarm_search_demo),
            "4": ("Code Smell Detection", self.run_code_smell_detection),
            "5": ("Dependency Graphs", self.run_dependency_graph),
            "6": ("Code Embeddings", self.run_code_embedding_demo),
            "7": ("ECS Architecture", self.run_ecs_demo),
        }
        
        self.console.print("\n[bold]Select features to demo:[/bold]")
        for key, (name, _) in features.items():
            self.console.print(f"{key}. {name}")
            
        choices = Prompt.ask("Enter numbers separated by comma", default="1,3,4")
        selected = [c.strip() for c in choices.split(",")]
        
        # Run selected features
        for choice in selected:
            if choice in features:
                name, func = features[choice]
                self.console.print(f"\n[bold cyan]Running: {name}[/bold cyan]")
                if asyncio.iscoroutinefunction(func):
                    await func()
                else:
                    func()
                    
        self.show_summary()
        
    async def run_dashboard_demo(self):
        """Launch live dashboard"""
        self.console.print("\n[bold cyan]🌐 Launching Live Dashboard[/bold cyan]")
        
        # Import dashboard runner
        from scripts.launchers.run_dashboard import main as run_dashboard
        
        self.console.print("[yellow]Starting dashboard server...[/yellow]")
        self.console.print("Open http://localhost:8080 in your browser")
        self.console.print("[dim]Press Ctrl+C to stop[/dim]")
        
        # Run dashboard
        await run_dashboard()
        
    async def run(self):
        """Main demo runner"""
        try:
            self.show_welcome()
            mode = self.select_demo_mode()
            
            if mode == "1":
                await self.run_quick_demo()
            elif mode == "2":
                await self.run_full_demo()
            elif mode == "3":
                await self.run_custom_demo()
            elif mode == "4":
                await self.run_dashboard_demo()
                
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Demo interrupted by user[/yellow]")
        except Exception as e:
            self.console.print(f"\n[red]Error: {e}[/red]")
            raise


async def main():
    """Entry point"""
    demo = UnifiedBioCodeDemo()
    await demo.run()


if __name__ == "__main__":
    asyncio.run(main())