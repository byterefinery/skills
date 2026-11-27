# .travis.yml configuration

In addition to command line arguments, `doctr` can be configured using the `.travis.yml` file. Command line arguments take precedence over values in the config file.

## Structure

Use a `doctr` section in your `.travis.yml`:

```yaml
- language: python
- script:
    - set -e
    - py.test
    - cd docs
    - make html
    - cd ..
    - doctr deploy .
- doctr:
    - key-path : 'path/to/key/from/repo/root/path.key'
    - deploy-repo : 'myorg/myrepo'
```

Configuration keys mirror their command line siblings **except** that the leading `--` (and the `--no-` prefix) is dropped:

| CLI flag | Config key |
|---|---|
| `--key-path` | `key-path` |
| `--deploy-repo` | `deploy-repo` |
| `--built-docs` | `built-docs` |
| `--command` | `command` |
| `--branch-whitelist` | `branch-whitelist` |
| `--exclude` | `exclude` |
| `--gh-pages-docs` (deprecated) | `gh-pages-docs` |
| `--token` / `--no-token` | `token` (boolean) |
| `--build-tags` / `--no-build-tags` | `build-tags` (boolean) |
| `--no-require-master` / `--require-master` | `require-master` (boolean) |
| `--no-sync` / `--sync` | `sync` (boolean) |
| `--no-push` / `--push` | `push` (boolean) |

Not config-aware: the positional deploy directory, `--deploy-branch-name`, `--no-temp-dir`, and `--force` (it has a `--no-force` inverse but no config lookup).

Boolean flags automatically get an opposite, exclusive option: passing the flag on the CLI overwrites the config value. For example `sync: False` in the config can be overridden with `--sync` on the command line.

## `branches` — config-only option

`branches` is available from the configuration file and **not** from the command line. It is a list of regular expressions matching branches on which doctr should still deploy (e.g. `.*\.x` deploys all branches like `3.x`, `4.x`).

## Unknown options

If `.travis.yml` contains keys that are not recognized by the parser, doctr prints a warning listing them (as JSON) and continues. This is how you notice typos in the config.

## Precedence

Command line arguments override config values. The deploy directory itself must still be passed as a positional argument on the command line (there is no config key for it).
