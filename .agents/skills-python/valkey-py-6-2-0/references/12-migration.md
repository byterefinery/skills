# Migrating from redis-py

Source: README.md (Migration from redis-py), `valkey/__init__.py`.

valkey-py is a fork of redis-py, so most code carries over. The README "encourages you to use the new class names, but to allow for a smooth transition aliases are available":

```python
import valkey as redis

r = redis.Redis(host='localhost', port=6379, db=0)   # works: Redis is an alias of Valkey
r.set('foo', 'bar')      # True
r.get('foo')             # b'bar'
```

## Aliases (defined in `valkey/__init__.py`)

| redis-py name | valkey-py alias target |
|---|---|
| `Redis` | `Valkey` |
| `StrictRedis` | `StrictValkey` |
| `RedisCluster` | `ValkeyCluster` |
| `RedisError` | `ValkeyError` |

Recommended end state: `import valkey` and use `valkey.Valkey` / `valkey.ValkeyCluster` / `valkey.WatchError` etc.

## Practical Migration Checklist

1. **Package name** — `pip install valkey` (the PyPI distribution is `valkey`; import is `import valkey`).
2. **Rename classes** — `Redis` → `Valkey`, `StrictRedis` → `StrictValkey`, `RedisCluster` → `ValkeyCluster`, `RedisError` → `ValkeyError` (aliases keep old names working).
3. **Async import** — `from redis.asyncio import Redis` becomes `from valkey.asyncio import Valkey`.
4. **Behavior is unchanged at the protocol level** — same RESP2/RESP3 support, same connection parameters, same command surface (fork lineage).
5. **Python version** — valkey-py 6.x requires Python 3.11+ (docs/index.rst); older redis-py supported earlier Pythons.
6. **Extras** — `valkey[libvalkey]` adds the compiled parser (gated on libvalkey 4.0.0+).
