# Search, Query, and Inspect

## Search

```bash
brew search <text>                      # Substring search of names
brew search /<regex>/                   # Regex search
brew search --formula <text>            # Search formulae only
brew search --cask <text>               # Search casks only
brew search --desc <text>               # Search descriptions
brew search --pull-request <text>       # Search GitHub PRs
brew search --open                      # Open PRs only
brew search --closed                    # Closed PRs only
brew formulae                           # List all installable formulae
brew casks                              # List all installable casks
```

Search extends online to `homebrew/core` and `homebrew/cask`. Without arguments, lists all locally available formulae.

## Info

```bash
brew info                               # Homebrew installation statistics
brew info <formula>                     # Package info
brew info --installed                   # Inventory of installed packages
brew info --sizes                       # Show sizes of installed packages
brew info --json=v1 <formula>           # JSON output (formulae)
brew info --json=v2 <formula>           # JSON output (formulae + casks)
brew info --analytics <formula>         # Install/build error analytics
brew info --github <formula>            # Open GitHub source page
brew info --verbose <formula>           # Detailed info
```

### JSON querying

```bash
# Pretty-print formula info
brew info --json=v1 git | jq .

# All installed formulae as JSON
brew info --json=v1 --installed

# Find keg-only linked formulae
brew info --json=v1 --installed | jq 'map(select(.keg_only == true and .linked_keg != null) | .name)'

# Installed but unlinked normal formulae
brew info --json=v1 --installed | jq 'map(select(.keg_only == false and .linked_keg == null) | .name)'
```

## Dependencies

```bash
brew deps <formula>                     # Show dependencies
brew deps --direct <formula>            # Direct deps only
brew deps --tree <formula>              # Dependency tree
brew deps --tree --prune <formula>      # Tree with pruning
brew deps --graph <formula>             # Directed graph
brew deps --dot <formula>               # DOT format graph
brew deps --annotate <formula>          # Mark build/test/optional deps
brew deps --include-build <formula>     # Include :build deps
brew deps --include-optional <formula>  # Include :optional deps
brew deps --include-test <formula>      # Include :test deps
brew deps --include-requirements <formula>  # Include requirements
brew deps --include-implicit <formula>  # Include implicit deps
brew deps --skip-recommended <formula>  # Skip :recommended deps
brew deps --missing <formula>           # Only missing deps
brew deps --installed <formula>         # Only installed deps
brew deps --topological <formula>       # Sort in topological order
brew deps --union <f1> <f2>             # Union (not intersection)
brew deps --full-name <formula>         # Full names
brew deps --HEAD <formula>              # HEAD version deps
brew deps --os=linux <formula>          # Deps for specific OS
brew deps --arch=arm64 <formula>        # Deps for specific arch
```

## Reverse dependencies

```bash
brew uses <formula>                     # Who depends on this?
brew uses --recursive <formula>         # Multi-level
brew uses --installed <formula>         # Only installed dependents
brew uses --missing <formula>           # Only uninstalled dependents
```

## Description

```bash
brew desc <formula>                     # Name + one-line description
brew desc --search <text>               # Search names and descriptions
brew desc --name <text>                 # Search names only
brew desc --description <text>          # Search descriptions only
```

## Which formula

```bash
brew which-formula <command>            # Find formula providing a command
brew which-formula --explain <command>  # With installation instructions
```

## Options

```bash
brew options <formula>                  # Show install options for formula
brew options --compact <formula>        # All options on one line
brew options --installed                # Options for installed formulae
```

## Outdated

```bash
brew outdated                           # List outdated packages
brew outdated --formula                 # Formulae only
brew outdated --cask                    # Casks only
brew outdated --verbose                 # Include version details
brew outdated --quiet                   # Names only
brew outdated --json                    # JSON output
brew outdated --greedy                  # Include auto-updating casks
```

## Linkage

```bash
brew linkage <formula>                  # Check linked libraries
brew missing                            # Check for missing dependencies
brew missing --hide=<formulae>          # Hide specified formulae
```

## List

```bash
brew list                               # All installed formulae and casks
brew list --formula                     # Formulae only
brew list --cask                        # Casks only
brew list --versions                    # Show version numbers
brew list --pinned                      # Pinned packages
brew list --multiple                    # Multi-version formulae
brew list --full-name                   # Fully-qualified names
brew list --installed-on-request        # Manually installed
brew list --no-installed-on-request     # Installed as dependencies
brew list --poured-from-bottle          # Installed from bottles
brew list --built-from-source           # Built from source
brew list --json --versions             # JSON with versions (needs jq)
brew list <formula>                     # Files installed by formula
```

## Log

```bash
brew log <formula>                      # Git log for formula
brew log --patch <formula>              # With patches
brew log --oneline <formula>            # One line per commit
brew log -1 <formula>                   # Latest commit only
brew log -n 10 <formula>                # Last 10 commits
```

## formulae.brew.sh API

The [formulae.brew.sh API](https://formulae.brew.sh/docs/api/) provides JSON access to all formula metadata without needing Homebrew installed:

```bash
# All formulae
curl https://formulae.brew.sh/api/formula.json | jq '.[].name'

# Single formula
curl https://formulae.brew.sh/api/formula/git.json | jq .

# Analytics
curl https://formulae.brew.sh/api/analytics/install/30d.json
```

## Aliases

```bash
brew alias                              # List aliases
brew alias <name>                       # Show alias command
brew alias ug='upgrade'                 # Create alias
brew alias i='install'                  # Short alias
brew alias --edit                       # Edit aliases in $EDITOR
brew unalias <name>                     # Remove alias
```

Aliases prefixed with `!` run shell commands, `%` preserves local variables.
