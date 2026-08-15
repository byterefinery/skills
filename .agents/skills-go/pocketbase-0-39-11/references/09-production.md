# pocketbase 0.39.11 — Production

## Deploying the standalone binary

PocketBase is fully portable: upload the executable (+ `pb_hooks/`, `pb_migrations/`, `pb_public/`) and run it.

```bash
# auto TLS via Let's Encrypt (needs root or cap_net_bind_service for :80/:443)
./pocketbase serve my.example.com
# non-root: setcap 'cap_net_bind_service=+ep' pocketbase (or iptables/authbind)
```

Systemd unit (`/lib/systemd/system/pocketbase.service`):

```ini
[Unit]
Description=PocketBase
After=network.target

[Service]
User=pb
ExecStart=/path/to/pocketbase serve --http=0.0.0.0:8090
Restart=on-failure
WorkingDirectory=/path/to/app
StandardOutput=append:/path/to/std.log
StandardError=append:/path/to/std.log

[Install]
WantedBy=multi-user.target
```

Docker (no official image; minimal example):

```dockerfile
FROM alpine:latest
RUN apk add --no-cache unzip ca-certificates
ADD https://github.com/pocketbase/pocketbase/releases/download/v0.39.11/pocketbase_0.39.11_linux_amd64.zip /tmp/pb.zip
RUN unzip /tmp/pb.zip -d /pb/
# COPY ./pb_migrations /pb/pb_migrations
# COPY ./pb_hooks /pb/pb_hooks
EXPOSE 8080
CMD ["/pb/pocketbase", "serve", "--http=0.0.0.0:8080"]
```

Mount a volume at `/pb/pb_data` to persist data.

## Behind a reverse proxy

Proxy to `127.0.0.1:8090`; pass `X-Forwarded-For` / `X-Real-IP` and set the matching headers in **Settings > Trusted proxy**, otherwise real client IPs (activity logs, rate limits, superuser IP whitelist) are wrong. NGINX must disable response buffering for realtime SSE (`proxy_buffering off`; PocketBase already sends `X-Accel-Buffering: no` on the SSE route). `client_max_body_size` should cover the largest upload (default body limit is configurable; see Settings).

## Backups

- Builtin: `POST /api/backups` / Dashboard > Settings > Backups. A ZIP snapshot of `pb_data/` (local disk or S3, separate bucket recommended). During ZIP generation the app is read-only — slow for large data (2GB+ → prefer `sqlite3 data.db .backup` while running + `rsync` the files dir). Restore is UNIX-only and restarts the process.
- Manual: stop the app, copy/replace `pb_data/`, start. This is a complete backup (DB + settings + local uploads + `pb_data` state).
- `migrate down` is the tool for *schema* rollback, not data recovery — keep DB backups before risky migrations.

## Email

Default mailer is the local `sendmail` command — fine for dev, unreliable in production (spam/delivery). Configure **Settings > Mail settings** (SMTP or sendmail) with a real provider (SES, Mailgun, Brevo, SendGrid, ...). Test with `POST /api/settings/test/email`.

## Misc hardening

- Set `--encryptionEnv=PB_SECRET` (32-char value) to encrypt sensitive settings at rest.
- `--origins` to tighten CORS (default `*`).
- Superuser IP whitelist (`pocketbase superuser ips ...` or Settings) if the dashboard must be reachable only from your IPs.
- Rate limits are per-route/per-collection configurable in Settings > Application (and inline for record actions).
- Batch API stays disabled unless explicitly enabled (Settings > Application) with conservative body/time limits.

## Upgrades

Pre-v1.0: **no backward compatibility guarantees between releases** — read the CHANGELOG (repo root `CHANGELOG.md`) before upgrading and back up `pb_data/` first. Typical upgrade: stop the app, replace the executable (or `./pocketbase update`), start — system migrations run automatically on bootstrap; automigrate keeps your `pb_migrations/` current for schema changes.
