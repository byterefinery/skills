# Data Types and Commands

Valkey supports nine native data types plus module-extensible custom types.

## Strings

The basic type. Stores text or binary data up to 512 MB.

**Core commands:** `SET`, `GET`, `DEL`, `EXISTS`, `EXPIRE`, `TTL`, `TYPE`, `MGET`, `MSET`, `MSETEX`, `INCR`, `DECR`, `INCRBY`, `DECRBY`, `INCRBYFLOAT`, `APPEND`, `STRLEN`, `GETDEL`, `GETEX`, `SETNX`, `SETEX`, `PSETEX`, `SETRange`, `GETRANGE`, `SUBSTR`, `RANDOMKEY`, `RENAME`, `RENAMENX`, `MOVE`, `COPY`, `SWAPDB`, `TOUCH`, `DUMP`, `RESTORE`, `OBJECT`

**SET options:** `NX`/`XX` (conditional), `EX`/`PX`/`EXAT`/`PXAT` (expiration), `KEEPTTL` (preserve TTL), `GET` (return old value), `IFEQ` (compare-and-set, since 8.1.0)

**MSETEX** (since 9.1.0): Set multiple keys with a shared expiration in one command.

**Internal encodings:** int (64-bit integer), embstr (embedded string, threshold 128 bytes since 9.1), raw (regular SDS string)

## Hashes

Field-value maps. Ideal for objects.

**Core commands:** `HSET`, `HGET`, `HMSET`, `HMGET`, `HGETALL`, `HDEL`, `HLEN`, `HEXISTS`, `HKEYS`, `HVALS`, `HSTRLEN`, `HINCRBY`, `HINCRBYFLOAT`, `HSCAN`, `HRANDFIELD`, `HSETNX`

**9.1.0 additions:**
- `HSETEX` — set hash fields with per-field TTL (supports `NX`/`XX` flags)
- `HGETDEL` — get and delete fields atomically (supports `FIELDS` keyword)
- `HEXPIRE`/`HEXPIREAT`/`HPTTL`/`HPERSIST`/`HPEXPIRE`/`HPEXPIREAT`/`HEXPIRETIME`/`HPERSIST` — per-field TTL management

**Internal encodings:** listpack (small hashes, configurable via `hash-max-listpack-entries`/`hash-max-listpack-value`), hashtable

## Lists

Ordered sequences of strings. Backed by quicklists (linked list of listpacks).

**Core commands:** `LPUSH`, `RPUSH`, `LPOP`, `RPOP`, `LINSERT`, `LLEN`, `LRANGE`, `LINDEX`, `LSET`, `LREM`, `LTRIM`, `LPOS`, `LMOVE`, `BLPOP`, `BRPOP`, `BLMOVE`, `LMPop`, `BLMPop`

**Internal encodings:** quicklist with listpack nodes (configurable via `list-max-listpack-size`, `list-compress-depth`)

## Sets

Unordered collections of unique strings.

**Core commands:** `SADD`, `SREM`, `SMEMBERS`, `SISMEMBER`, `SMISMEMBER`, `SCARD`, `SPOP`, `SRANDMEMBER`, `SMOVE`, `SINTER`, `SINTERCARD`, `SINTERSTORE`, `SUNION`, `SUNIONSTORE`, `SDIFF`, `SDIFFSTORE`, `SSCAN`

**Internal encodings:** intset (integer-only sets, up to `set-max-intset-entries`), listpack (small sets), hashtable

## Sorted Sets (ZSets)

Sets with scores for ordering. Backed by skiplist + hashtable.

**Core commands:** `ZADD`, `ZREM`, `ZRANGE`, `ZREVRANGE`, `ZRANGEBYSCORE`, `ZRANGEBYLEX`, `ZREVRANGEBYSCORE`, `ZREVRANGEBYLEX`, `ZRANGESTORE`, `ZRANK`, `ZREVRANK`, `ZSCORE`, `ZINCRBY`, `ZCARD`, `ZCOUNT`, `ZLEXCOUNT`, `ZPOPMIN`, `ZPOPMAX`, `ZMPOP`, `BZMPOP`, `ZMSCORE`, `ZRANDMEMBER`, `ZSCAN`, `ZINTER`, `ZINTERCARD`, `ZINTERSTORE`, `ZUNION`, `ZUNIONSTORE`, `ZDIFF`, `ZDIFFSTORE`, `ZREMRangeByRank`, `ZREMRangeByScore`, `ZREMRangeByLex`

**Internal encodings:** listpack (small zsets, configurable via `zset-max-listpack-entries`/`zset-max-listpack-value`), skiplist + hashtable (with embedded elements and headers since 9.1 for memory savings)

## Streams

Ordered, append-only logs with consumer group support.

**Core commands:** `XADD`, `XDEL`, `XTRIM`, `XRANGE`, `XREVRANGE`, `XLEN`, `XREAD`, `XREADGROUP`, `XACK`, `XGROUP` (CREATE/DESTROY/SETID/CREATECONSUMER/DELCONSUMER), `XCLAIM`, `XAUTOCLAIM`, `XPENDING`, `XINFO` (STREAM/GROUPS/CONSUMERS)

**Internal structure:** radix tree of macro nodes, each node holding up to `stream-node-max-entries` entries or `stream-node-max-bytes` bytes.

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

**Core commands:** `SETBIT`, `GETBIT`, `BITCOUNT`, `BITPOS`, `BITFIELD`, `BITFIELD_RO`, `BITOP`

**BITFIELD** supports: `GET`, `SET`, `INCRBY`, `OVERFLOW` (WRAP/SAT/FAIL/FAIL_WRAP), `SUBSTR`

## Keyspace commands

Type-agnostic operations: `DEL`, `UNLINK` (async delete), `EXISTS`, `EXPIRE`/`PEXPIRE`/`EXPIREAT`/`PEXPIREAT`, `TTL`/`PTTL`, `PERSIST`, `KEYS`, `SCAN`, `CLUSTERSCAN`, `DBSIZE`, `FLUSHDB`, `FLUSHALL`, `SORT`, `SORT_RO`, `RANDOMKEY`, `DUMP`, `RESTORE`, `MIGRATE`, `SWAPDB`, `TOUCH`, `OBJECT`

**SCAN family:** `SCAN`, `SSCAN`, `HSCAN`, `ZSCAN` with `COUNT`, `MATCH`, `TYPE` options. `CLUSTERSCAN` (since 9.1.0) enables cluster-wide scanning.

## Command categories

Commands are organized into ACL categories: `@admin`, `@bitmap`, `@connection`, `@dangerous`, `@fast`, `@geo`, `@hash`, `@hyperloglog`, `@list`, `@pubsub`, `@read`, `@scripting`, `@set`, `@sortedset`, `@slow`, `@stream`, `@string`, `@transaction`, `@write`, `@keyspace`.

Use `COMMAND LIST`, `COMMAND INFO`, `COMMAND COUNT`, `COMMAND DOCS` for introspection.
