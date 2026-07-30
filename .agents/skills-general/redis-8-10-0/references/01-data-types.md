# Data Types and Commands

Redis 8.10 supports nine native data types plus module-extensible custom types.

## Strings

The basic type. Stores text or binary data up to 512 MB.

**Core commands:** `SET`, `GET`, `DEL`, `EXISTS`, `EXPIRE`, `TTL`, `TYPE`, `MGET`, `MSET`, `MSETEX`, `INCR`, `DECR`, `INCRBY`, `DECRBY`, `INCRBYFLOAT`, `APPEND`, `STRLEN`, `GETDEL`, `GETEX`, `SETNX`, `SETEX`, `PSETEX`, `SETRANGE`, `GETRANGE`, `SUBSTR`, `RANDOMKEY`, `RENAME`, `RENAMENX`, `MOVE`, `COPY`, `SWAPDB`, `TOUCH`, `DUMP`, `RESTORE`, `OBJECT`

**SET options:** `NX`/`XX` (conditional), `EX`/`PX`/`EXAT`/`PXAT` (expiration), `KEEPTTL` (preserve TTL), `GET` (return old value)

**MSETEX** (since 8.0): Set multiple keys with a shared expiration in one command.

**Internal encodings:** int (64-bit integer), embstr (embedded string), raw (regular SDS string)

## Hashes

Field-value maps. Ideal for objects. Redis 8.10 introduces **compact hashes** — a new encoding that stores field names just once for keys sharing a schema, reducing memory significantly.

**Core commands:** `HSET`, `HGET`, `HMSET`, `HMGET`, `HGETALL`, `HDEL`, `HLEN`, `HEXISTS`, `HKEYS`, `HVALS`, `HSTRLEN`, `HINCRBY`, `HINCRBYFLOAT`, `HSCAN`, `HRANDFIELD`, `HSETNX`

**8.10 additions:**
- **Compact hashes** — new encoding (`OBJ_ENCODING_TMPL_LP` / `OBJ_ENCODING_TMPL_ARRAY`) that shares field name storage across hashes with matching schemas. Controlled by `hash-max-template-entries` (default 0 = disabled).
- **`HIMPORT`** — session-based bulk hash import using fieldsets. Workflow: `HIMPORT PREPARE` defines a fieldset (sorted field names), then `HIMPORT SET` creates hashes from ordered values. Much faster than individual `HSET` calls for bulk loads.
  - `HIMPORT PREPARE <name> <field1> <field2> ...` — define fieldset
  - `HIMPORT SET <key> <fieldset-name> <val1> <val2> ...` — create hash from values
  - `HIMPORT DISCARD <name>` — remove a fieldset
  - `HIMPORT DISCARDALL` — remove all fieldsets
  - Fieldsets are session-scoped (tied to client connection)

**Internal encodings:**
- listpack (small hashes, configurable via `hash-max-listpack-entries`/`hash-max-listpack-value`)
- hashtable (large hashes)
- **compact hash** (new in 8.10, `OBJ_ENCODING_TMPL_LP` / `OBJ_ENCODING_TMPL_ARRAY`) — shares field name templates across keys

**8.0 additions:**
- `HSETEX` — set hash fields with per-field TTL
- `HGETDEL` — get and delete fields atomically
- `HEXPIRE`/`HEXPIREAT`/`HPTTL`/`HPERSIST` — per-field TTL management

## Lists

Ordered sequences of strings. Backed by quicklists (linked list of listpacks).

**Core commands:** `LPUSH`, `RPUSH`, `LPOP`, `RPOP`, `LINSERT`, `LLEN`, `LRANGE`, `LINDEX`, `LSET`, `LREM`, `LTRIM`, `LPOS`, `LMOVE`, `BLPOP`, `BRPOP`, `BLMOVE`, `LMPop`, `BLMPop`

**8.10 additions:**
- **`LMOVEM`** — move multiple elements between lists in one command. Supports `COUNT` (up to N) and `EXACTLY` (exactly N, returns null if insufficient). Ordering options: `OBO` (original order) or `BULK` (reversed).
  ```
  LMOVEM source dest LEFT RIGHT [COUNT|EXACTLY count] [OBO|BULK]
  ```
- **`BLMOVEM`** — blocking variant of `LMOVEM`.

**Internal encodings:** quicklist with listpack nodes (configurable via `list-max-listpack-size`, `list-compress-depth`)

## Sets

Unordered collections of unique strings.

**Core commands:** `SADD`, `SREM`, `SMEMBERS`, `SISMEMBER`, `SMISMEMBER`, `SCARD`, `SPOP`, `SRANDMEMBER`, `SMOVE`, `SINTER`, `SINTERCARD`, `SINTERSTORE`, `SUNION`, `SUNIONSTORE`, `SDIFF`, `SDIFFSTORE`, `SSCAN`

**8.10 additions:**
- **`SUNIONCARD`** — cardinality of the union of multiple sets (without computing the full union). Supports `APPROX` for probabilistic counting and `LIMIT` for early termination.
  ```
  SUNIONCARD numkeys key [key ...] [APPROX] [LIMIT limit]
  ```
- **`SDIFFCARD`** — cardinality of the difference between sets. Supports `LIMIT` for early termination.
  ```
  SDIFFCARD numkeys key [key ...] [LIMIT limit]
  ```

**Internal encodings:** intset (integer-only sets, up to `set-max-intset-entries`), listpack (small sets), hashtable

## Sorted Sets (ZSets)

Sets with scores for ordering. Backed by skiplist + hashtable.

**Core commands:** `ZADD`, `ZREM`, `ZRANGE`, `ZREVRANGE`, `ZRANGEBYSCORE`, `ZRANGEBYLEX`, `ZREVRANGEBYSCORE`, `ZREVRANGEBYLEX`, `ZRANGESTORE`, `ZRANK`, `ZREVRANK`, `ZSCORE`, `ZINCRBY`, `ZCARD`, `ZCOUNT`, `ZLEXCOUNT`, `ZPOPMIN`, `ZPOPMAX`, `ZMPOP`, `BZMPOP`, `ZMSCORE`, `ZRANDMEMBER`, `ZSCAN`, `ZINTER`, `ZINTERCARD`, `ZINTERSTORE`, `ZUNION`, `ZUNIONSTORE`, `ZDIFF`, `ZDIFFSTORE`, `ZREMRANGEBYRANK`, `ZREMRANGEBYSCORE`, `ZREMRANGEBYLEX`

**Internal encodings:** listpack (small zsets, configurable via `zset-max-listpack-entries`/`zset-max-listpack-value`), skiplist + hashtable

## Streams

Ordered, append-only logs with consumer group support.

**Core commands:** `XADD`, `XDEL`, `XTRIM`, `XRANGE`, `XREVRANGE`, `XLEN`, `XREAD`, `XREADGROUP`, `XACK`, `XGROUP` (CREATE/DESTROY/SETID/CREATECONSUMER/DELCONSUMER), `XCLAIM`, `XAUTOCLAIM`, `XPENDING`, `XINFO` (STREAM/GROUPS/CONSUMERS)

**8.10 additions:**
- `XREAD`/`XREADGROUP` — new `MAXCOUNT` and `MAXSIZE` arguments to cap cumulative reply entries and size, preventing OOM on consumers with large pending entries.

**Internal structure:** radix tree of macro nodes, each node holding up to `stream-node-max-entries` entries or `stream-node-max-bytes` bytes.

## Arrays

Fixed-index collections of string values. Introduced in Redis 8.8, refined in 8.10.

**Core commands:** `ARSET`, `ARGET`, `ARGETRANGE`, `ARDEL`, `ARDELRANGE`, `ARINSERT`, `ARLEN`, `ARCOUNT`, `ARINFO`, `ARSCAN`, `ARSEEK`, `ARNEXT`, `ARLASTITEMS`, `ARPOP`, `ARRING`, `ARMGET`, `ARMSET`, `AROP`, `ARREPLACE`

Arrays support sparse indexing, ring mode (circular buffer), and efficient range operations. Use `ARINFO` to inspect internal structure.

**Internal encoding:** sliced array (`OBJ_ENCODING_SLICED_ARRAY`) — directory of slices with flat or super-directory indexing.

## Vector Sets (VSET)

Vector-based similarity search. Built into the Redis 8.10 binary (no separate module needed). Uses HNSW graph with optional quantization.

**Core commands:** `VADD`, `VSIM`, `VINFO`, `VCARD`, `VREM`, `VGETATTR`, `VSETATTR`, `VRANDMEMBER`, `VLINKS`, `VISMEMBER`, `VDIM`, `VEMB`, `VRANGE`

**VADD** — add vectors to a set:
```
VADD key [REDUCE dim] FP32|VALUES vector element [CAS] [NOQUANT|Q8|BIN] [EF factor] [SETATTR attrs] [M numlinks]
```
- `NOQUANT` — no quantization (full FP32)
- `Q8` — signed 8-bit quantization (default)
- `BIN` — binary quantization (fastest, lowest recall)
- `EF` — exploration factor for graph building (default 200)
- `M` — max connections per node (default 16)

**VSIM** — find similar vectors:
```
VSIM key [ELE|FP32|VALUES] <vector> [WITHSCORES] [WITHATTRIBS] [COUNT n] [EPSILON delta] [EF factor] [FILTER expr] [FILTER-EF effort] [TRUTH] [NOTHREAD]
```
- `FILTER` — scalar attribute filtering (e.g., `".year > 1950"`)
- `FILTER-EF` — max effort spent on filtering

## Geo

Geographic positions stored as sorted sets (score = geohash).

**Core commands:** `GEOADD`, `GEOPOS`, `GEODIST`, `GEOHASH`, `GEORADIUS`, `GEORADIUS_RO`, `GEORADIUSBYMEMBER`, `GEORADIUSBYMEMBER_RO`, `GEOSEARCH`, `GEOSEARCHSTORE`

**GEOSEARCH** supports: `BYRADIUS`, `BYBOX`, `BYMEMBER`, `BYPOLYGON`, `WITHCOORD`, `WITHDIST`, `WITHHASH`, `ASC`/`DESC`, `COUNT`, `STORE`

## HyperLogLog

Probabilistic cardinality counting (~0.81% standard error, ~12 KB per HLL).

**Core commands:** `PFADD`, `PFCOUNT`, `PFMERGE`, `PFDEBUG`, `PFSELFTEST`

**Config:** `hll-sparse-max-bytes` (default 3000) — threshold for sparse-to-dense conversion.

## Bitmaps

Bit-level operations on string values.

**Core commands:** `SETBIT`, `GETBIT`, `BITFIELD`, `BITFIELD_RO`, `BITOP`, `BITCOUNT`, `BITPOS`

**BITFIELD** supports overflow control (`WRAP`/`SAT`/`FAIL`/`WRAP`) and subcommand batching.
