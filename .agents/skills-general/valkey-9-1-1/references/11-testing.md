# Testing

Valkey uses two test systems: C++ unit tests (GoogleTest) and Tcl integration tests.

## Unit Tests

Located in `src/unit/`. Written in C++ using GoogleTest (gtest/gmock). Cover data structures and low-level logic.

### Building and running

```bash
# Build with unit tests (Makefile)
# Enable in src/Makefile or via CMake:
cmake .. -DBUILD_UNIT_GTESTS=yes
make -C src test-unit

# Run all unit tests
./src/unit/valkey-unit-gtests

# Run a specific test
./src/unit/valkey-unit-gtests --gtest_filter='DictTest.AddAndLookup'

# Run all tests in a suite
./src/unit/valkey-unit-gtests --gtest_filter='QuicklistTest.*'
```

### Test files

| File | Coverage |
|---|---|
| `test_dict.cpp` | Dictionary (hashtable) operations |
| `test_hashtable.cpp` | Generic hashtable |
| `test_quicklist.cpp` | Quicklist (list internal encoding) |
| `test_listpack.cpp` | Listpack encoding |
| `test_ziplist.cpp` | Ziplist encoding |
| `test_zipmap.cpp` | Zipmap encoding |
| `test_intset.cpp` | Intset (integer set) |
| `test_rax.cpp` | Radix tree |
| `test_sds.cpp` | SDS (simple dynamic string) |
| `test_vector.cpp` | Dynamic vector |
| `test_fifo.cpp` | FIFO queue |
| `test_queues.cpp` | Queue implementations |
| `test_mutexqueue.cpp` | Lock-free mutex queue |
| `test_kvstore.cpp` | KV store (cluster slot mapping) |
| `test_entry.cpp` | Entry type system |
| `test_object.cpp` | Server objects |
| `test_t_stream.cpp` | Stream data structure |
| `test_vset.cpp` | Vector set (with ARM NEON SIMD) |
| `test_bitops.cpp` | Bit operations |
| `test_crc64.cpp` / `test_crc64combine.cpp` | CRC64 checksums |
| `test_sha1.cpp` / `test_sha256.cpp` | Hash functions |
| `test_networking.cpp` | Network utilities |
| `test_timeout.cpp` | Timeout handling |
| `test_endianconv.cpp` | Endianness conversion |
| `test_zmalloc.cpp` | Memory allocator |
| `test_valkey_strtod.cpp` | String-to-double parsing |

## Integration Tests

Located in `tests/`. Written in Tcl. Test end-to-end functionality using real server instances.

### Running tests

```bash
# Full integration suite
make test

# Unit tests
make test-unit

# Module API tests
make test-modules

# Sentinel tests
make test-sentinel

# Cluster tests
make test-cluster

# RDMA tests
make test-rdma
```

### Running specific tests

```bash
# Single test file
./runtest --single unit/test_condition_variable.tcl

# Specific test within a file
./runtest --single integration/replication/psync2 --tag <tag>

# With TLS
./runtest --tls

# With TLS module
./runtest --tls-module

# Against external server
./runtest --host 10.0.0.1 --port 6379

# Cluster mode
./runtest --cluster-mode

# Large memory tests
./runtest --large-memory

# Valgrind
./runtest --valgrind

# Single database only
./runtest --singledb

# Ignore specific encodings
./runtest --ignore-encoding

# Skip digest checks
./runtest --ignore-digest
```

### Test structure

```
tests/
├── integration/          # Integration test files
│   ├── replication/      # Replication tests
│   ├── cluster/          # Cluster tests
│   └── ...
├── unit/                 # Unit tests (Tcl-based)
├── modules/              # Module test helpers
├── sentinel/             # Sentinel tests
├── helpers/              # Test helper libraries
├── support/              # Support infrastructure
├── test_helper.tcl       # Test framework entry point
└── instances.tcl         # Server instance management
```

### Test tags

| Tag | Meaning |
|---|---|
| `external:skip` | Not compatible with external servers |
| `cluster` | Uses cluster with multiple nodes |
| `cluster:skip` | Not compatible with `--cluster-mode` |
| `large-memory` | Requires >100MB |
| `tls` | Uses TLS |
| `tls:skip` | Not compatible with `--tls` |
| `ipv6` | Uses IPv6 |
| `needs:repl` | Uses replication |
| `needs:debug` | Uses DEBUG command |
| `needs:save` | Uses SAVE/BGSAVE |
| `needs:config-maxmemory` | Manipulates memory limits |
| `needs:pfdebug` | Uses PFDEBUG |
| `needs:reset` | Uses RESET command |
| `needs:config-resetstat` | Uses CONFIG RESETSTAT |
| `singledb` | Runs as if `--singledb` |
| `valgrind:skip` | Not compatible with valgrind |
| `network` | Requires network operations |
| `needs:other-server` | Requires `--other-server-path` |
| `compatible-redis` | Runs against Redis |

### Debugging tests

```tcl
# Breakpoint in test code
bp 1
# Press 'c' to continue, 'i' to print local variables

# Skip specific breakpoints
set ::bp_skip "label1 label2"
```

### TLS test setup

```bash
# Generate test certificates
./utils/gen-test-certs.sh

# Install tcl-tls (Debian/Ubuntu)
sudo apt install tcl-tls

# Build with TLS
make BUILD_TLS=yes

# Run tests
./runtest --tls
```

## Code Style

```bash
# Format with clang-format-18
clang-format-18 -i src/myfile.c
```

CI enforces `clang-format-18` on all `*.c`, `*.h`, `*.cpp`, `*.hpp` files.
