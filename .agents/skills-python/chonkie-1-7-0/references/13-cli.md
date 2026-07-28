# CLI

Chonkie provides a command-line interface via the `chonkie` command. Requires `chonkie[cli]`.

---

## Serve

Start the REST API server:

```bash
chonkie serve                              # default: port 8000
chonkie serve --port 3000                  # custom port
chonkie serve --reload                     # auto-reload on code changes
chonkie serve --log-level debug            # debug logging
chonkie serve --host 0.0.0.0               # bind to all interfaces
```

Equivalent to `uvicorn chonkie.api.main:app --host 0.0.0.0 --port 8000`.

---

## Help

```bash
chonkie --help
chonkie serve --help
```

---

## Notes

- The CLI is built on `typer`
- `chonkie serve` requires `chonkie[api]` (FastAPI, uvicorn, SQLAlchemy, alembic, aiosqlite)
- Other subcommands may be added in future releases
