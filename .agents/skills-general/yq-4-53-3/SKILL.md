---
name: yq-4-53-3
description: Query, transform, and convert YAML, JSON, XML, INI, TOML, HCL, CSV, TSV, Properties, Lua, Shell variables, and Base64 data using jq-like expressions. Use when the user mentions yq, YAML processing, JSON-to-YAML conversion, config file manipulation, Kubernetes YAML editing, or any structured data transformation task. Supports multi-document YAML, anchors/aliases, comments, and in-place updates.
metadata:
  tags:
    - cli
    - data-processing
    - yaml
    - json
    - config
---

# yq 4.53.3

## Overview

`yq` is a lightweight, portable command-line processor for YAML, JSON, XML, INI, TOML, HCL, CSV, TSV, Properties, Lua, Shell variables, and Base64. It uses `jq`-like expression syntax but works across all these formats. Written in Go — single binary, no dependencies.

Key capabilities:
- Read, update, delete, and create structured data via jq-style expressions
- In-place file editing (`-i`)
- Format conversion between any supported pair (YAML↔JSON, XML→YAML, TOML↔HCL, etc.)
- Multi-document YAML support
- Environment variable injection (`env()`, `strenv()`, `envsubst()`)
- File loading (`load()`, `load_xml()`, `load_props()`)
- Comment and anchor/alias preservation during edits
- Reduce/merge across multiple files with `eval-all`

## Usage

### Basic syntax

```bash
yq [flags] 'expression' [file ...]
yq [flags] 'expression' < file          # pipe from stdin
yq -n 'expression'                       # no input, create from scratch
```

### Common operations

**Read a value:**
```bash
yq '.a.b[0].c' file.yaml
```

**Update in place:**
```bash
yq -i '.a.b[0].c = "cool"' file.yaml
```

**Use environment variables:**
```bash
NAME=mike yq -i '.a.b[0].c = strenv(NAME)' file.yaml
```

**Multiple updates in one pass:**
```bash
yq -i '.a = "x" | .b.c = "y"' file.yaml
```

**Find and update in an array:**
```bash
yq -i '(.[] | select(.name == "foo") | .address) = "12 cat st"' data.yaml
```

**Convert formats:**
```bash
yq -Poy sample.json    # JSON → pretty YAML
yq -o json file.yaml   # YAML → JSON
yq -o yaml file.xml    # XML → YAML
```

**Merge multiple files:**
```bash
yq -n 'load("a.yaml") * load("b.yaml")'
yq ea '. as $item ireduce ({}; . * $item)' path/*.yml
```

**Create from scratch:**
```bash
yq -n '.a.b = "cat" | .x = "frog"'
```

### Key flags

| Flag | Description |
|---|---|
| `-i` | Update file in place |
| `-n` | Null input (create from scratch) |
| `-P` | Pretty print (`... style = ""`) |
| `-r` | Unwrap scalar (no quotes) |
| `-o fmt` | Output format: `yaml`, `json`, `xml`, `toml`, `hcl`, `csv`, `tsv`, `props`, `ini`, `lua`, `shell`, `base64`, `kyaml` |
| `-p fmt` | Input format (default `auto` from extension) |
| `-I n` | Output indent level (default 2) |
| `-N` | No document separators (`---`) |
| `-e` | Exit status based on result |
| `-s exp` | Split output into files named by expression |
| `--indent` | Same as `-I` |
| `--yaml-fix-merge-anchor-to-spec` | Fix merge anchor behavior to YAML spec |

### Expression commands

```bash
yq eval 'expr' file.yaml      # default: process each document in sequence
yq eval-all 'expr' file.yaml  # load all docs from all files, run once (alias: yq ea)
```

## Gotchas

- **PowerShell quoting** — use single quotes for expressions, or escape double quotes. PowerShell expands `$()` and `""` inside strings.
- **Bash trailing newlines** — `$(cmd)` strips trailing newlines. Use `printf -v var "text\n"` or multiline assignment to preserve them in YAML blocks.
- **Merge anchor legacy behavior** — by default, yq uses non-spec merge anchor semantics (later anchors override earlier ones). Add `--yaml-fix-merge-anchor-to-spec` for correct YAML 1.2 behavior (earlier keys win).
- **`yes`/`no` are not booleans** — YAML 1.2 dropped them as boolean values. They parse as strings.
- **Comment preservation is imperfect** — yq tries to preserve comments and whitespace during edits, but complex restructures may lose them.
- **In-place editing (`-i`)** writes to the first file argument only. Subsequent files are read-only inputs.
- **`env()` parses YAML** — `env(VAR)` interprets the value as YAML (so `"true"` becomes boolean). Use `strenv(VAR)` for raw strings.
- **Numeric keys** — `.0` traverses array index 0; use `.["0"]` to access a map key that is literally the string `"0"`.
- **Security flags** — use `--security-disable-env-ops` and `--security-disable-file-ops` when processing untrusted expressions.

## References

- [01-traverse-read](references/01-traverse-read.md) — Path navigation, splat, wildcards, dynamic keys
- [02-assign-update](references/02-assign-update.md) — `=`, `|=`, create nodes, update in place
- [03-select-filter](references/03-select-filter.md) — `select()`, `filter`, boolean and comparison operators
- [04-reduce-merge](references/04-reduce-merge.md) — `ireduce`, merge files, collect into arrays/objects
- [05-format-conversion](references/05-format-conversion.md) — Convert between YAML, JSON, XML, TOML, HCL, CSV, INI, Properties, Lua, Shell
- [06-string-operators](references/06-string-operators.md) — Regex (`test`, `match`, `capture`, `sub`), interpolation, slicing
- [07-env-file-operators](references/07-env-file-operators.md) — `env()`, `strenv()`, `envsubst()`, `load()`, file operations
- [08-datetime](references/08-datetime.md) — Date/time parsing, formatting, timezone handling
- [09-advanced-features](references/09-advanced-features.md) — Comments, style, tags, anchors/aliases, entries, path
