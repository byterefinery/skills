# CI/CD Integration

## GitHub Actions

### Using ruff-action

```yaml
name: Ruff
on: [push, pull_request]
jobs:
  ruff:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: chartboost/ruff-action@v1
        with:
          version: '0.4.10'
```

### Manual installation

```yaml
name: Ruff
on: [push, pull_request]
jobs:
  lint-and-format:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install Ruff
        run: pip install ruff==0.4.10
      - name: Lint
        run: ruff check .
      - name: Format check
        run: ruff format --check .
```

### With caching

```yaml
      - name: Cache Ruff
        uses: actions/cache@v4
        with:
          path: .ruff_cache
          key: ruff-${{ runner.os }}-${{ hashFiles('**/pyproject.toml') }}
      - name: Lint
        run: ruff check .
```

## GitLab CI

```yaml
ruff-lint:
  image: python:3.11-slim
  before_script:
    - pip install ruff==0.4.10
  script:
    - ruff check .
    - ruff format --check .
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == "main"
```

## pre-commit

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.10
    hooks:
      # Linter
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
        # Optional: limit to specific files
        # types: [python]
        # exclude: ^migrations/

      # Formatter
      - id: ruff-format
```

### pre-commit tips

- `--exit-non-zero-on-fix` causes pre-commit to re-run if fixes were applied (ensures
  all fixable issues are resolved before commit)
- pre-commit passes files directly, bypassing file discovery — use pre-commit's
  `exclude` key for filtering, not Ruff's `exclude` config
- Use `additional_dependencies` if you need a specific Ruff version different from
  the repo tag

## tox

```ini
[tox]
envlist = lint

[testenv:lint]
skip_install = true
deps = ruff==0.4.10
commands =
    ruff check {posargs:.}
    ruff format --check {posargs:.}
```

## Makefile

```makefile
.PHONY: lint format lint-fix

lint:
	ruff check .
	ruff format --check .

format:
	ruff format .

lint-fix:
	ruff check --fix .
	ruff format .
```

## VS Code settings

```json
{
  "ruff.path": ["venv", "bin", "ruff"],
  "ruff.formatting": true,
  "ruff.linting": true,
  "ruff.args": [],
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.ruff": "explicit"
  }
}
```

## Neovim (with lspconfig)

```lua
require("lspconfig").ruff_lsp.setup({
  on_attach = function(client, bufnr)
    vim.api.nvim_buf_set_option(bufnr, "omnifunc", "v:lua.vim.lsp.omnifunc")
  end,
  settings = {
    ["ruff-lsp"] = {
      logLevel = "warning",
      server = {
        installationPath = "/path/to/venv/bin/ruff",
      },
    },
  },
})
```

## Docker

```dockerfile
FROM python:3.11-slim
RUN pip install --no-cache-dir ruff==0.4.10
WORKDIR /app
COPY . .
RUN ruff check . && ruff format --check .
```

## Performance tips for CI

- Use `--no-cache` only when needed; caching speeds up repeated runs
- Run `ruff check` and `ruff format --check` in parallel if possible
- Use `--show-files` to verify Ruff is checking the expected files
- For large repos, consider `ruff check --output-format github` for annotated PR comments
