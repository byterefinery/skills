# Modules

Valkey supports modules that extend the server with new data structures and commands. valkey-py provides clients for JSON, Search (RediSearch), Bloom filters (probabilistic), Graph, and TimeSeries modules.

## JSON Module

```python
from valkey.commands.json import JSON

json_client = JSON(r)

# Set JSON
json_client.set("doc", "$", {"name": "Alice", "age": 30, "tags": ["a", "b"]})

# Get JSON
data = json_client.get("doc", "$")
# '[{"name": "Alice", "age": 30, "tags": ["a", "b"]}]'

# Get specific field
name = json_client.get("doc", "$.name")
# '["Alice"]'

# Update
json_client.set("doc", "$.age", 31)
json_client.set("doc", "$.email", "alice@example.com")  # add new field

# Delete field
json_client.delete("doc", "$.tags")

# Number operations
json_client.arrappend("doc", "$.tags", "c")
json_client.arrindex("doc", "$.tags", "b")
json_client.arrlen("doc", "$.tags")
json_client.arrinsert("doc", "$.tags", 0, "new")
json_arrpop("doc", "$.tags")
json_client.arrtrim("doc", "$.tags", 0, 2)

# Object operations
json_client.objkeys("doc", "$")
json_client.objlen("doc", "$")

# Type and length
json_client.type("doc", "$")
json_client.strlen("doc", "$.name")
json_client.toggle("doc", "$.active")

# Debug
json_client.debug("MEMORY", "doc")
```

### JSON Path Syntax

JSON module uses JSONPath expressions:

```python
# Root path
json_client.get("doc", "$")           # full document (array wrapper)
json_client.get("doc", "$.name")      # field value
json_client.get("doc", "$.tags[*]")   # all array elements
json_client.get("doc", "$.tags[0]")   # first element

# Legacy path (no $ prefix, returns unwrapped)
json_client.get("doc", ".name")       # "Alice"
```

## Search Module (RediSearch)

```python
from valkey.commands.search import IndexDefinition, Schema, TextField, NumericField, TagField

# Create index
r.ft("idx:products").create_index(
    fields=[
        TextField("name", weight=1.0),
        TextField("description"),
        NumericField("price"),
        TagField("category"),
    ],
    definition=IndexDefinition(index_type="HASH", prefix=["product:"]),
)

# Add document (auto-indexed via prefix)
r.hset("product:1", mapping={
    "name": "Laptop",
    "description": "High-performance laptop",
    "price": 999.99,
    "category": "electronics",
})

# Search
result = r.ft("idx:products").search("Laptop")
print(result.total)        # total matches
for doc in result.docs:
    print(doc.id, doc.name, doc.price)

# Filtered search
query = r.ft("idx:products").create_query("Laptop") \
    .filter("@price:[0 500]") \
    .sort_by("price") \
    .paging(0, 10)
result = r.ft("idx:products").search(query)

# Aggregation
result = r.ft("idx:products").agg(
    "category:electronics"
).group_by("@category",
    r.ReduceCount().as_field("count"),
    r.ReduceAvg("@price").as_field("avg_price"),
).sort_by("@avg_price", True) \
 .limit(0, 10)
```

### Search Query Syntax

```python
# Full-text search
r.ft("idx:docs").search("hello world")
r.ft("idx:docs").search('"exact phrase"')
r.ft("idx:docs").search("hello|world")  # OR
r.ft("idx:docs").search("-deleted")      # NOT

# Field-specific
r.ft("idx:docs").search("@title:hello @content:world")

# Numeric range
r.ft("idx:docs").search("@price:[0 100]")
r.ft("idx:docs").search("@price:[(100 200]")  # exclusive lower

# Tag filter
r.ft("idx:docs").search("@category:{electronics}")
r.ft("idx:docs").search("@category:{electronics|books}")

# Geo search
r.ft("idx:docs").search("@location:[48.85 2.35 100 km]")
```

## Probabilistic Module (Bloom Filters, CMS, TopK, TDigest)

### Bloom Filter

```python
# Add
r.bfadd("mybf", "item1")
r.bfadd("mybf", "item2")

# Check existence (probabilistic — false positives possible)
r.bfexists("mybf", "item1")   # True
r.bfexists("mybf", "missing") # False

# Multi operations
r.bfinsert("mybf", capacity=1000, error_rate=0.01, items=["a", "b", "c"])
r.bfmexists("mybf", "a", "missing")  # [True, False]

# Info
r.bfinfo("mybf")
```

### Count-Min Sketch

```python
# Initialize
r.cmsinitbydim("mysketch", 100, 5)  # width=100, depth=5
# or
r.cmsinitbyprob("mysketch", 0.001, 0.01)  # error_rate, prob

# Increment
r.cmsincrby("mysketch", ["item1"], [1])
r.cmsincrby("mysketch", ["item1", "item2"], [5, 3])

# Query (probabilistic — may overcount)
r.cmsquery("mysketch", "item1", "item2")
```

### TopK

```python
# Initialize
r.topkreserve("mytopk", 10, 100, 0.01, 0.5)  # k, width, depth, decay

# Add items
r.topkadd("mytopk", "item1", "item2", "item3")

# Increment
r.topkincrby("mytopk", "item1", 5)

# Query
r.topkquery("mytopk", "item1", "item2")  # [True, False]

# List top items
r.topklist("mytopk")
r.topklist("mytopk", withcounts=True)

# Info
r.topkinfo("mytopk")
```

### TDigest

```python
# Create
r.tdigestcreate("mytdigest")

# Add values
r.tdigestadd("mytdigest", 1.0, 2.0, 3.0, 100.0)

# Quantiles
r.tdigestcdf("mytdigest", 50.0)    # fraction <= 50
r.tdigestquantile("mytdigest", 0.5) # median

# Min/Max
r.tdigestmin("mytdigest")
r.tdigestmax("mytdigest")

# Trimmed mean
r.tdigesttrimmed_mean("mytdigest", 0.025, 0.975)

# Rank
r.tdigestrank("mytdigest", 50.0)

# Info
r.tdigestinfo("mytdigest")

# Merge
r.tdigestmerge("dest", "src1", "src2")
```

## Graph Module

```python
# Create graph
r.graph_query("social", "CREATE (alice:Person {name: 'Alice', age: 30})")
r.graph_query("social", "CREATE (bob:Person {name: 'Bob', age: 25})")
r.graph_query("social", "CREATE (alice)-[:FRIENDS_WITH]->(bob)")

# Query
result = r.graph_query("social",
    "MATCH (p:Person) WHERE p.age > 25 RETURN p.name, p.age"
)
print(result.result_set)

# Delete graph
r.graph_delete("social")
```

### Graph Query Language (Cypher-like)

```python
# Create nodes and relationships
r.graph_query("g", """
    CREATE (a:Person {name: 'Alice'})
    CREATE (b:Person {name: 'Bob'})
    CREATE (a)-[:KNOWS]->(b)
""")

# Match
r.graph_query("g", """
    MATCH (a:Person)-[:KNOWS]->(b:Person)
    RETURN a.name, b.name
""")

# Path finding
r.graph_query("g", """
    MATCH path = (a:Person)-[:KNOWS*1..3]->(b:Person)
    RETURN path
""")
```

## TimeSeries Module

```python
# Create time series
r.tscreate("sensor:temp", retention_msecs=3600000)

# Add sample
r.tsadd("sensor:temp", 1000, 25.5)
r.tsadd("sensor:temp", "*", 26.0)  # * = current time

# Get latest value
r.tsget("sensor:temp")

# Range query
r.tsrange("sensor:temp", 0, 2000)
r.tsrange("sensor:temp", -1000, "+inf")  # last 1000ms

# Range with aggregation
r.tsmrange(0, 2000, aggregation_type="avg", bucket_size_msecs=100, filters=["sensor:*"])

# Info
r.tsinfo("sensor:temp")

# Delete
r.tsdel("sensor:temp", 0, 1000)

# Alter
r.tsalter("sensor:temp", retention_msecs=7200000)

# Create rules (continuous aggregation)
r.tscreaterule("sensor:temp", "sensor:temp:1m", aggregation_type="avg", bucket_size_msecs=60000)

# Duplicate (real-time replication)
r.tsadd("sensor:temp", 1000, 25.5, on_duplicate="BLOCK")
r.tsadd("sensor:temp", 1000, 25.5, on_duplicate="SUM")
```

## Module Clients via ValkeyModuleCommands

All module commands are available on the base `Valkey` client through mixin inheritance:

```python
import valkey
r = valkey.Valkey(host="localhost", port=6379)

# JSON commands available directly
# r.json().set(...) — via JSON wrapper
# r.ft("idx").search(...) — via Search

# Or use the module-specific client
from valkey.commands.json import JSON
json_client = JSON(r)
```

## Gotchas

- **Modules must be loaded on the server** — valkey-py commands will fail with `ResponseError` if the module is not loaded.
- **JSON module uses JSONPath** — The `$` prefix returns array-wrapped results. Legacy paths (`.field`) return unwrapped values.
- **Search requires index creation** — Documents are only indexed if they match the index prefix or are explicitly added.
- **Bloom filters have false positives** — `bfexists` may return True for items not added. Tune capacity and error rate during initialization.
- **Count-Min Sketch may overcount** — `cmsquery` returns an upper bound, not exact counts.
- **Graph queries use Cypher-like syntax** — Not full Cypher. Check Valkey Graph documentation for supported features.
- **TimeSeries uses millisecond timestamps** — All time values are in milliseconds since epoch.
- **Module commands may not be cluster-aware** — Some module commands don't support cluster routing. Check module documentation.
