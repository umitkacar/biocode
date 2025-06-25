"""
Integrated Digital Life Simulation Demo
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.evolution.integrated_simulation import (
    IntegratedLifeSimulation, 
    EnvironmentalConditions,
    AdvancedGenome,
    AdvancedCell
)
import matplotlib.pyplot as plt
import numpy as np


def demo_basic_simulation():
    """Run a basic simulation demo"""
    print("=== BioCode Integrated Life Simulation Demo ===\n")
    
    # Create small simulation
    sim = IntegratedLifeSimulation(
        initial_population=20,
        world_size=(50, 50),
        enable_sandbox=False  # Disable for demo
    )
    
    print(f"Starting with {len(sim.population)} cells")
    print(f"Initial environment: Temp={sim.environment.temperature:.1f}°C, Resources={sim.environment.resource_level:.1f}%\n")
    
    # Run for 100 steps
    for i in range(100):
        sim.step()
        
        if i % 20 == 0:
            print(f"Step {i}: Population={len(sim.population)}, Avg Energy={np.mean([c.energy for c in sim.population]):.1f}")
    
    # Final report
    print("\n" + sim.generate_report())
    
    return sim


def demo_environmental_adaptation():
    """Demonstrate adaptation to changing environment"""
    print("\n=== Environmental Adaptation Demo ===\n")
    
    # Create population with specific traits
    sim = IntegratedLifeSimulation(initial_population=30, enable_sandbox=False)
    
    print("Phase 1: Normal conditions")
    for _ in range(50):
        sim.step()
    
    initial_metabolism = np.mean([c.metabolic_rate for c in sim.population])
    print(f"Average metabolism: {initial_metabolism:.3f}")
    
    # Change environment drastically
    print("\nPhase 2: Extreme heat")
    sim.environment.temperature = 35.0  # Hot environment
    
    for _ in range(100):
        sim.step()
    
    adapted_metabolism = np.mean([c.metabolic_rate for c in sim.population])
    print(f"Average metabolism after heat: {adapted_metabolism:.3f}")
    print(f"Change: {(adapted_metabolism - initial_metabolism) / initial_metabolism * 100:.1f}%")
    
    return sim


def demo_social_behavior():
    """Demonstrate collective intelligence and social networks"""
    print("\n=== Social Behavior Demo ===\n")
    
    # Create population with varying social tendencies
    sim = IntegratedLifeSimulation(initial_population=25, enable_sandbox=False)
    
    # Track social metrics
    social_history = []
    
    for i in range(150):
        sim.step()
        
        if i % 30 == 0:
            total_connections = sum(len(c.social_network) for c in sim.population)
            avg_connections = total_connections / len(sim.population) if sim.population else 0
            
            social_history.append({
                'step': i,
                'connections': total_connections,
                'avg_connections': avg_connections,
                'population': len(sim.population)
            })
            
            print(f"Step {i}: Total connections={total_connections}, Avg per cell={avg_connections:.1f}")
    
    # Analyze collective knowledge
    print(f"\nCollective knowledge entries: {len(sim.collective_knowledge)}")
    
    # Count knowledge types
    knowledge_types = {}
    for k in sim.collective_knowledge:
        knowledge_types[k['type']] = knowledge_types.get(k['type'], 0) + 1
    
    print("Knowledge distribution:")
    for ktype, count in knowledge_types.items():
        print(f"  {ktype}: {count}")
    
    return sim, social_history


def demo_genetic_evolution():
    """Demonstrate genetic evolution and mutation"""
    print("\n=== Genetic Evolution Demo ===\n")
    
    # Create founder population with identical genomes
    founder_genome = AdvancedGenome()
    
    sim = IntegratedLifeSimulation(initial_population=0, enable_sandbox=False)
    
    # Add identical founders
    for _ in range(10):
        cell = AdvancedCell(founder_genome)
        sim.population.append(cell)
    
    print("Starting with genetically identical population")
    
    # Add radiation to increase mutations
    sim.environment.radiation = 20.0
    
    # Track genetic diversity
    diversity_history = []
    
    for gen in range(10):
        # Run generation
        for _ in range(50):
            sim.step()
        
        # Measure diversity
        unique_genomes = set()
        for cell in sim.population:
            genome_hash = hash(str(cell.genome.chromosomes))
            unique_genomes.add(genome_hash)
        
        diversity = len(unique_genomes) / len(sim.population) if sim.population else 0
        diversity_history.append(diversity)
        
        print(f"Generation {gen + 1}: Population={len(sim.population)}, Unique genomes={len(unique_genomes)}, Diversity={diversity:.3f}")
    
    return sim, diversity_history


def visualize_demo_results(basic_sim, adaptation_sim, social_data, diversity_data):
    """Create visualization of demo results"""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # 1. Population dynamics
    ax = axes[0, 0]
    if basic_sim.stats_history:
        steps = [s['time_step'] for s in basic_sim.stats_history]
        pop_sizes = [s['population_size'] for s in basic_sim.stats_history]
        ax.plot(steps, pop_sizes, 'b-', linewidth=2)
        ax.set_xlabel('Time Steps')
        ax.set_ylabel('Population Size')
        ax.set_title('Population Dynamics')
        ax.grid(True)
    
    # 2. Environmental adaptation
    ax = axes[0, 1]
    if adaptation_sim.stats_history:
        steps = [s['time_step'] for s in adaptation_sim.stats_history]
        temps = [s['environment']['temperature'] for s in adaptation_sim.stats_history]
        metabolisms = [s['traits']['metabolism'] for s in adaptation_sim.stats_history]
        
        ax2 = ax.twinx()
        ax.plot(steps, temps, 'r-', label='Temperature')
        ax2.plot(steps, metabolisms, 'g-', label='Avg Metabolism')
        
        ax.set_xlabel('Time Steps')
        ax.set_ylabel('Temperature (°C)', color='r')
        ax2.set_ylabel('Metabolism', color='g')
        ax.set_title('Environmental Adaptation')
    
    # 3. Social network growth
    ax = axes[1, 0]
    if social_data:
        steps = [d['step'] for d in social_data]
        connections = [d['connections'] for d in social_data]
        ax.plot(steps, connections, 'purple', linewidth=2)
        ax.set_xlabel('Time Steps')
        ax.set_ylabel('Total Connections')
        ax.set_title('Social Network Growth')
        ax.grid(True)
    
    # 4. Genetic diversity
    ax = axes[1, 1]
    if diversity_data:
        generations = list(range(1, len(diversity_data) + 1))
        ax.plot(generations, diversity_data, 'orange', linewidth=2, marker='o')
        ax.set_xlabel('Generation')
        ax.set_ylabel('Genetic Diversity')
        ax.set_title('Evolution of Diversity')
        ax.grid(True)
    
    plt.tight_layout()
    plt.savefig('integrated_simulation_demo_results.png', dpi=150)
    print("\nVisualization saved as 'integrated_simulation_demo_results.png'")
    plt.show()


def main():
    """Run all demos"""
    # Run basic simulation
    basic_sim = demo_basic_simulation()
    
    # Run adaptation demo
    adaptation_sim = demo_environmental_adaptation()
    
    # Run social behavior demo
    social_sim, social_data = demo_social_behavior()
    
    # Run genetic evolution demo
    genetic_sim, diversity_data = demo_genetic_evolution()
    
    # Create visualization
    visualize_demo_results(basic_sim, adaptation_sim, social_data, diversity_data)
    
    print("\n=== Demo Complete ===")
    print("This demonstration showed:")
    print("1. Basic population dynamics")
    print("2. Environmental adaptation through epigenetics")
    print("3. Social network formation and collective learning")
    print("4. Genetic evolution and increasing diversity")
    print("\nThe BioCode system successfully simulates digital life!")


if __name__ == "__main__":
    main()