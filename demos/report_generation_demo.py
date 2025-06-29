#!/usr/bin/env python3
"""
🧬 BioCode Report Generation Demo
Demonstrates multi-format report generation for code analysis
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.evolution_lab.report_generator import ReportGenerator
from src.evolution_lab.analyzers.code_smell_analyzer import CodeSmellAnalyzer
from src.evolution_lab.colony import EvolutionLabColony


async def analyze_project_and_generate_reports():
    """Analyze a project and generate reports in multiple formats"""
    print("🧬 BioCode Report Generation Demo")
    print("=" * 50)
    
    # Target project
    project_path = "/home/umit/CLAUDE_PROJECT/Ear-segmentation-ai"
    print(f"\n📂 Analyzing project: {project_path}")
    
    # 1. Run code smell analysis
    print("\n🔍 Running code analysis...")
    smell_analyzer = CodeSmellAnalyzer(project_path)
    smell_results = smell_analyzer.analyze()
    
    # 2. Run Evolution Lab analysis
    print("🧪 Running Evolution Lab analysis...")
    colony = EvolutionLabColony()
    colony_snapshot = await colony.analyze_project(project_path)
    
    # 3. Prepare comprehensive results
    analysis_results = {
        'project_name': 'Ear Segmentation AI',
        'health_score': colony_snapshot.health_score,
        'total_issues': sum(smell_results['smell_distribution'].values()),
        'coverage': 65,  # Mock value for demo
        'debt_hours': 48,  # Mock value
        'security_issues': 3,  # Mock value
        'performance_bottlenecks': 7,  # Mock value
        'files_analyzed': list(smell_results.get('files_analyzed', []))[:10],
        'metrics': {
            'health_score': colony_snapshot.health_score,
            'total_issues': sum(smell_results['smell_distribution'].values()),
            'code_coverage': 65,
            'technical_debt': 48,
            'analyzers': colony_snapshot.metrics
        },
        'code_smells': smell_results,
        'quality_metrics': {
            'maintainability': 72,
            'reliability': 78,
            'security': 65,
            'performance': 70,
            'testability': 60,
            'documentation': 45
        },
        'file_metrics': {
            'model.py': {'complexity': 15, 'lines': 450, 'functions': 23, 'classes': 5},
            'train.py': {'complexity': 12, 'lines': 380, 'functions': 18, 'classes': 3},
            'utils.py': {'complexity': 8, 'lines': 220, 'functions': 15, 'classes': 2},
            'preprocess.py': {'complexity': 10, 'lines': 180, 'functions': 12, 'classes': 1}
        },
        'dependencies': {
            'model': ['utils', 'preprocess'],
            'train': ['model', 'utils'],
            'utils': ['config'],
            'preprocess': ['utils']
        },
        'history': [
            {'generation': i, 'fitness': 0.5 + i*0.05, 'mutations': i*2}
            for i in range(10)
        ]
    }
    
    # 4. Generate reports
    print("\n📊 Generating reports...")
    generator = ReportGenerator(output_dir="reports")
    
    # Generate in multiple formats
    generated_files = await generator.generate_report(
        analysis_results,
        'ear_segmentation',
        formats=['html', 'pdf', 'md', 'json'],
        theme='biological'
    )
    
    print("\n✅ Reports generated successfully!")
    print("\n📁 Generated files:")
    for format_type, file_path in generated_files.items():
        print(f"  • {format_type.upper()}: {file_path}")
        
    # Show file sizes
    print("\n📏 File sizes:")
    for format_type, file_path in generated_files.items():
        if file_path.exists():
            size_kb = file_path.stat().st_size / 1024
            print(f"  • {format_type.upper()}: {size_kb:.1f} KB")
    
    # Display summary of what's in each report
    print("\n📋 Report contents:")
    print("  • Executive summary with health metrics")
    print("  • Interactive visualizations (HTML)")
    print("  • Code smell distribution charts")
    print("  • Quality radar charts")
    print("  • Dependency network graphs")
    print("  • Colony health visualization")
    print("  • Actionable recommendations")
    print("  • Detailed findings and metrics")
    
    print("\n🌐 To view the HTML report:")
    print(f"  Open: {generated_files.get('html', 'N/A')}")
    
    return generated_files


async def main():
    """Main demo runner"""
    try:
        # Create reports directory
        Path("reports").mkdir(exist_ok=True)
        
        # Generate reports
        files = await analyze_project_and_generate_reports()
        
        print("\n" + "="*50)
        print("🎉 Demo completed successfully!")
        print("\nNext steps:")
        print("1. Open the HTML report in your browser")
        print("2. Review the PDF for a printable version")
        print("3. Check the Markdown for version control")
        print("4. Use the JSON for API integration")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())