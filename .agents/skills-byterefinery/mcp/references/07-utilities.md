# Utilities

Cross-cutting concerns shared across server features.

## Pagination

List endpoints (`tools/list`, `resources/list`, `prompts/list`, `resources/templates/list`) support cursor-based pagination.

**Request:**

```json
{ "method": "tools/list", "params": { "cursor": "optional-cursor-value" } }
```

**Response:**

```json
{
  "result": {
    "resultType": "complete",
    "tools": [ /* items */ ],
    "nextCursor": "next-page-cursor"
  }
}
```

- `nextCursor` is absent or null when there are no more results
- Clients pass `nextCursor` as `cursor` in the next request to get the following page

## Caching

List and read endpoints support caching via `ttlMs` and `cacheScope` fields on results.

**Fields:**

- `ttlMs` — freshness hint in milliseconds; clients may cache responses for this duration
- `cacheScope` — `"public"` (shared intermediaries may cache) or `"private"` (only the receiving client may cache)

**Applicable endpoints:**

- `tools/list`, `prompts/list`, `resources/list`
- `resources/read`, `resources/templates/list`
- `server/discover`

**Invalidation:**

- `listChanged` notifications signal that cached lists are stale
- Resource update notifications signal that cached resource contents are stale
- Clients should re-fetch after receiving invalidation notifications

## Completion

Servers can provide argument auto-completion for resources and prompts through the completion API.

**Request:**

```json
{
  "method": "completion/complete",
  "params": {
    "ref": {
      "type": "ref/resource",
      "uri": "file:///{path}"
    },
    "argument": {
      "name": "path",
      "value": "src/"
    }
  }
}
```

**Response:**

```json
{
  "result": {
    "resultType": "complete",
    "completion": {
      "values": ["src/main.rs", "src/lib.rs", "src/utils/"],
      "total": 10,
      "hasMore": true
    }
  }
}
```

## Logging

Logging is set per-request via `io.modelcontextprotocol/logLevel` in `_meta`. Servers MUST NOT emit `notifications/message` for requests that did not include this field.

**Log levels** (from most to least verbose): `debug`, `info`, `notice`, `warning`, `error`, `critical`, `alert`, `emergency`.

```json
{
  "params": {
    "_meta": {
      "io.modelcontextprotocol/logLevel": "debug"
    }
  }
}
```

Note: the `logging/setLevel` method is removed. Log level is now per-request.

The Logging feature itself is deprecated. New implementations should log to `stderr` (stdio) or use OpenTelemetry instead.
