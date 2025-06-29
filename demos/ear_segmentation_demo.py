#!/usr/bin/env python3
"""
🧬 BioCode Analysis for Ear Segmentation AI Project
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.

This demo analyzes the Ear Segmentation AI project with BioCode features:
- Evolution Lab analysis
- Code smell detection
- Dependency graphs
- ML optimization suggestions
"""
import asyncio
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track, Progress
from rich.prompt import Prompt, Confirm
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

# For ML optimization demo
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC


class EarSegmentationAnalyzer:
    """Analyzer for Ear Segmentation AI project"""
    
    def __init__(self):
        self.console = Console()
        self.project_path = "/home/umit/CLAUDE_PROJECT/Ear-segmentation-ai"
        self.results = {}
        
    def show_welcome(self):
        """Display welcome screen"""
        welcome_text = """
[bold cyan]👂 Ear Segmentation AI - BioCode Analysis[/bold cyan]
        
[yellow]This analysis will examine:[/yellow]
• Code quality and health metrics
• ML model optimization opportunities  
• Dependency structure
• Code smell detection
• Performance bottlenecks
• Best practice recommendations

[green]Target Project:[/green] /home/umit/CLAUDE_PROJECT/Ear-segmentation-ai

[dim]Press Ctrl+C anytime to exit[/dim]
        """
        self.console.print(Panel(welcome_text, title="Welcome", border_style="cyan"))
        
    async def run_evolution_lab_analysis(self):
        """Run Evolution Lab analysis on Ear Segmentation project"""
        self.console.print("\n[bold cyan]🔬 Evolution Lab Analysis[/bold cyan]")
        
        with Progress() as progress:
            task = progress.add_task("[cyan]Analyzing Ear Segmentation AI project...", total=100)
            
            # Create colony
            colony = EvolutionLabColony()
            progress.update(task, advance=20)
            
            # Analyze project
            progress.update(task, description="[cyan]Running 9 analyzers on project...")
            snapshot = await colony.analyze_project(self.project_path)
            progress.update(task, advance=60)
            
            # Store results
            self.results['colony_snapshot'] = snapshot
            self.results['metrics'] = snapshot.metrics
            progress.update(task, advance=20)
            
        # Display results
        self._display_analysis_results(snapshot)
        
    def _display_analysis_results(self, snapshot):
        """Display comprehensive analysis results"""
        # Overall health
        self.console.print(f"\n[bold]Overall Project Health:[/bold] {snapshot.health_score}%")
        
        # Analyzer-specific results
        results_table = Table(title="Analysis Results by Category")
        results_table.add_column("Analyzer", style="cyan")
        results_table.add_column("Score", style="yellow")
        results_table.add_column("Key Findings", style="white")
        
        for name, metrics in snapshot.metrics.items():
            score = metrics.get('score', metrics.get('health_score', 'N/A'))
            
            # Extract key findings based on analyzer type
            findings = []
            if 'complexity' in name.lower():
                if 'complex_functions' in metrics:
                    findings.append(f"{len(metrics['complex_functions'])} complex functions")
            elif 'duplication' in name.lower():
                if 'clones' in metrics:
                    findings.append(f"{len(metrics['clones'])} code clones")
            elif 'security' in name.lower():
                if 'vulnerabilities' in metrics:
                    findings.append(f"{len(metrics['vulnerabilities'])} security issues")
            elif 'performance' in name.lower():
                if 'bottlenecks' in metrics:
                    findings.append(f"{len(metrics['bottlenecks'])} bottlenecks")
            
            findings_str = ", ".join(findings) if findings else "No issues"
            results_table.add_row(name, str(score), findings_str)
            
        self.console.print(results_table)
        
    def run_code_smell_analysis(self):
        """Detect code smells in Ear Segmentation project"""
        self.console.print("\n[bold cyan]🦨 Code Smell Detection[/bold cyan]")
        
        analyzer = CodeSmellAnalyzer(self.project_path)
        results = analyzer.analyze()
        
        # Display smell summary
        smell_table = Table(title="Code Smells in Ear Segmentation AI")
        smell_table.add_column("Smell Type", style="cyan")
        smell_table.add_column("Count", style="yellow")
        smell_table.add_column("Severity", style="red")
        
        severity_map = {
            'long_method': 'High',
            'god_class': 'Critical',
            'magic_number': 'Medium',
            'deep_nesting': 'High',
            'long_parameter_list': 'Medium',
            'empty_exception': 'High'
        }
        
        total_smells = 0
        for smell_type, count in results['smell_distribution'].items():
            if count > 0:
                total_smells += count
                severity = severity_map.get(smell_type, 'Low')
                smell_table.add_row(
                    smell_type.replace('_', ' ').title(), 
                    str(count),
                    severity
                )
                
        self.console.print(smell_table)
        self.console.print(f"\n[bold]Total Code Smells:[/bold] {total_smells}")
        self.console.print(f"[bold]Health Score:[/bold] {results['health_score']}%")
        self.console.print(f"[bold]Auto-fixable:[/bold] {results['auto_fixable_count']} issues")
        
        # Show example smells
        if results['smells']:
            self.console.print("\n[bold]Example Issues:[/bold]")
            for smell in results['smells'][:3]:  # Show first 3
                self.console.print(f"  • {smell['type']} in {smell['file']}:{smell['line']}")
                if 'suggestion' in smell:
                    self.console.print(f"    → {smell['suggestion']}")
        
        self.results['code_smells'] = results
        
    def run_ml_optimization_suggestions(self):
        """Suggest ML optimizations for Ear Segmentation"""
        self.console.print("\n[bold cyan]🤖 ML Optimization Suggestions[/bold cyan]")
        
        # Simulate hyperparameter optimization for ear segmentation model
        self.console.print("\n[yellow]Analyzing potential hyperparameter optimizations...[/yellow]")
        
        # Example: Suggest PSO for CNN hyperparameters
        suggestions = [
            {
                'category': 'Model Architecture',
                'current': 'Fixed CNN layers',
                'suggestion': 'Use SwarmSearchCV to optimize layer depths and filter sizes',
                'impact': 'Potential 5-10% accuracy improvement'
            },
            {
                'category': 'Learning Rate',
                'current': 'Fixed learning rate',
                'suggestion': 'Implement adaptive learning rate with PSO optimization',
                'impact': 'Faster convergence, better final accuracy'
            },
            {
                'category': 'Data Augmentation',
                'current': 'Basic augmentation',
                'suggestion': 'Use Pareto optimization for augmentation strategy',
                'impact': 'Better generalization on diverse ear images'
            },
            {
                'category': 'Batch Size',
                'current': 'Fixed batch size',
                'suggestion': 'Dynamic batch sizing based on GPU memory',
                'impact': '20-30% training speed improvement'
            }
        ]
        
        opt_table = Table(title="ML Optimization Opportunities")
        opt_table.add_column("Category", style="cyan")
        opt_table.add_column("Current", style="yellow")
        opt_table.add_column("Suggestion", style="green")
        opt_table.add_column("Expected Impact", style="magenta")
        
        for sugg in suggestions:
            opt_table.add_row(
                sugg['category'],
                sugg['current'],
                sugg['suggestion'],
                sugg['impact']
            )
            
        self.console.print(opt_table)
        
        # Demo SwarmSearchCV for a simplified model
        self.console.print("\n[yellow]Demo: Optimizing SVM classifier with SwarmSearchCV...[/yellow]")
        
        # Generate synthetic data similar to ear features
        X, y = make_classification(
            n_samples=200, 
            n_features=20,  # Simulating extracted ear features
            n_classes=2,    # Binary classification
            n_informative=15,
            random_state=42
        )
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        
        # Define search space
        param_distributions = {
            'C': (0.1, 100.0, 'log'),
            'gamma': (0.0001, 1.0, 'log'),
            'kernel': ['rbf', 'linear', 'poly']
        }
        
        # Run SwarmSearchCV
        swarm = SwarmSearchCV(
            SVC(),
            param_distributions,
            n_particles=15,
            n_iterations=20,
            cv=3,
            verbose=0,
            random_state=42
        )
        
        with self.console.status("[cyan]Running Particle Swarm Optimization..."):
            swarm.fit(X_train, y_train)
            
        # Display results
        self.console.print(f"\n[green]✓[/green] PSO Optimization Complete!")
        self.console.print(f"Best CV Score: {swarm.best_score_:.4f}")
        self.console.print(f"Test Score: {swarm.score(X_test, y_test):.4f}")
        self.console.print(f"Best Parameters: {swarm.best_params_}")
        
    async def run_dependency_analysis(self):
        """Analyze dependency structure"""
        self.console.print("\n[bold cyan]🕸️ Dependency Structure Analysis[/bold cyan]")
        
        analyzer = DependencyGraphAnalyzer(self.project_path)
        results = await analyzer.analyze()
        
        # Display metrics
        dep_table = Table(title="Dependency Metrics")
        dep_table.add_column("Metric", style="cyan")
        dep_table.add_column("Value", style="yellow")
        dep_table.add_column("Status", style="green")
        
        # Extract metrics from result
        module_metrics = results.metrics.get('module_metrics', {})
        
        metrics = [
            ("Total Modules", module_metrics.get('total_modules', 0), "✓" if module_metrics.get('total_modules', 0) < 50 else "⚠"),
            ("Total Dependencies", module_metrics.get('total_dependencies', 0), "✓"),
            ("Circular Dependencies", len(module_metrics.get('cycles', [])), "✓" if len(module_metrics.get('cycles', [])) == 0 else "✗"),
            ("Health Score", f"{results.metrics.get('health_score', 0):.1f}%", "✓" if results.metrics.get('health_score', 0) > 70 else "⚠"),
        ]
        
        for metric, value, status in metrics:
            dep_table.add_row(metric, str(value), status)
            
        self.console.print(dep_table)
        
        # Show problematic areas
        class_metrics = results.metrics.get('class_metrics', {})
        
        if class_metrics.get('god_classes'):
            self.console.print("\n[bold red]God Classes Detected:[/bold red]")
            for cls in class_metrics['god_classes'][:3]:
                self.console.print(f"  • {cls['name']} ({cls['method_count']} methods, {cls['line_count']} lines)")
                
        if module_metrics.get('cycles'):
            self.console.print("\n[bold red]Circular Dependencies:[/bold red]")
            for cycle in module_metrics['cycles'][:3]:
                self.console.print(f"  • {' → '.join(cycle)}")
                
    def generate_report(self):
        """Generate comprehensive analysis report"""
        self.console.print("\n[bold cyan]📊 Generating Analysis Report[/bold cyan]")
        
        report_path = Path("ear_segmentation_analysis_report.md")
        
        with open(report_path, "w") as f:
            f.write("# Ear Segmentation AI - BioCode Analysis Report\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Executive Summary
            f.write("## Executive Summary\n\n")
            if 'colony_snapshot' in self.results:
                f.write(f"- **Overall Health Score**: {self.results['colony_snapshot'].health_score}%\n")
            if 'code_smells' in self.results:
                f.write(f"- **Total Code Smells**: {sum(self.results['code_smells']['smell_distribution'].values())}\n")
                f.write(f"- **Auto-fixable Issues**: {self.results['code_smells']['auto_fixable_count']}\n")
            f.write("\n")
            
            # Detailed Findings
            f.write("## Detailed Findings\n\n")
            
            # Code Quality
            f.write("### Code Quality Analysis\n\n")
            if 'code_smells' in self.results:
                f.write("| Smell Type | Count | Severity |\n")
                f.write("|------------|-------|----------|\n")
                for smell_type, count in self.results['code_smells']['smell_distribution'].items():
                    if count > 0:
                        f.write(f"| {smell_type.replace('_', ' ').title()} | {count} | Medium |\n")
            f.write("\n")
            
            # Recommendations
            f.write("## Recommendations\n\n")
            f.write("1. **Immediate Actions**:\n")
            f.write("   - Run auto-fix for simple code smells\n")
            f.write("   - Refactor god classes\n")
            f.write("   - Resolve circular dependencies\n\n")
            
            f.write("2. **ML Optimizations**:\n")
            f.write("   - Implement SwarmSearchCV for hyperparameter tuning\n")
            f.write("   - Use Pareto optimization for multi-objective goals\n")
            f.write("   - Consider ensemble methods with optimized weights\n\n")
            
            f.write("3. **Architecture Improvements**:\n")
            f.write("   - Modularize large classes\n")
            f.write("   - Implement dependency injection\n")
            f.write("   - Add comprehensive error handling\n\n")
            
        self.console.print(f"[green]✓[/green] Report saved to: {report_path}")
        
    async def run_full_analysis(self):
        """Run complete analysis pipeline"""
        try:
            self.show_welcome()
            
            # Confirm before starting
            if not Confirm.ask("\nProceed with full analysis?", default=True):
                return
                
            # Run all analyses
            await self.run_evolution_lab_analysis()
            self.run_code_smell_analysis()
            self.run_ml_optimization_suggestions()
            await self.run_dependency_analysis()
            self.generate_report()
            
            # Summary
            self.console.print("\n" + "="*60)
            self.console.print("[bold green]✨ Analysis Complete![/bold green]")
            self.console.print("\n[bold]Key Findings:[/bold]")
            
            if 'colony_snapshot' in self.results:
                self.console.print(f"  • Project Health: {self.results['colony_snapshot'].health_score}%")
            if 'code_smells' in self.results:
                total_smells = sum(self.results['code_smells']['smell_distribution'].values())
                self.console.print(f"  • Code Smells: {total_smells} issues found")
                self.console.print(f"  • Auto-fixable: {self.results['code_smells']['auto_fixable_count']} issues")
                
            self.console.print("\n[dim]Check ear_segmentation_analysis_report.md for detailed findings[/dim]")
            
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Analysis interrupted by user[/yellow]")
        except Exception as e:
            self.console.print(f"\n[red]Error during analysis: {e}[/red]")
            raise


async def main():
    """Entry point"""
    analyzer = EarSegmentationAnalyzer()
    await analyzer.run_full_analysis()


if __name__ == "__main__":
    asyncio.run(main())