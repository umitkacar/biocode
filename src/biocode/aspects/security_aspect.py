"""
Security Aspect - Method access control and validation
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
from typing import Set, Dict, Any, Optional, Callable, List
from enum import Enum
from .base import Aspect, JoinPoint


class SecurityLevel(Enum):
    """Security access levels"""
    PUBLIC = 0      # Anyone can access
    INTERNAL = 1    # Internal components only
    PROTECTED = 2   # Specific permissions required
    ADMIN = 3       # Admin only


class SecurityContext:
    """Current security context"""
    
    def __init__(self):
        self.user_id: Optional[str] = None
        self.roles: Set[str] = set()
        self.permissions: Set[str] = set()
        self.security_level: SecurityLevel = SecurityLevel.PUBLIC
        
    def has_role(self, role: str) -> bool:
        """Check if context has role"""
        return role in self.roles
        
    def has_permission(self, permission: str) -> bool:
        """Check if context has permission"""
        return permission in self.permissions
        
    def has_security_level(self, required_level: SecurityLevel) -> bool:
        """Check if context meets security level"""
        return self.security_level.value >= required_level.value


# Global security context (thread-local in production)
_security_context = SecurityContext()


def get_security_context() -> SecurityContext:
    """Get current security context"""
    return _security_context


def set_security_context(context: SecurityContext):
    """Set security context"""
    global _security_context
    _security_context = context


class SecurityAspect(Aspect):
    """
    Security aspect for access control
    
    Controls method access based on security rules.
    """
    
    def __init__(self):
        """Initialize security aspect"""
        super().__init__()
        
        # Method security requirements
        self.method_requirements: Dict[str, Dict[str, Any]] = {}
        
        # Security validators
        self.validators: Dict[str, Callable] = {}
        
        # Audit log
        self.audit_log: List[Dict[str, Any]] = []
        
        # Set up default rules
        self._setup_default_rules()
        
    def _setup_default_rules(self):
        """Set up default security rules"""
        # System modification methods require INTERNAL level
        self.set_method_requirement("System.initialize", security_level=SecurityLevel.INTERNAL)
        self.set_method_requirement("System.cleanup", security_level=SecurityLevel.INTERNAL)
        
        # Entity deletion requires permission
        self.set_method_requirement("World.remove_entity", permission="entity:delete")
        
        # Infection system requires special permission
        self.set_method_requirement("InfectionSystem.introduce_pathogen", 
                                  permission="infection:create")
                                  
    def get_pointcut(self) -> str:
        """Apply to all methods"""
        return "*"
        
    def before(self, join_point: JoinPoint):
        """Check security before method execution"""
        # Get method signature
        class_name = join_point.target.__class__.__name__
        method_sig = f"{class_name}.{join_point.method_name}"
        
        # Check if method has security requirements
        requirements = self.method_requirements.get(method_sig)
        if not requirements:
            return  # No requirements, allow access
            
        # Get current security context
        context = get_security_context()
        
        # Check security level
        required_level = requirements.get('security_level')
        if required_level and not context.has_security_level(required_level):
            self._audit_access_denied(join_point, f"Insufficient security level")
            raise PermissionError(
                f"Access denied to {method_sig}: "
                f"Required level {required_level.name}, "
                f"current level {context.security_level.name}"
            )
            
        # Check required role
        required_role = requirements.get('role')
        if required_role and not context.has_role(required_role):
            self._audit_access_denied(join_point, f"Missing role: {required_role}")
            raise PermissionError(
                f"Access denied to {method_sig}: "
                f"Required role '{required_role}'"
            )
            
        # Check required permission
        required_permission = requirements.get('permission')
        if required_permission and not context.has_permission(required_permission):
            self._audit_access_denied(join_point, f"Missing permission: {required_permission}")
            raise PermissionError(
                f"Access denied to {method_sig}: "
                f"Required permission '{required_permission}'"
            )
            
        # Run custom validator
        validator_name = requirements.get('validator')
        if validator_name and validator_name in self.validators:
            validator = self.validators[validator_name]
            if not validator(context, join_point):
                self._audit_access_denied(join_point, f"Custom validator failed")
                raise PermissionError(
                    f"Access denied to {method_sig}: "
                    f"Validation failed"
                )
                
        # Audit successful access
        self._audit_access_granted(join_point)
        
    def after_throwing(self, join_point: JoinPoint):
        """Log security exceptions"""
        if isinstance(join_point.exception, PermissionError):
            # Already logged in before()
            pass
        else:
            # Log other exceptions for security monitoring
            self._audit_exception(join_point)
            
    def set_method_requirement(self, method_signature: str,
                             security_level: Optional[SecurityLevel] = None,
                             role: Optional[str] = None,
                             permission: Optional[str] = None,
                             validator: Optional[str] = None):
        """
        Set security requirements for a method
        
        Args:
            method_signature: Method to protect (e.g., "System.process")
            security_level: Required security level
            role: Required role
            permission: Required permission
            validator: Name of custom validator
        """
        requirements = {}
        
        if security_level is not None:
            requirements['security_level'] = security_level
        if role is not None:
            requirements['role'] = role
        if permission is not None:
            requirements['permission'] = permission
        if validator is not None:
            requirements['validator'] = validator
            
        self.method_requirements[method_signature] = requirements
        
    def add_validator(self, name: str, validator: Callable[[SecurityContext, JoinPoint], bool]):
        """
        Add custom security validator
        
        Args:
            name: Validator name
            validator: Function that returns True if access allowed
        """
        self.validators[name] = validator
        
    def _audit_access_granted(self, join_point: JoinPoint):
        """Audit successful access"""
        import time
        
        context = get_security_context()
        audit_entry = {
            'timestamp': time.time(),
            'event': 'access_granted',
            'user_id': context.user_id,
            'method': f"{join_point.target.__class__.__name__}.{join_point.method_name}",
            'security_level': context.security_level.name
        }
        
        self.audit_log.append(audit_entry)
        self._trim_audit_log()
        
    def _audit_access_denied(self, join_point: JoinPoint, reason: str):
        """Audit access denial"""
        import time
        
        context = get_security_context()
        audit_entry = {
            'timestamp': time.time(),
            'event': 'access_denied',
            'user_id': context.user_id,
            'method': f"{join_point.target.__class__.__name__}.{join_point.method_name}",
            'reason': reason,
            'security_level': context.security_level.name
        }
        
        self.audit_log.append(audit_entry)
        self._trim_audit_log()
        
    def _audit_exception(self, join_point: JoinPoint):
        """Audit exceptions"""
        import time
        
        context = get_security_context()
        audit_entry = {
            'timestamp': time.time(),
            'event': 'exception',
            'user_id': context.user_id,
            'method': f"{join_point.target.__class__.__name__}.{join_point.method_name}",
            'exception': type(join_point.exception).__name__,
            'security_level': context.security_level.name
        }
        
        self.audit_log.append(audit_entry)
        self._trim_audit_log()
        
    def _trim_audit_log(self):
        """Keep audit log size manageable"""
        max_entries = 1000
        if len(self.audit_log) > max_entries:
            self.audit_log = self.audit_log[-max_entries:]
            
    def get_audit_log(self, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get audit log entries
        
        Args:
            event_type: Filter by event type
            
        Returns:
            List of audit entries
        """
        if event_type:
            return [
                entry for entry in self.audit_log
                if entry['event'] == event_type
            ]
        return self.audit_log.copy()