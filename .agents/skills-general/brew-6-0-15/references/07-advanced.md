# Advanced Topics

## brew exec

Run commands with Homebrew formulae on PATH without manual setup:

```bash
brew exec --formulae=jq,yq -- ./script.sh
brew exec <command>                     # Auto-find and install formula providing command
brew exec --sandbox=. -- ./script.sh    # Run in sandbox
brew exec --deny-network -- ./script.sh # Deny network access
```

Shebang form (systems with `env -S`):
```bash
#!/usr/bin/env -S brew exec --formulae=jq,yq --
```

## Version management

### Pin specific versions

```bash
brew pin <formula>                      # Prevent upgrade
brew unpin <formula>                    # Allow upgrade
```

### Install older versions

```bash
brew install gcc@13                     # Versioned formula (if in homebrew/core)
brew version-install automake@1.12      # Extract into personal tap + install
brew extract <formula> <version> <tap>  # Lower-level extraction
```

`brew version-install` creates a `user/versions` tap automatically. Extracted formulae may use deprecated syntax and are your responsibility to maintain.

### Version locking strategies

| Method | Scope | Notes |
|--------|-------|-------|
| `brew pin` | Single formula | Simplest; no security updates while pinned |
| `HOMEBREW_NO_AUTO_UPDATE=1` | All metadata | Homebrew only learns new versions on manual `brew update` |
| `HOMEBREW_NO_INSTALL_UPGRADE=1` | Install command | `brew install` won't upgrade already-installed packages |
| `HOMEBREW_BUNDLE_NO_UPGRADE=1` | Bundle command | `brew bundle` skips upgrades |
| `HOMEBREW_NO_INSTALLED_DEPENDENTS_CHECK=1` | Post-install | Skips cascading upgrades/reinstalls |
| `brew version-install` | Single formula | Extract into personal tap; you maintain it |
| `brew extract` | Single formula | Manual extraction; you maintain it |

## Environment variables

### Core paths

```bash
brew --prefix                    # Homebrew install path
brew --cellar                    # Cellar directory
brew --cache                     # Download cache directory
brew --caskroom                  # Caskroom directory
brew --repository homebrew/core  # Git repo path for a tap
brew --taps                      # Taps directory path
```

### Build and install behavior

| Variable | Effect |
|----------|--------|
| `HOMEBREW_NO_AUTO_UPDATE=1` | Skip auto-update before install/upgrade |
| `HOMEBREW_NO_INSTALL_UPGRADE=1` | Don't upgrade on `brew install` |
| `HOMEBREW_NO_INSTALL_CLEANUP=1` | Skip post-install cleanup |
| `HOMEBREW_NO_INSTALLED_DEPENDENTS_CHECK=1` | Skip dependent checks |
| `HOMEBREW_NO_INSTALL_FROM_API=1` | Read formulae from Git, not JSON API |
| `HOMEBREW_NO_ASK=1` | Skip confirmation prompts |
| `HOMEBREW_NO_EMOJI=1` | Hide emoji output |
| `HOMEBREW_INSTALL_BADGE="☕"` | Replace beer mug emoji |
| `HOMEBREW_DISPLAY_INSTALL_TIMES=1` | Show install times |
| `HOMEBREW_NO_ANALYTICS=1` | Disable anonymous analytics |
| `HOMEBREW_NO_GITHUB_API=1` | Skip GitHub API calls |
| `HOMEBREW_DEVELOPER=1` | Enable developer mode |
| `HOMEBREW_UPGRADE_GREEDY=1` | Include auto-updating casks in upgrades |
| `HOMEBREW_NO_UPGRADE_QUIT_CASKS=1` | Don't quit running casks on upgrade |

### Network and caching

| Variable | Effect |
|----------|--------|
| `HOMEBREW_CACHE` | Custom cache directory |
| `HOMEBREW_CLEANUP_MAX_AGE_DAYS` | Download retention (default 120) |
| `HOMEBREW_API_DOMAIN` | Custom JSON API domain |
| `HOMEBREW_ARTIFACT_DOMAIN` | Custom bottle/artifact domain |
| `HOMEBREW_BREW_GIT_REMOTE` | Custom Homebrew/brew Git remote |
| `HTTP_PROXY` / `HTTPS_PROXY` | Proxy for downloads |

### Tap trust

| Variable | Effect |
|----------|--------|
| `HOMEBREW_REQUIRE_TAP_TRUST=1` | Require tap trust (default) |
| `HOMEBREW_NO_REQUIRE_TAP_TRUST=1` | Disable tap trust (not recommended) |

## Sandbox

```bash
brew sandbox-exec . -- make test        # Run in sandbox, allow writes to .
brew sandbox-exec --deny-network . -- ./script.sh  # Sandbox + no network
```

## Troubleshooting

### Standard diagnostic workflow

1. `brew update` — update Homebrew
2. `brew update` — run again (first update may leave stale state)
3. `brew doctor` — check for problems, read all warnings
4. Fix warnings related to the issue
5. Retry the original command

### Collecting diagnostic info

```bash
brew config                              # Homebrew and system configuration
brew doctor                              # System health check
brew gist-logs <formula>                 # Upload build logs to Gist
brew gist-logs --new-issue <formula>     # Create Gist + open issue
brew gist-logs --private <formula>       # Private Gist
```

### Common issues

- **Permission errors**: Homebrew should not need `sudo` for installs. Run `brew doctor` and follow permission fixes.
- **Xcode CLT missing**: `xcode-select --install` on macOS.
- **Stuck updates**: `brew update-reset` hard-resets to origin/HEAD (destroys local changes).
- **Conflicting formulae**: Use `brew unlink <conflict>` to temporarily disable, or `brew link --overwrite`.
- **Build failures**: `brew install --debug <formula>` opens IRB in the build directory.
- **Keg-only not on PATH**: Use `brew shellenv` or access via `$(brew --prefix <formula>)`.

## Developer commands

```bash
brew audit <formula>                     # Check formula style
brew audit --strict <formula>            # Strict audit
brew audit --new <formula>               # Audit for new formulae
brew test <formula>                      # Run formula tests
brew create <URL>                        # Scaffold new formula from URL
brew edit <formula>                      # Edit formula in $EDITOR
brew irb                                 # Interactive Ruby shell
brew irb --examples                      # Show example commands
brew fetch <formula>                     # Download bottle/source
brew cat <formula>                       # Show formula source
brew readall                             # Load all formulae (debugging)
brew readall --syntax                    # Syntax-check all Ruby files
brew developer on                        # Enable developer mode
brew developer off                       # Disable developer mode
```

## Shell integration

```bash
eval "$(brew shellenv)"                  # Add Homebrew to PATH/MANPATH/INFOPATH
eval "$(brew shellenv zsh)"              # Explicit shell
brew completions link                    # Link shell completions
brew completions unlink                  # Unlink completions
brew command-not-found-init              # Setup command-not-found hook
```

Cross-platform dotfiles:
```bash
command -v brew || export PATH="/opt/homebrew/bin:/home/linuxbrew/.linuxbrew/bin:/usr/local/bin"
command -v brew && eval "$(brew shellenv)"
```

## Sync commands

```bash
brew pyenv-sync                          # Sync Python versions to ~/.pyenv/versions
brew rbenv-sync                          # Sync Ruby versions to ~/.rbenv/versions
brew nodenv-sync                         # Sync NodeJS versions to ~/.nodenv/versions
```

## Tab editing

```bash
brew tab --installed-on-request <formula>    # Mark as manually installed
brew tab --no-installed-on-request <formula> # Mark as dependency
```

Controls whether `brew autoremove` considers a formula removable.

## Vulnerability scanning

```bash
brew vulns                               # Check all installed formulae
brew vulns <formula>                     # Check specific formula
brew vulns --deps <formula>              # Include dependencies
brew vulns --severity=high               # Filter by severity
brew vulns --json                        # JSON output
```

Uses the OSV.dev database for vulnerability data.

## MCP Server

```bash
brew mcp-server                          # Start Homebrew MCP server
brew mcp-server --debug                  # With debug logging
```

Enables Homebrew integration with AI agents via Model Context Protocol.
