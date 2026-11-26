# Data Structures

Valkey supports rich data structures beyond simple key-value pairs. This reference covers Lists, Sets, Hashes, Sorted Sets, Streams, HyperLogLog, and Geospatial indexes.

## Lists

Ordered collections of strings, supporting push/pop from both ends.

```python
# Push
r.lpush("mylist", "a", "b", "c")   # ["c", "b", "a"]
r.rpush("mylist", "d")             # ["c", "b", "a", "d"]
r.lpushx("mylist", "x")            # only if list exists
r.rpushx("mylist", "y")            # only if list exists

# Pop
r.lpop("mylist")     # "c" (leftmost)
r.rpop("mylist")     # "y" (rightmost)
r.lpop("mylist", 3)  # pop 3 elements from left

# Blocking pop (waits for element)
r.blpop("mylist", timeout=10)       # ("mylist", "value") or None
r.brpop("mylist", timeout=10)
r.blpop(["list1", "list2"], timeout=5)  # pop from first non-empty list
r.blmpop(10, "MAX", "list1", "list2")   # multi-key blocking pop (Valkey 7+)

# Range
r.lrange("mylist", 0, -1)      # all elements
r.lrange("mylist", 0, 9)       # first 10
r.lrange("mylist", -5, -1)     # last 5

# Index, Length, Set
r.lindex("mylist", 0)          # first element
r.lindex("mylist", -1)         # last element
r.llen("mylist")               # length
r.lset("mylist", 0, "new")     # set element at index

# Remove, Trim, Insert
r.lrem("mylist", "value", 0)   # remove all occurrences
r.ltrim("mylist", 0, 99)       # keep only indices 0-99
r.linsert("mylist", "BEFORE", "pivot", "new")
r.linsert("mylist", "AFTER", "pivot", "new")

# Move between lists
r.rpoplpush("src", "dst")
r.lmpop(["list1", "list2"], "LEFT")  # pop from first non-empty
```

## Sets

Unordered collections of unique strings.

```python
# Add, Check, Count
r.sadd("myset", "a", "b", "c")
r.sismember("myset", "a")      # True
r.scard("myset")               # 3

# Members, Random, Pop
r.smembers("myset")            # all members
r.srandmember("myset")         # random member
r.srandmember("myset", 5)      # 5 random members
r.spop("myset")                # remove and return random
r.spop("myset", 3)             # remove and return 3 random

# Remove
r.srem("myset", "a", "b")

# Set algebra
r.sinter("set1", "set2")               # intersection
r.sunion("set1", "set2")               # union
r.sdiff("set1", "set2")                # difference
r.sinterstore("out", "set1", "set2")   # store intersection
r.sunionstore("out", "set1", "set2")   # store union
r.sdiffstore("out", "set1", "set2")    # store difference

# Move between sets
r.smove("src", "dst", "member")

# Iteration
for member in r.sscan_iter("myset", match="prefix:*"):
    print(member)
```

## Hashes

Key-value maps stored under a single key.

```python
# Set
r.hset("user:1", "name", "Alice")
r.hset("user:1", {"name": "Alice", "age": "30", "email": "a@b.com"})
r.hsetnx("user:1", "name", "Bob")  # only if field doesn't exist

# Get
r.hget("user:1", "name")
r.hmget("user:1", "name", "age")
r.hgetall("user:1")  # {"name": "Alice", "age": "30", ...}

# Fields, Values, Length
r.hkeys("user:1")    # ["name", "age", "email"]
r.hvals("user:1")    # ["Alice", "30", "a@b.com"]
r.hlen("user:1")     # 3

# Exists, Delete
r.hexists("user:1", "name")
r.hdel("user:1", "field1", "field2")

# Increment
r.hincrby("user:1", "login_count", 1)
r.hincrbyfloat("user:1", "score", 0.5)

# Strlen of field
r.hstrlen("user:1", "name")

# Iteration (avoids loading entire hash)
for field, value in r.hscan_iter("user:1", match="*name*"):
    print(field, value)
```

### Hash as Structured Data

Hashes are ideal for object-like data:

```python
# Store a user profile
r.hset("user:42", mapping={
    "username": "alice",
    "email": "alice@example.com",
    "created_at": "2024-01-15T10:30:00Z",
    "settings_theme": "dark",
    "settings_notifications": "true",
})

# Partial update
r.hset("user:42", mapping={"email": "new@example.com"})

# Read all
user = r.hgetall("user:42")
```

## Sorted Sets

Sets with scores, enabling ranked ordering.

```python
# Add
r.zadd("leaderboard", {"alice": 100, "bob": 95, "charlie": 85})
r.zadd("leaderboard", {"dave": 90}, nx=True)   # only new members
r.zadd("leaderboard", {"alice": 110}, xx=True)  # only existing members
r.zadd("leaderboard", {"alice": 110}, ch=True)  # return changed count
r.zadd("leaderboard", {"alice": 110}, incr=True) # act as zincrby

# Score
r.zscore("leaderboard", "alice")  # 110.0

# Rank (0-based)
r.zrank("leaderboard", "charlie")      # 0 (ascending, lowest first)
r.zrevrank("leaderboard", "charlie")   # 3 (descending, highest first)

# Range by index
r.zrange("leaderboard", 0, -1)                    # all members
r.zrange("leaderboard", -3, -1, withscores=True)  # top 3 with scores
r.zrevrange("leaderboard", 0, 2)                  # top 3 descending

# Range by score
r.zrangebyscore("leaderboard", 80, 100)
r.zrangebyscore("leaderboard", "-inf", "(100")  # exclusive upper bound
r.zrangebyscore("leaderboard", 0, "+inf", start=0, num=10)

# Count
r.zcard("leaderboard")            # total members
r.zcount("leaderboard", 80, 100)  # members in score range

# Remove
r.zrem("leaderboard", "alice", "bob")
r.zremrangebyrank("leaderboard", 0, 0)    # remove lowest
r.zremrangebyscore("leaderboard", 0, 50)  # remove by score range
r.zremrangebylex("leaderboard", "-", "(M") # remove by lex range

# Increment
r.zincrby("leaderboard", 5, "bob")

# Lex range (for equal scores)
r.zrangebylex("leaderboard", "-", "+")
r.zrangebylex("leaderboard", "[abc", "[zzz")

# Intersection/Union
r.zinterstore("out", ["set1", "set2"], aggregate="SUM")
r.zunionstore("out", ["set1", "set2"], aggregate="MAX")

# Pop
r.zpopmin("leaderboard")       # pop lowest scoring member
r.zpopmax("leaderboard", 3)    # pop 3 highest scoring members
r.zmpop(["z1", "z2"], "MIN")   # multi-key pop

# Iteration
for member, score in r.zscan_iter("leaderboard"):
    print(member, score)
```

### Sorted Set Patterns

**Leaderboard with pagination:**
```python
# Get ranked page
page = 2
per_page = 10
entries = r.zrevrange("leaderboard", (page-1)*per_page, page*per_page-1, withscores=True)
rank = r.zrevrank("leaderboard", "alice") + 1  # 1-based rank
```

**Time-based sliding window:**
```python
import time
now = time.time()
# Add with timestamp as score
r.zadd("events", {f"user:1:{now}": now})
# Remove old entries (older than 1 hour)
r.zremrangebyscore("events", 0, now - 3600)
# Count recent events
count = r.zcard("events")
```

## Streams

Ordered, append-only logs with consumer group support.

```python
# Add entries
r.xadd("mystream", {"message": "hello"})
r.xadd("mystream", {"message": "world"}, id="*", maxlen=1000, approximate=True)
r.xadd("mystream", {"message": "test"}, id="0-0")  # explicit ID

# Get entries
r.xrange("mystream")                    # all entries
r.xrange("mystream", start="-", end="+")
r.xrange("mystream", start="0-0", end="0-2")
r.xrevrange("mystream", end="+", start="-", count=10)  # reverse

# Get by ID
r.xrange("mystream", start="0-0", end="0-0")

# Length
r.xlen("mystream")

# Trim
r.xtrim("mystream", maxid="1000-0")
r.xtrim("mystream", maxlen=1000, approximate=True)

# Delete
r.xdel("mystream", "id1", "id2")

# Consumer groups
r.xgroup_create("mystream", "mygroup", id="0", mkstream=True)

# Read from group
r.xreadgroup("mygroup", "consumer1", {"mystream": ">"})

# Pending messages
r.xpending("mystream", "mygroup")
r.xpending_range("mystream", "mygroup", "-", "+", 10)

# Claim pending
r.xclaim("mystream", "mygroup", "consumer2", min_idle_time=60000, ids=["id1"])

# Acknowledge
r.xack("mystream", "mygroup", "id1", "id2")

# Destroy group
r.xgroup_destroy("mystream", "mygroup")
```

### Stream Reading Patterns

**Simple consumer:**
```python
# Read new messages
while True:
    messages = r.xread({"mystream": ">"}, block=1000)
    for stream, entries in messages:
        for entry_id, data in entries:
            process(data)
```

**Consumer group worker:**
```python
r.xgroup_create("mystream", "workers", id="0", mkstream=True)

while True:
    messages = r.xreadgroup(
        "workers", "worker-1",
        {"mystream": ">"},
        count=10,
        block=5000,
    )
    for stream, entries in messages:
        for entry_id, data in entries:
            try:
                process(data)
                r.xack("mystream", "workers", entry_id)
            except Exception:
                pass  # will be retried via XPENDING
```

## HyperLogLog

Probabilistic cardinality estimation using ~12KB per key.

```python
# Add
r.pfadd("visitors", "user1", "user2", "user3")

# Count (approximate unique count)
r.pfcount("visitors")

# Merge
r.pfmerge("total", "visitors:day1", "visitors:day2")
```

## Geospatial

Store and query geographic positions.

```python
# Add location
r.geoadd("cities", {"Rome": (41.9028, 12.4964), "Paris": (48.8566, 2.3522)})

# Distance
r.geodist("cities", "Rome", "Paris", unit="km")

# Coordinates
r.geopos("cities", "Rome")  # [(12.4964, 41.9028)]

# Radius search
r.georadius("cities", 12.5, 41.9, 100, "km")
r.georadius("cities", 12.5, 41.9, 100, "km", withdist=True)
r.georadius("cities", 12.5, 41.9, 100, "km", withcoord=True, count=10, sort="ASC")

# Radius by member
r.georadiusbymember("cities", "Rome", 100, "km")

# Geohash
r.geohash("cities", "Rome", "Paris")
```

## Bitmaps

Bit arrays stored as strings, for efficient boolean tracking.

```python
# Set bits
r.setbit("active:2024", day_of_year, 1)

# Get bit
is_active = r.getbit("active:2024", day_of_year)

# Count set bits
active_days = r.bitcount("active:2024")
january_active = r.bitcount("active:2024", start=0, end=30)

# Bit operations across keys
r.bitop("AND", "both_active", "active:2024", "active:2023")
r.bitop("OR", "either_active", "active:2024", "active:2023")
r.bitop("XOR", "exclusive", "active:2024", "active:2023")
r.bitop("NOT", "inactive", "active:2024")

# Find first bit at position
r.bitpos("active:2024", 1)     # first active day
r.bitpos("active:2024", 0)     # first inactive day
```

## Strings (Advanced)

```python
# GETEX — get with optional expiry change
r.getex("key", ex=60)       # get + set 60s expiry
r.getex("key", px=60000)    # get + set 60s expiry (ms)
r.getex("key", exat=1234)   # get + set absolute expiry
r.getex("key", persist=True)# get + remove expiry

# LMOVE / BLMOVE — move between lists
r.lmove("src", "dst", "LEFT", "RIGHT")
r.blmove("src", "dst", "LEFT", "RIGHT", timeout=5)

# LMPOP — multi-key list pop
r.lmpop(["list1", "list2"], "LEFT", count=3)
```
