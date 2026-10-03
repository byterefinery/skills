# Console commands

Global flags (work with every command):

| Flag | Default | Purpose |
|---|---|---|
| `-dir` | `./pb_data` | the PocketBase data directory |
| `-dev` | `false` | dev mode — print logs and SQL statements to the console |
| `-encryptionEnv` | none | env variable whose 32-char value is used to encrypt the app settings |
| `-queryTimeout` | `120` (s) | default SELECT queries timeout |

## serve

```
./pocketbase serve [domain(s)]
```

Starts the web server. With no domain: listens on `127.0.0.1:8090`. With domain(s): auto-provisions Let's Encrypt TLS, listens on `0.0.0.0:80` (redirect) and `0.0.0.0:443`.

Flags:

- `--http` — TCP address for the HTTP server (default `127.0.0.1:8090`, or `0.0.0.0:80` with domains)
- `--https` — TCP address for the HTTPS server (empty = no TLS; `0.0.0.0:443` with domains); HTTP traffic auto-redirects to HTTPS
- `--origins` — CORS allowed origins list (default `*`)

Binding 80/443 requires root or equivalent privileges (`setcap 'cap_net_bind_service=+ep' ./pocketbase`, `authbind`, iptables, …). See `10-production` for systemd/Docker/reverse-proxy setups.

## superuser

Manage `_superusers` records from the CLI:

```
./pocketbase superuser upsert EMAIL [PASS]     # create or update (idempotent)
./pocketbase superuser create EMAIL PASS       # create (fails if exists)
./pocketbase superuser update EMAIL [PASS]     # update
./pocketbase superuser delete EMAIL
./pocketbase superuser otp EMAIL               # send a one-time password
./pocketbase superuser ips IP1 IP2            # update the superuser IPs whitelist (space separated; empty clears it)
```

## migrate

Runs DB migration scripts (registered by `migratecmd` — present in the prebuilt binary and in Go apps that call `migratecmd.MustRegister`). Arguments:

```
./pocketbase migrate up               # run all available migrations
./pocketbase migrate down [number]    # revert the last [number] applied migrations
./pocketbase migrate create name      # create a new blank migration template file
./pocketbase migrate collections      # create a migration with a snapshot of local collections
./pocketbase migrate history-sync     # drop _migrations history rows for deleted files
```

Related flags (prebuilt binary / `examples/base`): `--automigrate` (auto-create migration files on collection changes, default on), `--migrationsDir`.

## update

Self-updates the current executable from GitHub releases (registered by `ghupdate` in the prebuilt binary).

## version / help

`--version` prints the PocketBase version; `--help` (or `./pocketbase [command] --help`) lists commands and flags. The default help command is hidden — use the `--help` flag only.

## Custom commands (Go)

Register any [cobra](https://pkg.go.dev/github.com/spf13/cobra) command on `app.RootCmd`:

```go
import "github.com/spf13/cobra"

app.RootCmd.AddCommand(&cobra.Command{
    Use:   "hello",
    Short: "Example hello world command",
    Run: func(cmd *cobra.Command, args []string) {
        fmt.Println("Hello World!")
    },
})
```

Run with `./myapp hello` (or `go run main.go hello`). Note: console commands execute in their **own process** — hooks and realtime state are not shared between `serve` and other commands. Since v0.40.0, command errors/panics propagate to `app.Start()` and produce a non-zero exit code (while still running `OnTerminate`).
