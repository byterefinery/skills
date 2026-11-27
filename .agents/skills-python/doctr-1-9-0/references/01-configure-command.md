# doctr configure

`doctr configure` is run **locally** (not on Travis) and is interactive. It generates the key material needed for deploys and prints the exact `.travis.yml` lines to add. It never pushes anything itself — you commit the key file and edit `.travis.yml`, then push to GitHub; Travis builds do the rest.

## Flow

1. Refuses to run on Travis unless `--force` is passed (checks `TRAVIS_JOB_NUMBER`).
2. Prints a welcome message and asks whether to authenticate with GitHub. With authentication, it uses the **GitHub device authorization flow** (1.9.0; username/password login is no longer supported) — prints a user code, opens the browser, polls until authorized. The `repo` scope is used so the deploy key can be uploaded to the repo.
3. Guesses the build repo from `git ls-remote --get-url origin` (via `guess_github_repo()`); prompts for the build repo if not guessed or if you want to override (default shown in blue).
4. Checks the build repo exists on GitHub (`check_repo_exists(..., service='github')`) and whether it is private. If private, a temporary personal access token may be generated for Travis authentication (see Private repos below).
5. Checks which Travis instance the repo is enabled on — `travis-ci.com` vs `travis-ci.org` — via `check_repo_exists(..., service='travis', ask=True)`. If both are enabled it asks which to use (unless `--travis-tld` is given). The tld determines the public key used for encryption.
6. Prompts for the deploy repo (default: the build repo). If different, checks it exists on GitHub too.
7. Generates either a **deploy key** (default) or a **personal access token** (`--token`):
   - Deploy key: RSA 4096-bit SSH keypair (via `generate_ssh_key()`), private key Fernet-encrypted to `<keypath>.enc`, Fernet key encrypted to the Travis public key (RSA PKCS1v15) as a secure env var. If `--upload-key` (default), uploads the public key to GitHub via the API; otherwise prints it for manual pasting.
   - Token: generates a GitHub personal access token (`generate_GitHub_token()`, default scope `public_repo`) and encrypts `GH_TOKEN=<token>` as the secure env var.
8. Prints numbered instructions: add the key file to git, add the `secure:` env var + `script:` block to `.travis.yml`, commit and push, optionally revoke the doctr app at `https://github.com/settings/connections/applications/<client-id>`.

## Flags

| Flag | Default | Behavior |
|---|---|---|
| `--force` | off | Run even if on Travis (normally errors) |
| `--token` | off | Generate a personal access token instead of a deploy key. Not recommended — grants read/write to all public repos of the user. Private repos use scopes `read:org`, `user:email`, `repo` for the Travis-auth token |
| `--no-upload-key` | upload on | Don't automatically upload the deploy key to GitHub; prints the public key + URL instead. To prevent doctr from requiring GitHub login entirely, use `--no-authenticate` |
| `--no-authenticate` | auth on | Skip GitHub authentication entirely (implies `--no-upload-key`). Not compatible with private repos — it errors out if the repo is private |
| `--key-path` | auto | Path to save the encrypted key file. Default: `github_deploy_key_<org>_<repo>` (special chars → underscores, lowercased); `.enc` is appended automatically |
| `--travis-tld` | auto | Force `travis-ci.com` or `travis-ci.org` (accepts `c`/`com`/`.com`/`travis-ci.com` and `o`/`org`/`.org`/`travis-ci.org`). Default: detect which the repo is enabled on; ask if both |

## Private repos

Private repositories require authentication (`--no-authenticate` errors out). During configure, doctr generates a **temporary** personal access token with scopes `read:org`, `user:email`, `repo` to authenticate with Travis, and deletes it immediately after use. You will receive an email from GitHub about this. If the temporary token is still visible at `https://github.com/settings/tokens` after configure exits, delete it manually.

## Output color guide

- red — warnings and errors
- green — welcome messages (sparingly)
- blue — default values
- bold magenta — action items
- bold black — parts of code to be run or copied that should be modified

## Key generation details

- `generate_ssh_key()`: RSA, 4096-bit, public exponent 65537. Private key is PKCS8 PEM (no encryption); public key is OpenSSH format. Returns `(private_key, public_key)` as bytes.
- `encrypt_to_file(contents, filename)`: Fernet-encrypts contents to `filename` (must end with `.enc`); returns the Fernet key. Decrypt with `doctr.travis.decrypt_file()`.
- `encrypt_variable(variable, build_repo, *, tld='.org', public_key=None, travis_token=None, **login_kwargs)`: RSA PKCS1v15-encrypts a bytes `b'ENV=value'` variable to the Travis public key and base64-encodes it. For private repos (via Travis API v3 with `travis_token`) it fetches the public key from `https://api.travis-ci.com/repo/<repo>/key_pair/generated`; otherwise from `https://api.travis-ci{tld}/repos/<repo>/key` (API v2).

## Env var naming

The secure env var is named `DOCTR_DEPLOY_ENCRYPTION_KEY_<ORG>_<REPO>` — the deploy repo name lowercased with `-`, `.`, `/` replaced by `_`, then uppercased (e.g. `drdoctr/doctr` → `DOCTR_DEPLOY_ENCRYPTION_KEY_DRDOCTR_DOCTR`). The key file is `github_deploy_key_<org>_<repo>.enc` by default.
