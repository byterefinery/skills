# Ecosystem

pkgx is a composable primitive that powers a broader ecosystem of tools.

## dev

`dev` creates "virtual environments" by automatically detecting project dependencies from keyfiles (Cargo.toml, package.json, Gemfile, etc.) and making the right tools available.

```bash
cd my-rust-proj && ls
# Cargo.toml  src/

cargo build
# command not found: cargo

dev
# +rust +cargo

cargo build
# Compiling my-rust-proj v0.1.0
```

Migrate from pkgx^1 shellcode:

```bash
pkgx pkgx^1 deintegrate
pkgx dev integrate
```

- Repo: [github.com/pkgxdev/dev](https://github.com/pkgxdev/dev)

## pkgm

`pkgm` installs pkgx packages to `/usr/local` for persistent, system-wide availability. It installs alongside pkgx.

```bash
pkgm shim git
# created shim: ~/.local/bin/git

cat ~/.local/bin/git
# #!/usr/bin/env -S pkgx -q! git
```

- Repo: [github.com/pkgxdev/pkgm](https://github.com/pkgxdev/pkgm)

## mash

`mash` is a package manager for scripts built on top of pkgx scripting. It distributes reusable scripts that leverage the full Open Source ecosystem.

```bash
pkgx mash upgrade    # upgrade cached packages
pkgx mash prune       # remove older versions
pkgx mash ls          # list downloaded packages
pkgx mash outdated    # list outdated packages
pkgx mash inventory git  # available versions
pkgx mash ensure git  # use system or pkgx version
```

- Repo: [github.com/pkgxdev/mash](https://github.com/pkgxdev/mash)

## pkgo

`pkgo` handles Open Source projects that resist packaging by following installation instructions automatically. It uses pkgx under the hood.

```bash
pkgo stable-diffusion-webui
```

- Repo: [github.com/pkgxdev/pkgo](https://github.com/pkgxdev/pkgo)

## pantry

The pkgx pantry is the metadata repository that describes how to package each project. It contains `package.yml` files that tell pkgx where to find binaries and what dependencies a package has.

```bash
pkgx bk edit deno   # opens deno's package.yml in your editor
```

- Repo: [github.com/pkgxdev/pantry](https://github.com/pkgxdev/pantry)

## Migration from pkgx^1

Key changes in pkgx^2:

- **No shellcode in pkgx** — `dev` is now a separate tool with its own shellcode
- **`env +foo` removed** — use `eval "$(pkgx +foo)"` instead
- **`pkgx install` removed** — use `pkgm` for persistent installs
- **`pkgm shim`** provides the lightweight shim behavior pkgx^1 users may have expected
