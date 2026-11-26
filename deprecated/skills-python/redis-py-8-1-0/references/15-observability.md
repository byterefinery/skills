# Observability

## OpenTelemetry Integration

redis-py includes built-in OpenTelemetry support for collecting Redis metrics.

```python
# Requires: pip install "redis[otel]"
from redis.observability import get_observability_instance, OTelConfig, MetricGroup

# Initialize OpenTelemetry
otel = get_observability_instance()
otel.init(OTelConfig())
```

### OTelConfig

```python
from redis.observability import OTelConfig, MetricGroup, TelemetryOption

config = OTelConfig(
    # Metric groups to collect
    metric_groups=[
        MetricGroup.OPERATION_DURATION,
        MetricGroup.ERROR_COUNT,
        MetricGroup.PUBSUB_MESSAGES,
        MetricGroup.CONNECTION_COUNT,
        MetricGroup.CONNECTION_WAIT_TIME,
        MetricGroup.CONNECTION_CREATE_TIME,
        MetricGroup.CSC_ITEMS,  # Client-side caching
    ],

    # Telemetry options
    telemetry_options=[
        TelemetryOption.DATABASE_NAME,
        TelemetryOption.OPERATION_NAME,
        TelemetryOption.CONNECTION_STATE,
    ],

    # Exporter configuration
    exporter=None,  # Default OTLP exporter
)

otel = get_observability_instance()
otel.init(config)
```

### Metric Groups

| Metric Group | Description |
|---|---|
| `OPERATION_DURATION` | Duration of Redis operations |
| `ERROR_COUNT` | Count of failed operations |
| `PUBSUB_MESSAGES` | Pub/Sub message counts |
| `CONNECTION_COUNT` | Active connection count |
| `CONNECTION_WAIT_TIME` | Time waiting for connections from pool |
| `CONNECTION_CREATE_TIME` | Time to establish new connections |
| `CSC_ITEMS` | Client-side caching metrics |

## Event Dispatcher

Hook into client lifecycle events for custom observability.

```python
from redis.event import (
    EventDispatcher,
    AfterConnectionReleasedEvent,
    AfterPooledConnectionsInstantiationEvent,
    AfterPubSubConnectionInstantiationEvent,
    AfterSingleConnectionInstantiationEvent,
    AfterSlotsCacheRefreshEvent,
    ClientType,
)

class MyEventDispatcher(EventDispatcher):
    def on_after_connection_released(self, event: AfterConnectionReleasedEvent):
        # Called when a connection is released back to the pool
        log_connection_release(event)

    def on_after_pooled_connections_instantiation(self, event: AfterPooledConnectionsInstantiationEvent):
        # Called when connection pools are created
        log_pool_creation(event.pools, event.client_type)

    def on_after_slots_cache_refresh(self, event: AfterSlotsCacheRefreshEvent):
        # Called when cluster slots cache is refreshed
        log_topology_change(event)

# Use with client
r = redis.Redis(host="localhost", event_dispatcher=MyEventDispatcher())
```

### Event Types

| Event | Trigger |
|---|---|
| `AfterConnectionReleasedEvent` | Connection returned to pool |
| `AfterPooledConnectionsInstantiationEvent` | Connection pools created |
| `AfterPubSubConnectionInstantiationEvent` | Pub/Sub connection created |
| `AfterSingleConnectionInstantiationEvent` | Single connection acquired |
| `AfterSlotsCacheRefreshEvent` | Cluster topology updated |

### Client Types

| Type | Description |
|---|---|
| `ClientType.SYNC` | Synchronous client |
| `ClientType.ASYNC` | Asynchronous client |

## Observability Attributes

```python
from redis.observability.attributes import (
    DB_CLIENT_CONNECTION_POOL_NAME,
    DB_CLIENT_CONNECTION_STATE,
    ConnectionState,
    CSCReason,
    CSCResult,
    PubSubDirection,
    GeoFailoverReason,
)

# Connection states
ConnectionState.CREATED
ConnectionState.CLOSED
ConnectionState.REUSED

# Client-side caching
CSCReason.HIT
CSCReason.MISS
CSCResult.INVALIDATED

# Pub/Sub
PubSubDirection.SUBSCRIBE
PubSubDirection.UNSUBSCRIBE
```

## Recorder

Direct access to metrics recording (for custom instrumentation).

```python
from redis.observability.recorder import (
    record_operation_duration,
    record_error_count,
    record_pubsub_message,
    record_connection_count,
    record_connection_create_time,
    record_connection_wait_time,
    record_connection_closed,
    init_csc_items,
    register_csc_items_callback,
)

# Record custom metrics
record_operation_duration("GET", duration=0.001, attributes={...})
record_error_count("GET", error_type="TimeoutError", attributes={...})
```

## Observability Gotchas

- **Requires `redis[otel]` extra** — Install with `pip install "redis[otel]"` for OpenTelemetry support
- **Global singleton** — `get_observability_instance()` returns a global singleton. Initialize once per process
- **`reset_observability_instance()`** — Use for testing to reset the singleton between test cases
- **Event dispatcher is per-client** — Each client can have its own event dispatcher
- **Events are synchronous** — Event handlers run synchronously. Avoid blocking operations in handlers
- **Metrics are opt-in** — Observability is disabled by default. Call `otel.init(config)` to enable
- **Attributes are standardized** — Use the attribute constants from `redis.observability.attributes` for consistency with other Redis clients
- **Cluster events** — `AfterSlotsCacheRefreshEvent` is specific to cluster clients and fires when topology changes
