---
name: pkgx-2-11-0
description: pkgx 2.11.0 — a standalone binary that runs any Open Source tool on demand without installing it system-wide. Use when the user needs to run CLI tools (Node, Python, Deno, cargo, git, etc.) without installing them, run specific versions of tools, use `+pkg` syntax to inject dependencies into environments, write portable scripts with pkgx shebangs, manage downloaded packages with mash scripts, or set up CI/CD with pkgx. Covers version pinning (@, ^, ~, semver ranges), disambiguation, environment injection via eval, PKGX_DIR for virtual environments, and the broader pkgx ecosystem (dev, pkgm, mash, pkgo).
compatibility: Requires macOS >= 11 (Intel/Apple Silicon) or Linux (glibc >= 2.28, libgcc). Windows 10+ experimental. Needs `pkgx` on PATH.
metadata:
  tags:
    - package-manager
    - cli
    - scripting
    - devops
    - macos
    - linux
---

# pkgx 2.11.0

## Overview

pkgx is a 4 MiB standalone binary that runs any Open Source tool on demand. It downloads packages to `~/.pkgx` (or `$PKGX_DIR`) and executes them without polluting the system. Nothing is "installed" globally — packages are fetched on first use and cached.

Core model: `pkgx <tool>` runs the latest downloaded version. `pkgx <tool>@<version>` pins a version. `pkgx +<dep> <command>` injects dependencies into the environment.

**Key distinction from package managers:** pkgx does not install packages system-wide. It creates isolated environments on demand. For persistent installs, use `pkgm` (the companion tool).

### Package storage

- macOS: `~/.pkgx` (or `~/Library/Packages` if it exists)
- Linux: `~/.pkgx` (or `$XDG_DATA_HOME/pkgx`)
- Each package lives at `~/.pkgx/<fqdn>/v<version>/` (relocatable POSIX prefix)
- Symlinks for major/minor/latest: `v3 -> v3.11.11`, `v3.11 -> v3.11.11`

## Usage

### Run a tool

```bash
pkgx deno              # latest downloaded version
pkgx node@14 --version # specific major
pkgx python@2          # major version
```

### Version pinning

- `@3` → `^3` (major)
- `@3.1` → `~3.1` (minor)
- `@3.1.2` → `>=3.1.2<3.1.3` (patch)
- `^20.1.3` → `>=20.1.3<21` (semver caret)
- `>=12<14` → range (semver)
- `=1.35.3` → exact (semver)

### Inject dependencies with `+pkg`

```bash
pkgx +openssl cargo build      # add openssl to cargo's environment
pkgx +gum -- gum choose        # add gum, then run system command after --
pkgx +llvm.org /usr/bin/make   # run system make with llvm in env
```

### Environment injection (no command to run)

```bash
eval "$(pkgx +gum)"   # adds gum to current shell's PATH
eval "$(pkgx +gum --json)"  # JSON output for programmatic use
```

### Quiet modes

```bash
pkgx -q  gum format "suppress resolving/syncing"   # -q / --quiet
pkgx -qq gum format "silence everything"            # -qq / --silent
```

### Search / query

```bash
pkgx -Q git           # is git available? (prints FQDN)
pkgx -Q | grep git-   # list git extensions
pkgx -Q               # list everything pkgx can run
```

### Disambiguation

When multiple packages provide the same binary name:

```bash
# pkgx yarn errors with suggestions:
pkgx +classic.yarnpkg.com yarn --version
pkgx +yarnpkg.com yarn --version
```

Use fully-qualified names in scripts for long-term robustness.

### Virtual environments

```bash
export PKGX_DIR="$PWD/foo"   # must be absolute path
pkgx +gum                    # installs into $PWD/foo/
```

### Managing packages (mash scripts)

```bash
pkgx mash upgrade       # update cached packages to latest
pkgx mash upgrade deno  # upgrade specific package
pkgx mash prune         # remove older versions from cache
pkgx mash ls            # list downloaded packages
pkgx mash inventory git # list all available versions
pkgx mash outdated      # list outdated packages
pkgx mash ensure git    # use system git if available, else pkgx
```

### Scripting with pkgx shebangs

```bash
#!/usr/bin/env -S pkgx +git python@3.12
# python 3.12 runs the script, git is available in PATH
```

```bash
#!/usr/bin/env -S pkgx +gum +gh +npx +git bash>=4 -eo pipefail
# multiple deps, specific bash version, strict mode
```

The `-S` flag to `env` is required for multiple arguments. Packages are downloaded to `~/.pkgx` but never installed system-wide.

### Running system commands with pkgx environment

```bash
pkgx +llvm.org -- make        # finds system make, runs with llvm env
pkgx +llvm.org /usr/bin/make  # explicit system binary
```

Without `--` or full path, pkgx would use its own package for the command.

## Gotchas

- **`pkgx foo` runs the latest _downloaded_ version, not the latest available.** Use `pkgx mash upgrade foo` to fetch newer versions.
- **`+pkg` syntax is positional:** `pkgx +openssl cargo build` — the `+pkg` comes before the command. Multiple `+pkg` entries are additive.
- **`--` separates pkgx args from the command to run.** Without it, pkgx tries to use its own package for every argument.
- **Ambiguous binaries require FQDN.** When two packages provide the same binary (e.g., `yarn`), use `+<fqdn>` to disambiguate. Always prefer FQDN in scripts for longevity.
- **`PKGX_DIR` must be absolute.** Relative paths are silently ignored.
- **`-S` is required with `env` shebangs.** `#!/usr/bin/env pkgx python` works for single args, but `#!/usr/bin/env -S pkgx +git python` needs `-S`.
- **Packages are relocatable.** The entire `~/.pkgx` tree can be copied and used elsewhere.
- **Windows support is experimental** with limited packages. WSL2 gets full Linux support.
- **`pkgx` is not a package manager.** It doesn't install, uninstall, or manage system packages. Use `pkgm` for persistent installs.
- **`mash` is a separate script/tool** distributed through pkgx itself — commands like `pkgx mash upgrade` invoke a mash script, not a built-in pkgx subcommand.

## References

- [01-scripting-examples](references/01-scripting-examples.md) — Python, Ruby, JS/TS, Rust, C/C++ shebang patterns
- [02-installation-methods](references/02-installation-methods.md) — brew, curl, cargo, Docker, GitHub Actions, manual download
- [03-ecosystem](references/03-ecosystem.md) — dev, pkgm, mash, pkgo overview
