# Frontmatter Field Reference

Complete reference for OKF v0.2 frontmatter fields.

## Core Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `type` | string | **Yes** | Kind of concept. Not registered centrally. Examples: `Concept`, `Reference`, `Metric`, `Playbook`, `Policy`, `Attested Computation`, `Skill`, `Table`, `Dataset`, `API Endpoint`, `Document`. |
| `title` | string | No | Human-readable display name. Used in `index.md`, search snippets, previews. |
| `description` | string | No | One sentence summarizing the concept. |
| `resource` | URI/path | No | Canonical URI or path identifying the underlying asset. Absent for abstract concepts. |
| `tags` | [string] | No | Short strings for cross-cutting categorization. |

## Provenance: `sources` and `usage_window`

`sources` records the materials a concept derives from.

### `sources` entry fields

| Field | Type | Required | Description |
|---|---|---|---|
| `resource` | URI/path/scope | **Yes** | Concrete artifact (URL, bundle-relative path) or scope descriptor. |
| `id` | string | No | Stable key for per-claim footnote attribution. Use when body cites the source. |
| `title` | string | No | Human-readable label. |
| `author` | actor string | No | Who produced the source. Authority signal. |
| `usage_count` | number | No | How often resource was exercised over `usage_window`. Liveness signal. |
| `last_modified` | YYYY-MM-DD | No | When the source itself last changed. Recency signal. |

### `usage_window`

Sibling of `sources`. Frames every `usage_count` with a date range.

```yaml
usage_window: { from: 2026-06-01, to: 2026-06-30 }
```

A single `sources` entry may carry its own `usage_window` to override.

### Per-claim attribution

End a sentence with a markdown footnote whose label matches a `sources[].id`:

```markdown
Revenue recognized per the finance policy.[^rev-policy]

[^rev-policy]: Revenue recognition policy
```

The footnote label is the join key into `sources`.

## Trust: `generated` and `verified`

`generated` records how content was produced. `verified` records who confirmed it.

### `generated`

| Field | Type | Required | Description |
|---|---|---|---|
| `by` | actor string | **Yes** | Actor that produced the content. |
| `at` | ISO 8601 | No | Datetime of last meaningful change. |

```yaml
generated: { by: okf_agent/claude-sonnet-4-5, at: 2025-07-15T14:30:00Z }
```

### `verified`

List of verification events, or a single bare mapping.

| Field | Type | Required | Description |
|---|---|---|---|
| `by` | actor string | **Yes** | Actor that verified. |
| `at` | ISO 8601 | **Yes** | Datetime of verification. |

```yaml
verified:
  - { by: human:alice, at: 2025-07-16T09:00:00Z }
  - { by: process:nightly-check, at: 2025-07-17T02:00:00Z }
```

Single verifier (bare mapping):

```yaml
verified: { by: human:alice, at: 2025-07-16T09:00:00Z }
```

### Trust tiers

Derived from `verified`:

- No `verified` key → **unverified**
- Only non-`human:` actors → **machine-confirmed**
- Any `human:<id>` actor → **human-reviewed**

### Actor convention

- `<producer>/<version>` — agents/tools, e.g. `okf_agent/claude-sonnet-4-5`
- `human:<id>` — people, e.g. `human:alice`
- `process:<id>` — automated processes, e.g. `process:nightly-check`

## Lifecycle: `status` and `stale_after`

| Field | Type | Values | Default |
|---|---|---|---|
| `status` | string | `draft`, `stable`, `deprecated` | `stable` |
| `stale_after` | YYYY-MM-DD | Absolute date | never stale |

- `draft` — not yet reviewed; possibly incomplete.
- `stable` — ready for consumption.
- `deprecated` — kept for links and history; no longer current.

`stale_after` is an absolute date. A concept is stale when `today >= stale_after`.

## Coverage (known extension)

`coverage` tracks which source regions a concept covers. Enables verification that no content was missed during extraction.

```yaml
coverage:
  - source: annual-report.pdf
    region: { pages: [12-15] }
  - source: annual-report.pdf
    region: { pages: [22-23] }
```

Each entry:
- `source`: required, filename or URI
- `region`: required, mapping with `pages` (list), `slides` (list), `sheet`+`range` (Excel), or `section` (web/markdown)

Region formats:
- PDF/Word: `{ pages: [12, 13, 15-18] }`
- PowerPoint: `{ slides: [7-12] }`
- Excel: `{ sheet: "Revenue", range: "A1:D50" }`
- Web/Markdown: `{ section: "## Authentication" }`

Check coverage with `okf.py check-coverage --bundle ./bundle`.

## Extensions

Producers may include any additional keys. Consumers must not reject documents with unrecognized fields and should preserve unknown keys when round-tripping.

Example extension from reference bundles — `not` for negative definitions:

```yaml
not:
  - term: "revenue minus product cost only"
    why: "that is the pre-FY2026 definition"
    instead: "revenue minus full COGS"
```
