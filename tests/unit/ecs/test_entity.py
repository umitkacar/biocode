"""
Unit tests for ECS Entity
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
import pytest
from src.biocode.ecs import Entity, Component


class MockComponent(Component):
    """Mock component for testing"""
    def __init__(self, value: int = 0):
        self.value = value


class AnotherMockComponent(Component):
    """Another mock component for testing"""
    def __init__(self, name: str = "test"):
        self.name = name


class TestEntity:
    """Test Entity class"""
    
    def test_entity_creation(self):
        """Test entity creation with UUID"""
        entity = Entity()
        assert entity.id is not None
        assert len(entity.id) == 36  # UUID format
        assert entity.active is True
        assert len(entity.components) == 0
        assert len(entity.tags) == 0
        
    def test_entity_creation_with_id(self):
        """Test entity creation with custom ID"""
        entity = Entity(entity_id="custom-id-123")
        assert entity.id == "custom-id-123"
        
    def test_add_component(self):
        """Test adding components to entity"""
        entity = Entity()
        component = MockComponent(value=42)
        
        entity.add_component(component)
        
        assert entity.has_component(MockComponent)
        assert entity.get_component(MockComponent).value == 42
        
    def test_add_multiple_components(self):
        """Test adding multiple components"""
        entity = Entity()
        comp1 = MockComponent(value=10)
        comp2 = AnotherMockComponent(name="test-name")
        
        entity.add_component(comp1)
        entity.add_component(comp2)
        
        assert entity.has_component(MockComponent)
        assert entity.has_component(AnotherMockComponent)
        assert len(entity.components) == 2
        
    def test_replace_component(self):
        """Test replacing existing component"""
        entity = Entity()
        comp1 = MockComponent(value=10)
        comp2 = MockComponent(value=20)
        
        entity.add_component(comp1)
        entity.add_component(comp2)  # Should replace
        
        assert entity.get_component(MockComponent).value == 20
        assert len(entity.components) == 1
        
    def test_remove_component(self):
        """Test removing component"""
        entity = Entity()
        component = MockComponent(value=42)
        
        entity.add_component(component)
        entity.remove_component(MockComponent)
        
        assert not entity.has_component(MockComponent)
        assert len(entity.components) == 0
        
    def test_remove_nonexistent_component(self):
        """Test removing component that doesn't exist"""
        entity = Entity()
        # Should not raise error
        entity.remove_component(MockComponent)
        
    def test_get_nonexistent_component(self):
        """Test getting component that doesn't exist"""
        entity = Entity()
        assert entity.get_component(MockComponent) is None
        
    def test_add_tags(self):
        """Test adding tags to entity"""
        entity = Entity()
        
        entity.add_tag("enemy")
        entity.add_tag("flying")
        
        assert entity.has_tag("enemy")
        assert entity.has_tag("flying")
        assert len(entity.tags) == 2
        
    def test_add_duplicate_tag(self):
        """Test adding duplicate tag"""
        entity = Entity()
        
        entity.add_tag("enemy")
        entity.add_tag("enemy")  # Duplicate
        
        assert len(entity.tags) == 1
        
    def test_remove_tag(self):
        """Test removing tag"""
        entity = Entity()
        
        entity.add_tag("enemy")
        entity.remove_tag("enemy")
        
        assert not entity.has_tag("enemy")
        assert len(entity.tags) == 0
        
    def test_remove_nonexistent_tag(self):
        """Test removing tag that doesn't exist"""
        entity = Entity()
        # Should not raise error
        entity.remove_tag("nonexistent")
        
    def test_active_state(self):
        """Test entity active state"""
        entity = Entity()
        
        assert entity.active is True
        
        entity.active = False
        assert entity.active is False
        
    def test_entity_equality(self):
        """Test entity equality based on ID"""
        entity1 = Entity(entity_id="same-id")
        entity2 = Entity(entity_id="same-id")
        entity3 = Entity(entity_id="different-id")
        
        assert entity1.id == entity2.id
        assert entity1.id != entity3.id