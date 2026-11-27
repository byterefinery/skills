# Security and authentication

## The encryption pipeline

Doctr keeps secrets out of the build logs by encrypting everything before it touches Travis:

1. **Deploy key (default)** — `generate_ssh_key()` creates an RSA 4096-bit SSH keypair (PKCS8 PEM private, OpenSSH public). The private key is Fernet-encrypted to `<keypath>.enc` (`encrypt_to_file()`). The Fernet key is then encrypted to the Travis public key with RSA PKCS1v15 and base64-encoded (`encrypt_variable()`) — this is the `secure:` env var value added to `.travis.yml`.
2. **Personal access token (`--token`)** — a GitHub PAT is generated, and `GH_TOKEN=<token>` is encrypted the same way into the secure env var. The deploy key is never created in this mode.
3. On Travis, `setup_deploy_key()` reads the Fernet key from the env var (`DOCTR_DEPLOY_ENCRYPTION_KEY_<ORG>_<REPO>`, or legacy `DOCTR_DEPLOY_ENCRYPTION_KEY`), decrypts the private key (permissions 0o600), installs it in `~/.ssh/`, and adds an SSH config block + ssh-agent entry.
4. The token path: `run()` hides the `GH_TOKEN` value from command output by replacing it with `~`*len(token)` — always use `run()` rather than raw subprocess calls when a token is present.

The Fernet key never appears in the build logs; Travis does not make secure environment variables available to pull request builds (and forks).

## Auth types

| | Deploy key (default, recommended) | Personal access token (`--token`) |
|---|---|---|
| Scope | Push access to a single repository | Read/write access to all public repos of the user |
| Setup | `doctr configure` uploads the public key to the repo (or prints it for manual pasting with `--no-upload-key`) | `doctr configure --token` generates the token |
| Revocation | Repo settings → keys: `https://github.com/<org>/<repo>/settings/keys` | `https://github.com/settings/tokens` |
| Private repos | Supported (key works for private repos) | Supported; configure generates a temporary PAT for Travis auth and deletes it immediately (email warning from GitHub) |

Deploy keys are the recommended option. A deploy key only grants push access to one repository; a personal access token grants access to your entire account. If you revoke a key, re-run `doctr configure` to generate a new one.

## Environment variables and file naming

- Env var: `DOCTR_DEPLOY_ENCRYPTION_KEY_<ORG>_<REPO>` — deploy repo lowercased, with `-`/`.`/`/` replaced by `_`, uppercased (e.g. `myorg/myrepo` → `DOCTR_DEPLOY_ENCRYPTION_KEY_MYORG_MYREPO`). Legacy fallback: `DOCTR_DEPLOY_ENCRYPTION_KEY`.
- Key file: `github_deploy_key_<org>_<repo>.enc` (default), or a custom path via `--key-path`. Legacy fallback: `github_deploy_key.enc`.
- The env var is added to `.travis.yml` as a `secure:` entry under `env.global`; the key file is committed alongside it.

## Push restrictions

Doctr refuses to push when:

- On a tag build without `--build-tags`
- The branch doesn't match any whitelist regex (default: `master`)
- It's a PR build — secure env vars are not available to PR builds from forks, and doctr also checks the repo is not a fork via the GitHub API
- The last commit on the branch was made by doctr itself (author email `drdoctr@users.noreply.github.com`) — avoids infinite build loops

## Travis .org vs .com

travis-ci.org and travis-ci.com have different public keys for the same repo, so `doctr configure` must know which is enabled (auto-detected; asks if both are enabled; override with `--travis-tld`). Once configured, there is no difference in the `.travis.yml` file. To run doctr on both, configure each separately, renaming the generated encrypted files, add both secure env vars to `.travis.yml`, and branch on `$TRAVIS_BUILD_WEB_URL`:

```bash
if [[ $TRAVIS_BUILD_WEB_URL == *"travis-ci.com"* ]]; then
    doctr deploy --built-docs <built-docs> . --key-path github_deploy_key-com.enc;
else
    doctr deploy --built-docs <built-docs> . --key-path github_deploy_key-org.enc;
fi
```

## 1.9.0 authentication changes

GitHub authentication now uses the **device authorization flow** — the username/password flow is no longer supported (issue #373). If a session expires mid-configure, doctr prints "The two-factor authentication code has expired. Please run doctr configure again." and you re-run it. GitHub API rate limits are shared across all OAuth applications; if hit, wait an hour and re-run (common cause: the Travis "sync account" button).
