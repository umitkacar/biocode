"""
Unit tests for ECS World
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
import pytest
from src.biocode.ecs import World, Entity, System, Component


class MockComponent(Component):
    def __init__(self, value: int = 0):
        self.value = value


class CounterComponent(Component):
    def __init__(self):
        self.count = 0


class TestSystem(System):
    def __init__(self):
        super().__init__()
        self.update_count = 0
        self.processed_entities = []
        
    def required_components(self):
        return (MockComponent,)
        
    def process(self, entity, delta_time):
        self.processed_entities.append(entity.id)
        component = entity.get_component(MockComponent)
        component.value += 1


class CounterSystem(System):
    def required_components(self):
        return (CounterComponent,)
        
    def process(self, entity, delta_time):
        counter = entity.get_component(CounterComponent)
        counter.count += 1


class TestWorld:
    """Test World/Registry class"""
    
    def test_world_creation(self):
        """Test creating a world"""
        world = World()
        assert len(world.entities) == 0
        assert len(world.systems) == 0
        assert len(world.component_index) == 0
        
    def test_add_entity(self):
        """Test adding entities to world"""
        world = World()
        entity = Entity()
        
        world.add_entity(entity)
        
        assert entity.id in world.entities
        assert len(world.entities) == 1
        
    def test_add_multiple_entities(self):
        """Test adding multiple entities"""
        world = World()
        entities = [Entity() for _ in range(5)]
        
        for entity in entities:
            world.add_entity(entity)
            
        assert len(world.entities) == 5
        
    def test_remove_entity(self):
        """Test removing entity from world"""
        world = World()
        entity = Entity()
        
        world.add_entity(entity)
        world.remove_entity(entity.id)
        
        assert entity.id not in world.entities
        assert len(world.entities) == 0
        
    def test_remove_nonexistent_entity(self):
        """Test removing entity that doesn't exist"""
        world = World()
        # Should not raise error
        world.remove_entity("nonexistent-id")
        
    def test_get_entity(self):
        """Test getting entity by ID"""
        world = World()
        entity = Entity()
        
        world.add_entity(entity)
        retrieved = world.get_entity(entity.id)
        
        assert retrieved is entity
        
    def test_get_nonexistent_entity(self):
        """Test getting entity that doesn't exist"""
        world = World()
        assert world.get_entity("nonexistent-id") is None
        
    def test_add_system(self):
        """Test adding systems to world"""
        world = World()
        system = TestSystem()
        
        world.add_system(system)
        
        assert system in world.systems
        assert len(world.systems) == 1
        
    def test_add_multiple_systems(self):
        """Test adding multiple systems"""
        world = World()
        system1 = TestSystem()
        system2 = CounterSystem()
        
        world.add_system(system1)
        world.add_system(system2)
        
        assert len(world.systems) == 2
        
    def test_add_system_with_priority(self):
        """Test system execution order by priority"""
        world = World()
        
        system1 = TestSystem()
        system1.priority = 10
        
        system2 = CounterSystem()
        system2.priority = 5
        
        world.add_system(system2)
        world.add_system(system1)
        
        # Should be sorted by priority (lower value = earlier execution)
        assert world.systems[0] is system2  # priority 5
        assert world.systems[1] is system1  # priority 10
        
    def test_remove_system(self):
        """Test removing system from world"""
        world = World()
        system = TestSystem()
        
        world.add_system(system)
        world.remove_system(TestSystem)  # Pass the type, not instance
        
        assert system not in world.systems
        assert len(world.systems) == 0
        
    def test_component_indexing(self):
        """Test component-based entity indexing"""
        world = World()
        
        entity1 = Entity()
        entity1.add_component(MockComponent(value=1))
        
        entity2 = Entity()
        entity2.add_component(MockComponent(value=2))
        entity2.add_component(CounterComponent())
        
        entity3 = Entity()
        entity3.add_component(CounterComponent())
        
        world.add_entity(entity1)
        world.add_entity(entity2)
        world.add_entity(entity3)
        
        # Check component indexing
        mock_entities = world.query(MockComponent)
        assert len(mock_entities) == 2
        assert entity1 in mock_entities
        assert entity2 in mock_entities
        
        counter_entities = world.query(CounterComponent)
        assert len(counter_entities) == 2
        assert entity2 in counter_entities
        assert entity3 in counter_entities
        
    def test_update_world(self):
        """Test updating world systems"""
        world = World()
        system = TestSystem()
        
        entity = Entity()
        entity.add_component(MockComponent(value=10))
        
        world.add_entity(entity)
        world.add_system(system)
        
        # Update world
        world.update(delta_time=1.0)
        
        # Check that entity was processed
        assert entity.id in system.processed_entities
        assert entity.get_component(MockComponent).value == 11
        
    def test_update_only_enabled_systems(self):
        """Test that only enabled systems are updated"""
        world = World()
        
        system1 = TestSystem()
        system2 = CounterSystem()  # Use different system type
        system2.enabled = False
        
        entity = Entity()
        entity.add_component(MockComponent(value=0))
        entity.add_component(CounterComponent())
        
        world.add_entity(entity)
        world.add_system(system1)
        world.add_system(system2)
        
        world.update(delta_time=1.0)
        
        # Only system1 should have processed the entity
        assert len(system1.processed_entities) == 1
        # system2 is disabled, so counter should not increment
        assert entity.get_component(CounterComponent).count == 0
        
    def test_query_entities(self):
        """Test querying entities with specific components"""
        world = World()
        
        # Create entities with different component combinations
        entity1 = Entity()
        entity1.add_component(MockComponent())
        
        entity2 = Entity()
        entity2.add_component(MockComponent())
        entity2.add_component(CounterComponent())
        
        entity3 = Entity()
        entity3.add_component(CounterComponent())
        
        world.add_entity(entity1)
        world.add_entity(entity2)
        world.add_entity(entity3)
        
        # Query entities with both components
        results = world.query(MockComponent, CounterComponent)
        assert len(results) == 1
        assert entity2 in results
        
    def test_component_modification_updates_index(self):
        """Test that component changes update the index"""
        world = World()
        entity = Entity()
        
        world.add_entity(entity)
        
        # Initially no components
        assert len(world.query(MockComponent)) == 0
        
        # Add component using world method
        world.add_component_to_entity(entity.id, MockComponent())
        
        # Should now be indexed
        assert entity in world.query(MockComponent)
        
        # Remove component using world method
        world.remove_component_from_entity(entity.id, MockComponent)
        
        # Should no longer be indexed
        assert entity not in world.query(MockComponent)
        
    def test_clear_world(self):
        """Test clearing all entities from world"""
        world = World()
        
        # Add some entities
        for _ in range(5):
            entity = Entity()
            entity.add_component(MockComponent())
            world.add_entity(entity)
            
        # Clear all entities
        for entity_id in list(world.entities.keys()):
            world.remove_entity(entity_id)
        
        assert len(world.entities) == 0
        # Component index may still have keys but with empty sets
        for comp_type, entity_ids in world.component_index.items():
            assert len(entity_ids) == 0