"""
BioCode AOP (Aspect-Oriented Programming) Layer
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.

Manages cross-cutting concerns like logging, monitoring, security, etc.
"""
from .base import Aspect, AspectType, JoinPoint
from .logging_aspect import LoggingAspect
from .performance_aspect import PerformanceAspect
from .security_aspect import SecurityAspect
from .transaction_aspect import TransactionAspect
from .error_handling_aspect import ErrorHandlingAspect
from .monitoring_aspect import MonitoringAspect
from .weaver import AspectWeaver

__all__ = [
    'Aspect',
    'AspectType',
    'JoinPoint',
    'LoggingAspect',
    'PerformanceAspect',
    'SecurityAspect',
    'TransactionAspect',
    'ErrorHandlingAspect',
    'MonitoringAspect',
    'AspectWeaver'
]