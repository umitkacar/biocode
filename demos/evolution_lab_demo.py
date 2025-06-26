"""
Evolution Lab Demo - Analyzing External Projects with BioCode Colony
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
import asyncio
import json
from pathlib import Path

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from evolution_lab.colony import EvolutionLabColony


async def main():
    """Demo: Analyze an external project using Evolution Lab Colony"""
    
    print("=" * 60)
    print("🧬 BioCode Evolution Lab - Project Analysis Demo")
    print("=" * 60)
    
    # Initialize colony
    colony = EvolutionLabColony()
    
    # Target project path (change this to analyze different projects)
    project_path = "/home/umit/CLAUDE_PROJECT/Ear-segmentation-ai"
    
    if not Path(project_path).exists():
        print(f"❌ Project not found: {project_path}")
        print("📝 Creating mock analysis for demonstration...")
        
        # Create mock snapshot for demo
        from evolution_lab.colony import ProjectSnapshot
        snapshot = ProjectSnapshot(
            project_path=project_path,
            health_score=85.5,
            metrics={
                'CodeAnalyzer': {
                    'primary_language': 'python',
                    'total_files': 45,
                    'total_lines': 3420,
                    'frameworks': ['TensorFlow', 'OpenCV'],
                    'average_complexity': 4.2
                },
                'AIModelAnalyzer': {
                    'model_files': {
                        'count': 2,
                        'files': [
                            {'path': 'models/ear_segmentation_v2.h5', 'size': 25*1024*1024},
                            {'path': 'checkpoints/best_model.pth', 'size': 18*1024*1024}
                        ]
                    },
                    'frameworks': {
                        'tensorflow': True,
                        'pytorch': True,
                        'opencv': True
                    },
                    'architecture': {
                        'type': 'segmentation',
                        'backbone': 'resnet50',
                        'custom_model': True
                    },
                    'dataset_analysis': {
                        'data_types': {'image': 1250},
                        'structure': {'split_found': True, 'splits': ['train', 'val', 'test']}
                    }
                }
            },
            issues=[
                {'severity': 'medium', 'type': 'size', 'message': 'Large model file (25MB): models/ear_segmentation_v2.h5'},
                {'severity': 'low', 'type': 'documentation', 'message': 'Missing API documentation'}
            ],
            suggestions=[
                "Consider model compression techniques to reduce model size",
                "Add REST API for model deployment",
                "Implement segmentation metrics (IoU, Dice) for evaluation"
            ]
        )
    else:
        print(f"🔬 Analyzing: {project_path}")
        print("⏳ Spawning analyzer cells...")
        print()
        
        # Run actual analysis
        snapshot = await colony.analyze_project(project_path)
    
    # Display results
    print("\n" + "=" * 60)
    print("📊 ANALYSIS RESULTS")
    print("=" * 60)
    
    print(f"\n🏥 Project Health Score: {snapshot.health_score:.1f}%")
    print(f"📁 Project Path: {snapshot.project_path}")
    print(f"🕐 Analysis Time: {snapshot.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Code Analysis Results
    if 'CodeAnalyzer' in snapshot.metrics:
        print("\n📝 CODE ANALYSIS")
        print("-" * 40)
        code_metrics = snapshot.metrics['CodeAnalyzer']
        print(f"  Primary Language: {code_metrics.get('primary_language', 'unknown')}")
        print(f"  Total Files: {code_metrics.get('total_files', 0)}")
        print(f"  Total Lines: {code_metrics.get('total_lines', 0)}")
        if 'frameworks' in code_metrics:
            print(f"  Frameworks: {', '.join(code_metrics['frameworks'])}")
        if 'average_complexity' in code_metrics:
            print(f"  Average Complexity: {code_metrics['average_complexity']:.2f}")
    
    # AI/ML Analysis Results
    if 'AIModelAnalyzer' in snapshot.metrics:
        print("\n🤖 AI/ML ANALYSIS")
        print("-" * 40)
        ai_metrics = snapshot.metrics['AIModelAnalyzer']
        
        # Model files
        model_info = ai_metrics.get('model_files', {})
        print(f"  Model Files Found: {model_info.get('count', 0)}")
        for model in model_info.get('files', [])[:3]:
            size_mb = model['size'] / (1024 * 1024)
            print(f"    - {model['path']} ({size_mb:.1f} MB)")
        
        # Frameworks
        frameworks = ai_metrics.get('frameworks', {})
        active_frameworks = [k for k, v in frameworks.items() if v]
        if active_frameworks:
            print(f"  ML Frameworks: {', '.join(active_frameworks)}")
        
        # Architecture
        arch = ai_metrics.get('architecture', {})
        if arch.get('type'):
            print(f"  Architecture Type: {arch['type']}")
            if arch.get('backbone'):
                print(f"  Backbone: {arch['backbone']}")
        
        # Dataset
        dataset = ai_metrics.get('dataset_analysis', {})
        if dataset.get('data_types'):
            for dtype, count in dataset['data_types'].items():
                print(f"  {dtype.capitalize()} Files: {count}")
    
    # Issues Found
    if snapshot.issues:
        print(f"\n⚠️  ISSUES FOUND ({len(snapshot.issues)})")
        print("-" * 40)
        for issue in snapshot.issues[:5]:
            icon = "🔴" if issue['severity'] == 'high' else "🟡" if issue['severity'] == 'medium' else "🟢"
            print(f"  {icon} [{issue['severity'].upper()}] {issue['message']}")
    
    # Suggestions
    if snapshot.suggestions:
        print(f"\n💡 SUGGESTIONS ({len(snapshot.suggestions)})")
        print("-" * 40)
        for i, suggestion in enumerate(snapshot.suggestions[:5], 1):
            print(f"  {i}. {suggestion}")
    
    # Colony Health
    print("\n🧬 COLONY STATUS")
    print("-" * 40)
    health = colony.get_colony_health()
    print(f"  Colony Status: {health['status']}")
    print(f"  Total Analyzer Cells: {health['total_cells']}")
    if health['total_cells'] > 0:
        print(f"  Healthy Cells: {health['healthy_cells']}")
        print(f"  Average Energy: {health['average_energy']:.1f}%")
        print(f"  Active Analyzers: {', '.join(health['analyzers_active'])}")
    
    # Export results
    output_file = "project_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(snapshot.to_dict(), f, indent=2)
    print(f"\n💾 Full analysis exported to: {output_file}")
    
    print("\n" + "=" * 60)
    print("✅ Analysis Complete!")
    print("=" * 60)
    
    # Show what data could be sent to a dashboard
    print("\n📡 REALTIME DASHBOARD DATA PREVIEW")
    print("-" * 40)
    dashboard_data = {
        "project_id": "ear-segmentation-ai",
        "timestamp": snapshot.timestamp.isoformat(),
        "health_score": snapshot.health_score,
        "metrics_summary": {
            "total_files": snapshot.metrics.get('CodeAnalyzer', {}).get('total_files', 0),
            "primary_language": snapshot.metrics.get('CodeAnalyzer', {}).get('primary_language', 'unknown'),
            "model_count": snapshot.metrics.get('AIModelAnalyzer', {}).get('model_files', {}).get('count', 0),
            "issues_count": len(snapshot.issues),
            "suggestions_count": len(snapshot.suggestions)
        },
        "live_updates": {
            "analyzer_cells": health['total_cells'],
            "healthy_cells": health.get('healthy_cells', 0),
            "analysis_progress": 100.0  # Complete
        }
    }
    
    print(json.dumps(dashboard_data, indent=2))
    
    print("\n🚀 This data could be streamed to a WebSocket dashboard for real-time monitoring!")
    
    # Ask if user wants to run dashboard
    print("\n" + "=" * 60)
    choice = input("\n🔧 Would you like to run the realtime dashboard? (y/n): ")
    
    if choice.lower() == 'y':
        print("\n🌐 Starting Realtime Dashboard...")
        print("=" * 60)
        
        # Check if required packages are installed
        try:
            import websockets
            import aiohttp
            import aiohttp_cors
        except ImportError:
            print("\n⚠️  Missing required packages for dashboard!")
            print("   Please install: pip install websockets aiohttp aiohttp-cors")
            return
            
        # Import and run dashboard
        from evolution_lab.dashboard_demo import main as dashboard_main
        await dashboard_main()


if __name__ == "__main__":
    asyncio.run(main())