# Install and storage configuration

## Installer

```sh
curl -fsSL https://celld.dev/install.sh | sh
```

- The installer downloads the `celld` binary and keeps each release under `~/.local/lib/celld/releases` with one symlink pointing at the current one. Put `~/.local/bin` on `PATH` if the installer asks.
- Pin or roll back a release by setting `CELLD_VERSION` to the tag (for example `CELLD_VERSION=v0.2.1`) before running the installer. Releases are on [GitHub](https://github.com/denoland/celld/releases).
- Each release has a GitHub Actions build attestation. Verify a downloaded file with:

```sh
gh attestation verify <asset> --repo denoland/celld
```

- Uninstall: `rm $(which celld) && rm -rf ~/.local/lib/celld`.
- `celld deploy` needs esbuild on `PATH` (or set `CELLD_ESBUILD` to the executable path). Asset-only projects do not need esbuild.
- Windows is not available, and Intel Macs get no prebuilt binaries; a build from source works.

## Container

The release image contains the `celld` binary and is published for Linux x86-64 and ARM64:

```sh
docker run --rm ghcr.io/denoland/celld --version
```

Persist the runtime's local state and pass the standard AWS credential environment through:

```sh
docker volume create celld-state
docker run --rm --network host \
  -e AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY \
  -e AWS_SESSION_TOKEN \
  -e CELLD_WATCH=/var/lib/celld/state \
  -v celld-state:/var/lib/celld \
  ghcr.io/denoland/celld \
  --bucket s3://my-cells-bucket \
  --endpoint https://ACCOUNT.r2.cloudflarestorage.com \
  --region auto \
  --listen 0.0.0.0:8080 \
  --internal-listen 10.0.0.12:8081 \
  --advertise node-a.internal:8081
```

Drop `--endpoint` and `--region` for AWS S3. Expose port 8080 through the load balancer, and keep port 8081 on the private network.

## Object storage

### S3-compatible (S3, R2, …)

celld uses the standard AWS credential chain. For Cloudflare R2, create a bucket and an S3 API token that has access to it, then set:

```sh
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export AWS_REGION=auto
export S3_ENDPOINT=https://ACCOUNT_ID.r2.cloudflarestorage.com
export CELLD_BUCKET=s3://YOUR-BUCKET
```

Credential notes: celld reads the `AWS_*` environment, instance metadata, and web identity tokens. It does **not** read `~/.aws` profiles or SSO logins.

### Google Cloud Storage

celld uses Application Default Credentials. Create a bucket, then authenticate with `gcloud auth application-default login` or point `GOOGLE_APPLICATION_CREDENTIALS` at a service-account key that has access to the bucket. Then set:

```sh
export CELLD_BUCKET=gs://YOUR-BUCKET
```

A `gs://` bucket takes no `S3_ENDPOINT` and no AWS credentials, and celld ignores the storage region. On a Compute Engine instance, celld can use the attached service account, but the instance's access scopes cap the credential — create the instance with the `cloud-platform` scope so the IAM role of the service account controls access (the default scope permits only storage reads).

### Bucket key prefix

A bucket value can add a key prefix: `s3://YOUR-BUCKET/PREFIX`. Every object of the fleet then goes below `PREFIX/`, so two fleets can share one bucket. A bucket value without a prefix keeps objects at the root of the bucket.

### Store qualification

Ownership records depend on conditional writes and read-after-write consistency:

- **Qualify** — Amazon S3, Cloudflare R2, Google Cloud Storage, Azure Blob Storage, Tigris
- **Do not qualify** — MinIO (community edition), Backblaze B2, Hetzner Object Storage, DigitalOcean Spaces

On a non-qualifying store, celld is not correct: two nodes can own one cell. A store can also accept the conditional headers and not apply the condition, failing late and silently — `celld diagnose` probes the store directly (see [04-ownership-and-fencing](04-ownership-and-fencing.md)).

The bucket credentials give full control of the fleet — they cover the deployments, the SQLite replicas, the ownership records, the node leases, and the peer-authentication secret. Keep them safe and give each credential access to one fleet bucket only.

## Reserved object prefixes

celld reserves these prefixes, and it deletes objects under some of them. An application must not write under any of them:

`cells/`, `nodes/`, `node-cells/`, `fleet/`, `deploy/`, `deploy-blobs/`, `wake/`, `probe/`, `telemetry/`

## Environment variables

Run `celld -h` for the complete list, including the advanced tuning switches and their defaults. Primary settings:

| variable | purpose |
| --- | --- |
| `CELLD_BUCKET` | The fleet bucket, and an optional key prefix. Same as `--bucket` |
| `S3_ENDPOINT` | The S3-compatible endpoint. Same as `--endpoint` |
| `AWS_REGION`, `AWS_DEFAULT_REGION` | The storage region |
| `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN` | Explicit AWS credentials; the standard AWS credential chain is also available |
| `GOOGLE_APPLICATION_CREDENTIALS`, `GOOGLE_SERVICE_ACCOUNT_KEY` | Google credentials for a `gs://` bucket; Application Default Credentials is also available |
| `CELLD_ADDR` | The public Worker listener. Same as `--listen` |
| `CELLD_INTERNAL_ADDR` | The peer and operator listener. Same as `--internal-listen` |
| `CELLD_ADVERTISE` | The internal address that peers can reach. Same as `--advertise` |
| `CELLD_UNSAFE_PUBLIC_ADVERTISE` | Set to `1` to permit a literal public IP in `CELLD_ADVERTISE`; it does not resolve a DNS name or restrict the internal listener |
| `CELLD_NODE` | An explicit node-session ID |
| `CELLD_WATCH` | The local work directory for SQLite and replication |
| `CELLD_ESBUILD` | The path of the esbuild executable |
| `CELLD_ACTIVATIONS` | Limit for concurrent cold-cell activations (default, available CPU count or 128, whichever is smaller) |
| `CELLD_OPERATION_DEADLINE_MS` | Deadline for a non-restore operation (default 15000) |
| `CELLD_WORKER_LOADER` | Bind a Worker Loader (Code Mode) at this `env` name so a Worker can start isolates at runtime. Off unless set (experimental) |
| `CELLD_MAX_LOADED_WORKERS` | Limit for concurrent loaded workers (default 256) |
| `CELLD_MAX_RESIDENT_CELLS` | Hard limit for resident cells, enforced at admission |
| `CELLD_MAX_RSS_MB` | Memory threshold for pressure shedding, applied to the memory the cells hold (default 80% of the available memory; `0` disables the threshold and the absolute cap) |
| `CELLD_OUTPUT_GATE` | Default `1`, so celld proves each write durable before acknowledging it. `0` removes the replication wait and accepts possible loss of an acknowledged write |
| `CELLD_LTX_COMPACTION` | Default `1`, celld creates additive L1 objects so a takeover reads tens of objects instead of thousands. Set `0` on every node of a mixed fleet until all nodes can read v0.5.2 block objects, because an old reader cannot take over a cell after its first L1 publication |
| `CELLD_LTX_COMPACTION_MIN_TXIDS` | Durable TXID distance that queues an L1 attempt (default 256) |
| `CELLD_LTX_COMPACTIONS` | Node-wide limit for concurrent L1 attempts (default 2) |
| `CELLD_VAR_*`, `CELLD_VARS_FILE` | Worker variable overrides |
| `CELLD_TRUST_FORWARDED_HEADERS` | Set to `1` to trust `X-Forwarded-Host`/`X-Forwarded-Proto` from a trusted proxy |
| `CELLD_STORAGE_PROBE` | Set to `0` to disable the startup bucket conditional-write probe |
| `RUST_LOG` | The runtime log filter |

An unset variable selects its documented default. A boolean variable accepts only `0` or `1`. celld exits during startup when a supplied value is invalid.
