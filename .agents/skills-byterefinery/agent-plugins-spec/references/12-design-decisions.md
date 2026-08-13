# Design Decisions

*Non-normative — for context only. Binding rules are in the normative spec sections.*

## Why directory-based discovery?

Plugins use filesystem directories as the package unit rather than archives (`.zip`, `.tar.gz`) or registry-fetched bundles. This keeps plugins inspectable with standard tools (`ls`, `cat`, `git`), editable in-place during development, and compatible with version control without special tooling. Fixed root-level locations (`skills/`, `mcp.json`) eliminate discovery indirection and manifest configuration that every client would otherwise need to implement.

## Why only Agent Skills and MCP in v1?

Agent Skills and MCP both have established specifications outside this project and meaningful cross-client adoption. Other proposed component types — commands, hooks, agents, rules, LSP servers — remain too client-specific for a stable portable contract and are outside v1 until their formats converge.

## Why root-level `plugin.json` is the conformance floor

Every conformant client MUST check `plugin.json` at the plugin root. This gives plugin authors a single guaranteed manifest that works across all clients without client-specific path knowledge.

## Why a closed portable manifest?

Restricting root `plugin.json` to known fields enables strict validation, typo detection, and schema-driven key completion. Client experiments cannot claim arbitrary top-level fields; they are contained under reverse-domain keys in `extensions`. Unknown top-level fields remain schema violations, but clients report and ignore them instead of rejecting an otherwise valid plugin.

## Why reverse-domain client extensions?

Reverse-domain identifiers provide a decentralized convention for avoiding collisions without requiring a central client-name registry. The same identifier can be used for manifest data and a client-specific directory. Extension directories remain top-level to keep plugin layouts flat and convention-driven.

## Why an explicit MCP configuration format?

Existing clients use incompatible MCP configuration shapes and infer transports differently. Agent Plugins defines an explicit closed union whose meaning is independent of any client-native format. Distinguishing Streamable HTTP from legacy HTTP+SSE gives each entry an unambiguous initial transport while leaving fallback behavior outside the portable format.

## Why may clients support only one standard MCP transport?

Stdio and Streamable HTTP serve different deployment and security models. Requiring both would expand a client's implementation and trust surface. Because each server entry declares its transport, a client can skip unsupported entries while loading independent servers and components.

## Why do schemas share the specification version?

`plugin.json` and `mcp.json` schemas use the Agent Plugins specification version rather than independent version sequences. This gives one portable format version to understand, prevents mixed-version packages, and lets `$schema` select the complete validation contract. Republishing an unchanged schema with a new spec release is small maintenance cost compared with exposing three independent compatibility timelines.

## Why plugin variables over relative paths in configs?

MCP server arguments often need absolute paths at runtime. `${PLUGIN_ROOT}` provides an unambiguous client-resolved anchor for bundled files, while `${PLUGIN_DATA}` identifies client-managed writable state that persists across updates. The `command` field does not use interpolation: `./` paths resolve directly against the plugin root, bare names use platform executable search. Treating `command` as one token avoids requiring clients to parse shell command strings.

## Why component failures are non-fatal

A plugin providing skills and an MCP server should not become entirely unusable because one server is unavailable. The spec pairs non-fatal component failures with diagnostic requirements so failures are visible rather than silent.
