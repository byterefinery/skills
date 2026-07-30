# Basic Commands

Core key management and string operations form the foundation of valkey-py usage.

## Key Operations

```python
import valkey
r = valkey.Valkey(host="localhost", port=6379, decode_responses=True)

# Check existence
r.exists("key")           # 1 or 0
r.exists("k1", "k2", "k3")  # count of existing keys

# Delete
r.delete("key")           # 1 if deleted, 0 if not found
r.delete("k1", "k2", "k3")  # count of deleted keys
del r["key"]              # __delitem__ syntax

# Rename
r.rename("old", "new")          # overwrite target
r.renamenx("old", "new")        # only if target doesn't exist

# Copy
r.copy("source", "dest", db=1)  # copy key to another database

# Type
r.type("key")  # "string", "list", "set", "zset", "hash", "stream", etc.

# Scan keys
for key in r.scan_iter(match="prefix:*", count=100):
    print(key)

# Full scan (returns cursor, keys)
cursor, keys = r.scan(cursor=0, match="prefix:*", count=100)
while keys:
    cursor, keys = r.scan(cursor=cursor, match="prefix:*", count=100)
```

### Key Iteration

`scan_iter()` is a convenience generator that handles cursor pagination:

```python
# Iterate all keys
for key in r.scan_iter():
    print(key)

# With pattern
for key in r.scan_iter(match="user:*", count=200):
    print(key)

# With type filter
for key in r.scan_iter(type="string"):
    print(key)
```

## Expiration and TTL

```python
# Set expiration
r.expire("key", 60)           # 60 seconds
r.expire("key", 60, nx=True)  # only if key has no expiry
r.expire("key", 60, xx=True)  # only if key already has expiry
r.expire("key", 60, gt=True)  # only if new TTL > current TTL
r.expire("key", 60, lt=True)  # always set (lower TTL wins)

# Absolute expiration
r.expireat("key", timestamp)       # Unix timestamp
r.pexpireat("key", ms_timestamp)   # milliseconds

# Check TTL
r.ttl("key")      # seconds remaining, -1 = no expiry, -2 = key doesn't exist
r.pttl("key")     # milliseconds remaining

# Get and set expiry in one call
r.getex("key", ex=60)       # GET + SETEX
r.getex("key", px=60000)    # GET + PSETEX
r.getex("key", exat=123456) # GET + EXPIREAT
r.getex("key", persist=True)# GET + remove expiry

# Remove expiry
r.persist("key")
```

## String Commands

```python
# Set
r.set("key", "value")                    # basic set
r.set("key", "value", ex=60)             # with expiration (seconds)
r.set("key", "value", px=60000)          # with expiration (ms)
r.set("key", "value", nx=True)           # only if not exists
r.set("key", "value", xx=True)           # only if exists
r.set("key", "value", keepttl=True)      # preserve existing TTL
r.set("key", "value", get=True)          # return old value
result = r.set("key", "value", nx=True, get=True)
# result: True (set succeeded), old_value returned via get

# Get
r.get("key")             # value or None
r.getdel("key")          # get and delete atomically
r.getrange("key", 0, 3)  # substring by byte range
r.getset("key", "new")   # deprecated, use set(..., get=True)

# Set multiple
r.mset({"k1": "v1", "k2": "v2"})
r.msetnx({"k1": "v1", "k2": "v2"})  # only if none exist

# Get multiple
r.mget("k1", "k2", "k3")  # [v1, v2, v3] or None for missing

# Append
r.append("key", "suffix")  # returns new length

# String length
r.strlen("key")

# Increment/Decrement
r.incr("counter")      # +1, returns new value
r.incrby("counter", 5) # +N
r.incrbyfloat("counter", 1.5)
r.decr("counter")      # -1
r.decrby("counter", 5) # -N

# Set range
r.setrange("key", 5, "XY")  # overwrite bytes at offset 5

# Set with options dict
r.set("key", "value", ex=60, nx=True)
```

### SET Return Values

```python
r.set("key", "value")           # True
r.set("key", "value", nx=True)  # True if set, False if already existed
r.set("key", "value", nx=True, get=True)  # True/False, and old value is returned
```

When `get=True` is used with `nx=True` or `xx=True`, the return value is a tuple-like response where you get both the SET result and the previous value.

## Bit Operations

```python
# Bit count
r.bitcount("key")
r.bitcount("key", start=0, end=-1)  # byte range

# Bit position
r.bitpos("key", 1)      # find first bit set to 1
r.bitpos("key", 0)      # find first bit set to 0
r.bitpos("key", 1, start=10, end=20)

# Bit operations
r.bitop("AND", "dest", "key1", "key2")  # AND, OR, XOR, NOT

# Bitfield
r.bitfield("key", "SET", "i8", 0, 5)
r.bitfield("key", "GET", "i8", 0)

# Bitfield with multiple operations (returns list)
r.bitfield("key",
    "GET", "i8", 0,
    "SET", "i8", 0, 5,
    "INCRBY", "i8", 0, 1,
)
```

## Sorted Set Basics

```python
# Add
r.zadd("scores", {"alice": 100, "bob": 95, "charlie": 85})

# Score
r.zscore("scores", "alice")  # 100.0

# Rank (0-based, ascending)
r.zrank("scores", "charlie")   # 0 (lowest score)
r.zrevrank("scores", "charlie") # 2 (highest score)

# Range
r.zrange("scores", 0, -1)              # all members
r.zrange("scores", 0, -1, withscores=True)  # with scores
r.zrangebyscore("scores", 80, 100)     # by score range
r.zrangebyscore("scores", "-inf", "+inf", start=0, num=10)

# Count
r.zcard("scores")           # total members
r.zcount("scores", 80, 100) # members in score range

# Remove
r.zrem("scores", "alice")

# Increment score
r.zincrby("scores", 5, "bob")

# Remove by rank
r.zremrangebyrank("scores", 0, 0)   # remove lowest
r.zremrangebyscore("scores", 0, 50) # remove by score range
```

## Hash Operations

```python
# Set
r.hset("user:1", "name", "Alice")
r.hset("user:1", {"name": "Alice", "age": "30", "email": "a@b.com"})
r.hsetnx("user:1", "name", "Bob")  # only if field doesn't exist

# Get
r.hget("user:1", "name")
r.hmget("user:1", "name", "age")
r.hgetall("user:1")  # {"name": "Alice", "age": "30", ...}

# Keys/Values
r.hkeys("user:1")
r.hvals("user:1")

# Length
r.hlen("user:1")

# Exists
r.hexists("user:1", "name")

# Delete
r.hdel("user:1", "field1", "field2")

# Increment
r.hincrby("user:1", "age", 1)
r.hincrbyfloat("user:1", "score", 0.5)

# Iterate large hashes
for field, value in r.hscan_iter("user:1"):
    print(field, value)
```

## List Operations

```python
# Push
r.lpush("tasks", "task1")        # left push
r.rpush("tasks", "task2")        # right push
r.lpushx("tasks", "task3")       # only if list exists
r.rpushx("tasks", "task4")       # only if list exists

# Pop
r.lpop("tasks")                  # pop from left
r.rpop("tasks")                  # pop from right
r.blpop("tasks", timeout=5)      # blocking pop from left
r.brpop("tasks", timeout=5)      # blocking pop from right
r.blpop(["tasks", "backup"], timeout=5)  # blocking pop from multiple lists

# Range
r.lrange("tasks", 0, -1)         # all elements
r.lrange("tasks", 0, 9)          # first 10
r.lrange("tasks", -5, -1)        # last 5

# Index
r.lindex("tasks", 0)             # first element
r.lindex("tasks", -1)            # last element

# Length
r.llen("tasks")

# Set by index
r.lset("tasks", 0, "new_value")

# Remove
r.lrem("tasks", "value", num=0)  # remove all occurrences
r.lrem("tasks", "value", num=2)  # remove first 2 from left
r.lrem("tasks", "value", num=-2) # remove last 2 from right

# Trim
r.ltrim("tasks", 0, 99)  # keep first 100 elements

# Insert
r.linsert("tasks", "BEFORE", "pivot", "new_value")
r.linsert("tasks", "AFTER", "pivot", "new_value")

# Move between lists
r.rpoplpush("source", "dest")
r.brpoplpush("source", "dest", timeout=5)
```

## Set Operations

```python
# Add
r.sadd("tags", "python", "redis", "valkey")

# Members
r.smembers("tags")

# Check membership
r.sismember("tags", "python")

# Cardinality
r.scard("tags")

# Remove
r.srem("tags", "redis")

# Pop random
r.spop("tags")
r.spop("tags", 3)  # pop N random members

# Random member
r.srandmember("tags")
r.srandmember("tags", 3)  # N random members (with replacement)

# Intersection, Union, Difference
r.sinter("set1", "set2")
r.sunion("set1", "set2")
r.sdiff("set1", "set2")

# Store results
r.sinterstore("result", "set1", "set2")
r.sunionstore("result", "set1", "set2")
r.sdiffstore("result", "set1", "set2")

# Move
r.smove("source", "dest", "member")

# Iterate
for member in r.sscan_iter("tags"):
    print(member)
```

## Server Management

```python
# Ping
r.ping()  # "PONG"

# Info
r.info()                    # all sections
r.info("memory")            # specific section
r.info("cpu")

# DB size
r.dbsize()

# Select database
r.select(1)

# Flush
r.flushdb()           # current database
r.flushall()          # all databases
r.flushdb(async=True) # asynchronous flush

# Config
r.config_get("maxmemory")
r.config_set("maxmemory", "1gb")
r.config_resetstat()
r.config_rewrite()

# Slow log
r.slowlog_get(10)
r.slowlog_len()
r.slowlog_reset()

# Time
r.time()  # (seconds, microseconds)

# Last save
r.lastsave()

# Shutdown
r.shutdown(save=True)
```

## Scan Family

All scan commands use cursor-based iteration:

```python
# Keys
for key in r.scan_iter(match="user:*", count=100):
    print(key)

# Hash fields
for field, value in r.hscan_iter("hash_key"):
    print(field, value)

# Set members
for member in r.sscan_iter("set_key"):
    print(member)

# Sorted set members
for member, score in r.zscan_iter("zset_key"):
    print(member, score)
```

Each `scan_iter` handles cursor pagination automatically. Use `match` for pattern filtering and `count` to hint batch size.
