"""
Versionable Mixin - Version control for entities
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import copy


class VersionableMixin:
    """
    Adds version control capabilities to entities
    
    Track changes, maintain history, and rollback to previous states.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize versionable"""
        super().__init__(*args, **kwargs)
        self._version: int = 1
        self._version_history: List[Dict[str, Any]] = []
        self._max_versions: int = 10
        self._version_metadata: Dict[str, Any] = {}
        self._auto_versioning: bool = True
        
        # Create initial version
        self._create_version("Initial version")
        
    def get_version(self) -> int:
        """Get current version number"""
        return self._version
        
    def set_auto_versioning(self, enabled: bool):
        """Enable/disable automatic versioning on changes"""
        self._auto_versioning = enabled
        
    def create_version(self, message: str = "", metadata: Optional[Dict[str, Any]] = None):
        """
        Create a new version snapshot
        
        Args:
            message: Version message/description
            metadata: Additional metadata for version
        """
        self._create_version(message, metadata)
        
    def _create_version(self, message: str, metadata: Optional[Dict[str, Any]] = None):
        """Internal version creation"""
        # Create snapshot of current state
        snapshot = {
            'version': self._version,
            'timestamp': time.time(),
            'datetime': datetime.now().isoformat(),
            'message': message,
            'metadata': metadata or {},
            'state': self._capture_state()
        }
        
        # Add to history
        self._version_history.append(snapshot)
        
        # Increment version
        self._version += 1
        
        # Limit history size
        if len(self._version_history) > self._max_versions:
            self._version_history.pop(0)
            
    def _capture_state(self) -> Dict[str, Any]:
        """Capture current entity state"""
        state = {
            'id': self.id,
            'tags': list(self.tags),
            'active': self.active,
            'components': {}
        }
        
        # Capture component states
        for comp_type, component in self.components.items():
            if hasattr(component, '__dict__'):
                # Deep copy component data
                try:
                    comp_state = copy.deepcopy(component.__dict__)
                except:
                    # Fallback to string representation
                    comp_state = str(component)
            else:
                comp_state = str(component)
                
            state['components'][comp_type.__name__] = comp_state
            
        return state
        
    def rollback_to_version(self, version: int) -> bool:
        """
        Rollback entity to specific version
        
        Args:
            version: Version number to rollback to
            
        Returns:
            True if successful
        """
        # Find version in history
        version_data = None
        for v in self._version_history:
            if v['version'] == version:
                version_data = v
                break
                
        if not version_data:
            return False
            
        # Restore state
        self._restore_state(version_data['state'])
        
        # Create new version for the rollback
        self._create_version(f"Rollback to version {version}")
        
        return True
        
    def rollback(self, steps: int = 1) -> bool:
        """
        Rollback by number of steps
        
        Args:
            steps: Number of versions to go back
            
        Returns:
            True if successful
        """
        if steps >= len(self._version_history):
            return False
            
        # Get target version
        target_index = -(steps + 1)  # -1 is current, so we need one more
        target_version = self._version_history[target_index]
        
        return self.rollback_to_version(target_version['version'])
        
    def _restore_state(self, state: Dict[str, Any]):
        """Restore entity from state snapshot"""
        # Restore basic attributes
        self.active = state.get('active', True)
        
        # Restore tags
        self.tags.clear()
        for tag in state.get('tags', []):
            self.add_tag(tag)
            
        # Component restoration would require component registry
        # This is a simplified version that preserves existing components
        # but updates their values where possible
        
        for comp_name, comp_state in state.get('components', {}).items():
            # Find matching component
            for comp_type, component in self.components.items():
                if comp_type.__name__ == comp_name:
                    # Try to restore component state
                    if isinstance(comp_state, dict) and hasattr(component, '__dict__'):
                        for key, value in comp_state.items():
                            if hasattr(component, key):
                                try:
                                    setattr(component, key, value)
                                except:
                                    pass  # Skip if can't set attribute
                    break
                    
    def get_version_history(self) -> List[Dict[str, Any]]:
        """
        Get version history
        
        Returns:
            List of version snapshots (without full state data)
        """
        history = []
        for v in self._version_history:
            history.append({
                'version': v['version'],
                'timestamp': v['timestamp'],
                'datetime': v['datetime'],
                'message': v['message'],
                'metadata': v['metadata']
            })
        return history
        
    def get_version_diff(self, version1: int, version2: int) -> Dict[str, Any]:
        """
        Get differences between two versions
        
        Args:
            version1: First version
            version2: Second version
            
        Returns:
            Dictionary describing differences
        """
        v1_data = None
        v2_data = None
        
        for v in self._version_history:
            if v['version'] == version1:
                v1_data = v
            elif v['version'] == version2:
                v2_data = v
                
        if not v1_data or not v2_data:
            return {}
            
        diff = {
            'version1': version1,
            'version2': version2,
            'tag_changes': {
                'added': [],
                'removed': []
            },
            'component_changes': {}
        }
        
        # Compare tags
        tags1 = set(v1_data['state'].get('tags', []))
        tags2 = set(v2_data['state'].get('tags', []))
        
        diff['tag_changes']['added'] = list(tags2 - tags1)
        diff['tag_changes']['removed'] = list(tags1 - tags2)
        
        # Compare components (simplified)
        comps1 = v1_data['state'].get('components', {})
        comps2 = v2_data['state'].get('components', {})
        
        all_comps = set(comps1.keys()) | set(comps2.keys())
        
        for comp in all_comps:
            if comp not in comps1:
                diff['component_changes'][comp] = 'added'
            elif comp not in comps2:
                diff['component_changes'][comp] = 'removed'
            elif comps1[comp] != comps2[comp]:
                diff['component_changes'][comp] = 'modified'
                
        return diff
        
    def set_max_versions(self, max_versions: int):
        """
        Set maximum number of versions to keep
        
        Args:
            max_versions: Maximum versions in history
        """
        self._max_versions = max_versions
        
        # Trim history if needed
        while len(self._version_history) > max_versions:
            self._version_history.pop(0)
            
    def tag_version(self, version: int, tag: str):
        """
        Add a tag to a specific version
        
        Args:
            version: Version number
            tag: Tag to add
        """
        for v in self._version_history:
            if v['version'] == version:
                if 'tags' not in v['metadata']:
                    v['metadata']['tags'] = []
                if tag not in v['metadata']['tags']:
                    v['metadata']['tags'].append(tag)
                break
                
    def find_version_by_tag(self, tag: str) -> Optional[int]:
        """
        Find version by tag
        
        Args:
            tag: Tag to search for
            
        Returns:
            Version number or None
        """
        for v in self._version_history:
            if tag in v['metadata'].get('tags', []):
                return v['version']
        return None
        
    # Override modification methods to auto-version
    def add_component(self, component):
        """Add component with auto-versioning"""
        result = super().add_component(component)
        
        if self._auto_versioning:
            self._create_version(f"Added component: {type(component).__name__}")
            
        return result
        
    def remove_component(self, component_type):
        """Remove component with auto-versioning"""
        result = super().remove_component(component_type)
        
        if self._auto_versioning and result:
            self._create_version(f"Removed component: {component_type.__name__}")
            
        return result