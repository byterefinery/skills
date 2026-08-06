# Flakes Reference

## Flake Structure

A flake is a filesystem tree containing a `flake.nix` at its root and optionally a `flake.lock`.

```
my-flake/
├── flake.nix       # declares inputs and outputs
├── flake.lock      # locks input revisions (auto-generated)
├── default.nix     # optional: legacy compatibility
└── src/            # source files
```

## flake.nix Format

```nix
{
  description = "My project";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
    flake-utils.url = "github:numtide/flake-utils";

    # Input without flake (just fetched as source)
    some-source = {
      url = "github:owner/repo";
      flake = false;
    };

    # Shared input (avoid duplication)
    my-lib.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
      in
      {
        packages.default = pkgs.hello;
        apps.default = {
          type = "app";
          program = "${pkgs.hello}/bin/hello";
        };
        devShells.default = pkgs.mkShell {
          buildInputs = [ pkgs.python3 pkgs.cargo ];
        };
      }
    );
}
```

## Inputs

### URL-like syntax

```nix
inputs.nixpkgs.url = "github:NixOS/nixpkgs";
inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";           # branch
inputs.nixpkgs.url = "github:NixOS/nixpkgs/abc123...";             # revision
inputs.nixpkgs.url = "github:NixOS/nixpkgs?dir=subdir";            # subdirectory
inputs.nixpkgs.url = "github:NixOS/nixpkgs/pull/12345/head";       # PR
inputs.nixpkgs.url = "git+https://gitlab.com/org/repo";            # generic git
inputs.nixpkgs.url = "path:/absolute/path";                         # local path
inputs.nixpkgs.url = "path:.";                                      # current dir
inputs.nixpkgs.url = "nixpkgs";                                     # registry lookup
inputs.nixpkgs.url = "nixpkgs/abc123...";                           # registry + override rev
inputs.nixpkgs.url = "sourcehut:user/repo.git";                     # sourcehut
inputs.nixpkgs.url = "tarball+https://example.com/source.tar.gz";   # tarball
```

### Attribute set representation

```nix
inputs.nixpkgs = {
  type = "github";
  owner = "NixOS";
  repo = "nixpkgs";
  ref = "nixos-24.11";   # optional: branch, tag, or revision
};
```

### `follows` for shared inputs

When multiple inputs should share the same source:

```nix
inputs.foo.inputs.nixpkgs.follows = "nixpkgs";
inputs.bar.inputs.nixpkgs.follows = "nixpkgs";
```

This avoids downloading nixpkgs multiple times and ensures consistency. Empty string `follows = ""` means "no input".

## Outputs Schema

### Standard output attributes

| Attribute | Path | Description |
|-----------|------|-------------|
| `packages` | `packages.<system>.<name>` | Buildable derivations |
| `apps` | `apps.<system>.<name>` | Runnable applications |
| `devShells` | `devShells.<system>.<name>` | Development environments |
| `formatter` | `formatter.<system>` | Nix code formatter (derivation) |
| `nixosModules` | `nixosModules.<name>` | NixOS module |
| `nixosConfigurations` | `nixosConfigurations.<name>` | NixOS system config |
| `homeManagerModules` | `homeManagerModules.<name>` | Home Manager module |
| `overlays` | `overlays.<name>` | Nixpkgs overlay |
| `templates` | `templates.<name>` | Project templates |

### System identifiers

Common values: `x86_64-linux`, `aarch64-linux`, `x86_64-darwin`, `aarch64-darwin`.

Use `builtins.currentSystem` for the current system. For cross-compilation, use target triples like `aarch64-unknown-linux-gnu`.

### App definition

```nix
apps.myapp = {
  type = "app";
  program = "/path/to/binary";
  # or:
  meta = { ... };  # optional metadata
};
```

The `program` must be an absolute path to an executable.

## Flake Lock File

`flake.lock` is auto-generated and pins exact revisions:

```json
{
  "nodes": {
    "nixpkgs": {
      "locked": {
        "lastModified": 1700000000,
        "narHash": "sha256-...",
        "owner": "NixOS",
        "repo": "nixpkgs",
        "rev": "abc123...",
        "type": "github"
      },
      "original": {
        "owner": "NixOS",
        "ref": "nixos-24.11",
        "type": "github"
      }
    }
  },
  "root": "root",
  "version": 7
}
```

- Always commit `flake.lock` to version control
- `nix flake lock` — create or add missing entries
- `nix flake update` — update all inputs
- `nix flake update nixpkgs` — update specific input
- `nix flake update --override-input nixpkgs github:NixOS/nixpkgs/nixos-unstable`

## Flake Registry

The flake registry maps short names to concrete flake references. Indicated by `~` prefix in CLI.

```bash
# Indicated inputs (use registry, allow updates)
nix build ~nixpkgs#hello

# Pinned inputs (ignore registry, use lock file)
nix build nixpkgs#hello
```

Registry commands:

```bash
nix registry list
nix registry add mypkgs github:NixOS/nixpkgs
nix registry add mypkgs github:NixOS/nixpkgs/rev --from nixpkgs
nix registry remove mypkgs
nix registry pin mypkgs
nix registry resolve nixpkgs
```

Built-in registry entries: `nixpkgs`, `nixpkgs-unstable`, `nix`.

## Templates

Create new projects from flake templates:

```bash
nix flake new . --template nixpkgs#cmake-application
nix flake new . --template nixpkgs#fluent-bit
nix flake new my-project --template github:owner/template-flake
```

Define templates in your flake:

```nix
outputs = { self, ... }: {
  templates.my-template = {
    path = ./templates/my-template;
    description = "My project template";
  };
  defaultTemplate = ./templates/my-template;
};
```

## Common Patterns

### EachDefaultSystem (flake-utils pattern)

```nix
outputs = { self, nixpkgs, flake-utils, ... }:
  flake-utils.lib.eachDefaultSystem (system:
    let pkgs = nixpkgs.legacyPackages.${system}; in
    {
      packages.default = pkgs.callPackage ./default.nix {};
      devShells.default = pkgs.mkShell { buildInputs = [ pkgs.nix ]; };
      formatter = pkgs.nixfmt;
    }
  );
```

### Without flake-utils

```nix
outputs = { self, nixpkgs, ... }:
  let
    system = "x86_64-linux";
    pkgs = import nixpkgs { inherit system; };
  in
  {
    packages.${system}.default = pkgs.hello;
    devShells.${system}.default = pkgs.mkShell { buildInputs = [ pkgs.hello ]; };
    formatter.${system} = pkgs.nixfmt;
  };
```

### Overlay

```nix
outputs = { self, nixpkgs, ... }: {
  overlays.my-overlay = final: prev: {
    my-package = prev.my-package.override {
      enableFeature = true;
    };
  };
};
```

Use in another flake:

```nix
inputs.my-flake.url = "path:./my-flake";
outputs = { self, nixpkgs, my-flake, ... }:
  let
    pkgs = import nixpkgs {
      overlays = [ my-flake.overlays.my-overlay ];
    };
  in { ... };
```

## Gotchas

- **Flakes are pure by default** — they cannot access `$NIX_PATH`, local filesystem (except declared inputs), or environment variables. Use `--impure` to relax.
- **Git-only files** — flake inputs from git repos only see tracked files. Untracked and `.gitignore`d files are invisible. Use `path:` instead of relying on git auto-detection.
- **`flake.lock` must be committed** — without it, flakes are not reproducible. The lock file is the source of truth for input versions.
- **Input name collisions** — if two inputs have the same name at different levels, use fully qualified paths: `inputs.foo.bar` vs just `bar` in outputs function.
- **`self` refers to the current flake** — use `self` to reference the flake's own outputs from within its outputs function, enabling recursion.
