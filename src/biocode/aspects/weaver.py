"""
Aspect Weaver - Applies aspects to target objects
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
import inspect
from typing import Any, List, Dict, Set, Optional
from .base import Aspect


class AspectWeaver:
    """
    Weaves aspects into target objects
    
    Dynamically applies cross-cutting concerns to methods.
    """
    
    def __init__(self):
        """Initialize aspect weaver"""
        self.aspects: List[Aspect] = []
        self.woven_objects: Set[int] = set()  # Track object IDs that have been woven
        self.original_methods: Dict[str, Any] = {}  # Store original methods
        
    def add_aspect(self, aspect: Aspect):
        """
        Add an aspect to be woven
        
        Args:
            aspect: Aspect to add
        """
        if aspect not in self.aspects:
            self.aspects.append(aspect)
            
    def remove_aspect(self, aspect: Aspect):
        """
        Remove an aspect
        
        Args:
            aspect: Aspect to remove
        """
        if aspect in self.aspects:
            self.aspects.remove(aspect)
            
    def weave(self, target: Any):
        """
        Weave aspects into target object
        
        Args:
            target: Object to weave aspects into
        """
        # Check if already woven
        obj_id = id(target)
        if obj_id in self.woven_objects:
            return
            
        # Get all methods of the target
        methods = self._get_methods(target)
        
        # Apply aspects to each method
        for method_name, method in methods:
            # Find matching aspects
            matching_aspects = [
                aspect for aspect in self.aspects
                if aspect.matches(target, method_name)
            ]
            
            if matching_aspects:
                # Store original method
                original_key = f"{obj_id}.{method_name}"
                self.original_methods[original_key] = method
                
                # Create wrapped method
                wrapped = self._create_wrapped_method(
                    target, method, method_name, matching_aspects
                )
                
                # Replace method
                setattr(target, method_name, wrapped)
                
                # Track that aspects are applied
                for aspect in matching_aspects:
                    aspect.applied_to.append(f"{target.__class__.__name__}.{method_name}")
                    
        # Mark as woven
        self.woven_objects.add(obj_id)
        
    def unweave(self, target: Any):
        """
        Remove aspects from target object
        
        Args:
            target: Object to remove aspects from
        """
        obj_id = id(target)
        if obj_id not in self.woven_objects:
            return
            
        # Restore original methods
        methods = self._get_methods(target)
        
        for method_name, _ in methods:
            original_key = f"{obj_id}.{method_name}"
            if original_key in self.original_methods:
                # Restore original method
                original = self.original_methods[original_key]
                setattr(target, method_name, original)
                del self.original_methods[original_key]
                
        # Remove from woven set
        self.woven_objects.discard(obj_id)
        
    def weave_class(self, target_class: type):
        """
        Weave aspects into all instances of a class
        
        Args:
            target_class: Class to weave aspects into
        """
        # Get class methods
        methods = []
        for name, method in inspect.getmembers(target_class):
            if (inspect.ismethod(method) or inspect.isfunction(method)) and \
               not name.startswith('_'):
                methods.append((name, method))
                
        # Apply aspects to each method
        for method_name, method in methods:
            # Find matching aspects
            matching_aspects = [
                aspect for aspect in self.aspects
                if aspect.matches(target_class, method_name)
            ]
            
            if matching_aspects:
                # Create wrapped method
                wrapped = self._create_wrapped_class_method(
                    target_class, method, method_name, matching_aspects
                )
                
                # Replace method in class
                setattr(target_class, method_name, wrapped)
                
    def _get_methods(self, obj: Any) -> List[tuple]:
        """Get all public methods of an object"""
        methods = []
        
        # Get methods from the class to avoid double-binding issues
        cls = obj.__class__
        for name in dir(cls):
            if not name.startswith('_'):  # Skip private methods
                attr = getattr(cls, name)
                if callable(attr) and not isinstance(attr, type):
                    methods.append((name, attr))
                    
        return methods
        
    def _create_wrapped_method(self, target: Any, method: Any,
                              method_name: str, aspects: List[Aspect]) -> Any:
        """Create a wrapped method with all aspects applied"""
        # Bind the method to the instance
        bound_method = method.__get__(target, target.__class__)
        
        # Start with the bound method
        wrapped = bound_method
        
        # Apply each aspect in reverse order (so first aspect runs first)
        for aspect in reversed(aspects):
            wrapped = aspect.create_wrapper(target, wrapped, method_name)
            
        return wrapped
        
    def _create_wrapped_class_method(self, target_class: type, method: Any,
                                   method_name: str, aspects: List[Aspect]) -> Any:
        """Create a wrapped class method with all aspects applied"""
        def wrapped_method(self, *args, **kwargs):
            # Create instance wrapper
            if not hasattr(self, '_aspect_wrapped_methods'):
                self._aspect_wrapped_methods = {}
                
            if method_name not in self._aspect_wrapped_methods:
                # Bind method to instance
                bound_method = method.__get__(self, target_class)
                
                # Apply aspects
                wrapped = bound_method
                for aspect in reversed(aspects):
                    wrapped = aspect.create_wrapper(self, wrapped, method_name)
                    
                self._aspect_wrapped_methods[method_name] = wrapped
                
            return self._aspect_wrapped_methods[method_name](*args, **kwargs)
            
        return wrapped_method
        
    def get_woven_summary(self) -> Dict[str, Any]:
        """Get summary of woven aspects"""
        summary = {
            'total_aspects': len(self.aspects),
            'total_woven_objects': len(self.woven_objects),
            'aspects': []
        }
        
        for aspect in self.aspects:
            summary['aspects'].append({
                'type': aspect.__class__.__name__,
                'pointcut': aspect.get_pointcut(),
                'enabled': aspect.enabled,
                'applied_to': aspect.applied_to
            })
            
        return summary
        
    def enable_aspect(self, aspect_type: type):
        """Enable all aspects of a specific type"""
        for aspect in self.aspects:
            if isinstance(aspect, aspect_type):
                aspect.set_enabled(True)
                
    def disable_aspect(self, aspect_type: type):
        """Disable all aspects of a specific type"""
        for aspect in self.aspects:
            if isinstance(aspect, aspect_type):
                aspect.set_enabled(False)
                

# Global weaver instance
_global_weaver = AspectWeaver()


def get_global_weaver() -> AspectWeaver:
    """Get global aspect weaver"""
    return _global_weaver


def weave_aspects(target: Any, aspects: Optional[List[Aspect]] = None):
    """
    Convenience function to weave aspects into a target
    
    Args:
        target: Object to weave into
        aspects: List of aspects (uses global weaver if None)
    """
    weaver = get_global_weaver()
    
    if aspects:
        for aspect in aspects:
            weaver.add_aspect(aspect)
            
    weaver.weave(target)