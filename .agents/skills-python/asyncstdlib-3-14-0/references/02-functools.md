# Functools

Async versions of `functools` utilities — reduction, caching, and cached properties.

## reduce

```python
async def reduce(function: Callable[[T, T], T], iterable: AnyIterable[T], /, initial: T = <no default>) -> T
```

Cumulatively apply a function across an iterable. The function receives the accumulated value and the next item. If `initial` is provided, it is used as the starting value; if the iterable is empty with no initial, `TypeError` is raised. If the combination of initial and iterable has exactly one item, it is returned without calling the function.

```python
# Sum via reduce
total = await a.reduce(lambda x, y: x + y, async_numbers, initial=0)

# Async reduction
async def combine(acc, item):
    return await merge(acc, item)

result = await a.reduce(combine, async_items, initial=base)
```

## lru_cache

```python
def lru_cache(maxsize: int | None = 128, typed: bool = False) -> Callable[[AC], LRUAsyncCallable[AC]]
```

Least Recently Used cache for async functions. Stores call arguments and their *awaited* return value. When cached arguments are called again, the underlying function is not invoked — side effects and scheduling are skipped.

**maxsize behavior:**
- Positive integer: up to `maxsize` entries; oldest evicted on overflow
- Zero or negative: cache disabled (every call is forwarded, counted as miss)
- `None`: unbounded cache (never evicts automatically)

**typed:** if `True`, argument values are compared by value *and* type (`3` and `3.0` are distinct). Not applied recursively.

The cache supports overlapping `await` calls if the wrapped function does, but is not thread-safe.

### Cache Methods

Wrapped functions gain these methods:

- **`cache_info()`** → `CacheInfo(hits, misses, maxsize, currsize)` — NamedTuple with cache statistics
- **`cache_parameters()`** → `CacheParameters(maxsize, typed)` — TypedDict with configuration
- **`cache_clear()`** — evict all entries and reset counters
- **`cache_discard(*args, **kwargs)`** — evict a specific argument pattern

```python
@a.lru_cache(maxsize=256)
async def fetch(url):
    return await http.get(url)

result = await fetch("https://api.example.com/data")
print(fetch.cache_info())  # CacheInfo(hits=0, misses=1, maxsize=256, currsize=1)

# Subsequent call with same args returns cached result
result2 = await fetch("https://api.example.com/data")  # instant

# Remove specific entry
fetch.cache_discard("https://api.example.com/data")

# Clear all
fetch.cache_clear()
```

### Unbounded Decorator Form

```python
@a.lru_cache  # equivalent to lru_cache(maxsize=128)
async def compute(x):
    ...
```

### Descriptor Support

Works as a method decorator — binds correctly on class instances:

```python
class Service:
    @a.lru_cache(maxsize=64)
    async def get_config(self, key):
        return await self._fetch(key)
```

## cache

```python
def cache(user_function: AC) -> LRUAsyncCallable[AC]
```

Simple unbounded memoization for async functions. Equivalent to `@a.lru_cache(maxsize=None)`. Use when cache size is not a concern and you want all results cached indefinitely.

```python
@a.cache
async def expensive_computation(x):
    return await do_work(x)
```

## cached_property

```python
def cached_property(type_or_getter: Type[AsyncContextManager] | Callable[[T], Awaitable[R]], /) -> CachedProperty[T, R]
```

Transform an async method into a cached attribute. The getter runs once per instance; subsequent `await` accesses return the cached value without re-execution. Use `del instance.attr` to invalidate and force re-computation.

### Basic Usage

```python
class Resource:
    def __init__(self, url):
        self.url = url

    @a.cached_property
    async def data(self):
        return await http.get(self.url)

resource = Resource("https://example.com")
print(await resource.data)  # fetches
print(await resource.data)  # instant — cached
del resource.data           # invalidate
print(await resource.data)  # fetches again
```

### Concurrency-Safe Usage

By default, concurrent `await` on the same uncached property may run the getter multiple times. Pass an async context manager type (like `asyncio.Lock`) to serialize access:

```python
from asyncio import Lock

class Resource:
    @a.cached_property(Lock)
    async def data(self):
        return await http.get(self.url)

# Both awaits share the same result
results = await gather(resource.data, resource.data)
```

### Requirements

- Instances must have a mutable `__dict__` — classes using `__slots__` without including `"__dict__"` will raise `TypeError`
- Does not support `setter` or `deleter` (unlike `property`)

## CacheInfo

```python
class CacheInfo(NamedTuple):
    hits: int          # results read from cache
    misses: int        # freshly computed results
    maxsize: int | None  # max entries (None = unbounded)
    currsize: int      # current number of entries
```

Unpackable: `hits, misses, maxsize, currsize = cache.cache_info()`

## CacheParameters

```python
class CacheParameters(TypedDict):
    maxsize: int | None
    typed: bool
```
