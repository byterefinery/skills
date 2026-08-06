# Brew Bundle and Brewfile

## Overview

`brew bundle` provides a declarative interface for managing dependencies. A `Brewfile` is a Ruby DSL file listing formulae, casks, taps, and other package types. It is the Homebrew equivalent of `package.json`, `Gemfile`, or `requirements.txt`.

## Brewfile location

- Default: `./Brewfile` (current directory)
- Global: `~/.Brewfile` (or `${XDG_CONFIG_HOME}/homebrew/Brewfile`)
- Custom: `--file=/path/to/Brewfile` or `$HOMEBREW_BUNDLE_FILE`

## Basic Brewfile syntax

```ruby
tap "user/repository"
tap "user/repository", "https://custom-git-url.git"

brew "git"
brew "postgresql@16", restart_service: true
brew "user/repository/formula"

cask "firefox"
cask "visual-studio-code"

mas "1Password", id: 443987910

vscode "editorconfig.editorconfig"
go "github.com/charmbracelet/crush"
cargo "ripgrep"
uv "mkdocs"
npm "typescript"
krew "ctx"
flatpak "com.visualstudio.code"  # Linux only
```

## Commands

### Install

```bash
brew bundle                           # Install from ./Brewfile (upgrades too)
brew bundle install                   # Same as above
brew bundle --file=/path/to/Brewfile  # Custom Brewfile
brew bundle --global                  # Use global Brewfile
brew bundle --no-upgrade              # Skip upgrading outdated deps
brew bundle --verbose                 # Print commands as they run
brew bundle --force                   # Use --force/--overwrite
brew bundle --zap                     # Use zap for cask cleanup
brew bundle --jobs=auto               # Parallel installs (CPU cores, max 4)
```

### Check

```bash
brew bundle check                     # Exit 0 if all deps satisfied
brew bundle check --verbose           # List unmet dependencies
```

Useful for scripting: `brew bundle check || brew bundle install`

### Dump

```bash
brew bundle dump                      # Save current state to ./Brewfile
brew bundle dump --global --force     # Save to global Brewfile, overwrite
brew bundle dump --formula            # Dump only formulae
brew bundle dump --cask               # Dump only casks
brew bundle dump --tap                # Dump only taps
brew bundle dump --no-describe        # Omit description comments
```

### Cleanup

```bash
brew bundle cleanup                   # Uninstall deps not in Brewfile (prompts)
brew bundle cleanup --force           # Actually remove
brew bundle cleanup --all             # Clean all supported types
brew bundle cleanup --formula         # Clean only formulae
```

### List / Add / Remove / Edit

```bash
brew bundle list                      # List formulae in Brewfile
brew bundle list --all                # List all dependency types
brew bundle list --cask               # List casks
brew bundle add wget                  # Add formula to Brewfile
brew bundle add --cask firefox        # Add cask to Brewfile
brew bundle remove wget               # Remove from Brewfile
brew bundle edit                      # Open Brewfile in $EDITOR
```

### Exec / Sh / Env

```bash
brew bundle exec <command>            # Run with Brewfile deps on PATH
brew bundle exec --check <command>    # Check deps first, then run
brew bundle exec --install <command>  # Install deps first, then run
brew bundle exec --services <command> # Start services during execution
brew bundle sh                        # Interactive shell with Brewfile env
brew bundle env                       # Print env vars for eval
```

Inside `brew bundle exec`, `HOMEBREW_INSIDE_BUNDLE` is set to `1`.

### Upgrade

```bash
brew bundle upgrade                   # Upgrade all (shorthand for install --upgrade)
brew bundle --upgrade-formulae git    # Upgrade only specific formulae
```

## Advanced Brewfile syntax

### Options

```ruby
brew "postgresql@16",
  link: true,
  args: ["with-rmtp"],
  restart_service: :changed     # :always, :changed, true
brew "postgresql@16",
  conflicts_with: ["mysql"],
  postinstall: "/opt/homebrew/opt/postgresql@16/bin/postgres -D ..."
brew "ruby", version_file: ".ruby-version"
```

### Conditional installs

```ruby
brew "gnupg" if OS.mac?
brew "glibc" if OS.linux?
cask "java" unless system "/usr/libexec/java_home", "--failfast"
```

### Cask args

```ruby
cask_args appdir: "~/Applications", require_sha: true
cask "firefox", args: { appdir: "~/my-apps/Applications" }
cask "opera", greedy: true        # Force upgrade even if auto-updated
```

### Environment variables

```ruby
ENV["SOME_VAR"] = "value"
```

Available inside `brew bundle exec` and `system` commands.

## Environment variables

| Variable | Effect |
|----------|--------|
| `HOMEBREW_BUNDLE_FILE` | Custom Brewfile path |
| `HOMEBREW_BUNDLE_NO_UPGRADE` | Skip upgrades (like `--no-upgrade`) |
| `HOMEBREW_BUNDLE_BREW_SKIP` | Space-separated formulae to skip |
| `HOMEBREW_BUNDLE_CASK_SKIP` | Space-separated casks to skip |
| `HOMEBREW_BUNDLE_TAP_SKIP` | Space-separated taps to skip |
| `HOMEBREW_BUNDLE_MAS_SKIP` | Skip Mac App Store entries |
| `HOMEBREW_BUNDLE_SERVICES` | Start services in exec/sh (like `--services`) |
| `HOMEBREW_BUNDLE_CHECK` | Check deps before exec/sh (like `--check`) |
| `HOMEBREW_BUNDLE_NO_DESCRIBE` | Omit description comments in dump |
| `HOMEBREW_BUNDLE_FORCE_INSTALL_CLEANUP` | Auto-cleanup with --global |

## No lock file

Homebrew is rolling release — there is no `Brewfile.lock`. For version stability:
- Use `brew pin <formula>` to prevent upgrades
- Use `--no-upgrade` or `HOMEBREW_BUNDLE_NO_UPGRADE=1`
- Use `brew version-install` for specific older versions
