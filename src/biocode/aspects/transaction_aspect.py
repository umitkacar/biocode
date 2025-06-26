"""
Transaction Aspect - Transactional method execution
Copyright (c) 2024 Umit Kacar, PhD. All rights reserved.
"""
import uuid
from typing import Dict, Any, List, Optional, Set, Callable
from contextlib import contextmanager
from .base import Aspect, JoinPoint


class Transaction:
    """Represents a transaction"""
    
    def __init__(self, transaction_id: str):
        self.id = transaction_id
        self.changes: List[Dict[str, Any]] = []
        self.status = "active"
        self.savepoints: List[int] = []
        
    def add_change(self, change: Dict[str, Any]):
        """Record a change in the transaction"""
        self.changes.append(change)
        
    def create_savepoint(self) -> int:
        """Create a savepoint"""
        savepoint = len(self.changes)
        self.savepoints.append(savepoint)
        return savepoint
        
    def rollback_to_savepoint(self, savepoint: int):
        """Rollback to a savepoint"""
        if savepoint in self.savepoints:
            self.changes = self.changes[:savepoint]
            # Remove savepoints after this one
            self.savepoints = [sp for sp in self.savepoints if sp <= savepoint]
            
    def commit(self):
        """Commit the transaction"""
        self.status = "committed"
        
    def rollback(self):
        """Rollback the transaction"""
        self.status = "rolled_back"
        self.changes.clear()


class TransactionManager:
    """Manages transactions"""
    
    def __init__(self):
        self.transactions: Dict[str, Transaction] = {}
        self.current_transaction: Optional[Transaction] = None
        
    def begin_transaction(self) -> Transaction:
        """Begin a new transaction"""
        transaction_id = str(uuid.uuid4())
        transaction = Transaction(transaction_id)
        self.transactions[transaction_id] = transaction
        self.current_transaction = transaction
        return transaction
        
    def commit_transaction(self, transaction: Transaction):
        """Commit a transaction"""
        transaction.commit()
        if self.current_transaction == transaction:
            self.current_transaction = None
            
    def rollback_transaction(self, transaction: Transaction):
        """Rollback a transaction"""
        transaction.rollback()
        if self.current_transaction == transaction:
            self.current_transaction = None
            
        # Apply rollback changes
        self._apply_rollback(transaction)
        
    def get_current_transaction(self) -> Optional[Transaction]:
        """Get current active transaction"""
        return self.current_transaction
        
    def _apply_rollback(self, transaction: Transaction):
        """Apply rollback changes (undo operations)"""
        # Reverse changes
        for change in reversed(transaction.changes):
            if change['type'] == 'component_add':
                # Remove added component
                entity = change['entity']
                component_type = change['component_type']
                entity.remove_component(component_type)
                
            elif change['type'] == 'component_remove':
                # Re-add removed component
                entity = change['entity']
                component = change['component']
                entity.add_component(component)
                
            elif change['type'] == 'component_update':
                # Restore old value
                component = change['component']
                field = change['field']
                old_value = change['old_value']
                setattr(component, field, old_value)


# Global transaction manager
_transaction_manager = TransactionManager()


def get_transaction_manager() -> TransactionManager:
    """Get global transaction manager"""
    return _transaction_manager


class TransactionAspect(Aspect):
    """
    Transaction aspect for transactional method execution
    
    Provides atomicity for method operations.
    """
    
    def __init__(self):
        """Initialize transaction aspect"""
        super().__init__()
        
        self.transaction_manager = get_transaction_manager()
        
        # Methods that should be transactional
        self.transactional_methods: Set[str] = {
            "World.add_entity",
            "World.remove_entity",
            "System.process_batch",
            "Entity.add_component",
            "Entity.remove_component"
        }
        
        # Methods that participate in transactions
        self.participates_in_transaction: Set[str] = {
            "Entity.add_component",
            "Entity.remove_component",
            "Entity.add_tag",
            "Entity.remove_tag"
        }
        
    def get_pointcut(self) -> str:
        """Apply to all methods"""
        return "*"
        
    def matches(self, target: Any, method_name: str) -> bool:
        """Check if method should have transaction support"""
        if not super().matches(target, method_name):
            return False
            
        method_sig = f"{target.__class__.__name__}.{method_name}"
        
        return (method_sig in self.transactional_methods or 
                method_sig in self.participates_in_transaction)
                
    def around(self, join_point: JoinPoint, proceed: Callable) -> Any:
        """Wrap method in transaction"""
        method_sig = f"{join_point.target.__class__.__name__}.{join_point.method_name}"
        
        # Check if we need to start a new transaction
        current_transaction = self.transaction_manager.get_current_transaction()
        
        if method_sig in self.transactional_methods and not current_transaction:
            # Start new transaction
            return self._execute_in_transaction(join_point, proceed)
            
        elif method_sig in self.participates_in_transaction and current_transaction:
            # Participate in existing transaction
            return self._participate_in_transaction(join_point, proceed, current_transaction)
            
        else:
            # No transaction needed
            return proceed()
            
    def _execute_in_transaction(self, join_point: JoinPoint, proceed: Callable) -> Any:
        """Execute method in a new transaction"""
        transaction = self.transaction_manager.begin_transaction()
        
        try:
            # Execute method
            result = proceed()
            
            # Commit on success
            self.transaction_manager.commit_transaction(transaction)
            
            return result
            
        except Exception as e:
            # Rollback on failure
            self.transaction_manager.rollback_transaction(transaction)
            raise
            
    def _participate_in_transaction(self, join_point: JoinPoint, proceed: Callable,
                                  transaction: Transaction) -> Any:
        """Participate in existing transaction"""
        # Record changes for potential rollback
        self._record_before_state(join_point, transaction)
        
        try:
            # Execute method
            result = proceed()
            
            # Record successful change
            self._record_change(join_point, transaction, result)
            
            return result
            
        except Exception:
            # Exception will be handled by parent transaction
            raise
            
    def _record_before_state(self, join_point: JoinPoint, transaction: Transaction):
        """Record state before method execution"""
        method_name = join_point.method_name
        
        if method_name == "add_component" and hasattr(join_point.target, 'components'):
            # Record that we're adding a component
            if len(join_point.args) > 1:
                component = join_point.args[1]
                transaction.add_change({
                    'type': 'component_add',
                    'entity': join_point.target,
                    'component_type': type(component)
                })
                
        elif method_name == "remove_component" and hasattr(join_point.target, 'get_component'):
            # Record component before removal
            if len(join_point.args) > 1:
                component_type = join_point.args[1]
                component = join_point.target.get_component(component_type)
                if component:
                    transaction.add_change({
                        'type': 'component_remove',
                        'entity': join_point.target,
                        'component': component,
                        'component_type': component_type
                    })
                    
    def _record_change(self, join_point: JoinPoint, transaction: Transaction, result: Any):
        """Record change after successful execution"""
        # Additional change recording if needed
        pass
        
    def add_transactional_method(self, method_signature: str):
        """Add method to transactional methods"""
        self.transactional_methods.add(method_signature)
        
    def remove_transactional_method(self, method_signature: str):
        """Remove method from transactional methods"""
        self.transactional_methods.discard(method_signature)
        
    @contextmanager
    def transaction(self):
        """Context manager for explicit transactions"""
        transaction = self.transaction_manager.begin_transaction()
        
        try:
            yield transaction
            self.transaction_manager.commit_transaction(transaction)
            
        except Exception:
            self.transaction_manager.rollback_transaction(transaction)
            raise