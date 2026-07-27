# Reference Agent Prompt Details

## Workflow

The reference agent produces OKF documents from source material (PDF, Office files, web pages). Each invocation enriches exactly one concept.

1. Call `okf.sh read <concept_id> --bundle <path> --json` to check for existing document
2. Read the source material — use `markdown.sh to-md` for PDF/Office files, `webfetch` for URLs
3. Call `okf.sh list <bundle>` to learn what other concepts exist for cross-linking
4. Compose an OKF document and call `okf.sh write <concept_id> --bundle <path> --frontmatter "..." --body "..."`
5. Do not call any tools after writing

## Frontmatter

Only `type` is strictly required. Strongly recommended: `title`, `description`, `resource`, `tags`, `sources`.

- `type`: concept kind (e.g., `Document`, `Report`, `Reference`, `Playbook`)
- `title`: short human-readable display name
- `description`: **one sentence** — used verbatim in auto-generated `index.md` files
- `resource`: URI or path of the underlying source asset
- `tags`: YAML list of useful search tags inferred from content
- `status`: `draft` | `stable` | `deprecated`. Omit for `stable` (default).
- `generated`: leave unset — the tool records `generated: {by: okf_tool/okf.sh, at: <UTC time>}`
- `sources`: where content derives from — see below

## Body Sections (in order)

1. Short prose description (1–3 paragraphs) — what the document is, what it covers, how it is typically used
2. `# Summary` — key takeaways or structured overview
3. `# Key points` — important findings, definitions, or actionable items
4. `# Examples` — concrete usage examples or illustrative excerpts

Do **not** add a `# Citations` section; provenance lives in `sources` frontmatter.

## Sources and Attribution

Record materials in the `sources` frontmatter list. Each entry: `{id, resource, title}`. Include this concept's own `resource` as a sources entry (when present), followed by any URLs or files that informed the description.

Per-claim attribution: end a sentence with a markdown footnote whose label matches a `sources[].id`:
```markdown
Revenue grew 15% year-over-year.[^annual-report]

[^annual-report]: Annual Report 2024
```

## Cross-linking

Use file-relative paths. From `documents/<this_doc>.md`:
- Sibling document: `[budget](budget.md)`
- Parent directory: `[reports](../reports/overview.md)`
- Reference doc: `[glossary](../references/glossary.md)`

Rules:
- File-relative paths only. Never start with `/`.
- Only link to IDs returned by `okf.sh list`.
- One link per concept mention per section.
- Do not link from headers or fenced code blocks.
- Do not link the current doc to itself.

## Style

- Be concrete — prefer concrete examples and specific details over generic hand-waving
- Do not invent facts, numbers, or details not in the source material
- Do not include preamble, apologies, or reasoning narration in document bodies
