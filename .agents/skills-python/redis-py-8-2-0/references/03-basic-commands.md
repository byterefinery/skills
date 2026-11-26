# Basic Commands

## Key Management

```python
# Check existence
r.exists("key")           # int — number of existing keys
r.exists("k1", "k2", "k3")  # multiple keys

# Delete
r.delete("key")           # int — number of keys deleted
r.delete("k1", "k2")      # delete multiple

# Expiration
r.expire("key", 3600)     # TTL in seconds
r.pexpire("key", 3600000) # TTL in milliseconds
r.expireat("key", timestamp)    # Absolute Unix timestamp (seconds)
r.pexpireat("key", timestamp)   # Absolute Unix timestamp (milliseconds)
r.persist("key")          # Remove expiration

# Query expiration
r.ttl("key")   # seconds remaining (-1 = no TTL, -2 = key doesn't exist)
r.pttl("key")  # milliseconds remaining

# Type
r.type("key")  # "string", "list", "set", "hash", "zset", "stream", etc.

# Rename
r.rename("old", "new")        # Overwrite destination
r.renamenx("old", "new")      # Only if destination doesn't exist

# Random key
r.randomkey()  # Return a random key name

# Sort
r.sort("mylist", alpha=True, start=0, num=10)
```

## Scanning Keys

```python
# SCAN — cursor-based iteration (non-blocking)
cursor = 0
while True:
    cursor, keys = r.scan(cursor=cursor, match="user:*", count=100)
    for key in keys:
        process(key)
    if cursor == 0:
        break

# SSCAN, HSCAN, ZSCAN — scan within a collection
cursor = 0
while True:
    cursor, members = r.sscan("myset", cursor=cursor, match="*", count=100)
    for member in members:
        process(member)
    if cursor == 0:
        break

# SCAN with type filter
cursor, keys = r.scan(match="*", count=100, type="string")
```

**Never use `KEYS` in production** — it blocks the server. Use `SCAN` for iteration.

```python
# Avoid this in production:
r.keys("user:*")  # Blocks server for entire key space scan

# Use this instead:
for key in r.scan_iter(match="user:*", count=100):
    process(key)
```

## String Commands

```python
# Set
r.set("key", "value")                    # Basic set
r.set("key", "value", ex=3600)           # With expiration (seconds)
r.set("key", "value", px=3600000)        # With expiration (milliseconds)
r.set("key", "value", nx=True)           # Only if key doesn't exist
r.set("key", "value", xx=True)           # Only if key exists
r.set("key", "value", keepttl=True)      # Preserve existing TTL
r.set("key", "value", get=True)          # Return old value (RESP3)

# Get
r.get("key")              # Value or None
r.getdel("key")           # Get and delete atomically
r.getrange("key", 0, 9)   # Substring
r.getset("key", "new")    # Get old value, set new value

# Multiple
r.mset({"k1": "v1", "k2": "v2"})    # Set multiple
r.mget("k1", "k2", "k3")            # Get multiple

# Append
r.append("key", "suffix")  # Append to string value

# Increment/Decrement
r.incr("counter")          # Increment by 1, return new value
r.incrby("counter", 10)    # Increment by N
r.incrbyfloat("counter", 1.5)  # Increment by float
r.decr("counter")          # Decrement by 1
r.decrby("counter", 10)    # Decrement by N

# String length
r.strlen("key")  # Length of string value in bytes
```

## Hash Commands

```python
# Set
r.hset("hash", "field", "value")              # Set single field
r.hset("hash", mapping={"f1": "v1", "f2": "v2"})  # Set multiple fields
r.hsetnx("hash", "field", "value")            # Set only if field doesn't exist

# Get
r.hget("hash", "field")       # Get single field
r.hgetall("hash")             # Get all fields as dict
r.hmget("hash", "f1", "f2")   # Get multiple fields

# Delete
r.hdel("hash", "field1", "field2")  # Delete fields

# Keys/Values
r.hkeys("hash")   # All field names
r.hvals("hash")   # All field values
r.hlen("hash")    # Number of fields

# Increment
r.hincrby("hash", "field", 1)      # Increment integer field
r.hincrbyfloat("hash", "field", 1.5)  # Increment float field

# Exists
r.hexists("hash", "field")  # Check if field exists

# Iterate
for field, value in r.hscan_iter("hash", match="*", count=100):
    process(field, value)
```

## List Commands

```python
# Push
r.lpush("list", "value")       # Push to left (head)
r.rpush("list", "value")       # Push to right (tail)
r.lpushx("list", "value")      # Push only if list exists
r.rpushx("list", "value")      # Push only if list exists

# Pop
r.lpop("list")    # Pop from left
r.rpop("list")    # Pop from right
r.lpop("list", 3) # Pop N elements (returns list)

# Atomic transfer
r.rpoplpush("source", "dest")  # Pop from source, push to dest

# Get/Set
r.lindex("list", 0)    # Get by index
r.lset("list", 0, "v") # Set by index
r.lrange("list", 0, -1)  # Get range of elements

# Length
r.llen("list")  # Number of elements

# Trim
r.ltrim("list", 0, 9)  # Keep only elements 0-9

# Remove
r.lrem("list", "value", 0)  # Remove occurrences (0 = all, positive = from head, negative = from tail)

# Insert
r.linsert("list", "BEFORE", "pivot", "new")  # Insert before/after pivot
```

## Set Commands

```python
# Add
r.sadd("set", "member1", "member2")  # Add members
r.sadd("set", *members)

# Remove
r.srem("set", "member")  # Remove members

# Members
r.smembers("set")        # All members
r.scard("set")           # Cardinality (count)
r.sismember("set", "m")  # Check membership

# Random
r.srandmember("set")     # Random member
r.srandmember("set", 5)  # N random members

# Pop
r.spop("set")     # Remove and return random member
r.spop("set", 3)  # Remove and return N random members

# Operations
r.sunion("s1", "s2")       # Union
r.sinter("s1", "s2")       # Intersection
r.sdiff("s1", "s2")        # Difference

# Store results
r.sunionstore("dest", "s1", "s2")
r.sinterstore("dest", "s1", "s2")
r.sdiffstore("dest", "s1", "s2")

# Iterate
for member in r.sscan_iter("set", match="*", count=100):
    process(member)
```

## Sorted Set Commands

```python
# Add
r.zadd("zset", {"member1": 1.0, "member2": 2.5})
r.zadd("zset", {"m": 3.0}, nx=True)   # Only add new members
r.zadd("zset", {"m": 3.0}, xx=True)   # Only update existing

# Score
r.zscore("zset", "member")  # Get score
r.zincrby("zset", 1.5, "member")  # Increment score

# Range
r.zrange("zset", 0, -1)              # All members by rank
r.zrange("zset", 0, -1, withscores=True)  # With scores
r.zrangebyscore("zset", "-inf", "+inf")   # By score range
r.zrangebyscore("zset", 0, 100, start=0, num=10)  # Paginated

# Reverse range
r.zrevrange("zset", 0, 9)  # Highest scores first

# Rank
r.zrank("zset", "member")    # Rank (0 = lowest score)
r.zrevrank("zset", "member") # Rank (0 = highest score)

# Count/Remove
r.zcard("zset")              # Number of members
r.zcount("zset", 0, 100)     # Count in score range
r.zrem("zset", "member")     # Remove members
r.zremrangebyrank("zset", 0, 9)    # Remove by rank range
r.zremrangebyscore("zset", 0, 100) # Remove by score range

# Operations
r.zunionstore("dest", ["s1", "s2"])
r.zinterstore("dest", ["s1", "s2"])
```

## Stream Commands

```python
# Add entries
r.xadd("stream", {"field": "value", "field2": "value2"})
r.xadd("stream", {"f": "v"}, id="0-1")    # Explicit ID
r.xadd("stream", {"f": "v"}, maxlen=1000, approximate=True)  # Trim

# Read
r.xread([{"stream": "stream", "id": "0-0"}], block=0)
r.xread([{"stream": "s1", "id": "0-0"}, {"stream": "s2", "id": "0-0"}], count=10)

# Range
r.xrange("stream", "-", "+")
r.xrange("stream", start="0-0", end="0-5", count=10)

# Consumer groups
r.xgroup_create("stream", "group", id="0-0")
r.xreadgroup("group", "consumer", {"stream": "stream": "last-id"})
r.xack("stream", "group", "id1", "id2")
r.xpending("stream", "group")
```

## Bit Operations

```python
# Set/Get bits
r.setbit("key", offset, 1)
r.getbit("key", offset)

# Count
r.bitcount("key")
r.bitcount("key", start=0, end=-1)

# Operations
r.bitop("AND", "dest", "k1", "k2")
r.bitop("OR", "dest", "k1", "k2")
r.bitop("XOR", "dest", "k1", "k2")
r.bitop("NOT", "dest", "k1")

# Position
r.bitpos("key", 1)    # Find first bit set to 1
r.bitpos("key", 0)    # Find first bit set to 0
```

## Geo Commands

```python
# Add
r.geoadd("locations", {"place1": 13.361389, 38.115556, "place2": 15.087269, 37.502669})

# Distance
r.geodist("locations", "place1", "place2", unit="km")

# Coordinates
r.geopos("locations", "place1")

# Radius
r.georadius("locations", 15, 37, 200, unit="km")
r.georadiusbymember("locations", "place1", 200, unit="km")

# Hash
r.geohash("locations", "place1", "place2")
```

## HyperLogLog

```python
r.pfadd("hll", "a", "b", "c")
r.pfcount("hll")
r.pfmerge("dest", "hll1", "hll2")
```

## Server Commands

```python
# Ping
r.ping()

# Info
r.info()             # All sections
r.info("memory")     # Specific section
r.info("cpu")

# Database
r.dbsize()           # Number of keys
r.flushdb()          # Flush current database
r.flushall()         # Flush all databases

# Time
r.time()             # Server time as (seconds, microseconds)

# Command
r.command()          # Command info
r.command_count()    # Number of commands
r.command_info()     # Detailed command info
```

## Custom Commands

```python
# Execute arbitrary commands
r.execute_command("CUSTOM.CMD", "arg1", "arg2")

# Set custom response callback
r.set_response_callback("CUSTOM.CMD", lambda r: r.decode())
```
