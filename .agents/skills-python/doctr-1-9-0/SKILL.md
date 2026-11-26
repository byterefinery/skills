---
name: doctr-1-9-0
description: Deploys documentation (or any website) to GitHub Pages from Travis CI. Use when setting up or troubleshooting automated docs deployment with doctr, including doctr configure key generation, .travis.yml setup, and doctr deploy options like branch whitelists, tag builds, and separate deploy repos.
license: Apache-2.0
compatibility: Requires Python 3.5+; runs on Travis CI for deploy (doctr configure runs locally)
---

# doctr 1.9.0

## Overview

Doctr automatically deploys docs from Travis CI to GitHub Pages, handling key generation, SSH deploy keys, and syncing files to the `gh-pages` branch. It works with any site that can be built on Travis CI (Sphinx is auto-detected but not required). Two commands: `doctr configure` (run locally, once) and `doctr deploy` (run in `.travis.yml`).

## Usage

Install: `pip install doctr` or `conda install -c conda-forge doctr`. Requires Python 3.5+.

### One-time setup

```bash
doctr configure
```

Prompts for GitHub username/password and the repo org/name to deploy docs for. It generates an encrypted deploy key file (default name `github_deploy_key_<org>_<repo>.enc`) and prints the secure environment variable plus instructions. Commit the key file and edit `.travis.yml` with the printed text:

```yaml
language: python
python:
  - 3.6

sudo: false
env:
  global:
    secure: "<secure key from doctr configure>"

script:
  - set -e
  - pip install doctr
  - cd docs
  - make html
  - cd ..
  - doctr deploy . --built-docs path/to/built/html/
```

`doctr configure` options: `--token` (use a personal access token instead of a deploy key — grants read/write on all public repos for the user, not recommended), `--no-upload-key`, `--no-authenticate`, `--key-path PATH`, `--travis-tld {com|org}`, `--force`.

### Deploy options (`doctr deploy`)

Positional: `deploy_directory` — where to place the HTML on gh-pages. Key flags:

- `--built-docs PATH` — location of built HTML; omit only for Sphinx (auto-detected)
- `--branch-whitelist [BRANCH ...]` — branches to deploy from (default `master`; no args = no branch, used with tag builds)
- `--no-require-master` — allow deploying from any branch
- `--build-tags` — deploy on tag builds (`$TRAVIS_TAG`)
- `--deploy-repo REPO` / `--deploy-branch-name NAME` — deploy elsewhere (default branch `gh-pages`, or `master` for `*.github.io` and wiki repos)
- `--command CMD` — run a command after sync, before commit/push
- `--no-sync`, `--no-push` (debugging), `--exclude FILE [FILE ...]`, `--force` (run outside Travis), `--key-path PATH`, `--token`

`.travis.yml` can also hold a `doctr:` section with the same parameters (dashes and `--no-` prefixes dropped), plus `branches` — a list of regexes for branches that should still deploy. Command line arguments take precedence over the config file.

### Recipes

See [01-recipes](references/01-recipes.md) for deploying from any branch, non-master branches, git tags, a separate repo, repos without admin access, post-processing on gh-pages, GitHub wikis, and `*.github.io` pages.

## Gotchas

- Put `doctr deploy` in the `script:` section of `.travis.yml`, not `after_success` — an `after_success` failure does not fail the build.
- Add `set -e` to `script:` so doctr doesn't run when the docs build fails.
- Doctr only deploys from `master` by default and never on pull requests from forks (Travis hides encrypted env vars there); push branch PRs to the main repo to test them.
- Deploy keys can push to any branch in the repo — enable branch protection for `gh-pages`.
- `--gh-pages-docs` is deprecated; pass the deploy directory as the first positional argument instead.
- Do not commit `.travis.yml` to both the `master` and `source` branches of a `*.github.io` repo, or Travis will loop infinitely.

## References

- [01-recipes](references/01-recipes.md) — branch/tag deployment, separate repos, wikis, github.io pages
- https://drdoctr.github.io/doctr/docs/ — full documentation (commandline, recipes, API)
