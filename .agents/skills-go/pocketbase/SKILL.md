---
name: pocketbase
description: PocketBase backend (server v0.40.1) and official JavaScript SDK (v0.28.0). Use when building, configuring, or debugging PocketBase applications - collections, API rules and filters, the REST-ish Web API, authentication (password, OTP, OAuth2, MFA), files, Go framework extension, JS VM hooks, CLI, deployment - and when using the js-sdk client from browsers, Node.js, or React Native.
metadata:
  tags: ["go", "backend", "api", "sdk", "database"]
---

# pocketbase

## Overview

PocketBase is an open source Go backend in a single portable binary - an embedded SQLite database with realtime subscriptions, built-in auth and file management, an admin dashboard, and a stateless REST-ish JSON API under `/api/`. It runs either as a standalone app or as a Go framework (`pocketbase.New()`), and can be extended with JavaScript via the built-in JS VM (`pb_hooks/`).

This skill covers **v0.40.1** of the server and **v0.28.0** of the official JavaScript SDK (browser, Node.js, React Native). The two parts are kept in separate reference files:

- **PocketBase server** — references `01-` … `10-`: overview, collections, API rules/filters, Web API, files, authentication, Go framework, JS VM, console commands, production deployment
- **PocketBase JavaScript SDK** — references `11-` … `13-`: client/authStore/options, record service (CRUD + auth), other services (collections, files, logs, settings, backups, crons, sql, health, batch, realtime)

PocketBase is pre-1.0 — backward compatibility is not guaranteed; check the changelog before upgrading (the v0.40.0 bump to Go 1.27 / `encoding/json/v2` is a notable one).

## Usage

Quick start (standalone binary):

```bash
./pocketbase serve                     # starts on 127.0.0.1:8090
./pocketbase superuser create EMAIL PASS
# dashboard on /_/, API on /api/, static from pb_public/
```

Quick start (js-sdk client):

```js
import PocketBase from 'pocketbase';
const pb = new PocketBase('http://127.0.0.1:8090');

await pb.collection('users').authWithPassword('test@example.com', '1234567890');
const posts = await pb.collection('posts').getFullList({ filter: 'status = "published"' });
pb.collection('posts').subscribe('*', (e) => { /* { action, record } */ });
pb.authStore.clear(); // "logout"
```

Load the reference matching the task:

- Data model, fields, relations → `02-collections`
- Access control, rules, filter expressions → `03-api-rules-and-filters`
- Any endpoint under `/api/` (records, collections, files, settings, logs, backups, crons, sql, health, realtime) → `04-web-api`
- File upload/URL/thumbnails → `05-files-handling`
- Login flows, tokens, OAuth2, MFA, impersonation → `06-authentication`
- Extending with Go (hooks, records, collections, DB, jobs, mails) → `07-go-framework`
- Server-side JavaScript (`pb_hooks`) → `08-jsvm`
- CLI (`serve`, `superuser`, `migrate`, …) → `09-console-commands`
- Deployment (systemd, reverse proxy, Docker) → `10-production`
- Instantiating/configuring the SDK client → `11-js-sdk-overview`
- SDK record CRUD and auth methods → `12-js-sdk-records`
- SDK collections/files/logs/settings/backups/crons/sql/health/batch → `13-js-sdk-services`

## Gotchas

- **Auth is fully stateless** — no sessions, no logout endpoint; a client is authenticated by sending a valid `Authorization: <token>` header (no `Bearer` prefix). "Logout" = discarding the token locally (`pb.authStore.clear()`).
- **API rules double as data filters** — an unsatisfied `listRule` returns 200 with empty items, unsatisfied `createRule` returns 400, unsatisfied `view/update/deleteRule` returns 404, and a locked rule (`null`) returns 403 for non-superusers. Rules are ignored entirely for superusers.
- **Superusers are a regular auth collection** (`_superusers`) — use `pb.collection('_superusers')`, not the removed `pb.admins`. OAuth2 does not work for superusers.
- **Dates are RFC3399 strings** (`2024-11-10 18:45:27.123Z`) and are compared as strings — filters need full datetime format, not partial dates.
- **View collections are read-only** SQL projections with no realtime events; base/auth collections are the writable kinds.
- **js-sdk auto-cancellation** — duplicate pending requests (same method+path) abort the previous one; disable with `pb.autoCancellation(false)` for shared/superuser server-side clients.
- **`localhost` vs `127.0.0.1`** — some Node environments fail on `localhost` (`ECONNREFUSED ::1`); use `127.0.0.1` in the SDK URL.
- **OAuth2 redirect URL** — register exactly `https://yourdomain.com/api/oauth2-redirect` in the provider; the modern js-sdk `authWithOAuth2({ provider })` form opens a popup and round-trips the code over a one-off realtime subscription (no page reload).
- **File fields store only names** — upload via multipart `FormData`; use `field+`/`+field`/`field-` modifiers to append/prepend/remove individual files on multi-file fields.
- **Prebuilt binary vs Go build differ** — the release binary ships JS VM + `migrate`/`update` commands; a bare `pocketbase.New()` Go app has only `serve`/`superuser` unless you register `jsvm.MustRegister` and `migratecmd.MustRegister`.
- **JS VM handlers have no outer scope** — closures don't capture top-level variables in `pb_hooks` files; use `require(`${__hooks}/...`)` for shared data.

## References

**PocketBase server (v0.40.1)** — references `01-` through `10-`

- [01-overview](references/01-overview.md) — what PocketBase is, standalone vs Go framework, quick start, data dirs, dashboard, integration guidance
- [02-collections](references/02-collections.md) — collection types (base/view/auth), all field types, set modifiers, indexes, relations
- [03-api-rules-and-filters](references/03-api-rules-and-filters.md) — API rules semantics and status codes, filter expression syntax, `@request`/`@collection`, modifiers, macros, functions
- [04-web-api](references/04-web-api.md) — REST API reference for records, auth endpoints, collections, files, settings, logs, backups, crons, sql, health, realtime, batch
- [05-files-handling](references/05-files-handling.md) — file upload, deletion, file URLs, thumbnail formats, protected files, S3
- [06-authentication](references/06-authentication.md) — token model, password/OTP/OAuth2 (PKCE + popup flow + HTML templates)/MFA, impersonation, API keys, token refresh
- [07-go-framework](references/07-go-framework.md) — Go app setup and config, event hooks, record/collection operations, DB, filesystem, jobs, mails, logging, routing, realtime, migrations, testing
- [08-jsvm](references/08-jsvm.md) — server-side JavaScript in `pb_hooks`, global objects, handler scope, modules, JS migrations
- [09-console-commands](references/09-console-commands.md) — CLI commands and flags (serve, superuser, migrate, update, custom commands)
- [10-production](references/10-production.md) — deployment strategies: bare metal, systemd, reverse proxy, Docker, monitoring

**PocketBase JavaScript SDK (v0.28.0)** — references `11-` through `13-`

- [11-js-sdk-overview](references/11-js-sdk-overview.md) — installation, Client instance, authStore types, send options, beforeSend/afterSend, filter()/buildURL(), errors, auto-cancellation
- [12-js-sdk-records](references/12-js-sdk-records.md) — RecordService CRUD, list/query options, all auth methods (password, OTP, OAuth2, MFA, reset, verification, email change), impersonation, record subscriptions
- [13-js-sdk-services](references/13-js-sdk-services.md) — collections, files, logs, settings, backups, crons, sql, health services and batch transactions
