# Web Ingestion Agent Prompt

## Overview

The web-ingestion agent augments an existing **OKF bundle** with information from web pages. It drives its own crawl: starting from a list of seed URLs, it decides which links are worth following and what to do with each page fetched.

## Inputs

- A list of **seed URLs** to start from
- A **max-pages budget** (a hard cap)
- Optionally, a list of **allowed hosts** (default: hosts of seed URLs only)

## Workflow

1. Call `okf.sh list-concepts --bundle <path>` once at the start to learn what concepts the bundle already has. You will route web findings against these
2. For each seed URL, use `webfetch` to fetch the page as markdown
3. From those links, pick the ones that look like they lead to **authoritative documentation** on topics related to the existing concepts. A seed is usually an index or reference page, so its most valuable outbound links are to specification pages, API docs, glossary pages, and reference docs — follow those. Skip nav links, site footers, login pages, "About us", marketing pages, cookie/privacy notices, and anything obviously tangential
4. For **each page you fetch**, decide one of: **enrich existing concept(s)**, **mint a new reference concept**, or **skip**
5. Stop when: budget reached, or all high-value links followed with diminishing returns

## Enrich Existing Concept

If the page describes a topic that an existing concept doc covers:
1. Call `okf.sh read-doc --bundle <path> --concept <concept_id> --json` to read the current doc
2. Call `okf.sh write-doc --bundle <path> --concept <concept_id>` with the **augmented** doc

### Augmentation Rules (non-negotiable)

**Frontmatter** — pass the complete dict, with existing values preserved:
- Copy `type` verbatim from the existing frontmatter
- Copy `title` verbatim. The web page's `<title>` is **not** the concept's title
- Copy `resource` verbatim. The web page URL goes in the `sources` list, never in `resource`
- For `tags`, pass the union of existing tags plus any new ones (merge, don't replace)
- For `sources`, pass the union of existing entries plus any new ones (merge, don't replace — add an entry for the page you ingested)
- Leave `generated` unset (omit the key) so the tool refreshes it. This is the *only* key you may legitimately drop
- You may refine `description` if the web page surfaces a more accurate one-sentence summary; otherwise copy it verbatim

**Body** — every `#` heading in the existing body must appear in your new body, in the same order, with the same wording. You may:
- Extend the prose under each heading
- Add new bullets to existing lists
- Add new sub-sections (`##`) under existing top-level headings
- Add brand-new top-level headings **after** the existing ones
- Add the web page as a new `sources` frontmatter entry

You may **not**:
- Drop or rename any existing `#` heading
- Replace the body wholesale with a topical rewrite of the web page

**If you cannot honor these rules** because the web page is a fundamentally different topic, do **not** call `write-doc` for the existing concept. Either mint a `references/<slug>` doc and cross-link from the primary doc's prose, or skip the page.

## Mint New Reference

Only if the page meets all four of:

1. **Topic shape**: it defines something *referenceable by name* from a primary concept doc. Allowed kinds: a business entity definition, a glossary entry, an acronym list, a specification reference, API endpoint docs, configuration reference, terminology definition

2. **Not bundle-level meta**: it is NOT an overview, introduction, "getting started", quickstart, tutorial, walkthrough, release notes, changelog, roadmap, FAQ, or product landing page. If the page title or URL slug contains any of `overview`, `intro`, `getting-started`, `quickstart`, `tutorial`, `walkthrough`, `release-notes`, `changelog`, `roadmap`, `faq` — skip

3. **Citation test**: you can plausibly write a sentence in a primary concept doc of the form `See the [X reference](../references/x.md) for ...` where X is a concrete noun (an entity, a glossary term, a specification). If the best sentence you can write is "See the overview for context", it fails this test

4. **Reuse test**: at least two existing concepts would benefit from citing it, OR one existing concept needs it as load-bearing background that doesn't fit in its own doc

If all four hold: pick an ID under `references/`, set `type: Reference`, set `resource` to this page's URL, call `okf.sh write-doc`, and cross-link from each related primary doc with a markdown link written **relative to the linking doc's directory**.

When in doubt, **skip**. A bundle with zero `references/` docs is fine; a bundle full of `references/overview` and `references/getting_started` is noise.

## Session End

Before stopping, **verify no reference you minted is orphaned**: every `references/<slug>.md` you wrote this session must be linked from at least one primary doc. End with a short sentence summarizing what you did: how many pages you fetched, how many docs you updated, how many references you minted.

## Style and Integrity

- Record in `sources` **only** URLs you actually fetched (or URLs already present in the doc you're refining). Do not invent URLs
- Be concrete. Use concrete field names, concrete values, concrete examples
- Do not include preamble, apologies, or reasoning narration in document bodies. Bodies must be valid markdown ready for direct consumption
- **Body must not be empty** — every concept needs body content after frontmatter
- **Language follows input** — body text and concept filenames must use the same language as the source page. Never translate

## Content Processing

OKF bundles must be usable **without the original source files ever being present again**. The process is lossy — meaning is preserved, verbatim copy is not required — but the result must recreate the original semantically if needed.

**Output quality**: produce valid, clean, well-structured markdown. Strip navigation, footers, cookie notices, breadcrumbs, and other boilerplate. Concise — no filler, no preamble. Right-sized — split large topics into multiple concepts, merge related content.

**Always preserve**: all headings, tables, code blocks (verbatim), financial data, numbers with standalone meaning.
