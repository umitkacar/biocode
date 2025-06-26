"""
Serializable Mixin - Entity serialization capabilities
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
import json
import pickle
from typing import Dict, Any, Optional
from datetime import datetime


class SerializableMixin:
    """
    Adds serialization capabilities to entities
    
    Supports JSON and binary serialization formats.
    """
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert entity to dictionary representation
        
        Returns:
            Dictionary with entity data
        """
        data = {
            'id': self.id,
            'tags': list(self.tags),
            'active': self.active,
            'components': {},
            'metadata': {
                'serialized_at': datetime.now().isoformat(),
                'version': '1.0'
            }
        }
        
        # Serialize each component
        for comp_type, component in self.components.items():
            comp_name = comp_type.__name__
            
            # Try to serialize component
            if hasattr(component, '__dict__'):
                # Handle dataclass components
                comp_data = {}
                for key, value in component.__dict__.items():
                    # Convert complex types to serializable format
                    if isinstance(value, set):
                        comp_data[key] = list(value)
                    elif isinstance(value, datetime):
                        comp_data[key] = value.isoformat()
                    elif hasattr(value, '__dict__'):
                        # Nested objects - simplified serialization
                        comp_data[key] = str(value)
                    else:
                        comp_data[key] = value
                        
                data['components'][comp_name] = comp_data
            else:
                # Fallback for non-dataclass components
                data['components'][comp_name] = str(component)
                
        return data
    
    def to_json(self, indent: Optional[int] = 2) -> str:
        """
        Convert entity to JSON string
        
        Args:
            indent: JSON indentation level
            
        Returns:
            JSON string representation
        """
        return json.dumps(self.to_dict(), indent=indent, default=str)
    
    def to_binary(self) -> bytes:
        """
        Convert entity to binary format using pickle
        
        Returns:
            Binary representation
        """
        return pickle.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], world=None):
        """
        Create entity from dictionary
        
        Args:
            data: Dictionary with entity data
            world: Optional world to add entity to
            
        Returns:
            Reconstructed entity
        """
        # This would need component registry to properly reconstruct
        # For now, return a basic entity
        from ..ecs import Entity
        
        entity = Entity(entity_id=data['id'])
        entity.active = data.get('active', True)
        
        # Restore tags
        for tag in data.get('tags', []):
            entity.add_tag(tag)
            
        # Component reconstruction would require a registry
        # This is a simplified version
        
        if world:
            world.add_entity(entity)
            
        return entity
    
    @classmethod
    def from_json(cls, json_str: str, world=None):
        """
        Create entity from JSON string
        
        Args:
            json_str: JSON string
            world: Optional world to add entity to
            
        Returns:
            Reconstructed entity
        """
        data = json.loads(json_str)
        return cls.from_dict(data, world)
    
    @classmethod
    def from_binary(cls, binary_data: bytes, world=None):
        """
        Create entity from binary data
        
        Args:
            binary_data: Binary representation
            world: Optional world to add entity to
            
        Returns:
            Reconstructed entity
        """
        data = pickle.loads(binary_data)
        return cls.from_dict(data, world)