"""
Unit tests for ECS System
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
import pytest
from src.biocode.ecs import System, Entity, Component


class HealthComponent(Component):
    def __init__(self, current: float = 100.0, maximum: float = 100.0):
        self.current = current
        self.maximum = maximum


class PositionComponent(Component):
    def __init__(self, x: float = 0.0, y: float = 0.0):
        self.x = x
        self.y = y


class VelocityComponent(Component):
    def __init__(self, dx: float = 0.0, dy: float = 0.0):
        self.dx = dx
        self.dy = dy


class MovementSystem(System):
    """Test movement system"""
    
    def required_components(self):
        return (PositionComponent, VelocityComponent)
        
    def process(self, entity, delta_time):
        pos = entity.get_component(PositionComponent)
        vel = entity.get_component(VelocityComponent)
        
        pos.x += vel.dx * delta_time
        pos.y += vel.dy * delta_time


class HealthSystem(System):
    """Test health system"""
    
    def __init__(self):
        super().__init__()
        self.processed_entities = []
        
    def required_components(self):
        return (HealthComponent,)
        
    def process(self, entity, delta_time):
        self.processed_entities.append(entity.id)
        health = entity.get_component(HealthComponent)
        # Simple regeneration
        if health.current < health.maximum:
            health.current = min(health.current + 10 * delta_time, health.maximum)


class TestSystem:
    """Test System base class"""
    
    def test_system_creation(self):
        """Test creating a system"""
        system = MovementSystem()
        assert system.enabled is True
        assert system.priority == 0
        
    def test_system_priority(self):
        """Test system priority"""
        system1 = MovementSystem()
        system2 = HealthSystem()
        
        system1.priority = 10
        system2.priority = 5
        
        assert system1.priority > system2.priority
        
    def test_system_enable_disable(self):
        """Test enabling/disabling system"""
        system = MovementSystem()
        
        system.enabled = False
        assert system.enabled is False
        
        system.enabled = True
        assert system.enabled is True
        
    def test_get_required_components(self):
        """Test getting required components"""
        system = MovementSystem()
        required = system.required_components()
        
        assert PositionComponent in required
        assert VelocityComponent in required
        assert len(required) == 2
        
    def test_should_process_entity(self):
        """Test entity filtering"""
        system = MovementSystem()
        
        # Entity with all required components
        entity1 = Entity()
        entity1.add_component(PositionComponent())
        entity1.add_component(VelocityComponent())
        
        # Entity missing VelocityComponent
        entity2 = Entity()
        entity2.add_component(PositionComponent())
        
        # Entity with extra components
        entity3 = Entity()
        entity3.add_component(PositionComponent())
        entity3.add_component(VelocityComponent())
        entity3.add_component(HealthComponent())
        
        assert system.matches_entity(entity1) is True
        assert system.matches_entity(entity2) is False
        assert system.matches_entity(entity3) is True
        
    def test_should_process_inactive_entity(self):
        """Test that inactive entities are not processed"""
        system = MovementSystem()
        
        entity = Entity()
        entity.add_component(PositionComponent())
        entity.add_component(VelocityComponent())
        entity.active = False
        
        assert system.matches_entity(entity) is False
        
    def test_process_entity(self):
        """Test processing an entity"""
        system = MovementSystem()
        
        entity = Entity()
        pos = PositionComponent(x=10.0, y=20.0)
        vel = VelocityComponent(dx=5.0, dy=-3.0)
        entity.add_component(pos)
        entity.add_component(vel)
        
        # Process for 1 second
        system.process(entity, 1.0)
        
        assert pos.x == 15.0  # 10 + 5*1
        assert pos.y == 17.0  # 20 + (-3)*1
        
    def test_system_with_state(self):
        """Test system that maintains state"""
        system = HealthSystem()
        
        entity1 = Entity()
        entity1.add_component(HealthComponent(current=50.0))
        
        entity2 = Entity()
        entity2.add_component(HealthComponent(current=75.0))
        
        system.process(entity1, 0.5)
        system.process(entity2, 0.5)
        
        assert len(system.processed_entities) == 2
        assert entity1.id in system.processed_entities
        assert entity2.id in system.processed_entities
        
    def test_health_regeneration(self):
        """Test health regeneration logic"""
        system = HealthSystem()
        
        entity = Entity()
        health = HealthComponent(current=50.0, maximum=100.0)
        entity.add_component(health)
        
        # Regenerate for 3 seconds
        system.process(entity, 3.0)
        
        assert health.current == 80.0  # 50 + 10*3
        
        # Regenerate more - should cap at maximum
        system.process(entity, 3.0)
        
        assert health.current == 100.0  # Capped at maximum