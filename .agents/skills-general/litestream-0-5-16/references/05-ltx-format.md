# LTX Format

Table of contents:
- [Concepts](#concepts)
- [File layout](#file-layout)
- [Header (100 bytes)](#header-100-bytes)
- [Page frames](#page-frames)
- [Page index](#page-index)
- [Trailer (16 bytes)](#trailer-16-bytes)
- [Checksums](#checksums)
- [Naming convention](#naming-convention)
- [Levels and compaction](#levels-and-compaction)
- [WAL vs LTX](#wal-vs-ltx)

Reference implementation: `github.com/superfly/ltx`.

## Concepts

LTX (Log Transaction) files are immutable, self-contained, checksummed archives of database changes:

- **Immutable** — never modified after upload; new changes create new files
- **Append-only** — a TXID range is only ever extended
- **Indexed** — a page index allows seeking individual pages without reading the whole file
- **Checksummed** — CRC-64 per file and pre/post-apply database checksums
- **Two kinds** — WAL-derived LTX files (incremental changes) and full snapshots (level 9)

## File layout

```
┌─────────────────────────┐
│ Header         100 bytes│  magic "LTX1", page size, TXID range, timestamp, checksums
├─────────────────────────┤
│ Page frames             │  per page: 4-byte pgno + PageSize bytes of data
├─────────────────────────┤
│ Page index              │  binary-searchable page no → offset/size
├─────────────────────────┤
│ Trailer        16 bytes │  post-apply checksum + whole-file checksum
└─────────────────────────┘

FileSize = 100 + N*(4 + PageSize) + PageIndexSize + 16
```

## Header (100 bytes)

```
Offset  Size  Field
0       4     Magic ("LTX1" — corresponds to ltx.Version 2)
4       4     Flags
8       4     PageSize
12      4     Commit (page count after applying the file)
16      8     MinTXID
24      8     MaxTXID
32      8     Timestamp (ms since Unix epoch)
40      8     PreApplyChecksum
48      8     WALOffset (0 for snapshots)
56      8     WALSize (0 for snapshots)
64      4     WALSalt1
68      4     WALSalt2
72      8     NodeID
80     20     Reserved (zeros)
```

The `CreatedAt` timestamp is what restore plans and the `litestream ltx` listing rely on for point-in-time selection — backends must preserve it (or set it from upload time) when writing files.

## Page frames

Each frame is `Pgno` (uint32, 1-based) + the full page (`PageSize` bytes):

```
Offset  Size     Field
0       4        Page number
4       PageSize Page data
```

Constraints: pages are written sequentially when created but randomly accessible via the index; the 1 GB **lock page is never included**; compacted files hold only the latest version of each page.

## Page index

A binary-search index mapping page number → `{offset, size}` of the frame. Use `ltx.DecodePageIndex` rather than parsing bytes manually.

## Trailer (16 bytes)

```
Offset  Size  Field
0       8     PostApplyChecksum (database checksum after applying the file)
8       8     FileChecksum (CRC-64 of the entire file)
```

## Checksums

CRC-64 (ECMA table) throughout: the whole-file checksum in the trailer, plus pre-apply and post-apply database checksums in the header/trailer that let restore verify the chain of transactions. Validation failures surface as LTX errors ("ltx validation failed", "nonsequential page numbers", "non-contiguous transaction files").

## Naming convention

```
MMMMMMMMMMMMMMMM-NNNNNNNNNNNNNNNN.ltx
  MinTXID (16 hex)      MaxTXID (16 hex)

0000000000000001-0000000000000064.ltx   TXIDs 1..100
0000000000000065-00000000000000c8.ltx   TXIDs 101..200
```

The TXID range is the file's identity — filenames sort lexicographically in TXID order, which is what level-based listings depend on.

## Levels and compaction

```
ltx/0000/    L0 — raw WAL-derived files (pruned by l0-retention, default 5m)
ltx/0001/    L1 — compacted every 30s (default)
ltx/0002/    L2 — compacted every 5m (default)
ltx/0003/    L3 — compacted every 1h (default)
ltx/0009/    level 9 — full snapshots (snapshot.interval 24h default)
```

- Levels 1–8 are configurable via `levels:`; level 0 always has interval 0 and the highest allowed level is 8.
- Level **9 is the snapshot level** — full database state, driven by `snapshot.interval`/`snapshot.retention`, not by `levels`.
- Compaction merges files by page number (latest version wins), skips the lock page, and preserves the earliest source `CreatedAt` so point-in-time granularity is not lost.
- The 1 GB lock page (pgno 262145 at 4 KB, 131073 at 8 KB, 65537 at 16 KB, 32769 at 32 KB) is skipped in every LTX file.

## WAL vs LTX

| Aspect | SQLite WAL | LTX |
|---|---|---|
| Purpose | Temporary changes | Permanent archive |
| Mutability | Mutable (checkpointed/truncated) | Immutable |
| Structure | Sequential frames | Indexed pages |
| Checksum | Per-frame | Per-file + pre/post-apply |
| Lock page | Present | Always skipped |
| Lifetime | Until checkpoint | Until retention prunes it |
