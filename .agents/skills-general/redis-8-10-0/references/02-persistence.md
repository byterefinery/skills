# Persistence

Redis supports two persistence mechanisms: RDB snapshots and AOF (Append Only File). Both can be used together.

## RDB Snapshots

Point-in-time snapshots of the dataset. Produced by forking a child process that writes the on-memory dataset to disk.

**Config:**
- `save` — trigger conditions (e.g., `save 900 1` means save after 900s if at least 1 key changed). Multiple rules stack. `save ""` disables RDB entirely.
- `rdbcompression` — use Snappy compression (default yes)
- `rdbchecksum` — append CRC64 checksum (default yes)
- `rdb-del-sync-files` — delete old RDB files on sync (default no)
- `rdb-save-incremental-fsync` — use incremental fsync during RDB save (default yes)
- `stop-writes-on-bgsave-error` — refuse writes if background save failed (default yes)

**Commands:**
- `BGSAVE` — trigger background save
- `LASTSAVE` — timestamp of last successful save
- `SAVE` — blocking save (use only in tests/debug)

**RDB file format:** binary, compact, supports RDB preamble (RDB + AOF hybrid). Load via `redis-check-rdb` for integrity checks.

## AOF (Append Only File)

Logs every write command. On restart, Redis replays the AOF to reconstruct the dataset.

**Config:**
- `appendonly yes` — enable AOF
- `appendfsync` — sync policy:
  - `always` — sync after every write (safest, slowest)
  - `everysec` — sync every second (default, recommended)
  - `no` — let OS decide (fastest, risk of losing up to 30s of data)
- `no-appendfsync-on-rewrite no` — don't defer fsync during BGREWRITEAOF (default no)
- `auto-aof-rewrite-percentage 100` — rewrite when AOF grows by this % since last rewrite
- `auto-aof-rewrite-min-size 64mb` — minimum AOF size before rewrite triggers
- `aof-use-rdb-preamble yes` — use RDB preamble in rewritten AOF (default yes, faster loading)
- `aof-load-truncated yes` — load truncated AOF instead of rejecting (default yes)
- `aof-timestamp-enabled no` — include timestamps in AOF entries
- `aof-rewrite-incremental-fsync yes` — incremental fsync during rewrite

**Commands:**
- `BGREWRITEAOF` — trigger AOF rewrite (compacts the log)
- `LASTSAVE` / `INFO persistence` — check AOF status

### Multi-Part AOF (MP-AOF)

Since Redis 7.0, AOF uses a multi-part structure: a base file (RDB preamble or AOF) plus incremental AOF files. This allows incremental backups and faster rewrites.

## BACKUP Command (new in 8.10)

Node-side backup based on MP-AOF. Produces a consistent, self-contained copy of the dataset without blocking writes.

**Subcommands:**
- `BACKUP START` — start a new backup into `backupdirname`
- `BACKUP STATUS` — report current backup state (idle/pending/snapshotting/incrementing/sealed/failed)
- `BACKUP SEAL` — freeze the backup (BASE + INCR + manifest)
- `BACKUP ABORT` — cancel an unsealed backup
- `BACKUP CLEANUP` — remove sealed backup files and return to idle
- `BACKUP LIST` — list pinned immutable backup file paths
- `BACKUP HELP` — show help

**Config:**
- `backupdirname "backupdir"` — directory for backup files (relative to working dir)
- `backup-sealed-ttl 0` — auto-remove sealed backups after N seconds (0 = disabled)

**Workflow:**
```
BACKUP START
# ... wait for snapshotting to complete ...
BACKUP STATUS    # check state
BACKUP SEAL      # freeze the backup
BACKUP LIST      # see pinned paths
BACKUP CLEANUP   # remove when done
```

**States:**
- `idle` — no backup in progress
- `pending` — waiting for BGREWRITEAOF to start
- `snapshotting` — creating base snapshot
- `incrementing` — recording incremental changes
- `sealed` — backup is frozen and immutable
- `failed` — backup encountered an error

**Gotchas:**
- Requires AOF to be enabled
- Blocks manual BGREWRITEAOF while in progress
- Hard-links AOF files — must be on the same filesystem
- `BACKUP ABORT` only works before sealing
- Sealed backups are immutable — use `BACKUP CLEANUP` to remove

## Persistence Tradeoffs

| Strategy | Durability | Performance | Recovery |
|---|---|---|---|
| RDB only | Last snapshot | High | Fast load |
| AOF only (everysec) | ~1 second | Good | Replay time |
| RDB + AOF | ~1 second | Good | Fast load + replay |
| AOF (always) | Every write | Lower | Replay time |
| BACKUP | Consistent | Moderate during snapshot | Fast restore |

## Lazy Freeing

Free memory asynchronously by forking a child to delete large objects.

**Config:**
- `lazyfree-lazy-eviction no` — lazy free on eviction
- `lazyfree-lazy-expire no` — lazy free on key expiration
- `lazyfree-lazy-server-del no` — lazy free on UNLINK/FLUSH
- `lazyfree-lazy-user-del no` — lazy free on DEL
- `lazyfree-lazy-user-flush no` — lazy free on FLUSHDB/FLUSHALL

When enabled, `DEL` becomes `UNLINK` (async). Use `UNLINK` explicitly for async deletion regardless of config.
