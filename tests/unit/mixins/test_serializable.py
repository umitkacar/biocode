"""
Unit tests for Serializable Mixin
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
import pytest
import json
from src.biocode.ecs import Entity
from src.biocode.mixins import SerializableMixin
from src.biocode.ecs.components.biological import HealthComponent, EnergyComponent


class SerializableEntity(SerializableMixin, Entity):
    """Test entity with serialization"""
    pass


class TestSerializableMixin:
    """Test SerializableMixin functionality"""
    
    def test_to_dict(self):
        """Test converting entity to dictionary"""
        entity = SerializableEntity()
        entity.add_component(HealthComponent(current=80.0, maximum=100.0))
        entity.add_tag("test_tag")
        
        data = entity.to_dict()
        
        assert data['id'] == entity.id
        assert data['active'] is True
        assert 'test_tag' in data['tags']
        assert 'HealthComponent' in data['components']
        assert data['components']['HealthComponent']['current'] == 80.0
        
    def test_from_dict(self):
        """Test creating entity from dictionary"""
        data = {
            'id': 'test-entity-123',
            'active': True,
            'tags': ['enemy', 'flying'],
            'components': {
                'HealthComponent': {
                    'current': 50.0,
                    'maximum': 100.0
                }
            }
        }
        
        entity = SerializableEntity.from_dict(data)
        
        assert entity.id == 'test-entity-123'
        assert entity.active is True
        assert entity.has_tag('enemy')
        assert entity.has_tag('flying')
        # Note: Component reconstruction would need registry
        
    def test_to_json(self):
        """Test JSON serialization"""
        entity = SerializableEntity()
        entity.add_component(EnergyComponent(current=75.0, maximum=100.0))
        entity.add_tag("player")
        
        json_str = entity.to_json()
        data = json.loads(json_str)
        
        assert data['id'] == entity.id
        assert 'player' in data['tags']
        assert data['components']['EnergyComponent']['current'] == 75.0
        
    def test_from_json(self):
        """Test JSON deserialization"""
        json_str = '''{
            "id": "json-entity-456",
            "active": false,
            "tags": ["npc"],
            "components": {
                "EnergyComponent": {
                    "current": 25.0,
                    "maximum": 50.0
                }
            }
        }'''
        
        entity = SerializableEntity.from_json(json_str)
        
        assert entity.id == 'json-entity-456'
        assert entity.active is False
        assert entity.has_tag('npc')
        
    def test_to_binary(self):
        """Test binary serialization"""
        entity = SerializableEntity()
        entity.add_tag("binary_test")
        
        binary_data = entity.to_binary()
        
        assert isinstance(binary_data, bytes)
        assert len(binary_data) > 0
        
    def test_from_binary(self):
        """Test binary deserialization"""
        # Create and serialize entity
        original = SerializableEntity(entity_id="binary-789")
        original.add_tag("serialized")
        binary_data = original.to_binary()
        
        # Deserialize into new entity
        entity = SerializableEntity.from_binary(binary_data)
        
        assert entity.id == "binary-789"
        assert entity.has_tag("serialized")
        
    def test_roundtrip_json(self):
        """Test full JSON roundtrip"""
        original = SerializableEntity(entity_id="roundtrip-json")
        original.add_component(HealthComponent(current=60.0, maximum=100.0))
        original.add_component(EnergyComponent(current=40.0, maximum=80.0))
        original.add_tag("test1")
        original.add_tag("test2")
        original.active = False
        
        # Serialize and deserialize
        json_str = original.to_json()
        restored = SerializableEntity.from_json(json_str)
        
        assert restored.id == original.id
        assert restored.active == original.active
        assert len(restored.tags) == len(original.tags)
        for tag in original.tags:
            assert restored.has_tag(tag)
            
    def test_roundtrip_binary(self):
        """Test full binary roundtrip"""
        original = SerializableEntity(entity_id="roundtrip-binary")
        original.add_tag("persistent")
        original.active = True
        
        # Serialize and deserialize
        binary_data = original.to_binary()
        restored = SerializableEntity.from_binary(binary_data)
        
        assert restored.id == original.id
        assert restored.active == original.active
        assert restored.has_tag("persistent")
        
    def test_pretty_json(self):
        """Test pretty JSON formatting"""
        entity = SerializableEntity()
        entity.add_tag("formatted")
        
        json_str = entity.to_json(indent=4)
        
        # Check for indentation
        assert '\n' in json_str
        assert '    ' in json_str  # 4-space indent
        
    def test_invalid_json(self):
        """Test handling invalid JSON"""
        entity = SerializableEntity()
        
        with pytest.raises(json.JSONDecodeError):
            entity.from_json("invalid json {")
            
    def test_invalid_binary(self):
        """Test handling invalid binary data"""
        entity = SerializableEntity()
        
        with pytest.raises(Exception):
            entity.from_binary(b"invalid pickle data")