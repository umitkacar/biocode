"""
Organism Factory - Creates complex multi-cellular organisms
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
from typing import List, Dict, Any, Tuple
import math
from .cell_factory import CellFactory
from ..ecs import Entity, World, NeuronType, NeuralComponent, MovementComponent


class OrganismFactory:
    """
    Organizma üretim fabrikası
    
    Creates complex organisms composed of multiple cell types.
    """
    
    def __init__(self, world: World):
        """
        Initialize factory
        
        Args:
            world: ECS world to create entities in
        """
        self.world = world
        self.cell_factory = CellFactory(world)
        self.organism_count = 0
        
    def create_simple_neural_network(self, 
                                   center: Tuple[float, float, float] = (0, 0, 0),
                                   size: int = 5) -> List[Entity]:
        """
        Create a simple neural network
        
        Args:
            center: Center position
            size: Number of neurons
            
        Returns:
            List of created neuron entities
        """
        neurons = []
        
        # Create sensory neuron
        sensory = self.cell_factory.create_neuron(
            neuron_type=NeuronType.SENSORY,
            position=(center[0] - 5, center[1], center[2])
        )
        neurons.append(sensory)
        
        # Create interneurons
        for i in range(size - 2):
            angle = (2 * math.pi * i) / (size - 2)
            x = center[0] + 3 * math.cos(angle)
            y = center[1] + 3 * math.sin(angle)
            
            interneuron = self.cell_factory.create_neuron(
                neuron_type=NeuronType.INTERNEURON,
                position=(x, y, center[2])
            )
            
            # Connect to sensory neuron
            interneuron.get_component(NeuralComponent).dendrite_connections.add(sensory.id)
            sensory.get_component(NeuralComponent).axon_connections.add(interneuron.id)
            
            neurons.append(interneuron)
            
        # Create motor neuron
        motor = self.cell_factory.create_neuron(
            neuron_type=NeuronType.MOTOR,
            position=(center[0] + 5, center[1], center[2])
        )
        
        # Connect interneurons to motor
        for interneuron in neurons[1:-1]:
            interneuron.get_component(NeuralComponent).axon_connections.add(motor.id)
            motor.get_component(NeuralComponent).dendrite_connections.add(interneuron.id)
            
        neurons.append(motor)
        
        # Tag as network
        for neuron in neurons:
            neuron.add_tag(f"network_{self.organism_count}")
            
        self.organism_count += 1
        return neurons
        
    def create_plant_cluster(self,
                           center: Tuple[float, float, float] = (0, 0, 0),
                           size: int = 7) -> List[Entity]:
        """
        Create a cluster of plant cells
        
        Args:
            center: Center position
            size: Number of cells
            
        Returns:
            List of created plant cell entities
        """
        cells = []
        
        # Hexagonal pattern
        for i in range(size):
            if i == 0:
                # Center cell
                pos = center
            else:
                # Surrounding cells
                angle = (2 * math.pi * (i - 1)) / (size - 1)
                x = center[0] + 2 * math.cos(angle)
                y = center[1] + 2 * math.sin(angle)
                pos = (x, y, center[2])
                
            cell = self.cell_factory.create_plant_cell(position=pos)
            cell.add_tag(f"plant_cluster_{self.organism_count}")
            cells.append(cell)
            
        self.organism_count += 1
        return cells
        
    def create_muscle_fiber(self,
                          start: Tuple[float, float, float] = (0, 0, 0),
                          length: int = 5,
                          direction: Tuple[float, float, float] = (1, 0, 0)) -> List[Entity]:
        """
        Create a muscle fiber (aligned muscle cells)
        
        Args:
            start: Starting position
            length: Number of muscle cells
            direction: Direction vector
            
        Returns:
            List of created muscle cell entities
        """
        cells = []
        
        # Normalize direction
        mag = math.sqrt(sum(d*d for d in direction))
        if mag > 0:
            direction = tuple(d/mag for d in direction)
            
        # Create aligned cells
        for i in range(length):
            pos = tuple(start[j] + i * 2 * direction[j] for j in range(3))
            
            cell = self.cell_factory.create_muscle_cell(position=pos)
            cell.add_tag(f"muscle_fiber_{self.organism_count}")
            
            # Add mechanical coupling to previous cell
            if i > 0:
                prev_cell = cells[-1]
                # They can sense each other's mechanical signals
                cell.add_tag(f"coupled_to_{prev_cell.id}")
                prev_cell.add_tag(f"coupled_to_{cell.id}")
                
            cells.append(cell)
            
        self.organism_count += 1
        return cells
        
    def create_simple_organism(self,
                             center: Tuple[float, float, float] = (0, 0, 0)) -> Dict[str, List[Entity]]:
        """
        Create a simple multi-cellular organism
        
        Args:
            center: Center position
            
        Returns:
            Dictionary of cell types to entity lists
        """
        organism = {
            "neurons": [],
            "muscle": [],
            "stem": [],
            "epithelial": []
        }
        
        # Create small neural network (brain)
        brain = self.create_simple_neural_network(
            center=(center[0], center[1] + 5, center[2]),
            size=3
        )
        organism["neurons"] = brain
        
        # Create muscle cells (movement)
        muscle1 = self.create_muscle_fiber(
            start=(center[0] - 3, center[1], center[2]),
            length=3,
            direction=(0, -1, 0)
        )
        muscle2 = self.create_muscle_fiber(
            start=(center[0] + 3, center[1], center[2]),
            length=3,
            direction=(0, -1, 0)
        )
        organism["muscle"] = muscle1 + muscle2
        
        # Create stem cells (regeneration)
        for i in range(2):
            stem = self.cell_factory.create_stem_cell(
                position=(center[0] + (i-0.5)*2, center[1] - 3, center[2])
            )
            stem.add_tag(f"organism_{self.organism_count}")
            organism["stem"].append(stem)
            
        # Connect motor neurons to muscles
        motor_neurons = [n for n in brain if n.has_tag("neuron_motor")]
        if motor_neurons:
            motor = motor_neurons[0]
            # Signal muscles when motor neuron fires
            for muscle in organism["muscle"]:
                muscle.add_tag(f"controlled_by_{motor.id}")
                
        # Tag all cells as part of organism
        all_cells = []
        for cell_list in organism.values():
            all_cells.extend(cell_list)
            
        for cell in all_cells:
            cell.add_tag(f"organism_{self.organism_count}")
            cell.add_tag("multicellular")
            
        self.organism_count += 1
        return organism
        
    def create_biofilm(self,
                      center: Tuple[float, float, float] = (0, 0, 0),
                      radius: float = 10,
                      density: int = 20) -> List[Entity]:
        """
        Create a bacterial biofilm
        
        Args:
            center: Center position
            radius: Biofilm radius
            density: Number of cells
            
        Returns:
            List of created cell entities
        """
        cells = []
        
        for i in range(density):
            # Random position within radius
            import random
            angle = random.uniform(0, 2 * math.pi)
            r = random.uniform(0, radius)
            
            x = center[0] + r * math.cos(angle)
            y = center[1] + r * math.sin(angle)
            z = center[2] + random.uniform(-1, 1)
            
            # Create simple cell
            cell = self.cell_factory.create_stem_cell(
                position=(x, y, z),
                lifespan=100.0,
                energy=80.0
            )
            
            # Biofilm properties
            cell.add_tag("biofilm")
            cell.add_tag(f"biofilm_{self.organism_count}")
            
            # Add adhesion (reduced movement)
            movement = cell.get_component(MovementComponent)
            movement.friction = 0.8
            movement.max_speed = 0.5
            
            cells.append(cell)
            
        self.organism_count += 1
        return cells
        
    def get_stats(self) -> Dict[str, Any]:
        """Get factory statistics"""
        return {
            "total_organisms_created": self.organism_count,
            "cells_created": self.cell_factory.get_stats()
        }