# Built-in Functions Reference

## Core Functions

### `derivation`

Create a store derivation. The most important built-in.

```nix
derivation {
  name = "hello";
  system = builtins.currentSystem;
  builder = "/bin/sh";
  args = [ "-c" "echo Hello > $out" ];
}
```

Returns an attribute set with the derivation's output paths. Side effect: creates `.drv` file in the store.

### `import`

Load and evaluate a Nix expression file.

```nix
import ./file.nix
import ./file.nix { arg1 = val1; arg2 = val2; }
```

The file must resolve to a readable path. If it returns a function, the argument set is applied.

### `builtins.getFlake`

Parse and resolve a flake reference.

```nix
builtins.getFlake "github:NixOS/nixpkgs"
builtins.getFlake "/path/to/flake"
```

### `builtins.fromTOML` / `builtins.fromJSON` / `builtins.fromXML` / `builtins.fromCSV`

Parse structured data formats into Nix values.

```nix
builtins.fromJSON '{ "key": "value" }'
builtins.fromTOML (builtins.readFile ./config.toml)
```

### `builtins.toJSON` / `builtins.toXML`

Serialize Nix values to JSON or XML strings.

## Fetch Functions

### `builtins.fetchurl`

Fetch a URL and store it in the Nix store.

```nix
builtins.fetchurl {
  url = "https://example.com/file.tar.gz";
  sha256 = "sha256-...";       # optional: verify hash
}
```

Returns a store path. Without `sha256`, the output is derivation-addressed (not reproducible across machines).

### `builtins.fetchTarball`

Fetch a URL and unpack a tarball.

```nix
builtins.fetchTarball {
  url = "https://github.com/NixOS/nixpkgs/archive/master.tar.gz";
  sha256 = "sha256-...";       # optional but recommended
}

# Shorthand (URL string):
builtins.fetchTarball "https://github.com/NixOS/nixpkgs/archive/master.tar.gz"
```

Returns a path to the unpacked directory.

### `builtins.fetchGit`

Clone a Git repository.

```nix
builtins.fetchGit {
  url = "https://github.com/NixOS/nix";
  ref = "master";               # optional: branch, tag, or revision
  sha256 = "sha256-...";        # optional: pin exact revision
  fallback = true;              # use tarball if git not available
}
```

Without `sha256`, fetches current HEAD (impure — differs by time).

### `builtins.fetchzip` / `builtins.fetchbzip2` / `builtins.fetchgzip` / `builtins.fetchxz`

Fetch and decompress archives in specific formats.

```nix
builtins.fetchzip {
  url = "https://example.com/source.zip";
  sha256 = "sha256-...";
}
```

## File System Functions

### `builtins.readFile`

Read a file as a string.

```nix
builtins.readFile ./version.txt
builtins.readFile "${pkgs.hello}/LICENSE"
```

### `builtins.readDir`

List directory contents.

```nix
builtins.readDir ./src
# → { "main.nix" = "regular"; "lib" = "directory"; }
```

Values: `"regular"`, `"directory"`, `"symlink"`.

### `builtins.readFileType`

Return the type of a path.

```nix
builtins.readFileType ./file.nix    # → "regular"
builtins.readFileType ./dir         # → "directory"
builtins.readFileType ./link        # → "symlink"
builtins.readFileType /nonexistent  # → null
```

### `builtins.path`

Create a path value, optionally copying to the store.

```nix
builtins.path {
  name = "source";
  path = ./src;
  filter = name: type:
    type != "directory" || name != ".git";
}
```

### `builtins.toFile`

Create a store file with given contents.

```nix
builtins.toFile "config.yaml" ''
  key: value
  nested:
    item: 1
''
```

Returns a store path.

### `builtins.storePath`

Convert a string to a store path value without copying.

```nix
builtins.storePath "/nix/store/...-hello-2.12"
```

## Filter Functions

### `builtins.filterSource`

Recursively filter a directory tree.

```nix
builtins.filterSource
  (path: type: baseName:
    baseName != ".git" && baseName != ".gitignore")
  ./source
```

Takes a predicate function `(path: type: baseName: bool)` and a root path. Returns a path to the filtered tree in the store.

### `builtins.sourceFilter`

Alias for `filterSource` with the arguments in a different order (legacy).

```nix
builtins.sourceFilter
  (path: type:
    type != "directory" || baseNameOf path != ".git")
  ./source
```

## String Functions

### `builtins.substring`

Extract a substring.

```nix
builtins.substring start length str
builtins.substring 0 5 "hello world"   # → "hello"
```

### `builtins.toString`

Convert any value to a string.

```nix
builtins.toString 42                    # → "42"
builtins.toString true                  # → "true"
builtins.toString ./file.txt            # → store path string
```

### `builtins.parseDrvName`

Split a derivation name into `pname` and `version`.

```nix
builtins.parseDrvName "hello-2.12"
# → { name = "hello"; version = "2.12"; }
```

### `builtins.hashString` / `builtins.hashFile`

Compute a hash.

```nix
builtins.hashString "sha256" "hello"
builtins.hashFile "sha256" ./file.txt
```

### `builtins.baseNameOf` / `builtins.dirOf`

Path components.

```nix
builtins.baseNameOf "/a/b/c.nix"   # → "c.nix"
builtins.dirOf "/a/b/c.nix"        # → "/a/b"
```

## Set and List Functions

### `builtins.attrNames` / `builtins.attrValues`

```nix
builtins.attrNames { a = 1; b = 2; }    # → [ "a" "b" ]
builtins.attrValues { a = 1; b = 2; }   # → [ 1 2 ]
```

### `builtins.hasAttr` / `builtins.getAttr`

```nix
builtins.hasAttr "x" { x = 1; }         # → true
builtins.getAttr "x" { x = 1; }         # → 1
```

### `builtins.get`

Get attribute with default.

```nix
builtins.get "x" { x = 1; } "default"   # → 1
builtins.get "y" { x = 1; } "default"   # → "default"
```

### `builtins.mapAttrs`

Apply a function to each attribute.

```nix
builtins.mapAttrs (name: value: value * 2) { a = 1; b = 2; }
# → { a = 2; b = 4; }
```

### `builtins.foldl'` / `builtins.foldl`

Reduce a list.

```nix
builtins.foldl' (acc: x: acc + x) 0 [ 1 2 3 4 ]   # → 10
```

### `builtins.listToAttrs`

Convert a list of `{ name; value; }` to an attribute set.

```nix
builtins.listToAttrs [
  { name = "a"; value = 1; }
  { name = "b"; value = 2; }
]
# → { a = 1; b = 2; }
```

### `builtins.zipAttrs`

Merge a list of attribute sets.

```nix
builtins.zipAttrs [ { a = 1; b = 2; } { a = 3; b = 4; } ]
# → { a = [ 1 3 ]; b = [ 2 4 ]; }
```

### `builtins.deepSeq`

Force deep evaluation of a value (for strictness).

```nix
builtins.deepSeq x x
```

## Type Tests

```nix
builtins.isInt v
builtins.isFloat v
builtins.isBool v
builtins.isString v
builtins.isPath v
builtins.isNull v
builtins.isAttrs v
builtins.isList v
builtins.isFunction v
builtins.isCoords v
builtins.isExternal v
builtins.typeOf v    # → "ints", "strings", "lists", "sets", "NULL", "BOOLS", "floats"
```

## Element Tests

```nix
builtins.elem x list           # true if x is in list
builtins.elemAt list index     # element at index (0-based)
builtins.head list             # first element
builtins.tail list             # all but first
builtins.length list           # list length
```

## System and Environment

```nix
builtins.currentSystem         # → "x86_64-linux"
builtins.currentRepos          # → { nixpkgs = "/path"; } (deprecated)
builtins.nixVersion            # → "2.35.1"
builtins.nixPath               # → [ "nixpkgs=/path"; ... ]
```

## Misc

```nix
builtins.abort "error message"           # abort evaluation with error
builtins.trace msg expr                  # print msg, return expr
builtins.warn msg                        # print warning to stderr, return ""
builtins.unreachable                     # abort with "this should be unreachable"
builtins.placeholder "out"               # → "/nix/store/<hash>-name" (for $out in strings)
builtins.isTriviallyCopyable path        # true if path has no symlinks/special files
```

## Gotchas

- **`fetchurl` without hash is not reproducible** — always specify `sha256` for reproducible builds. Without it, the same URL may produce different hashes on different machines if the substituter has a different cached copy.
- **`fetchGit` without `sha256` is impure** — it tracks the current HEAD of the branch, which changes over time. Pin with `sha256` for reproducibility.
- **`import` copies paths to store** — when you `import ./file.nix`, any paths referenced in that file are copied to the store during evaluation. This can be slow for large directories.
- **`builtins` is not importable** — you cannot write `import <builtins>`. Builtins are always in scope.
- **String context matters** — strings produced from path interpolation carry a "context" (set of store paths they reference). Operations like `builtins.substring` strip context.
