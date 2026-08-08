# Client Extensions

## Overview

Client-specific data belongs under reverse-domain namespaces. Two representations:

1. **Manifest data** — under `extensions` in `plugin.json`
2. **Directory files** — under a top-level directory named for the namespace

A client MAY use either or both.

## Namespace conventions

- Use reverse-domain notation (e.g., `com.example.client`)
- Base the namespace on a domain the client controls
- Keep the namespace stable

Agent Plugins assigns no portable discovery, validation, loading, or failure semantics to extension data or files. Each client defines its own namespace contents and behavior.

## Manifest extensions

The `extensions` field in `plugin.json` MUST be an object keyed by namespace, with object values:

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
  "name": "example-plugin",
  "extensions": {
    "com.example.client": {
      "setting": true
    },
    "org.other.tool": {
      "mode": "strict"
    }
  }
}
```

**Handling rules:**
- If `extensions` is not an object, report and ignore (non-fatal)
- Clients MUST ignore entries for namespaces they do not implement, without validating the contents of their values
- Validation and failure handling within an implemented namespace are defined by that client

## Extension directories

The extension directory for a namespace is the top-level directory named after it:

```text
my-plugin/
├── plugin.json
├── skills/
│   └── summarize/
│       └── SKILL.md
└── com.example.client/
    └── hooks/
        └── hooks.json
```

A client that implements file-based behavior for a namespace MUST look for it in the corresponding top-level directory.

## Key points

- Extensions keep client experiments out of the portable manifest
- Unknown namespaces are ignored without validation overhead
- Extension directories remain top-level — flat layout convention
- Either representation (manifest or directory) can exist independently
