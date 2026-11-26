# MultiDB Client

The `MultiDBClient` provides Active-Active geographic failover across multiple Redis deployments. It continuously monitors database health, detects failures, and automatically fails over to the next healthy database.

**Note:** This is an experimental feature. Use `@experimental` marker.

## Basic Usage

```python
from redis.multidb.client import MultiDBClient
from redis.multidb.config import MultiDbConfig, DatabaseConfig

# Configure databases
config = MultiDbConfig(
    databases=[
        DatabaseConfig.from_url("redis://primary.example.com:6379/0", weight=1),
        DatabaseConfig.from_url("redis://secondary.example.com:6379/0", weight=2),
    ],
)

# Create and initialize client
client = MultiDBClient(config)
client.initialize()

# Use like a regular Redis client
client.set("key", "value")
result = client.get("key")

# Cleanup
client.close()
```

## Configuration

### MultiDbConfig

```python
from redis.multidb.config import MultiDbConfig, DatabaseConfig, InitialHealthCheck

config = MultiDbConfig(
    # Databases in priority order (by weight)
    databases=[
        DatabaseConfig.from_url("redis://us-east.example.com:6379", weight=1),
        DatabaseConfig.from_url("redis://eu-west.example.com:6379", weight=2),
        DatabaseConfig.from_url("redis://ap-south.example.com:6379", weight=3),
    ],

    # Health check interval in seconds
    health_check_interval=10,

    # Health check policy
    health_check_policy="ALL",  # "ALL" or "ACTIVE"

    # Failover configuration
    failover_strategy=None,      # Default strategy if None
    failover_attempts=3,         # Max failover attempts
    failover_delay=1,            # Delay between failover attempts (seconds)

    # Auto-fallback
    auto_fallback_interval=60,   # Check for fallback every N seconds

    # Command retry
    command_retry=None,          # Retry policy for commands

    # Health checks and failure detectors
    health_checks=None,          # Custom health checks
    failure_detectors=None,      # Custom failure detectors

    # Event dispatcher
    event_dispatcher=None,
)
```

### DatabaseConfig

```python
from redis.multidb.config import DatabaseConfig

# From URL
db = DatabaseConfig.from_url("redis://host:6379/0", weight=1)

# From parameters
db = DatabaseConfig(
    connection_kwargs={
        "host": "localhost",
        "port": 6379,
        "db": 0,
        "password": "secret",
    },
    weight=1,
)
```

## Async MultiDB Client

```python
from redis.asyncio.multidb.client import MultiDBClient
from redis.multidb.config import MultiDbConfig, DatabaseConfig

async def main():
    config = MultiDbConfig(
        databases=[
            DatabaseConfig.from_url("redis://primary.example.com:6379", weight=1),
            DatabaseConfig.from_url("redis://secondary.example.com:6379", weight=2),
        ],
    )

    client = MultiDBClient(config)
    await client.initialize()

    await client.set("key", "value")
    result = await client.get("key")

    await client.close()
```

## Health Checks

```python
from redis.multidb.healthcheck import HealthCheck, HealthCheckPolicy

# Health check policy
policy = HealthCheckPolicy.ALL   # Check all databases
policy = HealthCheckPolicy.ACTIVE  # Check only active database

# Custom health check
class MyHealthCheck(HealthCheck):
    async def check(self, database):
        # Custom health check logic
        return True  # Healthy
```

## Circuit Breaker

Each database has a circuit breaker that prevents repeated attempts to unhealthy databases.

```python
from redis.multidb.circuit import CircuitBreaker, State

# Circuit states
State.CLOSED    # Database is healthy, accepting traffic
State.OPEN      # Database is unhealthy, rejecting traffic
State.HALF_OPEN # Testing if database recovered
```

The circuit breaker:
- Opens after consecutive failures
- Transitions to half-open after a grace period
- Closes again on successful health check

## Failover Strategies

```python
from redis.multidb.failover import FailoverStrategy

# Default strategy — failover to next healthy database by weight
# Custom strategy
class MyFailoverStrategy(FailoverStrategy):
    def select_database(self, databases):
        # Return the database to fail over to
        pass
```

## Monitoring

```python
# Get current databases
databases = client.get_databases()

# Get active database
active = client.command_executor._active_database

# Set active database manually
client.set_active_database(database)
```

## MultiDB Gotchas

- **Experimental feature** — Marked with `@experimental`. API may change
- **Not compatible with HIMPORT** — HIMPORT commands are not supported on MultiDBClient
- **Not compatible with Pub/Sub** — Pub/Sub requires a dedicated connection, which conflicts with failover
- **Health checks run in background** — The client uses a background scheduler for recurring health checks
- **`initialize()` is required** — Call `client.initialize()` before using the client. It performs initial health checks and sets the active database
- **Weight determines priority** — Lower weight = higher priority. The database with weight 1 is preferred
- **Auto-fallback** — When the preferred database recovers, traffic automatically switches back after `auto_fallback_interval`
- **Connection pools per database** — Each database has its own connection pool. Failover switches which pool is active
- **Thread-safe** — The sync MultiDBClient is thread-safe. The async version is designed for single-threaded async use
- **`close()` stops background tasks** — Always call `close()` to shut down the background health check scheduler
