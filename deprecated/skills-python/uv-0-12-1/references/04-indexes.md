# Package indexes — private indexes, authentication, strategies

## Defining indexes

Add `[[tool.uv.index]]` entries to `pyproject.toml`:

```toml
[[tool.uv.index]]
name = "pytorch"
url = "https://download.pytorch.org/whl/cpu"
```

Indexes are consulted in order of definition. PyPI is always the default (lowest priority) unless displaced.

### Default index

Replace PyPI as default:

```toml
[[tool.uv.index]]
name = "internal"
url = "https://internal.example.com/simple"
default = true
```

### Explicit indexes

Only usable by packages explicitly pinned to them:

```toml
[tool.uv.sources]
torch = { index = "pytorch" }

[[tool.uv.index]]
name = "pytorch"
url = "https://download.pytorch.org/whl/cpu"
explicit = true
```

### Command-line indexes

```bash
uv lock --index pytorch=https://download.pytorch.org/whl/cpu
UV_INDEX=pytorch=https://download.pytorch.org/whl/cpu uv lock
uv lock --default-index https://internal.example.com/simple
```

## Pinning packages to indexes

```toml
[tool.uv.sources]
torch = { index = "pytorch" }

[[tool.uv.index]]
name = "pytorch"
url = "https://download.pytorch.org/whl/cpu"
```

Platform-specific index selection:

```toml
[tool.uv.sources]
torch = [
  { index = "torch-cpu", marker = "platform_system == 'Darwin'" },
  { index = "torch-gpu", marker = "platform_system == 'Linux'" },
]

[[tool.uv.index]]
name = "torch-cpu"
url = "https://download.pytorch.org/whl/cpu"
explicit = true

[[tool.uv.index]]
name = "torch-gpu"
url = "https://download.pytorch.org/whl/cu130"
explicit = true
```

Extra-specific index selection:

```toml
[project.optional-dependencies]
cpu = ["torch"]
gpu = ["torch"]

[tool.uv.sources]
torch = [
  { index = "torch-cpu", extra = "cpu" },
  { index = "torch-gpu", extra = "gpu" },
]
```

## Index strategies

```bash
uv lock --index-strategy first-index       # default: stop at first index with the package
uv lock --index-strategy unsafe-first-match  # prefer first index even if newer elsewhere
uv lock --index-strategy unsafe-best-match   # pick best version across all indexes
```

Or via environment: `UV_INDEX_STRATEGY=unsafe-best-match`

Default `first-index` prevents dependency confusion attacks. `unsafe-best-match` is closest to pip behavior but exposes users to such attacks.

## Authentication

### Environment variables

For an index named `internal-proxy`:

```bash
export UV_INDEX_INTERNAL_PROXY_USERNAME=public
export UV_INDEX_INTERNAL_PROXY_PASSWORD=koala
```

Name is uppercased with non-alphanumeric chars replaced by underscores.

### Credentials in URL

```toml
[[tool.uv.index]]
name = "internal"
url = "https://public:koala@pypi-proxy.corp.dev/simple"
```

Credentials are never stored in `uv.lock`.

### Credential providers

uv supports netrc and keyring discovery. Configure per-index:

```toml
[[tool.uv.index]]
name = "example"
url = "https://example.com/simple"
authenticate = "always"    # always search for credentials
# or
authenticate = "never"     # never search for credentials
```

### Ignoring error codes

```toml
[[tool.uv.index]]
name = "private-index"
url = "https://private-index.com/simple"
authenticate = "always"
ignore-error-codes = [403]
```

uv always continues on 404. It stops on 401/403 by default (except for pytorch index 403s).

## Cache control

Override cache headers per-index:

```toml
[[tool.uv.index]]
name = "example"
url = "https://example.com/simple"
cache-control = { api = "max-age=600", files = "max-age=365000000, immutable" }
```

- `api` — Simple API (metadata) caching
- `files` — artifact (wheel/sdist) caching

## Flat indexes

Directories or HTML pages with flat lists of wheels/sdists (pip's `--find-links`):

```toml
[[tool.uv.index]]
name = "local-wheels"
url = "/path/to/directory"
format = "flat"
```

## Hash algorithm

```toml
[tool.uv]
preview-features = ["index-hash-algorithm"]

[[tool.uv.index]]
name = "private-index"
url = "https://private-index.com/simple"
hash-algorithm = "sha256"
```

## Index-specific exclude-newer

```toml
[[tool.uv.index]]
name = "internal"
url = "https://internal.example.com/simple"
exclude-newer = "7 days"
# or
exclude-newer = false    # disable cutoff for this index
```

## Pip-style options

```bash
uv pip install --index-url https://pypi.org/simple/ flask
uv pip install --extra-index-url https://test.pypi.org/simple/ flask
```

These map to `--default-index` and `--index` respectively.

## Provider guides

For specific providers, see the integration guides: Azure Artifacts, Google Artifact Registry, AWS CodeArtifact, JFrog Artifactory, GitLab Package Registry.
