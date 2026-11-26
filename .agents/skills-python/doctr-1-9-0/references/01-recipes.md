# Doctr recipes

Adapted from the official docs (`docs/recipes.rst` in the doctr 1.9.0 repo).

## Deploy docs from any branch

Doctr only deploys from `master` by default. To deploy other branches to per-branch directories:

```yaml
- if [[ "${TRAVIS_BRANCH}" == "master" ]]; then
    doctr deploy docs;
  else
    doctr deploy --no-require-master "docs-$TRAVIS_BRANCH";
  fi
```

Branch docs are not removed after merge — clean up manually. Branches on forks cannot deploy (Travis does not expose encrypted env vars to fork pull requests); push the branch to the main repo first.

## Deploy from a non-master default branch

Use `--branch-whitelist`; it accepts any number of arguments, so put it last in the call:

```yaml
- doctr deploy --built-docs build/ . --branch-whitelist develop
```

## Deploy from git tags

Travis runs separate builds for pushed tags. Enable with `--build-tags` (`$TRAVIS_TAG` is set on tag builds):

```yaml
- if [[ -z "$TRAVIS_TAG" ]]; then
    DEPLOY_DIR=dev;
  else
    DEPLOY_DIR="version-$TRAVIS_TAG";
  fi
- doctr deploy --build-tags --built-docs build/ $DEPLOY_DIR
```

To deploy only tags (e.g., to `latest`), pass `--branch-whitelist` with no arguments:

```yaml
- doctr deploy latest --built-docs build/ --build-tags --branch-whitelist
```

## Deploy to a separate repo

Specify both the build and deploy repository in `doctr configure` (admin access to the deploy repo is needed to upload the key). Without admin access, run `doctr configure --no-upload-key` — it prints the public deploy key and the URL of the GitHub form where an admin can add it. In `.travis.yml`:

```yaml
- doctr deploy --deploy-repo <deploy repo> deploy_dir
```

## Setting up a repo you don't have admin access to

Run `doctr configure --no-upload-key` (no GitHub credentials required), commit the `github_deploy_key_org_repo.enc` file and `.travis.yml` changes, open a pull request, and ask the repo owner to add the printed public key as a deploy key. The key is public, so posting it in the PR is safe.

## Post-processing on gh-pages

Run any command after sync but before commit/push with `--command`:

```bash
doctr deploy --command 'post-process.py' deploy_dir
```

To skip syncing entirely and use your own deploy tool (while still letting Doctr manage the key):

```bash
doctr deploy --no-sync --command 'command to deploy' deploy_dir
```

The command must `git add` any files it wants committed.

## Deploying to a GitHub wiki

Use `org/repo.wiki` as the deploy repo in `doctr configure`, then:

```bash
doctr deploy --deploy-repo org/repo.wiki .
```

The wiki uses the same deploy key as the repo itself.

## Using doctr with `*.github.io` pages

GitHub serves the `master` branch of `<name>/<name>.github.io` at `<name>.github.io`. Keep source files on a custom branch (e.g., `source`) and output HTML on `master`:

1. Create and push a `source` branch holding the website sources.
2. Set `source` as the default branch in GitHub settings.
3. Run `doctr configure` on the `source` branch; set both source and deploy repos to `<org>/<name>.github.io`.
4. Commit the encryption key and `.travis.yml` to `source` only — a `.travis.yml` on both branches causes an infinite Travis build loop.
5. Whitelist the `source` branch in the deploy call:

```bash
doctr deploy --branch-whitelist source --built-docs output-directory/ .
```
