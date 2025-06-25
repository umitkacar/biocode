// BioCode Agent Visualization with D3.js
class AgentVisualization {
    constructor(containerId) {
        this.container = d3.select(containerId);
        this.width = 1200;
        this.height = 800;
        this.nodes = [];
        this.links = [];
        this.simulation = null;
        
        // Color scheme
        this.colors = {
            generation0: '#00ff41',
            generation1: '#00cc33',
            generation2: '#009926',
            generation3: '#006619',
            dead: '#666666',
            link: '#333333',
            communication: '#0080ff',
            knowledge: '#ff00ff'
        };
        
        this.init();
    }
    
    init() {
        // Create SVG
        this.svg = this.container
            .append('svg')
            .attr('width', this.width)
            .attr('height', this.height)
            .style('background', '#0a0a0a');
            
        // Add patterns for different node states
        const defs = this.svg.append('defs');
        
        // Healthy pattern
        const healthyPattern = defs.append('pattern')
            .attr('id', 'healthy-pattern')
            .attr('width', 4)
            .attr('height', 4)
            .attr('patternUnits', 'userSpaceOnUse');
            
        healthyPattern.append('rect')
            .attr('width', 4)
            .attr('height', 4)
            .attr('fill', '#00ff41');
            
        healthyPattern.append('path')
            .attr('d', 'M 0,4 l 4,-4 M -1,1 l 2,-2 M 3,5 l 2,-2')
            .attr('stroke', '#00ff9f')
            .attr('stroke-width', 1);
            
        // Create groups
        this.g = this.svg.append('g');
        
        // Add zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.1, 10])
            .on('zoom', (event) => {
                this.g.attr('transform', event.transform);
            });
            
        this.svg.call(zoom);
        
        // Initialize force simulation
        this.simulation = d3.forceSimulation()
            .force('link', d3.forceLink().id(d => d.id).distance(100))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(this.width / 2, this.height / 2))
            .force('collision', d3.forceCollide().radius(30));
            
        // Create tooltip
        this.tooltip = d3.select('body')
            .append('div')
            .attr('class', 'agent-tooltip')
            .style('opacity', 0)
            .style('position', 'absolute')
            .style('background', 'rgba(0, 0, 0, 0.9)')
            .style('color', '#fff')
            .style('padding', '10px')
            .style('border', '1px solid #00ff41')
            .style('border-radius', '5px')
            .style('font-family', 'monospace')
            .style('font-size', '12px');
    }
    
    updateData(agentData) {
        // Convert agent data to nodes and links
        this.nodes = [];
        this.links = [];
        const nodeMap = {};
        
        // Create nodes
        agentData.forEach(agent => {
            const node = {
                id: agent.id,
                name: agent.id,
                generation: agent.generation,
                health: agent.health,
                status: agent.health > 0 ? 'alive' : 'dead',
                location: agent.location,
                files_scanned: agent.files_scanned || 0,
                errors_detected: agent.errors_detected || 0,
                patterns_found: agent.patterns_found || 0
            };
            
            this.nodes.push(node);
            nodeMap[agent.id] = node;
        });
        
        // Create links based on parent-child relationships
        agentData.forEach(agent => {
            if (agent.parent_id && nodeMap[agent.parent_id]) {
                this.links.push({
                    source: agent.parent_id,
                    target: agent.id,
                    type: 'replication'
                });
            }
            
            // Add communication links (mock data for demo)
            if (agent.communications) {
                agent.communications.forEach(comm => {
                    if (nodeMap[comm]) {
                        this.links.push({
                            source: agent.id,
                            target: comm,
                            type: 'communication'
                        });
                    }
                });
            }
        });
        
        this.render();
    }
    
    render() {
        // Clear previous elements
        this.g.selectAll('*').remove();
        
        // Create link elements
        const link = this.g.append('g')
            .selectAll('line')
            .data(this.links)
            .enter().append('line')
            .attr('stroke', d => {
                switch(d.type) {
                    case 'replication': return this.colors.link;
                    case 'communication': return this.colors.communication;
                    case 'knowledge': return this.colors.knowledge;
                    default: return this.colors.link;
                }
            })
            .attr('stroke-opacity', 0.6)
            .attr('stroke-width', d => d.type === 'replication' ? 2 : 1)
            .attr('stroke-dasharray', d => d.type === 'communication' ? '5,5' : null);
            
        // Create node groups
        const node = this.g.append('g')
            .selectAll('g')
            .data(this.nodes)
            .enter().append('g')
            .call(this.drag(this.simulation));
            
        // Add circles for nodes
        node.append('circle')
            .attr('r', d => 20 + Math.sqrt(d.files_scanned) * 0.5)
            .attr('fill', d => {
                if (d.status === 'dead') return this.colors.dead;
                return this.colors[`generation${Math.min(d.generation, 3)}`];
            })
            .attr('stroke', '#fff')
            .attr('stroke-width', 2)
            .style('cursor', 'pointer');
            
        // Add health indicator
        node.append('circle')
            .attr('r', d => (20 + Math.sqrt(d.files_scanned) * 0.5) * (d.health / 100))
            .attr('fill', 'none')
            .attr('stroke', '#fff')
            .attr('stroke-width', 1)
            .attr('stroke-dasharray', '2,2')
            .attr('opacity', 0.5);
            
        // Add labels
        node.append('text')
            .text(d => d.name)
            .attr('x', 0)
            .attr('y', -25)
            .attr('text-anchor', 'middle')
            .attr('fill', '#fff')
            .style('font-size', '12px')
            .style('font-family', 'monospace');
            
        // Add generation indicator
        node.append('text')
            .text(d => `G${d.generation}`)
            .attr('x', 0)
            .attr('y', 5)
            .attr('text-anchor', 'middle')
            .attr('fill', '#000')
            .style('font-size', '10px')
            .style('font-weight', 'bold');
            
        // Add mouseover effects
        node.on('mouseover', (event, d) => {
            this.tooltip.transition()
                .duration(200)
                .style('opacity', .9);
                
            this.tooltip.html(`
                <strong>${d.name}</strong><br/>
                Generation: ${d.generation}<br/>
                Health: ${d.health.toFixed(1)}%<br/>
                Status: ${d.status}<br/>
                Files Scanned: ${d.files_scanned}<br/>
                Errors: ${d.errors_detected}<br/>
                Patterns: ${d.patterns_found}
            `)
                .style('left', (event.pageX + 10) + 'px')
                .style('top', (event.pageY - 28) + 'px');
        })
        .on('mouseout', () => {
            this.tooltip.transition()
                .duration(500)
                .style('opacity', 0);
        });
        
        // Update simulation
        this.simulation
            .nodes(this.nodes)
            .on('tick', () => {
                link
                    .attr('x1', d => d.source.x)
                    .attr('y1', d => d.source.y)
                    .attr('x2', d => d.target.x)
                    .attr('y2', d => d.target.y);
                    
                node
                    .attr('transform', d => `translate(${d.x},${d.y})`);
            });
            
        this.simulation.force('link')
            .links(this.links);
            
        this.simulation.alpha(1).restart();
    }
    
    drag(simulation) {
        function dragstarted(event, d) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }
        
        function dragged(event, d) {
            d.fx = event.x;
            d.fy = event.y;
        }
        
        function dragended(event, d) {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }
        
        return d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended);
    }
    
    // Add new agent with animation
    addAgent(agentData) {
        const newNode = {
            id: agentData.id,
            name: agentData.id,
            generation: agentData.generation,
            health: 100,
            status: 'alive',
            x: this.width / 2 + (Math.random() - 0.5) * 100,
            y: this.height / 2 + (Math.random() - 0.5) * 100
        };
        
        this.nodes.push(newNode);
        
        if (agentData.parent_id) {
            this.links.push({
                source: agentData.parent_id,
                target: agentData.id,
                type: 'replication'
            });
        }
        
        this.render();
        
        // Add birth animation
        const newNodeElement = this.g.selectAll('g')
            .filter(d => d.id === agentData.id)
            .select('circle');
            
        newNodeElement
            .attr('r', 0)
            .transition()
            .duration(500)
            .attr('r', 20)
            .attr('fill', this.colors[`generation${Math.min(agentData.generation, 3)}`]);
    }
    
    // Update agent health
    updateAgentHealth(agentId, health) {
        const node = this.nodes.find(n => n.id === agentId);
        if (node) {
            node.health = health;
            if (health <= 0) {
                node.status = 'dead';
            }
            
            // Update visual
            this.g.selectAll('g')
                .filter(d => d.id === agentId)
                .select('circle')
                .transition()
                .duration(300)
                .attr('fill', health > 0 ? 
                    this.colors[`generation${Math.min(node.generation, 3)}`] : 
                    this.colors.dead);
        }
    }
    
    // Show communication between agents
    showCommunication(sourceId, targetId) {
        // Create temporary communication link
        const commLink = {
            source: this.nodes.find(n => n.id === sourceId),
            target: this.nodes.find(n => n.id === targetId),
            type: 'communication'
        };
        
        if (commLink.source && commLink.target) {
            // Add animated communication pulse
            const pulse = this.g.append('circle')
                .attr('r', 5)
                .attr('fill', this.colors.communication)
                .attr('cx', commLink.source.x)
                .attr('cy', commLink.source.y);
                
            pulse.transition()
                .duration(1000)
                .attr('cx', commLink.target.x)
                .attr('cy', commLink.target.y)
                .transition()
                .duration(200)
                .attr('r', 20)
                .attr('opacity', 0)
                .remove();
        }
    }
}

// Lineage Tree Visualization
class LineageTree {
    constructor(containerId) {
        this.container = d3.select(containerId);
        this.width = 800;
        this.height = 600;
        this.margin = { top: 20, right: 90, bottom: 30, left: 90 };
        
        this.init();
    }
    
    init() {
        this.svg = this.container
            .append('svg')
            .attr('width', this.width)
            .attr('height', this.height)
            .style('background', '#0a0a0a');
            
        this.g = this.svg.append('g')
            .attr('transform', `translate(${this.margin.left},${this.margin.top})`);
            
        this.tree = d3.tree()
            .size([this.height - this.margin.top - this.margin.bottom, 
                   this.width - this.margin.left - this.margin.right]);
    }
    
    updateData(agentData) {
        // Build hierarchy from agent data
        const root = this.buildHierarchy(agentData);
        
        if (!root) return;
        
        const treeData = this.tree(d3.hierarchy(root));
        
        // Clear previous
        this.g.selectAll('*').remove();
        
        // Links
        this.g.selectAll('.link')
            .data(treeData.links())
            .enter().append('path')
            .attr('class', 'link')
            .attr('fill', 'none')
            .attr('stroke', '#333')
            .attr('stroke-width', 2)
            .attr('d', d3.linkHorizontal()
                .x(d => d.y)
                .y(d => d.x));
                
        // Nodes
        const node = this.g.selectAll('.node')
            .data(treeData.descendants())
            .enter().append('g')
            .attr('class', 'node')
            .attr('transform', d => `translate(${d.y},${d.x})`);
            
        node.append('circle')
            .attr('r', 10)
            .attr('fill', d => d.data.health > 0 ? '#00ff41' : '#666');
            
        node.append('text')
            .attr('dy', '.35em')
            .attr('x', d => d.children ? -13 : 13)
            .style('text-anchor', d => d.children ? 'end' : 'start')
            .style('fill', '#fff')
            .style('font-size', '12px')
            .text(d => d.data.name);
    }
    
    buildHierarchy(agentData) {
        // Find root agents (no parent)
        const roots = agentData.filter(a => !a.parent_id);
        if (roots.length === 0) return null;
        
        // Build tree structure
        const buildNode = (agent) => {
            const children = agentData
                .filter(a => a.parent_id === agent.id)
                .map(child => buildNode(child));
                
            return {
                name: agent.id,
                health: agent.health,
                generation: agent.generation,
                children: children.length > 0 ? children : null
            };
        };
        
        // If multiple roots, create a virtual root
        if (roots.length === 1) {
            return buildNode(roots[0]);
        } else {
            return {
                name: 'Colony',
                health: 100,
                generation: -1,
                children: roots.map(r => buildNode(r))
            };
        }
    }
}