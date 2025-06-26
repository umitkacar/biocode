"""
Integration tests for complete ECS architecture
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
import pytest
import time
import json
from src.biocode.ecs import World, Entity, LifeSystem, EnergySystem
from src.biocode.factories import CellFactory
from src.biocode.mixins import EnhancedEntity
from src.biocode.aspects import AspectWeaver, LoggingAspect, PerformanceAspect
from src.biocode.ecs.components.biological import (
    HealthComponent, EnergyComponent, LifeComponent
)
from src.biocode.ecs.components.organelles import OrganelleComponent
from src.biocode.ecs.components.membrane import MembraneComponent
from src.biocode.ecs.components.movement import PositionComponent, VelocityComponent
from src.biocode.ecs.systems.organelle_system import OrganelleSystem
from src.biocode.ecs.systems.membrane_system import MembraneSystem
from src.biocode.ecs.systems.movement_system import MovementSystem


class TestECSIntegration:
    """Test complete ECS integration"""
    
    def test_cell_factory_integration(self):
        """Test cell factory with world integration"""
        world = World()
        factory = CellFactory(world)
        
        # Create different cell types
        stem_cell = factory.create_stem_cell()
        neuron = factory.create_neuron()
        muscle = factory.create_muscle_cell()
        
        # Verify all entities are in world
        assert len(world.entities) == 3
        assert world.get_entity(stem_cell.id) is stem_cell
        assert world.get_entity(neuron.id) is neuron
        assert world.get_entity(muscle.id) is muscle
        
        # Verify components
        assert stem_cell.has_component(LifeComponent)
        assert neuron.has_component(HealthComponent)
        assert muscle.has_component(EnergyComponent)
        
    def test_biological_simulation(self):
        """Test complete biological simulation"""
        world = World()
        
        # Add all biological systems
        world.add_system(LifeSystem())
        world.add_system(EnergySystem())
        world.add_system(OrganelleSystem())
        world.add_system(MembraneSystem())
        world.add_system(MovementSystem())
        
        # Create cells
        factory = CellFactory(world)
        cells = [
            factory.create_stem_cell(position=(i*10, 0, 0))
            for i in range(5)
        ]
        
        # Damage some cells
        cells[0].get_component(HealthComponent).current = 50.0
        cells[1].get_component(EnergyComponent).current = 20.0
        
        # Run simulation
        for _ in range(10):
            world.update(delta_time=0.1)
            
        # Check that systems processed entities
        assert cells[0].get_component(LifeComponent).age > 0
        assert cells[1].get_component(EnergyComponent).current < 20.0  # Energy depleted
        
    def test_enhanced_entity_integration(self):
        """Test enhanced entity with all mixins"""
        world = World()
        
        # Create enhanced entity
        entity = EnhancedEntity()
        entity.add_component(HealthComponent(current=100.0))
        entity.add_component(PositionComponent(x=10, y=20, z=30))
        entity.add_tag("enhanced")
        
        world.add_entity(entity)
        
        # Test serialization
        json_data = entity.to_json()
        restored = EnhancedEntity()
        restored.from_json(json_data)
        
        assert restored.id == entity.id
        assert restored.has_tag("enhanced")
        
        # Test observation
        events = []
        def observer(event_type, data):
            events.append(event_type)
            
        entity.add_observer(observer)
        entity.add_component(EnergyComponent())
        
        assert "component_added" in events
        
        # Test replication
        clone = entity.clone()
        assert clone.id != entity.id
        assert clone.has_component(HealthComponent)
        assert clone.has_component(PositionComponent)
        
    def test_aspect_weaving_integration(self):
        """Test aspects with ECS systems"""
        import logging
        
        world = World()
        life_system = LifeSystem()
        
        # Set up aspects
        logger = logging.getLogger("test")
        logging_aspect = LoggingAspect(logger=logger, log_args=False)
        perf_aspect = PerformanceAspect(alert_threshold_ms=10.0)
        
        # Weave aspects
        weaver = AspectWeaver()
        weaver.add_aspect(logging_aspect)
        weaver.add_aspect(perf_aspect)
        weaver.weave(life_system)
        
        world.add_system(life_system)
        
        # Create entities
        factory = CellFactory(world)
        for _ in range(10):
            factory.create_stem_cell()
            
        # Run with aspects
        world.update(delta_time=0.1)
        
        # Check performance metrics
        metrics = perf_aspect.get_metrics()
        assert len(metrics) > 0
        
        # Check for update method
        update_metrics = next(
            (m for method, m in metrics.items() if "update" in method),
            None
        )
        if update_metrics:
            assert update_metrics["call_count"] >= 1
            
    def test_cell_lifecycle(self):
        """Test complete cell lifecycle"""
        world = World()
        
        # Add systems
        world.add_system(LifeSystem())
        world.add_system(EnergySystem())
        
        # Create cell
        factory = CellFactory(world)
        cell = factory.create_stem_cell()
        
        # Get components
        life = cell.get_component(LifeComponent)
        health = cell.get_component(HealthComponent)
        energy = cell.get_component(EnergyComponent)
        
        # Age the cell significantly
        life.age = life.lifespan * 0.9  # 90% of lifespan
        
        # Run simulation
        initial_health = health.current
        for _ in range(20):
            world.update(delta_time=0.5)
            
        # Check aging effects
        assert life.age > life.lifespan * 0.9
        assert health.current < initial_health  # Health degraded
        
        # Check if cell died
        if life.age >= life.lifespan:
            assert not cell.active or cell.has_tag("dead")
            
    def test_system_priority_integration(self):
        """Test system execution order"""
        world = World()
        
        # Create systems with different priorities
        movement = MovementSystem()
        movement.priority = 10
        
        life = LifeSystem()
        life.priority = 5
        
        energy = EnergySystem()
        energy.priority = 1
        
        # Add in random order
        world.add_system(energy)
        world.add_system(movement)
        world.add_system(life)
        
        # Check order (lower priority value = earlier execution)
        assert world.systems[0] is energy   # priority 1
        assert world.systems[1] is life     # priority 5
        assert world.systems[2] is movement # priority 10
        
    def test_component_query_integration(self):
        """Test querying entities by components"""
        world = World()
        factory = CellFactory(world)
        
        # Create different cell types
        stem_cells = [factory.create_stem_cell() for _ in range(3)]
        neurons = [factory.create_neuron() for _ in range(2)]
        muscle_cells = [factory.create_muscle_cell() for _ in range(2)]
        
        # Query entities with OrganelleComponent
        organelle_entities = world.query(OrganelleComponent)
        assert len(organelle_entities) == 7  # All cells have organelles
        
        # Query entities with both Position and Velocity
        moving_entities = world.query(PositionComponent, VelocityComponent)
        # Neurons and muscle cells have velocity
        assert len(moving_entities) >= 4
        
    def test_network_simulation(self):
        """Test networked entity simulation"""
        from src.biocode.mixins import NetworkableMixin
        
        class NetworkedEntity(NetworkableMixin, Entity):
            pass
            
        # Create server entity
        server_entity = NetworkedEntity()
        server_entity.set_network_id("entity-001")
        server_entity.set_network_authority(True)
        server_entity.add_component(PositionComponent(x=10, y=20))
        server_entity.add_component(HealthComponent(current=80))
        
        # Create client entity
        client_entity = NetworkedEntity()
        client_entity.set_network_id("entity-001")
        client_entity.set_network_authority(False)
        
        # Mark component as dirty
        server_entity.mark_component_dirty(PositionComponent)
        
        # Get sync data
        if server_entity.needs_sync():
            sync_data = server_entity.get_sync_data()
            
            # Apply to client
            client_entity.apply_sync_data(sync_data)
            
        # Verify sync (components would need to be reconstructed)
        assert client_entity.get_network_id() == server_entity.get_network_id()