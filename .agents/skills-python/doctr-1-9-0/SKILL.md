---
name: doctr-1-9-0
description: >
  Doctr 1.9.0 — deploy documentation or any website built on Travis CI to GitHub
  pages. Use when setting up automatic docs deployment from Travis CI to the
  gh-pages branch of a GitHub repo, *.github.io sites, or GitHub wikis; configuring
  SSH deploy keys or personal access tokens; writing .travis.yml deploy scripts;
  deploying from non-master branches, git tags, or separate repos; or calling the
  Python API. Covers the doctr configure and doctr deploy commands, .travis.yml
  configuration, sync/log-file behavior, recipes, and the Python API. Triggers on
  doctr, drdoctr, Travis CI to GitHub pages, gh-pages deployment, docs deployment,
  deploy key, secure env var, travis-ci.com, travis-ci.org.
license: MIT
compatibility: >
  Python 3.5+; dependencies pyyaml, requests, cryptography. Needs git and ssh on
  the Travis build host plus GitHub and Travis CI accounts with repo access. Runs
  locally for doctr configure and on Travis for doctr deploy.
metadata:
  tags:
    - travis-ci
    - github-pages
    - deployment
    - documentation
    - python
---

# doctr 1.9.0

## Overview

Doctr is a tool for automatically deploying docs from Travis CI to GitHub pages. It manages the complicated tasks of generating, encrypting, managing SSH deploy keys, and syncing files to the `gh-pages` branch. It was designed for documentation but can deploy any kind of website built on Travis CI (e.g. a blog or static site generator output). It is not just for Sphinx — it works with any build that produces HTML on Travis.

Two commands, run in two different places:

- **`doctr configure`** — run locally, interactively. Generates the encrypted deploy key (or personal access token), prints the exact `.travis.yml` lines to add, and tells you what to commit. Does not push anything.
- **`doctr deploy <dir>`** — run on Travis in the same build that builds your docs. Decrypts the key, syncs the built HTML into the deploy directory, commits, and pushes to the `gh-pages` branch (or other deploy branch).

Key concepts:

- **Auth** — SSH deploy key by default (recommended; grants push access to one repo only) or a personal access token via `--token` (not recommended; grants read/write to all public repos of the user). Keys are RSA 4096-bit, Fernet-encrypted to a `.enc` file whose Fernet key is encrypted to the Travis public key as a secure env var.
- **Sync** — files in `--built-docs` are copied into the deploy directory; a `.doctr-files` log file records what was synced, and stale files (in the log but not in the new build) are removed.
- **Defaults** — deploys to the `gh-pages` branch of the same repo, from the `master` branch only, on push builds only (not PRs or forks).

## Usage

Install:

```bash
pip install doctr        # or: conda install -c conda-forge doctr
```

Then configure once locally:

```bash
doctr configure
```

This prompts for GitHub credentials (device authorization flow in 1.9.0), the build repo, and the deploy repo (defaults to the build repo). It prints the secure env var and `.travis.yml` lines to add — e.g.:

```yaml
env:
  global:
    - secure: "<secure key from doctr configure>"
script:
  - set -e
  - pip install doctr
  - cd docs && make html && cd ..
  - doctr deploy . --built-docs path/to/built/html/
```

Commit the generated `.enc` key file and the `.travis.yml` changes; push to GitHub. Travis builds then automatically build and deploy the docs. The deploy directory is passed as a positional argument (e.g. `doctr deploy .` for root, or `doctr deploy docs`).

Common deploy invocations:

```bash
doctr deploy . --built-docs path/to/built/html/   # default: same repo, gh-pages
doctr deploy .                                     # auto-detect Sphinx build dir
doctr deploy docs --built-docs build/              # custom deploy dir
doctr deploy latest --built-docs build/ --build-tags --branch-whitelist   # tags only
```

`doctr configure` and `doctr deploy` also accept a `doctr:` section in `.travis.yml` for defaults (command line takes precedence) — see [03-travis-yml-config](references/03-travis-yml-config.md).

## Gotchas

- **Add `set -e` to `script:`** — prevents doctr from running when the docs build fails. Put `doctr deploy .` in `script:`, not `after_success`; `after_success` will not fail the build.
- **`doctr configure` is local and interactive** — it errors on Travis unless `--force` is passed. It requires GitHub credentials (device flow) unless `--no-authenticate` is used, which cannot be used for private repos.
- **`doctr deploy` only runs on Travis** (checks `TRAVIS_JOB_NUMBER`) unless `--force` is passed.
- **Deploys from `master` only by default** — use `--branch-whitelist <branches>`, the config `branches:` list, or `--no-require-master` for other branches. Tag builds need `--build-tags` (default: no deploy on tags).
- **No pushes from forks or PRs** — Travis does not expose secure env vars to PR builds from forks; doctr also checks the repo is not a fork via the GitHub API and refuses to push on PR/fork builds.
- **`--token` is not recommended** — a personal access token grants read/write access to all public repos of the user, while a deploy key grants push access to one repository only.
- **Private repos need authentication** — `doctr configure` generates a temporary personal access token for Travis and deletes it immediately (you will get an email from GitHub about it). `--no-authenticate` is not supported for private repos.
- **1.9.0 uses the GitHub device authorization flow** — username/password login is no longer supported; re-run `doctr configure` if you see "The two-factor authentication code has expired" or rate-limit errors (wait an hour).
- **Push retries are 5** (increased from 3 in 1.9.0) — race conditions from concurrent builds are handled by retry; a failure still exits with "Giving up...".
- **Infinite loop prevention** — doctr does not commit or push when the last commit on the branch was made by doctr (author email `drdoctr@users.noreply.github.com`). This matters for `*.github.io` repos deployed from a separate branch.
- **`--gh-pages-docs` is deprecated** — pass the deploy directory as a positional argument instead. `--tmp-dir` was removed; passing it errors out.
- **`--command` runs on the deploy branch, before committing** — with `shell=True`. Files it creates must be added to the index manually (they are not committed otherwise). Use `--no-sync` when the command itself syncs files.
- **`--exclude` paths are relative to `--built-docs`** — excluded files are neither synced nor removed even if recorded in the log file.
- **The `.doctr-files` log file is committed** into the deploy directory — it records what was synced so stale files can be removed on the next run. Deleting it makes doctr treat the next run as a first run (no removals; everything is re-added).
- **Key/env-var naming** — env var `DOCTR_DEPLOY_ENCRYPTION_KEY_{ORG}_{REPO}` and key file `github_deploy_key_{org}_{repo}.enc` (special chars → underscores, uppercased). Legacy `DOCTR_DEPLOY_ENCRYPTION_KEY` and `github_deploy_key.enc` are still supported as fallbacks.
- **Deploy branch default** — `gh-pages` for regular repos; `master` for `*.github.io`, `*.github.com`, and wiki repos (`org/repo.wiki`). Override with `--deploy-branch-name`.

## References

- [01-configure-command](references/01-configure-command.md) — full configure flow, flags, key generation, private repos, auth details
- [02-deploy-command](references/02-deploy-command.md) — deploy flags reference, sync behavior, commit message, push retries
- [03-travis-yml-config](references/03-travis-yml-config.md) — `doctr:` section in `.travis.yml`, key mapping rules, precedence
- [04-recipes](references/04-recipes.md) — deploy from any branch, non-master branches, tags, separate repos, wikis, github.io pages, post-processing
- [05-python-api](references/05-python-api.md) — `doctr.local` and `doctr.travis` public functions
- [06-security-and-auth](references/06-security-and-auth.md) — encryption pipeline, deploy keys vs tokens, env var naming, revocation
