"""
Error Handling Aspect - Automatic error recovery and reporting
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
import time
import traceback
from typing import Dict, Type, Callable, Optional, Any, List
from .base import Aspect, JoinPoint


class ErrorHandlingAspect(Aspect):
    """
    Error handling aspect
    
    Provides automatic error recovery, retry logic, and error reporting.
    """
    
    def __init__(self, max_retries: int = 3, 
                 retry_delay: float = 0.1,
                 exponential_backoff: bool = True):
        """
        Initialize error handling aspect
        
        Args:
            max_retries: Maximum retry attempts
            retry_delay: Initial delay between retries (seconds)
            exponential_backoff: Whether to use exponential backoff
        """
        super().__init__()
        
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.exponential_backoff = exponential_backoff
        
        # Error handlers by exception type
        self.error_handlers: Dict[Type[Exception], Callable] = {}
        
        # Recovery strategies
        self.recovery_strategies: Dict[str, Callable] = {}
        
        # Error statistics
        self.error_stats: Dict[str, Dict[str, int]] = {}
        
        # Circuit breaker state
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        
        # Set up default handlers
        self._setup_default_handlers()
        
    def _setup_default_handlers(self):
        """Set up default error handlers"""
        # Handle common errors
        self.add_error_handler(
            ValueError,
            lambda jp, ex: print(f"ValueError in {jp.method_name}: {ex}")
        )
        
        self.add_error_handler(
            KeyError,
            lambda jp, ex: print(f"KeyError in {jp.method_name}: {ex}")
        )
        
    def get_pointcut(self) -> str:
        """Apply to all System methods"""
        return "System.*"
        
    def around(self, join_point: JoinPoint, proceed: Callable) -> Any:
        """Wrap method with error handling and retry logic"""
        method_sig = f"{join_point.target.__class__.__name__}.{join_point.method_name}"
        
        # Check circuit breaker
        if self._is_circuit_open(method_sig):
            raise RuntimeError(f"Circuit breaker open for {method_sig}")
            
        retry_count = 0
        last_exception = None
        
        while retry_count <= self.max_retries:
            try:
                # Attempt to execute method
                result = proceed()
                
                # Reset circuit breaker on success
                self._reset_circuit_breaker(method_sig)
                
                return result
                
            except Exception as e:
                last_exception = e
                
                # Record error
                self._record_error(method_sig, e)
                
                # Check if we should retry
                if self._should_retry(e, retry_count):
                    retry_count += 1
                    
                    # Calculate delay
                    delay = self._calculate_retry_delay(retry_count)
                    
                    # Log retry attempt
                    print(f"Retrying {method_sig} (attempt {retry_count}/{self.max_retries}) "
                          f"after {delay:.2f}s delay")
                          
                    # Wait before retry
                    time.sleep(delay)
                    
                else:
                    # No retry, handle error and re-raise
                    self._handle_error(join_point, e)
                    
                    # Check circuit breaker threshold
                    self._update_circuit_breaker(method_sig)
                    
                    raise
                    
        # All retries exhausted
        if last_exception:
            self._handle_error(join_point, last_exception)
            self._update_circuit_breaker(method_sig)
            raise last_exception
            
    def after_throwing(self, join_point: JoinPoint):
        """Handle exceptions after method failure"""
        exception = join_point.exception
        
        # Try recovery strategy
        method_sig = f"{join_point.target.__class__.__name__}.{join_point.method_name}"
        if method_sig in self.recovery_strategies:
            strategy = self.recovery_strategies[method_sig]
            try:
                strategy(join_point, exception)
            except Exception as recovery_error:
                print(f"Recovery strategy failed for {method_sig}: {recovery_error}")
                
    def add_error_handler(self, exception_type: Type[Exception], 
                         handler: Callable[[JoinPoint, Exception], None]):
        """
        Add error handler for specific exception type
        
        Args:
            exception_type: Type of exception to handle
            handler: Handler function
        """
        self.error_handlers[exception_type] = handler
        
    def add_recovery_strategy(self, method_signature: str,
                            strategy: Callable[[JoinPoint, Exception], None]):
        """
        Add recovery strategy for specific method
        
        Args:
            method_signature: Method to add recovery for
            strategy: Recovery function
        """
        self.recovery_strategies[method_signature] = strategy
        
    def _should_retry(self, exception: Exception, retry_count: int) -> bool:
        """Check if exception is retryable"""
        # Don't retry on programming errors
        if isinstance(exception, (TypeError, AttributeError, ImportError)):
            return False
            
        # Don't retry on explicit non-retryable errors
        if hasattr(exception, 'retryable') and not exception.retryable:
            return False
            
        # Check retry count
        return retry_count < self.max_retries
        
    def _calculate_retry_delay(self, retry_count: int) -> float:
        """Calculate delay before retry"""
        if self.exponential_backoff:
            return self.retry_delay * (2 ** (retry_count - 1))
        return self.retry_delay
        
    def _handle_error(self, join_point: JoinPoint, exception: Exception):
        """Handle error using registered handlers"""
        # Find matching handler
        for exc_type, handler in self.error_handlers.items():
            if isinstance(exception, exc_type):
                try:
                    handler(join_point, exception)
                except Exception as handler_error:
                    print(f"Error in error handler: {handler_error}")
                break
                
    def _record_error(self, method_sig: str, exception: Exception):
        """Record error statistics"""
        if method_sig not in self.error_stats:
            self.error_stats[method_sig] = {}
            
        exc_type = type(exception).__name__
        if exc_type not in self.error_stats[method_sig]:
            self.error_stats[method_sig][exc_type] = 0
            
        self.error_stats[method_sig][exc_type] += 1
        
    def _is_circuit_open(self, method_sig: str) -> bool:
        """Check if circuit breaker is open"""
        if method_sig not in self.circuit_breakers:
            return False
            
        breaker = self.circuit_breakers[method_sig]
        if breaker['state'] == 'open':
            # Check if we should try half-open
            if time.time() - breaker['opened_at'] > breaker['timeout']:
                breaker['state'] = 'half-open'
                return False
            return True
            
        return False
        
    def _update_circuit_breaker(self, method_sig: str):
        """Update circuit breaker state"""
        if method_sig not in self.circuit_breakers:
            self.circuit_breakers[method_sig] = {
                'state': 'closed',
                'failure_count': 0,
                'threshold': 5,
                'timeout': 60.0,
                'opened_at': None
            }
            
        breaker = self.circuit_breakers[method_sig]
        breaker['failure_count'] += 1
        
        if breaker['failure_count'] >= breaker['threshold']:
            breaker['state'] = 'open'
            breaker['opened_at'] = time.time()
            print(f"Circuit breaker opened for {method_sig}")
            
    def _reset_circuit_breaker(self, method_sig: str):
        """Reset circuit breaker on success"""
        if method_sig in self.circuit_breakers:
            self.circuit_breakers[method_sig]['state'] = 'closed'
            self.circuit_breakers[method_sig]['failure_count'] = 0
            
    def get_error_report(self) -> Dict[str, Any]:
        """Get comprehensive error report"""
        total_errors = 0
        error_by_type = {}
        
        for method_errors in self.error_stats.values():
            for exc_type, count in method_errors.items():
                total_errors += count
                if exc_type not in error_by_type:
                    error_by_type[exc_type] = 0
                error_by_type[exc_type] += count
                
        return {
            'total_errors': total_errors,
            'error_by_method': self.error_stats,
            'error_by_type': error_by_type,
            'circuit_breakers': {
                method: {
                    'state': breaker['state'],
                    'failure_count': breaker['failure_count']
                }
                for method, breaker in self.circuit_breakers.items()
            }
        }
        
    def reset_error_stats(self):
        """Reset error statistics"""
        self.error_stats.clear()
        self.circuit_breakers.clear()