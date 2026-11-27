# Recipes

All recipes below are from the doctr docs (`docs/recipes.rst`). They assume `doctr configure` has already been run and the secure env var + deploy call are in `.travis.yml`.

## Deploy docs from any branch

By default doctr only deploys from `master`. To deploy to a special directory per branch, use `$TRAVIS_BRANCH`:

```yaml
- if [[ "${TRAVIS_BRANCH}" == "master" ]]; then
    doctr deploy docs;
  else
    doctr deploy --no-require-master "docs-$TRAVIS_BRANCH";
  fi
```

This does not remove the docs after the branch is merged — do that manually. Note: only branches on the same repo can be deployed to (Travis does not expose secure env vars to fork PRs). To deploy docs for a branch from a PR, push it up to the main repository first.

## Deploy docs from a non-master branch

Use `--branch-whitelist` (default: `master`). It takes any number of arguments and should generally go last in the call:

```yaml
- doctr deploy --built-docs build/ . --branch-whitelist develop
```

## Deploy docs from git tags

Tag builds run separately; by default doctr does not deploy on them. Enable with `--build-tags` (the tag is in `$TRAVIS_TAG`, empty otherwise). To deploy to `dev` for normal master builds and `version-<TAG NAME>` for tags:

```yaml
- if [[ -z "$TRAVIS_TAG" ]]; then
    DEPLOY_DIR=dev;
  else
    DEPLOY_DIR="version-$TRAVIS_TAG";
  fi
- doctr deploy --build-tags --built-docs build/ $DEPLOY_DIR
```

To deploy only on a tag, use `--branch-whitelist` with no arguments (deploys from no branch):

```yaml
- doctr deploy latest --built-docs build/ --build-tags --branch-whitelist
```

## Deploy to a separate repo

By default doctr deploys to the `gh-pages` branch of the same repo. To deploy elsewhere, specify a separate deploy and build repository at `doctr configure` time (it asks for the two separately). You need admin access to the deploy repo to upload the key — if you don't have it, run `doctr configure --no-upload-key`; doctr prints the public key and the URL of the GitHub form where someone with admin access can paste it in.

In `.travis.yml`:

```yaml
- doctr deploy --deploy-repo <deploy repo> deploy_dir
```

## Setting up Doctr for a repo you don't have admin access to

Run `doctr configure --no-upload-key` — no GitHub credentials needed. Follow the on-screen instructions: create a new branch, commit the `github_deploy_key_org_repo.enc` file, edit `.travis.yml` with the encrypted env var and the deploy call. Then open a pull request; tell the repo owner to add the public key (printed by doctr) as a deploy key for the repo — doctr also prints the URL where they can add it. The public SSH key is safe to post publicly in the PR.

## Post-processing the docs on gh-pages

Run any command on the `gh-pages` branch with `doctr deploy --command`, after syncing but before committing/uploading:

```bash
doctr deploy --command 'post-process.py' deploy_dir
```

(e.g. adding links to other versions in `index.html`). The command runs on the deploy branch with `shell=True`; files it creates must be added to the index manually or they will not be committed.

## Using a separate command to deploy to gh-pages

If you already have an existing tool for deploying to `gh-pages`, still use doctr to manage the deploy key:

```bash
doctr deploy --no-sync --command 'command to deploy' deploy_dir
```

The command should add any files you want committed to the index.

## Deploying to a GitHub wiki

Use `org/repo.wiki` as the deploy repo at `doctr configure` time (the deploy key for pushing to a wiki is the same as for the repo itself — no separate key needed):

```bash
doctr deploy --deploy-repo org/repo.wiki .
```

## Using doctr with `*.github.io` pages

GitHub serves html from the `master` branch of a `coolteam/coolteam.github.io` repo at `https://coolteam.github.io`. Separate source files (input to a static site generator) from output HTML into two branches:

1. Create a new branch for the source files (e.g. `source`) and push it.
2. Set this branch as the default branch in GitHub settings for the repo.
3. Run `doctr configure` in the `source` branch; set both source and output repos to `coolteam/coolteam.github.io`.
4. Commit the generated encryption key and `.travis.yml` to the `source` branch only — do not commit a `.travis.yml` to both `master` and `source`, or you get an infinite loop of Travis builds.
5. Make sure the deploy command whitelists the `source` branch:

```bash
doctr deploy --branch-whitelist source --built-docs output-directory/ .
```

Source files are pushed only to the `source` branch; all output files go to `master` during Travis builds. doctr also refuses to commit when the last commit on the branch was made by doctr, avoiding infinite loops (see Gotchas).
