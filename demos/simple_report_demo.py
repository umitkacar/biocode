#!/usr/bin/env python3
"""
Simple Report Generation Demo - Works without external dependencies
"""
import json
from pathlib import Path
from datetime import datetime


def generate_html_report(results, output_path):
    """Generate a beautiful HTML report"""
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>🧬 BioCode Analysis Report - {results['project_name']}</title>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f7fa;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .metric-card {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        }}
        .metric-value {{
            font-size: 3rem;
            font-weight: 700;
            color: #667eea;
        }}
        .section {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        }}
        .bio-visual {{
            text-align: center;
            padding: 40px;
            background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
            border-radius: 12px;
        }}
        .colony-cell {{
            display: inline-block;
            width: 60px;
            height: 60px;
            margin: 5px;
            border-radius: 50%;
            line-height: 60px;
            font-size: 2rem;
            animation: pulse 2s infinite;
        }}
        @keyframes pulse {{
            0% {{ transform: scale(1); opacity: 0.8; }}
            50% {{ transform: scale(1.1); opacity: 1; }}
            100% {{ transform: scale(1); opacity: 0.8; }}
        }}
        .healthy {{ background: #48bb78; }}
        .warning {{ background: #ed8936; }}
        .critical {{ background: #f56565; }}
        .smell-bar {{
            margin: 15px 0;
        }}
        .smell-label {{
            display: inline-block;
            width: 150px;
        }}
        .smell-progress {{
            display: inline-block;
            width: 300px;
            height: 25px;
            background: #e2e8f0;
            border-radius: 12px;
            overflow: hidden;
        }}
        .smell-fill {{
            height: 100%;
            background: linear-gradient(90deg, #f56565 0%, #ed8936 100%);
            text-align: right;
            padding-right: 10px;
            color: white;
            line-height: 25px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🧬 BioCode Analysis Report</h1>
        <p>{results['project_name']} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
    </div>

    <div class="container">
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{results['health_score']:.1f}%</div>
                <div>Health Score</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{results['total_issues']}</div>
                <div>Total Issues</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{results['auto_fixable']}</div>
                <div>Auto-fixable</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{results['files_count']}</div>
                <div>Files Analyzed</div>
            </div>
        </div>

        <div class="section bio-visual">
            <h2>🦠 Code Cell Colony</h2>
            <div>
                <span class="colony-cell healthy">🧬</span>
                <span class="colony-cell healthy">🧬</span>
                <span class="colony-cell warning">🧬</span>
                <span class="colony-cell healthy">🧬</span>
                <span class="colony-cell critical">🧬</span>
                <span class="colony-cell healthy">🧬</span>
            </div>
            <p>Living code cells representing module health</p>
        </div>

        <div class="section">
            <h2>🦨 Code Smell Distribution</h2>
            {generate_smell_bars(results['smell_distribution'])}
        </div>

        <div class="section">
            <h2>💡 Top Recommendations</h2>
            <ol>
                <li><strong>Extract Magic Numbers:</strong> Convert {results['smell_distribution'].get('magic_number', 0)} hardcoded values to named constants</li>
                <li><strong>Refactor Long Methods:</strong> Break down {results['smell_distribution'].get('long_method', 0)} complex functions</li>
                <li><strong>Improve Test Coverage:</strong> Current coverage needs improvement</li>
                <li><strong>Use SwarmSearchCV:</strong> Optimize ML hyperparameters for better accuracy</li>
            </ol>
        </div>
    </div>
</body>
</html>"""
    
    with open(output_path, 'w') as f:
        f.write(html)
    print(f"✓ HTML report: {output_path}")


def generate_smell_bars(smell_dist):
    """Generate HTML for smell distribution bars"""
    html = ""
    total = sum(smell_dist.values())
    for smell, count in smell_dist.items():
        if count > 0:
            width = min(90, (count / total) * 100 * 3)  # Scale for visibility
            html += f"""
            <div class="smell-bar">
                <span class="smell-label">{smell.replace('_', ' ').title()}</span>
                <span class="smell-progress">
                    <div class="smell-fill" style="width: {width}%">{count}</div>
                </span>
            </div>"""
    return html


def generate_markdown_report(results, output_path):
    """Generate Markdown report"""
    md = f"""# 🧬 BioCode Analysis Report

**Project:** {results['project_name']}  
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**Generated by:** BioCode Analysis Engine

## Executive Summary

The codebase has an overall health score of **{results['health_score']:.1f}%** with **{results['total_issues']} issues** detected across **{results['files_count']} files**.

## Key Metrics

| Metric | Value | Status |
|--------|-------|--------|
| Health Score | {results['health_score']:.1f}% | {'🟢' if results['health_score'] > 70 else '🟡' if results['health_score'] > 40 else '🔴'} |
| Total Issues | {results['total_issues']} | {'🟢' if results['total_issues'] < 100 else '🟡' if results['total_issues'] < 300 else '🔴'} |
| Auto-fixable | {results['auto_fixable']} | 🟢 |
| Files Analyzed | {results['files_count']} | - |

## Code Smell Distribution

"""
    
    for smell, count in results['smell_distribution'].items():
        if count > 0:
            md += f"- **{smell.replace('_', ' ').title()}**: {count} occurrences\n"
    
    md += """
## Recommendations

1. **Extract Magic Numbers** - Convert hardcoded values to named constants
2. **Refactor Complex Methods** - Break down long functions into smaller, focused units
3. **Increase Test Coverage** - Add unit tests for critical functionality
4. **Optimize with SwarmSearchCV** - Use PSO for hyperparameter tuning

## Next Steps

- Run `biocode fix` to automatically resolve {auto_fixable} issues
- Review and refactor high-complexity modules
- Implement suggested optimizations

---
*Generated by BioCode - Living Code Analysis Platform*
""".format(auto_fixable=results['auto_fixable'])
    
    with open(output_path, 'w') as f:
        f.write(md)
    print(f"✓ Markdown report: {output_path}")


def generate_json_report(results, output_path):
    """Generate JSON report"""
    json_data = {
        "metadata": {
            "project_name": results['project_name'],
            "timestamp": datetime.now().isoformat(),
            "generator": "BioCode Analysis Engine v1.0"
        },
        "summary": {
            "health_score": results['health_score'],
            "total_issues": results['total_issues'],
            "auto_fixable": results['auto_fixable'],
            "files_analyzed": results['files_count']
        },
        "code_smells": results['smell_distribution'],
        "recommendations": [
            {
                "priority": "High",
                "title": "Extract Magic Numbers",
                "description": f"Convert {results['smell_distribution'].get('magic_number', 0)} hardcoded values"
            },
            {
                "priority": "Medium",
                "title": "Refactor Long Methods",
                "description": f"Break down {results['smell_distribution'].get('long_method', 0)} complex functions"
            },
            {
                "priority": "High",
                "title": "Improve Test Coverage",
                "description": "Add unit tests for critical paths"
            }
        ]
    }
    
    with open(output_path, 'w') as f:
        json.dump(json_data, f, indent=2)
    print(f"✓ JSON report: {output_path}")


def main():
    """Run the demo"""
    print("🧬 BioCode Report Generation Demo")
    print("=" * 50)
    
    # Create reports directory
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    # Sample analysis results (from our previous analysis)
    results = {
        'project_name': 'Ear Segmentation AI',
        'health_score': 3.08,
        'total_issues': 286,
        'auto_fixable': 237,
        'files_count': 42,
        'smell_distribution': {
            'magic_number': 234,
            'long_method': 28,
            'long_parameter_list': 16,
            'commented_code': 3,
            'long_line': 3,
            'global_variable': 2
        }
    }
    
    print(f"\n📂 Generating reports for: {results['project_name']}")
    print(f"📊 Health Score: {results['health_score']:.1f}%")
    print(f"🐛 Total Issues: {results['total_issues']}")
    
    # Generate reports
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"ear_segmentation_report_{timestamp}"
    
    print("\n📝 Generating reports...")
    
    # HTML
    html_path = reports_dir / f"{base_name}.html"
    generate_html_report(results, html_path)
    
    # Markdown
    md_path = reports_dir / f"{base_name}.md"
    generate_markdown_report(results, md_path)
    
    # JSON
    json_path = reports_dir / f"{base_name}.json"
    generate_json_report(results, json_path)
    
    print("\n✅ All reports generated successfully!")
    print(f"\n📁 Reports saved in: {reports_dir.absolute()}")
    print("\n📋 Generated files:")
    for file in sorted(reports_dir.glob(f"{base_name}*")):
        size_kb = file.stat().st_size / 1024
        print(f"  • {file.name} ({size_kb:.1f} KB)")
    
    print(f"\n🌐 To view the HTML report:")
    print(f"  Open: file://{html_path.absolute()}")
    
    print("\n🎉 Demo completed!")


if __name__ == "__main__":
    main()