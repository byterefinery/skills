# 10 — Production Deployment

## Minimal Setup

### Direct deployment

```bash
# Upload binary to server
rsync -avz -e ssh /local/path/to/myapp root@SERVER:/root/pb/

# Start with auto TLS (Let's Encrypt)
/root/pb/pocketbase serve yourdomain.com

# Or with custom port
/root/pb/pocketbase serve --http=0.0.0.0:8090
```

For non-root users, bind to privileged ports:
```bash
sudo setcap 'cap_net_bind_service=+ep' /root/pb/pocketbase
```

### Systemd Service

```ini
# /lib/systemd/system/pocketbase.service
[Unit]
Description=pocketbase

[Service]
Type=simple
User=root
Group=root
LimitNOFILE=4096
Restart=always
RestartSec=5s
StandardOutput=append:/root/pb/std.log
StandardError=append:/root/pb/std.log
WorkingDirectory=/root/pb
ExecStart=/root/pb/pocketbase serve yourdomain.com

[Install]
WantedBy=multi-user.target
```

```bash
systemctl enable pocketbase.service
systemctl start pocketbase
```

### Create initial superuser

```bash
/root/pb/pocketbase superuser create EMAIL PASS
```

## Reverse Proxy

### NGINX

```nginx
server {
    listen 80;
    server_name example.com;
    client_max_body_size 10M;

    location / {
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        proxy_read_timeout 360s;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_pass http://127.0.0.1:8090;
    }
}
```

### Caddy

```
example.com {
    request_body {
        max_size 10MB
    }
    reverse_proxy 127.0.0.1:8090 {
        transport http {
            read_timeout 360s
        }
    }
}
```

Set "User IP proxy headers" in PocketBase settings (usually `X-Real-IP`, `X-Forwarded-For`).

## Docker

```dockerfile
FROM alpine:latest

ARG PB_VERSION=0.39.8

RUN apk add --no-cache unzip ca-certificates

ADD https://github.com/pocketbase/pocketbase/releases/download/v${PB_VERSION}/pocketbase_${PB_VERSION}_linux_amd64.zip /tmp/pb.zip
RUN unzip /tmp/pb.zip -d /pb/

# COPY ./pb_migrations /pb/pb_migrations
# COPY ./pb_hooks /pb/pb_hooks

EXPOSE 8080

CMD ["/pb/pocketbase", "serve", "--http=0.0.0.0:8080"]
```

Mount volume at `/pb/pb_data` to persist data.

## Backups

### Built-in backups

Dashboard → Settings → Backups. Stored locally or in S3. Creates full ZIP of `pb_data`.

**Warning:** App is read-only during backup generation. For large `pb_data` (2GB+), use alternative strategy.

### Manual backup

```bash
# Stop the app first for transactional safety
./pocketbase stop

# Copy pb_data directory
rsync -avz /path/to/pb_data /backup/location/

# Or use sqlite3 .backup + rsync
sqlite3 /path/to/pb_data/data.db ".backup '/backup/data.db'"
rsync -avz /path/to/pb_data/files/ /backup/files/
```

### Backup API

```javascript
// Create backup
await pb.collection('_superusers').authWithPassword('admin@example.com', 'pass')
const backup = await pb.send('POST', '/api/admin/backups/create', { name: 'backup-2024' })

// Restore backup
await pb.send('POST', '/api/admin/backups/restore', { name: 'backup-2024' })
```

## Security Hardening

### Rate Limiter

Dashboard → Settings → Application. Configure requests per time window. Exclude specific IPs/CIDRs.

### Superuser IP Whitelist

Dashboard → Settings → Application → Superuser IPs.

```bash
# Clear whitelist
./pocketbase superuser ips --dir=/path/to/pb_data

# Set whitelist
./pocketbase superuser ips 127.0.0.1 10.0.0.0 --dir=/path/to/pb_data
```

### Enable MFA for Superusers

Enable MFA and OTP options for `_superusers` collection.

```bash
# Generate OTP manually if email fails
./pocketbase superuser otp yoursuperuser@example.com
```

### SMTP Mail Server

Configure SMTP in Dashboard → Settings → Mail settings. Avoid default `sendmail` for production.

Recommended services: MailerSend, Brevo, SendGrid, Mailgun, AWS SES.

### Encryption Key

```bash
./pocketbase serve --encryptionEnv=PB_ENCRYPTION_KEY
```

The env variable value (32 characters) encrypts sensitive settings.

### CSP Headers

Configure Content-Security-Policy in settings. Default allows audio/video previews.

## Monitoring

### Logs

Dashboard → Logs. Filter by level, date, IP, auth ID.

```go
// Programmatic log query
logs := []*core.Log{}
app.LogQuery().
    AndWhere(dbx.In("level", -4, 0)).
    AndWhere(dbx.NewExp("json_extract(data, '$.type') = 'request'")).
    OrderBy("created DESC").
    Limit(100).
    All(&logs)
```

### Health Check

```
GET /api/health
```

## Scaling Considerations

- PocketBase is designed as a single-instance application
- SQLite has limitations with concurrent writes
- For high traffic, use reverse proxy with load balancing and read replicas (not officially supported)
- Use S3 for file storage to offload disk I/O
- Consider external caching (Redis) for frequently accessed data

## Go Build for Production

```bash
# Linux AMD64
CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o pocketbase

# Linux ARM64
CGO_ENABLED=0 GOOS=linux GOARCH=arm64 go build -o pocketbase

# Windows AMD64
CGO_ENABLED=0 GOOS=windows GOARCH=amd64 go build -o pocketbase.exe
```

## Environment Variables

```bash
# Encryption key
export PB_ENCRYPTION_KEY="your-32-character-key-here"

# Or pass directly
./pocketbase serve --encryptionEnv=PB_ENCRYPTION_KEY
```

## Troubleshooting

- **Port already in use** — change `--http=0.0.0.0:PORT`
- **TLS certificate fails** — ensure domain resolves to server IP, port 80 accessible
- **File upload fails** — check `client_max_body_size` in proxy, field `MaxFileSize` option
- **Realtime disconnects** — set `proxy_read_timeout 360s` in NGINX
- **Slow queries** — check indexes, use `skipTotal=1` for large lists
- **Permission denied** — ensure pb_data directory is writable
