# 07 — Auth and CLI

## Python authentication

Verified from `_login.py`:

```python
login(
    token: str | None = None,
    *,
    add_to_git_credential: bool = False,   # register token with git credential helper
    skip_if_logged_in: bool = True,
) -> None
```

- **No token → browser-based OAuth flow** (2.x behavior): `login()` opens a URL, you enter a short code, and the token is retrieved and saved. In a terminal you may also choose to paste an existing token.
- Token persistence order: the `HF_TOKEN` env var **always overrides** the stored token (the CLI prints a note when this happens).
- Stored tokens live at `constants.HF_TOKEN_PATH` (plus `HF_STORED_TOKENS_PATH` for multiple tokens).
- `logout()` removes the stored token.
- `notebook_login()` — force the notebook UI (token entry widget); `interpreter_login()` — force the terminal prompt. Use these when environment detection is wrong.
- `whoami()` — current user info; `get_token()` — resolve the active token.
- Multiple tokens: `auth_check`, `auth_list`, `auth_switch` (CLI: `hf auth ...`).
- OAuth/OIDC: `attach_huggingface_oauth(...)`, `OAuthInfo`/`OAuthOrgInfo`/`OAuthUserInfo`, device-code OAuth (`HF_DEVICE_CODE_OAUTH_CLIENT_ID`), `OIDCError`, `DeviceCodeError`.
- `HF_HUB_DISABLE_IMPLICIT_TOKEN=1` prevents the client from silently using the stored token.

## The `hf` CLI

The 2.x package installs only the `hf` console script (and `tiny-agents`); there is **no** `huggingface-cli` entry point. The CLI is agent-aware — output adapts when run by a coding agent.

### Top-level commands (verified from `cli/hf.py`)

`hf sync` (bucket sync), `hf cp`, `hf download`, `hf upload`, `hf env`, `hf update`, `hf version` (hidden: `hf lfs-enable-largefiles`, `hf lfs-multipart-upload`)

### Command groups

`hf auth`, `hf buckets`, `hf cache`, `hf collections`, `hf datasets`, `hf discussions`, `hf endpoints` (inference endpoints), `hf extensions` (alias `hf ext`), `hf jobs`, `hf models`, `hf papers`, `hf repos`, `hf sandbox`, `hf skills`, `hf spaces`, `hf webhooks`

Useful examples (from the README quick start):

```bash
hf auth login                       # --token $HF_TOKEN non-interactively
hf models ls --warm                 # models served by Inference Providers
hf download Qwen/Qwen3-0.6B
hf upload username/my-cool-model ./model.safetensors
hf buckets sync ./checkpoints hf://buckets/username/my-bucket
hf jobs run python:3.12 python -c "print('Hello from the cloud!')"
```

### Agent skills

- `hf --skills` — print the generated `hf` CLI SKILL.md to stdout (alias `hf skills preview`).
- `hf skills add` — install the CLI skill for coding agents (Claude Code, Codex, Cursor, …).
- The CLI auto-checks for its own updates (`hf update` handles the skill too); disable with `HF_HUB_DISABLE_UPDATE_CHECK=1`.

### Debugging

Set `HF_DEBUG=1` for full tracebacks; the CLI otherwise formats known exceptions with a hint. Telemetry can be disabled with `HF_HUB_DISABLE_TELEMETRY` / `DO_NOT_TRACK` / `DISABLE_TELEMETRY`.
