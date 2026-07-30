# Modules

Redis modules extend the server with custom commands, data types, and functionality. Redis 8.10 ships with bundled modules managed via `modules/modules.yaml`.

## Module System

### Building and Loading

```bash
# Build all bundled modules
make build

# Build specific module
make build redisjson

# Load at startup
redis-server --loadmodule ./modules/redisjson/rejson.so

# Or in redis.conf
loadmodule ./modules/redisjson/rejson.so

# Generate redis-full.conf with all loadmodule lines
make sync-redis-conf
```

### Module Manifest

`modules/modules.yaml` pins each module to a specific git ref:

```yaml
modules:
  - name: redisjson
    repo: https://github.com/redisjson/redisjson
    ref: v8.10.0
    target_module: rejson.so
    loadmodule: ./modules/redisjson/rejson.so
```

**Commands:**
- `make modules-update` — clone/update all module sources
- `make modules-update redisjson` — update specific module
- `make bootstrap` — install module build dependencies

### Module API

Modules interface with Redis via `redismodule.h`. Key concepts:

- **`RedisModule_OnLoad`** — module entry point, registers commands/types
- **`RedisModule_CreateCommand`** — register a new command
- **`RedisModule_CreateDataType`** — register a custom data type
- **`RedisModule_OpenKey`** — access keys (with READ/WRITE mode)
- **`RedisModule_String/Set/List/Dict/ZSet/Stream API`** — manipulate data types
- **`RedisModule_Reply_*`** — send replies to clients
- **`RedisModule_CTX_*`** — context management
- **Key metadata classes** — attach custom metadata to keys via `kvobj` metabits

### Module Types

Custom data types implement `RedisModuleTypeMethods`:
- `rdb_load`/`rdb_save` — persistence
- `aof_rewrite` — AOF replication
- `free` — memory cleanup
- `mem_usage` — memory reporting
- `free_effort`/`free_args` — lazy freeing support
- `hash` — key hashing
- `aux_load`/`aux_save` — auxiliary data

## Bundled Modules

### RedisJSON

JSON document storage and querying with JSONPath.

**Build:** `make build redisjson` → `rejson.so`

**Core commands:**
- `JSON.SET <key> <path> <json>` — set JSON document
- `JSON.GET <key> [path]` — get JSON document
- `JSON.MGET <key> [key ...] <path>` — multi-get
- `JSON.ARRAPPEND`, `JSON.ARRINSERT`, `JSON.ARRPOP`, `JSON.ARRTRIM` — array operations
- `JSON.OBJKEYS`, `JSON.OBJLEN`, `JSON.OBJRENAME` — object operations
- `JSON.FORGET <key> <path>` — delete path
- `JSON.TYPE`, `JSON.STRAPPEND`, `JSON.STRLEN` — string operations
- `JSON.NUMINCRBY`, `JSON.NUMMULTBY` — numeric operations
- `JSON.ARRINDEX`, `JSON.ARRLEN`, `JSON.CLEAR` — array info
- `JSON.DEBUG`, `JSON.CACHE` — debugging and caching
- `JSON tok` — token-based operations

**8.10 JSONPath extensions:**
- Projection expressions at top level
- `==`/`!=` compare any literal (arrays, objects)
- Filter negation: `!`
- `size`/`sizeof`/`empty` operators on string, array, object, nodelist
- `in`/`nin` membership operators
- Arithmetic: binary `-`, `+`, `*`, `/`, `%`, unary `-`, `+`
- Object operator: `~`
- `length()` on array, object, string
- Number functions: `abs()`, `ceiling()`, `floor()`
- String functions: `match()`, `search()`, `concat()`
- Array functions: `first()`, `last()`, `index()`, `append()`
- Aggregation: `min()`, `max()`, `avg()`, `sum()`, `stddev()`
- Object function: `keys()`
- Nodelist: `count()`, `value()`
- Relations: `subsetof()`, `anyof()`, `noneof()`

### RediSearch

Full-text search, vector search, and aggregation engine.

**Build:** `make build redisearch` → `redisearch.so`

**Core commands:**
- `FT.CREATE <index> [SCHEMA <field> <type> ...]` — create index
- `FT.SEARCH <index> <query> [LIMIT offset num]` — search
- `FT.AGGREGATE <index> <query> [GROUPBY/SORTBY/REDUCE/APPLY]` — aggregation
- `FT.ADD`, `FT.DEL`, `FT.DROPINDEX` — document management
- `FT.ALTER` — modify index schema
- `FT.INFO <index>` — index metadata
- `FT._LIST` — list all indexes
- `FT.SUGADD`, `FT.SUGGET`, `FT.SUGDEL` — autocomplete
- `FT.SYNADD`, `FT.SYNDUMP` — synonym groups
- `FT.CONFIG GET/SET` — runtime config
- `FT.PROFILE` — query profiling
- `FT.CURSOR READ/DEL` — cursor-based result iteration
- `FT.ALIASADD`, `FT.ALIASDEL`, `FT.ALIASUPDATE` — index aliases
- `FT.ALIASLIST` — list all aliases (new in 8.10)
- `FT.HYBRID` — hybrid vector + filter search

**8.10 additions:**
- `FT.AGGREGATE` — whole-document fetching via `COLLECT`, in-group `SORTBY`/`LIMIT`, deduplication
- `FT.SEARCH`/`FT.AGGREGATE`/`FT.HYBRID` — strict `TIMEOUT` enforcement (`FAIL`/`RETURN`/`RETURN_STRICT`)
- `search-global-timeout` parameter as cap on query timeout
- `FT.HYBRID` — `EXPLAINSCORE` support (RRF or LINEAR fusion)
- Stemmer support for Malay and Tagalog

### RedisTimeSeries

Time series data storage with downsampling, labels, and aggregation.

**Build:** `make build redistimeseries` → `redistimeseries.so`

**Core commands:**
- `TS.CREATE <key> [RETENTION <ms>] [ENCODEMENT UNCOMPRESSED|GORILLA] [DUPLICATE_POLICY] [LABELS <k> <v> ...]` — create series
- `TS.ADD <key> <timestamp> <value> [LABELS]` — add sample
- `TS.MADD <key> <ts> <val> [LABELS] [<key> <ts> <val> ...]` — multi-add
- `TS.INCRBY`/`TS.DECRBY` — increment/decrement
- `TS.RANGE <key> <from> <to> [BUCKETSIZE] [AGGREGATION] [FILTERBY] [LIMIT]` — range query
- `TS.REVRANGE` — reverse range
- `TS.MRANGE`/`TS.MREVRANGE` — multi-series range
- `TS.QUERYINDEX [FILTER]` — query by labels
- `TS.INFO <key>` — series metadata
- `TS.ALTER` — modify series
- `TS.DEL` — delete samples
- `TS.CREATERULE`/`TS.DELETERULE` — downsampling rules

**8.10 additions:**
- `TS.NRANGE`/`TS.NREVRANGE` — query range across multiple series, grouped by timestamp
- `TS.READ` — optionally blocking read
- `TS.QUERYLABELS` — get list of labels and label-values
- `TS.MRANGE`/`TS.MREVRANGE` — new `EXCLUDEEMPTY` argument

### RedisBloom

Probabilistic data structures: Bloom filters, CMS, TopK, Count-Min Sketch.

**Build:** `make build redisbloom` → `redisbloom.so`

**Core commands:**
- `BF.ADD`, `BF.MADD`, `BF.EXISTS`, `BF.MEXISTS` — Bloom filter
- `BF.RESERVE` — pre-allocate Bloom filter
- `BF.INFO` — Bloom filter metadata
- `CF.ADD`, `CF.INSERT`, `CF.QUERY`, `CF.DELETE` — Cuckoo filter (supports deletion)
- `CMS.INITBYDIM`/`CMS.INITBYPROB`, `CMS.INCRBY`, `CMS.QUERY`, `CMS.MERGE` — Count-Min Sketch
- `TOPK.RESERVE`, `TOPK.ADD`, `TOPK.INCRBY`, `TOPK.QUERY`, `TOPK.LIST` — TopK

### Vector Sets (VSET) — Built-in

Vector similarity search using HNSW. **Built directly into the Redis 8.10 binary** — no separate module needed.

**Core commands:** `VADD`, `VSIM`, `VINFO`, `VCARD`, `VREM`, `VGETATTR`, `VSETATTR`, `VRANDMEMBER`, `VLINKS`, `VISMEMBER`, `VDIM`, `VEMB`, `VRANGE`

See [01-data-types](01-data-types.md) for details.

## Writing Custom Modules

```c
#include "redismodule.h"

int MyCommand(RedisModuleCtx *ctx, RedisModuleString **argv, int argc) {
    RedisModule_ReplyWithSimpleString(ctx, "Hello from module!");
    return REDISMODULE_OK;
}

int RedisModule_OnLoad(RedisModuleCtx *ctx, RedisModuleString **argv, int argc) {
    if (RedisModule_Init(ctx, "mymodule", 1, REDISMODULE_APIVER_1) == REDISMODULE_ERR)
        return REDISMODULE_ERR;

    if (RedisModule_CreateCommand(ctx, "my.command", MyCommand, "readonly", 1, 1, 1) == REDISMODULE_ERR)
        return REDISMODULE_ERR;

    return REDISMODULE_OK;
}
```

**Build:**
```bash
gcc -shared -fPIC -I/path/to/redis/src -o mymodule.so mymodule.c
```

**Load:**
```bash
redis-server --loadmodule ./mymodule.so
# or: MODULE LOAD ./mymodule.so
```

## Gotchas

- **Module sources are pinned** — `modules/modules.yaml` controls versions. Use `make modules-update <name>` to refresh.
- **Vector Sets are built-in** — no separate `.so` needed. `VADD`/`VSIM` commands are available by default.
- **Module load order matters** — some modules depend on others. `redis-full.conf` generated by `make sync-redis-conf` handles ordering.
- **`MODULE LOAD` at runtime** — use `MODULE LOAD <path>` to load without restart. `MODULE UNLOAD <name>` to unload.
- **Module commands inherit ACL** — use `ACL CAT` to see module command categories.
- **Module types need RDB/AOF handlers** — without them, data is lost on restart or not replicated.
- **RediSearch requires significant memory** — indexes can use 2-4x the raw data size. Monitor with `FT.INFO`.
- **RedisJSON uses JSONPath** — different from XPath or JSONPointer. Use `$` prefix for JSONPath, `.` for legacy path.
