# doctr deploy

`doctr deploy <deploy_directory>` is run on Travis in the same build that builds your docs. It refuses to run unless `TRAVIS_JOB_NUMBER` is set (unless `--force`). The positional `<deploy_directory>` is required — it is where the built HTML lands on the deploy branch (e.g. `.` for the root of `gh-pages`, or `docs`).

## Flags

| Flag | Default | Behavior |
|---|---|---|
| positional `deploy_directory` | required | Directory to deploy HTML to on the deploy branch. Also accepted via deprecated `--gh-pages-docs` (backwards compatibility only) |
| `--token` | off | Push using a personal access token (matches `doctr configure --token`). Default: SSH deploy key |
| `--key-path` | auto | Path of the encrypted deploy key file. Default: `github_deploy_key_<org>_<repo>.enc` |
| `--built-docs` | auto-detect | Location of the built HTML to deploy. If omitted, doctr globs `**/*build/html` (recursive) and uses the first match — works for Sphinx only; raises if none found. A single file is also allowed |
| `--deploy-branch-name` | auto | Branch to deploy to. Default: `master` for `*.github.io`, `*.github.com`, and wiki repos; `gh-pages` otherwise |
| `--deploy-repo` | build repo | Repo to deploy to (default: the repo doctr runs from). Use `org/repo.wiki` for a wiki |
| `--branch-whitelist` | `master` | Branches to deploy from (regex matched against `$TRAVIS_BRANCH`, via `re.compile(x).match()`). Pass no arguments to deploy from no branch (used with `--build-tags`). Should generally go last in the call |
| `--no-require-master` | off | Allow pushes from branches other than master (deploys from any branch) |
| `--command` | none | Command to run before committing and pushing, from the deploy repository/branch, with `shell=True`. Files it creates must be added to the index manually |
| `--no-sync` | sync on | Don't sync any files — generally used with `--command` when the command itself syncs files. Any files to commit should be added to the index |
| `--no-temp-dir` | temp dir on | Don't copy `--built-docs` to a temporary directory before syncing (default copies it, fixing syncing of committed files) |
| `--no-push` | push on | Run all steps except the final push — useful for debugging |
| `--build-tags` | off | Deploy on tag builds (`$TRAVIS_TAG` set). Default: no deploy on tags. Still deploys from branches unless `--branch-whitelist` with no args is passed |
| `--gh-pages-docs` | none | **Deprecated** — directory to deploy to; pass the deploy directory as a positional argument instead. Kept for backwards compatibility |
| `--exclude` | none | Files/directories from `--built-docs` that are not copied (relative paths, `nargs='+'`) |
| `--force` | off | Run even if not on Travis |
| `--tmp-dir` | removed | **Removed** — passing it errors out (doctr no longer uses a temporary directory when deploying; it always syncs via the log file) |

## Behavior pipeline

1. Prints the doctr version, checks Travis presence (unless `--force`).
2. Reads `.travis.yml` config (see [03-travis-yml-config](03-travis-yml-config.md)); unknown keys are printed as a warning.
3. Determines the deploy branch (see flags table) and the key/env var names from the deploy repo.
4. `setup_GitHub_push()` — checks fork status via the GitHub API, sets git user name/email if unset (`Doctr (Travis CI)` / `drdoctr@users.noreply.github.com`), adds a `doctr_remote` remote (SSH for deploy key; HTTPS with token for `--token`; read-only HTTPS when push is not allowed), fetches it, and returns `canpush`.
5. `git stash --all`, then checks out the deploy branch (creating it if missing — orphan branch with a `.nojekyll` file committed and pushed when possible).
6. Sync: copies `--built-docs` into the deploy directory via `sync_from_log()`. Files previously synced (recorded in `<deploy_dir>/.doctr-files`) but absent from the new build are removed. Excluded paths are neither added nor removed, even if recorded in the log file. The log file itself is committed with the docs.
7. If `--command`: runs it (shell=True) on the deploy branch.
8. `commit_docs()` — commits staged changes with a message containing the Travis build number, repo slug, branch/tag name, commit SHA, job URL, and the doctr command that was run. Returns True only if changes were committed (checked via `git diff-index --cached --quiet HEAD`).
9. If changes were committed: pushes to the deploy branch with retries (5 in 1.9.0; pulls with `-s recursive -X ours` first), unless `--no-push` or `canpush` is False (then prints "Don't have permission to push. Not trying."). If no changes were committed: prints "The docs have not changed. Not updating".
10. Always returns to the original commit and pops the stash (errors ignored if nothing was stashed).

## Push rights (`determine_push_rights()`)

Push is refused when:

- On a tag build without `--build-tags` (prints "The docs are not pushed on tag builds...")
- The branch doesn't match any whitelist regex (default: `master`)
- It's a PR build (`TRAVIS_PULL_REQUEST != "false"` — uses `$TRAVIS_PULL_REQUEST_BRANCH` for the branch name, not `$TRAVIS_BRANCH`)
- The repo is a fork (checked via GitHub API; if that check fails, the build errors anyway — ignorable)
- The last commit on the branch was made by doctr (author email `drdoctr@users.noreply.github.com`) — avoids infinite build loops

Note: whitelist regexes use `re.compile(x).match()` (prefix match, not fullmatch).

## Sync details (`sync_from_log()`)

- Returns `(added, removed)` — `added` includes every file synced plus the log file; `removed` is every file in the log that was deleted from the deploy directory because it wasn't in the new build.
- If the log file doesn't exist, no files are removed (assumed first run).
- Excluded paths: neither added nor removed, even if recorded in the log file.
- A single-file `--built-docs` is supported; it is copied to the deploy directory and the parent directory is created as needed.
