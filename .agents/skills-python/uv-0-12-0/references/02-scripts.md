# Scripts

## Running Scripts

### Without dependencies

```bash
uv run example.py                      # uses project deps if in a project
uv run --no-project example.py         # skip project deps
```

Arguments pass through to the script:

```bash
uv run example.py arg1 arg2
```

### With one-off dependencies

```bash
uv run --with rich example.py
uv run --with 'rich>=13' --with pygments example.py
```

`--with` installs the dependency into a temporary environment for that invocation only. It does not modify `pyproject.toml` or `uv.lock`.

### From stdin

```bash
echo 'print("hello")' | uv run -
```

Or with here-documents:

```bash
uv run - <<EOF
import sys
print(sys.version)
EOF
```

## Inline Script Metadata (PEP 723)

Scripts can declare dependencies directly in the file using a special comment block:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "requests>=2.28.0",
# ]
# ///

import requests
print(requests.get("https://example.com"))
```

### Creating scripts with metadata

```bash
uv init --script example.py --python 3.12
```

### Adding dependencies to scripts

```bash
uv add --script example.py requests
uv add --script example.py 'requests>=2.28.0'
```

This modifies the inline metadata block in the script file.

### Running scripts with inline metadata

```bash
uv run example.py
```

uv reads the inline metadata and creates an isolated environment with the declared dependencies. The environment is cached based on the script's content hash.

## Script Discovery

Since 0.12.0, uv discovers the project relative to the script's directory, not the current working directory:

```bash
# Uses other-project's dependencies, not the current directory's
uv run other-project/script.py
```

Force current-directory discovery:

```bash
uv run --project . other-project/script.py
```

## Script environments

uv caches script environments in its global cache, keyed by the script's content hash and declared dependencies. Re-running the same script reuses the cached environment, making subsequent runs fast.

To force a refresh:

```bash
uv run --refresh example.py
uv run --refresh-package requests example.py
```

## Script metadata fields

The inline metadata block supports these fields:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = ["requests"]
# dev-dependencies = ["pytest"]
# tools = { "ruff" = { "args" = ["check"] } }
# ///
```

- `requires-python` — Python version constraint
- `dependencies` — list of package requirements
- `dev-dependencies` — development-only packages
- `tools` — tool configuration (for `uv tool` integration)
