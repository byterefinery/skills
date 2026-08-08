# Conformance Checklist

*Non-normative — for convenience only. When this conflicts with the spec text, the spec governs.*

## Plugin loader

- [ ] Parse and validate `plugin.json` (§5.1, §5.2)
- [ ] Validate required `$schema` and `name` fields (§5.3)
- [ ] Validate plugin name against naming constraints (§5.5)
- [ ] Report and ignore unknown `plugin.json` fields (§5.2)
- [ ] Ignore unimplemented namespaces in `extensions` without validating values (§8.1)
- [ ] Reject package paths resolving outside plugin root (§4.1)
- [ ] Discover implemented file-based extensions from top-level namespace directories (§8.2)

## Component discovery

- [ ] Scan fixed location for each supported component type (§6.1)
- [ ] Ignore missing fixed locations without error (§6.2)

## MCP configuration

- [ ] Select supported `$schema`, validate closed `mcp.json` schema and each server variant (§7.2.1)
- [ ] If supporting MCP, implement at least one of stdio or Streamable HTTP (§7.2.1)
- [ ] Use each server entry's declared transport for initial connection (§7.2.1)
- [ ] Enforce remote URL and literal-header requirements (§7.2.1)

## Environment and expansion

- [ ] Provide `PLUGIN_ROOT` and dedicated writable `PLUGIN_DATA` (§9.1)
- [ ] Resolve `command` as single bare or plugin-relative executable token (§7.2.1)
- [ ] Use plugin root as default MCP server working directory (§7.2.1)
- [ ] Validate explicit `cwd` forms and post-resolution containment (§7.2.1)
- [ ] Overlay configured `env` entries on client-selected base environment (§9.1)
- [ ] Set client-provided `PLUGIN_ROOT` and `PLUGIN_DATA` after applying configured `env` (§9.1)
- [ ] Do not require configured `PATH` to affect bare-command resolution (§7.2.1)
- [ ] Expand only `${PLUGIN_ROOT}` and `${PLUGIN_DATA}` in `args`, `env`, `cwd` (§9.2)

## Resilience

- [ ] Ignore unsupported component types (§11.3)
- [ ] Skip servers with unsupported transport without affecting others (§7.2.2)
- [ ] Continue loading when independent component fails (§11.3)
- [ ] Support at least one component type (§11.1)
