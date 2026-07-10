# Using Scripts in Skills

How to run commands and bundle executable scripts in your skills.

## One-off commands

When an existing package already does what you need, reference it directly in `SKILL.md` without a `scripts/` directory. Many ecosystems provide tools that auto-resolve dependencies at runtime.

### uvx (Python, recommended)

Ships with [uv](https://docs.astral.sh/uv/). Fast, aggressive caching.

```bash
uvx ruff@0.8.0 check .
uvx black@24.10.0 .
```

### pipx (Python)

Available via OS package managers.

```bash
pipx run 'black==24.10.0' .
pipx run 'ruff==0.8.0' check .
```

### npx (Node.js)

Ships with npm (which ships with Node.js).

```bash
npx eslint@9 --fix .
npx create-vite@6 my-app
```

### bunx (Bun)

Drop-in replacement for npx in Bun-based environments.

```bash
bunx eslint@9 --fix .
```

### deno run (Deno)

Permission flags required for filesystem/network access.

```bash
deno run npm:create-vite@6 my-app
deno run --allow-read npm:eslint@9 -- --fix .
```

### go run (Go)

Built into Go — no extra tooling needed.

```bash
go run golang.org/x/tools/cmd/goimports@v0.28.0 .
go run github.com/golangci/golangci-lint/cmd/golangci-lint@v1.62.0 run
```

**Tips for one-off commands:**

- **Pin versions** (e.g., `npx eslint@9.0.0`) for reproducibility
- **State prerequisites** in `SKILL.md` (e.g., "Requires Node.js 18+") rather than assuming the environment has them
- **Move complex commands into scripts** — when a command grows complex enough that it's hard to get right on the first try, a tested script in `scripts/` is more reliable

## Referencing scripts from SKILL.md

Use **relative paths from the skill directory root**. The agent resolves these paths automatically.

List available scripts in `SKILL.md`:

```markdown
## Available scripts

- **`scripts/validate.sh`** — Validates configuration files
- **`scripts/process.py`** — Processes input data
```

Then instruct the agent to run them:

```markdown
## Workflow

1. Run the validation script:
   ```bash
   bash scripts/validate.sh "$INPUT_FILE"
   ```

2. Process the results:
   ```bash
   python3 scripts/process.py --input results.json
   ```
```

Script execution paths (in code blocks) are relative to the **skill directory root**, because the agent runs commands from there.

## Self-contained scripts

Bundle a script in `scripts/` that declares its own dependencies inline — no separate manifest or install step required.

### Python (PEP 723)

Declare dependencies in a TOML block inside `# ///` markers:

```python
# /// script
# dependencies = [
#   "beautifulsoup4",
# ]
# ///

from bs4 import BeautifulSoup
```

Run with uv (recommended):

```bash
uv run scripts/extract.py
```

- Pin versions with PEP 508 specifiers: `"beautifulsoup4>=4.12,<5"`
- Use `requires-python` to constrain the Python version
- Use `uv lock --script` for full reproducibility

### Deno

`npm:` and `jsr:` import specifiers make every script self-contained:

```typescript
#!/usr/bin/env -S deno run
import * as cheerio from "npm:cheerio@1.0.0";
```

```bash
deno run scripts/extract.ts
```

- Version specifiers follow semver: `@1.0.0` (exact), `@^1.0.0` (compatible)
- Dependencies are cached globally

### Bun

Auto-installs missing packages at runtime when no `node_modules` exists:

```typescript
#!/usr/bin/env bun
import * as cheerio from "cheerio@1.0.0";
```

```bash
bun run scripts/extract.ts
```

- TypeScript works natively
- If `node_modules` exists in the tree, auto-install is disabled

### Ruby (Bundler inline)

```ruby
require 'bundler/inline'

gemfile do
  source 'https://rubygems.org'
  gem 'nokogiri'
end
```

```bash
ruby scripts/extract.rb
```

- Pin versions explicitly (`gem 'nokogiri', '~> 1.16'`)
- An existing `Gemfile` or `BUNDLE_GEMFILE` env var can interfere

## Designing scripts for agentic use

When an agent runs your script, it reads stdout and stderr to decide what to do next.

### Avoid interactive prompts

Agents operate in non-interactive shells — they cannot respond to TTY prompts, password dialogs, or confirmation menus. A script that blocks on interactive input will hang indefinitely.

Accept all input via command-line flags, environment variables, or stdin:

```
# Bad: hangs waiting for input
$ python scripts/deploy.py
Target environment: _

# Good: clear error with guidance
$ python scripts/deploy.py
Error: --env is required. Options: development, staging, production.
Usage: python scripts/deploy.py --env staging --tag v1.2.3
```

### Document usage with --help

`--help` output is the primary way an agent learns your script's interface. Include a brief description, available flags, and usage examples. Keep it concise — the output enters the agent's context window.

### Write helpful error messages

When an agent gets an error, the message directly shapes its next attempt. Say what went wrong, what was expected, and what to try:

```
Error: --format must be one of: json, csv, table.
       Received: "xml"
```

### Use structured output

Prefer structured formats — JSON, CSV, TSV — over free-form text. They can be consumed by both the agent and standard tools (`jq`, `cut`, `awk`), making scripts composable in pipelines.

**Separate data from diagnostics:** send structured data to stdout and progress messages, warnings, and diagnostics to stderr.

### Further considerations

- **Idempotency** — agents may retry commands. "Create if not exists" is safer than "create and fail on duplicate"
- **Input constraints** — reject ambiguous input with a clear error rather than guessing
- **Dry-run support** — for destructive operations, a `--dry-run` flag lets the agent preview what will happen
- **Meaningful exit codes** — use distinct exit codes for different failure types and document them in `--help`
- **Safe defaults** — consider whether destructive operations should require explicit confirmation flags
- **Predictable output size** — agent harnesses may truncate tool output. Default to a summary or reasonable limit, support `--offset` for pagination, or require `--output` for large output
