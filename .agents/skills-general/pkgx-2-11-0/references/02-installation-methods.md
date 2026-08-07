# Installation Methods

## Homebrew (recommended)

```bash
brew install pkgx
```

Upgrade: `brew upgrade pkgx`

## cURL installer

```bash
curl -fsS https://pkgx.sh | sh
```

Same command upgrades pkgx if already installed.

## Windows (PowerShell)

```powershell
irm https://pkgx.sh | iex
```

Limited package availability. List with `pkgx -Q`. WSL2 gets full Linux support.

## Manual download

```bash
# Download standalone binary
curl -o ./pkgx \
  --compressed --fail --proto '=https' \
  https://pkgx.sh/$(uname)/$(uname -m)

# Install to /usr/local/bin
sudo install -m 755 pkgx /usr/local/bin
```

Or one-liner with tarball:

```bash
curl -Ssf https://pkgx.sh/$(uname)/$(uname -m).tgz | sudo tar xz -C /usr/local/bin
```

## Cargo

```bash
cargo install pkgx
```

## Docker

```bash
# Interactive
docker run -it pkgxdev/pkgx

# One-shot
docker run pkgxdev/pkgx node@21.1 --version

# With deps
docker run pkgxdev/pkgx +python@3.10 node@22 start
```

Dockerfile:

```dockerfile
FROM pkgxdev/pkgx
RUN pkgx +node@16 npm start
```

Or in any image:

```dockerfile
FROM ubuntu
RUN curl https://pkgx.sh | sh
RUN pkgx python@3.10 -m http.server 8000
```

## GitHub Actions

```yaml
- uses: pkgxdev/setup@v4
- run: pkgx shellcheck
```

Other CI/CD providers:

```bash
curl https://pkgx.sh | sh
pkgx shellcheck
```

## Arch Linux (AUR)

- `pkgx` — latest released version
- `pkgx-git` — latest development version (may be unstable)

Community-maintained; may lag behind releases.

## Uninstall

```bash
sudo rm /usr/local/bin/pkg[xm]
rm -rf ~/.pkgx
```

Platform-specific caches:

**macOS:**
```bash
rm -rf ~/Library/Caches/pkgx
rm -rf ~/Library/Application\ Support/pkgx
```

**Linux:**
```bash
rm -rf "${XDG_CACHE_HOME:-$HOME/.cache}/pkgx"
rm -rf "${XDG_DATA_HOME:-$HOME/.local/share}"/pkgx
```

**Windows:**
```bash
rm -rf "%LOCALAPPDATA%/pkgx"
```

Note: Tools run via pkgx may have created their own config/cache directories (e.g., `~/.npm`, `~/.gem`, `~/.node`). Check and clean those separately.
