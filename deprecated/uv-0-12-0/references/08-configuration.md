# Configuration

## tool.uv settings

Configure uv in `pyproject.toml` under `[tool.uv]`:

```toml
[tool.uv]
managed = false                            # disable auto lock/sync
package = false                            # non-package project (scripts)
python-downloads = "automatic"             # "automatic" | "manual" | "never"
required-version = ">=0.12.0"              # minimum uv version
override-dependencies = ["pkg==1.0"]       # force versions globally
constraint-dependencies = ["pkg>=1.0"]     # constrain resolution
compile-bytecode = true                    # pre-compile .pyc
default-groups = ["dev"]                   # always include these groups

# Cache key customization
cache-keys = [
  { file = "pyproject.toml" },
  { git = { commit = true, tags = true } }
]

# Workspace
[tool.uv.workspace]
members = ["packages/*"]
exclude = ["packages/internal"]

# Dependency sources
[tool.uv.sources]
my-lib = { workspace = true }
custom = { git = "https://github.com/user/repo", tag = "v1.0" }
local  = { path = "../local-pkg", editable = true }
```

## Indexes

### Configuration

```toml
[tool.uv.index]
url = "https://custom.pypi.org/simple/"
default = false                            # secondary index
explicit = false                           # available for all packages

[[tool.uv.index]]
name = "test-pypi"
url = "https://test.pypi.org/simple/"
explicit = true                            # only for packages that request it
```

### CLI overrides

```bash
uv add --index-url https://custom.pypi.org/simple/ requests
uv pip install --index-url https://custom.pypi.org/simple/ requests
uv pip install --extra-index-url https://test.pypi.org/simple/ requests
```

### Per-package indexes

```toml
[tool.uv.index]
url = "https://pypi.org/simple/"

[tool.uv.sources]
internal-pkg = { index = "internal" }

[[tool.uv.index]]
name = "internal"
url = "https://internal.pypi.org/simple/"
```

## Cache

### Cache location

- Linux: `$XDG_CACHE_HOME/uv` or `~/.cache/uv`
- macOS: `~/.cache/uv`
- Windows: `%LOCALAPPDATA%\uv\cache`

Override with `UV_CACHE_DIR`.

### Cache management

```bash
uv cache clean                    # clear all
uv cache clean requests           # clear specific package
uv cache dir                      # show cache directory
```

### Refreshing

```bash
uv sync --refresh                 # revalidate all cached data
uv sync --refresh-package ruff    # revalidate single package
uv pip install --refresh requests
```

## Environment variables

| Variable | Description |
|----------|-------------|
| `UV_CACHE_DIR` | Override cache directory |
| `UV_PYTHON_DOWNLOADS` | `"automatic"`, `"manual"`, `"never"` |
| `UV_INDEX_URL` | Default package index URL |
| `UV_EXTRA_INDEX_URL` | Additional index URLs |
| `UV_PROJECT_ENVIRONMENT` | Override project environment path |
| `UV_NO_CACHE` | Disable caching entirely (`1`/`true`) |
| `UV_RESOLUTION` | Resolution strategy: `"highest"` (default) or `"lowest"` or `"lowest-direct"` |
| `UV_PRERELEASE` | Pre-release strategy: `"allow"`, `"disallow"`, `"if-necessary"`, `"explicit"` |
| `UV_PUBLISH_TOKEN` | PyPI publish token |
| `UV_PYPI_TOKEN` | PyPI authentication token |
| `UV_TOOL_DIR` | Override tool installation directory |
| `UV_VIRTUAL_ENVS_IN_WORKSPACE` | Allow `.venv` in workspace root (`true`/`false`) |
| `UV_RESPECT_SYSTEM_PYTHON` | Use system Python without venv (`1`/`true`) |
| `VIRTUAL_ENV` | Target virtual environment |
| `PYTHONDONTWRITEBYTECODE` | Skip .pyc compilation |
| `SSL_CERT_FILE` / `SSL_CERT_DIR` | Custom certificate roots |

## Resolution strategies

```bash
uv lock --resolution highest         # latest compatible (default)
uv lock --resolution lowest          # lowest compatible versions
uv lock --resolution lowest-direct   # lowest for direct deps, highest for transitive
```

## Pre-release handling

```bash
uv lock --prerelease allow           # consider pre-releases freely
uv lock --prerelease disallow        # reject all pre-releases
uv lock --prerelease if-necessary    # prefer stable, fall back to pre-release (default)
uv lock --prerelease explicit        # only for direct deps that mention pre-release
```

## Python preferences

```bash
uv run --python-prefer-managed       # prefer uv-managed Python over system
uv run --python-platform linux-x86_64  # override platform for resolution
```
