# Future Considerations

*Non-normative — none of these items is required for conformance or committed for inclusion.*

## Permission and approval UX

v1.0.0 does not define a trust model, permission system, or sandboxing. A future version may address:

- Permission declarations in the manifest (filesystem, network, tool access)
- Client-enforced capability restrictions per plugin
- User consent flows for installation and capability grants
- Approval UX for MCP servers executing arbitrary commands or accessing external services
- Graduated trust levels (sandboxed, user-approved, organization-approved)

## Provenance verification

v1.0.0 does not specify how clients can verify plugin origin or integrity. A future version may define:

- Cryptographic signature verification for published plugins
- Attestation chains linking a published plugin to its source repository and build
- Client policies for requiring signatures from trusted publishers

## Secret and sensitive value handling

MCP servers often need credentials at runtime. v1.0.0 does not specify how sensitive values should be provided. A future version may define:

- A `secrets` manifest field or separate secrets configuration
- Client-mediated secret injection avoiding plaintext in config files
- Scoping rules preventing cross-plugin secret access
- Rotation and revocation semantics for plugin-held credentials

## Enterprise controls

Organizations deploying at scale need policy enforcement. A future version may define:

- Allowlist and blocklist policies for plugin installation
- Organization-scoped plugin registries with approval workflows
- Centralized configuration overrides taking precedence over user-level settings
- Compliance reporting for plugin installation and usage events

## Audit-trail standardization

v1.0.0 defines failure-reporting requirements but not event schemas. A future version may define:

- Standard event schema for install, enable, disable, update, uninstall actions
- Recommended fields: timestamp, actor, plugin name, version, action, outcome
- Integration points for forwarding to external logging or SIEM systems
- Retention and access policies for audit records

## Dependency resolution

Plugins currently cannot declare dependencies on other plugins. A future version may define:

- A `dependencies` manifest field with version constraints
- Resolution order and conflict handling for transitive dependencies
- Peer dependency semantics for shared components

## Plugin testing and validation

No test harness or validation tool is specified. A future version may define:

- A `test` manifest field or convention
- A standard plugin linter or validator command
- Conformance test suites for client implementations
