# Conformance

## OKF v0.2 Conformance Rules

A bundle is **conformant** with OKF v0.2 if:

1. Every non-reserved `.md` file contains a parseable YAML frontmatter block.
2. Every frontmatter block contains a non-empty `type` field.
3. Reserved filenames (`index.md`, `log.md`) follow their defined structure when present.

## Consumer Requirements

Consumers **MUST NOT** reject a bundle because of:

- Missing optional frontmatter fields
- Unknown `type` values
- Unknown additional frontmatter keys
- Broken cross-links
- Missing `index.md` files

Consumers **MUST**:

- Treat a bare `verified` mapping as a one-element list
- Derive trust tiers and staleness only from the specified fields
- Surface, not silently drop, a failing attestation

## Versioning

Bundles declare version with `okf_version: "0.2"` in bundle-root `index.md` frontmatter (the only place frontmatter is permitted in `index.md`).

- **Minor** version bump: backward-compatible additions (new optional fields, new conventional headings)
- **Major** version bump: may make breaking changes

Consumers that do not understand the declared version should attempt best-effort consumption.

## Changes from v0.1

### Breaking

- `timestamp` superseded by `generated.at`. Consumers may fall back to legacy `timestamp` when `generated` is absent.
- Body `# Citations` list superseded by `sources` in frontmatter. Consumers may still parse legacy `# Citations` for v0.1 documents.

### Additive

- `sources` with per-source credibility signals (`author`, `usage_count`, `last_modified`) and `usage_window`
- `generated`, `verified`
- `status`, `stale_after`
- `Attested Computation` type and its computation keys (`runtime`, `parameters`, `computation`, `executor`, `attester`)
- `# Computation` conventional body heading
- Actor convention for `generated.by` and `verified[].by`
