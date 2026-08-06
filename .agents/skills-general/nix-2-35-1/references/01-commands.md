# Commands Reference

## Build, Run, Shell, Develop

### `nix build`

Builds installables. Resolves to derivations, builds (or substitutes) them, creates `./result` symlink(s).

```bash
nix build nixpkgs#hello                    # build from flake
nix build nixpkgs#hello nixpkgs#cowsay     # multiple: result, result-1
nix build nixpkgs#glibc^dev                # specific output
nix build nixpkgs#openssl^*                # all outputs
nix build --file release.nix build.x86_64-linux
nix build --expr 'with import <nixpkgs> {}; hello'
nix build --print-out-paths nixpkgs#hello  # print store path, no symlink
nix build --profile /nix/var/nix/profiles/system .
```

### `nix run`

Builds and runs an installable. For apps, executes the app definition. For derivations, runs `<out>/bin/<name>` (using `meta.mainProgram`, `pname`, or derivation name).

```bash
nix run nixpkgs#hello
nix run nixpkgs#vim -- --help
nix run . -- arg1 arg2          # default app from current flake
nix run blender-bin             # default app from blender-bin flake
```

### `nix shell`

Runs a command in an environment with installables on `$PATH`. Starts `$SHELL` if no command given.

```bash
nix shell nixpkgs#python3 nixpkgs#cargo
nix shell nixpkgs#hello --command hello
nix shell nixpkgs#gnumake --command sh -c "cd src && make"
```

Shebang usage for self-contained scripts:

```python
#! /usr/bin/env nix
#! nix shell nixpkgs#python3 --command python3

print("hello")
```

### `nix develop`

Starts a `bash` shell providing the interactive build environment for an installable. Sets up environment variables and shell functions (`configurePhase`, `buildPhase`, `installPhase`, etc.).

```bash
nix develop                          # current flake's default
nix develop nixpkgs#hello
nix develop --profile /tmp/build-env nixpkgs#hello
nix develop --command bash -c "mkdir build && cmake .. && make"
nix develop --redirect nixpkgs#glibc.dev ~/my-glibc/outputs/dev
nix develop --build                  # run just the build phase
```

## Search and Eval

### `nix search`

Searches installable for packages matching regex patterns. Matches against name and `meta.description`.

```bash
nix search nixpkgs ^                # all packages
nix search nixpkgs blender          # match "blender"
nix search nixpkgs 'firefox|chromium'  # regex alternation
nix search nixpkgs git 'frontend|gui'  # multiple patterns (AND)
nix search nixpkgs neovim --exclude 'python|gui'
nix search nixpkgs#gnome3 vala      # search under attribute
```

### `nix eval`

Evaluates an installable and prints the result.

```bash
nix eval nixpkgs#hello.version
nix eval --raw nixpkgs#hello.version    # no quoting
nix eval nixpkgs#hello.meta.description
nix eval --json nixpkgs#hello           # JSON output
```

### `nix repl`

Interactive Nix expression evaluator. Supports `:b` (build), `:lf` (load file), `:r` (reset), `:q` (quit).

```bash
nix repl
> builtins.currentSystem
> :b <nixpkgs>
> pkgs = import <nixpkgs> {}
> pkgs.hello.version
```

## Profile Management

### `nix profile`

Manages user-level package profiles. Versioned — supports rollback.

```bash
nix profile install nixpkgs#hello
nix profile install ./my-package.drv
nix profile list
nix profile remove --index 2
nix profile upgrade
nix profile upgrade nixpkgs#hello
nix profile rollback
nix profile diff-closures
nix profile history
nix profile wipe-history
```

## Store Operations

### `nix store`

Low-level store operations.

```bash
nix store gc                          # garbage collect
nix store gc --max 1G                 # delete until 1G freed
nix store info nixpkgs#hello          # show closure size
nix store diff-closures /path/a /path/b
nix store delete /nix/store/...       # delete specific path
nix store verify                      # verify store integrity
nix store ls /nix/store/...-foo       # list contents
nix store cat /nix/store/...-foo/bar  # cat a file in store
nix store copy --from ssh://host .    # copy from remote
nix why-depends nixpkgs#hello nixpkgs#glibc
```

### `nix copy`

Copy closures between stores.

```bash
nix copy --to ssh://deploy-host nixpkgs#hello
nix copy --from ssh://build-host nixpkgs#hello
```

## Flake Commands

### `nix flake`

Create, modify, and query flakes.

```bash
nix flake new hello --template nixpkgs#cmake-application
nix flake show github:NixOS/nixpkgs
nix flake show .                     # show current flake's outputs
nix flake lock                       # create/update lock file
nix flake update                     # update all inputs
nix flake update nixpkgs             # update specific input
nix flake check                      # validate flake outputs
nix flake archive                    # archive flake inputs
nix flake clone github:NixOS/nixpkgs
nix flake init                       # create flake.nix in current dir
```

### `nix registry`

Manage the flake registry (local pinning of flake references).

```bash
nix registry list
nix registry add mypkgs github:NixOS/nixpkgs
nix registry add mypkgs github:NixOS/nixpkgs/revision --from nixpkgs
nix registry remove mypkgs
nix registry pin mypkgs              # resolve to concrete path
nix registry resolve nixpkgs
```

## Legacy Commands

### `nix-build`

Legacy equivalent of `nix build`. Uses `--expr` or file argument.

```bash
nix-build <nixpkgs> -A hello
nix-build --expr 'with import <nixpkgs> {}; hello'
```

### `nix-shell`

Legacy equivalent of `nix develop`/`nix shell`.

```bash
nix-shell -p hello vim               # packages on PATH
nix-shell --pure -p hello            # minimal environment
nix-shell package.nix                # use package's build env
nix-shell --show-trace               # show evaluation trace
```

### `nix-env`

Legacy user-environment package manager. Incompatible with `nix profile`.

```bash
nix-env -f <nixpkgs> -iA hello       # install
nix-env -e hello                      # remove
nix-env -u                            # upgrade all
nix-env --list-generations
nix-env --rollback
```

### `nix-instantiate`

Evaluate Nix expressions and show derivations.

```bash
nix-instantiate <nixpkgs> -A hello
nix-instantiate --parse <nixpkgs>     # parse and pretty-print
nix-instantiate --eval -E '1 + 2'
```

## Configuration

Key config file: `~/.config/nix/nix.conf` (user) or `/etc/nix/nix.conf` (system).

```ini
experimental-features = nix-command flakes
substituters = https://cache.nixos.org https://my-cache.cachix.org
trusted-public-keys = cache.nixos.org-... my-cache.cachix.org-...
max-jobs = auto
system-features = nixos-test benchmark big-parallel kvm
```

Key environment variables:

- `NIX_PATH` — search path for `<name>` lookups (e.g., `nixpkgs=/nix/repo`)
- `NIX_STORE` — alternative store directory
- `NIX_BUILD_CORES` — number of cores for builds
- `NIX_BUILD_SHELL` — shell used in build environments
