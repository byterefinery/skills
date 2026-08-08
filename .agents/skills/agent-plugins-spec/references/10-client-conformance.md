# Client Conformance

## Minimum requirements

A conformant client MUST satisfy all applicable requirements. At minimum:

1. **Load from directory** — can load a plugin from a directory path
2. **Manifest validation** — select schema from `$schema`, parse and validate closed `plugin.json` schema with non-fatal exceptions (§5.2, §8.1)
3. **Ignore unknown extensions** — ignore unimplemented `extensions` namespaces without validating their values
4. **Discover components** — for each supported component type, discover from its fixed location
5. **MCP support** (if applicable) — select MCP schema from `$schema`, support at least one of `stdio` or `streamable-http`
6. **Environment** (if launching subprocesses) — provide `PLUGIN_ROOT` and `PLUGIN_DATA`, expand both in `args`, `env`, `cwd`
7. **Command resolution** — resolve `command` as a single executable token, use plugin root as default working directory
8. **At least one component type** — support skills or MCP servers (or both)

## Incremental adoption

A client is not required to support every component type. A skills-only client conforms without MCP support, provided it satisfies all applicable requirements.

## Unsupported components and failures

1. Clients MUST ignore unsupported component types
2. Unknown top-level fields or non-object `extensions` are non-fatal (§5.2, §8.1). Any other `plugin.json` schema violation is fatal — reject the plugin entirely
3. Component-level failures MUST NOT prevent loading of independent valid components. Apply the failure behavior defined for that component (§6, §7)
4. Clients SHOULD report invalid configuration and component failures
5. Clients MAY report partially unsupported plugins, but lack of support is not itself an error

## Conformance checklist summary

- [ ] Parse and validate `plugin.json`
- [ ] Validate required `$schema` and `name`
- [ ] Validate name against naming constraints
- [ ] Report and ignore unknown `plugin.json` fields
- [ ] Ignore unimplemented `extensions` namespaces
- [ ] Reject paths resolving outside plugin root
- [ ] Discover implemented file-based extensions
- [ ] Scan fixed locations for supported component types
- [ ] Ignore missing fixed locations without error
- [ ] Validate `mcp.json` schema and server variants (if supporting MCP)
- [ ] Implement at least one MCP transport (if supporting MCP)
- [ ] Provide `PLUGIN_ROOT` and `PLUGIN_DATA` (if launching subprocesses)
- [ ] Resolve `command` as single executable token
- [ ] Use plugin root as default working directory
- [ ] Validate `cwd` forms and containment
- [ ] Overlay configured `env` on base environment
- [ ] Set `PLUGIN_ROOT`/`PLUGIN_DATA` after applying configured `env`
- [ ] Expand only `${PLUGIN_ROOT}` and `${PLUGIN_DATA}` in `args`, `env`, `cwd`
- [ ] Ignore unsupported component types
- [ ] Skip unsupported server entries without affecting others
- [ ] Continue loading when independent components fail
- [ ] Support at least one component type
