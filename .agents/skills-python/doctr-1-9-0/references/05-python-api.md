# Python API

The docs recommend most users use doctr from the command line; this is for programmatic use. The public surface is re-exported from `doctr/__init__.py` (all functions listed in `__all__`).

## Local side — `doctr.local`

| Function | Signature / behavior |
|---|---|
| `encrypt_variable(variable, build_repo, *, tld='.org', public_key=None, travis_token=None, **login_kwargs)` | RSA PKCS1v15-encrypts a bytes `b'ENV=value'` variable to the Travis public key; returns base64 bytes. For private repos pass `travis_token` (implies travis-ci.com API v3); otherwise fetches from `https://api.travis-ci{tld}/repos/<repo>/key` |
| `encrypt_to_file(contents, filename)` | Fernet-encrypts bytes to `filename` (must end `.enc`); returns the Fernet key |
| `GitHub_login(client_id, *, headers=None, scope='repo')` | GitHub device authorization flow; prints user code, opens browser, polls until authorized; returns an access token. Handles `authorization_pending`, `slow_down` (adds 5 s to interval), `expired_token`/`expires_in` expiry (re-runs the flow), `access_denied` (raises `AuthenticationFailed`) |
| `GitHub_post(data, url, *, headers)` | POST JSON data to GitHub; returns parsed JSON response or raises on error status |
| `generate_GitHub_token(*, note=..., scopes=None, **login_kwargs)` | Creates a GitHub personal access token (default scope `public_repo`); returns the API response dict (contains `token` and `id`) |
| `delete_GitHub_token(token_id, *, headers)` | Deletes a temporary token by id |
| `get_travis_token(*, GitHub_token=None, **login_kwargs)` | Generates a temporary GitHub token (scopes `read:org`, `user:email`, `repo`; note "temporary token for doctr to auth against travis (delete me)") if none is passed in, exchanges it at `https://api.travis-ci.com/auth/github`, returns the Travis access token, and deletes the temp token in a finally block |
| `upload_GitHub_deploy_key(deploy_repo, ssh_key, *, read_only=False, title=..., **login_kwargs)` | POSTs a public SSH key to `/repos/<deploy_repo>/keys`; returns the API response |
| `generate_ssh_key()` | RSA 4096-bit keypair; returns `(private_key, public_key)` bytes (PKCS8 PEM private, OpenSSH public) |
| `check_repo_exists(deploy_repo, service='github', *, headers=None, ask=False)` | Validates `org/repo` exists; raises `RuntimeError` if not. Returns `{'private': bool, 'service': str}`. For `service='travis'` checks both travis-ci.com and .org (asks which to use if both when `ask=True`); for `.wiki` repos strips the suffix and verifies via `git ls-remote` |
| `guess_github_repo()` | Returns `org/repo` from `git ls-remote --get-url origin` (regex matches https/git/ssh github URLs), or `False` if no guess can be made |

Also exported: `AuthenticationFailed`, `GitHubError`, `GIT_URL` (the repo URL regex).

## Travis side — `doctr.travis`

| Function | Signature / behavior |
|---|---|
| `decrypt_file(file, key)` | Fernet-decrypts `<file>.enc`; writes the plaintext to `<file>` (without `.enc`) with permissions 0o600 |
| `setup_deploy_key(keypath='github_deploy_key', key_ext='.enc', env_name='DOCTR_DEPLOY_ENCRYPTION_KEY')` | Decrypts the key (env var `env_name`, falling back to legacy `DOCTR_DEPLOY_ENCRYPTION_KEY`; falls back to legacy `github_deploy_key.enc` file), moves it to `~/.ssh/`, appends a `Host github.com` block to `~/.ssh/config`, starts `ssh-agent` and adds the key |
| `get_token()` | Reads `GH_TOKEN` from the environment (masked as `~`*len in output); returns bytes |
| `run(args, shell=False, exit=True)` | Runs a command (list of strings for non-shell, string for shell), hides the token from output, prints the command in blue, exits on nonzero return code unless `exit=False` |
| `get_current_repo()` | Returns `org/repo` from `git config --get remote.origin.url` (splits on `.git` and `/`) |
| `get_travis_branch()` | Returns `$TRAVIS_PULL_REQUEST_BRANCH` for PR builds, else `$TRAVIS_BRANCH` |
| `setup_GitHub_push(deploy_repo, *, auth_type='deploy_key', full_key_path='github_deploy_key.enc', require_master=None, branch_whitelist=None, deploy_branch='gh-pages', env_name='DOCTR_DEPLOY_ENCRYPTION_KEY', build_tags=False)` | Sets git user name/email if unset; adds `doctr_remote` (SSH for deploy key, HTTPS+token for token auth, read-only HTTPS when push not allowed); fetches it; returns `canpush`. Note: `require_master` is deprecated in favor of `branch_whitelist=['master']` |
| `checkout_deploy_branch(deploy_branch, canpush=True)` | Creates the deploy branch if missing (orphan + `.nojekyll`, pushed when possible); checks out a local `__doctr_working_branch` tracking the remote branch |
| `deploy_branch_exists(deploy_branch)` | Checks whether `doctr_remote/<deploy_branch>` exists locally |
| `create_deploy_branch(deploy_branch, push=True)` | Creates the deploy branch (orphan, `.nojekyll`, commit, optional push); returns True if created |
| `set_git_user_email()` | Sets `user.name` to "Doctr (Travis CI)" and `user.email` to `drdoctr@users.noreply.github.com` only if unset or already the Travis defaults |
| `copy_to_tmp(source)` | Copies a file or directory to a fresh temp dir; returns the copied location |
| `sync_from_log(src, dst, log_file, exclude=())` | Syncs files from `src` into `dst`; removes stale files recorded in `log_file` that are no longer in `src`; excluded paths are neither added nor removed. Returns `(added, removed)` — `added` includes the log file itself |
| `commit_docs(*, added, removed)` | Stages and commits changes with a detailed message (build number, repo slug, branch/tag, commit SHA, job URL, doctr command); returns True if committed, False otherwise |
| `push_docs(deploy_branch='gh-pages', retries=5)` | Pulls with `-s recursive -X ours` and pushes to the deploy branch, retrying up to `retries` times on failure; exits with "Giving up..." if all fail |
| `find_sphinx_build_dir()` | Globs `**/*build/html` (recursive); returns the first match; raises `RuntimeError` if none found |
| `determine_push_rights(*, branch_whitelist, TRAVIS_BRANCH, TRAVIS_PULL_REQUEST, TRAVIS_TAG, build_tags, fork)` | Returns True/False — see [02-deploy-command](02-deploy-command.md) for the refusal conditions |
| `last_commit_by_doctr()` | True if HEAD's author email is `drdoctr@users.noreply.github.com` |
| `is_subdir(a, b)` | True if `a` is a subdirectory of `b` (absolute paths) |
