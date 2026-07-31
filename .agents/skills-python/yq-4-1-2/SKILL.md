---
name: yq-4-1-2
description: >
  yq 4.1.2 — command-line YAML/XML/TOML processor that wraps jq. Use when querying,
  filtering, transforming, or editing YAML, XML, or TOML files from the shell or scripts.
  Provides three executables: `yq` (YAML), `xq` (XML), `tomlq` (TOML). Supports YAML
  roundtrip with tag/style preservation (`-Y`), in-place editing (`-i`), JSON conversion,
  and all jq filters. Trigger on: YAML processing, XML parsing CLI, TOML editing, yq,
  xq, tomlq, jq wrapper, YAML to JSON, editing YAML in-place, CloudFormation templates,
  Kubernetes config edits, or any shell-based structured data manipulation.
license: Apache-2.0
compatibility: Requires Python 3.8+ and jq installed on PATH. Depends on PyYAML, xmltodict, tomlkit, argcomplete
metadata:
  tags:
    - python
    - cli
    - yaml
    - xml
    - toml
    - jq
---

# yq 4.1.2

## Overview

yq is a lightweight, portable command-line processor for YAML, XML, and TOML documents. It works by transcoding input documents to JSON, piping them through `jq`, and optionally transcoding the result back to the original format. This gives you the full power of `jq` expressions on structured non-JSON data.

### Architecture

```
YAML/XML/TOML → JSON → jq → JSON → YAML/XML/TOML
```

All `jq` filters and options are supported. yq intercepts only a small set of flags (`-y`, `-Y`, `-x`, `-t`, `-T`, `-i`, `-w`) and forwards everything else to `jq`.

### Three Executables

| Command | Input | Output | Roundtrip flag |
|---|---|---|---|
| `yq` | YAML | JSON (default) | `-y` (YAML), `-Y` (YAML with tags/styles) |
| `xq` | XML | JSON (default) | `-x` (XML) |
| `tomlq` | TOML | JSON (default) | `-t` (TOML), `-T` (TOML with comments) |

### Installation

```bash
pip install yq==4.1.2
# Also requires jq on PATH (install via brew, apt, dnf, etc.)
```

### Core Concepts

- **Default output is JSON** — use `-y`/`-x`/`-t` to convert back to structured format
- **`-Y` (yaml-roundtrip)** preserves custom YAML tags (`!Ref`, `!GetAZs`) and string styles (`>-`, `|`) by injecting metadata keys into the JSON stream
- **`-i` (in-place)** edits files directly, like `sed -i`; requires a matching output flag
- **`python -m yq`**, `python -m yq.xq`, `python -m yq.tomlq` — invoke with a specific Python runtime
- **Multiple documents** — YAML multi-doc streams are handled via `yaml.safe_load_all` semantics
- **Mapping key order** is preserved through the JSON roundtrip

## Usage

### Basic YAML Queries

```bash
# Query a YAML file (output is JSON by default)
yq .foo.bar config.yml

# Output as YAML
yq -y .foo.bar config.yml

# Pipe from stdin
cat config.yml | yq -y '.items[] | select(.enabled)'

# Multiple files
yq -y '.version' app1.yml app2.yml
```

### In-Place Editing

```bash
# Edit YAML in place (like sed -i)
yq -i -y '.database.host = "prod-db.example.com"' config.yml

# Edit Kubernetes config
python -m yq -Y -i --indentless '.["current-context"] = "staging-cluster"' ~/.kube/config
```

### JSON Conversion

```bash
# YAML to JSON
yq . config.yml > config.json

# JSON to YAML (YAML treats JSON as a dialect)
yq -y . config.json > config.yml
```

### XML Processing (xq)

```bash
# Query XML
xq -x '.root.item' data.xml

# Stream large XML docs without loading fully into memory
cat dump.xml | xq . --xml-item-depth 2

# Force list output for single elements
xq -x '.items' data.xml --xml-force-list item --xml-force-list subitem

# Envelope output with a root element
xq -x --xml-root result '.[] | select(.active)' data.xml
```

### TOML Processing (tomlq)

```bash
# Query TOML
tomlq '.database' config.toml

# Output as TOML
tomlq -t '.database.host = "new-host"' config.toml

# Roundtrip — preserve comments and formatting
tomlq -T '.database.port = 5432' config.toml
```

### YAML Roundtrip with Tag and Style Preservation

```bash
# Preserve AWS CloudFormation tags (!Ref, !GetAZs) and folded styles
yq -Y '.Resources.EC2Instance' template.yml

# In-place edit preserving tags
yq -Y -i '.Resources.EC2Instance.Properties.InstanceType = "t3.large"' template.yml
```

### Advanced jq Integration

```bash
# Use jq's --arg for safe variable injection
yq -y --arg env production '.environment = $env' config.yml

# Use jq's --slurpfile for loading reference data
yq -y --slurpfile defaults defaults.yml '. + $defaults[0]' config.yml

# Combine with jq's built-in flags
yq -y -M '.' config.yml            # compact output (no indentation)
yq -y -C '.' config.yml            # colorized output (terminal only)
yq -y -n 'def tojson: tostring | @json; . | tojson' config.yml  # null input
```

### String Width Control

```bash
# Default wrapping
yq -y '.' config.yml

# Disable line wrapping for long strings
yq -y --width 0 '.' config.yml

# Custom wrap width
yq -y --width 80 '.' config.yml
```

### YAML Grammar Version

```bash
# YAML 1.1 output (default) — quotes "yes", "no", "on", "off"
yq -y '.' config.yml

# YAML 1.2 output — emits "yes", "no", "on", "off" unquoted
yq -y --yaml-output-grammar-version 1.2 '.' config.yml
```

### Explicit Document Markers

```bash
# Always emit --- and ... markers
yq -y --explicit-start --explicit-end '.' config.yml
```

### Programmatic Use

```python
from yq import yq

# Use yq as a Python function
yq(
    input_streams=[open("config.yml")],
    output_stream=sys.stdout,
    input_format="yaml",
    output_format="yaml",
    jq_args=[".foo.bar"],
)
```

## Gotchas

- **jq is a hard dependency** — yq will not work without `jq` installed and on PATH. Install it separately via your system package manager.
- **`-Y` mode injects metadata keys** — when using yaml-roundtrip (`-Y`), extra keys like `__yq_tag__`, `__yq_style__`, and `__yq_comment__` appear in the JSON stream. jq filters that count array entries or expect clean data will see inflated results. Always test jq filters in plain mode first, then add `-Y`.
- **`-i` requires a filename, not stdin** — in-place editing fails on piped input. Always provide explicit file paths with `-i`.
- **`-i` requires matching output format** — `yq -i` alone is an error; you must add `-y`, `-Y`, `-t`, `-T`, or `-x`.
- **YAML 1.1 vs 1.2 boolean/null resolution** — default output grammar is 1.1, which means strings like `yes`, `no`, `on`, `off` are quoted in output. Switch to `--yaml-output-grammar-version 1.2` if you need them unquoted. In 1.2, only `true`/`false` are booleans.
- **Aliases are expanded by default** — YAML anchors/aliases (`&anchor`, `*alias`) are expanded during loading. Use `--no-expand-aliases` to preserve them as `__yq_alias__` markers (roundtrip support for aliases is partial).
- **`--width 0` disables wrapping** — without it, long string values get line-wrapped at 80 chars by default, which can break values meant to stay on one line.
- **Entity expansion protection** — yq detects unsafe YAML entity bombs and aborts with exit code 1. The `--max-expansion-factor` (default 1024) controls the threshold.
- **`xq` streaming with `--xml-item-depth`** — for large XML files, use `--xml-item-depth=N` to stream entries at depth N without loading the full document. Entity expansion and DTD resolution are disabled by default for security.
- **TOML top-level must be a mapping** — `tomlq` cannot represent non-object types at the document root when outputting TOML. Wrap with a root key if needed.
- **Exit codes** — yq forwards jq's exit code. YAML parse errors produce exit code 1. Use `$?` or `set -e` to catch failures.
- **Not the same as mikefarah/yq** — this is `kislyuk/yq` (Python, jq-based). The Go-based `mikefarah/yq` is a completely different tool with different syntax and features. Check which one is installed with `yq --version`.

