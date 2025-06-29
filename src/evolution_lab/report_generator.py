"""
🧬 BioCode Report Generator - Advanced Multi-format Report Generation
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.

Generates beautiful reports in multiple formats:
- PDF with ReportLab
- Interactive HTML with Plotly
- Markdown for version control
- PNG/SVG visualizations
"""

import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import json
import base64
from io import BytesIO

# Visualization libraries
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import networkx as nx

# Report generation
from jinja2 import Environment, FileSystemLoader, Template
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.pdfgen import canvas

# For treemaps
try:
    import squarify
except ImportError:
    squarify = None

# For word clouds (optional)
try:
    from wordcloud import WordCloud
except ImportError:
    WordCloud = None


class BiologicalVisualizer:
    """Create biology-inspired visualizations"""
    
    @staticmethod
    def create_colony_visualization(metrics: Dict[str, Any]) -> go.Figure:
        """Create an animated cell colony visualization"""
        # Simulate cell positions and states
        import numpy as np
        
        n_cells = len(metrics.get('analyzers', {}))
        if n_cells == 0:
            n_cells = 10
            
        # Generate cell positions in a organic cluster
        theta = np.random.uniform(0, 2*np.pi, n_cells)
        r = np.random.normal(0, 1, n_cells)
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        
        # Cell properties
        sizes = np.random.uniform(20, 60, n_cells)
        health = np.random.uniform(0.3, 1.0, n_cells)
        
        # Create scatter plot
        fig = go.Figure()
        
        # Add cells
        fig.add_trace(go.Scatter(
            x=x, y=y,
            mode='markers',
            marker=dict(
                size=sizes,
                color=health,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Health"),
                line=dict(width=2, color='white')
            ),
            text=[f"Analyzer {i+1}<br>Health: {h:.2%}" for i, h in enumerate(health)],
            hoverinfo='text',
            name='Colony Cells'
        ))
        
        # Add connections between nearby cells
        for i in range(n_cells):
            for j in range(i+1, n_cells):
                dist = np.sqrt((x[i]-x[j])**2 + (y[i]-y[j])**2)
                if dist < 1.5:  # Connect nearby cells
                    fig.add_trace(go.Scatter(
                        x=[x[i], x[j]], y=[y[i], y[j]],
                        mode='lines',
                        line=dict(width=1, color='rgba(255,255,255,0.3)'),
                        showlegend=False,
                        hoverinfo='skip'
                    ))
        
        fig.update_layout(
            title="🧬 Code Cell Colony Health Status",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='rgba(0,0,0,0.9)',
            paper_bgcolor='rgba(0,0,0,0.8)',
            font=dict(color='white'),
            height=600,
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def create_evolution_tree(history: List[Dict]) -> go.Figure:
        """Create an evolutionary tree diagram"""
        if not history:
            # Create sample data
            history = [
                {'generation': i, 'fitness': 0.5 + i*0.05, 'mutations': i*2}
                for i in range(10)
            ]
        
        fig = go.Figure()
        
        # Main evolution line
        generations = [h.get('generation', i) for i, h in enumerate(history)]
        fitness = [h.get('fitness', 0.5) for h in history]
        
        fig.add_trace(go.Scatter(
            x=generations,
            y=fitness,
            mode='lines+markers',
            name='Main Branch',
            line=dict(width=4, color='green'),
            marker=dict(size=10, color='darkgreen')
        ))
        
        # Add mutation branches
        for i, h in enumerate(history):
            if h.get('mutations', 0) > 0:
                # Create small branches
                branch_x = [generations[i], generations[i] + 0.3]
                branch_y = [fitness[i], fitness[i] + np.random.uniform(-0.1, 0.1)]
                fig.add_trace(go.Scatter(
                    x=branch_x, y=branch_y,
                    mode='lines',
                    line=dict(width=2, color='lightgreen'),
                    showlegend=False
                ))
        
        fig.update_layout(
            title="🌳 Code Evolution Tree",
            xaxis_title="Generation",
            yaxis_title="Fitness Score",
            template="plotly_dark",
            height=500
        )
        
        return fig
    
    @staticmethod
    def create_dna_helix(code_metrics: Dict[str, float]) -> go.Figure:
        """Create a 3D DNA helix visualization"""
        import numpy as np
        
        # Generate helix coordinates
        t = np.linspace(0, 4*np.pi, 100)
        x1 = np.cos(t)
        y1 = np.sin(t)
        z = t
        
        x2 = np.cos(t + np.pi)
        y2 = np.sin(t + np.pi)
        
        fig = go.Figure()
        
        # First strand
        fig.add_trace(go.Scatter3d(
            x=x1, y=y1, z=z,
            mode='lines',
            line=dict(width=6, color='blue'),
            name='Code Structure'
        ))
        
        # Second strand
        fig.add_trace(go.Scatter3d(
            x=x2, y=y2, z=z,
            mode='lines',
            line=dict(width=6, color='red'),
            name='Test Coverage'
        ))
        
        # Connections between strands
        for i in range(0, len(t), 5):
            fig.add_trace(go.Scatter3d(
                x=[x1[i], x2[i]], 
                y=[y1[i], y2[i]], 
                z=[z[i], z[i]],
                mode='lines',
                line=dict(width=2, color='gray'),
                showlegend=False
            ))
        
        fig.update_layout(
            title="🧬 Code DNA Structure",
            scene=dict(
                xaxis=dict(showgrid=False, showticklabels=False),
                yaxis=dict(showgrid=False, showticklabels=False),
                zaxis=dict(showgrid=False, showticklabels=False),
                bgcolor='black'
            ),
            paper_bgcolor='black',
            font=dict(color='white'),
            height=600
        )
        
        return fig


class StandardVisualizer:
    """Create standard code analysis visualizations"""
    
    @staticmethod
    def create_complexity_heatmap(file_metrics: Dict[str, Dict]) -> plt.Figure:
        """Create a heatmap of code complexity"""
        if not file_metrics:
            return None
            
        # Prepare data
        files = list(file_metrics.keys())[:20]  # Top 20 files
        metrics = ['complexity', 'lines', 'functions', 'classes']
        
        data = []
        for metric in metrics:
            row = [file_metrics[f].get(metric, 0) for f in files]
            # Normalize
            if max(row) > 0:
                row = [v/max(row) for v in row]
            data.append(row)
        
        # Create heatmap
        fig, ax = plt.subplots(figsize=(12, 6))
        
        sns.heatmap(
            data, 
            xticklabels=[f.split('/')[-1][:20] for f in files],
            yticklabels=metrics,
            cmap='YlOrRd',
            annot=True,
            fmt='.2f',
            cbar_kws={'label': 'Normalized Score'}
        )
        
        plt.title('Code Complexity Heatmap')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        return fig
    
    @staticmethod
    def create_dependency_network(dependencies: Dict[str, List[str]]) -> go.Figure:
        """Create an interactive dependency network"""
        if not dependencies:
            return None
            
        # Create graph
        G = nx.DiGraph()
        
        for source, targets in dependencies.items():
            for target in targets:
                G.add_edge(source, target)
        
        # Calculate layout
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        # Create edge traces
        edge_trace = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_trace.append(go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode='lines',
                line=dict(width=0.5, color='gray'),
                hoverinfo='none'
            ))
        
        # Create node trace
        node_trace = go.Scatter(
            x=[pos[node][0] for node in G.nodes()],
            y=[pos[node][1] for node in G.nodes()],
            mode='markers+text',
            text=[node.split('.')[-1] for node in G.nodes()],
            textposition="top center",
            marker=dict(
                size=10,
                color=[G.degree(node) for node in G.nodes()],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Connections")
            )
        )
        
        # Create figure
        fig = go.Figure(data=edge_trace + [node_trace])
        
        fig.update_layout(
            title="Module Dependency Network",
            showlegend=False,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            hovermode='closest'
        )
        
        return fig
    
    @staticmethod
    def create_code_quality_radar(metrics: Dict[str, float]) -> go.Figure:
        """Create a radar chart for code quality metrics"""
        categories = ['Maintainability', 'Reliability', 'Security', 
                     'Performance', 'Testability', 'Documentation']
        
        # Normalize values to 0-100
        values = [
            metrics.get('maintainability', 70),
            metrics.get('reliability', 80),
            metrics.get('security', 60),
            metrics.get('performance', 75),
            metrics.get('testability', 65),
            metrics.get('documentation', 50)
        ]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Current State',
            fillcolor='rgba(0, 100, 255, 0.3)',
            line=dict(color='blue', width=2)
        ))
        
        # Add target line
        target = [80] * len(categories)
        fig.add_trace(go.Scatterpolar(
            r=target,
            theta=categories,
            name='Target',
            line=dict(color='green', width=2, dash='dash')
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            title="Code Quality Radar",
            showlegend=True
        )
        
        return fig


class ReportGenerator:
    """Main report generator supporting multiple formats"""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize visualizers
        self.bio_viz = BiologicalVisualizer()
        self.std_viz = StandardVisualizer()
        
        # Setup Jinja2 for HTML templates
        self.env = Environment(
            loader=FileSystemLoader(Path(__file__).parent / "templates"),
            autoescape=True
        )
        
    async def generate_report(
        self,
        analysis_results: Dict[str, Any],
        project_name: str,
        formats: List[str] = ['html', 'pdf', 'md'],
        theme: str = 'biological'
    ) -> Dict[str, Path]:
        """Generate reports in multiple formats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"{project_name}_analysis_{timestamp}"
        
        # Generate visualizations
        visualizations = await self._create_all_visualizations(
            analysis_results, theme
        )
        
        # Generate reports in each format
        generated_files = {}
        
        if 'html' in formats:
            generated_files['html'] = await self._generate_html(
                analysis_results, visualizations, base_name
            )
            
        if 'pdf' in formats:
            generated_files['pdf'] = await self._generate_pdf(
                analysis_results, visualizations, base_name
            )
            
        if 'md' in formats:
            generated_files['md'] = await self._generate_markdown(
                analysis_results, base_name
            )
            
        if 'json' in formats:
            generated_files['json'] = await self._generate_json(
                analysis_results, base_name
            )
            
        return generated_files
    
    async def _create_all_visualizations(
        self, 
        results: Dict[str, Any], 
        theme: str
    ) -> Dict[str, Any]:
        """Create all visualizations based on theme"""
        viz = {}
        
        if theme == 'biological':
            # Biological visualizations
            viz['colony'] = self.bio_viz.create_colony_visualization(
                results.get('metrics', {})
            )
            viz['evolution'] = self.bio_viz.create_evolution_tree(
                results.get('history', [])
            )
            viz['dna'] = self.bio_viz.create_dna_helix(
                results.get('code_metrics', {})
            )
        
        # Standard visualizations (always included)
        viz['complexity_heatmap'] = self.std_viz.create_complexity_heatmap(
            results.get('file_metrics', {})
        )
        viz['dependency_network'] = self.std_viz.create_dependency_network(
            results.get('dependencies', {})
        )
        viz['quality_radar'] = self.std_viz.create_code_quality_radar(
            results.get('quality_metrics', {})
        )
        
        # Code smell distribution
        if 'code_smells' in results:
            viz['smell_distribution'] = self._create_smell_distribution(
                results['code_smells']
            )
        
        return viz
    
    def _create_smell_distribution(self, code_smells: Dict) -> go.Figure:
        """Create a treemap of code smell distribution"""
        if not squarify:
            # Fallback to bar chart if squarify not available
            return self._create_smell_bar_chart(code_smells)
            
        smell_dist = code_smells.get('smell_distribution', {})
        if not smell_dist:
            return None
            
        labels = []
        values = []
        parents = []
        
        for smell_type, count in smell_dist.items():
            if count > 0:
                labels.append(smell_type.replace('_', ' ').title())
                values.append(count)
                parents.append("")
        
        fig = go.Figure(go.Treemap(
            labels=labels,
            values=values,
            parents=parents,
            textinfo="label+value+percent parent",
            marker=dict(
                colorscale='Reds',
                cmid=50
            )
        ))
        
        fig.update_layout(
            title="Code Smell Distribution",
            height=500
        )
        
        return fig
    
    def _create_smell_bar_chart(self, code_smells: Dict) -> go.Figure:
        """Fallback bar chart for code smells"""
        smell_dist = code_smells.get('smell_distribution', {})
        
        smells = []
        counts = []
        
        for smell, count in smell_dist.items():
            if count > 0:
                smells.append(smell.replace('_', ' ').title())
                counts.append(count)
        
        fig = go.Figure([go.Bar(x=smells, y=counts)])
        fig.update_layout(
            title="Code Smell Distribution",
            xaxis_title="Smell Type",
            yaxis_title="Count"
        )
        
        return fig
    
    async def _generate_html(
        self, 
        results: Dict[str, Any], 
        visualizations: Dict[str, Any],
        base_name: str
    ) -> Path:
        """Generate interactive HTML report"""
        # Convert Plotly figures to HTML
        viz_html = {}
        for name, fig in visualizations.items():
            if fig is not None:
                if isinstance(fig, go.Figure):
                    viz_html[name] = fig.to_html(
                        include_plotlyjs='cdn',
                        div_id=f"viz_{name}"
                    )
                elif isinstance(fig, plt.Figure):
                    # Convert matplotlib to base64 image
                    buf = BytesIO()
                    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
                    buf.seek(0)
                    img_base64 = base64.b64encode(buf.read()).decode()
                    viz_html[name] = f'<img src="data:image/png;base64,{img_base64}" class="img-fluid">'
                    plt.close(fig)
        
        # Prepare template data
        template_data = {
            'project_name': results.get('project_name', 'Unknown'),
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'summary': self._generate_summary(results),
            'metrics': results.get('metrics', {}),
            'visualizations': viz_html,
            'findings': self._generate_findings(results),
            'recommendations': self._generate_recommendations(results)
        }
        
        # Render template
        template = self._get_html_template()
        html_content = template.render(**template_data)
        
        # Save file
        output_path = self.output_dir / f"{base_name}.html"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        return output_path
    
    def _get_html_template(self) -> Template:
        """Get or create HTML template"""
        template_str = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BioCode Analysis Report - {{ project_name }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        .navbar { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .metric-card { 
            background: white; 
            border-radius: 10px; 
            padding: 20px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .metric-value { font-size: 2.5rem; font-weight: 700; color: #667eea; }
        .section-title { 
            font-size: 2rem; 
            font-weight: 600; 
            margin: 30px 0 20px 0;
            color: #2d3748;
        }
        .bio-theme { background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%); }
        .finding-card {
            background: #f7fafc;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark">
        <div class="container-fluid">
            <span class="navbar-brand mb-0 h1">🧬 BioCode Analysis Report</span>
            <span class="navbar-text">{{ timestamp }}</span>
        </div>
    </nav>
    
    <div class="container mt-4">
        <!-- Summary Section -->
        <div class="row">
            <div class="col-12">
                <h1>{{ project_name }} Analysis</h1>
                <p class="lead">{{ summary }}</p>
            </div>
        </div>
        
        <!-- Key Metrics -->
        <div class="row mt-4">
            <div class="col-md-3">
                <div class="metric-card text-center">
                    <div class="metric-value">{{ metrics.health_score|default(0) }}%</div>
                    <div class="metric-label">Health Score</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card text-center">
                    <div class="metric-value">{{ metrics.total_issues|default(0) }}</div>
                    <div class="metric-label">Total Issues</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card text-center">
                    <div class="metric-value">{{ metrics.code_coverage|default(0) }}%</div>
                    <div class="metric-label">Code Coverage</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card text-center">
                    <div class="metric-value">{{ metrics.technical_debt|default(0) }}h</div>
                    <div class="metric-label">Technical Debt</div>
                </div>
            </div>
        </div>
        
        <!-- Visualizations -->
        <h2 class="section-title">📊 Visualizations</h2>
        
        {% if visualizations.colony %}
        <div class="row">
            <div class="col-12">
                <div class="card mb-4">
                    <div class="card-body">
                        {{ visualizations.colony|safe }}
                    </div>
                </div>
            </div>
        </div>
        {% endif %}
        
        <div class="row">
            {% if visualizations.quality_radar %}
            <div class="col-md-6">
                <div class="card mb-4">
                    <div class="card-body">
                        {{ visualizations.quality_radar|safe }}
                    </div>
                </div>
            </div>
            {% endif %}
            
            {% if visualizations.smell_distribution %}
            <div class="col-md-6">
                <div class="card mb-4">
                    <div class="card-body">
                        {{ visualizations.smell_distribution|safe }}
                    </div>
                </div>
            </div>
            {% endif %}
        </div>
        
        {% if visualizations.dependency_network %}
        <div class="row">
            <div class="col-12">
                <div class="card mb-4">
                    <div class="card-body">
                        {{ visualizations.dependency_network|safe }}
                    </div>
                </div>
            </div>
        </div>
        {% endif %}
        
        <!-- Findings -->
        <h2 class="section-title">🔍 Key Findings</h2>
        {% for finding in findings %}
        <div class="finding-card">
            <h5>{{ finding.title }}</h5>
            <p>{{ finding.description }}</p>
            {% if finding.severity %}
            <span class="badge bg-{{ finding.severity }}">{{ finding.severity|upper }}</span>
            {% endif %}
        </div>
        {% endfor %}
        
        <!-- Recommendations -->
        <h2 class="section-title">💡 Recommendations</h2>
        <div class="row">
            {% for rec in recommendations %}
            <div class="col-md-6">
                <div class="card mb-3">
                    <div class="card-body">
                        <h5 class="card-title">{{ rec.title }}</h5>
                        <p class="card-text">{{ rec.description }}</p>
                        <small class="text-muted">Priority: {{ rec.priority }}</small>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
        
        <!-- Footer -->
        <footer class="mt-5 mb-3 text-center text-muted">
            <p>Generated by BioCode Analysis Engine | © 2024 Umit Kacar, PhD</p>
        </footer>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
        """
        return Template(template_str)
    
    async def _generate_pdf(
        self,
        results: Dict[str, Any],
        visualizations: Dict[str, Any],
        base_name: str
    ) -> Path:
        """Generate PDF report using ReportLab"""
        output_path = self.output_dir / f"{base_name}.pdf"
        
        # Create document
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Container for elements
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#667eea'),
            alignment=TA_CENTER
        )
        elements.append(Paragraph("BioCode Analysis Report", title_style))
        elements.append(Spacer(1, 20))
        
        # Project info
        elements.append(Paragraph(
            f"<b>Project:</b> {results.get('project_name', 'Unknown')}", 
            styles['Normal']
        ))
        elements.append(Paragraph(
            f"<b>Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}", 
            styles['Normal']
        ))
        elements.append(Spacer(1, 20))
        
        # Summary
        summary = self._generate_summary(results)
        elements.append(Paragraph("<b>Executive Summary</b>", styles['Heading2']))
        elements.append(Paragraph(summary, styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Key metrics table
        metrics_data = [
            ['Metric', 'Value', 'Status'],
            ['Health Score', f"{results.get('health_score', 0)}%", self._get_status_emoji(results.get('health_score', 0))],
            ['Code Coverage', f"{results.get('coverage', 0)}%", self._get_status_emoji(results.get('coverage', 0))],
            ['Technical Debt', f"{results.get('debt_hours', 0)} hours", '⚠️' if results.get('debt_hours', 0) > 40 else '✅'],
            ['Security Issues', str(results.get('security_issues', 0)), '🔴' if results.get('security_issues', 0) > 0 else '✅'],
        ]
        
        metrics_table = Table(metrics_data)
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(Paragraph("<b>Key Metrics</b>", styles['Heading2']))
        elements.append(metrics_table)
        elements.append(PageBreak())
        
        # Add visualizations as images
        for name, fig in visualizations.items():
            if fig is not None and isinstance(fig, (go.Figure, plt.Figure)):
                # Convert to image
                img_path = self.output_dir / f"{base_name}_{name}.png"
                
                if isinstance(fig, go.Figure):
                    fig.write_image(str(img_path), width=800, height=600)
                else:
                    fig.savefig(img_path, dpi=150, bbox_inches='tight')
                    plt.close(fig)
                
                # Add to PDF
                elements.append(Paragraph(f"<b>{name.replace('_', ' ').title()}</b>", styles['Heading3']))
                elements.append(Image(str(img_path), width=6*inch, height=4*inch))
                elements.append(Spacer(1, 20))
        
        # Build PDF
        doc.build(elements)
        
        return output_path
    
    async def _generate_markdown(
        self,
        results: Dict[str, Any],
        base_name: str
    ) -> Path:
        """Generate Markdown report"""
        output_path = self.output_dir / f"{base_name}.md"
        
        content = f"""# BioCode Analysis Report

**Project:** {results.get('project_name', 'Unknown')}  
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**Generated by:** BioCode Analysis Engine v1.0

## Executive Summary

{self._generate_summary(results)}

## Key Metrics

| Metric | Value | Status |
|--------|-------|--------|
| Health Score | {results.get('health_score', 0)}% | {self._get_status_emoji(results.get('health_score', 0))} |
| Code Coverage | {results.get('coverage', 0)}% | {self._get_status_emoji(results.get('coverage', 0))} |
| Technical Debt | {results.get('debt_hours', 0)} hours | {'⚠️' if results.get('debt_hours', 0) > 40 else '✅'} |
| Total Issues | {results.get('total_issues', 0)} | {'🔴' if results.get('total_issues', 0) > 100 else '✅'} |

## Analysis Results

### Code Quality

"""
        
        # Add code smell analysis if available
        if 'code_smells' in results:
            smell_dist = results['code_smells'].get('smell_distribution', {})
            content += "\n#### Code Smell Distribution\n\n"
            for smell, count in smell_dist.items():
                if count > 0:
                    content += f"- **{smell.replace('_', ' ').title()}**: {count} occurrences\n"
        
        # Add findings
        content += "\n## Key Findings\n\n"
        for finding in self._generate_findings(results):
            content += f"### {finding['title']}\n\n{finding['description']}\n\n"
        
        # Add recommendations
        content += "\n## Recommendations\n\n"
        for i, rec in enumerate(self._generate_recommendations(results), 1):
            content += f"{i}. **{rec['title']}** - {rec['description']}\n"
        
        # Write file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return output_path
    
    async def _generate_json(
        self,
        results: Dict[str, Any],
        base_name: str
    ) -> Path:
        """Generate JSON report for API consumption"""
        output_path = self.output_dir / f"{base_name}.json"
        
        # Prepare JSON-serializable data
        json_data = {
            'metadata': {
                'project_name': results.get('project_name', 'Unknown'),
                'timestamp': datetime.now().isoformat(),
                'generator': 'BioCode Analysis Engine v1.0'
            },
            'summary': {
                'health_score': results.get('health_score', 0),
                'total_issues': results.get('total_issues', 0),
                'code_coverage': results.get('coverage', 0),
                'technical_debt_hours': results.get('debt_hours', 0)
            },
            'metrics': results.get('metrics', {}),
            'findings': self._generate_findings(results),
            'recommendations': self._generate_recommendations(results)
        }
        
        # Write file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
            
        return output_path
    
    def _generate_summary(self, results: Dict[str, Any]) -> str:
        """Generate executive summary text"""
        health = results.get('health_score', 0)
        issues = results.get('total_issues', 0)
        
        if health > 80:
            status = "excellent condition"
        elif health > 60:
            status = "good condition with room for improvement"
        elif health > 40:
            status = "fair condition requiring attention"
        else:
            status = "poor condition requiring immediate action"
            
        summary = f"""The codebase is in {status} with an overall health score of {health}%. 
        Analysis identified {issues} total issues across {len(results.get('files_analyzed', []))} files. 
        The estimated technical debt is {results.get('debt_hours', 0)} hours of work."""
        
        return summary
    
    def _generate_findings(self, results: Dict[str, Any]) -> List[Dict]:
        """Generate key findings from analysis"""
        findings = []
        
        # Code smell findings
        if 'code_smells' in results:
            total_smells = sum(results['code_smells'].get('smell_distribution', {}).values())
            if total_smells > 0:
                findings.append({
                    'title': 'Code Quality Issues',
                    'description': f'Found {total_smells} code smells that impact maintainability',
                    'severity': 'warning' if total_smells < 50 else 'danger'
                })
        
        # Security findings
        if results.get('security_issues', 0) > 0:
            findings.append({
                'title': 'Security Vulnerabilities',
                'description': f'Detected {results["security_issues"]} potential security issues',
                'severity': 'danger'
            })
        
        # Performance findings
        if results.get('performance_bottlenecks', 0) > 0:
            findings.append({
                'title': 'Performance Bottlenecks',
                'description': f'Identified {results["performance_bottlenecks"]} performance issues',
                'severity': 'warning'
            })
        
        return findings
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[Dict]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Based on health score
        health = results.get('health_score', 0)
        if health < 60:
            recommendations.append({
                'title': 'Improve Code Quality',
                'description': 'Focus on refactoring complex functions and reducing code duplication',
                'priority': 'High'
            })
        
        # Based on code smells
        if 'code_smells' in results:
            auto_fixable = results['code_smells'].get('auto_fixable_count', 0)
            if auto_fixable > 0:
                recommendations.append({
                    'title': 'Apply Auto-fixes',
                    'description': f'Use BioCode auto-fix to resolve {auto_fixable} issues automatically',
                    'priority': 'Medium'
                })
        
        # Based on coverage
        coverage = results.get('coverage', 0)
        if coverage < 70:
            recommendations.append({
                'title': 'Increase Test Coverage',
                'description': f'Current coverage is {coverage}%. Aim for at least 80% coverage',
                'priority': 'High'
            })
        
        return recommendations
    
    def _get_status_emoji(self, value: float) -> str:
        """Get status emoji based on value"""
        if value >= 80:
            return '✅'
        elif value >= 60:
            return '⚠️'
        else:
            return '🔴'


# Example usage
async def demo_report_generation():
    """Demo the report generator"""
    # Sample analysis results
    results = {
        'project_name': 'Ear Segmentation AI',
        'health_score': 73.5,
        'total_issues': 286,
        'coverage': 65,
        'debt_hours': 48,
        'security_issues': 3,
        'performance_bottlenecks': 7,
        'files_analyzed': ['model.py', 'train.py', 'utils.py'],
        'metrics': {
            'health_score': 73.5,
            'total_issues': 286,
            'code_coverage': 65,
            'technical_debt': 48
        },
        'code_smells': {
            'smell_distribution': {
                'long_method': 28,
                'magic_number': 234,
                'deep_nesting': 17,
                'god_class': 7
            },
            'auto_fixable_count': 237
        },
        'quality_metrics': {
            'maintainability': 72,
            'reliability': 78,
            'security': 65,
            'performance': 70,
            'testability': 60,
            'documentation': 45
        }
    }
    
    # Generate reports
    generator = ReportGenerator()
    files = await generator.generate_report(
        results,
        'ear_segmentation',
        formats=['html', 'pdf', 'md', 'json'],
        theme='biological'
    )
    
    print("Generated reports:")
    for fmt, path in files.items():
        print(f"  {fmt}: {path}")


if __name__ == "__main__":
    # Run demo
    import asyncio
    asyncio.run(demo_report_generation())