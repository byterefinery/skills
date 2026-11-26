# Redis Modules

## Module Access Pattern

All module commands are accessed via namespace methods on the client:

```python
import redis

r = redis.Redis(host="localhost")

# JSON
json_client = r.json()

# Search
search_client = r.ft("my_index")

# TimeSeries
ts_client = r.ts()

# Probabilistic
bf_client = r.bf()
cf_client = r.cf()
cms_client = r.cms()
topk_client = r.topk()
tdigest_client = r.tdigest()

# VectorSet
vset_client = r.vset()
```

## RedisJSON

Store and manipulate JSON documents natively.

```python
# Set JSON document
r.json().set("doc", "$", {"name": "Alice", "age": 30, "tags": ["python", "redis"]})

# Get full document
doc = r.json().get("doc", "$")

# Get specific field
name = r.json().get("doc", "$.name")

# Set nested field
r.json().set("doc", "$.address.city", "NYC")

# Append to array
r.json().arrappend("doc", "$.tags", "nosql")

# Array operations
r.json().arrindex("doc", "$.tags", "python")
r.json().arrinsert("doc", "$.tags", 1, "web")
r.json().arrlen("doc", "$.tags")
r.json().arrpop("doc", "$.tags", -1)
r.json().arrtrim("doc", "$.tags", 0, 2)

# Numeric operations
r.json().numincrby("doc", "$.age", 1)
r.json().nummultby("doc", "$.age", 2)

# Object operations
r.json().objkeys("doc", "$.address")
r.json().objlen("doc", "$")

# String operations
r.json().strappend("doc", "$.name", " Jr.")
r.json().strlen("doc", "$.name")

# Delete
r.json().del("doc", "$.address")
r.json().forget("doc", "$.address")  # Alias for del

# Toggle boolean
r.json().set("doc", "$.active", True)
r.json().toggle("doc", "$.active")

# Type check
r.json().type("doc", "$.name")   # "string"
r.json().type("doc", "$.tags")   # "array"

# Merge (deep merge)
r.json().merge("doc", "$", {"address": {"zip": "10001"}})

# Multi-get
results = r.json().mget("$.name", "doc1", "doc2")

# Multi-set
r.json().mset([("doc1", "$", {"a": 1}), ("doc2", "$", {"b": 2}))]
```

### JSONPath vs Legacy Path

redis-py supports both JSONPath (`$...`) and legacy path (`.`) syntax. JSONPath is recommended — it returns arrays of results.

```python
# JSONPath (recommended) — returns array
r.json().get("doc", "$.name")    # ['Alice']

# Legacy path — returns scalar
r.json().get("doc", ".name")     # 'Alice'
```

## RediSearch

Full-text search and secondary indexing.

```python
from redis.commands.search.field import TextField, NumericField, TagField
from redis.commands.search.index_definition import IndexDefinition
from redis.commands.search.query import Query

# Create index
r.ft("products").create_index(
    fields=[
        TextField("name", weight=5.0),
        TextField("description"),
        NumericField("price"),
        TagField("category"),
    ],
    definition=IndexDefinition(prefix=["product:"]),
)

# Add documents (stored as hashes)
r.hset("product:1", mapping={"name": "Laptop", "price": "999", "category": "electronics"})
r.hset("product:2", mapping={"name": "Mouse", "price": "29", "category": "electronics"})

# Search
query = Query("@name:Laptop").paging(0, 10)
result = r.ft("products").search(query)
print(result.total)  # Total matches

# Complex query
query = Query("@price:[0 100] @category:{electronics}").sort_by("price", asc=True)
result = r.ft("products").search(query)

# With dialect
query = Query("@name:Laptop").dialect(2)
result = r.ft("products").search(query)

# Aggregation
from redis.commands.search.aggregation import AggregateRequest, FetchField
req = AggregateRequest("@price:[0 100]").load(FetchField("name")).group_by(
    "@category",
    redis.commands.search.reducers.count().alias("count"),
)
result = r.ft("products").aggregate(req)

# Index info
info = r.ft("products").info()

# Delete index
r.ft("products").delete_index(delete_docs=True)
```

### Batch Indexer

```python
indexer = r.ft("products").batch_indexer(chunk_size=1000)
for doc_id, fields in documents:
    indexer.add_document(doc_id, **fields)
indexer.commit()
```

## Probabilistic Data Structures

### Bloom Filter

```python
# Create
r.bf().create("urls", error_rate=0.01, capacity=1000000)

# Add/Check
r.bf().add("urls", "https://example.com")
exists = r.bf().exists("urls", "https://example.com")

# Multiple
added = r.bf().add_multi("urls", ["url1", "url2", "url3"])
results = r.bf().mexists("urls", ["url1", "url2"])

# Info
info = r.bf().info("urls")

# Reserve (pre-allocate)
r.bf().reserve("urls", error_rate=0.001, capacity=1000000)
```

### Cuckoo Filter

```python
r.cf().create("set", 1000)
r.cf().add("set", "member")
exists = r.cf().exists("set", "member")
r.cf().del_("set", "member")
info = r.cf().info("set")
```

### Count-Min Sketch

```python
r.cms().initbydim("counts", width=1000, depth=5)
r.cms().incrby("counts", ["item1", "item2"], [1, 5])
count = r.cms().query("counts", "item1", "item2")
info = r.cms().info("counts")
```

### Top-K

```python
r.topk().reserve("popular", top_k=10, width=1000, depth=10, decay=0.9)
r.topk().add("popular", "item1", "item2", "item3")
items = r.topk().list("popular", count=True)
info = r.topk().info("popular")
```

### T-Digest

```python
r.tdigest().create("dist", compression=100)
r.tdigest().add("dist", [1.0, 2.0, 3.0], [1, 1, 1])
cdf = r.tdigest().cdf("dist", 2.5)
quantile = r.tdigest().quantile("dist", 0.5, 0.9, 0.99)
info = r.tdigest().info("dist")
```

## RedisTimeSeries

```python
# Create time series
r.ts().create("sensors:temp", retention_msecs=86400000, labels={"room": "kitchen"})

# Add sample
r.ts().add("sensors:temp", timestamp=1609459200000, value=23.5)
r.ts().add("sensors:temp", "*", 24.0)  # "*" = current time

# Add multiple
r.ts().madd("sensors:temp", [(1000, 20.0), (2000, 21.0), (3000, 22.0)])

# Query
result = r.ts().range("sensors:temp", 0, -1)
result = r.ts().range("sensors:temp", from_timestamp=1000, to_timestamp=2000)

# Get latest
latest = r.ts().get("sensors:temp")

# Info
info = r.ts().info("sensors:temp")

# Delete
r.ts().delete("sensors:temp", from_timestamp=1000, to_timestamp=2000)

# Alter
r.ts().alter("sensors:temp", retention_msecs=172800000)
```

## VectorSet

Vector similarity search (new in redis-py 8.x).

```python
# Create vector set
r.vset().create(
    "my_vectors",
    dimension=128,
    algorithm="HNSW",
    distance_metric="COSINE",
)

# Add vectors
r.vset().add("my_vectors", "vec:1", [0.1, 0.2, ..., 0.128])
r.vset().add("my_vectors", "vec:2", [0.3, 0.1, ..., 0.05])

# Similarity search
results = r.vset().similarity_search(
    "my_vectors",
    query_vector=[0.1, 0.2, ..., 0.128],
    num_candidates=10,
)

# Info
info = r.vset().info("my_vectors")

# Get attributes
attrs = r.vset().get_attr("my_vectors", "vec:1")
```

## Module Gotchas

- **Modules require server-side installation** — The Redis module must be loaded on the server. redis-py only provides the client API
- **`r.ft(index_name)` creates a new Search client** — Each call creates a new instance. Reuse for performance
- **RediSearch default dialect is 2** — redis-py 6.0+ defaults to DIALECT 2 for search queries
- **JSONPath returns arrays** — `$`-prefixed paths return arrays of results. Legacy `.` paths return scalars
- **Module namespace methods are lazy** — `r.json()`, `r.ft()`, etc. import the module on first call
- **Async modules use same pattern** — `r.json()`, `r.ft()` work on async clients too, returning async module clients
- **Module commands in pipelines** — Module commands work in pipelines. Search has its own `Pipeline` class: `r.ft("idx").pipeline()`
- **VectorSet requires Redis 8+** — The VectorSet module is available on Redis 8.x servers
