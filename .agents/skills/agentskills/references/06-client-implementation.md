# Client Implementation Guide

How to add Agent Skills support to an AI agent or development tool.

## The core principle: progressive disclosure

Every skills-compatible agent follows the same three-tier loading strategy:

| Tier | What's loaded | When | Token cost |
|---|---|---|---|
| 1. Catalog | Name + description | Session start | ~50-100 tokens per skill |
| 2. Instructions | Full `SKILL.md` body | When the skill is activated | <5000 tokens (recommended) |
| 3. Resources | Scripts, references, assets | When the instructions reference them | Varies |

## Step 1: Discover skills

At session startup, find all available skills and load their metadata.

### Where to scan

| Scope | Path | Purpose |
|---|---|---|
| Project | `<project>/.<client>/skills/` | Client-specific location |
| Project | `<project>/.agents/skills/` | Cross-client interoperability |
| User | `~/.<client>/skills/` | Client-specific, user-wide |
| User | `~/.agents/skills/` | Cross-client, user-wide |

The `.agents/skills/` paths are the widely-adopted convention for cross-client skill sharing.

### What to scan for

Look for **subdirectories containing a file named exactly `SKILL.md`**:

```
~/.agents/skills/
├── pdf-processing/
│   ├── SKILL.md          ← discovered
│   └── scripts/
├── data-analysis/
│   └── SKILL.md          ← discovered
└── README.md             ← ignored
```

Practical scanning rules:

- Skip `.git/` and `node_modules/`
- Optionally respect `.gitignore`
- Set reasonable bounds (max depth 4-6 levels, max 2000 directories)

### Handling name collisions

Project-level skills override user-level skills. Within the same scope, pick first-found or last-found and be consistent. Log a warning on collision.

### Trust considerations

Project-level skills come from the repository being worked on, which may be untrusted. Consider gating project-level skill loading on a trust check.

### Cloud-hosted and sandboxed agents

- **Project-level skills** travel with the code and can be scanned from the repo
- **User-level and organization-level skills** need an external source — a config repo, skill URLs, or a web UI
- **Built-in skills** can be packaged as static assets within the deployment artifact

## Step 2: Parse SKILL.md files

For each discovered `SKILL.md`, extract the metadata and body content.

### Frontmatter extraction

1. Find the opening `---` at the start of the file and the closing `---` after it
2. Parse the YAML block between them. Extract `name` and `description` (required), plus any optional fields
3. Everything after the closing `---`, trimmed, is the skill's body content

### Handling malformed YAML

Skill files from other clients may contain technically invalid YAML. The most common issue is unquoted values containing colons:

```yaml
# Technically invalid YAML — the colon breaks parsing
description: Use this skill when: the user asks about PDFs
```

Consider a fallback that wraps such values in quotes or converts them to YAML block scalars before retrying.

### Lenient validation

Warn on issues but still load the skill when possible:

- Name doesn't match parent directory → warn, load anyway
- Name exceeds 64 characters → warn, load anyway
- Description is missing or empty → skip the skill
- YAML is completely unparseable → skip the skill

### What to store

| Field | Description |
|---|---|
| `name` | From frontmatter |
| `description` | From frontmatter |
| `location` | Absolute path to the `SKILL.md` file |

Store in an in-memory map keyed by `name` for fast lookup. Derive the skill's **base directory** from `location` when needed.

## Step 3: Disclose available skills to the model

Tell the model what skills exist without loading their full content.

### Building the skill catalog

```xml
<available_skills>
  <skill>
    <name>pdf-processing</name>
    <description>Extract PDF text, fill forms, merge files. Use when handling PDFs.</description>
    <location>/home/user/.agents/skills/pdf-processing/SKILL.md</location>
  </skill>
  <skill>
    <name>data-analysis</name>
    <description>Analyze datasets, generate charts, and create summary reports.</description>
    <location>/home/user/project/.agents/skills/data-analysis/SKILL.md</location>
  </skill>
</available_skills>
```

The `location` field enables file-read activation and gives the model a base path for resolving relative references.

### Where to place the catalog

**System prompt section**: Add the catalog as a labeled section in the system prompt, preceded by brief instructions. Simplest approach, works with any model that has file-reading tools.

**Tool description**: Embed the catalog in the description of a dedicated skill-activation tool. Keeps the system prompt clean.

### Behavioral instructions

**If the model activates skills by reading files:**

```
The following skills provide specialized instructions for specific tasks.
When a task matches a skill's description, use your file-read tool to load
the SKILL.md at the listed location before proceeding.
When a skill references relative paths, resolve them against the skill's
directory (the parent of SKILL.md) and use absolute paths in tool calls.
```

**If the model activates skills via a dedicated tool:**

```
The following skills provide specialized instructions for specific tasks.
When a task matches a skill's description, call the activate_skill tool
with the skill's name to load its full instructions.
```

### Filtering

Hide filtered skills entirely from the catalog rather than listing them and blocking at activation time. This prevents the model from wasting turns.

### When no skills are available

Omit the catalog and behavioral instructions entirely. Don't show an empty `<available_skills/>` block or register a skill tool with no valid options.

## Step 4: Activate skills

When the model or user selects a skill, deliver the full instructions into the conversation context.

### Model-driven activation

Two implementation patterns:

**File-read activation**: The model calls its standard file-read tool with the `SKILL.md` path from the catalog. No special infrastructure needed. Simplest approach when the model has file access.

**Dedicated tool activation**: Register a tool (e.g., `activate_skill`) that takes a skill name and returns the content. Required when the model can't read files directly. Advantages:

- Control what content is returned (strip frontmatter or preserve it)
- Wrap content in structured tags for identification during context management
- List bundled resources alongside the instructions
- Enforce permissions or prompt for user consent
- Track activation for analytics

Constrain the `name` parameter to valid skill names (e.g., as an enum). If no skills are available, don't register the tool at all.

### User-explicit activation

Users should be able to activate skills directly — the most common pattern is a **slash command or mention syntax** (`/skill-name` or `$skill-name`) that the harness intercepts. An autocomplete widget makes this discoverable.

### What the model receives

**Full file**: The model sees the entire `SKILL.md` including YAML frontmatter. Natural outcome with file-read activation.

**Body only (frontmatter stripped)**: The harness parses and removes the YAML frontmatter, returning only the markdown instructions. Common with dedicated activation tools.

### Structured wrapping

Consider wrapping skill content in identifying tags:

```xml
<skill_content name="pdf-processing">
# PDF Processing

[rest of SKILL.md body]

Skill directory: /home/user/.agents/skills/pdf-processing
Relative paths in this skill are relative to the skill directory.

<skill_resources>
  <file>scripts/extract.py</file>
  <file>scripts/merge.py</file>
  <file>references/pdf-spec-summary.md</file>
</skill_resources>
</skill_content>
```

Benefits: the model can distinguish skill instructions from other content; the harness can identify skill content during context compaction; bundled resources are surfaced without eager loading.

### Permission allowlisting

If your agent has a permission system that gates file access, **allowlist skill directories** so the model can read bundled resources without triggering user confirmation prompts.

## Step 5: Manage skill context over time

### Protect skill content from context compaction

If your agent truncates or summarizes older messages when the context window fills up, **exempt skill content from pruning**. Skill instructions are durable behavioral guidance — losing them mid-conversation silently degrades performance.

Common approaches:

- Flag skill tool outputs as protected so the pruning algorithm skips them
- Use the structured tags from Step 4 to identify skill content and preserve it

### Deduplicate activations

Track which skills have been activated in the current session. If the model (or user) attempts to load a skill already in context, skip the re-injection.

### Subagent delegation (optional)

Instead of injecting skill instructions into the main conversation, run the skill in a **separate subagent session**. The subagent receives the skill instructions, performs the task, and returns a summary of its work to the main conversation. Useful when a skill's workflow is complex enough to benefit from a dedicated, focused session.
