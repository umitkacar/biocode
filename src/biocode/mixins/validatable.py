"""
Validatable Mixin - Entity and component validation
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
from typing import Dict, Any, List, Optional, Callable, Set, Type
from dataclasses import dataclass
from enum import Enum


class ValidationSeverity(Enum):
    """Validation issue severity levels"""
    ERROR = "error"      # Must fix
    WARNING = "warning"  # Should fix
    INFO = "info"        # Nice to fix


@dataclass
class ValidationIssue:
    """Single validation issue"""
    severity: ValidationSeverity
    component: Optional[str]
    field: Optional[str]
    message: str
    suggested_fix: Optional[str] = None
    
    def __str__(self) -> str:
        location = ""
        if self.component:
            location = f"[{self.component}"
            if self.field:
                location += f".{self.field}"
            location += "] "
            
        return f"{self.severity.value.upper()}: {location}{self.message}"


class ValidationRule:
    """Base class for validation rules"""
    
    def __init__(self, severity: ValidationSeverity = ValidationSeverity.WARNING):
        self.severity = severity
        
    def validate(self, entity: 'Entity') -> List[ValidationIssue]:
        """Validate entity and return issues"""
        raise NotImplementedError


class ValidatableMixin:
    """
    Adds validation capabilities to entities
    
    Ensures entity and component integrity.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize validatable"""
        super().__init__(*args, **kwargs)
        self._validation_rules: List[ValidationRule] = []
        self._component_validators: Dict[Type, List[Callable]] = {}
        self._field_validators: Dict[str, Dict[str, Callable]] = {}
        self._validation_enabled = True
        self._last_validation: Optional[List[ValidationIssue]] = None
        
        # Add default validation rules
        self._add_default_rules()
        
    def _add_default_rules(self):
        """Add default validation rules"""
        # Entity must have at least one component
        self.add_validation_rule(
            lambda e: [
                ValidationIssue(
                    ValidationSeverity.WARNING,
                    None, None,
                    "Entity has no components",
                    "Add at least one component"
                )
            ] if not e.components else []
        )
        
        # Entity should have tags for categorization
        self.add_validation_rule(
            lambda e: [
                ValidationIssue(
                    ValidationSeverity.INFO,
                    None, None,
                    "Entity has no tags",
                    "Add descriptive tags for better organization"
                )
            ] if not e.tags else [],
            severity=ValidationSeverity.INFO
        )
        
    def add_validation_rule(self, rule: Callable[['Entity'], List[ValidationIssue]],
                          severity: ValidationSeverity = ValidationSeverity.WARNING):
        """
        Add custom validation rule
        
        Args:
            rule: Function that takes entity and returns list of issues
            severity: Default severity for rule
        """
        class CustomRule(ValidationRule):
            def __init__(self, func, sev):
                super().__init__(sev)
                self.func = func
                
            def validate(self, entity):
                return self.func(entity)
                
        self._validation_rules.append(CustomRule(rule, severity))
        
    def add_component_validator(self, component_type: Type,
                              validator: Callable[[Any], List[ValidationIssue]]):
        """
        Add validator for specific component type
        
        Args:
            component_type: Type of component to validate
            validator: Function that validates component
        """
        if component_type not in self._component_validators:
            self._component_validators[component_type] = []
            
        self._component_validators[component_type].append(validator)
        
    def add_field_validator(self, component_type: str, field: str,
                           validator: Callable[[Any], Optional[str]]):
        """
        Add validator for specific component field
        
        Args:
            component_type: Component type name
            field: Field name
            validator: Function that returns error message or None
        """
        if component_type not in self._field_validators:
            self._field_validators[component_type] = {}
            
        self._field_validators[component_type][field] = validator
        
    def validate(self) -> List[ValidationIssue]:
        """
        Validate entity and all components
        
        Returns:
            List of validation issues
        """
        if not self._validation_enabled:
            return []
            
        issues = []
        
        # Run entity-level rules
        for rule in self._validation_rules:
            issues.extend(rule.validate(self))
            
        # Validate each component
        for comp_type, component in self.components.items():
            comp_name = comp_type.__name__
            
            # Run component validators
            if comp_type in self._component_validators:
                for validator in self._component_validators[comp_type]:
                    comp_issues = validator(component)
                    # Add component context
                    for issue in comp_issues:
                        if not issue.component:
                            issue.component = comp_name
                    issues.extend(comp_issues)
                    
            # Run field validators
            if comp_name in self._field_validators:
                field_validators = self._field_validators[comp_name]
                
                for field, validator in field_validators.items():
                    if hasattr(component, field):
                        value = getattr(component, field)
                        error = validator(value)
                        
                        if error:
                            issues.append(ValidationIssue(
                                ValidationSeverity.ERROR,
                                comp_name,
                                field,
                                error
                            ))
                            
            # Built-in component validations
            issues.extend(self._validate_component_builtin(comp_type, component))
            
        # Cache results
        self._last_validation = issues
        
        return issues
        
    def _validate_component_builtin(self, comp_type: Type, component: Any) -> List[ValidationIssue]:
        """Built-in validations for known component types"""
        issues = []
        comp_name = comp_type.__name__
        
        # Health component validations
        if comp_name == "HealthComponent":
            if hasattr(component, 'current') and hasattr(component, 'maximum'):
                if component.current > component.maximum:
                    issues.append(ValidationIssue(
                        ValidationSeverity.ERROR,
                        comp_name,
                        "current",
                        f"Current health ({component.current}) exceeds maximum ({component.maximum})",
                        "Set current to maximum or increase maximum"
                    ))
                    
                if component.current < 0:
                    issues.append(ValidationIssue(
                        ValidationSeverity.ERROR,
                        comp_name,
                        "current",
                        "Health cannot be negative",
                        "Set current to 0"
                    ))
                    
        # Energy component validations
        elif comp_name == "EnergyComponent":
            if hasattr(component, 'current') and hasattr(component, 'maximum'):
                if component.current > component.maximum:
                    issues.append(ValidationIssue(
                        ValidationSeverity.ERROR,
                        comp_name,
                        "current",
                        f"Current energy ({component.current}) exceeds maximum ({component.maximum})"
                    ))
                    
            if hasattr(component, 'consumption_rate') and component.consumption_rate < 0:
                issues.append(ValidationIssue(
                    ValidationSeverity.WARNING,
                    comp_name,
                    "consumption_rate",
                    "Negative consumption rate is unusual"
                ))
                
        # Position component validations
        elif comp_name == "PositionComponent":
            if hasattr(component, 'x') and hasattr(component, 'y') and hasattr(component, 'z'):
                # Check for NaN or infinity
                import math
                for coord in ['x', 'y', 'z']:
                    value = getattr(component, coord)
                    if math.isnan(value) or math.isinf(value):
                        issues.append(ValidationIssue(
                            ValidationSeverity.ERROR,
                            comp_name,
                            coord,
                            f"Invalid coordinate value: {value}",
                            "Set to 0.0"
                        ))
                        
        # DNA component validations
        elif comp_name == "DNAComponent":
            if hasattr(component, 'sequence'):
                if not component.sequence:
                    issues.append(ValidationIssue(
                        ValidationSeverity.ERROR,
                        comp_name,
                        "sequence",
                        "DNA sequence is empty"
                    ))
                elif not all(base in 'ATCG' for base in component.sequence):
                    issues.append(ValidationIssue(
                        ValidationSeverity.ERROR,
                        comp_name,
                        "sequence",
                        "DNA sequence contains invalid bases"
                    ))
                    
            if hasattr(component, 'mutation_rate'):
                if component.mutation_rate < 0 or component.mutation_rate > 1:
                    issues.append(ValidationIssue(
                        ValidationSeverity.WARNING,
                        comp_name,
                        "mutation_rate",
                        f"Mutation rate ({component.mutation_rate}) should be between 0 and 1"
                    ))
                    
        return issues
        
    def is_valid(self) -> bool:
        """
        Check if entity is valid (no errors)
        
        Returns:
            True if no validation errors
        """
        issues = self.validate()
        return not any(issue.severity == ValidationSeverity.ERROR for issue in issues)
        
    def get_validation_summary(self) -> Dict[str, int]:
        """
        Get summary of validation issues
        
        Returns:
            Dictionary with counts by severity
        """
        if self._last_validation is None:
            self.validate()
            
        summary = {
            'errors': 0,
            'warnings': 0,
            'info': 0
        }
        
        if self._last_validation:
            for issue in self._last_validation:
                if issue.severity == ValidationSeverity.ERROR:
                    summary['errors'] += 1
                elif issue.severity == ValidationSeverity.WARNING:
                    summary['warnings'] += 1
                else:
                    summary['info'] += 1
                    
        return summary
        
    def fix_validation_issues(self, auto_fix: bool = False) -> List[str]:
        """
        Attempt to fix validation issues
        
        Args:
            auto_fix: If True, apply fixes automatically
            
        Returns:
            List of applied fixes
        """
        if self._last_validation is None:
            self.validate()
            
        fixes_applied = []
        
        if not self._last_validation:
            return fixes_applied
            
        for issue in self._last_validation:
            if issue.suggested_fix and auto_fix:
                # Simple auto-fixes
                if "Set current to maximum" in issue.suggested_fix:
                    comp = self._find_component_by_name(issue.component)
                    if comp and hasattr(comp, 'current') and hasattr(comp, 'maximum'):
                        comp.current = comp.maximum
                        fixes_applied.append(f"Set {issue.component}.current to maximum")
                        
                elif "Set current to 0" in issue.suggested_fix:
                    comp = self._find_component_by_name(issue.component)
                    if comp and hasattr(comp, 'current'):
                        comp.current = 0
                        fixes_applied.append(f"Set {issue.component}.current to 0")
                        
                elif "Set to 0.0" in issue.suggested_fix and issue.field:
                    comp = self._find_component_by_name(issue.component)
                    if comp and hasattr(comp, issue.field):
                        setattr(comp, issue.field, 0.0)
                        fixes_applied.append(f"Set {issue.component}.{issue.field} to 0.0")
                        
        # Re-validate after fixes
        if fixes_applied:
            self.validate()
            
        return fixes_applied
        
    def _find_component_by_name(self, name: str) -> Optional[Any]:
        """Find component by type name"""
        for comp_type, component in self.components.items():
            if comp_type.__name__ == name:
                return component
        return None
        
    def set_validation_enabled(self, enabled: bool):
        """Enable/disable validation"""
        self._validation_enabled = enabled