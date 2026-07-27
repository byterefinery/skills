# Web Ingestion Agent Prompt Details

## Inputs

- List of **seed URLs** to start from
- **max-pages budget** (hard cap)
- Optionally, list of **allowed hosts** (default: hosts of seed URLs only)

## Workflow

1. Call `okf.sh list <bundle>` to learn existing concepts
2. Use `webfetch` skill to fetch each seed URL as markdown
3. From fetched links, pick ones leading to **authoritative documentation** related to existing concepts. Follow reference pages, specification pages, API docs, glossary pages. Skip nav links, footers, login pages, marketing, cookie/privacy notices, tangential content.
4. For each fetched page, decide: **enrich existing concept(s)**, **mint new reference**, or **skip**
5. Stop when: budget reached, or all high-value links followed with diminishing returns

## Enrich Existing Concept

If the page describes a topic an existing concept covers:
1. Call `okf.sh read <concept_id> --bundle <path> --json` to read current doc
2. Call `okf.sh write <concept_id> --bundle <path>` with the **augmented** doc

### Augmentation Rules (non-negotiable)

**Frontmatter** — pass the complete dict with existing values preserved:
- Copy `type` verbatim
- Copy `title` verbatim (web page `<title>` is NOT the concept's title)
- Copy `resource` verbatim (web page URL goes in `sources`, never in `resource`)
- `tags`: union of existing + new (merge, don't replace)
- `sources`: union of existing + new (merge, don't replace — adding the fetched page)
- Leave `generated` unset (tool refreshes it) — the **only** key you may drop
- You may refine `description` if the page surfaces a more accurate one

**Body** — every `#` heading in the existing body must appear in the new body, same order, same wording:
- Extend prose under each heading
- Add new bullets to existing lists
- Add new sub-sections (`##`) under existing top-level headings
- Add brand-new top-level headings **after** the existing ones
- Do NOT drop or rename any existing `#` heading
- Do NOT replace the body wholesale

**If you cannot honor these rules** because the page is a fundamentally different topic, do NOT call `write` for the existing concept. Either mint a `references/<slug>` doc and cross-link, or skip.

## Mint New Reference

Only if the page meets all four gates:

1. **Topic shape**: defines something *referenceable by name* from a primary concept. Allowed: glossary entry, acronym list, specification reference, API endpoint docs, configuration reference, terminology definition.

2. **Not bundle-level meta**: NOT an overview, introduction, getting-started, quickstart, tutorial, walkthrough, release notes, changelog, roadmap, FAQ, or product landing page. If title/URL contains any of `overview`, `intro`, `getting-started`, `quickstart`, `tutorial`, `walkthrough`, `release-notes`, `changelog`, `roadmap`, `faq` — skip.

3. **Citation test**: you can plausibly write `See the [X reference](../references/x.md) for ...` where X is a concrete noun. If the best sentence is "See the overview for context", it fails.

4. **Reuse test**: at least two existing concepts would benefit from citing it, OR one existing concept needs it as load-bearing background.

When all four hold: pick an ID under `references/`, set `type: Reference`, set `resource` to the page URL, call `okf.sh write`, and cross-link from each related primary doc.

## Session End

Before stopping, verify no reference you minted is orphaned — every `references/` doc must be linked from at least one primary doc. End with a short sentence summarizing: pages fetched, docs updated, references minted.

## Style

- Record in `sources` **only** URLs you actually fetched (or already present)
- Be concrete — use specific details from the source material
- Do not include preamble, apologies, or reasoning narration in document bodies
