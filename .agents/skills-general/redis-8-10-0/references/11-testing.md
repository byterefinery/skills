# Testing

## Test Suite

Redis uses Tcl-based integration tests and C unit tests.

### Running Tests

```bash
# Run all tests
./runtest

# Run specific test group
./runtest --group unit
./runtest --group replication
./runtest --group cluster
./runtest --group sentinel
./runtest --group acl
./runtest --group persistence
./runtest --group streams
./runtest --group json
./runtest --group search
./runtest --group timeseries
./runtest --group probabilistic
./runtest --group vectorsets

# Run specific test file
./runtest --single unit/info.test

# Run with specific server
./runtest --server ./src/redis-server

# Parallel tests
./runtest -i  # run tests in parallel

# Verbose output
./runtest -v

# Stop on first failure
./runtest --stop

# Debug mode
./runtest --debug

# Skip slow tests
./runtest --skip-slow
```

### Cluster Tests

```bash
./runtest-cluster
```

### Sentinel Tests

```bash
./runtest-sentinel
```

### Module API Tests

```bash
./runtest-moduleapi
```

## Test Dependencies

```bash
# Install test dependencies
make bootstrap

# Required:
# - Tcl 8.6+
# - curl (for some tests)
# - python3 (for some module tests)
```

## Unit Tests

Redis includes C unit tests for internal data structures.

```bash
# Run unit tests
cd src
make test
```

## Module Tests

Each bundled module has its own test suite.

```bash
# Test all modules
make test

# Test specific module
make test redisjson
make test redisearch
make test redistimeseries
make test redisbloom
```

## Benchmarking

```bash
# Basic benchmark
./src/redis-benchmark -n 100000 -c 50 -q

# Specific commands
./src/redis-benchmark -n 100000 -t SET,GET,INCR,HSET,ZADD -q

# With pipeline
./src/redis-benchmark -n 100000 -P 16 -q

# With different data sizes
./src/redis-benchmark -n 100000 -d 1024 -q  # 1KB values

# With TLS
./src/redis-benchmark -n 100000 --tls -q

# Cluster mode
./src/redis-benchmark -n 100000 -c 50 -q -h 127.0.0.1 -p 7000 -C
```

## Debugging

### Debug Commands

```bash
# Enable debug commands
redis-server --enable-debug-command yes

# Or in redis.conf
enable-debug-command yes
```

**Debug commands:**
- `DEBUG OBJECT <key>` — internal object info
- `DEBUG SLEEP <seconds>` — sleep (test blocking)
- `DEBUG SET-ACTIVE-EXPIRE <0|1>` — toggle active expire cycle
- `DEBUG RELOAD` — force RDB reload (testing)
- `DEBUG CRASH` — intentional crash (testing crash logs)
- `DIGEST` — compute dataset checksum

### Memory Debugging

```bash
# Memory analysis
MEMORY DOCTOR
MEMORY STATS
MEMORY USAGE <key> [SAMPLES <n>]
MEMORY SAMPLES <count>
MEMORY HELP
```

### Crash Logs

Redis generates crash logs in the working directory (configurable via `crash-log-enabled` and `crash-log-dir`).

### Sanitizers

```bash
# Build with AddressSanitizer
make SANITIZER=address

# Build with UndefinedBehaviorSanitizer
make SANITIZER=undefined

# Build with ThreadSanitizer
make SANITIZER=thread

# Build with MemorySanitizer (clang only)
CC=clang make SANITIZER=memory
```

## Gotchas

- **`make bootstrap` installs test deps** — run before `./runtest` on a fresh system
- **Tests require Tcl 8.6+** — older versions may fail on string operations
- **`DEBUG` commands are disabled by default** — enable with `enable-debug-command yes`
- **Sanitizers force `MALLOC=libc`** — Jemalloc conflicts with sanitizers
- **Cluster tests need multiple ports** — ensure ports 30001-30006 (or similar) are available
- **`./runtest --single` is faster for debugging** — run one test file instead of the full suite
- **Module tests require built modules** — run `make build` before `make test`
- **Memory tests need large datasets** — `MEMORY USAGE` with `SAMPLES` option averages over N samples for accuracy
- **Crash logs are written to working directory** — check the server's CWD, not the config directory
