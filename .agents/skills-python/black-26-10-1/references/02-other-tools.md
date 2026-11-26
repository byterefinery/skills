# Black — Other Tools Compatibility

## isort

Use the `black` profile for automatic compatibility:

```toml
[tool.isort]
profile = "black"
```

For isort < 5.0.0 or custom Black config, use:

```ini
[settings]
multi_line_output = 3
include_trailing_comma = True
force_grid_wrap = 0
use_parentheses = True
ensure_newline_before_comments = True
line_length = 88
```

## pycodestyle

```ini
[pycodestyle]
max-line-length = 88
ignore = E203,E701
```

- `E203` — Black adds whitespace around `:` in complex slices (PEP 8 compliant);
  pycodestyle's warning is not PEP 8 compliant
- `E701` — Black collapses `pass`/`...` bodies to single line (PEP 8 compliant);
  pycodestyle does not mirror this logic

## Flake8

Recommended config with Bugbear plugin (B950 uses Black's 10% overage rule):

```ini
[flake8]
max-line-length = 80
extend-select = B950
extend-ignore = E203,E501,E701
```

Minimal config without Bugbear:

```ini
[flake8]
max-line-length = 88
extend-ignore = E203,E701
```

- `W503` (line break before binary operator) — disabled by default in Flake8, do not
  enable. Black breaks **before** binary operators per PEP 8. Use `W504` instead if
  needed.

## Pylint

```toml
[tool.pylint.format]
max-line-length = "88"
```

For `pylint < 2.6.0`, also disable `C0326` and `C0330` (incompatible with Black and
since removed).

## ruff

ruff has a built-in Black-compatible formatter. When using both Black and ruff:

- Use ruff for linting only (`ruff check`), Black for formatting
- Or use ruff for both (`ruff format` + `ruff check`) — ruff's formatter is
  Black-compatible but not identical

For ruff + Black coexistence, configure ruff to ignore formatting rules:

```toml
[tool.ruff.lint]
# Let Black handle formatting; ruff only lints
select = ["E", "F", "B", "I"]
ignore = ["E501", "E701", "E203", "W503"]
```

## Editor integrations

Most editors support Black via LSP or direct integration. Common approaches:

- **VS Code** — `python.formatting.provider` set to `black`, or use Black's language
  server
- **Neovim** — conform.nvim, ALE, or direct command execution
- **Sublime Text** — `sublack` plugin (archived/unmaintained as of 2025)
- **Vim** — various plugins available

Check Black's documentation for the latest editor-specific guides.
