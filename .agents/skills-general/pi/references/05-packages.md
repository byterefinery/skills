# Pi Packages

Pi packages bundle extensions, skills, prompt templates, and themes so you can share them through npm or git.

## Install and Manage

```bash
pi install npm:@foo/bar@1.0.0
pi install git:github.com/user/repo@v1
pi install https://github.com/user/repo
pi install /absolute/path/to/package
pi install ./relative/path/to/package

pi remove npm:@foo/bar
pi list                     # show installed packages from settings
pi update                   # update pi only
pi update --all             # update pi, update packages, reconcile pinned git refs
pi update --extensions      # update packages only
pi update --models          # refresh model catalogs only
pi update --self            # update pi only
pi update --self --force    # reinstall pi even if current
pi update npm:@foo/bar      # update one package
```

By default, `install` and `remove` write to user settings (`~/.pi/agent/settings.json`). Use `-l` to write to project settings (`.pi/settings.json`).

To try a package without installing: `pi -e npm:@foo/bar` (temporary, current run only).

## Package Sources

### npm

```
npm:@scope/pkg@1.2.3
npm:pkg
```

Versioned specs are pinned and skipped by package updates. User installs go under `~/.pi/agent/npm/`; project installs under `.pi/npm/`.

### git

```
git:github.com/user/repo@v1
git:git@github.com:user/repo@v1
https://github.com/user/repo@v1
ssh://git@github.com/user/repo@v1
```

Refs are pinned tags or commits. `pi update --extensions` reconciles existing clones to the configured ref but does not move them to newer refs. Use `pi install git:host/user/repo@new-ref` to update to a new pinned ref.

SSH URLs use configured SSH keys (respects `~/.ssh/config`). For non-interactive runs, set `GIT_TERMINAL_PROMPT=0` and `GIT_SSH_COMMAND`.

### Local Paths

```
/absolute/path/to/package
./relative/path/to/package
```

Relative paths resolve against the settings file. If the path is a file, it loads as a single extension. If a directory, pi loads resources using package rules.

## Creating a Pi Package

Add a `pi` manifest to `package.json` or use conventional directories. Include the `pi-package` keyword for discoverability.

```json
{
  "name": "my-package",
  "keywords": ["pi-package"],
  "pi": {
    "extensions": ["./extensions"],
    "skills": ["./skills"],
    "prompts": ["./prompts"],
    "themes": ["./themes"]
  }
}
```

### Gallery Metadata

For the [package gallery](https://pi.dev/packages), add `video` or `image` fields:

```json
{
  "pi": {
    "extensions": ["./extensions"],
    "video": "https://example.com/demo.mp4",
    "image": "https://example.com/screenshot.png"
  }
}
```

Video (MP4) takes precedence over image.

## Convention Directories

Without a `pi` manifest, pi auto-discovers from:

- `extensions/` — loads `.ts` and `.js` files
- `skills/` — recursively finds `SKILL.md` folders and loads top-level `.md` files
- `prompts/` — loads `.md` files
- `themes/` — loads `.json` files

## Dependencies

Runtime dependencies belong in `dependencies` in `package.json`. Pi installs packages with `npm install`, so dependencies install automatically.

Pi bundles core packages. List them in `peerDependencies` with `"*"` range and do not bundle: `@earendil-works/pi-ai`, `@earendil-works/pi-agent-core`, `@earendil-works/pi-coding-agent`, `@earendil-works/pi-tui`, `typebox`.

Other pi packages must be bundled. Add to `dependencies` and `bundledDependencies`:

```json
{
  "dependencies": { "shitty-extensions": "^1.0.1" },
  "bundledDependencies": ["shitty-extensions"],
  "pi": {
    "extensions": ["extensions", "node_modules/shitty-extensions/extensions"]
  }
}
```

## Package Filtering

Filter what a package loads using object form in settings:

```json
{
  "packages": [
    "npm:simple-pkg",
    {
      "source": "npm:my-package",
      "extensions": ["extensions/*.ts", "!extensions/legacy.ts"],
      "skills": [],
      "prompts": ["prompts/review.md"],
      "themes": ["+themes/legacy.json"]
    }
  ]
}
```

- Omit a key to load all of that type
- Use `[]` to load none
- `!pattern` excludes matches
- `+path` force-includes an exact path
- `-path` force-excludes an exact path

## Enable and Disable Resources

Use `pi config` to enable/disable extensions, skills, prompts, and themes from installed packages and local directories. `pi config` starts in global settings; press Tab to switch between global and project-local modes. Use `pi config -l` to start in project overrides.

## Scope and Deduplication

Packages can appear in both global and project settings. If the same package appears in both, the project entry wins unless it has `autoload: false`, in which case it is applied as a delta over the global entry.
