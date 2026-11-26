# Valkey Modules

Source: `valkey/commands/valkeymodules.py`, `valkey/commands/` package layout.

Module command objects hang off the client via `ValkeyModuleCommands` (sync) / `AsyncValkeyModuleCommands` (async):

| Client call | Module | Package |
|---|---|---|
| `r.json(encoder=JSONEncoder(), decoder=JSONDecoder())` | ValkeyJSON | `valkey/commands/json/` (also `path.py`, `decoders.py`) |
| `r.ft(index_name="idx")` | Search (RediSearch-compatible) | `valkey/commands/search/` (`aggregation.py`, `document.py`, `field.py`, `indexDefinition.py`, `query.py`, `querystring.py`, `reducers.py`, `result.py`, `suggestion.py`) |
| `r.ts()` | TimeSeries | `valkey/commands/timeseries/` (`commands.py`, `info.py`, `utils.py`) |
| `r.bf()` | Bloom filters | `valkey/commands/bf/` (`commands.py`, `info.py`) |
| `r.cf()` | Cuckoo filters | `valkey/commands/bf/` (shared package) |
| `r.cms()` | Count-Min Sketch | `valkey/commands/bf/` (shared package) |
| `r.topk()` | Top-K | `valkey/commands/bf/` (shared package) |
| `r.tdigest()` | t-digest | `valkey/commands/bf/` (shared package) |
| `r.graph(index_name="idx")` | Graph (RedisGraph-style) | `valkey/commands/graph/` (`node.py`, `edge.py`, `path.py`, `query_result.py`, `execution_plan.py`, `exceptions.py`) |

Notes:

- `r.json()` accepts custom `encoder`/`decoder`; async clients use `AsyncValkeyModuleCommands` with async `ft`/`graph` variants.
- Module clients are thin command wrappers — command semantics are those of the server-side modules (ValkeyJSON, Valkey Search, Valkey Bloom, Valkey TimeSeries, Valkey Graph). Verify module command options against the module's own documentation, not against this client.
- The default client-side-cache deny list already excludes most module introspection commands (`FT.*`, `CF.*`, `CMS.*`, `BF.*` info/debug, `JSON.DEBUG`) — see 10-advanced.
- Test suites in the repo cover module behavior: `tests/test_json.py`, `tests/test_search.py`, `tests/test_bloom.py`, `tests/test_timeseries.py`, `tests/test_graph.py` — useful as runnable reference for exact call shapes.
