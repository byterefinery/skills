# Change Data Capture (CDC) Reference

CDC streams INSERT, UPDATE, and DELETE events to an HTTP endpoint with at-least-once delivery.

## Simple Configuration

Pass a URL directly:

```bash
rqlited -cdc-config 'http://webhook.example.com/cdc' /data/node1
```

Or provide a config file path:

```bash
rqlited -cdc-config /path/to/cdc-config.json /data/node1
```

## Full Configuration

```json
{
  "endpoint": "http://webhook.example.com/cdc",
  "service_id": "production-db-01",
  "row_ids_only": false,
  "table_filter": "users|orders",
  "max_batch_size": 10,
  "max_batch_delay": "200ms",
  "high_watermark_interval": "1s",
  "transmit_timeout": "5s",
  "transmit_retry_policy": "linear",
  "transmit_min_backoff": "1s",
  "transmit_max_backoff": "30s",
  "tls": {
    "ca_cert_file": "/certs/ca.crt",
    "cert_file": "/certs/client.crt",
    "key_file": "/certs/client.key",
    "insecure_skip_verify": false,
    "server_name": "webhook.example.com"
  }
}
```

### Configuration Fields

| Field | Type | Default | Description |
|---|---|---|---|
| `endpoint` | string | *(required)* | HTTP URL for CDC events |
| `service_id` | string | — | Identifier included in events (for multi-cluster consumers) |
| `row_ids_only` | bool | false | Send only row IDs, not full row data |
| `table_filter` | regex | all tables | Only capture changes matching this regex |
| `max_batch_size` | int | 10 | Max events per batch request |
| `max_batch_delay` | duration | 200ms | Max wait before sending partial batch |
| `high_watermark_interval` | duration | 1s | Interval for high watermark updates |
| `transmit_timeout` | duration | 5s | HTTP request timeout |
| `transmit_retry_policy` | string | `linear` | `linear` or `exponential` |
| `transmit_min_backoff` | duration | 1s | Minimum retry delay |
| `transmit_max_backoff` | duration | 30s | Maximum retry delay |

## Event Format

Each batch request sends a JSON array of change events:

```json
[
  {
    "db_name": "",
    "table_name": "users",
    "operation": "INSERT",
    "row_id": 1,
    "old_data": null,
    "new_data": {
      "id": 1,
      "name": "alice",
      "email": "alice@example.com"
    },
    "service_id": "production-db-01",
    "timestamp": 1718000000000
  },
  {
    "db_name": "",
    "table_name": "users",
    "operation": "UPDATE",
    "row_id": 1,
    "old_data": {
      "id": 1,
      "name": "alice",
      "email": "alice@example.com"
    },
    "new_data": {
      "id": 1,
      "name": "alice updated",
      "email": "alice@example.com"
    },
    "service_id": "production-db-01",
    "timestamp": 1718000000001
  },
  {
    "db_name": "",
    "table_name": "users",
    "operation": "DELETE",
    "row_id": 1,
    "old_data": {
      "id": 1,
      "name": "alice updated",
      "email": "alice@example.com"
    },
    "new_data": null,
    "service_id": "production-db-01",
    "timestamp": 1718000000002
  }
]
```

### Event Fields

| Field | Type | Description |
|---|---|---|
| `db_name` | string | Database name (empty for default) |
| `table_name` | string | Table that changed |
| `operation` | string | `INSERT`, `UPDATE`, or `DELETE` |
| `row_id` | number/nil | Row ID (sqlite_rowid), null if table has no rowid |
| `old_data` | object/null | Row state before change (null for INSERT) |
| `new_data` | object/null | Row state after change (null for DELETE) |
| `service_id` | string | Service identifier from config |
| `timestamp` | number | Unix timestamp in milliseconds |

## High Watermark Events

Periodically, rqlite sends a high watermark event indicating the latest processed Raft index:

```json
{
  "high_watermark": {
    "raft_index": 12345
  }
}
```

Consumers can use this to track their replication lag and ensure no events are missed.

## Limitations

- **DDL is not captured** — CREATE, ALTER, DROP statements do not generate CDC events
- **Only available on voting nodes** — cannot be enabled with `-raft-non-voter`
- **At-least-once delivery** — events may be delivered more than once; consumers should be idempotent
- **No ordering guarantees across batches** — events within a batch are ordered, but batches may arrive out of order during retries
- **Triggers are not captured** — only direct INSERT/UPDATE/DELETE on the affected table

## CDC Consumer Best Practices

1. **Be idempotent** — deduplicate by `row_id` + `timestamp` or use the high watermark
2. **Ack with 200 OK** — non-200 responses trigger retries
3. **Track high watermarks** — know your replication lag
4. **Handle batched events** — process the entire array, not individual events
5. **Set reasonable timeouts** — slow consumers block the CDC pipeline
