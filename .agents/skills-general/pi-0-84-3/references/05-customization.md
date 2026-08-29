# Customization — skills, prompt templates, themes, pi packages

## Skills

Skills follow the [Agent Skills standard](https://agentskills.io); pi validates leniently (most violations warn, skill still loads).

**Locations:**

| Scope | Paths |
|---|---|
| Global | `~/.pi/agent/skills/`, `~/.agents/skills/` |
| Project (after trust) | `.pi/skills/`, `.agents/skills/` in cwd and ancestors (up to git repo root, else filesystem root) |
| Packages | `skills/` dirs or `pi.skills` in `package.json` |
| Settings | `skills` array (files or dirs; e.g. point at `~/.claude/skills` to reuse Claude Code skills) |
| CLI | `--skill <path>` (repeatable, additive even with `--no-skills`) |

**Discovery rules:**
- In `~/.pi/agent/skills/` and `.pi/skills/`, direct root `.md` files count as individual skills when they have valid frontmatter with a non-empty `description`.
- In all locations, directories containing `SKILL.md` are discovered recursively.
- In `~/.agents/skills/` and project `.agents/skills/`, root `.md` files are ignored, but nested `.md` in grouping folders load when they declare skill frontmatter.
- Name collisions (same name from different locations) warn and keep the first found. Missing descriptions, malformed `SKILL.md`, or no description → warning, not loaded.
- Unlike the standard, pi allows a skill `name` to differ from its parent directory (suboptimal rule for shared skill dirs).

**Structure** (freeform beyond SKILL.md):

```
my-skill/
├── SKILL.md          # required: frontmatter + instructions
├── scripts/          # helper scripts
├── references/       # detailed docs loaded on demand
└── assets/
```

**Frontmatter:** `name` (required; 1-64 chars, lowercase a-z/0-9/hyphens, no leading/trailing/consecutive hyphens), `description` (required; max 1024 chars; determines when the agent loads the skill — be specific), optional `license`, `compatibility` (max 500), `metadata` (arbitrary mapping), `allowed-tools` (experimental), `disable-model-invocation` (`true` hides the skill from the system prompt; users must use `/skill:name`).

**How they work:** descriptions go into the system prompt as XML; the agent `read`s the full SKILL.md when a task matches (not guaranteed — force with `/skill:name` or prompting). Arguments after the command append `User: <args>` to the skill content. Skills register as `/skill:name` commands (toggle: `enableSkillCommands`).

## Prompt templates

Markdown snippets that expand into full prompts; filename (without `.md`) becomes the command: `review.md` → `/review`.

**Locations:** `~/.pi/agent/prompts/*.md`, `.pi/prompts/*.md` (after trust), package `prompts/`, settings `prompts` array, `--prompt-template <path>`. Discovery in `prompts/` is **non-recursive** — add subdirs explicitly. `--no-prompt-templates` disables discovery.

**Format:**

```markdown
---
description: Review staged git changes
argument-hint: "<files>"
---
Review the staged changes (`git diff --cached`). Focus on $1.
```

`description` optional (first non-empty line is used); `argument-hint` shows in autocomplete.

**Argument substitution:** `$1` `$2`... positional, `$@`/`$ARGUMENTS` all joined, `${1:-default}`, `${@:-default}`, `${@:N}` (from Nth, 1-indexed), `${@:N:L}` (L args from N).

```
/review                       # no args
/component Button "handler"   # $1=Button, $2=handler
```

## Themes

JSON color files; built-ins `dark` and `light` (first run auto-detects terminal background).

**Locations:** `~/.pi/agent/themes/*.json`, `.pi/themes/*.json` (after trust), package `themes/`, settings `themes` array, `--theme <path>`. Select via `/settings` or `theme` setting; `--use-theme name` for one run, `--use-theme light/dark` follows terminal appearance. **Hot reload:** editing the active custom theme file applies immediately.

**Format:** `{ "$schema": ".../theme-schema.json", "name": "my-theme", "vars": { "primary": "#00aaff" }, "colors": { ...all 51 required tokens... } }`.

- `name` required, unique, no `/`. `vars` define reusable colors referenced from `colors`.
- **All 51 required color tokens** must be defined (optional with fallbacks: `thinkingMax`→`thinkingXhigh`, `scrollbarThumb`/`searchMatchBg`→`selectedBg`, `searchMatchText`→`text`).
- Token groups: core UI (11: `accent`, `border`, `borderAccent`, `borderMuted`, `success`, `error`, `warning`, `muted`, `dim`, `text` (usually `""`), `thinkingText`), backgrounds (14: `selectedBg`, `userMessageBg/Text`, `customMessageBg/Text/Label`, `toolPendingBg`, `toolSuccessBg`, `toolErrorBg`, `toolTitle`, `toolOutput`, ...), markdown (10: `mdHeading`, `mdLink`, `mdCode`, `mdCodeBlock(Border)`, `mdQuote(Border)`, `mdHr`, `mdListBullet`, `mdLinkUrl`), tool diffs (3: `toolDiffAdded/Removed/Context`), syntax (9: `syntaxComment/Keyword/Function/Variable/String/Number/Type/Operator/Punctuation`), thinking borders (6: `thinkingOff/Minimal/Low/Medium/High/Xhigh`), `bashMode`.
- Color values: `#rrggbb`, 256-color index (0-255), `vars` reference, or `""` (terminal default).
- Optional `export` section for `/export` HTML colors.
- Start from the built-in `dark.json`/`light.json` in the repo.

## Pi packages

Bundle extensions, skills, prompts, themes; share via npm or git.

> **Security:** packages run with full system access. Review source before installing.

**Install and manage:**

```bash
pi install npm:@foo/bar@1.0.0     # versioned specs are pinned
pi install git:github.com/user/repo@v1   # tag or commit; ssh:// and git@host:path work
pi install https://github.com/user/repo  # raw URLs
pi install ./local/path            # files/dirs added to settings without copying
pi install <source> -l             # project-local (.pi/settings.json, .pi/npm/ or .pi/git/)
pi -e npm:@foo/bar                 # temp install for this run only
pi remove|uninstall <source> [-l]
pi list
pi update [--all|--extensions|--models|--self [--force]] [source]
pi config [-l]                     # interactive enable/disable; Tab switches global/project
```

Defaults: user installs under `~/.pi/agent/npm/` or `~/.pi/agent/git/<host>/<path>`; project installs under `.pi/...`. Git `@ref` values are pinned; updates reconcile the clone to the pinned ref but never move it — reinstall with the new ref to advance. Git package deps install with `npm install --omit=dev` (plain `install` when `npmCommand` is configured). Project settings auto-install missing packages on startup after trust.

**Creating a package:** `package.json` with `keywords: ["pi-package"]` (gallery discoverability on pi.dev/packages) and a `pi` manifest, or conventional directories:

```json
{
  "name": "my-pi-package",
  "keywords": ["pi-package"],
  "pi": {
    "extensions": ["./extensions"],
    "skills": ["./skills"],
    "prompts": ["./prompts"],
    "themes": ["./themes"],
    "video": "https://example.com/demo.mp4",
    "image": "https://example.com/shot.png"
  }
}
```

Conventional dirs without a manifest: `extensions/` (`.ts`/`.js`), `skills/` (recursive `SKILL.md` + top-level `.md`), `prompts/` (`.md`), `themes/` (`.json`). Manifest arrays support globs and `!exclusions`; list dot-prefixed paths directly; video (MP4) takes precedence over image in the gallery.

**Dependencies:**
- Third-party runtime deps → `dependencies` (installed automatically by `npm install`).
- Pi-bundled core packages (`pi-ai`, `pi-agent-core`, `pi-coding-agent`, `pi-tui`, `typebox`) → `peerDependencies` with `*`, never bundled.
- Other pi packages → `dependencies` + `bundledDependencies`, referenced through `node_modules/` paths (packages load with separate module roots; no collisions).

**Filtering** (object form in settings):

```json
{
  "packages": [
    { "source": "npm:my-package",
      "extensions": ["extensions/*.ts", "!extensions/legacy.ts"],
      "skills": [],
      "prompts": ["prompts/review.md"],
      "themes": ["+themes/legacy.json"] }
  ]
}
```

Omit key = all; `[]` = none; `!pattern` excludes; `+path`/`-path` exact include/exclude. Filters narrow what the manifest allows.

**Scope/dedup:** a package in both global and project settings — project entry wins unless it sets `autoload: false` (then applied as a delta over global). Identity: npm by package name, git by URL without ref, local by resolved path.
