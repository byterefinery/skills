# Integrations

## Pre-commit

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.16.0
    hooks:
      - id: ruff-check
        args: [--fix]
      - id: ruff-format
```

For Markdown formatting in pre-commit, add `types_or`:

```yaml
      - id: ruff-format
        types_or: [python, pyi, jupyter, markdown]
```

## Editor Extensions

### VS Code

Install the official [Ruff extension](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff). Key settings:

```json
{
  "ruff.lint.enabled": true,
  "ruff.format.enabled": true,
  "ruff.lint.run": "onType",
  "ruff.format.args": [],
  "ruff.lint.args": []
}
```

For notebooks, use `notebook.source.*` code actions, not `source.*`:

```json
{
  "notebook.codeActionsOnSave": {
    "notebook.source.organizeImports": "explicit",
    "notebook.source.fixAll": "explicit"
  }
}
```

### Other editors

Ruff provides a language server (`ruff server`) for LSP support. Check [editor setup docs](https://docs.astral.sh/ruff/editors/setup/) for Neovim, Helix, Emacs, Sublime Text, Vim, and more.

## GitHub Actions

```yaml
name: Ruff
on: [push, pull_request]
jobs:
  ruff:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/ruff-action@v3
```

The `ruff-action` handles installation and runs both check and format by default. Configure via inputs:

```yaml
- uses: astral-sh/ruff-action@v3
  with:
    args: "--select E,F --ignore E501"
```

## CI/CD Patterns

### Check-only (no auto-fix)

```yaml
- run: ruff check .
- run: ruff format --check .
```

### Auto-fix PRs

```yaml
- run: ruff check --fix .
- run: ruff format .
- run: git diff --exit-code  # fails if changes remain
```

### With GitHub annotations

```bash
ruff check --output-format github
```

### With GitLab CI

```bash
ruff check --output-format gitlab > gl-report.json
```

## Docker

Official image: `ghcr.io/astral-sh/ruff`

```bash
docker run -v .:/io --rm ghcr.io/astral-sh/ruff check
docker run -v .:/io --rm ghcr.io/astral-sh/ruff:0.16.0 format
```

For Podman on SELinux:

```bash
docker run -v .:/io:Z --rm ghcr.io/astral-sh/ruff check
```

## Shell Completion

```bash
# Bash
echo 'eval "$(ruff generate-shell-completion bash)"' >> ~/.bashrc

# Zsh
echo 'eval "$(ruff generate-shell-completion zsh)"' >> ~/.zshrc

# Fish
echo 'ruff generate-shell-completion fish | source' > ~/.config/fish/completions/ruff.fish

# PowerShell
Add-Content -Path $PROFILE -Value '(& ruff generate-shell-completion powershell) | Out-String | Invoke-Expression'
```

Supported shells: bash, zsh, fish, elvish, powershell, fig.

## Installation Methods

```bash
# uv (recommended)
uv tool install ruff@latest
uv add --dev ruff

# pip
pip install ruff

# pipx
pipx install ruff

# Standalone installer (macOS/Linux)
curl -LsSf https://astral.sh/ruff/install.sh | sh
curl -LsSf https://astral.sh/ruff/0.16.0/install.sh | sh   # specific version

# Homebrew
brew install ruff

# Conda
conda install -c conda-forge ruff

# Arch Linux
pacman -S ruff

# Alpine
apk add ruff

# openSUSE
zypper install python3-ruff
```

## uv Integration

```bash
uvx ruff check              # run without installing
uv run ruff check           # run from project dependency
uv tool install ruff@0.16.0 # pin specific version
```
