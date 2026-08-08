# Environment Variables and Placeholder Expansion

## Subprocess environment

Clients that launch plugin subprocesses (stdio MCP servers) MUST provide:

| Variable | Value |
|---|---|
| `PLUGIN_ROOT` | Absolute path to the filesystem-resolved plugin root |
| `PLUGIN_DATA` | Absolute path to a client-managed persistent data directory for that plugin instance |

### PLUGIN_DATA

- Client chooses the location
- MUST be created before launching the subprocess
- MUST be writable to the subprocess
- Contents MUST persist across plugin updates
- Client MAY delete on plugin uninstall

Use `PLUGIN_DATA` for: installed dependencies (node_modules, virtualenvs), generated code, caches, and other plugin state that persists across updates.

Use `PLUGIN_ROOT` for: bundled scripts, binaries, and config files that ship with the plugin.

### Environment overlay

1. Client chooses base subprocess environment (may inherit, omit, or sanitize ambient variables)
2. After placeholder expansion, `env` entries from the server config overlay the base environment
3. Client then sets `PLUGIN_ROOT` and `PLUGIN_DATA`, replacing any same-name entries

Plugins MUST NOT depend on base-environment variables unless the spec requires them or the server config supplies them explicitly.

Example:

```text
PLUGIN_ROOT=/home/alex/.agents/plugins/devtools
PLUGIN_DATA=/home/alex/.agents/plugins/data/devtools
```

## Placeholder expansion

Clients MUST expand `${PLUGIN_ROOT}` and `${PLUGIN_DATA}` in supported fields. Expansion is a single, non-recursive textual replacement. Text introduced by replacement is NOT rescanned.

### Where expansion applies

| Field | Expansion? |
|---|---|
| `args` (each string element) | Yes |
| `env` values | Yes |
| `cwd` | Yes |
| `env` keys | No |
| `command` | No |
| `url` | No |
| Header names/values | No |
| Fixed component locations | No |

### Reserved environment variable names

An MCP server's `env` MUST NOT contain entries named `PLUGIN_ROOT` or `PLUGIN_DATA`. Such an entry makes the server configuration invalid. Clients supply these variables themselves.

### Unrecognized placeholders

Unrecognized placeholder-like text MUST remain literal. Clients MUST NOT perform any other placeholder or environment-variable expansion.

### Secrets

Configured `env` and `headers` values are visible package data, not a portable secret mechanism. Plugins MUST NOT embed credentials or other secrets in `env` or `headers`.

## Example

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
  "mcpServers": {
    "database": {
      "type": "stdio",
      "command": "npx",
      "args": ["--config", "${PLUGIN_ROOT}/config/db.json"],
      "cwd": "${PLUGIN_ROOT}",
      "env": {
        "DATA_DIR": "${PLUGIN_DATA}/database"
      }
    }
  }
}
```

After expansion (with `PLUGIN_ROOT=/opt/plugins/db`, `PLUGIN_DATA=/opt/plugins/data/db`):

```
args: ["--config", "/opt/plugins/db/config/db.json"]
cwd: "/opt/plugins/db"
env: { "DATA_DIR": "/opt/plugins/data/db/database" }
```
