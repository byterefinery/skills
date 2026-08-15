# Storage Backends

Table of contents:
- [URL schemes](#url-schemes)
- [S3 and S3-compatible](#s3-and-s3-compatible)
- [S3 query parameters](#s3-query-parameters)
- [Provider compatibility](#provider-compatibility)
- [Google Cloud Storage](#google-cloud-storage)
- [Azure Blob Storage](#azure-blob-storage)
- [Alibaba Cloud OSS](#alibaba-cloud-oss)
- [SFTP](#sftp)
- [WebDAV](#webdav)
- [NATS JetStream](#nats-jetstream)
- [Local filesystem](#local-filesystem)
- [Troubleshooting S3-compatible providers](#troubleshooting-s3-compatible-providers)

## URL schemes

| Scheme | Backend |
|---|---|
| `s3://bucket/prefix` | Amazon S3 (AWS SDK v2) and S3-compatible services |
| `gs://bucket/prefix` | Google Cloud Storage (native client) |
| `abs://container/prefix` | Azure Blob Storage (native client) |
| `oss://bucket/prefix` | Alibaba Cloud OSS (native client) |
| `sftp://[user@]host[:port]/prefix` | SFTP |
| `webdav://host[:port]/prefix` / `webdavs://...` | WebDAV (HTTP / HTTPS) |
| `nats://host:port/bucket/prefix` | NATS JetStream object store |
| (no scheme / local path) | Local filesystem |

Any `scheme://` string given to `restore`/`ltx` is treated as a replica URL (not a database path), and `-config` is rejected in that mode.

## S3 and S3-compatible

```yaml
replica:
  url: s3://my-bucket/my-db
  region: us-east-1
```

Credentials come from the standard AWS chain — `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` (or the litestream-specific `LITESTREAM_ACCESS_KEY_ID`/`LITESTREAM_SECRET_ACCESS_KEY`), shared config/credential files, or IAM roles (e.g. instance profiles).

Encryption: `sse-kms-key-id` for SSE-KMS, or `sse-customer-algorithm`/`sse-customer-key`/`sse-customer-key-path` for SSE-C. (Note — client-side age encryption is NOT supported in v0.5.x; see [01-configuration](01-configuration.md#backend-specific-settings).)

## S3 query parameters

Parameters can be set in the URL (camelCase or hyphenated) instead of the config:

| Parameter | Default | Purpose |
|---|---|---|
| `endpoint` | AWS S3 | Custom S3 endpoint URL |
| `region` | auto | AWS region |
| `force-path-style` | auto | Path-style vs virtual-hosted URLs |
| `sign-payload` | `true` | Sign request payloads |
| `require-content-md5` | `true` | Require Content-MD5 header |
| `skip-verify` | `false` | Skip TLS certificate verification |
| `concurrency` | `5` | Multipart upload concurrency |
| `part-size` | `5242880` (5 MB) | Multipart part size |
| `storage-class` | — | Object storage class |
| `sse-customer-algorithm` / `sse-customer-key` / `sse-customer-key-md5` | — | SSE-C |
| `sse-kms-key-id` | — | SSE-KMS key |

## Provider compatibility

Litestream auto-detects known endpoint patterns and applies defaults — but the table below is what to expect and what to set manually when detection does not cover your endpoint.

| Provider | Endpoint pattern | Auto-applied settings |
|---|---|---|
| Cloudflare R2 | `*.r2.cloudflarestorage.com` (must be `https://`) | `sign-payload=true`, `concurrency=2`, checksums off |
| Backblaze B2 | `*.backblazeb2.com` | `sign-payload=true`, `force-path-style=true` |
| DigitalOcean Spaces | `*.digitaloceanspaces.com` | `sign-payload=true` |
| MinIO | host with a port (not a cloud domain) | `sign-payload=true`, `force-path-style=true` |
| Scaleway | `*.scw.cloud` | `sign-payload=true` |
| Hetzner | `*.your-objectstorage.com` | `sign-payload=true` |
| Filebase | `s3.filebase.com` | `sign-payload=true`, `force-path-style=true` |
| Tigris | `*.tigris.dev` | `sign-payload=true`, `require-content-md5=false` |
| Supabase Storage | `*.supabase.co` | `sign-payload=true`, `force-path-style=true` |
| Google Cloud Storage (SigV4) | `storage.googleapis.com` | `Accept-Encoding` excluded from SigV4 signature |

Worked examples:

```yaml
# Cloudflare R2
replica:
  url: s3://bucket/prefix?endpoint=https://ACCOUNT.r2.cloudflarestorage.com
  access-key-id: ...
  secret-access-key: ...

# Backblaze B2
replica:
  url: s3://bucket/prefix?endpoint=https://s3.us-west-004.backblazeb2.com&sign-payload=true&force-path-style=true
  access-key-id: ...
  secret-access-key: ...

# DigitalOcean Spaces
replica:
  url: s3://bucket/prefix?endpoint=https://nyc3.digitaloceanspaces.com&force-path-style=false
  access-key-id: ...
  secret-access-key: ...

# MinIO
replica:
  url: s3://bucket/prefix?endpoint=https://minio.example.com:9000&force-path-style=true
  access-key-id: ...
  secret-access-key: ...

# Wasabi
replica:
  url: s3://bucket/prefix?endpoint=https://s3.us-east-2.wasabisys.com
  access-key-id: ...
  secret-access-key: ...
```

Provider notes:

- **R2** — strict concurrent-upload limit (~2–3), no `aws-chunked` encoding, no request/response checksums. Keep `concurrency=2`.
- **B2** — requires signed payloads; use the regional S3 API endpoint `https://s3.REGION.backblazeb2.com`.
- **Supabase** — S3 access keys from the dashboard (Storage > S3 Access Keys); no S3 versioning support.
- **GCS via SigV4** — GCS can also be addressed through the S3 XML API with HMAC keys (`type: s3`, `endpoint: https://storage.googleapis.com`, `force-path-style: true`), but the native `gs://` client is preferred.

## Google Cloud Storage

```yaml
replica:
  url: gs://my-bucket/my-db
```

Authentication is Application Default Credentials — `GOOGLE_APPLICATION_CREDENTIALS` env var, workload identity, or gcloud ADC. No config fields needed.

## Azure Blob Storage

```yaml
replica:
  url: abs://my-container/my-db
  account-name: myaccount
  account-key: <base64-key>
```

Auth options in priority order:

1. SAS token — `sas-token` config or `LITESTREAM_AZURE_SAS_TOKEN` env
2. Account key — `account-key` config or `LITESTREAM_AZURE_ACCOUNT_KEY` env
3. Default credential chain (managed identity via `AZURE_CLIENT_ID`/`AZURE_CLIENT_SECRET`/`AZURE_TENANT_ID`)

## Alibaba Cloud OSS

```yaml
replica:
  url: oss://my-bucket/my-db?endpoint=oss-cn-hangzhou.aliyuncs.com
  access-key-id: ...
  access-key-secret: ...
```

## SFTP

```yaml
replica:
  url: sftp://backup.example.com/Backups
  user: litestream
  key-path: /etc/litestream/sftp_key     # or password:
  host-key: "ssh-ed25519 AAAAC3NzaC1..." # strongly recommended
  concurrent-writes: false
```

`host-key` verifies the server identity — copy it from the server's `/etc/ssh/ssh_host_*.pub` or `ssh-keyscan`. Without it you get TOFU-style trust and no protection against MITM.

## WebDAV

```yaml
replica:
  url: webdavs://dav.example.com/Backups
  webdav-username: litestream
  webdav-password: ...
```

`webdav://` for plain HTTP, `webdavs://` for HTTPS.

## NATS JetStream

```yaml
replica:
  type: nats
  url: nats://nats.example.com:4222
  bucket: litestream-backups
  # auth: jwt + seed, creds file, nkey, or username + token
  # tls: true with root-cas / client-cert / client-key as needed
```

Objects are stored in a JetStream bucket; supports reconnection tuning (`max-reconnects`, `reconnect-wait`, `timeout`).

## Local filesystem

```yaml
replica:
  path: /var/backups/my-db       # or url: file:///var/backups/my-db
```

Useful for testing, NFS shares, and simple LAN backups. Note the replica path is a *directory* holding the `ltx/0000/...` layout — not a file.

## Troubleshooting S3-compatible providers

| Symptom | Fix |
|---|---|
| `InvalidArgument: Unsupported content encoding: aws-chunked` | Provider does not support chunked encoding; use the provider's endpoint (auto-detection disables checksums) or set `sign-payload`/`require-content-md5` explicitly |
| `SignatureDoesNotMatch` | Add `sign-payload=true`; check credentials and endpoint URL |
| `MissingContentLength` | Provider needs Content-Length; known providers are handled automatically |
| `Too many concurrent uploads` / timeouts | Lower `concurrency` (e.g. `?concurrency=2`) — especially R2 |
| `AccessDenied` | Verify credentials and bucket permissions; B2 needs `sign-payload=true` |

Enable verbose logging with `LITESTREAM_DEBUG=1` (or `logging.level: debug`) and test a new endpoint without starting replication:

```bash
litestream ltx s3://bucket/prefix?endpoint=...
litestream restore -dry-run -o /tmp/test.db s3://bucket/prefix?endpoint=...
```
