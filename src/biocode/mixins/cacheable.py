"""
Cacheable Mixin - Performance caching capabilities
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
import time
from typing import Dict, Any, Optional, Callable, Tuple
from functools import wraps
import weakref


class CacheableMixin:
    """
    Adds caching capabilities to entities
    
    Improves performance by caching expensive computations.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize cacheable"""
        super().__init__(*args, **kwargs)
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._cache_ttl: Dict[str, float] = {}  # Time-to-live per key
        self._cache_enabled = True
        self._cache_stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }
        
    def cache_get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        if not self._cache_enabled:
            self._cache_stats['misses'] += 1
            return None
            
        if key in self._cache:
            value, timestamp = self._cache[key]
            
            # Check TTL
            ttl = self._cache_ttl.get(key, float('inf'))
            if time.time() - timestamp <= ttl:
                self._cache_stats['hits'] += 1
                return value
            else:
                # Expired
                del self._cache[key]
                self._cache_stats['evictions'] += 1
                
        self._cache_stats['misses'] += 1
        return None
        
    def cache_set(self, key: str, value: Any, ttl: Optional[float] = None):
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None = infinite)
        """
        if not self._cache_enabled:
            return
            
        self._cache[key] = (value, time.time())
        
        if ttl is not None:
            self._cache_ttl[key] = ttl
        elif key in self._cache_ttl:
            del self._cache_ttl[key]
            
    def cache_invalidate(self, key: Optional[str] = None):
        """
        Invalidate cache
        
        Args:
            key: Specific key to invalidate (None = all)
        """
        if key is None:
            # Clear all cache
            self._cache.clear()
            self._cache_ttl.clear()
        else:
            # Clear specific key
            self._cache.pop(key, None)
            self._cache_ttl.pop(key, None)
            
    def cache_invalidate_pattern(self, pattern: str):
        """
        Invalidate cache keys matching pattern
        
        Args:
            pattern: Pattern to match (simple string contains)
        """
        keys_to_remove = [
            key for key in self._cache.keys()
            if pattern in key
        ]
        
        for key in keys_to_remove:
            self.cache_invalidate(key)
            
    def set_cache_enabled(self, enabled: bool):
        """Enable/disable caching"""
        self._cache_enabled = enabled
        if not enabled:
            self.cache_invalidate()
            
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total = self._cache_stats['hits'] + self._cache_stats['misses']
        hit_rate = self._cache_stats['hits'] / total if total > 0 else 0
        
        return {
            'enabled': self._cache_enabled,
            'size': len(self._cache),
            'hits': self._cache_stats['hits'],
            'misses': self._cache_stats['misses'],
            'evictions': self._cache_stats['evictions'],
            'hit_rate': hit_rate
        }
        
    def reset_cache_stats(self):
        """Reset cache statistics"""
        self._cache_stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }
        
    def cached_method(self, ttl: Optional[float] = None):
        """
        Decorator for caching method results
        
        Args:
            ttl: Cache time-to-live
            
        Usage:
            @entity.cached_method(ttl=60)
            def expensive_calculation(self):
                return sum(range(1000000))
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Create cache key from function name and arguments
                cache_key = f"{func.__name__}:{args}:{kwargs}"
                
                # Try cache first
                cached_value = self.cache_get(cache_key)
                if cached_value is not None:
                    return cached_value
                    
                # Calculate and cache
                result = func(*args, **kwargs)
                self.cache_set(cache_key, result, ttl)
                return result
                
            return wrapper
        return decorator


class CachedProperty:
    """
    Descriptor for cached properties
    
    Usage:
        class MyEntity(CacheableMixin, Entity):
            @CachedProperty(ttl=10)
            def expensive_property(self):
                return sum(range(1000000))
    """
    
    def __init__(self, ttl: Optional[float] = None):
        self.ttl = ttl
        self.func = None
        self.name = None
        
    def __set_name__(self, owner, name):
        self.name = name
        
    def __get__(self, instance, owner):
        if instance is None:
            return self
            
        if not hasattr(instance, 'cache_get'):
            # Fallback if not cacheable
            return self.func(instance)
            
        # Use caching
        cache_key = f"property:{self.name}"
        cached_value = instance.cache_get(cache_key)
        
        if cached_value is None:
            cached_value = self.func(instance)
            instance.cache_set(cache_key, cached_value, self.ttl)
            
        return cached_value
        
    def __call__(self, func):
        self.func = func
        return self


class ComponentCache:
    """
    Specialized cache for component queries
    
    Caches common component access patterns.
    """
    
    def __init__(self, entity: 'Entity'):
        self.entity_ref = weakref.ref(entity)
        self.component_cache: Dict[type, Any] = {}
        self.query_cache: Dict[Tuple[type, ...], bool] = {}
        
    def get_component_cached(self, component_type: type) -> Optional[Any]:
        """Get component with caching"""
        if component_type in self.component_cache:
            return self.component_cache[component_type]
            
        entity = self.entity_ref()
        if entity:
            component = entity.get_component(component_type)
            if component:
                self.component_cache[component_type] = component
            return component
            
        return None
        
    def has_components_cached(self, *component_types: type) -> bool:
        """Check if entity has all components (cached)"""
        cache_key = tuple(sorted(component_types, key=lambda x: x.__name__))
        
        if cache_key in self.query_cache:
            return self.query_cache[cache_key]
            
        entity = self.entity_ref()
        if entity:
            result = all(entity.has_component(ct) for ct in component_types)
            self.query_cache[cache_key] = result
            return result
            
        return False
        
    def invalidate(self):
        """Invalidate all component caches"""
        self.component_cache.clear()
        self.query_cache.clear()