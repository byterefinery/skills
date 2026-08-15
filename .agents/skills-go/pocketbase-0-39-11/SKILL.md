---
name: pocketbase-0-39-11
description: PocketBase v0.39.11 open source all-in-one backend (single Go executable). Use when building, extending, or operating PocketBase apps; running its CLI or Web APIs; writing pb_hooks JS extensions or Go framework code; configuring collections, API rules, filters, auth, realtime, files, migrations, or deploying the app.
license: MIT
compatibility: PocketBase v0.39.11 binary or Go module github.com/pocketbase/pocketbase v0.39.11; Go 1.25+ only when building from source
metadata:
  tags:
    - go
    - backend
    - sqlite
    - api
---

# pocketbase 0.39.11

## Overview

PocketBase is an open source backend in a single Go executable (MIT license, v0.39.11, pre-v1.0 so APIs can change between releases). It bundles:

- an embedded **SQLite** database (pure-Go `modernc.org/sqlite`, no CGO) with **realtime (SSE) subscriptions**
- **collections/records** data model with field types, **API rules**, and full-text-ish filter language
- **users/auth** management (password, email OTP, OAuth2, MFA) for any number of auth collections plus the `_superusers` collection
- file upload/storage (local disk or S3), backups, cron jobs, logs, SMTP email
- an embedded **Superuser dashboard UI** served at `/_/`

Two usage modes:

1. **Standalone app** — run the prebuilt binary; extend with JavaScript in `pb_hooks/` (the goja JS VM is enabled by default).
2. **Go framework** — `import "github.com/pocketbase/pocketbase"` in your own `main.go`, add custom routes/hooks in Go, build a statically linked executable.

Key defaults: listens on `127.0.0.1:8090` (no domain args) or `0.0.0.0:80`/`443` (with domain args, auto Let's Encrypt TLS); data lives in `./pb_data/` (`data.db` + `auxiliary.db` + `settings.json`); JS hooks in `./pb_hooks/`; JS migrations in `./pb_migrations/`; static files in `./pb_public/`.

## Usage

### Quick start (standalone binary)

```bash
# first start creates pb_data/ and prints a dashboard URL with a setup link
./pocketbase serve
# or pin an address explicitly
./pocketbase serve --http=0.0.0.0:8090 --origins=http://localhost:5173
```

Create the first superuser (required to unlock the dashboard):

```bash
./pocketbase superuser upsert admin@example.com "str0ngPassw0rd"
```

Then open the printed dashboard URL (e.g. `http://127.0.0.1:8090/_/`), create collections in the UI, and call the JSON APIs (`/api/collections/{name}/records`, ...) with the official **JavaScript SDK** (`pocketbase/js-sdk`) or **Dart SDK** (`pocketbase/dart-sdk`).

### Data model

A **collection** is a SQLite table; a row is a **record**. Three collection types: `base` (default), `auth` (adds `email`, `emailVisibility`, `verified`, `password`, `tokenKey` system fields plus auth options and a `manageRule`), and `view` (read-only, backed by a raw `SELECT`). Field types: `text`, `number`, `bool`, `email`, `url`, `editor`, `date`, `autodate`, `select`, `file`, `relation`, `json`, `geoPoint`. All fields are **non-nullable with zero defaults** (empty string, 0, etc.); `json` defaults to `null`.

Every collection carries **5 API rules** (`listRule`, `viewRule`, `createRule`, `updateRule`, `deleteRule`) written in the same filter expression language as record `filter` query params. Rules are both access control **and** data filters, and they are **ignored for superusers**.

### Extending

- **JavaScript hooks** (prebuilt binary): add `*.pb.js` files to `pb_hooks/`; register hooks (`onRecordAfterUpdateSuccess(...)`), routes (`routerAdd(...)`), crons (`cronAdd(...)`). The app auto-restarts on file change on UNIX. See [06-js-hooks](references/06-js-hooks.md).
- **JS migrations**: `*.js` files in `pb_migrations/`, applied automatically on `serve`. See [07-js-migrations](references/07-js-migrations.md).
- **Go**: bind `app.On*()` hooks and `app.OnServe()` routes in `main.go`; see [08-go-extensions](references/08-go-extensions.md).

Full Web API endpoints and query params are in the references below; the dashboard also generates per-collection API docs (Collections > API Preview).

## Gotchas

- **API rule values have three distinct meanings** — `null` ("locked", superuser-only, the default), `""` (public, anyone), non-empty string (filter that must pass). Rules double as filters: unsatisfied `listRule` returns 200 with empty items, unsatisfied `createRule` returns 400, unsatisfied `viewRule`/`updateRule`/`deleteRule` return 404, and locked rules return 403 for non-superusers.
- **Auth is fully stateless** — JWT (HS256) tokens are not stored server-side; there is no logout endpoint or token revocation. To invalidate issued tokens, change the superuser password (or the shared auth token secret in `_superusers` collection options). "Logout" = discard the token client-side. No OAuth2 for `_superusers`.
- **Superusers bypass everything** — all collection rules are skipped for superuser-authenticated requests; never expose a superuser token to clients. For server-to-server "API keys", use a non-renewable impersonate token from the Dashboard or `/api/collections/_superusers/records/{id}/impersonate`.
- **`--automigrate` is ON by default** in the prebuilt binary — every Dashboard collection change writes a migration file into `pb_migrations/`. Disable with `--automigrate=false` for clean migration control.
- **JS hook handlers run in isolated, serialized contexts** — each handler is executed as a separate "program": variables/functions declared outside the handler body are invisible inside it. Share code via `require()` of a local module (CommonJS only; the shared module registry makes mutation unsafe).
- **JS is not Node.js** — the goja engine (ES5+most of ES6) has no `setTimeout`/`setInterval`, no `fetch`, no `fs`, no ESM `import` (bundle with rollup/webpack if needed). Relative paths resolve against the CWD, not `pb_hooks` — use the `__hooks` global for absolute paths.
- **Only `*.pb.js` (and `*.pb.ts`) files load** from `pb_hooks/`; plain `*.js` there is ignored. For IDE autocomplete, reference `pb_data/types.d.ts` (ambient TypeScript declarations) or rename files to `.pb.ts`.
- **Dates are RFC3339 strings compared lexicographically** — filters need full datetime strings (e.g. `created >= '2024-11-19 00:00:00.000Z' && created < '2024-11-20 00:00:00.000Z'`); there is no date arithmetic.
- **Client-side `filter`/`sort` params cannot use `@request.*` or `@collection.`** — those rule fields are superuser-only in request query params (error for others).
- **`perPage` caps at 1000** (default 30); for "all records" use the SDK `getFullList()` (paginates internally) or keep filters tight.
- **File uploads require `multipart/form-data`** on the record create/update endpoints; the DB stores only the file name. Default max file size is ~5MB per field. Use `fieldName+` / `fieldName-` / `+fieldName` keys to append/prepend/remove files without touching the rest.
- **View collections emit no realtime events** (read-only, no CRUD) and cannot be written via the records API.
- **Realtime auth happens on the first subscription call**, not on the SSE connect; idle SSE clients are disconnected after 5 minutes (auto-reconnect in SDKs).
- **The batch API (`POST /api/batch`) is disabled by default** — enable and tune limits in Dashboard > Settings > Application.
- **`POST /api/sql` is superuser-only and dangerous** — one-off analytics/debugging, not a data-access interface.
- **Migrations apply automatically on `serve`** — after `migrate down`, restart the server so cached collections refresh. Applied filenames are tracked in the `_migrations` table; `migrate history-sync` removes rows for deleted files.
- **Go build targets** — the pure-Go driver supports linux/darwin/freebsd (amd64, arm64, arm, 386, loong64, ppc64le, riscv64, s390x) and windows (386, amd64, arm64); build with `CGO_ENABLED=0` for static binaries.
- **Restore/`app.Restart()` is UNIX-only** (relies on `execve`); backup ZIP generation puts the app in read-only mode and is slow for large `pb_data` — for 2GB+ prefer `sqlite3 .backup` + `rsync` scripts.
- **Behind a reverse proxy**, set "Trusted proxy" headers (e.g. `X-Forwarded-For`, `X-Real-IP`) in Settings, or real client IPs (and IP-based rate limits / superuser IP whitelist) won't work.
- **In Go hooks, use `e.App`** (the event-scoped instance) rather than a captured outer `app` variable — the handler may run inside a DB transaction, and reusing the outer instance can deadlock.

## References

- [01-install-cli](references/01-install-cli.md) — installation, directory layout, CLI commands and flags, settings
- [02-records-api](references/02-records-api.md) — record CRUD endpoints, query params, set modifiers, batch API
- [03-rules-and-filters](references/03-rules-and-filters.md) — API rule semantics and the filter expression language
- [04-authentication](references/04-authentication.md) — auth endpoints, token model, MFA, impersonation, API-key patterns
- [05-realtime-files](references/05-realtime-files.md) — realtime SSE protocol and file download/token endpoints
- [06-js-hooks](references/06-js-hooks.md) — pb_hooks JavaScript extensions, globals, routing, crons
- [07-js-migrations](references/07-js-migrations.md) — pb_migrations, migrate commands, automigrate
- [08-go-extensions](references/08-go-extensions.md) — PocketBase as a Go framework, event hooks, DB access, testing
- [09-production](references/09-production.md) — deployment, backups, email, static files, upgrades
