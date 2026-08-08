# Versioning

## Specification and schema versions

The version number identifies the complete Agent Plugins specification release, including:
- Normative text
- Plugin manifest schema (`plugin.schema.json`)
- MCP configuration schema (`mcp.schema.json`)

Every spec release publishes both schemas with the same version, even when a schema's validation rules are unchanged.

### Schema version matching

- `plugin.json` `$schema` declares the Agent Plugins version the package targets
- `mcp.json` `$schema` MUST match the version declared by `plugin.json`
- A version mismatch makes the MCP configuration invalid but does not invalidate other component types

### Canonical schema identifiers

- `https://agent-plugins.org/schemas/1.0.0/plugin.schema.json`
- `https://agent-plugins.org/schemas/1.0.0/mcp.schema.json`

Published canonical identifiers MUST NOT be reassigned to different schema contents. Existing plugins MAY continue targeting older versions; clients determine support using declared identifiers and explicit compatibility mappings.

## Plugin versions

Plugins SHOULD use Semantic Versioning for `version`:

| Segment | Meaning |
|---|---|
| Major | Breaking change — incompatible behavior or schema change |
| Minor | Backward-compatible feature — new behavior without breaking clients |
| Patch | Backward-compatible fix — corrective change without behavioral break |

Clients MAY use `version` for update checks and cache freshness. Clients MUST NOT reject a manifest solely because `version` is not valid Semantic Versioning.

## Key points

- One version number covers the entire spec (text + both schemas)
- `plugin.json` and `mcp.json` must declare the same spec version
- Plugin `version` is independent of spec version — it tracks the plugin itself
- Changing either schema requires a new spec release
