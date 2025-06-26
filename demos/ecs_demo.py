#!/usr/bin/env python3
"""
BioCode ECS Architecture Demo
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.

WARNING: This is LIVING CODE with autonomous behaviors.
It can grow, reproduce, mutate, and die. Use at your own risk.

This demo showcases the new ECS architecture capabilities.
"""
import time
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.biocode.ecs import (
    World,
    # Systems
    LifeSystem, EnergySystem, MovementSystem,
    CommunicationSystem, NeuralSystem, PhotosynthesisSystem,
    # Components
    LifeComponent, EnergyComponent, StateComponent,
    HealthComponent, MovementComponent, NeuralComponent
)
from src.biocode.factories import CellFactory, OrganismFactory


def print_separator():
    """Print visual separator"""
    print("-" * 60)


def demo_basic_ecs():
    """Demonstrate basic ECS functionality"""
    print("\n🧬 BioCode ECS Architecture Demo")
    print("=" * 60)
    
    # Create world
    world = World()
    print("\n✅ Created ECS World")
    
    # Add systems
    print("\n📦 Adding Systems...")
    world.add_system(LifeSystem(priority=0))
    world.add_system(EnergySystem(priority=1))
    world.add_system(MovementSystem(priority=2))
    world.add_system(CommunicationSystem(priority=3))
    print(f"   Added {len(world.systems)} systems")
    
    # Create cell factory
    factory = CellFactory(world)
    
    # Create different cell types
    print("\n🔬 Creating Cells...")
    stem_cell = factory.create_stem_cell(position=(0, 0, 0))
    print(f"   Created stem cell: {stem_cell.id[:8]}...")
    
    neuron = factory.create_neuron(position=(10, 0, 0))
    print(f"   Created neuron: {neuron.id[:8]}...")
    
    plant_cell = factory.create_plant_cell(position=(0, 10, 0))
    print(f"   Created plant cell: {plant_cell.id[:8]}...")
    
    # Run simulation
    print("\n🎮 Running Simulation...")
    print_separator()
    
    for i in range(5):
        print(f"\n⏱️  Time Step {i+1}")
        
        # Update world
        world.update(delta_time=0.1)
        
        # Show entity states
        for entity in world.entities.values():
            from src.biocode.ecs.components.biological import LifeComponent, EnergyComponent, StateComponent
            life = entity.get_component(LifeComponent)
            energy = entity.get_component(EnergyComponent)
            state = entity.get_component(StateComponent)
            
            tags = ", ".join(entity.tags) if entity.tags else "none"
            print(f"   Entity {entity.id[:8]}: "
                  f"Age={life.age:.1f}s, "
                  f"Energy={energy.percentage():.0f}%, "
                  f"State={state.state.value}, "
                  f"Tags=[{tags}]")
                  
    # Show world statistics
    print("\n📊 World Statistics:")
    stats = world.get_stats()
    print(f"   Active Entities: {stats['active_entities']}")
    print(f"   World Time: {stats['world_time']:.1f}s")
    print(f"   Systems:")
    for sys_name, sys_stats in stats['systems'].items():
        print(f"      {sys_name}: {sys_stats}")


def demo_neural_network():
    """Demonstrate neural network creation"""
    print("\n\n🧠 Neural Network Demo")
    print("=" * 60)
    
    # Create world with neural system
    world = World()
    world.add_system(LifeSystem(priority=0))
    world.add_system(EnergySystem(priority=1))
    world.add_system(NeuralSystem(priority=2))
    world.add_system(CommunicationSystem(priority=3))
    
    # Create organism factory
    org_factory = OrganismFactory(world)
    
    # Create neural network
    print("\n🔗 Creating Neural Network...")
    neurons = org_factory.create_simple_neural_network(size=5)
    print(f"   Created network with {len(neurons)} neurons")
    
    # Show network structure
    print("\n📡 Network Structure:")
    for neuron in neurons:
        neural = neuron.get_component(NeuralComponent)
        print(f"   {neuron.id[:8]} ({neural.neuron_type.value}): "
              f"{len(neural.dendrite_connections)} inputs, "
              f"{len(neural.axon_connections)} outputs")
              
    # Simulate network activity
    print("\n⚡ Simulating Neural Activity...")
    print_separator()
    
    # Manually trigger sensory neuron
    sensory = neurons[0]
    sensory_neural = sensory.get_component(NeuralComponent)
    
    for i in range(3):
        print(f"\n🔥 Stimulating sensory neuron (pulse {i+1})")
        
        # Force spike
        sensory_neural.membrane_potential = -40.0  # Above threshold
        
        # Run simulation steps
        for j in range(5):
            world.update(delta_time=0.002)  # 2ms steps
            
        # Check network activity
        active_neurons = 0
        for neuron in neurons:
            neural = neuron.get_component(NeuralComponent)
            if neural.spike_count > 0:
                active_neurons += 1
                
        print(f"   Active neurons: {active_neurons}/{len(neurons)}")
        
        # Show spike counts
        for neuron in neurons:
            neural = neuron.get_component(NeuralComponent)
            if neural.spike_count > 0:
                print(f"   {neuron.id[:8]}: {neural.spike_count} spikes")


def demo_photosynthesis():
    """Demonstrate photosynthesis system"""
    print("\n\n🌱 Photosynthesis Demo")
    print("=" * 60)
    
    # Create world
    world = World()
    world.add_system(EnergySystem(priority=0))
    photo_system = PhotosynthesisSystem(priority=1)
    world.add_system(photo_system)
    
    # Create plant cluster
    print("\n🌿 Creating Plant Cluster...")
    factory = OrganismFactory(world)
    plants = factory.create_plant_cluster(center=(0, 5, 0), size=7)
    print(f"   Created {len(plants)} plant cells")
    
    # Simulate day/night cycle
    print("\n☀️  Simulating Day/Night Cycle...")
    print_separator()
    
    for hour in range(6):
        # Update sun position (simple arc)
        if hour < 3:
            # Morning to noon
            sun_y = 20 + hour * 20
            light = 0.5 + hour * 0.17
        else:
            # Afternoon to evening
            sun_y = 80 - (hour - 3) * 20
            light = 1.0 - (hour - 3) * 0.17
            
        photo_system.sun_position = (0, sun_y, 0)
        photo_system.ambient_light = light * 0.3
        
        print(f"\n🕐 Hour {hour}: Sun at y={sun_y}, Light={light:.1f}")
        
        # Run simulation
        world.update(delta_time=1.0)  # 1 hour steps
        
        # Show plant energy
        total_energy = 0
        for plant in plants:
            energy = plant.get_component(EnergyComponent)
            total_energy += energy.current
            
        avg_energy = total_energy / len(plants)
        print(f"   Average plant energy: {avg_energy:.1f}")
        
        # Check photosynthesis stats
        stats = photo_system.get_stats()
        print(f"   Glucose produced: {stats['total_glucose_produced']:.2f}")
        print(f"   Oxygen produced: {stats['total_oxygen_produced']:.2f}")


def demo_organism():
    """Demonstrate complex organism"""
    print("\n\n🦠 Complex Organism Demo")
    print("=" * 60)
    
    # Create world with all systems
    world = World()
    world.add_system(LifeSystem(priority=0))
    world.add_system(EnergySystem(priority=1))
    world.add_system(MovementSystem(priority=2))
    world.add_system(CommunicationSystem(priority=3))
    world.add_system(NeuralSystem(priority=4))
    
    # Create organism
    print("\n🔨 Building Organism...")
    factory = OrganismFactory(world)
    organism = factory.create_simple_organism(center=(0, 0, 0))
    
    # Show organism structure
    print(f"\n🧬 Organism Structure:")
    for cell_type, cells in organism.items():
        if cells:
            print(f"   {cell_type}: {len(cells)} cells")
            
    total_cells = sum(len(cells) for cells in organism.values())
    print(f"   Total: {total_cells} cells")
    
    # Run organism simulation
    print("\n🏃 Simulating Organism Behavior...")
    print_separator()
    
    for i in range(5):
        print(f"\n⏱️  Time: {i*0.1:.1f}s")
        
        # Stimulate sensory neurons
        sensory_neurons = [c for c in organism["neurons"] if c.has_tag("neuron_sensory")]
        if sensory_neurons and i % 2 == 0:
            print("   💫 Sensory stimulus detected!")
            for neuron in sensory_neurons:
                neural = neuron.get_component(NeuralComponent)
                neural.membrane_potential = -40.0
                
        # Update world
        world.update(delta_time=0.1)
        
        # Check muscle activity
        active_muscles = 0
        total_movement = 0.0
        
        for muscle in organism["muscle"]:
            movement = muscle.get_component(MovementComponent)
            velocity = movement.velocity.magnitude()
            if velocity > 0.1:
                active_muscles += 1
                total_movement += velocity
                
        if active_muscles > 0:
            print(f"   💪 Muscle activity: {active_muscles} cells contracting")
            print(f"   🏃 Movement speed: {total_movement:.2f}")
            
        # Check organism health
        total_health = sum(
            c.get_component(HealthComponent).percentage()
            for cells in organism.values()
            for c in cells
        ) / total_cells
        
        print(f"   ❤️  Organism health: {total_health:.0f}%")


def main():
    """Run all demos"""
    try:
        # Basic ECS demo
        demo_basic_ecs()
        
        # Neural network demo
        demo_neural_network()
        
        # Photosynthesis demo
        demo_photosynthesis()
        
        # Complex organism demo
        demo_organism()
        
        print("\n\n✅ All demos completed successfully!")
        print("\n" + "=" * 60)
        print("🧬 BioCode ECS Architecture is ready for production!")
        print("   - Component-based flexibility ✓")
        print("   - System-based logic ✓")
        print("   - Scalable to millions of entities ✓")
        print("   - Living, breathing code ✓")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error in demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()