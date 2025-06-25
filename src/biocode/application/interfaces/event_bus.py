"""Event bus interface"""
from abc import ABC, abstractmethod
from typing import Any, Callable, Type


class EventBus(ABC):
    @abstractmethod
    async def publish(self, event: Any) -> None:
        """Publish an event"""
        pass
    
    @abstractmethod
    async def subscribe(self, event_type: Type, handler: Callable) -> None:
        """Subscribe to an event type"""
        pass
