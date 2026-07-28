# Indexes and Authentication

## Package Indexes

uv uses PyPI by default. Configure alternative indexes via `[[tool.uv.index]]` or `--index`.

### Defining Indexes

```toml
[[tool.uv.index]]
name = "pytorch"
url = "https://download.pytorch.org/whl/cpu"

[[tool.uv.index]]
name = "internal"
url = "https://pypi-proxy.corp.dev/simple"
```

Command-line equivalents:

```bash
uv lock --index pytorch=https://download.pytorch.org/whl/cpu
uv lock --default-index https://pypi-proxy.corp.dev/simple
UV_INDEX=pytorch=https://... uv lock
```

### Default Index

PyPI is the default (lowest priority). Replace it:

```toml
[[tool.uv.index]]
name = "internal"
url = "https://pypi-proxy.corp.dev/simple"
default = true
```

Or via CLI: `--default-index https://...`

### Explicit Indexes

Only usable by packages explicitly pinned to them:

```toml
[tool.uv.sources]
torch = { index = "pytorch" }

[[tool.uv.index]]
name = "pytorch"
url = "https://download.pytorch.org/whl/cpu"
explicit = true
```

### Pinning Packages to Indexes

```toml
[tool.uv.sources]
torch = { index = "pytorch" }

[[tool.uv.index]]
name = "pytorch"
url = "https://download.pytorch.org/whl/cpu"
```

Platform-specific pinning:

```toml
[tool.uv.sources]
torch = [
  { index = "pytorch-cpu", marker = "sys_platform == 'darwin'" },
  { index = "pytorch-cu132", marker = "sys_platform != 'darwin'" },
]

[[tool.uv.index]]
name = "pytorch-cpu"
url = "https://download.pytorch.org/whl/cpu"

[[tool.uv.index]]
name = "pytorch-cu132"
url = "https://download.pytorch.org/whl/cu132"
```

### Index Strategy

```bash
uv lock --index-strategy first-index       # default: stop at first index with package
uv lock --index-strategy unsafe-first-match # prefer first index, allow newer from others
uv lock --index-strategy unsafe-best-match  # combine all indexes (closest to pip)
```

`first-index` prevents dependency confusion attacks. `unsafe-best-match` is closest to pip's behavior but exposes users to such attacks.

### Flat Indexes

Directories or HTML pages with flat lists of wheels/sdists (pip's `--find-links`):

```toml
[[tool.uv.index]]
name = "local-wheels"
url = "/path/to/wheel/directory"
format = "flat"
```

Flat indexes cache files by name. Replacing a file under the same name requires `--refresh` or `uv cache clean`.

### Legacy pip Options

```bash
uv pip install --index-url https://...        # maps to --default-index
uv pip install --extra-index-url https://...  # maps to --index
```

## Authentication

### Environment Variables

For an index named `internal-proxy`:

```bash
export UV_INDEX_INTERNAL_PROXY_USERNAME=public
export UV_INDEX_INTERNAL_PROXY_PASSWORD=koala
```

Index names are uppercased with non-alphanumeric characters replaced by underscores.

### Embedded Credentials

```toml
[[tool.uv.index]]
name = "internal"
url = "https://public:koala@pypi-proxy.corp.dev/simple"
```

Credentials are never stored in `uv.lock`.

### Credential Providers

uv discovers credentials from:

1. Environment variables (`UV_INDEX_<NAME>_USERNAME/PASSWORD`)
2. `.netrc` file
3. Keyring

### Authenticate Setting

```toml
[[tool.uv.index]]
name = "example"
url = "https://example.com/simple"
authenticate = "always"     # always search for credentials
# authenticate = "never"    # never search for credentials
# authenticate = "auto"     # default: try unauthenticated first
```

Use `always` for indexes that reject unauthenticated requests (e.g., GitLab).

### Ignoring Error Codes

```toml
[[tool.uv.index]]
name = "private-index"
url = "https://private-index.com/simple"
authenticate = "always"
ignore-error-codes = [403]
```

uv always continues on `404 Not Found`. By default, `401` and `403` stop resolution.

### Disabling Authentication

```toml
[[tool.uv.index]]
name = "example"
url = "https://example.com/simple"
authenticate = "never"
```

Prevents credential leakage to untrusted indexes.

### Custom Cache Control

```toml
[[tool.uv.index]]
name = "example"
url = "https://example.com/simple"
cache-control = { api = "max-age=600", files = "max-age=365000000, immutable" }
```

Override HTTP cache-control headers. Recommended to follow PyPI's approach.

### Index-Specific exclude-newer

```toml
[[tool.uv.index]]
name = "internal"
url = "https://internal.example.com/simple"
exclude-newer = "7 days"
# exclude-newer = false     # disable for this index
```

## Git Authentication

```bash
# Via environment variables
export GIT_TOKEN=ghp_...
uv pip install "git+https://oauth2:$GIT_TOKEN@github.com/org/repo"

# Via SSH (requires ssh-agent)
uv pip install "git+ssh://git@github.com/org/repo"
```

## Provider-Specific Guides

- **Azure Artifacts** — use `UV_INDEX_<NAME>_USERNAME` with `azuredevops` and PAT token
- **Google Artifact Registry** — use `gcloud auth configure-docker` or service account keys
- **AWS CodeArtifact** — use `aws codeartifact get-authorization-token` and `--index-url`
- **JFrog Artifactory** — use environment variables or `.netrc`
