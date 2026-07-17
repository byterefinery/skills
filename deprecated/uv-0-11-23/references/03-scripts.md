# Scripts

uv runs Python scripts with automatic dependency management, supporting inline metadata (PEP 723) for self-contained executable scripts.

## Running Scripts

```bash
# Run a script (uses project env if in a project)
uv run script.py

# Run with arguments
uv run script.py --flag value

# Run with ad-hoc dependencies
uv run --with requests script.py
uv run --with 'requests>=2.28' --with rich script.py

# Run without project context
uv run --no-project script.py

# Read from stdin
echo 'print("hello")' | uv run -

# Here-document
uv run - <<EOF
import sys
print(sys.version)
EOF
```

## Inline Script Metadata (PEP 723)

Dependencies declared directly in the script file using a TOML comment block:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "requests",
#     "rich",
# ]
# ///

import requests
from rich.pretty import pprint

resp = requests.get("https://httpbin.org/get")
pprint(resp.json())
```

The block must appear within the first 100 lines. The `dependencies` field is required even if empty.

### Managing Script Metadata

```bash
# Initialize a script with metadata
uv init --script tool.py --python 3.12

# Add dependencies to script
uv add --script tool.py requests rich

# Remove dependency from script
uv remove --script tool.py rich

# Lock script dependencies (creates tool.py.lock)
uv lock --script tool.py

# Export script dependencies
uv export --script tool.py
```

### Running Scripts with Inline Metadata

Simply run with `uv run` — no extra flags needed:

```bash
uv run tool.py
```

uv reads the inline metadata, creates an ephemeral environment with the declared dependencies, and executes the script. The script runs independently of any surrounding project.

## Shebang for Executable Scripts

Make scripts directly executable without `uv run`:

```python
#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.12"
# dependencies = ["httpx"]
# ///

import httpx
print(httpx.get("https://example.com"))
```

```bash
chmod +x tool.py
./tool.py
```

## Reproducible Scripts

Lock dependencies and add `exclude-newer` for reproducibility:

```python
# /// script
# dependencies = ["requests"]
# [tool.uv]
# exclude-newer = "2025-01-01T00:00:00Z"
# ///
```

This ensures the same versions resolve regardless of when the script runs.

## Alternative Indexes for Scripts

```bash
uv add --index "https://private.pypi/simple" --script tool.py requests
```

Adds `[[tool.uv.index]]` to the inline metadata.

## GUI Scripts (Windows)

Scripts with `.pyw` extension run with `pythonw` (no console window):

```bash
uv run example.pyw
uv run --with PyQt5 example.pyw
```

## Key Differences from Projects

- Inline script metadata **ignores project dependencies** — no need for `--no-project`
- Script lockfiles are adjacent: `script.py.lock` (not `uv.lock`)
- Scripts use ephemeral environments unless locked
- Scripts cannot be part of a workspace
