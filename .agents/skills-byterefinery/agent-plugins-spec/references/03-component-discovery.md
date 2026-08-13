# Component Discovery

## Fixed locations

Clients MUST discover each supported component type from its fixed location. `plugin.json` cannot override these locations or contain inline component configuration.

| Component type | Fixed location | Pattern |
|---|---|---|
| Skills | `skills/` | Subdirectories containing `SKILL.md` |
| MCP servers | `mcp.json` | JSON configuration |

## Discovery rules

- **Skills**: scan `skills/` for immediate child directories. Each directory containing a path named exactly `SKILL.md` that resolves to a regular file is one skill. Do NOT recursively search deeper descendants.
- **MCP servers**: load `mcp.json` from the plugin root. It must be a JSON file.

## Missing locations

- If a fixed component location is absent, the client MUST NOT treat that as an error.
- If a fixed component location is present but does not resolve to the expected filesystem kind (e.g., `skills` is not a directory, `mcp.json` is not a regular file), the client MUST treat that component type as invalid and continue loading other types.

## Example

```text
reports-plugin/
├── plugin.json
├── skills/summarize/SKILL.md
└── mcp.json
```

The client discovers skill `summarize` from `skills/` and MCP servers from `mcp.json`. If `skills/` were absent, the client would still load MCP servers without error.
