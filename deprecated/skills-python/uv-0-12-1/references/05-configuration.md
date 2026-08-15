# Configuration — files, environment variables, settings

## Config file discovery

uv searches for config in this order (most specific first):

1. `uv.toml` in current directory (takes precedence over pyproject.toml in same dir)
2. `pyproject.toml` → `[tool.uv]` section
3. Parent directories upward
4. User-level: `~/.config/uv/uv.toml` (Unix) or `%APPDATA%\uv\uv.toml` (Windows)
5. System-level: `/etc/uv/uv.toml` (Unix) or `%PROGRAMDATA%\uv\uv.toml` (Windows)

Settings merge upward: project > user > system. Arrays are concatenated; scalars are overridden.

`uv.toml` files omit the `[tool.uv]` prefix:

```toml
# uv.toml (equivalent to [tool.uv] in pyproject.toml)
[[index]]
url = "https://test.pypi.org/simple"
default = true
```

User- and system-level configs must use `uv.toml` format (not pyproject.toml).

### Disabling config

```bash
uv run --no-config                        # disable all config discovery
uv run --config-file /path/to/uv.toml     # use specific config file only
```

## Environment variables

Key environment variables:

| Variable | Purpose |
|---|---|
| `UV_CACHE_DIR` | Override cache directory |
| `UV_PROJECT_ENVIRONMENT` | Override `.venv` path |
| `UV_PYTHON_DOWNLOADS` | `auto` (default), `never` |
| `UV_NO_CACHE` | Use temp cache (equivalent to `--no-cache`) |
| `UV_INDEX` | Extra index (`name=url`) |
| `UV_DEFAULT_INDEX` | Default index URL |
| `UV_INDEX_STRATEGY` | `first-index`, `unsafe-first-match`, `unsafe-best-match` |
| `UV_PYTHON_PREFERENCE` | `managed`, `system`, `only-managed`, `only-system` |
| `UV_RESOLUTION` | `highest` (default), `lowest`, `lowest-direct` |
| `UV_PUBLISH_TOKEN` | Token for `uv publish` |
| `UV_PUBLISH_USERNAME` | Username for `uv publish` |
| `UV_PUBLISH_PASSWORD` | Password for `uv publish` |
| `UV_ENV_FILE` | Default .env file for `uv run` |
| `UV_NO_ENV_FILE` | Disable .env loading |
| `UV_LOCK_TIMEOUT` | Cache lock timeout (default 5 min) |
| `UV_GIT_LFS` | Default Git LFS behavior (`true`/`false`) |
| `UV_RESPECT_SYSTEM_PYTHON` | Use system Python (`--system`) |
| `UV_SYSTEM_PYTHON` | Same as above |
| `UV_MALWARE_CHECK` | Enable on-sync malware checking |
| `UV_NO_BARRIER` | Disable progress bars |

## .env files

`uv run` loads `.env` files automatically:

```bash
uv run --env-file .env -- python script.py
uv run --env-file .env --env-file .env.local -- python script.py
uv run --no-env-file -- python script.py        # disable
```

Environment variables override `.env` values.

## uv.toml vs pyproject.toml

Use `uv.toml` when:
- You want uv settings separate from project metadata
- You need settings that apply outside project context
- You want to override `pyproject.toml` settings in the same directory

Use `pyproject.toml` → `[tool.uv]` when:
- Settings are project-specific
- You want settings checked into version control with the project

## Key settings

### Cache

```toml
cache-dir = "/custom/cache/path"
```

### Python

```toml
python-downloads = "never"          # disable auto-download
python-preference = "managed"       # prefer managed over system
```

### Resolution

```toml
resolution = "lowest"               # resolve lowest compatible versions
resolution = "lowest-direct"        # lowest for direct deps only
```

### Indexes

```toml
[[index]]
name = "pytorch"
url = "https://download.pytorch.org/whl/cpu"

# or pip-style
index-url = "https://pypi.org/simple/"
extra-index-url = ["https://test.pypi.org/simple/"]
```

### Exclude newer

```toml
exclude-newer = "2024-01-01T00:00:00Z"
```

Or per-package in `uv.toml`:

```toml
exclude-newer-package = { requests = "2023-06-01T00:00:00Z" }
```

### Build

```toml
no-build-package = ["package-a"]    # never build these from source
```

### Compilation

```toml
compile-bytecode = true             # pre-compile .pyc files
```

### Link mode

```toml
link-mode = "clone"                 # clone (default), copy, hardlink, symlink
```

### Tool

```toml
[tool]
upgrade = true                      # auto-upgrade tools on `uv tool install`
```

## Settings precedence

Command-line > environment variables > project config > user config > system config.

## Storage directories

| Directory | Purpose | Default (Unix) |
|---|---|---|
| Cache | Wheels, metadata, git | `$XDG_CACHE_HOME/uv` or `~/.cache/uv` |
| Data | Tools, Python versions | `$XDG_DATA_HOME/uv` or `~/.local/share/uv` |
| Config | uv.toml | `$XDG_CONFIG_HOME/uv` or `~/.config/uv` |
| Bin | Python executables, tool bins | `~/.local/bin` |
| Config (system) | System uv.toml | `/etc/uv/uv.toml` |

View paths:

```bash
uv cache dir
uv tool dir
uv python dir
```
