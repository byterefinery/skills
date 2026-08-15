---
name: nix-2-35-1
description: Nix 2.35.1 — the purely functional package manager. Use for building, running, developing, and managing software with Nix expressions, flakes, derivations, and the Nix store. Covers `nix build`, `nix run`, `nix shell`, `nix develop`, `nix profile`, `nix search`, `nix flake`, store operations, garbage collection, and the Nix language (types, operators, scoping, string interpolation, derivations).
license: LGPL-2.1-only
compatibility: Requires Nix 2.35.1. Flakes and `nix` commands require `--experimental-features nix-command flakes` or `experimental-features = nix-command flakes` in config.
allowed-tools: Bash(nix) Bash(git) Read
metadata:
  tags:
    - package-manager
    - functional
    - reproducible-builds
    - linux
    - devops
---

# nix 2.35.1

Nix is a powerful package manager for Linux and Unix systems that makes package management reliable and reproducible. It uses a purely functional deployment model — every package is built in isolation with explicitly declared dependencies, stored under `/nix/store/<hash>-<name>`, and never modified in place.

## Overview

Nix distinguishes itself through:

- **Purely functional** — packages are derivations (precise build descriptions) that produce immutable store paths. No global state, no in-place upgrades.
- **Declarative** — configurations and environments are described as data, not sequential steps.
- **Reproducible** — same inputs always produce the same store path (hash-based naming).
- **Multi-version coexistence** — multiple versions of a package install side by side without conflict.
- **Rollback** — every profile change is versioned; roll back instantly.
- **Binary caching** — pre-built packages are substituted from binary caches (e.g., Cachix, Cachenix).

### Core concepts

- **Nix store** — the central directory (`/nix/store`) where all packages and their dependencies live, addressed by content-addressed paths.
- **Derivation** — a description of how to build something: inputs, builder script, environment variables, outputs. Evaluating a Nix expression produces derivations; building a derivation produces store paths.
- **Flake** — a filesystem tree with a `flake.nix` file that declares inputs (dependencies on other flakes) and outputs (packages, apps, devShells, NixOS modules). Flakes are reproducible by default via `flake.lock`.
- **Installable** — a command-line argument representing something realisable: `flake#attr`, store path, `--file`, or `--expr`.
- **Profile** — a versioned set of packages installed for a user or system. Supports add, remove, upgrade, rollback, list.
- **Nix language** — a domain-specific, declarative, pure, functional, lazy, dynamically typed language for creating and composing derivations.

## Usage

```bash
# Build a package from nixpkgs flake
nix build nixpkgs#hello
./result/bin/hello

# Run a package directly
nix run nixpkgs#hello

# Get a shell with tools available on PATH
nix shell nixpkgs#python3 nixpkgs#cargo

# Enter a build/dev environment for a package
nix develop nixpkgs#hello

# Search for packages
nix search nixpkgs neovim

# Manage installed packages
nix profile install nixpkgs#hello
nix profile list
nix profile upgrade
nix profile rollback

# Garbage collect
nix store gc

# Work with flakes
nix flake new my-project --template flake-flutter
nix flake show .
nix flake lock
nix flake update nixpkgs

# Evaluate / debug
nix eval nixpkgs#hello.version
nix repl
nix print-dev-env nixpkgs#hello
```

## Gotchas

- **Experimental features** — flakes and the new `nix` command require `--experimental-features nix-command flakes`. Enable permanently in `~/.config/nix/nix.conf`: `experimental-features = nix-command flakes`. Without this, `nix build nixpkgs#hello` fails with "experimental features flag".
- **`./result` symlink** — `nix build` creates `./result` pointing to the output. Multiple build targets produce `result`, `result-1`, `result-2`, etc. Use `--print-out-paths` to get the store path directly.
- **`nix shell` vs `nix develop`** — `nix shell` adds packages to `$PATH` for ad-hoc use. `nix develop` provides the full build environment (with `buildInputs`, `nativeBuildInputs`, shell functions like `configurePhase`, `buildPhase`). Use `shell` for quick access, `develop` for building/debugging.
- **String interpolation copies to store** — `"${./file.txt}"` copies `file.txt` into the Nix store. This is intentional and enables reproducibility, but can be surprising — paths in interpolated strings are not just references, they trigger store copies.
- **`<nixpkgs>` is impure** — lookup paths like `<nixpkgs>` depend on `$NIX_PATH` and require `--impure` flag. Prefer flakes (`nixpkgs#...`) for pure, reproducible references.
- **Flake lock files pin revisions** — `flake.lock` pins exact Git revisions. This is the source of reproducibility. Use `nix flake update` to refresh inputs; do not commit without updating the lock file.
- **`follows` for shared inputs** — when multiple flake inputs should track the same source, use `follows` to avoid duplication: `inputs.foo.inputs.nixpkgs.follows = "nixpkgs"`.
- **Attribute search order** — `nix build nixpkgs#hello` searches `packages.<system>.hello`, `legacyPackages.<system>.hello`, then `hello`. Use `#.` prefix to bypass search: `nixpkgs#.myExactAttr`.
- **`--impure` for local paths** — expressions using `<nixpkgs>`, `$NIX_PATH`, or local filesystem lookups need `--impure`. Pure evaluation rejects these.
- **Derivation output selection** — use `^output` syntax: `nixpkgs#glibc^dev` for the `dev` output, `nixpkgs#openssl^*` for all outputs. Result symlinks become `result-dev`, `result-bin`, etc.
- **`nix profile` and `nix-env` are incompatible** — once you use `nix profile`, you cannot use `nix-env` on the same profile. Delete the profile to migrate back.
- **Path literals need a slash** — `builder.sh` is parsed as attribute access, not a path. Use `./builder.sh` (with leading `./`) for relative paths.
- **Lists are strict in length** — list elements are lazy, but the list length is evaluated eagerly. You cannot have infinite lists.
- **Function calls in lists need parens** — `[ f { x = 1; } ]` is five elements, not one. Write `[ (f { x = 1; }) ]` to get the function result as a single element.

## References

- [01-commands](references/01-commands.md) — Full command reference: build, run, shell, develop, search, profile, store, flake subcommands
- [02-nix-language](references/02-nix-language.md) — Types, operators, syntax, scoping, string interpolation, functions, let/with/rec
- [03-flakes](references/03-flakes.md) — Flake format, flake.nix structure, flakerefs, outputs schema, lock files, registry
- [04-store](references/04-store.md) — Store paths, derivations, closures, garbage collection, binary substitution, profiles
- [05-builtins](references/05-builtins.md) — Key built-in functions: derivation, import, fetchurl, fetchTarball, fetchGit, filterSource, currentSystem
