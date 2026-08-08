---
name: agent-plugins-spec
description: Agent Plugins Specification 1.0.0 — vendor-neutral standard for packaging AI agent extensions into distributable plugins. Use when creating, validating, or implementing Agent Plugins (plugin.json manifests, skills/ discovery, mcp.json MCP servers, client extensions, PLUGIN_ROOT/PLUGIN_DATA). Covers plugin package model, component discovery, manifest schema, MCP transports, placeholder expansion, and client conformance.
license: CC-BY-4.0 (spec), Apache-2.0 (schemas)
compatibility: Requires jq for JSON validation; jsonschema for schema validation
metadata:
  tags:
    - spec
    - packaging
    - mcp
    - skills
    - ai-agents
---

# agent-plugins-spec

## Overview

Agent Plugins is an open, vendor-neutral standard for packaging reusable components that extend AI agents into distributable plugins. It defines a portable directory-based package format combining [Agent Skills](https://agentskills.io) and [MCP servers](https://modelcontextprotocol.io) under a single manifest.

Key concepts:

- **Plugin** — a directory with `plugin.json` manifest and optional components
- **Component types** — Agent Skills (`skills/`) and MCP servers (`mcp.json`)
- **Client** — a tool that discovers, loads, and executes plugin components
- **Extension namespace** — reverse-domain identifier for client-specific data

A conformant client loads `plugin.json`, discovers components from fixed locations, and applies failure isolation so one broken component does not block others.

## Usage

### Creating a plugin

The smallest valid plugin:

```text
my-plugin/
├── plugin.json
└── skills/
    └── greet/
        └── SKILL.md
```

`plugin.json`:

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
  "name": "my-plugin"
}
```

`skills/greet/SKILL.md`:

```markdown
---
name: greet
description: Greet the user and offer help.
---

Greet the user and offer help.
```

### Adding MCP servers

Create `mcp.json` at the plugin root:

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
  "mcpServers": {
    "local-tool": {
      "type": "stdio",
      "command": "./bin/tool",
      "args": ["--data", "${PLUGIN_DATA}/tool"]
    },
    "remote-api": {
      "type": "streamable-http",
      "url": "https://api.example.com/mcp"
    }
  }
}
```

### Adding client extensions

Place client-specific data under reverse-domain namespaces:

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
  "name": "my-plugin",
  "extensions": {
    "com.example.client": {
      "setting": true
    }
  }
}
```

Or use a top-level directory: `com.example.client/hooks/hooks.json`.

### Validating a plugin

1. Check `plugin.json` against [`plugin.schema.json`](https://agent-plugins.org/schemas/1.0.0/plugin.schema.json)
2. If present, check `mcp.json` against [`mcp.schema.json`](https://agent-plugins.org/schemas/1.0.0/mcp.schema.json)
3. Verify `$schema` versions match between `plugin.json` and `mcp.json`
4. Validate plugin name: 1-64 chars, `[a-z0-9.-]`, starts/ends alphanumeric, no `--` or `..`
5. Verify all plugin-relative paths start with `./` and stay within plugin root
6. Check that `env` keys do not include `PLUGIN_ROOT` or `PLUGIN_DATA`

## Gotchas

- **`plugin.json` schema is closed** — only `$schema`, `name`, `version`, `description`, `author`, `homepage`, `repository`, `license`, `keywords`, and `extensions` are permitted. Unknown top-level fields are reported and ignored (non-fatal), but any other schema violation is fatal.
- **`$schema` must match between manifests** — if `mcp.json` is present, its `$schema` version must match `plugin.json`'s version. A mismatch invalidates MCP configuration but does not affect skills.
- **Components use fixed locations only** — `plugin.json` cannot override where skills or MCP config are discovered. Skills live in `skills/`, MCP in `mcp.json`. No inline component config in the manifest.
- **Skills discovery is non-recursive** — only immediate subdirectories of `skills/` containing `SKILL.md` are discovered. Nested skill directories are ignored.
- **`command` is a single token** — not a shell command string. Use bare executable name or `./` plugin-relative path. Clients MUST NOT perform placeholder expansion in `command`.
- **`cwd` has strict forms** — must be `./...`, `${PLUGIN_ROOT}...`, or `${PLUGIN_DATA}...`. Bare paths like `"data"` are invalid.
- **`PLUGIN_ROOT`/`PLUGIN_DATA` are reserved** — clients supply these; plugins must not set them in `env`. Doing so invalidates the server entry.
- **Placeholder expansion is single-pass** — `${PLUGIN_ROOT}` and `${PLUGIN_DATA}` are replaced once. Text introduced by replacement is not rescanned for further placeholders.
- **Expansion applies only to `args`, `env` values, and `cwd`** — not to `command`, `env` keys, `url`, or header names/values.
- **HTTP-only for loopback** — remote MCP servers using `streamable-http` or `sse` must use HTTPS unless the host is `localhost` or a loopback IP literal.
- **Headers are not secrets** — do not embed credentials in `headers` or `env`. Authorization is client-managed.
- **Component failures are non-fatal** — skip invalid skills or MCP servers, continue loading the rest. The plugin should not become entirely unusable because one component is broken.
- **`extensions` must be an object** — if `extensions` is not an object, report and ignore it. Non-object extensions do not invalidate the plugin.
- **Symlinks must stay within plugin root** — clients reject any path that resolves outside the filesystem-resolved plugin root.
- **`author` is strictly typed** — only `name`, `email`, `url` as strings. Any other field or value type makes the manifest invalid.
- **`sse` is legacy** — `sse` selects the deprecated HTTP+SSE transport from MCP 2024-11-05. It does not refer to SSE within Streamable HTTP. Prefer `streamable-http`.
- **Client may support just one transport** — a conformant MCP client need only support `stdio` or `streamable-http`, not both. `sse` is optional.

## References

- [01-plugin-package-model](references/01-plugin-package-model.md) — Directory layout, containment rules, path safety
- [02-manifest](references/02-manifest.md) — plugin.json fields, validation, name constraints, schema details
- [03-component-discovery](references/03-component-discovery.md) — Fixed locations, missing-location behavior, non-recursive scanning
- [04-skills](references/04-skills.md) — Agent Skills within plugins, discovery rules, format delegation
- [05-mcp-servers](references/05-mcp-servers.md) — MCP transports (stdio, streamable-http, sse), configuration variants
- [06-mcp-loading-rules](references/06-mcp-loading-rules.md) — Loading, validation, failure isolation for MCP servers
- [07-client-extensions](references/07-client-extensions.md) — Reverse-domain namespaces, manifest and directory extensions
- [08-environment-and-expansion](references/08-environment-and-expansion.md) — PLUGIN_ROOT, PLUGIN_DATA, placeholder expansion rules
- [09-versioning](references/09-versioning.md) — Spec versioning, plugin semver, schema version matching
- [10-client-conformance](references/10-client-conformance.md) — Minimum client requirements, incremental adoption, failure handling
- [11-conformance-checklist](references/11-conformance-checklist.md) — Full conformance checklist for plugin loaders and clients
- [12-design-decisions](references/12-design-decisions.md) — Rationale behind key design choices
- [13-future-considerations](references/13-future-considerations.md) — Permissions, provenance, secrets, enterprise controls, dependencies
