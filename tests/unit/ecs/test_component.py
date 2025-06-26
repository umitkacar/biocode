"""
Unit tests for ECS Component
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
import pytest
from dataclasses import dataclass
from src.biocode.ecs import Component


class TestComponent:
    """Test Component base class"""
    
    def test_component_is_base_class(self):
        """Test that Component is a proper base class"""
        assert hasattr(Component, '__init__')
        
    def test_custom_component_inheritance(self):
        """Test creating custom components"""
        
        class HealthComponent(Component):
            def __init__(self, max_health: float = 100.0):
                self.current = max_health
                self.maximum = max_health
                
        health = HealthComponent(150.0)
        assert isinstance(health, Component)
        assert health.current == 150.0
        assert health.maximum == 150.0
        
    def test_dataclass_component(self):
        """Test using dataclass for components"""
        
        @dataclass
        class PositionComponent(Component):
            x: float = 0.0
            y: float = 0.0
            z: float = 0.0
            
        pos = PositionComponent(x=10.0, y=20.0, z=30.0)
        assert isinstance(pos, Component)
        assert pos.x == 10.0
        assert pos.y == 20.0
        assert pos.z == 30.0
        
    def test_component_with_methods(self):
        """Test components can have methods"""
        
        class VelocityComponent(Component):
            def __init__(self, dx: float = 0.0, dy: float = 0.0):
                self.dx = dx
                self.dy = dy
                
            def get_speed(self) -> float:
                return (self.dx ** 2 + self.dy ** 2) ** 0.5
                
        velocity = VelocityComponent(dx=3.0, dy=4.0)
        assert velocity.get_speed() == 5.0
        
    def test_component_modification(self):
        """Test modifying component data"""
        
        class StateComponent(Component):
            def __init__(self, state: str = "idle"):
                self.state = state
                self.previous_state = None
                
            def change_state(self, new_state: str):
                self.previous_state = self.state
                self.state = new_state
                
        state = StateComponent("walking")
        state.change_state("running")
        
        assert state.state == "running"
        assert state.previous_state == "walking"
        
    def test_component_composition(self):
        """Test components containing other data structures"""
        
        class InventoryComponent(Component):
            def __init__(self):
                self.items = []
                self.capacity = 10
                
            def add_item(self, item: str) -> bool:
                if len(self.items) < self.capacity:
                    self.items.append(item)
                    return True
                return False
                
        inventory = InventoryComponent()
        assert inventory.add_item("sword")
        assert inventory.add_item("potion")
        assert len(inventory.items) == 2
        assert "sword" in inventory.items
        
    def test_component_types_are_unique(self):
        """Test that component types are distinguishable"""
        
        class ComponentA(Component):
            pass
            
        class ComponentB(Component):
            pass
            
        assert ComponentA != ComponentB
        assert type(ComponentA()) != type(ComponentB())