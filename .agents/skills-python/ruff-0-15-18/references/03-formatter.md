# Formatter

## Overview

`ruff format` is a Black-compatible Python code formatter. It targets near-identical output to Black (>99.9% line match on large projects) while being significantly faster and offering a few additional configuration options.

## Commands

```bash
ruff format                   # Format in-place
ruff format path/to/code/     # Format specific directory
ruff format file.py           # Format single file
ruff format --check           # Check without writing (non-zero exit if changes needed)
ruff format --diff            # Show formatting diff
ruff format --preview         # Enable preview formatting
ruff format --no-cache        # Skip cache
ruff format --exit-non-zero-on-format  # Exit non-zero if any file was modified
```

## Configuration

```toml
[tool.ruff.format]
quote-style = "double"           # "double", "single", or "preserve"
indent-style = "space"           # "space" or "tab"
skip-magic-trailing-comma = false  # Respect magic trailing commas like Black
line-ending = "auto"             # "auto", "lf", "crlf", or "cr"
docstring-code-format = false    # Format code in docstrings
docstring-code-line-length = "dynamic"  # Line length for docstring snippets
preview = false                  # Enable preview formatting
```

## Black Compatibility

Ruff's formatter is designed as a drop-in replacement for Black:

- Same default line length (88)
- Same quote style (double)
- Same indentation (spaces, width 4)
- Magic trailing comma support
- Similar handling of function signatures, collections, and binary operations

### Known deviations

Ruff differs from Black in a few conscious ways where Ruff's behavior is deemed more consistent or simpler to implement. Do not run Black and Ruff formatter interchangeably on the same codebase over time.

## Docstring Formatting

When `docstring-code-format = true`, Ruff formats Python code examples inside docstrings:

- **doctest** format (```>>>``` prompts)
- **Markdown** fenced code blocks (`python`, `py`, `python3`, `py3`, or no info string)
- **reStructuredText** literal blocks and `code-block`/`sourcecode` directives

Docstring code uses its own line length limit set by `docstring-code-line-length`. Use `"dynamic"` to inherit the main `line-length`, or set a specific number.

## Jupyter Notebooks

Ruff formats `.ipynb` files by default (since 0.6.0). It reformats code cells while preserving notebook metadata, outputs, and structure.

To exclude notebooks from formatting:

```toml
[tool.ruff.format]
exclude = ["*.ipynb"]
```

## Preview Formatting

Preview mode enables unstable formatting changes:

```bash
ruff format --preview
```

Or in config:

```toml
[tool.ruff.format]
preview = true
```

Preview formatting can be enabled independently of preview linting.

## Combining Lint and Format in CI

```bash
# Check both without modifying files
ruff check . && ruff format --check .

# Or fix and format together
ruff check --fix . && ruff format .
```

## Performance Tips

- Ruff caches results in `.ruff_cache`. Use `ruff clean` to clear.
- The `--no-cache` flag disables caching (useful for CI with fresh checkout).
- For large projects, consider setting `cache-dir` to a fast storage location.
