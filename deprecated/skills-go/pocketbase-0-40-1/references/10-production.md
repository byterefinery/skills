# Production deployment

PocketBase is completely portable — no external dependencies; deploying means uploading the executable (plus `pb_migrations/`, `pb_hooks/`, `pb_public/` if used) and running `serve`.

## Minimal setup (bare metal)

1. Layout on the server:

```
myapp/
  pb_migrations/
  pb_hooks/
  pocketbase
```

2. Upload (e.g. `rsync -avz -e ssh /local/path/to/myapp root@YOUR_SERVER_IP:/root/pb`)
3. Start with a domain (auto Let's Encrypt TLS): `serve yourdomain.com` — needs root for the privileged 80/443 ports, or grant the binary the capability: `sudo setcap 'cap_net_bind_service=+ep' /root/pb/pocketbase`

First-run superuser: the installer link is printed to the service log, or create it explicitly with `./pocketbase superuser create EMAIL PASS`.

## Systemd service

`/lib/systemd/system/pocketbase.service`:

```ini
[Unit]
Description = pocketbase

[Service]
Type = simple
User = root
Group = root
LimitNOFILE = 4096
Restart = always
RestartSec = 5s
StandardOutput = append:/root/pb/std.log
StandardError = append:/root/pb/std.log
WorkingDirectory = /root/pb
ExecStart = /root/pb/pocketbase serve yourdomain.com

[Install]
WantedBy = multi-user.target
```

Then `systemctl enable pocketbase.service && systemctl start pocketbase`.

## Reverse proxy

For multi-app servers or finer network control, put PocketBase behind NGINX/Apache/Caddy and point it at `127.0.0.1:8090` (start with `./pocketbase serve` without a domain). Minimal Caddy:

```
example.com {
    reverse_proxy 127.0.0.1:8090
}
```

After this, set the **"User IP proxy headers"** in PocketBase Settings (usually `X-Real-IP`, `X-Forwarded-For`) so the real client IP is extracted for logs/rate limiting.

## Docker

No official image; minimal Dockerfile:

```dockerfile
FROM alpine:latest

ARG PB_VERSION=0.40.1

RUN apk add --no-cache unzip ca-certificates

ADD https://github.com/pocketbase/pocketbase/releases/download/v${PB_VERSION}/pocketbase_${PB_VERSION}_linux_amd64.zip /tmp/pb.zip
RUN unzip /tmp/pb.zip -d /pb/

# optionally copy your migrations / hooks into the image
# COPY ./pb_migrations /pb/pb_migrations
# COPY ./pb_hooks /pb/pb_hooks

EXPOSE 8080

CMD ["/pb/pocketbase", "serve", "--http=0.0.0.0:8080"]
```

Mount a volume at `/pb/pb_data` to persist the database and files.

## Recommendations

- **Use an SMTP mail server** (highly recommended) — built-in auth emails need working SMTP
- **Enable the rate limiter** (highly recommended) — Dashboard → Settings
- **Restrict superusers to specific IPs/subnets** (highly recommended):
  `./pocketbase superuser ips 127.0.0.1 10.0.0.0 --dir=/path/to/pb_data` (run with no args to clear)
- **Enable MFA for superusers** (optional)
- **Increase open file descriptors** (optional): `LimitNOFILE = 4096` in the service
- **Set `GOMEMLIMIT`** (optional) to cap the Go runtime heap
- **Enable settings encryption** (optional): create an env variable with a random 32-char value and start with `-encryptionEnv=PB_ENCRYPTION_KEY`

## Monitoring

`GET /api/health` returns 200 with a JSON payload — use it for load-balancer/uptime probes.

## Upgrading

Download the new binary, stop the service, replace the executable, start again. Database migrations run automatically on start; read the changelog for each major version (e.g. v0.40.0 required Go 1.27 + `encoding/json/v2` — test locally before upgrading production). Back up first: `./pocketbase` backups API / copy `pb_data/`.
