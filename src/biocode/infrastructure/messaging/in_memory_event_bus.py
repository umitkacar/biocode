"""In-Memory Event Bus Implementation"""
import asyncio
from collections import defaultdict
from typing import Any, Callable, Dict, List, Type, Optional
import logging
from datetime import datetime

from biocode.application.interfaces.event_bus import EventBus
# Import removed - will use Any type for events


logger = logging.getLogger(__name__)


class InMemoryEventBus(EventBus):
    """
    In-memory implementation of EventBus.
    Suitable for single-process applications and testing.
    """
    
    def __init__(self):
        # Event type -> List of handlers
        self._handlers: Dict[Type[Any], List[Callable]] = defaultdict(list)
        
        # Event history for debugging/testing
        self._event_history: List[Dict[str, Any]] = []
        self._max_history_size = 1000
        
        # Async queue for event processing
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._processing_task: Optional[asyncio.Task] = None
        self._running = False
        
    async def start(self):
        """Start the event bus processing"""
        if not self._running:
            self._running = True
            self._processing_task = asyncio.create_task(self._process_events())
            logger.info("InMemoryEventBus started")
            
    async def stop(self):
        """Stop the event bus processing"""
        if self._running:
            self._running = False
            if self._processing_task:
                self._processing_task.cancel()
                try:
                    await self._processing_task
                except asyncio.CancelledError:
                    pass
            logger.info("InMemoryEventBus stopped")
            
    async def publish(self, event: Any) -> None:
        """Publish an event to the bus"""
        # Add to history
        self._add_to_history(event)
        
        # Queue for async processing
        await self._event_queue.put(event)
        
        logger.debug(
            f"Published event: {event.get_event_type()} "
            f"for aggregate: {event.get_aggregate_id()}"
        )
        
    async def publish_batch(self, events: List[Any]) -> None:
        """Publish multiple events"""
        for event in events:
            await self.publish(event)
            
    async def subscribe(
        self, 
        event_type: Type[Any], 
        handler: Callable[[Any], Any]
    ) -> None:
        """Subscribe to an event type"""
        self._handlers[event_type].append(handler)
        
        logger.info(
            f"Subscribed handler {handler.__name__} "
            f"to event type {event_type.__name__}"
        )
        
    async def unsubscribe(
        self, 
        event_type: Type[Any], 
        handler: Callable[[Any], Any]
    ) -> None:
        """Unsubscribe from an event type"""
        if handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)
            
            logger.info(
                f"Unsubscribed handler {handler.__name__} "
                f"from event type {event_type.__name__}"
            )
            
    async def _process_events(self):
        """Process events from the queue"""
        logger.info("Event processing started")
        
        while self._running:
            try:
                # Wait for event with timeout
                event = await asyncio.wait_for(
                    self._event_queue.get(), 
                    timeout=1.0
                )
                
                # Process the event
                await self._dispatch_event(event)
                
            except asyncio.TimeoutError:
                # No events to process, continue
                continue
            except Exception as e:
                logger.error(f"Error processing event: {e}", exc_info=True)
                
        logger.info("Event processing stopped")
        
    async def _dispatch_event(self, event: Any):
        """Dispatch event to all registered handlers"""
        event_type = type(event)
        handlers = self._handlers.get(event_type, [])
        
        # Also check for base class handlers
        for base_type in event_type.__bases__:
            if issubclass(base_type, Any):
                handlers.extend(self._handlers.get(base_type, []))
                
        if not handlers:
            logger.debug(
                f"No handlers registered for event type: {event_type.__name__}"
            )
            return
            
        # Execute handlers concurrently
        tasks = []
        for handler in handlers:
            task = self._execute_handler(handler, event)
            tasks.append(task)
            
        # Wait for all handlers to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Log any errors
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(
                    f"Handler {handlers[i].__name__} failed: {result}",
                    exc_info=result
                )
                
    async def _execute_handler(
        self, 
        handler: Callable[[Any], Any], 
        event: Any
    ):
        """Execute a single handler"""
        try:
            # Check if handler is async
            if asyncio.iscoroutinefunction(handler):
                return await handler(event)
            else:
                # Run sync handler in thread pool
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, handler, event)
                
        except Exception as e:
            logger.error(
                f"Error in handler {handler.__name__}: {e}",
                exc_info=True
            )
            raise
            
    def _add_to_history(self, event: Any):
        """Add event to history for debugging"""
        self._event_history.append({
            "event_id": event.event_id,
            "event_type": event.get_event_type(),
            "aggregate_id": event.get_aggregate_id(),
            "timestamp": event.occurred_at,
            "data": event.__dict__
        })
        
        # Trim history if too large
        if len(self._event_history) > self._max_history_size:
            self._event_history = self._event_history[-self._max_history_size:]
            
    def get_event_history(
        self, 
        event_type: Optional[str] = None,
        aggregate_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get event history for debugging"""
        history = self._event_history
        
        # Filter by event type
        if event_type:
            history = [h for h in history if h["event_type"] == event_type]
            
        # Filter by aggregate ID
        if aggregate_id:
            history = [h for h in history if h["aggregate_id"] == aggregate_id]
            
        # Return limited results
        return history[-limit:]
        
    def clear_history(self):
        """Clear event history"""
        self._event_history.clear()
        
    def get_handler_count(self, event_type: Type[Any]) -> int:
        """Get number of handlers for an event type"""
        return len(self._handlers.get(event_type, []))
        
    def get_all_handlers(self) -> Dict[str, List[str]]:
        """Get all registered handlers (for debugging)"""
        return {
            event_type.__name__: [h.__name__ for h in handlers]
            for event_type, handlers in self._handlers.items()
        }
        
    async def wait_for_empty_queue(self, timeout: float = 5.0):
        """Wait for the event queue to be empty (useful for testing)"""
        start_time = asyncio.get_event_loop().time()
        
        while not self._event_queue.empty():
            if asyncio.get_event_loop().time() - start_time > timeout:
                raise TimeoutError("Event queue did not empty in time")
                
            await asyncio.sleep(0.1)


# Example event handlers
class LoggingEventHandler:
    """Example handler that logs all events"""
    
    def __init__(self, logger_name: str = "event_log"):
        self.logger = logging.getLogger(logger_name)
        
    async def handle_all_events(self, event: Any):
        """Log any domain event"""
        self.logger.info(
            f"Event: {event.get_event_type()} | "
            f"Aggregate: {event.get_aggregate_id()} | "
            f"Time: {event.occurred_at}"
        )


class MetricsEventHandler:
    """Example handler that collects metrics from events"""
    
    def __init__(self):
        self.event_counts: Dict[str, int] = defaultdict(int)
        self.last_event_time: Dict[str, datetime] = {}
        
    async def handle_all_events(self, event: Any):
        """Count events by type"""
        event_type = event.get_event_type()
        self.event_counts[event_type] += 1
        self.last_event_time[event_type] = event.occurred_at
        
    def get_metrics(self) -> Dict[str, Any]:
        """Get collected metrics"""
        return {
            "event_counts": dict(self.event_counts),
            "last_event_times": {
                k: v.isoformat() for k, v in self.last_event_time.items()
            }
        }