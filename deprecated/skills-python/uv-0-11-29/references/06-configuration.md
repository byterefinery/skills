# Configuration

## Configuration Hierarchy

Settings are resolved in order:

1. Command-line flags (highest priority)
2. Environment variables
3. `pyproject.toml` (`[tool.uv]` section)
4. User-level config file
5. Defaults (lowest priority)

Disable config file discovery with `--no-config`.

## pyproject.toml Settings

```toml
[tool.uv]
# Python
python-preference = "managed"       # managed, only-managed, system, only-system
python-downloads = "automatic"      # automatic, manual, disabled

# Resolution
resolution = "highest"              # highest, lowest, lowest-direct
prerelease = "allow"                # allow, disallow, if-necessary-or-explicit
fork-priorities = []                # custom fork priority order

# Cache
cache-dir = "/custom/cache/path"    # override cache directory

# Sources
sources = []                        # package sources (see dependencies)

# Workspace
workspace = { members = ["packages/*"], exclude = ["packages/seeds"] }

# Build
no-build-isolation-package = ["cchardet"]
extra-build-dependencies = { cchardet = ["cython"] }
reinstall-package = ["my-package"]

# Cache keys
cache-keys = [{ file = "pyproject.toml" }, { git = { commit = true } }]

# Indexes
indexes = []                        # [[tool.uv.index]] entries

# Constraints
constraint-dependencies = ["pydantic<2.0"]
build-constraint-dependencies = ["setuptools==75.0.0"]

# Overrides
override-dependencies = []          # force specific versions

# Environment filtering
environments = ["sys_platform == 'linux'"]
required-environments = ["sys_platform == 'linux' and platform_machine == 'x86_64'"]

# Conflicts
conflicts = [[{ extra = "extra1" }, { extra = "extra2" }]]

# Packaging
package = true                      # force build/install project

# Exclude newer
exclude-newer = "2024-06-01T00:00:00Z"
```

## Environment Variables

| Variable | Description |
|---|---|
| `UV_CACHE_DIR` | Override cache directory |
| `UV_PYTHON_INSTALL_DIR` | Override managed Python install directory |
| `UV_TOOL_DIR` | Override tool install directory |
| `UV_PROJECT_ENVIRONMENT` | Override project virtual environment path |
| `UV_NO_CACHE` | Equivalent to `--no-cache` |
| `UV_PYTHON_PREFERENCE` | Equivalent to `--python-preference` |
| `UV_PYTHON_DOWNLOADS` | Equivalent to `--python-downloads` |
| `UV_RESOLUTION` | Equivalent to `--resolution` |
| `UV_PRERELEASE` | Equivalent to `--prerelease` |
| `UV_INDEX` | Equivalent to `--index` |
| `UV_DEFAULT_INDEX` | Equivalent to `--default-index` |
| `UV_INDEX_<NAME>_USERNAME` | Username for named index |
| `UV_INDEX_<NAME>_PASSWORD` | Password for named index |
| `UV_LOCK_TIMEOUT` | Timeout for cache locks (default: 5 min) |
| `UV_PUBLISH_TOKEN` | Token for `uv publish` |
| `UV_EXCLUDE_NEWER` | Equivalent to `--exclude-newer` |
| `UV_NATIVE_TLS` | Use platform TLS (default: true) |
| `UV_NO_NATIVE_TLS` | Disable platform TLS |
| `UV_OFFLINE` | Disable network access |
| `UV_NO_OFFLINE` | Re-enable network access |
| `UV_VERBOSE` / `UV_QUIET` | Equivalent to `-v` / `-q` |
| `UV_COLOR` | Control color output (auto, always, never) |
| `UV_PREVIEW` | Enable preview features |

## User-Level Config

Store persistent settings in the user configuration directory:

- Linux/macOS: `$XDG_CONFIG_HOME/uv/config.toml` or `~/.config/uv/config.toml`
- Windows: `%APPDATA%\uv\config.toml`

```toml
[global]
python-preference = "managed"
python-downloads = "automatic"
```

## Build Isolation

### Augmenting Build Dependencies

```toml
[tool.uv.extra-build-dependencies]
cchardet = ["cython"]
deepspeed = [{ requirement = "torch", match-runtime = true }]
flash-attn = [{ requirement = "torch", match-runtime = true }]
```

`match-runtime = true` ensures the build dependency matches the runtime version.

### Disabling Build Isolation

```toml
[tool.uv]
no-build-isolation-package = ["cchardet", "flash-attn"]
```

uv performs two-phase install: isolated packages first, then non-isolated.

### Providing Metadata Upfront

For packages without static metadata:

```toml
[[tool.uv.dependency-metadata]]
name = "flash-attn"
version = "2.6.3"
requires-dist = ["torch", "einops"]
```

## Cache Keys

Control when local packages are rebuilt:

```toml
[tool.uv]
# Default: pyproject.toml, setup.py, setup.cfg
cache-keys = [{ file = "pyproject.toml" }, { git = { commit = true } }]

# Include requirements.txt
cache-keys = [{ file = "pyproject.toml" }, { file = "requirements.txt" }]

# Include environment variable
cache-keys = [{ file = "pyproject.toml" }, { env = "MY_ENV_VAR" }]

# Track directory creation/removal
cache-keys = [{ file = "pyproject.toml" }, { dir = "src" }]

# Glob pattern
cache-keys = [{ file = "**/*.toml" }]
```

Setting `cache-keys` replaces defaults — include `pyproject.toml` explicitly.

## Editable Mode

```bash
uv sync                          # editable (default)
uv sync --no-editable            # non-editable (deployment)
```

Non-editable mode is intended for deployment (Docker, production) where source code changes are not expected.

## Project Environment Path

```bash
UV_PROJECT_ENVIRONMENT=/path/to/venv uv sync
```

Relative paths resolve from workspace root. Absolute paths are used as-is.

Targeting system Python:

```bash
UV_PROJECT_ENVIRONMENT=/usr/local uv sync
```

Not recommended — `uv sync` removes extraneous packages by default.

## Conflicting Dependencies

Declare incompatible groups:

```toml
[tool.uv]
conflicts = [
    [{ extra = "extra1" }, { extra = "extra2" }],
    [{ group = "group1" }, { group = "group2" }],
]
```

## Environment Filtering

Limit resolution to specific platforms:

```toml
[tool.uv]
environments = [
    "sys_platform == 'darwin'",
    "sys_platform == 'linux'",
]
```

Require specific platforms:

```toml
[tool.uv]
required-environments = [
    "sys_platform == 'darwin' and platform_machine == 'x86_64'",
]
```

## Preview Features

Enable experimental features:

```bash
uv sync --preview
UV_PREVIEW=1 uv sync
```

```toml
[tool.uv]
preview = true
```
