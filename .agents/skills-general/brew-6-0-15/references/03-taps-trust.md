# Taps and Tap Trust

## Tapping repositories

```bash
brew tap user/repository                     # GitHub shorthand
brew tap user/repository https://git.example.com/user/repo.git  # Custom URL
brew tap                                      # List tapped repos
brew untap user/repository                   # Remove a tap
brew untap --force user/repository           # Remove tap + all its formulae/casks
brew tap --repair                            # Fix missing symlinks and remote refs
```

### GitHub naming convention

`brew tap user/repository` maps to `https://github.com/user/homebrew-repository`. The `homebrew-` prefix is assumed for the one-argument form.

## Tap trust (Homebrew 6.0+)

Non-official taps require explicit trust before Homebrew loads their formulae, casks, or external commands. Official taps (`homebrew/core`, `homebrew/cask`) are always trusted.

### Trusting individual items (preferred)

```bash
brew install user/repository/formula         # Trusts just this formula on install
brew install --cask user/repository/cask     # Trusts just this cask on install
brew trust --formula user/repository/formula # Explicit trust for formula
brew trust --cask user/repository/cask       # Explicit trust for cask
brew trust --command user/repository/command # Explicit trust for external command
```

### Trusting entire taps

```bash
brew trust user/repository                   # Trust all items in tap
```

Whole-tap trust allows Homebrew to load every current and future item from that tap. Only use for taps you administer or fully trust.

### Managing trust

```bash
brew trust                                   # List trusted entries
brew trust --json --version=v1               # List as JSON
brew untrust user/repository                 # Untrust entire tap
brew untrust --formula user/repo/formula     # Untrust specific formula
brew untrust --cask user/repo/cask           # Untrust specific cask
brew untrust --command user/repo/command     # Untrust specific command
brew untrust                                 # List untrusted items
```

Trust is stored in `${XDG_CONFIG_HOME}/homebrew/trust.json` or `~/.homebrew/trust.json`.

### Environment variables

- `HOMEBREW_REQUIRE_TAP_TRUST=1` — explicitly require tap trust (default behavior)
- `HOMEBREW_NO_REQUIRE_TAP_TRUST=1` — disable tap trust requirement (not recommended, temporary opt-out)

### Trust in Brewfiles

```ruby
# Trust entire tap
tap "user/repository", trusted: true

# Trust specific items
tap "user/repository", trusted: {
  formula:  "formula",
  formulae: ["another-formula"],
  cask:     "cask",
  casks:    ["another-cask"],
  command:  "command",
  commands: ["another-command"],
}

# Trust individual formula/cask entries
brew "user/repository/formula", trusted: true
cask "user/repository/cask", trusted: true
```

`brew bundle cleanup --force` resets trust to Brewfile-declared values and removes undeclared trust entries.

## Duplicate names

When a tap has a formula with the same name as one in `homebrew/core`, use fully qualified names:

```bash
brew install vim                              # from homebrew/core
brew install username/repository/vim          # from specific tap
```

Dependencies of `homebrew/core` formulae cannot be replaced with formulae from other taps.

## Tap info

```bash
brew tap-info <tap>                           # Show tap details
brew tap-info --installed                     # Info for all installed taps
brew tap-info --json                          # JSON output
```
