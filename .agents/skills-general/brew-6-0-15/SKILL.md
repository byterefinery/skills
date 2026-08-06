---
name: brew-6-0-15
description: Homebrew 6.0.15 — the package manager for macOS, Linux, and WSL. Use when the user needs to install, manage, upgrade, or remove software packages (formulae and casks), manage taps, use brew bundle/Brewfile for declarative dependency management, run background services with brew services, search/query installed packages, pin versions, or troubleshoot Homebrew installations. Covers formulae, casks, bottles, taps, tap trust, Brewfiles, services, and all brew 6.0.15 commands.
metadata:
  tags:
    - package-manager
    - cli
    - macos
    - linux
    - devops
---

# brew 6.0.15

## Overview

Homebrew is the most popular package manager for macOS and a widely-used option on Linux. It installs software from pre-built bottles (binary packages) or builds from source. Version 6.0.15 introduces tap trust as the default security model — non-official taps require explicit trust before their formulae, casks, or commands can be loaded.

Homebrew installs to:
- macOS ARM (Apple Silicon): `/opt/homebrew`
- macOS Intel: `/usr/local`
- Linux: `/home/linuxbrew/.linuxbrew`

Two package types: **formulae** (built from source or poured from bottles) and **casks** (pre-compiled binaries, typically GUI apps on macOS).

## Usage

### Essential commands

```bash
brew install <formula|cask>       # Install a package
brew uninstall <formula|cask>     # Remove a package
brew upgrade                      # Upgrade all outdated packages
brew upgrade <formula|cask>       # Upgrade specific package
brew list                         # List installed packages
brew search <text>                # Search for packages
brew info <formula|cask>          # Show package info
brew doctor                       # Check system for problems
brew update                       # Update Homebrew and taps
brew cleanup                      # Remove old versions and cached downloads
```

### Formulae vs casks

```bash
brew install git          # formula (built from source or bottle)
brew install --cask firefox  # cask (pre-compiled binary)
brew install --cask visual-studio-code
```

### Managing taps (third-party repositories)

```bash
brew tap user/repository          # Add a tap (GitHub shorthand)
brew tap user/repo <URL>          # Add from any Git URL
brew tap                          # List tapped repos
brew untap user/repository        # Remove a tap
```

### Tap trust (new in 6.0)

Non-official taps require explicit trust. Install by fully qualified name to trust just that item:

```bash
brew install user/repository/formula    # trusts just this formula
brew trust --formula user/repo/formula  # trust explicitly
brew trust user/repository              # trust entire tap
```

### Services (background daemons)

```bash
brew services start <formula>    # Start and register at login
brew services stop <formula>     # Stop and unregister
brew services restart <formula>  # Restart
brew services list               # Show managed services
brew services run <formula>      # Run without registering
```

### Brewfile (declarative dependencies)

```bash
brew bundle dump                 # Save current state to Brewfile
brew bundle install              # Install from Brewfile
brew bundle check                # Check if Brewfile is satisfied
brew bundle cleanup --force      # Remove packages not in Brewfile
brew bundle exec <command>       # Run command with Brewfile deps on PATH
```

### Version control

```bash
brew pin <formula>               # Prevent upgrade
brew unpin <formula>             # Allow upgrade
brew outdated                    # List outdated packages
```

### Querying

```bash
brew deps <formula>              # Show dependencies
brew deps --tree <formula>       # Show dependency tree
brew uses <formula>              # Show reverse dependencies
brew info --json=v1 <formula>    # JSON output for scripting
brew which-formula <command>     # Find which formula provides a command
```

### Running commands with dependencies

```bash
brew exec --formulae=jq,yq -- ./script.sh   # Install deps, run with PATH
# Shebang form (systems with env -S):
#!/usr/bin/env -S brew exec --formulae=jq,yq --
```

### Installing specific versions

```bash
brew install gcc@13                    # Versioned formula (if available)
brew version-install automake@1.12     # Extract older version into personal tap
```

## Gotchas

- **Run `brew update` before filing issues** — Homebrew requires current metadata. Always update first, then retry the failing command.
- **Tap trust is required by default** — since Homebrew 6.0, non-official taps need explicit trust. Use `brew install user/repo/formula` (fully qualified) to trust just one item, or `brew trust` for whole taps. Disabling with `HOMEBREW_NO_REQUIRE_TAP_TRUST=1` is not recommended.
- **`brew install` upgrades if outdated** — unless `HOMEBREW_NO_INSTALL_UPGRADE=1` is set, `brew install foo` will upgrade an already-installed but outdated `foo`. Use `brew upgrade` explicitly or set the env var.
- **`keg-only` formulae are not symlinked** — some formulae (e.g., `openssl`, `openjdk`) are keg-only to avoid conflicts. Access via `brew --prefix <formula>` or use `brew shellenv`/`brew exec`. Do not `brew link --force` keg-only formulae unless you understand the conflict risk.
- **`HOMEBREW_NO_INSTALL_FROM_API=1` needed for local formula editing** — when developing formulae locally, set this env var so brew reads from the tapped repo instead of the JSON API.
- **`brew bundle` has no lock file** — Homebrew is rolling release. There is no `Brewfile.lock`. Use `brew pin` for version stability, `--no-upgrade` flag, or `HOMEBREW_BUNDLE_NO_UPGRADE=1` env var.
- **`--zap` removes all cask files** — `brew uninstall --zap --cask <name>` may remove shared files between applications. Use `brew uninstall --cask` (without `--zap`) for safer removal.
- **`brew doctor` warnings are informational** — they help with debugging but do not mean your system is broken. Ignore warnings unrelated to your issue.
- **`brew cleanup` removes old versions** — runs automatically after installs (every 30 days for all). Use `brew cleanup --dry-run` to preview. Set `HOMEBREW_CLEANUP_MAX_AGE_DAYS` to control download retention (default 120 days).
- **Formulae are downloaded as JSON** — since Homebrew 4.0, formulae come from `formulae.brew.sh` API, not Git. Local taps need `HOMEBREW_NO_INSTALL_FROM_API=1` to use.
- **`brew services` user vs system** — without `sudo`, services run per-user (launch agents / user systemd). With `sudo`, they run system-wide (launch daemons / system systemd). Environment files go to `~/.homebrew/services/<formula>.env`.
- **`brew shellenv` for PATH setup** — add `eval "$(brew shellenv)"` to your shell config. It produces no output when Homebrew paths are already first in PATH (idempotent).
- **`brew update-reset` destroys local changes** — it hard-resets Homebrew and all taps to `origin/HEAD`. Only use when stuck, not as routine maintenance.

## References

- [01-terminology](references/01-terminology.md) — formula, cask, keg, bottle, tap, prefix, Cellar
- [02-install-uninstall](references/02-install-uninstall.md) — install, uninstall, upgrade, pin, cleanup options
- [03-taps-trust](references/03-taps-trust.md) — tapping repos, tap trust model, managing trust
- [04-bundle](references/04-bundle.md) — Brewfile format, bundle subcommands, advanced Brewfile syntax
- [05-services](references/05-services.md) — brew services lifecycle, env files, user vs system
- [06-search-query](references/06-search-query.md) — search, info, deps, linkage, JSON output, formulae.brew.sh API
- [07-advanced](references/07-advanced.md) — exec, version-install, environment variables, troubleshooting, developer commands
