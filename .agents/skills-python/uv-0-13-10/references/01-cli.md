# uv 0.13.10 CLI reference

Generated from the `uv --help` output of uv 0.13.10 (tag `0.13.10`). Each command section lists its own options; every command also accepts the shared **Global**, **Cache**, and **Python** option groups, and resolution/install commands additionally accept the **Index**, **Resolver**, **Build**, and **Installer** groups defined below.

## Commands

| Command | Description |
|---|---|
| `uv auth` | Manage authentication |
| `uv run` | Run a command or script |
| `uv init` | Create a new project |
| `uv add` | Add dependencies to the project |
| `uv remove` | Remove dependencies from the project |
| `uv version` | Read or update the project's version |
| `uv sync` | Update the project's environment |
| `uv lock` | Update the project's lockfile |
| `uv export` | Export the project's lockfile to an alternate format |
| `uv tree` | Display the project's dependency tree |
| `uv format` | Format Python code in the project |
| `uv check` | Run checks on the project (type-check with ty) |
| `uv audit` | Audit the project's dependencies (vulnerabilities) |
| `uv tool` | Run and install commands provided by Python packages |
| `uv python` | Manage Python versions and installations |
| `uv pip` | Manage Python packages with a pip-compatible interface |
| `uv venv` | Create a virtual environment |
| `uv build` | Build Python packages into source distributions and wheels |
| `uv publish` | Upload distributions to an index |
| `uv workspace` | Inspect uv workspaces |
| `uv cache` | Manage uv's cache |
| `uv self` | Manage the uv executable |
| `uv help` | Display documentation for a command |

`uvx <tool>` is an alias for `uv tool run <tool>`.

## Global options (all commands)

- `-q, --quiet...` — use quiet output
- `-v, --verbose...` — use verbose output
- `--color <auto|always|never>` — control color in output
- `--system-certs` — load TLS certificates from the platform certificate store
- `--offline` — disable network access
- `--allow-insecure-host <HOST>` — allow insecure connections to a host
- `--no-progress` — hide progress outputs
- `--directory <DIR>` — change to the given directory before running
- `--project <PROJECT>` — discover a project in the given directory
- `--config-file <FILE>` — use the given `uv.toml` for configuration
- `--no-config` — avoid discovering configuration files (`pyproject.toml`, `uv.toml`)
- `-h, --help` / `-V, --version`

## Shared option groups

**Index options** (resolving/install commands):
- `--index <INDEX>` — indexes in addition to the default (URL, configured name, or `name=url`)
- `--default-index <DEFAULT_INDEX>` — the default package index (default `https://pypi.org/simple`)
- `-i, --index-url <URL>` — deprecated, use `--default-index`
- `--extra-index-url <URL>` — deprecated, use `--index`
- `-f, --find-links <LOCATION>` — locations of candidate distributions (flat indexes)
- `--no-index` — ignore the registry index; rely on direct URLs and `--find-links`
- `--index-strategy <first-index|unsafe-first-match|unsafe-best-match>`
- `--keyring-provider <disabled|subprocess>` — use `keyring` for index authentication

**Resolver options**:
- `-U, --upgrade` — allow upgrades, ignoring pinned versions (implies `--refresh`)
- `-P, --upgrade-package <PKG>` — upgrade a specific package (implies `--refresh-package`)
- `--upgrade-group <GROUP>` — upgrade all packages in a dependency group
- `--resolution <highest|lowest|lowest-direct>` — version selection strategy
- `--prerelease <disallow|allow|if-necessary|explicit|if-necessary-or-explicit>`
- `--prerelease-package <PKG=strategy>` — per-package pre-release strategy
- `--fork-strategy <fewest|requires-python>` — multi-version selection across platforms
- `--exclude-newer <DATE|DURATION>` — limit candidates to uploads before a date (also durations, e.g. `1 week`)
- `--exclude-newer-package <PKG=DATE>` — per-package date cutoff
- `--no-sources` — ignore `tool.uv.sources` (lock against publishable metadata)
- `--no-sources-package <PKG>` — ignore sources for specific packages

**Build options**:
- `-C, --config-setting <KEY=VALUE>` — PEP 517 backend settings
- `--config-settings-package <PKG:KEY=VALUE>` — per-package backend settings
- `--no-build-isolation` / `--no-build-isolation-package <PKG>`
- `--no-build` / `--no-build-package <PKG>` — don't build source distributions
- `--no-binary` / `--no-binary-package <PKG>` — don't install pre-built wheels
- `--require-build-hashes` / `--no-require-build-hashes`

**Installer options**:
- `--reinstall` — reinstall all packages (implies `--refresh`)
- `--reinstall-package <PKG>` — reinstall a specific package
- `--link-mode <clone|copy|hardlink|symlink>` — install method from the global cache
- `--compile-bytecode` — compile Python files to bytecode after install

**Cache options**:
- `-n, --no-cache` — use a temporary cache for the duration
- `--cache-dir <DIR>` — path to the cache directory
- `--refresh` / `--refresh-package <PKG>` — refresh cached data

**Python options**:
- `-p, --python <PYTHON>` — the Python interpreter to use
- `--managed-python` / `--no-managed-python` — restrict to managed/system installs
- `--no-python-downloads` — disable automatic Python downloads

## uv init

`uv init [OPTIONS] [PATH]`

- `--name <NAME>` — project name
- `--bare` — only create a `pyproject.toml`
- `--package` / `--no-package` — set up (or not) to be built as a Python package
- `--app` / `--lib` — create a project for an application / a library
- `--script` — create a PEP 723 script
- `--description <DESC>` / `--no-description`
- `--vcs <git|none>` — initialize a version control system
- `--build-backend <uv|hatch|flit|pdm|poetry|setuptools|maturin|scikit>` — build backend (env `UV_INIT_BUILD_BACKEND`)
- `--no-readme` — do not create `README.md`
- `--author-from <auto|git|none>` — fill in the `authors` field
- `--no-pin-python` — do not create `.python-version`
- `--no-workspace` — avoid discovering a workspace, create a standalone project

## uv add

`uv add [OPTIONS] <PACKAGES|--requirements <FILE>>`

- `-r, --requirements <FILE>` — add packages listed in the given files
- `-c, --constraints <FILE>` — constrain versions using requirements files
- `-m, --marker <MARKER>` — apply this marker to all added packages
- `--dev` — add to the `dev` dependency group
- `--optional <EXTRA>` — add to the named extra
- `--group <GROUP>` — add to the named dependency group
- `--editable` — add as editable
- `--raw` — add the dependency as provided (no bounds)
- `--bounds <lower|major|minor|exact>` — kind of version specifier to add
- `--rev <REV>` / `--tag <TAG>` / `--branch <BRANCH>` — Git reference to use
- `--lfs` — use Git LFS when adding from Git
- `--extra <EXTRA>` — enable extras for the dependency
- `--no-sync` — avoid syncing the environment
- `--locked` / `--frozen` — see lockfile flags
- `--active` — prefer the active virtual environment
- `--package <PACKAGE>` — add to a specific workspace package
- `--script <SCRIPT>` — add to a PEP 723 script rather than a project
- `--workspace` / `--no-workspace` — add as (or not as) a workspace member
- `--no-install-project` / `--no-install-workspace` / `--no-install-local` / `--no-install-package <PKG>`

## uv remove

`uv remove [OPTIONS] <PACKAGES>...`

- `--dev` — remove from the `dev` group
- `--optional <EXTRA>` — remove from the named extra
- `--group <GROUP>` — remove from the named group
- `--no-sync`, `--active`, `--locked`, `--frozen`, `--package <PACKAGE>`, `--script <SCRIPT>`

## uv lock

`uv lock [OPTIONS]`

- `--check` — check if the lockfile is up-to-date
- `--check-exists` — assert `uv.lock` exists without checking freshness
- `--dry-run` — perform a dry run, without writing the lockfile
- `--script <SCRIPT>` — lock a PEP 723 script rather than the current project
- plus **Index**, **Resolver**, **Build**, **Installer**, **Cache**, **Python** options

## uv sync

`uv sync [OPTIONS]`

- `--extra <EXTRA>` / `--all-extras` / `--no-extra <EXTRA>`
- `--no-dev` / `--only-dev` / `--group <G>` / `--no-group <G>` / `--no-default-groups` / `--only-group <G>` / `--all-groups`
- `--no-editable` / `--no-editable-package <PKG>` — install editables as non-editable
- `--inexact` — do not remove extraneous packages
- `--active` — sync the active virtual environment
- `--no-install-project` / `--no-install-workspace` / `--no-install-local` / `--no-install-package <PKG>`
- `--locked` / `--frozen`
- `--dry-run` — without writing the lockfile or modifying the environment
- `--all-packages` / `--package <PACKAGE>` — workspace scope
- `--script <SCRIPT>` — sync the environment for a PEP 723 script
- `--python-platform <PLATFORM>` — platform for which requirements should be installed (e.g. `x86_64-manylinux_2_28`, `aarch64-apple-darwin`, `windows`, `macos`)
- `--check` — check if the environment is synchronized with the project
- `--output-format <text|json>`

## uv run

`uv run [OPTIONS] [COMMAND]`

- `--extra`, `--all-extras`, `--no-extra`, `--no-dev`, `--only-dev`, `--group`, `--no-group`, `--no-default-groups`, `--only-group`, `--all-groups`
- `-m, --module` — run a Python module
- `--no-editable` / `--no-editable-package <PKG>`
- `--exact` — perform an exact sync, removing extraneous packages
- `--env-file <FILE>` / `--no-env-file` — load `.env` variables
- `-w, --with <PKG>` — run with the given packages installed
- `--with-editable <PKG>` — run with the given packages in editable mode
- `--with-requirements <FILE>` — run with packages listed in the given files
- `--isolated` — run in an isolated virtual environment
- `--active` — prefer the active virtual environment
- `--no-sync` / `--locked` / `--frozen`
- `-s, --script` — run the given path as a Python script
- `--gui-script` — run the given path as a Python GUI script
- `--all-packages` / `--package <PACKAGE>` — workspace scope
- `--no-project` — avoid discovering the project or workspace (must precede the command)
- `--python-platform <PLATFORM>`
- plus **Index**, **Resolver**, **Installer**, **Build**, **Cache**, **Python** options

## uv export

`uv export [OPTIONS]`

- `--format <requirements.txt|pylock.toml|cyclonedx1.5>`
- `--all-packages` / `--package <PACKAGE>` — workspace scope
- `--prune <PACKAGE>` — prune the given package from the tree
- `--extra <EXTRA>` / `--all-extras` / `--no-extra <EXTRA>`
- `--no-dev` / `--only-dev` / `--group <G>` / `--no-group <G>` / `--no-default-groups` / `--only-group <G>` / `--all-groups`
- `--no-annotate` — exclude `# via` source comments
- `--no-header` — exclude the command header comment
- `--emit-index-url` / `--emit-find-links`
- `--no-editable` / `--no-editable-package <PKG>`
- `--no-hashes` — omit hashes
- `-o, --output-file <FILE>`
- `--no-emit-project` / `--no-emit-workspace` / `--no-emit-local` / `--no-emit-package <PKG>`
- `--locked` / `--frozen`
- `--script <SCRIPT>` — export dependencies for a PEP 723 script

## uv build

`uv build [OPTIONS] [SRC]`

- `--package <PACKAGE>` / `--all-packages` — workspace scope
- `-o, --out-dir <DIR>` — output directory (default `dist/`)
- `--sdist` / `--wheel` — build only the given distribution type
- `--no-build-logs` — hide build backend logs
- `--force-pep517` — always build through PEP 517 (skip the uv backend fast path)
- `--clear` — clear the output directory before the build
- `--no-create-gitignore` — do not create `.gitignore` in the output dir
- `-b, --build-constraints <FILE>` — constrain build dependencies
- `--require-hashes` / `--no-verify-hashes`

## uv publish

`uv publish [OPTIONS] [FILES]...` (default `dist/*`, globs accepted)

- `--index <NAME>` — index from configuration to publish to
- `-u, --username <U>` / `-p, --password <P>` / `-t, --token <T>`
- `--trusted-publishing <automatic|always|never>`
- `--keyring-provider <disabled|subprocess>`
- `--publish-url <URL>` — upload endpoint (not the index URL)
- `--check-url <URL>` — check an index for existing files to skip duplicates
- `--dry-run`
- `--no-attestations`

## uv format / uv check / uv audit (0.13)

`uv format [OPTIONS] [-- EXTRA_ARGS]...` — format Python code with Ruff.

- `--check` — check without applying changes
- `--diff` — show a diff without applying
- `--version <VERSION>` — the Ruff version to use
- `--exclude-newer <DATE>` — limit candidate Ruff versions
- Extra arguments are passed through to Ruff after `--`

`uv check [OPTIONS]` — run checks on the project (type-checking with ty).

- `--fix` — apply safe fixes to resolve type-checking errors
- `--all-packages` / `--package <PACKAGE>` — workspace scope
- `--script <SCRIPT>` — run checks for a PEP 723 script
- `--ty-version <VERSION>` — the ty version to use
- group/extras options as `uv sync`, plus `--locked`, `--frozen`, `--no-sync`, `--no-install-project`, `--isolated`

`uv audit [OPTIONS]` — audit the project's dependencies for known vulnerabilities.

- `--no-extra <EXTRA>` / `--no-dev` / `--no-group <G>` / `--no-default-groups` / `--only-group <G>` / `--only-dev`
- `--locked` / `--frozen`
- `--output-format <text|json|sarif>`
- `--ignore <ID>` — ignore a vulnerability by ID
- `--ignore-until-fixed <ID>` — ignore only while no fix is available
- `--service-format <osv>` / `--service-url <URL>` — vulnerability service (OSV)
- `--script <SCRIPT>` — audit a PEP 723 script
- `--python-version <VER>` / `--python-platform <PLATFORM>` — audit for a specific target

## uv version (0.13)

`uv version [OPTIONS] [VALUE]` — read or update the project's version.

- `[VALUE]` — set the project version to this value
- `--bump <major|minor|patch|stable|alpha|beta|rc|post|dev[=VALUE]>` — bump with the given semantics
- `--dry-run` — don't write the new version
- `--short` — only show the version
- `--output-format <text|json>`
- `--no-sync` / `--active` / `--locked` / `--frozen` / `--package <PACKAGE>`

## uv tree

`uv tree [OPTIONS]`

- `--universal` — platform-independent tree
- `--format <text|json>`
- `-d, --depth <N>` — maximum display depth (default 255)
- `--prune <PKG>` — prune a package from the display
- `--package <PKG>` — display only the specified packages
- `--no-dedupe` — do not de-duplicate repeated dependencies
- `--invert` — show reverse dependencies (who depends on the package)
- `--outdated` — show the latest available version of each package
- `--show-sizes` — show compressed wheel sizes
- group/extras options as `uv sync`, plus `--locked`, `--frozen`, `--script <SCRIPT>`
- `--python-version <VER>` / `--python-platform <PLATFORM>` — filter the tree

## uv workspace (0.13)

`uv workspace <COMMAND>` — inspect uv workspaces.

- `uv workspace metadata` — view metadata about the current workspace
- `uv workspace dir <MEMBER>` — display the path of a workspace member
- `uv workspace list` — list the members of a workspace

## uv venv

`uv venv [OPTIONS] [PATH]`

- `--no-project` — avoid discovering a project or workspace
- `--seed` — install seed packages (`pip`, `setuptools`, `wheel`)
- `-c, --clear` — remove existing files at the target path
- `--force` — allow `--clear` to remove a non-virtual-environment directory
- `--allow-existing` — preserve existing files at the target path
- `--prompt <PROMPT>` — alternative prompt prefix
- `--system-site-packages`
- `--relocatable` — make the environment relocatable
- `--link-mode <clone|copy|hardlink|symlink>`

## uv tool

`uv tool <COMMAND>`

- `run` — run a command provided by a Python package (alias `uvx`)
- `install` — install a tool user-wide
- `upgrade` — upgrade installed tools
- `list` — list installed tools
- `audit` — audit installed tools and their dependencies
- `uninstall` — uninstall a tool
- `update-shell` — add the tool executable directory to `PATH` in shell configs
- `dir` — show the path to the uv tools directory

`uv tool run` (and `uvx`) key options:

- `--from <PKG>` — use the given package to provide the command
- `-w, --with <PKG>` / `--with-editable <PKG>` / `--with-requirements <FILE>` — extra packages
- `-c, --constraints <FILE>` / `-b, --build-constraints <FILE>` / `--overrides <FILE>`
- `--isolated` — run in an isolated environment, ignoring installed tools
- `--env-file <FILE>` / `--no-env-file`
- `--lfs` — use Git LFS for Git sources
- `--python-platform <PLATFORM>`

`uv tool install` additionally supports `package@version` and `package@latest` specifiers, plus `--with-executables-from <PKG[,PKG...]>` to install executables from additional packages into the same tool environment. `uv tool upgrade` supports `--reinstall` / `--reinstall-package <PKG>`.

## uv python

`uv python <COMMAND>`

- `list` — list available Python installations (`--only-installed`, `--all-versions`, `--all-platforms`, request filter, e.g. `3.13`, `pypy`)
- `install` — download and install Python versions (requests: `3`, `3.12`, `3.12.3`, `>=3.8,<3.10`, `pypy`, multiple versions at once; `--default` also installs `python`/`python3` executables)
- `upgrade` — upgrade managed Python to the latest supported patch release (e.g. `uv python upgrade 3.12`, or all)
- `find` — find a Python executable (`--system` to ignore virtual environments)
- `pin` — pin to a specific Python version (writes `.python-version`; `--global` for the user config dir; `--allow-existing`)
- `dir` — show the uv Python installation directory
- `uninstall` — uninstall Python versions
- `update-shell` — add the Python executable directory to `PATH` in shell configs

## uv pip

`uv pip <COMMAND>` — pip-compatible interface (operates on an environment, bypassing `uv.lock`).

- `compile` — compile a `requirements.in` to `requirements.txt` or `pylock.toml`
- `sync` — sync an environment with a `requirements.txt` or `pylock.toml`
- `install` — install packages into an environment
- `uninstall` — uninstall packages from an environment
- `freeze` — list installed packages in requirements format
- `list` — list installed packages in tabular format
- `show` — show information about one or more installed packages
- `tree` — display the dependency tree for an environment
- `check` — verify installed packages have compatible dependencies

Environment selection for `uv pip` commands: `--python <PYTHON>`, `--python-preference`, `--system` (the system environment), `--active` (the active virtual environment).

## uv cache

`uv cache <COMMAND>`

- `clean [PACKAGE]...` — clear the cache (all entries or those linked to specific packages; `--force` ignores in-use checks)
- `prune` — prune dangling cache entries and cached environments
- `dir` — show the cache directory
- `size` — show the cache size

## uv self

`uv self <COMMAND>`

- `update` — update uv
- `version` — display uv's version
