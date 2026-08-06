# Terminology

## Core terms

| Term | Description | Example |
|------|-------------|---------|
| **formula** | Package definition that builds from upstream sources | `git`, `python`, `openssl@3` |
| **cask** | Package definition for pre-compiled binaries (typically GUI apps) | `firefox`, `visual-studio-code` |
| **prefix** | Root path where Homebrew is installed | `/opt/homebrew`, `/usr/local`, `/home/linuxbrew/.linuxbrew` |
| **keg** | Installation directory for one version of a formula | `/opt/homebrew/Cellar/git/2.47.0` |
| **rack** | Directory containing versioned kegs for one formula | `/opt/homebrew/Cellar/git` |
| **Cellar** | Directory containing all racks | `/opt/homebrew/Cellar` |
| **Caskroom** | Directory containing installed casks | `/opt/homebrew/Caskroom` |
| **keg-only** | Formula not symlinked into prefix (avoids conflicts) | `openssl`, `openjdk`, `python@3.12` |
| **opt prefix** | Stable symlink to the active keg version | `/opt/homebrew/opt/git` → `../Cellar/git/2.47.0` |
| **bottle** | Pre-built keg poured into Cellar instead of building from source | `git--2.47.0.sonoma.bottle.tar.gz` |
| **tab** | Metadata about an installed keg (bottle vs source, install time) | `INSTALL_RECEIPT.json` inside a keg |
| **tap** | Git repository of formulae, casks, and/or external commands | `homebrew/core`, `homebrew/cask`, `user/repository` |
| **external command** | `brew` subcommand defined outside Homebrew/brew repo | `brew tap-info`, `brew shellcheck` |
| **Brewfile** | Declarative dependency file for `brew bundle` | Ruby DSL listing formulae, casks, taps, services |
| **Brew Bundle** | Declarative interface for installing/upgrading packages | `brew bundle install` |
| **Brew Services** | Background service management via launchctl/systemctl | `brew services start postgresql` |

## Installation paths by platform

| Platform | Prefix | Cellar |
|----------|--------|--------|
| macOS ARM (Apple Silicon) | `/opt/homebrew` | `/opt/homebrew/Cellar` |
| macOS Intel | `/usr/local` | `/usr/local/Cellar` |
| Linux | `/home/linuxbrew/.linuxbrew` | `/home/linuxbrew/.linuxbrew/Cellar` |

## Bottle naming

Bottles are named `<formula>--<version>.<tag>.bottle.tar.gz` where the tag encodes macOS version and architecture, e.g., `sonoma.arm64_sequoia`.

## API mode

Since Homebrew 4.0, formulae are downloaded as JSON from `formulae.brew.sh` rather than read from Git. Local formula development requires `HOMEBREW_NO_INSTALL_FROM_API=1` to force Git-based reading.
