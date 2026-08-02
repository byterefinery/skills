# Bundle Structure

## Directory Layout

```
path/to/bundle/
  index.md                      # Optional. Directory listing.
  log.md                        # Optional. Update history (always English).
  <concept>.md                  # A concept at the bundle root.
  <subdirectory>/
    index.md
    <concept>.md
    references/
      <reference>.md
```

## Reserved Filenames

| Filename | Purpose |
|---|---|
| `index.md` | Directory listing. No frontmatter (except bundle root may carry `okf_version: "0.2"`). |
| `log.md` | Update history. Always written in English. |

## `index.md`

Enumerates directory contents. No frontmatter (except bundle root may carry `okf_version`). Body uses sections with bulleted lists:

```markdown
# Documents

* [Annual Report 2024](annual-report-2024.md) — Financial and operational summary for FY2024.
* [Revenue computation](references/metrics/revenue.md) — Sanctioned revenue calculation.
```

## `log.md`

Date-grouped change entries, newest first. Always English.

```markdown
# Directory Update Log

## 2025-07-15
* **Creation**: Established bundle from annual-report-2024.pdf.
```

## Cross-linking

Concepts link to each other using standard markdown links. Two forms:

- **Absolute (bundle-relative):** begins with `/`, interpreted relative to bundle root. **Recommended** — stable when documents are moved within their subdirectory.

  ```markdown
  See the [customers table](/tables/customers.md) for the join key.
  ```

- **Relative:** standard markdown relative path.

  ```markdown
  See the [neighboring concept](./other.md).
  ```

Consumers must tolerate broken links.

## Path-valued fields

`resource`, `sources[].resource`, `computation`, `executor.resource`, `attester.resource` accept:

- An absolute URL (e.g. `https://...`)
- A bundle-relative path beginning with `/`
- A relative path (e.g. `../computations/revenue.md`)

## `references/` Convention

A `references/` subdirectory conventionally mirrors external material, run instructions, or code as first-class concepts within the bundle. Sources, executors, and attesters commonly point into it. It is a naming convention, not a requirement.

## Body Conventions

No required body sections. Conventional headings:

| Heading | Purpose |
|---|---|
| `# Schema` | Structured description of fields, columns, or properties. |
| `# Examples` | Concrete usage examples, often as fenced code blocks. |
| `# Computation` | The sanctioned computation of an Attested Computation. |
| `# Metrics` | Metrics derived from this concept. |
| `# Joins` | Relationships to other concepts. |
| `# Dimensions` | Groupable or filterable attributes. |

Do not add a `# Citations` section; provenance lives in `sources` frontmatter with per-claim footnotes.
