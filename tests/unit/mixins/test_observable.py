"""
Unit tests for Observable Mixin
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
import pytest
from src.biocode.ecs import Entity
from src.biocode.mixins import ObservableMixin
from src.biocode.mixins.observable import ChangeType
from src.biocode.ecs.components.biological import HealthComponent


class ObservableEntity(ObservableMixin, Entity):
    """Test entity with observation capabilities"""
    pass


class TestObservableMixin:
    """Test ObservableMixin functionality"""
    
    def test_add_observer(self):
        """Test adding observers"""
        entity = ObservableEntity()
        events = []
        
        def observer(entity_ref, change_type, **kwargs):
            events.append((entity_ref, change_type, kwargs))
            
        entity.add_observer(ChangeType.COMPONENT_ADDED, observer)
        
        # Trigger an event by adding component
        health = HealthComponent()
        entity.add_component(health)
        
        assert len(events) == 1
        assert events[0][0] is entity
        assert events[0][1] == ChangeType.COMPONENT_ADDED
        assert events[0][2]['component_type'] == HealthComponent
        assert events[0][2]['component'] == health
        
    def test_multiple_observers(self):
        """Test multiple observers"""
        entity = ObservableEntity()
        events1 = []
        events2 = []
        
        def observer1(entity_ref, change_type, **kwargs):
            events1.append(kwargs)
            
        def observer2(entity_ref, change_type, **kwargs):
            events2.append(kwargs)
            
        entity.add_observer(ChangeType.TAG_ADDED, observer1)
        entity.add_observer(ChangeType.TAG_ADDED, observer2)
        
        entity.add_tag("test")
        
        assert len(events1) == 1
        assert len(events2) == 1
        assert events1[0]['tag'] == "test"
        assert events2[0]['tag'] == "test"
        
    def test_remove_observer(self):
        """Test removing observers"""
        entity = ObservableEntity()
        events = []
        
        def observer(entity_ref, change_type, **kwargs):
            events.append(kwargs)
            
        entity.add_observer(ChangeType.TAG_ADDED, observer)
        entity.remove_observer(ChangeType.TAG_ADDED, observer)
        
        entity.add_tag("test")
        
        assert len(events) == 0
        
    def test_observer_exception_handling(self):
        """Test that observer exceptions don't break notification"""
        entity = ObservableEntity()
        events = []
        
        def bad_observer(entity_ref, change_type, **kwargs):
            raise RuntimeError("Observer error")
            
        def good_observer(entity_ref, change_type, **kwargs):
            events.append(kwargs)
            
        entity.add_observer(ChangeType.TAG_ADDED, bad_observer)
        entity.add_observer(ChangeType.TAG_ADDED, good_observer)
        
        # Should not raise exception
        entity.add_tag("test")
        
        # Good observer should still be called
        assert len(events) == 1
        
    def test_component_change_tracking(self):
        """Test automatic component change tracking"""
        entity = ObservableEntity()
        changes = []
        
        def track_changes(entity_ref, change_type, **kwargs):
            changes.append(kwargs)
                
        entity.add_observer(ChangeType.COMPONENT_ADDED, track_changes)
        entity.add_observer(ChangeType.COMPONENT_REMOVED, track_changes)
        
        # Add component
        health = HealthComponent()
        entity.add_component(health)
        
        # Remove component
        entity.remove_component(HealthComponent)
        
        assert len(changes) == 2
        assert changes[0]['component_type'] == HealthComponent
        assert changes[1]['component_type'] == HealthComponent
        
    def test_tag_change_tracking(self):
        """Test automatic tag change tracking"""
        entity = ObservableEntity()
        tag_events = []
        
        def track_tags(entity_ref, change_type, **kwargs):
            tag_events.append(kwargs)
                
        entity.add_observer(ChangeType.TAG_ADDED, track_tags)
        entity.add_observer(ChangeType.TAG_REMOVED, track_tags)
        
        # Add and remove tags
        entity.add_tag("enemy")
        entity.add_tag("flying")
        entity.remove_tag("enemy")
        
        assert len(tag_events) == 3
        assert tag_events[0]['tag'] == "enemy"
        assert tag_events[1]['tag'] == "flying"
        assert tag_events[2]['tag'] == "enemy"
        
    def test_change_history(self):
        """Test change history tracking"""
        entity = ObservableEntity()
        
        # Make some changes
        entity.add_tag("test1")
        entity.add_component(HealthComponent())
        entity.add_tag("test2")
        
        # Get all history
        history = entity.get_change_history()
        assert len(history) == 3
        
        # Get filtered history
        tag_history = entity.get_change_history(ChangeType.TAG_ADDED)
        assert len(tag_history) == 2
        
        comp_history = entity.get_change_history(ChangeType.COMPONENT_ADDED)
        assert len(comp_history) == 1
        
    def test_clear_history(self):
        """Test clearing change history"""
        entity = ObservableEntity()
        
        entity.add_tag("test")
        assert len(entity.get_change_history()) > 0
        
        entity.clear_change_history()
        assert len(entity.get_change_history()) == 0
        
    def test_disable_recording(self):
        """Test disabling change recording"""
        entity = ObservableEntity()
        
        # Disable recording
        entity.set_recording_changes(False)
        
        entity.add_tag("test")
        
        # No history should be recorded
        assert len(entity.get_change_history()) == 0
        
        # Re-enable recording
        entity.set_recording_changes(True)
        
        entity.add_tag("test2")
        
        # Should record again
        assert len(entity.get_change_history()) == 1