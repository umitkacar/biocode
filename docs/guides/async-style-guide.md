# 🔄 Async/Sync Style Guide

## 📋 Genel Prensipler

### 1. **I/O Operasyonları = Async**
Tüm I/O işlemleri (network, disk, database) async olmalı:
```python
# ✅ Doğru
async def read_data(self, path: str) -> str:
    async with aiofiles.open(path) as f:
        return await f.read()

# ❌ Yanlış
def read_data(self, path: str) -> str:
    with open(path) as f:
        return f.read()
```

### 2. **CPU-Bound = Sync (with Executor)**
CPU yoğun işlemler sync olmalı ama executor ile çalıştırılmalı:
```python
# ✅ Doğru
async def heavy_computation(self, data: Any) -> Any:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(self.executor, self._compute, data)

def _compute(self, data: Any) -> Any:
    # CPU intensive work
    return processed_data
```

### 3. **Cell Operasyonları**
```python
# ✅ Doğru - Async for operations that might wait
async def perform_operation(self, operation: str, *args) -> Any:
    async with self.operation_lock:
        result = await self._execute_operation(operation, *args)
        return result

# ✅ Doğru - Sync for quick state changes
def update_health(self, amount: float):
    self.health_score = max(0, min(100, self.health_score + amount))
```

## 🧬 Code Organism Spesifik Kurallar

### CodeCell
- `perform_operation()` → **async** (might wait for resources)
- `heal()`, `infect()` → **sync** (quick state change)
- `receive_signal()` → **async** (inter-cell communication)
- `get_health_report()` → **sync** (read-only)

### CodeTissue
- `grow_cell()` → **sync** (object creation)
- `send_signal()` → **async** (communication)
- `execute_coordinated_operation()` → **async** (multi-cell coordination)
- `transaction()` → **sync context manager** (wraps async operations)

### CodeOrgan
- `process_request()` → **async** (I/O and coordination)
- `add_tissue()` → **sync** (registration)
- `calculate_health()` → **sync** (computation)
- `hot_swap_tissue()` → **async** (gradual migration)

### CodeSystem
- `process_request()` → **async** (orchestration)
- `broadcast()` → **async** (multi-organ communication)
- `self_diagnose()` → **sync** (health check)
- `optimize()` → **async** (background optimization)

## 🔧 Praktik Örnekler

### 1. Mixed Operations
```python
class MyTissue:
    async def complex_operation(self, data: Any) -> Any:
        # Sync preparation
        prepared_data = self._prepare_data(data)  # sync
        
        # Async I/O
        external_data = await self._fetch_external_data()  # async
        
        # Parallel async operations
        results = await asyncio.gather(
            self._process_cell_1(prepared_data),
            self._process_cell_2(external_data)
        )
        
        # Sync finalization
        return self._finalize_results(results)  # sync
```

### 2. Transaction Pattern
```python
@contextmanager
def transaction(self, tx_id: str):
    """Sync context manager for async operations"""
    tx = Transaction(tx_id)
    try:
        yield tx
        # Commit might be async internally
        asyncio.create_task(self._commit_async(tx))
    except Exception:
        asyncio.create_task(self._rollback_async(tx))
        raise
```

### 3. Event Handler Pattern
```python
async def handle_event(self, event: Dict[str, Any]):
    """Async event handler"""
    # Quick sync validation
    if not self._validate_event(event):  # sync
        return
        
    # Async processing
    await self._process_event(event)  # async
    
    # Async notification
    await self._notify_listeners(event)  # async
```

## 📊 Decision Matrix

| Operation Type | Sync/Async | Reason |
|---------------|------------|---------|
| State read | Sync | Quick memory access |
| State write | Sync | Quick memory update |
| Network call | Async | I/O wait |
| File I/O | Async | Disk wait |
| Database query | Async | Network + disk wait |
| Heavy computation | Sync + Executor | CPU bound |
| Inter-cell communication | Async | Potential wait |
| Object creation | Sync | Memory allocation |
| Cleanup/destruction | Sync/Async | Depends on resources |

## 🚨 Common Pitfalls

### 1. Mixing in Constructors
```python
# ❌ Yanlış - Constructor'da async
class BadCell:
    async def __init__(self):  # Python doesn't support this
        self.data = await fetch_data()

# ✅ Doğru - Factory pattern
class GoodCell:
    @classmethod
    async def create(cls):
        instance = cls()
        instance.data = await fetch_data()
        return instance
```

### 2. Forgetting await
```python
# ❌ Yanlış
async def process(self):
    self.send_signal(data)  # Forgot await!

# ✅ Doğru
async def process(self):
    await self.send_signal(data)
```

### 3. Unnecessary async
```python
# ❌ Yanlış - No need for async
async def get_name(self):
    return self.name

# ✅ Doğru
def get_name(self):
    return self.name
```

## 🎯 Testing Guidelines

### Async Tests
```python
import pytest

@pytest.mark.asyncio
async def test_async_operation():
    cell = CodeCell("test")
    result = await cell.perform_operation("test_op")
    assert result is not None

def test_sync_operation():
    cell = CodeCell("test")
    cell.heal()
    assert cell.health_score > 0
```

## 📝 Checklist for New Code

- [ ] All I/O operations are async
- [ ] CPU-bound operations use executor
- [ ] No async in `__init__`
- [ ] All async calls have `await`
- [ ] Sync methods don't call async without proper handling
- [ ] Tests use `pytest.mark.asyncio` for async tests
- [ ] Documentation clearly marks async methods