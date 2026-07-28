# Build and Publish

## Building distributions

```bash
uv build                           # build sdist + wheel
uv build --sdist                   # source distribution only
uv build --wheel                   # wheel only
uv build --out-dir dist/           # output directory (default: dist/)
uv build /path/to/project          # build specific project
```

Output:

```
dist/
├── my_package-0.1.0-py3-none-any.whl
└── my_package-0.1.0.tar.gz
```

### Build system

Projects need a `[build-system]` in `pyproject.toml`:

```toml
[build-system]
requires = ["uv_build>=0.12.0,<0.13"]
build-backend = "uv_build"
```

Alternative build backends (hatchling, setuptools, flit) are also supported.

### Build isolation

uv builds in an isolated environment by default. Dependencies from `build-system.requires` are installed into a temporary build environment.

```bash
uv build --no-isolation            # use current environment for build
```

## Publishing

```bash
uv publish                         # publish to PyPI
uv publish --token $UV_PUBLISH_TOKEN
uv publish --index-url https://test.pypi.org/legacy/  # TestPyPI
uv publish --dry-run               # validate without uploading
```

### Authentication

```bash
# Environment variable
export UV_PUBLISH_TOKEN="pypi-..."

# Or via --token flag
uv publish --token "pypi-..."

# Or via keyring (if configured)
uv publish
```

### Distribution validation

Since 0.12.0, `uv publish` skips distributions with non-normalized filenames. Wheel names must use normalized package names and versions (e.g., `example-1.1.0-py3-none-any.whl`, not `example-1.01.0-...`).

### Building before publishing

```bash
uv build && uv publish
```

Or in one step (build happens automatically if no dist/ exists):

```bash
uv publish
```

## Version management

```bash
uv version                         # show package version (from pyproject.toml)
uv version --short                 # version only, no package name
uv version --output-format json    # JSON output
```

To update the version, edit `pyproject.toml` directly:

```toml
[project]
version = "0.2.0"
```

## File-based publishing

Publish specific files:

```bash
uv publish dist/my_package-0.1.0-py3-none-any.whl
uv publish dist/my_package-0.1.0.tar.gz
```

## Repository configuration

```toml
[tool.uv.publish]
url = "https://custom-index.example.com/simple/"
username = "token"
password = "pypi-..."
```

Or via CLI:

```bash
uv publish --url https://custom-index.example.com/simple/
```
