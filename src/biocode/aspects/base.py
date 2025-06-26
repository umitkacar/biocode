"""
Base Aspect Classes - Foundation for AOP
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass
import functools


class AspectType(Enum):
    """Types of aspect interventions"""
    BEFORE = "before"       # Run before method
    AFTER = "after"         # Run after method
    AROUND = "around"       # Wrap method
    AFTER_RETURNING = "after_returning"  # Run after successful return
    AFTER_THROWING = "after_throwing"    # Run after exception


@dataclass
class JoinPoint:
    """
    Join point information
    
    Represents the point in code where aspect is applied.
    """
    target: Any           # Object being intercepted
    method_name: str      # Method being called
    args: tuple          # Method arguments
    kwargs: dict         # Method keyword arguments
    result: Any = None   # Method result (for after advice)
    exception: Exception = None  # Exception (for after throwing)
    metadata: Dict[str, Any] = None  # Additional metadata
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
            
    def proceed(self, method: Callable) -> Any:
        """Execute the original method"""
        return method(*self.args, **self.kwargs)


class Aspect(ABC):
    """
    Base class for all aspects
    
    Aspects encapsulate cross-cutting concerns.
    """
    
    def __init__(self, enabled: bool = True):
        """
        Initialize aspect
        
        Args:
            enabled: Whether aspect is active
        """
        self.enabled = enabled
        self.applied_to: List[str] = []  # Track where aspect is applied
        
    @abstractmethod
    def get_pointcut(self) -> str:
        """
        Define pointcut pattern
        
        Returns:
            Pattern for matching join points (e.g., "*.process", "System.*")
        """
        pass
        
    def before(self, join_point: JoinPoint):
        """
        Advice to run before method execution
        
        Args:
            join_point: Join point information
        """
        pass
        
    def after(self, join_point: JoinPoint):
        """
        Advice to run after method execution
        
        Args:
            join_point: Join point information
        """
        pass
        
    def around(self, join_point: JoinPoint, proceed: Callable) -> Any:
        """
        Advice to wrap method execution
        
        Args:
            join_point: Join point information
            proceed: Function to call original method
            
        Returns:
            Method result
        """
        # Default implementation just proceeds
        return proceed()
        
    def after_returning(self, join_point: JoinPoint):
        """
        Advice to run after successful method execution
        
        Args:
            join_point: Join point information (includes result)
        """
        pass
        
    def after_throwing(self, join_point: JoinPoint):
        """
        Advice to run after method throws exception
        
        Args:
            join_point: Join point information (includes exception)
        """
        pass
        
    def matches(self, target: Any, method_name: str) -> bool:
        """
        Check if aspect should apply to target method
        
        Args:
            target: Object to check
            method_name: Method name
            
        Returns:
            True if aspect should apply
        """
        if not self.enabled:
            return False
            
        pattern = self.get_pointcut()
        
        # Simple pattern matching
        if pattern == "*":
            return True
            
        if pattern.endswith("*") and "." not in pattern:
            # Prefix matching (only if no dot)
            prefix = pattern[:-1]
            return method_name.startswith(prefix)
            
        if pattern.startswith("*") and "." not in pattern:
            # Suffix matching (only if no dot)
            suffix = pattern[1:]
            return method_name.endswith(suffix)
            
        if "." in pattern:
            # Class.method pattern
            class_pattern, method_pattern = pattern.split(".", 1)
            
            # Check class name
            class_name = target.__class__.__name__
            if class_pattern != "*" and class_pattern != class_name:
                return False
                
            # Check method name
            if method_pattern == "*":
                return True
            elif method_pattern == method_name:
                return True
            else:
                return False
                
        # Exact match
        return pattern == method_name
        
    def create_wrapper(self, target: Any, method: Callable, method_name: str) -> Callable:
        """
        Create wrapped method with aspect applied
        
        Args:
            target: Object owning the method
            method: Original method
            method_name: Name of method
            
        Returns:
            Wrapped method
        """
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            if not self.enabled:
                return method(*args, **kwargs)
                
            # Create join point
            join_point = JoinPoint(
                target=target,
                method_name=method_name,
                args=args,
                kwargs=kwargs
            )
            
            try:
                # Before advice
                self.before(join_point)
                
                # Around advice
                def proceed():
                    return method(*args, **kwargs)
                    
                result = self.around(join_point, proceed)
                
                # Store result in join point
                join_point.result = result
                
                # After returning advice
                self.after_returning(join_point)
                
                # After advice (always runs)
                self.after(join_point)
                
                return result
                
            except Exception as e:
                # Store exception in join point
                join_point.exception = e
                
                # After throwing advice
                self.after_throwing(join_point)
                
                # After advice (always runs)
                self.after(join_point)
                
                # Re-raise exception
                raise
                
        return wrapper
        
    def set_enabled(self, enabled: bool):
        """Enable or disable aspect"""
        self.enabled = enabled
        
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(enabled={self.enabled}, pointcut='{self.get_pointcut()}')"