# AI agent workflows in Next.js 16

How Next.js 16 is designed for coding agents: version-matched docs, runtime visibility, error-driven fixes, and the official skills.

## Contents

- [AGENTS.md and the managed block](#agentsmd-and-the-managed-block)
- [Bundled docs](#bundled-docs)
- [Runtime visibility](#runtime-visibility)
- [Error-driven fixes](#error-driven-fixes)
- [Official Next.js skills](#official-nextjs-skills)
- [Agent upgrade prompt](#agent-upgrade-prompt)

## AGENTS.md and the managed block

`create-next-app` generates `AGENTS.md` (and `CLAUDE.md` referencing it) by default; pass `--no-agents-md` to skip. On 16.3+, `next dev` also **auto-generates** these files when an agent is detected in the environment, and **upserts** the managed block in existing files — content outside the markers is preserved.

The managed block:

```md
<!-- BEGIN:nextjs-agent-rules -->

# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` (resolved from this file's directory; in monorepos the `next` package may not be visible from the repo root) before writing any code. Heed deprecation notices.

This block is written and re-added by `next dev` — verify at `node_modules/next/dist/server/lib/generate-agent-files.js`. Removing it from a diff only re-creates the uncommitted change; committing it with your work keeps the tree clean.

<!-- END:nextjs-agent-rules -->
```

Practical rules for agents:

- Read `AGENTS.md` first in any Next.js project; it encodes where the version-matched docs live.
- Commit the managed block with your work — deleting it in a diff just recreates the uncommitted change.
- Add project-specific instructions **outside** the markers so upserts preserve them.
- Opt out with `agentRules: false` in next.config (the default — generation on — is recommended).

## Bundled docs

Since 16.2, the docs ship inside the package:

```
node_modules/next/dist/docs/
├── 01-app/          # getting-started, guides, api-reference
├── 02-pages/
├── 03-architecture/
└── index.mdx
```

- Mirrors nextjs.org/docs structure with numbered directories for ordering. Resolve a page by slug: `find node_modules/next/dist/docs -name '<slug>.md'`.
- In monorepos the `next` package may not be visible from the repo root — resolve from the package's location (the managed block says to).
- The per-error pages under `/docs/messages` are **not** bundled.
- Network fallback: append `.md` to any nextjs.org/docs URL for plain markdown (`Accept: text/markdown` works too); `https://nextjs.org/docs/llms.txt` and `llms-full.txt` follow the llms.txt convention.
- Upgrading Next.js upgrades the bundled docs automatically.
- Pre-16.2: `npx @next/codemod@canary agents-md` downloads a version-matched copy to `.next-docs/` and indexes it in AGENTS.md.

## Runtime visibility

`next dev` exposes two views an agent can read from the terminal:

1. **Framework view** — the MCP server at `/_next/mcp` on the running dev server: routes, server logs, and compilation issues. Tools include `get_compilation_issues`, `compile_route`, and `get_errors` (the instant-navigation insights land here). An agent can check whether code compiles without running a full `next build`.
2. **Browser view** — `agent-browser` (vercel-labs CLI) exposes DOM, console, network, and Web Vitals as structured text; with `--enable react-devtools` it reports the component tree and pending Suspense boundaries.

Supporting behaviors:

- `logging.browserToTerminal` (default on in 16) forwards browser console errors/warnings to the terminal.
- `next dev` writes PID, port, and URL to `.next/dev/lock`; a second `next dev` in the same project prints the running server's URL and the PID to kill — connect to the existing server instead of starting a duplicate.
- The official loop: edit → verify via MCP + browser → repeat. That is what the `next-dev-loop` skill packages.

## Error-driven fixes

Blocking errors and insights come with **labeled fixes**, each a different trade-off. Example:

```
Route "/products/[slug]": Next.js encountered uncached data during prerendering.

Ways to fix this:
  - [stream] Provide a placeholder with `<Suspense fallback={...}>` around the data access
  - [cache] Cache the data access with `"use cache"` (does not apply to `connection()`)
  - [block] Set `export const instant = false` to allow a blocking route

Learn more: https://nextjs.org/docs/messages/blocking-prerender-dynamic
```

- The dev overlay renders these as clickable fix cards with a **Copy prompt** button that packages the chosen fix into a paste-ready agent prompt.
- The same menu prints in the `next dev` terminal and in `next build` output, so CI logs carry it too.
- Each `Learn more` link is an agent-readable page under `/docs/messages` with canonical patterns, trade-offs, and gotchas (fetchable as `.md` over the network).
- In dev, stack frames resolve to source; in production builds server code is minified — use `next build --debug-prerender` for readable prerender errors.
- The insight-only case (route still returns 200): read the dev overlay, the dev-server log, or MCP `get_errors`.

## Official Next.js skills

Installed with `npx skills add vercel/next.js --skill <name>` (source in the repo's `skills/` directory, listed on skills.sh/vercel/next.js):

| Skill | Use for |
| --- | --- |
| `next-dev-loop` | The runtime foundation: verify every edit against the running dev server (MCP + browser). Prompt: "After every edit, verify the page still works at runtime using the next-dev-loop Skill." |
| `next-cache-components-adoption` | Adopt Cache Components: flip the flag, opt out blocking routes, fix them one feature at a time with user checkpoints, confirm each against `next dev` and `next build`. |
| `next-cache-components-optimizer` | Drive a specific route to instant navigation: write a failing `@next/playwright` `instant()` e2e, refactor until green, ship the test as a regression guard. |
| `next-partial-prefetching-adoption` | Adopt Partial Prefetching (shared App Shell): audit `<Link prefetch>` calls, flip the flag, resolve insights. |

Guiding principle: **framework knowledge comes from the bundled docs, not from skills** — always-available version-matched context outperforms on-demand retrieval. Skills package *workflows* (sequenced, verifiable, with checkpoints), not API reference.

## Agent upgrade prompt

The version-16 upgrade guide ships a prompt for running the whole upgrade through an agent. In summary: ensure `AGENTS.md` points at version-matched docs (set up via the guide if missing), follow the upgrade guide as source of truth, use the codemod for the mechanical pass, keep the migration scoped and explain changes, then run the post-upgrade runtime verification (prefer `next-dev-loop` on 16.3+ with Turbopack) and re-run the AGENTS.md check. Ask the user before destructive changes or when the correct migration is ambiguous.
