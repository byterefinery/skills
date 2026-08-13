# Plugin Package Model

## Directory structure

A plugin is a directory rooted at a single filesystem location. Standard layout:

```text
my-plugin/
├── plugin.json              # Required manifest
├── skills/                  # Agent Skills (optional)
│   └── summarize/
│       ├── SKILL.md
│       ├── scripts/
│       │   └── analyze.sh
│       └── references/
│           └── checklist.md
├── mcp.json                 # MCP servers (optional)
├── com.example.client/      # Client extension (optional)
│   └── hooks/
├── LICENSE
└── CHANGELOG.md
```

## General requirements

1. A plugin MUST include `plugin.json` at the root.
2. All filesystem-resolved paths MUST remain within the plugin root. Symlinks, junctions, and reparse points may resolve to targets within the root, but clients MUST reject paths resolving outside it.
3. Plugin-relative paths MUST begin with `./`, resolve against the plugin root, and stay within the root after resolution.
4. Non-path configuration values (command arguments, env variable values) are opaque strings — clients MUST NOT interpret them as package paths.

## Path containment examples

Valid:

```json
{
  "mcpServers": {
    "server": {
      "type": "stdio",
      "command": "./bin/server",
      "cwd": "./data"
    }
  }
}
```

Invalid — `../` escapes the root, `data` lacks `./` prefix:

```json
{
  "mcpServers": {
    "server": {
      "type": "stdio",
      "command": "../bin/server",
      "cwd": "data"
    }
  }
}
```

## Failure boundaries for containment violations

When a path fails containment, apply the narrowest applicable failure:

| Violation | Action |
|---|---|
| `plugin.json` outside root | Reject the entire plugin |
| Fixed component location outside root | Treat that component type as invalid |
| Discovered `SKILL.md` outside root | Skip that skill |
| MCP server `command`/`cwd` fails containment | Treat that server entry as invalid |
| Any other path outside root | Deny access to that path |

These rules govern access to plugin-supplied files. They do not sandbox a plugin subprocess or restrict paths supplied at runtime.
