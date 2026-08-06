# Store Reference

## Store Paths

All Nix-managed content lives under `/nix/store` (configurable via `NIX_STORE`). Each path is content-addressed:

```
/nix/store/<hash>-<name>
/nix/store/10l19qifk7hjjq47px8m2prqk1gv4isy-hello-2.10
/nix/store/frzgk3v1ycnarpfc2rkynravng27a86d-cowsay-3.03+dfsg2
```

- `<hash>` — SHA-256 (or other) hash of the derivation or fixed-output content
- `<name>` — human-readable name from the derivation's `name` attribute
- Paths are immutable — once created, contents never change
- Symlinks outside the store (e.g., `./result`, profile links) point into the store

## Derivations

A derivation (`.drv` file) describes how to produce store paths:

```json
{
  "builder": "/bin/sh",
  "args": ["-c", "cp $src/hello.c $out"],
  "env": {
    "stdenv": "/nix/store/...-stdenv",
    "name": "hello-2.12",
    "out": "/nix/store/<hash>-hello-2.12"
  },
  "inputsDrvs": {
    "/nix/store/...-stdenv.drv": ["out"]
  },
  "inputsSources": {
    "./src": "/nix/store/...-source"
  },
  "outputs": {
    "out": "/nix/store/<hash>-hello-2.12"
  },
  "system": "x86_64-linux"
}
```

### Derivation attributes

| Attribute | Required | Description |
|-----------|----------|-------------|
| `name` | Yes | Symbolic name; affects output path |
| `system` | Yes | Target system (`x86_64-linux`, etc.) |
| `builder` | Yes | Executable that performs the build |
| `args` | No (default `[]`) | Arguments to the builder |
| `env` | No | Environment variables for the builder |
| `outputs` | No (default `["out"]`) | Output names (`out`, `dev`, `doc`, `bin`, etc.) |
| `inputSrcs` | No | Source files/directories |
| `inputDrvs` | No | Other derivations this depends on |
| `outputHash` | No | For fixed-output derivations (fetchFromGitHub, etc.) |
| `outputHashAlgo` | No | Hash algorithm (`sha256`, etc.) |
| `outputMaxConnections` | No | For fixed-output derivations |

### Multiple outputs

A single derivation can produce multiple outputs:

```nix
derivation {
  name = "my-lib-1.0";
  system = builtins.currentSystem;
  builder = "/bin/sh";
  args = [ "-c" ''
    mkdir -p $out/bin $dev/include $doc/share/doc
    # install binaries to $out, headers to $dev, docs to $doc
  '' ];
  outputs = [ "out" "dev" "doc" ];
}
```

Select outputs: `nix build nixpkgs#glibc^dev`, `nix build nixpkgs#openssl^*`.

## Closures

The closure of a store path is the transitive set of all dependencies needed to use it.

```bash
nix store info nixpkgs#hello        # show closure size and element count
nix store diff-closures /path/a /path/b   # compare closures
nix why-depends nixpkgs#hello nixpkgs#glibc  # show dependency chain
```

## Garbage Collection

Nix tracks *roots* — symlinks or database entries that mark paths as "in use". Unreachable paths (not in any root's closure) are garbage.

```bash
nix store gc                          # delete all unreachable paths
nix store gc --max 1G                 # free at least 1G
nix store gc --max-size 50G           # keep store under 50G
nix store ls-root                     # list garbage collector roots
nix verify                            # check store integrity
nix optimise                          # deduplicate identical blocks
nix store repair                      # repair invalid paths
```

### Common roots

- `/nix/var/nix/gcroots/` — manual gc roots
- `/nix/var/nix/profiles/` — system profiles
- `~/.local/state/nix/profiles/` — user profiles
- `/run/current-system` — NixOS booted system

## Binary Substitution

Instead of building locally, Nix can fetch pre-built packages from binary caches.

```ini
# ~/.config/nix/nix.conf
substituters = https://cache.nixos.org https://my-cache.cachix.org
trusted-public-keys = cache.nixos.org-1:... my-cache.cachix.org-1:...
```

```bash
nix build --substitute-on-try nixpkgs#hello   # try substituter first, build if missing
nix build --no-substitute-on-walk nixpkgs#hello  # build locally, don't substitute
nix copy --to ssh://host nixpkgs#hello        # build locally, copy to remote
```

## Profiles

Profiles are versioned sets of store paths. Each operation creates a new generation.

```bash
# User profiles (nix profile)
nix profile install nixpkgs#hello
nix profile list
nix profile remove --index 3
nix profile upgrade
nix profile upgrade nixpkgs#hello
nix profile rollback              # to previous generation
nix profile rollback --generation 5
nix profile diff-closures         # diff current vs previous
nix profile history
nix profile wipe-history          # delete old generations

# System profiles
nix build --profile /nix/var/nix/profiles/system .
```

Profile storage: `~/.local/state/nix/profiles/profile` (user) or `/nix/var/nix/profiles/system` (system).

## Store Types

### Local store

Default. Uses the local filesystem at `/nix/store`.

### SSH store

Remote store accessed over SSH:

```bash
nix --store ssh://deploy-host build nixpkgs#hello
nix copy --to ssh://deploy-host nixpkgs#hello
```

### SSC (Simple Store Connection)

TCP-based store protocol for build farms and containers.

### Docker store

Nix store inside a Docker container (experimental).

### Mount store

Access a store from another machine via mounted filesystem.

## Nix Daemon

`nix-daemon` runs builds with appropriate privileges. Required on multi-user installations.

```bash
sudo systemctl enable --now nix-daemon
sudo journalctl -u nix-daemon -f
```

Config: `/etc/nix/nix.conf`. Key settings:

```ini
max-jobs = auto                # parallel builds
cores = 0                      # 0 = all cores
max-memory-size = 0            # 0 = unlimited
build-cores = 1                # default cores per build
sandbox = true                 # isolate builds
sandbox-fallback = true        # allow non-sandbox if unavailable
```

## Content-Addressed Store Paths

Two types of store paths:

1. **Derivation-addressed** — hash includes the derivation content. Changing any input changes the output hash. Most packages use this.

2. **Fixed-output (content-addressed)** — hash is computed from the output content itself. Used for fetched sources (fetchurl, fetchTarball, fetchGit with `sha256`).

```nix
builtins.fetchTarball {
  url = "https://example.com/source.tar.gz";
  sha256 = "sha256-...";       # fixed output hash
}
```

## Copying Between Stores

```bash
nix copy --to ssh://host nixpkgs#hello
nix copy --from ssh://host nixpkgs#hello
nix copy --to s3://bucket --from ssh://build-host nixpkgs#hello
nix store copy-log /path/to/nar        # copy from .nar archive
```

## Nar (Nix Archive)

The `.nar` format serializes store paths for transfer:

```bash
nix store dump-path /nix/store/...-hello > hello.nar
nix store load-file < hello.nar
nix nar cat /nix/store/...-hello       # cat NAR contents
nix nar ls /nix/store/...-hello        # list NAR directory
nix nar dump-path /nix/store/...-hello > hello.nar
```
