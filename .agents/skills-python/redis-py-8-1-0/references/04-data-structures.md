# Data Structures

## String

Redis strings are binary-safe, supporting up to 512MB of data.

```python
# Basic operations
r.set("key", "value")
r.get("key")

# Atomic operations
r.incr("counter")           # Increment (creates key with 0 if missing)
r.incrby("counter", 100)
r.incrbyfloat("counter", 1.5)
r.decr("counter")
r.decrby("counter", 10)

# Substrings
r.getrange("key", 0, 9)     # Characters 0-9
r.setrange("key", 5, "XY")  # Overwrite at offset 5
r.strlen("key")             # Byte length

# Conditional sets
r.set("key", "value", nx=True)   # SET NX — only if not exists
r.set("key", "value", xx=True)   # SET XX — only if exists
r.set("key", "value", nx=True, ex=3600)  # NX + expiration

# Get-and-set patterns
r.getset("key", "new")    # Return old value, set new
r.getdel("key")           # Return value and delete atomically

# Append
r.append("key", "suffix")

# Multiple keys
r.mset({"k1": "v1", "k2": "v2"})
r.mget("k1", "k2")
```

### Use Cases

- Caching computed values
- Session storage
- Counters and rate limiters
- Simple configuration values
- Atomic operations via `INCR`/`SET NX`

## Hash

Redis hashes map fields to values, ideal for objects.

```python
# Set
r.hset("user:1", "name", "Alice")
r.hset("user:1", mapping={"email": "alice@example.com", "age": "30"})
r.hsetnx("user:1", "name", "Bob")  # Only if field doesn't exist

# Get
r.hget("user:1", "name")
r.hgetall("user:1")           # Full object as dict
r.hmget("user:1", "name", "email")

# Modify
r.hdel("user:1", "age")
r.hincrby("user:1", "age", 1)
r.hincrbyfloat("user:1", "score", 0.5)

# Inspect
r.hlen("user:1")              # Field count
r.hexists("user:1", "name")   # Field exists?
r.hkeys("user:1")             # All field names
r.hvals("user:1")             # All field values

# Iterate large hashes
for field, value in r.hscan_iter("user:1", match="*", count=100):
    process(field, value)
```

### Use Cases

- Object storage (users, products, configs)
- Counters per field (page views, feature usage)
- Sets with metadata (each field carries extra data)

## List

Redis lists are linked lists of strings, supporting push/pop from both ends.

```python
# Push
r.lpush("queue", "task1", "task2", "task3")  # Left push (most recent first)
r.rpush("queue", "task4")                     # Right push
r.lpushx("queue", "task5")                    # Only if list exists

# Pop
r.lpop("queue")     # Pop from left
r.rpop("queue")     # Pop from right
r.lpop("queue", 5)  # Pop N elements

# Access
r.lindex("queue", 0)     # First element
r.lindex("queue", -1)    # Last element
r.lrange("queue", 0, 9)  # First 10 elements
r.lrange("queue", -10, -1)  # Last 10 elements
r.llen("queue")          # Length

# Modify
r.lset("queue", 0, "new_value")
r.ltrim("queue", 0, 9)   # Keep only first 10
r.lrem("queue", "value", 0)  # Remove all occurrences
r.linsert("queue", "BEFORE", "pivot", "new")

# Transfer
r.rpoplpush("source", "dest")
```

### Use Cases

- Message queues (LPUSH + BRPOP)
- Recent activity feeds (LPUSH + LRANGE)
- Stacks and queues
- Bounded logs (LPUSH + LTRIM)

## Set

Redis sets are unordered collections of unique strings.

```python
# Add/Remove
r.sadd("tags", "python", "redis", "nosql")
r.srem("tags", "nosql")

# Query
r.smembers("tags")          # All members
r.scard("tags")             # Count
r.sismember("tags", "python")  # Membership test

# Random
r.srandmember("tags")       # One random member
r.srandmember("tags", 3)    # Three random members
r.spop("tags")              # Remove and return random
r.spop("tags", 2)           # Remove and return N random

# Set algebra
r.sunion("set1", "set2")       # Union
r.sinter("set1", "set2")       # Intersection
r.sdiff("set1", "set2")        # Difference
r.sunionstore("dest", "s1", "s2")
r.sinterstore("dest", "s1", "s2")
r.sdiffstore("dest", "s1", "s2")

# Iterate
for member in r.sscan_iter("tags", match="py*", count=100):
    process(member)
```

### Use Cases

- Tagging systems
- Unique visitors tracking
- Common followers (intersection)
- Deduplication
- Random sampling

## Sorted Set

Redis sorted sets order members by score, supporting range queries.

```python
# Add
r.zadd("leaderboard", {"alice": 100, "bob": 200, "carol": 150})
r.zadd("leaderboard", {"dave": 300}, nx=True)  # Only new members
r.zadd("leaderboard", {"alice": 120}, xx=True) # Only update existing

# Score
r.zscore("leaderboard", "alice")
r.zincrby("leaderboard", 10, "alice")

# Range queries
r.zrange("leaderboard", 0, -1)              # All, lowest to highest
r.zrange("leaderboard", -1, 0)              # Reverse (highest first)
r.zrange("leaderboard", 0, 9, withscores=True)  # Top 10 with scores
r.zrevrange("leaderboard", 0, 9)            # Top 10 (highest first)

# By score
r.zrangebyscore("leaderboard", "-inf", "+inf")
r.zrangebyscore("leaderboard", 100, 200)
r.zcount("leaderboard", 100, 200)           # Count in range

# Rank
r.zrank("leaderboard", "alice")             # Position (0 = lowest)
r.zrevrank("leaderboard", "alice")          # Position (0 = highest)

# Remove
r.zrem("leaderboard", "alice")
r.zremrangebyrank("leaderboard", 0, 9)      # Remove bottom 10
r.zremrangebyscore("leaderboard", 0, 100)   # Remove below score 100

# Cardinality
r.zcard("leaderboard")

# Set operations
r.zunionstore("dest", ["s1", "s2"], weights=[2, 1])
r.zinterstore("dest", ["s1", "s2"])
```

### Use Cases

- Leaderboards and rankings
- Timed expiration queues (score = expiration time)
- Rate limiting (sliding window)
- Scheduled jobs
- Top-N queries

## Stream

Redis streams are append-only log data structures with consumer group support.

```python
# Add entries
r.xadd("mystream", {"user": "alice", "action": "login"})
r.xadd("mystream", {"user": "bob", "action": "logout"})
# Returns entry ID: "1690000000000-0"

# With trimming
r.xadd("mystream", {"f": "v"}, maxlen=10000, approximate=True)

# Read
r.xread([{"stream": "mystream", "id": "0-0"}], block=0)
# Returns: [("mystream", [("1690000000000-0", {"user": "alice", ...}), ...])]

# Range
r.xrange("mystream", "-", "+")           # All entries
r.xrange("mystream", "0-0", "0-5")       # First 6 entries
r.xrevrange("mystream", "+", "-", count=10)  # Last 10

# Consumer groups
r.xgroup_create("mystream", "mygroup", id="0-0", mkstream=True)
r.xreadgroup("mygroup", "consumer1", {"mystream": ">"})  # ">" = new entries only

# Acknowledge
r.xack("mystream", "mygroup", "entry-id-1", "entry-id-2")

# Pending
r.xpending("mystream", "mygroup")
r.xpending_range("mystream", "mygroup", "-", "+", 10)

# Delete entries
r.xdel("mystream", "entry-id")
r.xtrim("mystream", maxlen=1000)

# Info
r.xinfo_stream("mystream")
r.xinfo_groups("mystream")
r.xinfo_consumers("mystream", "mygroup")
```

### Use Cases

- Event sourcing
- Message queues with consumer groups
- Activity logs
- Real-time data pipelines
- Chat message history

## Bitmap

Bitmaps are strings interpreted as bit arrays.

```python
# Set/get individual bits
r.setbit("active:today", user_id, 1)
is_active = r.getbit("active:today", user_id)

# Count bits
r.bitcount("active:today")
r.bitcount("active:today", start=0, end=6)  # Byte range

# Bitwise operations
r.bitop("AND", "result", "set1", "set2")
r.bitop("OR", "result", "set1", "set2")
r.bitop("XOR", "result", "set1", "set2")
r.bitop("NOT", "result", "set1")

# Find bit position
r.bitpos("active:today", 1)    # First active user
r.bitpos("active:today", 0)    # First inactive user
```

### Use Cases

- Daily active users tracking
- Feature flag storage
- Presence tracking
- Compact boolean arrays

## HyperLogLog

HyperLogLog estimates cardinality of unique elements with ~0.81% error using ~12KB.

```python
r.pfadd("visitors", "user1", "user2", "user3")
r.pfcount("visitors")  # Estimated unique count

# Merge counts
r.pfadd("day1", "a", "b")
r.pfadd("day2", "b", "c")
r.pfmerge("total", "day1", "day2")
r.pfcount("total")
```

### Use Cases

- Unique visitor counting
- Approximate distinct counts
- Analytics with limited memory

## Geo

Geo indexes store latitude/longitude coordinates for spatial queries.

```python
# Add locations
r.geoadd("cities", {
    "rome": 12.4963655, 41.9027835,
    "milan": 9.1900091, 45.4641335,
    "naples": 14.2502458, 40.8525929,
})

# Distance
r.geodist("cities", "rome", "milan", unit="km")

# Coordinates
r.geopos("cities", "rome", "milan")

# Radius search
r.georadius("cities", 12.5, 41.9, 200, unit="km", withdist=True, withcoord=True, count=10)
r.georadiusbymember("cities", "rome", 300, unit="km")

# Geohash
r.geohash("cities", "rome", "milan")
```

### Use Cases

- Nearby location search
- Delivery radius checks
- Geofencing
- Location-based recommendations
