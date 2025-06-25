"""Logging utilities for BioCode"""
import logging
from functools import wraps
from typing import Any, Callable, Optional


def get_logger(name: str, **kwargs) -> logging.Logger:
    """Get a logger instance
    
    Args:
        name: Logger name
        **kwargs: Additional arguments (ignored for compatibility)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def log_tissue_event(tissue_name: str, event: str, **kwargs):
    """Log a tissue event
    
    Args:
        tissue_name: Name of the tissue
        event: Event description
        **kwargs: Additional event data
    """
    logger = logging.getLogger(f"tissue.{tissue_name}")
    logger.info(f"[{tissue_name}] {event}", extra=kwargs)


class LoggingMixin:
    """Mixin to add logging capabilities to classes"""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for the class"""
        if not hasattr(self, '_logger'):
            self._logger = logging.getLogger(self.__class__.__name__)
        return self._logger
    
    def log_debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(message, extra=kwargs)
    
    def log_info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(message, extra=kwargs)
    
    def log_warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(message, extra=kwargs)
    
    def log_error(self, message: str, **kwargs):
        """Log error message"""
        self.logger.error(message, extra=kwargs)


def log_cell_event(event_type: str) -> Callable:
    """Decorator to log cell events"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            if hasattr(self, 'logger'):
                self.logger.info(f"Cell event: {event_type}", 
                               extra={'cell_id': getattr(self, 'cell_id', 'unknown')})
            result = func(self, *args, **kwargs)
            return result
        return wrapper
    return decorator


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)


def log_tissue_event(event_type: str) -> Callable:
    """Decorator to log tissue events"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            if hasattr(self, 'logger'):
                self.logger.info(f"Tissue event: {event_type}",
                               extra={'tissue_name': getattr(self, 'name', 'unknown')})
            result = func(self, *args, **kwargs)
            return result
        return wrapper
    return decorator