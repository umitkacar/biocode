"""
BioCode Error Handling Utilities
"""
import logging
import traceback
from typing import Optional, Dict, Any, Callable
from functools import wraps
from datetime import datetime

logger = logging.getLogger(__name__)


class BioCodeError(Exception):
    """Base exception for BioCode project"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.details = details or {}
        self.timestamp = datetime.now()


class AgentError(BioCodeError):
    """Agent-specific errors"""
    pass


class SandboxError(BioCodeError):
    """Sandbox-related errors"""
    pass


class ColonyError(BioCodeError):
    """Colony-level errors"""
    pass


class ResourceError(BioCodeError):
    """Resource management errors"""
    pass


def safe_execute(func: Callable, default: Any = None, log_errors: bool = True):
    """
    Safely execute a function and return default on error
    
    Args:
        func: Function to execute
        default: Default value to return on error
        log_errors: Whether to log errors
    
    Returns:
        Function result or default value
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if log_errors:
                logger.error(f"Error in {func.__name__}: {e}")
                logger.debug(traceback.format_exc())
            return default
    return wrapper


def retry_on_error(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Retry decorator for functions that may fail
    
    Args:
        max_attempts: Maximum number of attempts
        delay: Initial delay between attempts
        backoff: Multiplier for delay after each failure
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_error = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_attempts - 1:
                        logger.warning(
                            f"{func.__name__} failed (attempt {attempt + 1}/{max_attempts}): {e}"
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"{func.__name__} failed after {max_attempts} attempts: {e}"
                        )
            
            raise last_error
        return wrapper
    return decorator


def handle_agent_error(agent_id: str, error: Exception, context: Optional[Dict[str, Any]] = None):
    """
    Handle agent-specific errors with proper logging and recovery
    
    Args:
        agent_id: Agent identifier
        error: The exception that occurred
        context: Additional context information
    """
    error_info = {
        'agent_id': agent_id,
        'error_type': type(error).__name__,
        'error_message': str(error),
        'timestamp': datetime.now().isoformat(),
        'context': context or {}
    }
    
    # Log error with full traceback
    logger.error(f"Agent {agent_id} error: {error}")
    logger.debug(f"Error details: {error_info}")
    logger.debug(traceback.format_exc())
    
    # Return error info for potential recovery
    return error_info


class ErrorCollector:
    """Collect and analyze errors across the system"""
    
    def __init__(self, max_errors: int = 1000):
        self.errors = deque(maxlen=max_errors)
        self._lock = threading.RLock()
        
    def add_error(self, error_info: Dict[str, Any]):
        """Add error to collection"""
        with self._lock:
            self.errors.append(error_info)
            
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of collected errors"""
        with self._lock:
            if not self.errors:
                return {'total_errors': 0}
                
            error_types = defaultdict(int)
            agent_errors = defaultdict(int)
            
            for error in self.errors:
                error_types[error.get('error_type', 'Unknown')] += 1
                agent_errors[error.get('agent_id', 'Unknown')] += 1
                
            return {
                'total_errors': len(self.errors),
                'error_types': dict(error_types),
                'errors_by_agent': dict(agent_errors),
                'recent_errors': list(self.errors)[-10:]
            }
            
    def clear(self):
        """Clear error collection"""
        with self._lock:
            self.errors.clear()


# Global error collector
_error_collector = ErrorCollector()


def get_error_collector() -> ErrorCollector:
    """Get global error collector instance"""
    return _error_collector


# Import required modules
import time
import threading
from collections import deque, defaultdict