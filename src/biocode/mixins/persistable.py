"""
Persistable Mixin - Database persistence capabilities
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
import json


class PersistableMixin:
    """
    Adds database persistence capabilities to entities
    
    Supports save/load operations with various backends.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize persistable"""
        super().__init__(*args, **kwargs)
        self._persistence_id: Optional[str] = None
        self._last_saved: Optional[float] = None
        self._is_dirty: bool = False
        self._save_version: int = 0
        self._metadata: Dict[str, Any] = {}
        
    def set_persistence_id(self, persistence_id: str):
        """Set unique persistence identifier"""
        self._persistence_id = persistence_id
        
    def get_persistence_id(self) -> Optional[str]:
        """Get persistence identifier"""
        return self._persistence_id or self.id
        
    def mark_dirty(self):
        """Mark entity as needing to be saved"""
        self._is_dirty = True
        
    def is_dirty(self) -> bool:
        """Check if entity needs saving"""
        return self._is_dirty
        
    def to_persistence_dict(self) -> Dict[str, Any]:
        """
        Convert entity to persistence format
        
        Returns:
            Dictionary ready for database storage
        """
        # Use serialization from SerializableMixin if available
        if hasattr(self, 'to_dict'):
            data = self.to_dict()
        else:
            # Basic persistence data
            data = {
                'id': self.id,
                'tags': list(self.tags),
                'active': self.active,
                'components': {}
            }
            
        # Add persistence metadata
        data['_persistence'] = {
            'id': self.get_persistence_id(),
            'version': self._save_version,
            'saved_at': datetime.now().isoformat(),
            'metadata': self._metadata
        }
        
        return data
        
    def save_to_backend(self, backend: 'PersistenceBackend') -> bool:
        """
        Save entity to persistence backend
        
        Args:
            backend: Persistence backend to use
            
        Returns:
            True if successful
        """
        try:
            data = self.to_persistence_dict()
            backend.save(self.get_persistence_id(), data)
            
            # Update persistence state
            self._last_saved = time.time()
            self._is_dirty = False
            self._save_version += 1
            
            return True
            
        except Exception as e:
            print(f"Failed to save entity: {e}")
            return False
            
    def load_from_backend(self, backend: 'PersistenceBackend', 
                         persistence_id: Optional[str] = None) -> bool:
        """
        Load entity from persistence backend
        
        Args:
            backend: Persistence backend to use
            persistence_id: Optional ID to load
            
        Returns:
            True if successful
        """
        try:
            pid = persistence_id or self.get_persistence_id()
            data = backend.load(pid)
            
            if not data:
                return False
                
            # Restore entity state
            self.id = data.get('id', self.id)
            self.active = data.get('active', True)
            
            # Restore tags
            self.tags.clear()
            for tag in data.get('tags', []):
                self.add_tag(tag)
                
            # Restore persistence metadata
            if '_persistence' in data:
                pers = data['_persistence']
                self._persistence_id = pers.get('id')
                self._save_version = pers.get('version', 0)
                self._metadata = pers.get('metadata', {})
                
            self._is_dirty = False
            self._last_saved = time.time()
            
            return True
            
        except Exception as e:
            print(f"Failed to load entity: {e}")
            return False
            
    def delete_from_backend(self, backend: 'PersistenceBackend') -> bool:
        """
        Delete entity from persistence backend
        
        Args:
            backend: Persistence backend to use
            
        Returns:
            True if successful
        """
        try:
            backend.delete(self.get_persistence_id())
            self._persistence_id = None
            self._last_saved = None
            return True
            
        except Exception as e:
            print(f"Failed to delete entity: {e}")
            return False
            
    def add_metadata(self, key: str, value: Any):
        """Add persistence metadata"""
        self._metadata[key] = value
        self.mark_dirty()
        
    def get_metadata(self, key: str, default=None) -> Any:
        """Get persistence metadata"""
        return self._metadata.get(key, default)
        
    def get_save_info(self) -> Dict[str, Any]:
        """Get information about save state"""
        return {
            'persistence_id': self.get_persistence_id(),
            'is_dirty': self._is_dirty,
            'last_saved': self._last_saved,
            'save_version': self._save_version,
            'metadata': self._metadata
        }


class PersistenceBackend:
    """
    Abstract base for persistence backends
    
    Implement this for different storage systems (SQL, NoSQL, File, etc.)
    """
    
    def save(self, key: str, data: Dict[str, Any]):
        """Save data with key"""
        raise NotImplementedError
        
    def load(self, key: str) -> Optional[Dict[str, Any]]:
        """Load data by key"""
        raise NotImplementedError
        
    def delete(self, key: str):
        """Delete data by key"""
        raise NotImplementedError
        
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        raise NotImplementedError
        
    def list_keys(self, pattern: str = "*") -> List[str]:
        """List all keys matching pattern"""
        raise NotImplementedError


class InMemoryBackend(PersistenceBackend):
    """Simple in-memory persistence backend for testing"""
    
    def __init__(self):
        self.storage: Dict[str, Dict[str, Any]] = {}
        
    def save(self, key: str, data: Dict[str, Any]):
        self.storage[key] = data.copy()
        
    def load(self, key: str) -> Optional[Dict[str, Any]]:
        return self.storage.get(key, {}).copy() if key in self.storage else None
        
    def delete(self, key: str):
        self.storage.pop(key, None)
        
    def exists(self, key: str) -> bool:
        return key in self.storage
        
    def list_keys(self, pattern: str = "*") -> List[str]:
        if pattern == "*":
            return list(self.storage.keys())
        # Simple pattern matching
        return [k for k in self.storage.keys() if pattern in k]


class JSONFileBackend(PersistenceBackend):
    """JSON file-based persistence backend"""
    
    def __init__(self, directory: str = "./data"):
        self.directory = directory
        import os
        os.makedirs(directory, exist_ok=True)
        
    def _get_filepath(self, key: str) -> str:
        """Get file path for key"""
        import os
        # Sanitize key for filename
        safe_key = key.replace('/', '_').replace('\\', '_')
        return os.path.join(self.directory, f"{safe_key}.json")
        
    def save(self, key: str, data: Dict[str, Any]):
        filepath = self._get_filepath(key)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
            
    def load(self, key: str) -> Optional[Dict[str, Any]]:
        filepath = self._get_filepath(key)
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
            
    def delete(self, key: str):
        filepath = self._get_filepath(key)
        import os
        try:
            os.remove(filepath)
        except FileNotFoundError:
            pass
            
    def exists(self, key: str) -> bool:
        import os
        return os.path.exists(self._get_filepath(key))
        
    def list_keys(self, pattern: str = "*") -> List[str]:
        import os
        import glob
        
        if pattern == "*":
            pattern = "*.json"
        else:
            pattern = f"*{pattern}*.json"
            
        files = glob.glob(os.path.join(self.directory, pattern))
        # Extract keys from filenames
        return [
            os.path.splitext(os.path.basename(f))[0] 
            for f in files
        ]