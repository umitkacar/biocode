"""
Logging Aspect - Automatic method logging
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
import logging
import time
from typing import Any, Optional, Set
from .base import Aspect, JoinPoint


class LoggingAspect(Aspect):
    """
    Logging aspect for automatic method logging
    
    Logs method entry, exit, parameters, results, and exceptions.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None,
                 log_level: int = logging.INFO,
                 log_args: bool = True,
                 log_result: bool = True,
                 max_arg_length: int = 100):
        """
        Initialize logging aspect
        
        Args:
            logger: Logger to use (creates default if None)
            log_level: Logging level
            log_args: Whether to log method arguments
            log_result: Whether to log method results
            max_arg_length: Maximum length for logged arguments
        """
        super().__init__()
        
        self.logger = logger or logging.getLogger("biocode.aspects")
        self.log_level = log_level
        self.log_args = log_args
        self.log_result = log_result
        self.max_arg_length = max_arg_length
        self.excluded_methods: Set[str] = {"__str__", "__repr__", "__hash__"}
        
    def get_pointcut(self) -> str:
        """Log all System methods by default"""
        return "System.*"
        
    def before(self, join_point: JoinPoint):
        """Log method entry"""
        if join_point.method_name in self.excluded_methods:
            return
            
        class_name = join_point.target.__class__.__name__
        method_sig = f"{class_name}.{join_point.method_name}"
        
        # Build log message
        msg = f">>> Entering {method_sig}"
        
        if self.log_args:
            # Format arguments
            args_str = self._format_args(join_point.args, join_point.kwargs)
            if args_str:
                msg += f" with args: {args_str}"
                
        self.logger.log(self.log_level, msg)
        
        # Store start time for duration logging
        join_point.metadata['start_time'] = time.time()
        
    def after_returning(self, join_point: JoinPoint):
        """Log successful method exit"""
        if join_point.method_name in self.excluded_methods:
            return
            
        class_name = join_point.target.__class__.__name__
        method_sig = f"{class_name}.{join_point.method_name}"
        
        # Calculate duration
        duration = time.time() - join_point.metadata.get('start_time', time.time())
        
        # Build log message
        msg = f"<<< Exiting {method_sig} (took {duration*1000:.2f}ms)"
        
        if self.log_result and join_point.result is not None:
            result_str = self._format_value(join_point.result)
            msg += f" with result: {result_str}"
            
        self.logger.log(self.log_level, msg)
        
    def after_throwing(self, join_point: JoinPoint):
        """Log method exception"""
        if join_point.method_name in self.excluded_methods:
            return
            
        class_name = join_point.target.__class__.__name__
        method_sig = f"{class_name}.{join_point.method_name}"
        
        # Calculate duration
        duration = time.time() - join_point.metadata.get('start_time', time.time())
        
        # Log exception
        self.logger.error(
            f"!!! Exception in {method_sig} (after {duration*1000:.2f}ms): "
            f"{type(join_point.exception).__name__}: {str(join_point.exception)}"
        )
        
    def _format_args(self, args: tuple, kwargs: dict) -> str:
        """Format method arguments for logging"""
        parts = []
        
        # Format positional arguments (skip 'self')
        if args and len(args) > 1:
            for i, arg in enumerate(args[1:], 1):
                parts.append(self._format_value(arg))
                
        # Format keyword arguments
        for key, value in kwargs.items():
            parts.append(f"{key}={self._format_value(value)}")
            
        return ", ".join(parts)
        
    def _format_value(self, value: Any) -> str:
        """Format a value for logging"""
        if value is None:
            return "None"
            
        # Handle common types
        if isinstance(value, (int, float, bool)):
            return str(value)
            
        if isinstance(value, str):
            if len(value) > self.max_arg_length:
                return f'"{value[:self.max_arg_length]}..."'
            return f'"{value}"'
            
        # Handle collections
        if isinstance(value, list):
            return f"[{len(value)} items]"
            
        if isinstance(value, dict):
            return f"{{{len(value)} items}}"
            
        if isinstance(value, set):
            return f"{{{len(value)} items}}"
            
        # Handle objects
        if hasattr(value, '__class__'):
            class_name = value.__class__.__name__
            if hasattr(value, 'id'):
                return f"{class_name}(id={getattr(value, 'id', 'unknown')[:8]}...)"
            return f"{class_name}()"
            
        # Fallback
        str_val = str(value)
        if len(str_val) > self.max_arg_length:
            return str_val[:self.max_arg_length] + "..."
        return str_val
        
    def add_excluded_method(self, method_name: str):
        """Add method to exclusion list"""
        self.excluded_methods.add(method_name)
        
    def remove_excluded_method(self, method_name: str):
        """Remove method from exclusion list"""
        self.excluded_methods.discard(method_name)
        
    def set_log_level(self, level: int):
        """Change logging level"""
        self.log_level = level