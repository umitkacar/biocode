#!/usr/bin/env python3
"""
Advanced BioCode ECS Architecture Demo
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.

WARNING: This is LIVING CODE with autonomous behaviors.
It can grow, reproduce, mutate, and die. Use at your own risk.

This demo showcases the complete ECS architecture with:
- Organelles and cellular metabolism
- Membrane transport and signaling
- Infection and immune response
"""
import time
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.biocode.ecs import (
    World,
    # All Systems
    LifeSystem, EnergySystem, MovementSystem,
    CommunicationSystem, NeuralSystem, PhotosynthesisSystem,
    OrganelleSystem, MembraneSystem, InfectionSystem,
    # Components for inspection
    OrganelleComponent, MembraneComponent, InfectionComponent,
    HealthComponent, EnergyComponent, StateComponent, NeuralComponent,
    CommunicationComponent,
    # Enums
    PathogenType, ReceptorType, TransportType, SignalType
)
from src.biocode.factories import CellFactory, OrganismFactory


def print_separator(char="-", length=80):
    """Print visual separator"""
    print(char * length)


def demo_cellular_metabolism():
    """Demonstrate organelle and membrane systems"""
    print("\n🔬 Cellular Metabolism Demo")
    print_separator("=")
    
    # Create world with metabolic systems
    world = World()
    world.add_system(EnergySystem(priority=1))
    world.add_system(OrganelleSystem(priority=2))
    world.add_system(MembraneSystem(priority=3))
    
    # Create different cell types
    factory = CellFactory(world)
    
    print("\n🧫 Creating Cells with Different Metabolic Profiles...")
    
    # High metabolism cell
    muscle = factory.create_muscle_cell(position=(0, 0, 0))
    print(f"   Muscle cell: {muscle.id[:8]}... (500 mitochondria)")
    
    # Normal metabolism cell
    stem = factory.create_stem_cell(position=(10, 0, 0))
    print(f"   Stem cell: {stem.id[:8]}... (100 mitochondria)")
    
    # Photosynthetic cell
    plant = factory.create_plant_cell(position=(0, 10, 0))
    print(f"   Plant cell: {plant.id[:8]}... (photosynthesis)")
    
    # Set environmental conditions
    membrane_sys = world.get_system(MembraneSystem)
    membrane_sys.set_environment_molecule("glucose", 5.0)
    membrane_sys.set_environment_molecule("oxygen", 0.8)
    
    organelle_sys = world.get_system(OrganelleSystem)
    organelle_sys.set_oxygen_level(0.8)
    
    print("\n⚡ Running Metabolic Simulation...")
    print_separator()
    
    for i in range(5):
        print(f"\n⏱️  Time: {i*0.1:.1f}s")
        
        # Update world
        world.update(delta_time=0.1)
        
        # Show cellular metabolism
        for entity in [muscle, stem, plant]:
            organelles = entity.get_component(OrganelleComponent)
            energy = entity.get_component(EnergyComponent)
            membrane = entity.get_component(MembraneComponent)
            
            cell_type = "Muscle" if entity == muscle else "Stem" if entity == stem else "Plant"
            
            print(f"\n   {cell_type} Cell:")
            print(f"      Energy: {energy.percentage():.0f}%")
            print(f"      ATP Production: {organelles.get_total_atp_production(0.8):.1f}/s")
            print(f"      Membrane Integrity: {membrane.integrity*100:.0f}%")
            print(f"      Membrane Potential: {membrane.potential:.1f} mV")
            
            # Show organelle health
            if organelles.mitochondria:
                print(f"      Mitochondria Health: {(1-organelles.mitochondria.damage_level)*100:.0f}%")
                
    # Show system stats
    print("\n📊 Metabolic Statistics:")
    org_stats = organelle_sys.get_stats()
    mem_stats = membrane_sys.get_stats()
    print(f"   Total ATP Produced: {org_stats['total_atp_produced']:.1f}")
    print(f"   Total Molecules Transported: {mem_stats['total_transported']:.1f}")


def demo_infection_response():
    """Demonstrate infection and immune response"""
    print("\n\n🦠 Infection & Immune Response Demo")
    print_separator("=")
    
    # Create world
    world = World()
    world.add_system(LifeSystem(priority=0))
    world.add_system(EnergySystem(priority=1))
    world.add_system(InfectionSystem(priority=2))
    world.add_system(CommunicationSystem(priority=3))
    
    # Create a small tissue
    factory = CellFactory(world)
    
    print("\n🧬 Creating Tissue...")
    cells = []
    for i in range(5):
        cell = factory.create_stem_cell(position=(i*2, 0, 0))
        cells.append(cell)
    print(f"   Created {len(cells)} healthy cells")
    
    # Infect patient zero
    infection_sys = world.get_system(InfectionSystem)
    patient_zero = cells[2]  # Middle cell
    
    print(f"\n💉 Infecting cell {patient_zero.id[:8]}... with virus")
    infection_sys.introduce_pathogen(patient_zero, PathogenType.VIRUS, "flu_h1n1")
    
    print("\n🏥 Monitoring Infection Spread...")
    print_separator()
    
    for step in range(10):
        print(f"\n⏱️  Time: {step*0.5:.1f}s")
        
        # Update world
        world.update(delta_time=0.5)
        
        # Count infected cells
        infected_count = 0
        total_pathogen_load = 0.0
        
        for cell in cells:
            infection = cell.get_component(InfectionComponent)
            health = cell.get_component(HealthComponent)
            
            if infection.infected:
                infected_count += 1
                total_pathogen_load += infection.pathogen_load
                
                # Show infected cell details
                print(f"   Cell {cell.id[:8]}: INFECTED")
                print(f"      Pathogen Load: {infection.pathogen_load:.1f}")
                print(f"      Inflammation: {infection.inflammation_level*100:.0f}%")
                print(f"      Health: {health.percentage():.0f}%")
                
                # Show antibodies
                if infection.antibodies:
                    print(f"      Antibodies: {len(infection.antibodies)}")
                    for ab_name, antibody in infection.antibodies.items():
                        print(f"         {ab_name}: concentration={antibody.concentration:.1f}")
                        
        print(f"\n   Summary: {infected_count}/{len(cells)} cells infected")
        print(f"   Total Pathogen Load: {total_pathogen_load:.1f}")
        
        # Check for recovery
        if infected_count == 0 and step > 0:
            print("\n   ✅ All cells have cleared the infection!")
            break
            
    # Show final statistics
    stats = infection_sys.get_stats()
    print(f"\n📊 Infection Statistics:")
    print(f"   Total Infections: {stats['total_infections']}")
    print(f"   Total Cleared: {stats['total_cleared']}")
    print(f"   Cure Rate: {stats['cure_rate']*100:.0f}%")


def demo_membrane_signaling():
    """Demonstrate membrane receptors and signaling"""
    print("\n\n📡 Membrane Signaling Demo")
    print_separator("=")
    
    # Create world
    world = World()
    world.add_system(MembraneSystem(priority=0))
    world.add_system(CommunicationSystem(priority=1))
    world.add_system(EnergySystem(priority=2))
    
    # Create cells
    factory = CellFactory(world)
    
    print("\n🔗 Creating Signaling Network...")
    sender = factory.create_stem_cell(position=(0, 0, 0))
    receiver1 = factory.create_stem_cell(position=(5, 0, 0))
    receiver2 = factory.create_stem_cell(position=(0, 5, 0))
    
    print(f"   Sender: {sender.id[:8]}...")
    print(f"   Receiver 1: {receiver1.id[:8]}...")
    print(f"   Receiver 2: {receiver2.id[:8]}...")
    
    print("\n📨 Sending Growth Factor Signal...")
    print_separator()
    
    # Send growth factor signal
    comm = sender.get_component(CommunicationComponent)
    comm.emit_signal(
        signal_type=SignalType.CHEMICAL,
        strength=1.0,
        source_id=sender.id,
        payload={"ligand": "growth_factor", "response": "growth"},
        timestamp=time.time()
    )
    
    # Run simulation
    for i in range(3):
        print(f"\n⏱️  Step {i+1}")
        world.update(delta_time=0.1)
        
        # Check receptor status
        for cell_name, cell in [("Receiver 1", receiver1), ("Receiver 2", receiver2)]:
            membrane = cell.get_component(MembraneComponent)
            
            print(f"\n   {cell_name}:")
            # Check active receptors
            if membrane.active_receptors:
                print(f"      Active Receptors: {list(membrane.active_receptors)}")
            
            # Check for growth signal tag
            if cell.has_tag("growth_signal_received"):
                print(f"      ✅ Growth signal received!")
                
            # Show receptor states
            for receptor_name, receptor in membrane.receptors.items():
                if receptor.occupied:
                    print(f"      {receptor_name}: BOUND (sensitivity={receptor.sensitivity:.2f})")


def demo_complex_organism():
    """Demonstrate a complex organism with all systems"""
    print("\n\n🧬 Complex Living Organism Demo")
    print_separator("=")
    
    # Create world with ALL systems
    world = World()
    world.add_system(LifeSystem(priority=0))
    world.add_system(EnergySystem(priority=1))
    world.add_system(OrganelleSystem(priority=2))
    world.add_system(MembraneSystem(priority=3))
    world.add_system(MovementSystem(priority=4))
    world.add_system(CommunicationSystem(priority=5))
    world.add_system(NeuralSystem(priority=6))
    world.add_system(InfectionSystem(priority=7))
    
    print(f"\n✅ Initialized {len(world.systems)} biological systems")
    
    # Create organism
    factory = OrganismFactory(world)
    
    print("\n🔨 Building Multi-Cellular Organism...")
    organism = factory.create_simple_organism(center=(0, 0, 0))
    
    total_cells = sum(len(cells) for cells in organism.values())
    print(f"   Created organism with {total_cells} cells")
    print(f"   Cell types: {list(organism.keys())}")
    
    # Introduce mild infection
    infection_sys = world.get_system(InfectionSystem)
    if organism["muscle"]:
        target_cell = organism["muscle"][0]
        infection_sys.introduce_pathogen(target_cell, PathogenType.BACTERIA, "mild_bacteria")
        print(f"\n🦠 Introduced bacterial infection to muscle cell")
    
    print("\n🏃 Simulating Living Organism...")
    print_separator()
    
    for step in range(5):
        print(f"\n⏱️  Time: {step*0.2:.1f}s")
        
        # Update world
        world.update(delta_time=0.2)
        
        # Organism health check
        total_health = 0
        infected_cells = 0
        dead_cells = 0
        
        all_cells = []
        for cell_list in organism.values():
            all_cells.extend(cell_list)
            
        for cell in all_cells:
            health = cell.get_component(HealthComponent)
            total_health += health.percentage()
            
            if cell.has_component(InfectionComponent):
                infection = cell.get_component(InfectionComponent)
                if infection.infected:
                    infected_cells += 1
                    
            if cell.has_tag("dead"):
                dead_cells += 1
                
        avg_health = total_health / len(all_cells)
        
        print(f"   Organism Health: {avg_health:.0f}%")
        print(f"   Infected Cells: {infected_cells}")
        print(f"   Dead Cells: {dead_cells}")
        
        # Check specific systems
        if organism["neurons"]:
            neural_activity = sum(
                1 for n in organism["neurons"] 
                if n.get_component(NeuralComponent).spike_count > 0
            )
            if neural_activity > 0:
                print(f"   Neural Activity: {neural_activity} neurons firing")
                
        # Check for immune response
        immune_active = sum(
            1 for c in all_cells
            if c.has_component(InfectionComponent) and 
            c.get_component(InfectionComponent).antibodies
        )
        if immune_active > 0:
            print(f"   Immune Response: {immune_active} cells producing antibodies")


def main():
    """Run all advanced demos"""
    try:
        print("\n" + "=" * 80)
        print("🧬 ADVANCED BIOCODE ECS ARCHITECTURE DEMO")
        print("Demonstrating Complete Cellular Biology Simulation")
        print("=" * 80)
        
        # Run demos
        demo_cellular_metabolism()
        demo_infection_response()
        demo_membrane_signaling()
        demo_complex_organism()
        
        print("\n\n" + "=" * 80)
        print("✅ ADVANCED ECS DEMO COMPLETED!")
        print("\nThe BioCode ECS Architecture now supports:")
        print("   ✓ Complete cellular metabolism")
        print("   ✓ Organelle simulation")
        print("   ✓ Membrane transport and signaling")
        print("   ✓ Infection and immune response")
        print("   ✓ Complex multi-cellular organisms")
        print("   ✓ Emergent biological behaviors")
        print("\n🚀 Ready to beat Codex and ChatGPT!")
        print("=" * 80)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error in demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()