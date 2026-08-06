# Install, Uninstall, Upgrade, Pin, Cleanup

## Install

```bash
brew install <formula>              # Install formula (bottle preferred)
brew install --cask <cask>          # Install cask
brew install --build-from-source <formula>   # Build from source
brew install --force-bottle <formula>        # Force bottle even if not ideal
brew install --HEAD <formula>       # Install HEAD (development) version
brew install --skip-link <formula>  # Install without symlinking
brew install --only-dependencies <formula>   # Install deps only
brew install --overwrite <formula>  # Delete conflicting files during linking
brew install --verbose <formula>    # Show verification and post-install steps
brew install --dry-run <formula>    # Show what would be installed
```

### Install options

- `--build-from-source` / `-s` — compile from source even if bottle exists
- `--force-bottle` — use bottle even for older macOS versions
- `--HEAD` — install development version (if formula defines it)
- `--fetch-HEAD` — check if HEAD installation is outdated
- `--keep-tmp` — retain temporary build files
- `--debug-symbols` — generate debug symbols, retain source in cache
- `--cc=<compiler>` — use specific compiler (e.g., `--cc=gcc-13`)
- `--interactive` / `-i` — download, patch, open shell for manual build
- `--debug` / `-d` — open IRB debugging session on failure
- `--display-times` — print install times per package
- `--no-ask` / `-y` — skip confirmation prompts

### Cask-specific install options

- `--adopt` — adopt existing identical artifacts
- `--require-sha` — require checksum for all casks
- `--skip-cask-deps` — skip cask dependencies
- `--[no-]binaries` — control linking of helper executables (default: enabled)

## Uninstall

```bash
brew uninstall <formula>            # Uninstall formula
brew uninstall --cask <cask>        # Uninstall cask
brew uninstall --zap --cask <cask>  # Remove all cask files (may remove shared files)
brew uninstall --force <formula>    # Delete all installed versions
brew uninstall --ignore-dependencies <formula>  # Ignore dependent formulae
```

## Upgrade

```bash
brew upgrade                        # Upgrade all outdated packages
brew upgrade <formula>              # Upgrade specific package
brew upgrade --formula              # Upgrade only formulae
brew upgrade --cask                 # Upgrade only casks
brew upgrade --greedy               # Include auto-updating casks
brew upgrade --dry-run              # Show what would be upgraded
```

### Upgrade options

- `--greedy` / `-g` — include `version :latest` and `auto_updates true` casks
- `--greedy-latest` — include `version :latest` casks
- `--greedy-auto-updates` — include `auto_updates true` casks
- `--no-quit` — prevent running cask apps from being quit during upgrade
- `--minimum-version` — only upgrade if below given version

## Pin / Unpin

```bash
brew pin <formula>                  # Prevent upgrade
brew unpin <formula>                # Allow upgrade
brew list --pinned                  # List pinned packages
```

Pinned formulae are skipped by `brew upgrade`. Pinned casks with `auto_updates true` may still self-update outside Homebrew.

## Reinstall

```bash
brew reinstall <formula>            # Uninstall + reinstall with same options
brew reinstall --cask <cask>        # Reinstall cask
brew reinstall --zap --cask <cask>  # Reinstall cask, removing all old files
```

## Cleanup

```bash
brew cleanup                        # Remove old versions and stale downloads
brew cleanup <formula>              # Cleanup specific formula
brew cleanup --dry-run              # Show what would be removed
brew cleanup --scrub                # Scrub cache including latest versions
brew cleanup --prune-prefix         # Only prune symlinks from prefix
brew autoremove                     # Remove orphaned dependencies
brew autoremove --dry-run           # Show what would be autoremoved
```

Cleanup runs automatically after installs. Full cleanup runs every 30 days. Set `HOMEBREW_CLEANUP_MAX_AGE_DAYS` to control download retention (default 120 days).

## Link / Unlink

```bash
brew link <formula>                 # Symlink keg into prefix
brew link --overwrite <formula>     # Delete conflicting files
brew link --force <formula>         # Allow keg-only formulae to link
brew unlink <formula>               # Remove symlinks from prefix
brew unlink --dry-run <formula>     # Show what would be unlinked
```

## Postinstall

```bash
brew postinstall <formula>          # Rerun post-install steps
```

## Migrate

```bash
brew migrate <old_name>             # Migrate renamed packages
brew migrate --dry-run <old_name>   # Show what would be migrated
```
