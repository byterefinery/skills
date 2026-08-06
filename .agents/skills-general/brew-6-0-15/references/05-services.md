# Brew Services

## Overview

`brew services` manages background daemons using macOS `launchctl` or Linux `systemctl`. Services are defined by formulae that declare a service block.

## User vs system services

| Mode | macOS | Linux | Scope |
|------|-------|-------|-------|
| Default | `~/Library/LaunchAgents` | `~/.config/systemd/user` | Per-user, starts at login |
| `sudo` | `/Library/LaunchDaemons` | `/usr/lib/systemd/system` | System-wide, starts at boot |

## Commands

```bash
brew services start <formula>          # Start and register at login/boot
brew services stop <formula>           # Stop and unregister
brew services restart <formula>        # Stop + start
brew services run <formula>            # Run without registering
brew services list                     # List all managed services
brew services list --json              # JSON output
brew services info <formula>           # Service details
brew services info --all               # All services
brew services kill <formula>           # Stop immediately, keep registered
brew services cleanup                  # Remove unused service files
```

### With sudo

Prefix any command with `sudo` to manage system-wide services:

```bash
sudo brew services start <formula>
sudo brew services stop <formula>
sudo brew services list
```

### Options

- `--all` — operate on all services (for start, stop, restart, kill)
- `--file=<path>` — use custom service file
- `--keep` — don't unregister on stop
- `--no-wait` — don't wait for stop to complete
- `--max-wait=<seconds>` — wait limit for stop (default 60, 0 = indefinite)
- `--sudo-service-user` — run as specific user when invoked as root on macOS

## Environment files

Per-service environment variables go in `$HOMEBREW_USER_CONFIG_HOME/services/<formula>.env` (default: `~/.homebrew/services/<formula>.env`):

```
# ~/.homebrew/services/postgresql@16.env
PGDATA=/opt/homebrew/var/postgresql@16
PGPORT=5433
```

Format: `KEY=value`, one per line. Lines starting with `#` are comments. Changes take effect on next `brew services restart` and persist across upgrades.

## Brewfile integration

```ruby
brew "postgresql@16", restart_service: true
brew "redis", restart_service: :changed
brew "nginx", restart_service: :always
```

- `restart_service: true` — restart on install/upgrade
- `restart_service: :changed` — restart only if installed or upgraded
- `restart_service: :always` — always restart

## macOS console user

On macOS with MDM/Munki/Jamf workflows where `brew` runs as root:

```bash
brew as-console-user services start <formula>
```

Dispatches the command through the logged-in console user.
